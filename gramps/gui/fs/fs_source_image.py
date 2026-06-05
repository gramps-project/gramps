#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2026  Gabriel Rios
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
# -------------------------------------------------------------------------
#
# Future imports
#
# -------------------------------------------------------------------------
from __future__ import annotations

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import shutil
import sys
import webbrowser
from typing import Any, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import (
    Gtk,
    Gdk,
    GLib,
)  # noqa: F401

from gramps.gen.fs import tree
from gramps.gui.fs import ui as fs_ui


def _is_windows() -> bool:
    # Avoid importing gramps.gen.constfunc.is_windows because mypy/type stubs
    # may not expose it even if it exists at runtime.
    return sys.platform.startswith("win") or os.name == "nt"


WebKit2: Optional[Any] = None
try:
    if not _is_windows():
        gi.require_version("WebKit2", "4.0")
        from gi.repository import WebKit2 as _WebKit2  # type: ignore

        WebKit2 = _WebKit2
except Exception:
    WebKit2 = None


def _canonicalize_fs_web_url(url: str) -> str:
    """
    - If session exists and has canonical_web_url(), use it
    - else rewrite beta/familysearch to www.familysearch.org
    """
    if not url:
        return "about:blank"
    u = str(url).strip()
    if not u.startswith(("http://", "https://")):
        return u
    try:
        sess = getattr(tree, "_fs_session", None)
        if sess and hasattr(sess, "canonical_web_url"):
            return sess.canonical_web_url(u)
    except Exception:
        pass
    try:
        p = urlparse(u)
        host = (p.netloc or "").lower()
        if host in (
            "beta.familysearch.org",
            "familysearch.org",
            "www.familysearch.org",
        ):
            return urlunparse(
                (
                    p.scheme or "https",
                    "www.familysearch.org",
                    p.path or "",
                    p.params or "",
                    p.query or "",
                    p.fragment or "",
                )
            )
        return u
    except Exception:
        return u


