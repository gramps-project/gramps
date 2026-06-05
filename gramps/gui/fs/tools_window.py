# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025-2026 Gabriel Rios
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
FamilySearch tools window for the gtk side of the integration.
it tracks the active Edit Person context, then routes button clicks into the
existing actions/sync helpers
"""

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
import gc
import os
import sys
import weakref
from dataclasses import dataclass
from typing import Any, Callable, Optional, cast

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import GdkPixbuf, GLib, Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import DATA_DIR, GRAMPS_LOCALE as glocale
from gramps.gen.const import IMAGE_DIR as _GRAMPS_IMAGE_DIR
from gramps.gen.display.name import displayer as name_displayer
from gramps.gui.dialog import ErrorDialog
from gramps.gui.editors.editperson import EditPerson
from gramps.gen.errors import HandleError

from . import actions
from . import sync_directions as fs_syncdir
from . import ui as fs_ui
from .tags import build_tag_color_note_widget

_ = glocale.translation.gettext

_SINGLETON: Optional["FamilySearchToolsWindow"] = None
_EDITPERSON_HOOK_INSTALLED = False


def _dbg(message: str) -> None:
    enabled = os.environ.get("GRAMPS_FS_DEBUG", "").strip().lower()
    if enabled in {"1", "true", "yes", "on"}:
        sys.stderr.write(f"[FS TOOLS] {message}\n")
        sys.stderr.flush()


def _show_error(parent: Gtk.Window, title: str, message: str) -> None:
    # If Gramps dialog path doesnt load up for some reason, still show something
    try:
        ErrorDialog(title, message, parent=parent)
    except Exception:
        fs_ui.error_dialog(parent, title, message)


def _show_info(parent: Gtk.Window, title: str, message: str) -> None:
    fs_ui.info_dialog(parent, title, message)


def _person_handle(person: Any) -> Optional[str]:
    handle_getter = getattr(person, "get_handle", None)
    if callable(handle_getter):
        try:
            handle = handle_getter()
        except Exception:
            return None
    else:
        handle = getattr(person, "handle", None)

    return handle if isinstance(handle, str) and handle else None


def _person_exists_in_db(dbstate: Any, handle: str) -> bool:
    """Check that the current person handle really resolves in the db."""
    db = getattr(dbstate, "db", None)
    if db is None or not handle:
        return False

    has_person_handle = getattr(db, "has_person_handle", None)
    if callable(has_person_handle):
        try:
            return bool(has_person_handle(handle))
        except Exception:
            return False

    # exceptions so it doesnt crash when there's a new tree with no one in it & FS is connected
    try:
        db.get_person_from_handle(handle)
        return True
    except HandleError:
        return False
    except Exception:
        return False


def _get_editor_window(editor: Any) -> Any:
    window = getattr(editor, "window", None)
    if window is not None:
        return window

    top = getattr(editor, "top", None)
    if top is None:
        return None

    return getattr(top, "toplevel", None)


@dataclass
class _EditorCtx:
    """Last known Edit Person context for the tools window singleton."""

    dbstate: Any = None
    uistate: Any = None
    track: Any = None
    person_handle: Optional[str] = None
    person_obj_ref: Optional[weakref.ReferenceType[Any]] = None
    editor_ref: Optional[weakref.ReferenceType[Any]] = None

    def person_obj(self) -> Any:
        return self.person_obj_ref() if self.person_obj_ref else None

    def editor_obj(self) -> Any:
        return self.editor_ref() if self.editor_ref else None


_LAST_EDITOR = _EditorCtx()


def notify_from_person_editor(
    dbstate: Any,
    uistate: Any,
    track: Any,
    person: Any,
    editor: Any = None,
) -> None:
    """Refresh the shared editor context from the active Edit Person window."""
    global _LAST_EDITOR

    person_handle = _person_handle(person)
    if not person_handle:
        return

    _LAST_EDITOR.dbstate = dbstate
    _LAST_EDITOR.uistate = uistate
    _LAST_EDITOR.track = track
    _LAST_EDITOR.person_handle = person_handle

    try:
        _LAST_EDITOR.person_obj_ref = weakref.ref(person)
    except TypeError:
        _LAST_EDITOR.person_obj_ref = None

    try:
        _LAST_EDITOR.editor_ref = weakref.ref(editor) if editor is not None else None
    except TypeError:
        _LAST_EDITOR.editor_ref = None

    if _SINGLETON is not None and _SINGLETON.is_alive():
        GLib.idle_add(_SINGLETON._on_editor_ctx_changed)

    _dbg(f"notify_from_person_editor: handle={person_handle}")


def _install_editperson_hook() -> None:
    """Hook EditPerson once so the tools window can follow focus/context changes."""
    global _EDITPERSON_HOOK_INSTALLED

    if _EDITPERSON_HOOK_INSTALLED:
        return

    editor_class = cast(Any, EditPerson)

    if getattr(editor_class, "_fs_tools_hooked", False):
        _EDITPERSON_HOOK_INSTALLED = True
        return

    original_post_init = getattr(editor_class, "_post_init", None)
    if not callable(original_post_init):
        _dbg("EditPerson._post_init is not callable; skipping hook install")
        return

    def _attach_editor_hook(editor: Any) -> None:
        if getattr(editor, "_fs_tools_hook_attached", False):
            return

        setattr(editor, "_fs_tools_hook_attached", True)

        def _fire() -> bool:
            # This runs from GTK callbacks
            try:
                notify_from_person_editor(
                    editor.dbstate,
                    editor.uistate,
                    editor.track,
                    editor.obj,
                    editor=editor,
                )
            except Exception as exc:
                _dbg(f"Could not refresh editor context: {exc}")
            return False

        GLib.idle_add(_fire)

        window = _get_editor_window(editor)
        if window is not None:
            window.connect("focus-in-event", lambda *_args: _fire())
            window.connect("map-event", lambda *_args: _fire())

    def wrapped_post_init(editor: Any, *args: Any, **kwargs: Any) -> Any:
        result = original_post_init(editor, *args, **kwargs)
        _attach_editor_hook(editor)
        return result

    setattr(editor_class, "_post_init", wrapped_post_init)
    setattr(editor_class, "_fs_tools_hooked", True)
    _EDITPERSON_HOOK_INSTALLED = True
    _dbg("Installed EditPerson hook for FamilySearch Tools")


def _find_open_editperson_instance() -> Any:
    """Best-effort search for a visible Edit Person window to latch onto."""
    app = Gtk.Application.get_default()
    active_window = app.get_active_window() if app is not None else None
    fallback_editor = None

    for obj in gc.get_objects():
        if not isinstance(obj, EditPerson):
            continue

        window = _get_editor_window(obj)
        if window is None or not window.get_visible():
            continue

        if active_window is not None and window is active_window:
            return obj

        fallback_editor = obj

    return fallback_editor


def close_tools_window() -> None:
    """Close the singleton tools window if it is open."""
    global _SINGLETON

    if _SINGLETON is None:
        return

    if _SINGLETON.is_alive():
        _SINGLETON.window.destroy()

    _SINGLETON = None


def toggle_tools_window(session: Any, dbstate: Any = None, uistate: Any = None) -> None:
    """Toggle the singleton tools window on/off."""
    global _SINGLETON

    _install_editperson_hook()

    if _SINGLETON is not None and _SINGLETON.is_alive():
        close_tools_window()
        return

    _SINGLETON = FamilySearchToolsWindow(session=session)
    _SINGLETON.present()


def present_tools_window(
    session: Any, dbstate: Any = None, uistate: Any = None
) -> None:
    global _SINGLETON

    _install_editperson_hook()

    if _SINGLETON is not None and _SINGLETON.is_alive():
        _SINGLETON.present()
        return

    _SINGLETON = FamilySearchToolsWindow(session=session)
    _SINGLETON.present()


class FamilySearchToolsWindow:
    """control window for the main FamilySearch actions"""

    _BANNER_MAX_HEIGHT = 120
    _BANNER_MIN_HEIGHT = 64
    _BANNER_SIDE_PAD = 10

    def __init__(self, session: Any):
        self.session = session
        self._tick_id: Optional[int] = None

        self._logo_pixbuf_orig: Optional[GdkPixbuf.Pixbuf] = None
        self._logo_last_width = 0
        self._logo_image: Optional[Gtk.Image] = None

        self.window = Gtk.Window(title=_("FamilySearch Tools"))
        self.window.set_default_size(820, 430)
        self.window.set_border_width(12)
        self.window.get_style_context().add_class("fs-tools-window")

        self._install_css()

        # layout is simple on purpose, status row, person actions, imports & utilities
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.window.add(outer)

        banner = self._build_banner()
        if banner is not None:
            outer.pack_start(banner, False, False, 0)

        status_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        status_row.get_style_context().add_class("fs-status-row")
        outer.pack_start(status_row, False, False, 0)

        status_widget = None
        get_status_widget = getattr(self.session, "get_status_widget", None)
        if callable(get_status_widget):
            status_widget = get_status_widget()

        if status_widget is not None:
            status_widget.set_halign(Gtk.Align.START)
            status_row.pack_start(status_widget, False, False, 0)

        self.active_label = Gtk.Label(label=_("Editor person: (none)"))
        self.active_label.set_xalign(0.0)
        self.active_label.set_ellipsize(3)
        self.active_label.get_style_context().add_class("fs-active-label")
        status_row.pack_start(self.active_label, True, True, 0)

        outer.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
            False,
            False,
            0,
        )

        self._size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.BOTH)

        sec_person, box_person = self._make_section(
            _("Person actions"), "fs-sec-person"
        )
        outer.pack_start(sec_person, False, False, 0)

        self.btn_link = Gtk.Button(label=_("Link FamilySearch ID"))
        self.btn_cmp = Gtk.Button(label=_("Compare"))
        self.btn_sync = Gtk.Button(label=_("Sync from FamilySearch"))
        self.btn_sync.get_style_context().add_class("suggested-action")

        self.btn_sync_to = Gtk.Button(label=_("Sync to FamilySearch..."))
        self.btn_sync_to.set_tooltip_text(
            _("Overwrite selected FamilySearch fields with Gramps values (no deletes).")
        )

        self.btn_export_basic = Gtk.Button(label=_("Export to FamilySearch (basic)..."))
        self.btn_export_basic.set_tooltip_text(
            _(
                "Create missing people on FamilySearch and link relationships (name + birth/death)."
            )
        )

        for button in (
            self.btn_link,
            self.btn_cmp,
            self.btn_sync,
            self.btn_sync_to,
            self.btn_export_basic,
        ):
            self._add_btn(box_person, button)

        sec_import, box_import = self._make_section(
            _("Import relatives"), "fs-sec-import"
        )
        outer.pack_start(sec_import, False, False, 0)

        self.btn_imp_par = Gtk.Button(label=_("Import Parents"))
        self.btn_imp_spo = Gtk.Button(label=_("Import Spouse"))
        self.btn_imp_chi = Gtk.Button(label=_("Import Children"))

        for button in (self.btn_imp_par, self.btn_imp_spo, self.btn_imp_chi):
            self._add_btn(box_import, button)

        sec_util, box_util = self._make_section(_("Utilities"), "fs-sec-util")
        outer.pack_start(sec_util, False, False, 0)

        self.btn_tags = Gtk.Button(label=_("Tags..."))
        self.btn_clear_cache = Gtk.Button(label=_("Clear Cache"))
        self.btn_clear_cache.get_style_context().add_class("destructive-action")

        self._add_btn(box_util, self.btn_tags)
        self._add_btn(box_util, self.btn_clear_cache)

        note = build_tag_color_note_widget()
        if note is not None:
            note.set_margin_top(6)
            util_inner = sec_util.get_child()
            if isinstance(util_inner, Gtk.Box):
                util_inner.pack_start(note, False, False, 0)

        self.btn_link.connect("clicked", self._on_link)
        self.btn_cmp.connect("clicked", self._on_compare)
        self.btn_sync.connect("clicked", self._on_sync)
        self.btn_sync_to.connect("clicked", self._on_sync_to)
        self.btn_export_basic.connect("clicked", self._on_export_basic)

        self.btn_imp_par.connect("clicked", self._on_import_parents)
        self.btn_imp_spo.connect("clicked", self._on_import_spouse)
        self.btn_imp_chi.connect("clicked", self._on_import_children)

        self.btn_tags.connect("clicked", self._on_tags)
        self.btn_clear_cache.connect("clicked", self._on_clear_cache)

        self.window.connect("destroy", self._on_destroy)
        self.window.show_all()

        editor = _find_open_editperson_instance()
        if editor is not None:
            notify_from_person_editor(
                editor.dbstate,
                editor.uistate,
                editor.track,
                editor.obj,
                editor=editor,
            )

        self._tick_id = GLib.timeout_add_seconds(1, self._tick)
        self._tick()

    def _install_css(self) -> None:
        """Install the shared gramps.css file for the tools window."""
        candidate_paths = [
            self._repo_gramps_css_path(),
            os.path.join(DATA_DIR, "gramps.css"),
        ]
        for css_path in candidate_paths:
            try:
                if not os.path.isfile(css_path):
                    continue
                with open(css_path, "rb") as handle:
                    css = handle.read()
                if fs_ui.install_css_once("fs.tools_window", css):
                    _dbg(f"Loaded tools CSS from {css_path}")
                    return
            except Exception:
                continue

    @staticmethod
    def _repo_gramps_css_path() -> str:
        """Return this project copy of data/gramps.css before falling back to DATA_DIR."""
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "data", "gramps.css"
            )
        )

    def _make_section(
        self, title: str, css_class: str
    ) -> tuple[Gtk.Widget, Gtk.FlowBox]:
        """Build one titled button section."""
        wrapper = Gtk.EventBox()
        wrapper.set_visible_window(True)

        style = wrapper.get_style_context()
        style.add_class("fs-section")
        style.add_class(css_class)

        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        inner.set_border_width(10)
        wrapper.add(inner)

        label = Gtk.Label()
        label.set_markup(
            f"<span size='large'><b>{GLib.markup_escape_text(title)}</b></span>"
        )
        label.set_xalign(0.0)
        label.get_style_context().add_class("fs-section-title")
        inner.pack_start(label, False, False, 0)

        inner.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
            False,
            False,
            0,
        )

        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_row_spacing(8)
        flow.set_column_spacing(8)
        flow.set_max_children_per_line(6)
        flow.set_min_children_per_line(2)
        inner.pack_start(flow, False, False, 0)

        return wrapper, flow

    def _add_btn(self, flow: Gtk.FlowBox, button: Gtk.Button) -> None:
        button.set_can_focus(True)
        self._size_group.add_widget(button)

        child = Gtk.FlowBoxChild()
        child.add(button)
        flow.add(child)

    def _build_banner(self) -> Optional[Gtk.Widget]:
        """Build the banner/logo row if the image is available."""
        pixbuf = self._load_logo_pixbuf()
        if pixbuf is None:
            _dbg("FamilySearch logo not found; banner disabled")
            return None

        self._logo_pixbuf_orig = pixbuf

        wrapper = Gtk.EventBox()
        wrapper.set_visible_window(True)
        wrapper.get_style_context().add_class("fs-banner")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_border_width(self._BANNER_SIDE_PAD)
        wrapper.add(box)

        self._logo_image = Gtk.Image()
        self._logo_image.set_halign(Gtk.Align.FILL)
        self._logo_image.set_valign(Gtk.Align.CENTER)
        box.pack_start(self._logo_image, True, True, 0)

        width = self.window.get_size()[0]
        self._set_logo_width(width)

        wrapper.connect("size-allocate", self._on_banner_size_allocate)
        return wrapper

    def _load_logo_pixbuf(self) -> Optional[GdkPixbuf.Pixbuf]:
        candidates: list[str] = []

        if _GRAMPS_IMAGE_DIR:
            candidates.append(os.path.join(_GRAMPS_IMAGE_DIR, "fs_logo.png"))

        repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        candidates.append(os.path.join(repo_root, "images", "fs_logo.png"))
        candidates.append(os.path.join(os.path.dirname(__file__), "fs_logo.png"))

        for path in candidates:
            if path and os.path.isfile(path):
                _dbg(f"Loading FS logo from {path}")
                return GdkPixbuf.Pixbuf.new_from_file(path)

        return None

    def _on_banner_size_allocate(self, _widget: Any, allocation: Any) -> None:
        width = int(getattr(allocation, "width", 0) or 0)
        if width <= 0:
            return

        if abs(width - self._logo_last_width) < 12:
            return

        self._logo_last_width = width
        self._set_logo_width(width)

    def _set_logo_width(self, container_width: int) -> None:
        if self._logo_pixbuf_orig is None or self._logo_image is None:
            return

        original_width = self._logo_pixbuf_orig.get_width()
        original_height = self._logo_pixbuf_orig.get_height()
        if original_width <= 0 or original_height <= 0:
            return

        available_width = max(
            1, int(container_width) - (self._BANNER_SIDE_PAD * 2) - 24
        )
        scale = available_width / float(original_width)

        new_width = int(original_width * scale)
        new_height = int(original_height * scale)

        if new_height > self._BANNER_MAX_HEIGHT:
            new_height = self._BANNER_MAX_HEIGHT
            scale = new_height / float(original_height)
            new_width = max(1, int(original_width * scale))

        if new_height < self._BANNER_MIN_HEIGHT:
            new_height = self._BANNER_MIN_HEIGHT
            scale = new_height / float(original_height)
            new_width = max(1, int(original_width * scale))

        scaled = self._logo_pixbuf_orig.scale_simple(
            new_width,
            new_height,
            GdkPixbuf.InterpType.BILINEAR,
        )
        self._logo_image.set_from_pixbuf(scaled)

    def is_alive(self) -> bool:
        return self.window is not None and self.window.get_visible() is not None

    def present(self) -> None:
        self.window.present()

    def _on_destroy(self, *_args: Any) -> None:
        global _SINGLETON

        _SINGLETON = None

        if self._tick_id is not None:
            GLib.source_remove(self._tick_id)
            self._tick_id = None

    def _fs_connected(self) -> bool:
        return bool(getattr(self.session, "connected", False)) or bool(
            getattr(self.session, "access_token", None)
        )

    def _editor_person_obj(self) -> Any:
        # Return the db-backed editor person when possible
        # The DB copy is the one that matters for compare/sync logic.
        person_handle = _LAST_EDITOR.person_handle
        dbstate = _LAST_EDITOR.dbstate

        if person_handle and dbstate is not None:
            db = getattr(dbstate, "db", None)
            if db is not None:
                try:
                    return db.get_person_from_handle(person_handle)
                except HandleError:
                    pass
                except Exception as exc:
                    _dbg(
                        f"Could not get person from db for handle {person_handle}: {exc}"
                    )

        person = _LAST_EDITOR.person_obj()
        if person is not None:
            return person

        return None

    def _update_label(self) -> None:
        """Refresh the label that shows which editor person were on"""
        person = self._editor_person_obj()
        if person is None:
            self.active_label.set_text(_("Editor person: (none)"))
            return

        try:
            display_name = name_displayer.display(person)
        except Exception:
            display_name = "(person)"

        gramps_id_getter = getattr(person, "get_gramps_id", None)
        gramps_id = gramps_id_getter() if callable(gramps_id_getter) else ""

        if gramps_id:
            self.active_label.set_text(
                _("Editor person: %(name)s  [%(gid)s]")
                % {
                    "name": display_name,
                    "gid": gramps_id,
                }
            )
        else:
            self.active_label.set_text(
                _("Editor person: %(name)s") % {"name": display_name}
            )

    def _set_action_sensitivity(self, enabled: bool) -> None:
        """Enable/disable buttons based on connection state and editor readiness."""
        for button in (
            self.btn_link,
            self.btn_cmp,
            self.btn_sync,
            self.btn_sync_to,
            self.btn_export_basic,
            self.btn_imp_par,
            self.btn_imp_spo,
            self.btn_imp_chi,
        ):
            button.set_sensitive(enabled)

        self.btn_tags.set_sensitive(
            bool(self._fs_connected() and _LAST_EDITOR.dbstate is not None)
        )
        self.btn_clear_cache.set_sensitive(bool(self._fs_connected()))

    def _tick(self, *_args: Any) -> bool:
        """Periodic refresh so the floating window stays in sync with the editor."""
        _install_editperson_hook()

        person_handle = _LAST_EDITOR.person_handle
        db_ready = bool(
            person_handle
            and _LAST_EDITOR.dbstate is not None
            and _person_exists_in_db(_LAST_EDITOR.dbstate, person_handle)
        )

        self._update_label()
        self._set_action_sensitivity(bool(self._fs_connected() and db_ready))
        return True

    def _on_editor_ctx_changed(self) -> bool:
        self._tick()
        return False

    def _require_ready(self) -> Any:
        """Return the active person only when session + editor context are usable."""
        if not self._fs_connected():
            _show_info(self.window, "FamilySearch", "Not connected to FamilySearch.")
            return None

        person_handle = _LAST_EDITOR.person_handle
        if not person_handle or _LAST_EDITOR.dbstate is None:
            _show_info(
                self.window,
                "FamilySearch",
                "No Edit Person window context yet.\nOpen an Edit Person window first.",
            )
            return None

        if not _person_exists_in_db(_LAST_EDITOR.dbstate, person_handle):
            _show_info(
                self.window,
                "FamilySearch",
                "This person is not saved in the database yet.\nSave or click OK on the person first.",
            )
            return None

        person = self._editor_person_obj()
        if person is None:
            _show_info(
                self.window,
                "FamilySearch",
                "Could not resolve the active person from the database.",
            )
            return None

        return person

    def _ctx(self) -> Optional[dict[str, Any]]:
        """Build the full action context for person-specific actions."""
        person = self._require_ready()
        if person is None:
            return None

        return {
            "dbstate": _LAST_EDITOR.dbstate,
            "uistate": _LAST_EDITOR.uistate,
            "track": _LAST_EDITOR.track,
            "person": person,
            "editor": _LAST_EDITOR.editor_obj(),
            "parent": self.window,
            "session": self.session,
        }

    def _ctx_db_only(self) -> Optional[dict[str, Any]]:
        """Build context for actions that only need db/ui state."""
        if not self._fs_connected():
            _show_info(self.window, "FamilySearch", "Not connected to FamilySearch.")
            return None

        if _LAST_EDITOR.dbstate is None or _LAST_EDITOR.uistate is None:
            _show_info(
                self.window,
                "FamilySearch",
                "No UI context yet.\nOpen an Edit Person window first.",
            )
            return None

        person = None
        person_handle = _LAST_EDITOR.person_handle
        db = getattr(_LAST_EDITOR.dbstate, "db", None)

        if person_handle and db is not None:
            try:
                person = db.get_person_from_handle(person_handle)
            except HandleError:
                person = None
            except Exception as exc:
                _dbg(f"Could not get db-only person for handle {person_handle}: {exc}")
                person = None

        if person is None:
            person = _LAST_EDITOR.person_obj()

        return {
            "dbstate": _LAST_EDITOR.dbstate,
            "uistate": _LAST_EDITOR.uistate,
            "track": _LAST_EDITOR.track,
            "person": person,
            "editor": _LAST_EDITOR.editor_obj(),
            "parent": self.window,
            "session": self.session,
        }

    def _call_action(
        self,
        fn: Callable[..., Any],
        error_prefix: str,
        ctx: Optional[dict[str, Any]],
    ) -> None:
        """Call one of the action helpers with the standard editor/session context."""
        if not ctx:
            return

        try:
            fn(
                ctx["dbstate"],
                ctx["uistate"],
                ctx["track"],
                ctx["person"],
                ctx["session"],
                ctx["parent"],
                editor=ctx["editor"],
            )
        except Exception as exc:
            _show_error(self.window, "FamilySearch", f"{error_prefix}: {exc}")

    def _on_export_basic(self, *_args: Any) -> None:
        ctx = self._ctx()
        if not ctx:
            return

        fn = getattr(actions, "export_basic_to_familysearch", None)
        if callable(fn):
            self._call_action(fn, "Export failed", ctx)
            return

        fn = getattr(fs_syncdir, "export_basic_people_to_familysearch", None)
        if callable(fn):
            self._call_action(fn, "Export failed", ctx)
            return

        _show_error(
            self.window, "FamilySearch", "Export failed: no export function found."
        )

    def _on_link(self, *_args: Any) -> None:
        ctx = self._ctx()
        if not ctx:
            return

        self._call_action(actions.link_familysearch_id, "Link failed", ctx)

    def _on_compare(self, *_args: Any) -> None:
        ctx = self._ctx()
        if not ctx:
            return

        self._call_action(actions.compare_person, "Compare failed", ctx)

    def _on_sync(self, *_args: Any) -> None:
        ctx = self._ctx()
        if not ctx:
            return

        fn = getattr(actions, "sync_from_familysearch", None)
        if not callable(fn):
            fn = getattr(actions, "sync_this_person", None)

        if not callable(fn):
            _show_error(
                self.window,
                "FamilySearch",
                "Sync failed: no pull-sync function found in actions.py "
                "(expected sync_from_familysearch or sync_this_person).",
            )
            return

        self._call_action(fn, "Sync failed", ctx)

    def _on_sync_to(self, *_args: Any) -> None:
        ctx = self._ctx()
        if not ctx:
            return

        fn = getattr(actions, "sync_to_familysearch", None)
        if callable(fn):
            self._call_action(fn, "Sync to FamilySearch failed", ctx)
            return

        fn = getattr(fs_syncdir, "sync_to_familysearch", None)
        if callable(fn):
            self._call_action(fn, "Sync to FamilySearch failed", ctx)
            return

        _show_error(
            self.window,
            "FamilySearch",
            "Sync to FamilySearch failed: no push-sync function found.",
        )

    def _on_import_parents(self, *_args: Any) -> None:
        ctx = self._ctx()
        if not ctx:
            return

        self._call_action(actions.import_parents, "Import parents failed", ctx)

    def _on_import_spouse(self, *_args: Any) -> None:
        ctx = self._ctx()
        if not ctx:
            return

        self._call_action(actions.import_spouse, "Import spouse failed", ctx)

    def _on_import_children(self, *_args: Any) -> None:
        ctx = self._ctx()
        if not ctx:
            return

        self._call_action(actions.import_children, "Import children failed", ctx)

    def _on_tags(self, *_args: Any) -> None:
        ctx = self._ctx_db_only()
        if not ctx:
            return

        self._call_action(actions.tags_dialog, "Tags failed", ctx)

    def _on_clear_cache(self, *_args: Any) -> None:
        ctx = self._ctx_db_only()
        if not ctx:
            return

        self._call_action(actions.clear_cache, "Clear cache failed", ctx)
