# -*- coding: utf-8 -*-
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

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING, cast
from types import ModuleType

from gi.repository import Gtk, Gdk

# mypy Pango
Pango: Any = None
try:
    from gi.repository import Pango as _Pango  # type: ignore

    Pango = cast(Any, _Pango)
except Exception:
    Pango = None

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.dialog import OkDialog, WarningDialog

import gramps.gen.fs.fs_import as fs_import
from gramps.gen.fs import utils as fs_utilities
from gramps.gen.fs.fs_import import deserializer as deserialize
from gramps.gui.fs import ui as fs_ui

_has_img_picker = False
fs_source_image: Optional[ModuleType] = None

try:
    from gramps.gui.fs import fs_source_image as _fs_source_image

    fs_source_image = cast(ModuleType, _fs_source_image)
    _has_img_picker = True
except Exception:
    fs_source_image = None
    _has_img_picker = False

_ = glocale.translation.gettext

if TYPE_CHECKING:
    from typing import Protocol

    class _SourcesDialogDeps(Protocol):
        # provided by host class / other mixins
        dbstate: Any
        uistate: Any
        CONFIG: Any
        fs_Tree: Any

        def _ensure_sources_cached(self, fsid: str) -> None: ...

        def _gather_sr_meta(self, fsid: str) -> dict[str, Any]: ...

        def _import_fs_sources(self, gr: Any, selected_items: Any) -> int: ...

        def _pretty_tags(self, tags: Any) -> str: ...