class SourceImageBrowser:
    """
    browser for grabbing image files from a source page.

    - Linux with WebKit2 available: embedded WebView, intercept downloads.
    - Windows (or no WebKit2): open system browser and let user pick files from disk.
    - Lets user choose a download folder (optional) and also pick local files.
    - Tracks all saved files and returns them on close.
    """

    def __init__(
        self,
        url: str,
        parent_window: Optional[Gtk.Window] = None,
        start_dir: Optional[str] = None,
        title: str = "Add Source Image",
    ):
        self.url = _canonicalize_fs_web_url(url)
        self.parent_window = parent_window
        self.download_dir: Optional[str] = start_dir
        self.saved_files: List[str] = []

        # Store signal connections as (object_with_disconnect, handler_id)
        self._handlers: List[Tuple[Any, int]] = []

        self._ctx: Optional[Any] = None
        self._use_webkit = (not _is_windows()) and (WebKit2 is not None)

        self.dialog = Gtk.Dialog(
            title=title,
            transient_for=parent_window,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
        )
        self.dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        self.dialog.set_default_size(1040, 820)

        # keep UI CSS centralized
        self._install_css()

        try:
            self.dialog.get_style_context().add_class("fs-srcimg-window")
        except Exception:
            pass

        fs_ui.set_headerbar(self.dialog, title, "Source images")

        # top part (folder + actions)
        header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            margin_top=10,
            margin_bottom=6,
            margin_start=10,
            margin_end=10,
        )
        try:
            header.get_style_context().add_class("fs-srcimg-header")
        except Exception:
            pass

        self.lbl_dir = Gtk.Label(xalign=0)
        self.lbl_dir.set_ellipsize(3)
        try:
            self.lbl_dir.get_style_context().add_class("fs-muted")
        except Exception:
            pass

        self.btn_pick_folder = Gtk.Button()
        fs_ui.set_button_icon_and_label(
            self.btn_pick_folder, "folder-open-symbolic", "Folder..."
        )
        self.btn_pick_folder.set_tooltip_text("Choose download folder")
        self.btn_pick_folder.connect("clicked", self._choose_dir)

        self.btn_pick_files = Gtk.Button()
        fs_ui.set_button_icon_and_label(
            self.btn_pick_files, "document-open-symbolic", "Choose file..."
        )
        self.btn_pick_files.set_tooltip_text("Choose a local file from disk")
        self.btn_pick_files.connect("clicked", self._choose_files)

        self.btn_open_browser = Gtk.Button()
        fs_ui.set_button_icon_and_label(
            self.btn_open_browser, "web-browser-symbolic", "Browser"
        )
        self.btn_open_browser.set_tooltip_text("Open source page in system browser")
        self.btn_open_browser.connect("clicked", self._open_external_browser)

        self.btn_reload = Gtk.Button()
        fs_ui.set_button_icon_and_label(
            self.btn_reload, "view-refresh-symbolic", "Reload"
        )
        self.btn_reload.set_tooltip_text("Reload page")
        self.btn_reload.connect("clicked", self._reload)

        header.pack_start(self.lbl_dir, True, True, 0)
        header.pack_end(self.btn_reload, False, False, 0)
        header.pack_end(self.btn_open_browser, False, False, 0)
        header.pack_end(self.btn_pick_files, False, False, 0)
        header.pack_end(self.btn_pick_folder, False, False, 0)

        # main body
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        body.set_margin_start(10)
        body.set_margin_end(10)
        body.set_margin_bottom(10)
        try:
            body.get_style_context().add_class("fs-srcimg-wrap")
        except Exception:
            pass

        # embedded browser or empty
        self.webview: Optional[Any] = None
        webkit = WebKit2
        if self._use_webkit and webkit is not None:
            try:
                self.webview = webkit.WebView()
            except Exception:
                self.webview = None

            if self.webview is not None:
                sc = Gtk.ScrolledWindow()
                sc.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
                sc.add(self.webview)
                try:
                    sc.get_style_context().add_class("fs-srcimg-web")
                except Exception:
                    pass
                body.pack_start(sc, True, True, 0)

        if self.webview is None:
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            box.set_margin_top(18)
            box.set_margin_bottom(18)
            box.set_margin_start(12)
            box.set_margin_end(12)
            try:
                box.get_style_context().add_class("fs-srcimg-empty")
            except Exception:
                pass

            lab = Gtk.Label(
                label=(
                    "Embedded browser is not available on this platform.\n"
                    "A system browser will be used instead.\n\n"
                    "1) Click 'Browser' to open the source page.\n"
                    "2) Download images in your browser.\n"
                    "3) Click 'Choose file...' to select files from disk.\n"
                )
            )
            lab.set_xalign(0.0)
            lab.set_line_wrap(True)
            box.pack_start(lab, False, False, 0)
            body.pack_start(box, True, True, 0)

        self._liststore = Gtk.ListStore(str)
        self._tree = Gtk.TreeView(model=self._liststore)
        self._tree.set_headers_visible(False)
        try:
            self._tree.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        except Exception:
            pass

        col = Gtk.TreeViewColumn("Files")
        cell = Gtk.CellRendererText()
        cell.set_property("ellipsize", 3)
        col.pack_start(cell, True)
        col.add_attribute(cell, "text", 0)
        self._tree.append_column(col)

        files_frame = Gtk.Frame(label="Selected / saved files")
        try:
            files_frame.get_style_context().add_class("fs-srcimg-frame")
        except Exception:
            pass

        files_sc = Gtk.ScrolledWindow()
        files_sc.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        try:
            files_sc.set_min_content_height(120)
        except Exception:
            pass
        files_sc.add(self._tree)
        files_frame.add(files_sc)
        body.pack_end(files_frame, False, False, 0)

        # Footer info label
        self.info = Gtk.Label(xalign=0)
        self.info.set_margin_top(2)
        self.info.set_margin_bottom(2)
        self.info.set_line_wrap(True)
        try:
            self.info.get_style_context().add_class("fs-srcimg-info")
        except Exception:
            pass

        # Assemble
        vbox = self.dialog.get_content_area()
        vbox.set_spacing(0)
        vbox.pack_start(header, False, False, 0)
        vbox.pack_start(body, True, True, 0)
        vbox.pack_end(self.info, False, False, 0)

        # Wire downloads webkit
        self._wire_downloads()
        self._refresh_dir_label()

        if self._use_webkit and self.webview is not None:
            try:
                self.webview.load_uri(self.url)
            except Exception:
                pass
        else:
            self._open_external_browser()

    # public API
    def run(self) -> List[str]:
        self.dialog.show_all()
        self.dialog.run()
        self._teardown()
        return self.saved_files

    # old
    def _install_css(self) -> None:
        return

    # internals
    def _reload(self, *_a) -> None:
        if self._use_webkit and self.webview is not None:
            try:
                self.webview.reload()
                self.info.set_text("Reloading...")
            except Exception:
                pass
        else:
            self._open_external_browser()

    def _open_external_browser(self, *_a) -> None:
        if not self.url or self.url == "about:blank":
            return
        try:
            webbrowser.open(self.url, new=1, autoraise=True)
            self.info.set_text(
                "Opened system browser. Download images there, then use 'Choose file...'."
            )
        except Exception:
            self.info.set_text("Could not open system browser.")

    def _wire_downloads(self) -> None:
        if not self._use_webkit or self.webview is None:
            return

        try:
            # more mypy w/ local ctx
            ctx = self.webview.get_context()
            hid = ctx.connect("download-started", self._on_download_started)
            self._handlers.append((ctx, hid))
            self._ctx = ctx
        except Exception:
            pass

    def _on_download_started(self, _ctx, download) -> None:
        if not self.download_dir:
            self._choose_dir()
            self._refresh_dir_label()
            if not self.download_dir:
                try:
                    download.cancel()
                except Exception:
                    pass
                return
        try:
            download.connect("decide-destination", self._on_decide_destination)
            download.connect("finished", self._on_finished)
            download.connect("failed", self._on_failed)
            download.connect("received-data", self._on_progress)
        except Exception:
            pass

    def _on_decide_destination(self, download, suggested_filename: str) -> bool:
        if not self.download_dir:
            return False
        fname = suggested_filename or "download.bin"
        dest_path = self._unique_path(os.path.join(self.download_dir, fname))
        try:
            dest_uri = GLib.filename_to_uri(dest_path)
        except Exception:
            dest_uri = "file://" + dest_path
        try:
            download.set_destination(dest_uri)
        except Exception:
            pass
        try:
            setattr(download, "_dest_path", dest_path)
        except Exception:
            pass
        return True

    def _on_progress(self, download, _received) -> None:
        try:
            t = download.get_estimated_progress() * 100.0
            self.info.set_text("Downloading... %0.0f%%" % t)
        except Exception:
            pass

    def _on_finished(self, download) -> None:
        path = None
        try:
            path = getattr(download, "_dest_path", None)
        except Exception:
            path = None
        if path and os.path.exists(path):
            self._add_saved_file(path)
            self.info.set_text(
                "Saved: %s (total: %d)"
                % (os.path.basename(path), len(self.saved_files))
            )

    def _on_failed(self, _download, _error) -> None:
        self.info.set_text("Download failed.")

    def _choose_dir(self, *_a) -> None:
        dlg = Gtk.FileChooserDialog(
            title="Choose download folder",
            parent=self.dialog,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(
                "Cancel",
                Gtk.ResponseType.CANCEL,
                "Select",
                Gtk.ResponseType.OK,
            ),
        )
        if self.download_dir and os.path.isdir(self.download_dir):
            try:
                dlg.set_current_folder(self.download_dir)
            except Exception:
                pass
        resp = dlg.run()
        if resp == Gtk.ResponseType.OK:
            self.download_dir = dlg.get_filename()
        dlg.destroy()
        self._refresh_dir_label()

    def _choose_files(self, *_a) -> None:
        dlg = Gtk.FileChooserDialog(
            title="Choose image file(s)",
            parent=self.dialog,
            action=Gtk.FileChooserAction.OPEN,
            buttons=(
                "Cancel",
                Gtk.ResponseType.CANCEL,
                "Select",
                Gtk.ResponseType.OK,
            ),
        )
        try:
            dlg.set_select_multiple(True)
        except Exception:
            pass
        try:
            flt = Gtk.FileFilter()
            flt.set_name("Images")
            flt.add_mime_type("image/*")
            dlg.add_filter(flt)
            flt2 = Gtk.FileFilter()
            flt2.set_name("All files")
            flt2.add_pattern("*")
            dlg.add_filter(flt2)
        except Exception:
            pass
        if self.download_dir and os.path.isdir(self.download_dir):
            try:
                dlg.set_current_folder(self.download_dir)
            except Exception:
                pass
        resp = dlg.run()
        paths: List[str] = []
        if resp == Gtk.ResponseType.OK:
            try:
                paths = dlg.get_filenames() or []
            except Exception:
                try:
                    p = dlg.get_filename()
                    paths = [p] if p else []
                except Exception:
                    paths = []
        dlg.destroy()
        if not paths:
            return
        if self.download_dir and os.path.isdir(self.download_dir):
            for src in paths:
                try:
                    base = os.path.basename(src) or "picked.bin"
                    dest = self._unique_path(os.path.join(self.download_dir, base))
                    shutil.copy2(src, dest)
                    self._add_saved_file(dest)
                except Exception:
                    self._add_saved_file(src)
        else:
            for src in paths:
                self._add_saved_file(src)
        self._refresh_dir_label()
        self.info.set_text(
            "Selected %d file(s) (total: %d)" % (len(paths), len(self.saved_files))
        )

    def _refresh_dir_label(self) -> None:
        path = self.download_dir or "(no folder selected)"
        self.lbl_dir.set_text("Download folder: %s" % path)

    def _unique_path(self, path: str) -> str:
        if not os.path.exists(path):
            return path
        root, ext = os.path.splitext(path)
        i = 2
        while True:
            candidate = "%s (%d)%s" % (root, i, ext)
            if not os.path.exists(candidate):
                return candidate
            i += 1

    def _add_saved_file(self, path: str) -> None:
        if not path:
            return
        if path not in self.saved_files:
            self.saved_files.append(path)
            try:
                self._liststore.append([path])
            except Exception:
                pass

    def _teardown(self) -> None:
        for obj, hid in self._handlers:
            try:
                obj.disconnect(hid)
            except Exception:
                pass
        self._handlers = []
        try:
            self.dialog.destroy()
        except Exception:
            pass


def pick_images(
    url: str,
    parent_window=None,
    start_dir: Optional[str] = None,
    title: str = "Add Source Image",
) -> List[str]:
    """
    launches browser and returns saved file paths.
    - Opens the system browser w/o WebKit
    - User downloads images and then Choose file to select them
    """
    b = SourceImageBrowser(
        url, parent_window=parent_window, start_dir=start_dir, title=title
    )
    return b.run()