class SourcesDialogMixin:
    # Sources import dialog UI

    _CSS_KEY = "fs.sources_dialog"

    def _install_sources_css(self) -> None:
        css = b"""
        .fs-sources-dialog { }
        .fs-sources-wrap { padding: 10px; }

        .fs-sources-panel {
            padding: 8px 10px;
            border-radius: 10px;
            border: 1px solid rgba(0,0,0,0.10);
            background-color: rgba(0,0,0,0.03);
        }

        .fs-sources-legend {
            padding: 6px 8px;
            border-radius: 10px;
            border: 1px solid rgba(0,0,0,0.10);
            background-color: rgba(0,0,0,0.03);
        }

        .fs-sources-treeview header button {
            font-weight: 700;
        }
        """
        fs_ui.install_css_once(self._CSS_KEY, css)

    def _import_sources_dialog(self, gr: Any, fsid: str) -> None:
        deps = cast("_SourcesDialogDeps", self)

        items = self._collect_fs_sources(fsid)
        if not items:
            OkDialog(_("No FamilySearch sources found to import."))
            return

        self._install_sources_css()

        by_sdid: Dict[str, List[Any]] = {}
        citation_handles: set[str] = set(gr.get_citation_list())

        for er in gr.get_event_ref_list():
            ev = deps.dbstate.db.get_event_from_handle(er.ref)
            citation_handles.update(ev.get_citation_list())

        for fam_h in gr.get_family_handle_list():
            fam = deps.dbstate.db.get_family_from_handle(fam_h)
            citation_handles.update(fam.get_citation_list())
            for er in fam.get_event_ref_list():
                ev = deps.dbstate.db.get_event_from_handle(er.ref)
                citation_handles.update(ev.get_citation_list())

        for ch in citation_handles:
            c = deps.dbstate.db.get_citation_from_handle(ch)
            sdid = fs_utilities.get_fsftid(c)
            if sdid:
                by_sdid.setdefault(sdid, []).append(c)

        def detect_color_for_sdid(sdid: str) -> str:
            if sdid not in by_sdid:
                return "yellow3"

            sd = deserialize.SourceDescription._index.get(sdid)
            if not sd:
                return "orange"

            src_fs = fs_import.IntermediateSource()
            src_fs.from_fs(sd, None)

            fs_title = src_fs.citation_title or ""
            fs_text = src_fs.note_text or ""
            fs_date = str(src_fs.date) if getattr(src_fs, "date", "") else ""
            fs_url = src_fs.url or ""

            for c in by_sdid.get(sdid, []):
                src_gr = fs_import.IntermediateSource()
                src_gr.from_gramps(deps.dbstate.db, c)

                title = src_gr.citation_title or ""
                note_text = (src_gr.note_text or "").strip()
                gr_url = src_gr.url or ""
                date = fs_utilities.gramps_date_to_formal(c.date)

                if (
                    fs_date == date
                    and fs_title == title
                    and fs_url == gr_url
                    and (fs_text or "").strip() == note_text
                ):
                    return "green"

            return "orange"

        dlg = Gtk.Dialog(
            title=_("Import FamilySearch sources"),
            transient_for=deps.uistate.window,
            flags=0,
        )
        dlg.get_style_context().add_class("fs-sources-dialog")
        fs_ui.set_headerbar(dlg, _("Import FamilySearch sources"), subtitle=fsid or "")

        dlg.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        dlg.add_button(_("Import selected"), Gtk.ResponseType.OK)

        box = dlg.get_content_area()
        box.set_spacing(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)

        images_by_sdid: Dict[str, List[str]] = {}
        last_dir = deps.CONFIG.get("preferences.fs_image_download_dir") or ""

        # store:
        # 0 import?, 1 bg_color_token, 2 action text, 3 auto_kind, 4 chosen kind,
        # 5 title, 6 date, 7 url, 8 tags, 9 contributor, 10 sdid, 11 img_count, 12 add_to_person_gallery
        store = Gtk.ListStore(
            bool, str, str, str, str, str, str, str, str, str, str, int, bool
        )

        for sdid, auto_kind, title, date_s, url, tags, contributor in items:
            color_token = detect_color_for_sdid(sdid)
            store.append(
                [
                    True,
                    color_token,
                    "",
                    auto_kind or "",
                    "Auto",
                    title or "",
                    date_s or "",
                    url or "",
                    tags or "",
                    contributor or "",
                    sdid,
                    0,
                    True,
                ]
            )

        treeview = Gtk.TreeView(model=store)
        treeview.set_activate_on_single_click(True)
        treeview.get_style_context().add_class("fs-sources-treeview")
        fs_ui.tune_treeview(treeview)

        # import toggle
        toggle = Gtk.CellRendererToggle()
        toggle.connect(
            "toggled", lambda _w, path: store[path].__setitem__(0, not store[path][0])
        )
        col0 = Gtk.TreeViewColumn(_("Import"), toggle, active=0)

        # color indicator column
        color_cell = Gtk.CellRendererText()
        color_col = Gtk.TreeViewColumn(" ", color_cell)

        def _color_cell_data_func(_col, cell, model, itr, _data=None):
            token = model.get_value(itr, 1) or ""
            fs_ui.set_cell_bg(cell, token, widget=treeview)
            try:
                cell.set_property("text", "")
            except Exception:
                pass

        color_col.set_cell_data_func(color_cell, _color_cell_data_func)

        try:
            color_col.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            color_col.set_fixed_width(20)
        except Exception:
            pass

        # detected kind
        col_auto = Gtk.TreeViewColumn(_("Detected"), Gtk.CellRendererText(), text=3)

        # Combo: Import as
        kind_model = Gtk.ListStore(str)
        for v in ("Auto", "Direct", "Mention"):
            kind_model.append([v])

        cell_combo = Gtk.CellRendererCombo()
        cell_combo.set_property("editable", True)
        cell_combo.set_property("model", kind_model)
        cell_combo.set_property("text-column", 0)
        cell_combo.set_property("has-entry", False)

        def on_combo_edited(_cell, path, new_text):
            if new_text in ("Auto", "Direct", "Mention"):
                store[path][4] = new_text

        cell_combo.connect("edited", on_combo_edited)
        col_kind = Gtk.TreeViewColumn(_("Import as"), cell_combo, text=4)

        # Text columns
        cr_title = Gtk.CellRendererText()
        try:
            cr_title.set_property("wrap-mode", 2)
            cr_title.set_property("wrap-width", 520)
        except Exception:
            pass
        col_title = Gtk.TreeViewColumn(_("Title"), cr_title, text=5)

        col_date = Gtk.TreeViewColumn(_("FS Date"), Gtk.CellRendererText(), text=6)

        cr_url = Gtk.CellRendererText()
        try:
            cr_url.set_property("underline", 1)
            cr_url.set_property("foreground", "steelblue")
        except Exception:
            pass
        col_url = Gtk.TreeViewColumn(_("URL"), cr_url, text=7)

        cr_tags = Gtk.CellRendererText()
        try:
            cr_tags.set_property("wrap-mode", 2)
            cr_tags.set_property("wrap-width", 360)
        except Exception:
            pass
        col_tags = Gtk.TreeViewColumn(_("Tags"), cr_tags, text=8)

        col_con = Gtk.TreeViewColumn(_("Contributor"), Gtk.CellRendererText(), text=9)
        col_img_ct = Gtk.TreeViewColumn(_("Images"), Gtk.CellRendererText(), text=11)

        cr_person = Gtk.CellRendererToggle()

        def _on_person_gallery_toggled(_w, path):
            store[path][12] = not store[path][12]

        cr_person.connect("toggled", _on_person_gallery_toggled)
        col_person = Gtk.TreeViewColumn(_("To Person gallery"), cr_person, active=12)

        # Actions
        action_cell = Gtk.CellRendererText()
        if Pango is not None:
            try:
                action_cell.set_property("underline", Pango.Underline.SINGLE)
                action_cell.set_property("foreground", "steelblue")
            except Exception:
                pass
        else:
            try:
                action_cell.set_property("underline", 1)
                action_cell.set_property("foreground", "steelblue")
            except Exception:
                pass

        action_col = Gtk.TreeViewColumn(_("Actions"), action_cell, text=2)

        def _action_cell_data_func(_col, cell, _model, _itr, _data=None):
            cell.set_property("text", _("Manage Images…"))

        action_col.set_cell_data_func(action_cell, _action_cell_data_func)

        for col in (
            col0,
            color_col,
            col_auto,
            col_kind,
            col_title,
            col_date,
            col_url,
            col_tags,
            col_con,
            col_img_ct,
            col_person,
            action_col,
        ):
            treeview.append_column(col)

        try:
            col_title.set_expand(True)
            col_url.set_expand(True)
        except Exception:
            pass

        # ---------------- Manage images dialog ----------------

        def manage_images_for_sdid(sdid: str, url_for_picker: str) -> int:
            nonlocal last_dir

            def _sanitize_base(name: str) -> str:
                base = (name or "").strip()
                if not base:
                    base = "image"
                base = re.sub(r'[\\\/<>:"|?*\n\r\t]+', "_", base)
                return base

            imgs = images_by_sdid.setdefault(sdid, [])

            dlg2 = Gtk.Dialog(title=_("Manage images"), transient_for=dlg, flags=0)
            dlg2.get_style_context().add_class("fs-sources-dialog")
            fs_ui.set_headerbar(dlg2, _("Manage images"), subtitle=sdid or "")
            dlg2.add_button(_("Close"), Gtk.ResponseType.CLOSE)

            actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            actions.get_style_context().add_class("fs-sources-panel")

            btn_add = Gtk.Button(label=_("Add from source…"))
            btn_add.set_tooltip_text(_("Open the source page and download images"))

            btn_choose = Gtk.Button(label=_("Choose file…"))
            btn_choose.set_tooltip_text(_("Pick existing files from disk"))

            btn_rename = Gtk.Button(label=_("Rename files"))
            btn_rename.set_tooltip_text(_("Rename selected files on disk"))

            actions.pack_start(btn_add, False, False, 0)
            actions.pack_start(btn_choose, False, False, 0)
            actions.pack_end(btn_rename, False, False, 0)

            box2 = dlg2.get_content_area()
            box2.set_spacing(10)
            box2.set_margin_top(10)
            box2.set_margin_bottom(10)
            box2.set_margin_start(10)
            box2.set_margin_end(10)

            box2.pack_start(actions, False, False, 0)

            # cols: dir, base, ext, fullpath
            model = Gtk.ListStore(str, str, str, str)

            def _split_path(p: str) -> Tuple[str, str, str]:
                d, fname = os.path.split(p)
                base, ext = os.path.splitext(fname)
                return d, base, ext or ""

            for p in imgs:
                d, b, ext = _split_path(p)
                model.append([d, b, ext, p])

            tv = Gtk.TreeView(model=model)
            fs_ui.tune_treeview(tv)

            cr_base = Gtk.CellRendererText()
            cr_base.set_property("editable", True)

            def on_base_edited(_cell, path, new_text):
                row = model[path]
                row[1] = _sanitize_base(new_text)

            cr_base.connect("edited", on_base_edited)
            col_base = Gtk.TreeViewColumn(
                _("Filename (without extension)"), cr_base, text=1
            )

            cr_ext = Gtk.CellRendererText()
            col_ext = Gtk.TreeViewColumn(_("Extension"), cr_ext, text=2)

            tv.append_column(col_base)
            tv.append_column(col_ext)

            sw2 = fs_ui.wrap_scroller(tv, min_h=260)

            help_lbl = Gtk.Label()
            help_lbl.set_xalign(0)
            help_lbl.set_line_wrap(True)
            help_lbl.get_style_context().add_class("fs-muted")
            help_lbl.set_text(
                _(
                    "Tips:\n"
                    "• Double-click the name to edit.\n"
                    "• Extensions are preserved.\n"
                    "• If a file with the new name exists, a numeric suffix will be added."
                )
            )

            v2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            v2.pack_start(help_lbl, False, False, 0)
            v2.pack_start(sw2, True, True, 0)
            box2.add(v2)

            def _refresh_imgs_from_model() -> List[str]:
                new_list: List[str] = []
                for d, b, ext, _old in model:
                    new_list.append(os.path.join(d, b + ext))
                return new_list

            def do_add(_btn):
                nonlocal last_dir
                if not _has_img_picker or fs_source_image is None:
                    WarningDialog(_("Image picker module is not available."))
                    return
                try:
                    saved = fs_source_image.pick_images(
                        url_for_picker,
                        parent_window=dlg2,
                        start_dir=last_dir,
                        title=_("Add Source Image"),
                    )
                except Exception as ex:
                    WarningDialog(
                        _("Could not open image picker:\n{e}").format(e=str(ex))
                    )
                    return
                if not saved:
                    return
                for p in saved:
                    d, b, ext = _split_path(p)
                    model.append([d, b, ext, p])

                last_dir_local = os.path.dirname(saved[0]) if saved else last_dir
                if last_dir_local:
                    last_dir = last_dir_local
                    deps.CONFIG.set("preferences.fs_image_download_dir", last_dir)
                    deps.CONFIG.save()

            def do_choose(_btn):
                nonlocal last_dir
                dlg_pick = Gtk.FileChooserDialog(
                    title=_("Choose image file(s)"),
                    parent=dlg2,
                    action=Gtk.FileChooserAction.OPEN,
                    buttons=(
                        _("Cancel"),
                        Gtk.ResponseType.CANCEL,
                        _("Select"),
                        Gtk.ResponseType.OK,
                    ),
                )
                try:
                    dlg_pick.set_select_multiple(True)
                except Exception:
                    pass

                try:
                    flt = Gtk.FileFilter()
                    flt.set_name(_("Images"))
                    flt.add_mime_type("image/*")
                    dlg_pick.add_filter(flt)
                    flt2 = Gtk.FileFilter()
                    flt2.set_name(_("All files"))
                    flt2.add_pattern("*")
                    dlg_pick.add_filter(flt2)
                except Exception:
                    pass

                if last_dir and os.path.isdir(last_dir):
                    try:
                        dlg_pick.set_current_folder(last_dir)
                    except Exception:
                        pass

                resp = dlg_pick.run()
                paths: List[str] = []
                if resp == Gtk.ResponseType.OK:
                    try:
                        paths = dlg_pick.get_filenames() or []
                    except Exception:
                        p = dlg_pick.get_filename()
                        paths = [p] if p else []
                dlg_pick.destroy()

                if not paths:
                    return

                for p in paths:
                    d, b, ext = _split_path(p)
                    model.append([d, b, ext, p])

                last_dir_local = os.path.dirname(paths[0]) if paths else last_dir
                if last_dir_local:
                    last_dir = last_dir_local
                    deps.CONFIG.set("preferences.fs_image_download_dir", last_dir)
                    deps.CONFIG.save()

            def do_rename(_btn):
                for row in list(model):
                    d, b_new, ext, full_old = row[:]
                    d = d or ""
                    b_new = (b_new or "").strip()

                    d_old, fname_old = os.path.split(full_old)
                    base_old, ext_old = os.path.splitext(fname_old)

                    if d_old and not d:
                        d = d_old
                    if not ext:
                        ext = ext_old

                    if base_old == b_new and d_old == d and ext_old == ext:
                        continue

                    def _unique_path(dirpath: str, base: str, ext2: str) -> str:
                        candidate = os.path.join(dirpath, base + ext2)
                        if not os.path.exists(candidate):
                            return candidate
                        i = 1
                        while True:
                            candidate = os.path.join(dirpath, f"{base} ({i}){ext2}")
                            if not os.path.exists(candidate):
                                return candidate
                            i += 1

                    target = _unique_path(d or d_old, b_new, ext)
                    try:
                        os.rename(full_old, target)
                        d_new, fname_new = os.path.split(target)
                        base_new, ext_new = os.path.splitext(fname_new)
                        row[0] = d_new
                        row[1] = base_new
                        row[2] = ext_new
                        row[3] = target
                    except Exception as ex:
                        WarningDialog(
                            _("Rename failed for:\n{p}\n\n{err}").format(
                                p=full_old, err=str(ex)
                            )
                        )

                images_by_sdid[sdid] = _refresh_imgs_from_model()

            btn_add.connect("clicked", do_add)
            btn_choose.connect("clicked", do_choose)
            btn_rename.connect("clicked", do_rename)

            dlg2.show_all()
            dlg2.run()
            dlg2.destroy()

            images_by_sdid[sdid] = _refresh_imgs_from_model()
            return len(images_by_sdid[sdid])

        def on_row_activated(_tv, path, column):
            if column is not action_col:
                return
            row = store[path]
            sdid = row[10]
            source_url = row[7] or ""
            new_count = manage_images_for_sdid(sdid, source_url)
            row[11] = new_count

        treeview.connect("row-activated", on_row_activated)

        # top controls row
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        top.get_style_context().add_class("fs-sources-panel")

        btn_all = Gtk.CheckButton.new_with_label(_("Select all"))
        btn_all.set_active(True)

        def on_all_toggled(btn):
            val = btn.get_active()
            for row in store:
                row[0] = val

        btn_all.connect("toggled", on_all_toggled)
        top.pack_start(btn_all, False, False, 0)

        # main layout
        box.pack_start(top, False, False, 0)
        box.pack_start(
            fs_ui.build_legend_row(
                [
                    ("green", _("Match")),
                    ("orange", _("Different")),
                    ("yellow3", _("Only in FamilySearch")),
                ],
                hint=_(
                    "Tip: click “Manage Images…” to add/choose/rename files before importing."
                ),
                wrap_class="fs-sources-legend",
            ),
            False,
            False,
            0,
        )
        box.pack_start(fs_ui.wrap_scroller(treeview, min_h=420), True, True, 0)

        dlg.show_all()
        resp = dlg.run()
        if resp != Gtk.ResponseType.OK:
            dlg.destroy()
            return

        source_meta = deps._gather_sr_meta(fsid)

        selected_items: List[Tuple[str, str, str, str, List[str], bool]] = []
        for row in store:
            if not row[0]:
                continue

            sdid = row[10]
            auto_kind = row[3] or "Mention"
            chosen = row[4] or "Auto"
            final_kind = auto_kind if chosen == "Auto" else chosen
            contributor = row[9] or ""

            modified = (source_meta.get(sdid, {}) or {}).get("modified", "")
            img_list = images_by_sdid.get(sdid, [])[:]
            add_to_person = bool(row[12])

            selected_items.append(
                (sdid, modified, contributor, final_kind, img_list, add_to_person)
            )

        dlg.destroy()
        if not selected_items:
            return

        count = deps._import_fs_sources(gr, selected_items)
        OkDialog(_("{n} source(s) imported.").format(n=count))

    # ------------------
    # Data collection
    # ------------------

    def _collect_fs_sources(
        self, fsid: str
    ) -> List[Tuple[str, str, str, str, str, str, str]]:
        deps = cast("_SourcesDialogDeps", self)

        deps._ensure_sources_cached(fsid)
        fs_person = deserialize.Person.index.get(fsid)
        if not fs_person:
            return []

        meta = deps._gather_sr_meta(fsid)

        sdids: set[str] = set()
        for sr in getattr(fs_person, "sources", []) or []:
            sdids.add(getattr(sr, "descriptionId", ""))
        for rel in getattr(fs_person, "_spouses", []) or []:
            for sr in getattr(rel, "sources", []) or []:
                sdids.add(getattr(sr, "descriptionId", ""))

        for sdid in list(sdids):
            if not sdid:
                continue
            if sdid not in deserialize.SourceDescription._index:
                sd_new = deserialize.SourceDescription()
                sd_new.id = sdid
                deserialize.SourceDescription._index[sdid] = sd_new
                deps.fs_Tree.sourceDescriptions.add(sd_new)

        fs_import.fetch_source_dates(deps.fs_Tree)

        out: List[Tuple[str, str, str, str, str, str, str]] = []
        for sdid in sdids:
            if not sdid:
                continue
            sd_obj = deserialize.SourceDescription._index.get(sdid)
            if sd_obj is None:
                continue

            isrc = fs_import.IntermediateSource()
            isrc.from_fs(sd_obj, None)
            title = isrc.citation_title or ""
            date_s = str(isrc.date) if getattr(isrc, "date", "") else ""
            url = isrc.url or ""
            m = meta.get(sdid, {})
            auto_kind = m.get("kind", "Mention")
            tags_disp = deps._pretty_tags(m.get("tags", []))
            contributor = m.get("contributor", "")
            out.append((sdid, auto_kind, title, date_s, url, tags_disp, contributor))

        return out
