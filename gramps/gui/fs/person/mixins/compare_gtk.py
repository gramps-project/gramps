#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2023-2026  Gabriel Rios
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

# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import re
from typing import Any, ClassVar, Optional, TYPE_CHECKING

from gi.repository import Gtk, Gdk, GLib

from gramps.gen.const import DATA_DIR, GRAMPS_LOCALE as glocale
from gramps.gui.dialog import WarningDialog
from gramps.gui.listmodel import ListModel, NOSORT, COLOR, TOGGLE
from gramps.gen.lib import Person

from gramps.gen.fs import tree
from gramps.gen.fs import utils as fs_utilities
from gramps.gen.fs.compare import compare_fs_to_gramps
import gramps.gen.fs.fs_import as fs_import
from gramps.gui.fs import tags as fs_tags
from gramps.gen.fs.fs_import import deserializer as deserialize

_ = glocale.translation.gettext


class CompareGtkMixin:
    fs_Tree: ClassVar[Any] = None
    _UI: ClassVar[dict[str, str]] = {}

    # Provided by the owning instance (tool/window) at runtime:
    dbstate: Any
    uistate: Any

    if TYPE_CHECKING:
        from gramps.gen.lib import Person as _GrPerson

        def get_active(self, category: str) -> Any: ...

        def _toggle_noop(self, *args: Any, **kwargs: Any) -> None: ...

        def _ensure_person_cached(
            self, fsid: str, *, with_relatives: bool, force: bool = False
        ) -> Any: ...

        def _ensure_notes_cached(self, fsid: str) -> None: ...

        def _ensure_sources_cached(self, fsid: str) -> None: ...

        def _gather_sr_meta(self, fsid: str) -> dict[str, Any]: ...

        def _pretty_tags(self, tags: Any) -> str: ...

        def _import_sources_dialog(
            self, gr: Optional[_GrPerson], fsid: str
        ) -> None: ...

        def _build_compare_json(self, gr: _GrPerson, fsid: str) -> dict[str, Any]: ...

    # Color tokens produced by compare code:
    #   green   -> match
    #   orange  -> different
    #   yellow  -> only in Gramps
    #   yellow3 -> only in FamilySearch
    #   red     -> critical mismatch
    _TINT_COLOR_NAME = {
        "green": "fs_compare_match_bg",
        "orange": "fs_compare_different_bg",
        "yellow": "fs_compare_only_gramps_bg",
        "yellow3": "fs_compare_only_fs_bg",
        "red": "fs_compare_critical_bg",
    }

    _TINT_FALLBACK_HEX = {
        "green": "#D8F3DC",
        "orange": "#FFE8CC",
        "yellow": "#FFF3BF",
        "yellow3": "#D0EBFF",
        "red": "#FFE3E3",
    }

    _CSS_INSTALLED = False
    _CSS_DEFINE_CACHE: ClassVar[Optional[dict[str, str]]] = None

    def _ui_color(self, semantic: str) -> str:
        return self._UI.get((semantic or "").strip(), semantic or "")

    def _ui_row(self, row: Any) -> Any:
        if not row:
            return row
        try:
            return list(row)
        except Exception:
            return row

    def _tint_rgba_from_css(self, color_name: str) -> Optional[Gdk.RGBA]:
        try:
            win = getattr(getattr(self, "uistate", None), "window", None)
            if win is None:
                raise ValueError("no ui window")
            ok, rgba = win.get_style_context().lookup_color(color_name)
            if ok:
                return rgba
        except Exception:
            pass

        color_value = self._css_define_value(color_name)
        if color_value:
            try:
                rgba = Gdk.RGBA()
                if rgba.parse(color_value):
                    return rgba
            except Exception:
                pass
        return None

    @classmethod
    def _css_define_value(cls, color_name: str) -> str:
        if not color_name:
            return ""

        cache = cls._CSS_DEFINE_CACHE
        if cache is None:
            cache = {}
            css_path = os.path.join(DATA_DIR, "gramps.css")
            try:
                with open(css_path, "r", encoding="utf-8") as handle:
                    css_text = handle.read()
                for name, value in re.findall(
                    r"@define-color\s+([A-Za-z0-9_]+)\s+([^;]+);", css_text
                ):
                    cache[name.strip()] = value.strip()
            except Exception:
                cache = {}
            cls._CSS_DEFINE_CACHE = cache

        return cache.get(color_name, "")

    def _resolve_tint_rgba(self, token: str) -> Optional[Gdk.RGBA]:
        token = (token or "").strip()
        if not token:
            return None

        css_name = self._TINT_COLOR_NAME.get(token)
        if css_name:
            rgba = self._tint_rgba_from_css(css_name)
            if rgba is not None:
                return rgba

        fallback = self._TINT_FALLBACK_HEX.get(token)
        if fallback:
            try:
                rgba = Gdk.RGBA()
                if rgba.parse(fallback):
                    return rgba
            except Exception:
                pass

        try:
            rgba = Gdk.RGBA()
            if rgba.parse(token):
                return rgba
        except Exception:
            pass

        return None

    def _install_compare_css(self) -> None:
        if self.__class__._CSS_INSTALLED:
            return

        try:
            provider = Gtk.CssProvider()
            provider.load_from_path(os.path.join(DATA_DIR, "gramps.css"))
            screen = Gdk.Screen.get_default()
            if screen is not None:
                Gtk.StyleContext.add_provider_for_screen(
                    screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                self.__class__._CSS_INSTALLED = True
        except Exception:
            return

    def _wrap_scroller(self, child: Gtk.Widget, min_h: int = 420) -> Gtk.Widget:
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        try:
            sw.set_min_content_height(min_h)
        except Exception:
            pass
        sw.add(child)
        return sw

    def _tune_treeview(self, tv: Gtk.TreeView, kind: str) -> None:
        """
        kind in {"overview","notes","sources"}: tune column widths + renderer behavior.
        """
        try:
            tv.set_headers_visible(True)
        except Exception:
            pass

        try:
            tv.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        except Exception:
            pass

        try:
            tv.set_rules_hint(True)
        except Exception:
            pass

        cols = tv.get_columns() or []
        for i, col in enumerate(cols):
            try:
                col.set_resizable(True)
                col.set_reorderable(True)
            except Exception:
                pass

            try:
                if kind == "overview" and i in (3, 5):
                    col.set_expand(True)
                if kind == "notes" and i in (3, 5):
                    col.set_expand(True)
                if kind == "sources" and i in (3, 4, 6, 7, 8):
                    col.set_expand(True)
            except Exception:
                pass

            try:
                renderers = col.get_cells() or []
            except Exception:
                renderers = []

            for r in renderers:
                if not isinstance(r, Gtk.CellRendererText):
                    continue

                try:
                    # 3 == Pango.EllipsizeMode.END
                    r.set_property("ellipsize", 3)
                except Exception:
                    pass

                try:
                    if kind == "overview" and i in (3, 5):
                        # 2 == Pango.WrapMode.WORD_CHAR
                        r.set_property("wrap-mode", 2)
                        r.set_property("wrap-width", 520)
                    elif kind == "notes" and i in (3, 5):
                        r.set_property("wrap-mode", 2)
                        r.set_property("wrap-width", 520)
                    elif kind == "sources" and i in (4, 7):  # URL columns
                        # make URLs look link-ish
                        r.set_property("underline", 1)  # Pango.Underline.SINGLE
                        r.set_property("foreground", "steelblue")
                    elif kind == "sources" and i in (3, 6):  # titles
                        r.set_property("wrap-mode", 2)
                        r.set_property("wrap-width", 420)
                except Exception:
                    pass

    def _looks_like_color(self, v: Any) -> bool:
        try:
            if v is None:
                return False

            s = v.strip() if isinstance(v, str) else str(v).strip()
            if not s:
                return False

            if s.startswith("#") and len(s) in (4, 7, 9):
                return True

            if s in self._TINT_COLOR_NAME:
                return True

            if s in self._TINT_FALLBACK_HEX:
                return True

            return False
        except Exception:
            return False

    def _guess_color_model_col(self, model: Gtk.TreeModel) -> int:
        try:
            n = model.get_n_columns()
        except Exception:
            return 0

        def scan_iter(it: Any) -> Optional[int]:
            if it is None:
                return None
            for ci in range(n):
                try:
                    v = model.get_value(it, ci)
                except Exception:
                    continue
                if self._looks_like_color(v):
                    return ci
            return None

        try:
            it = model.get_iter_first()
        except Exception:
            it = None

        found = scan_iter(it)
        if found is not None:
            return found

        # If first row is a section header with blank color, try first child
        try:
            if it is not None and model.iter_has_child(it):
                child = model.iter_children(it)
                found = scan_iter(child)
                if found is not None:
                    return found
        except Exception:
            pass

        return 0

    def _install_treeview_row_tints(self, tv: Gtk.TreeView) -> None:
        """
        Force row tinting via cell_data_func so it works even if ListModel COLOR
        is not painting anything by itself.
        """
        try:
            model = tv.get_model()
        except Exception:
            model = None
        if model is None:
            return

        color_col = self._guess_color_model_col(model)
        tv_ctx = tv.get_style_context()

        def make_func(is_indicator_col: bool):
            def _func(column: Any, cell: Any, model2: Any, it: Any, _data: Any) -> None:
                try:
                    token = model2.get_value(it, color_col)
                except Exception:
                    token = None

                s = ""
                try:
                    if token is None:
                        s = ""
                    elif isinstance(token, str):
                        s = token.strip()
                    else:
                        s = str(token).strip()
                except Exception:
                    s = ""

                if not s:
                    try:
                        cell.set_property("cell-background-set", False)
                    except Exception:
                        pass
                    return

                # 1) Prefer the named CSS colors
                rgba = None
                css_name = self._TINT_COLOR_NAME.get(s)
                if css_name:
                    try:
                        ok, rgba2 = tv_ctx.lookup_color(css_name)
                        if ok:
                            rgba = rgba2
                    except Exception:
                        rgba = None

                # 2) Fall back to hardcoded hex
                if rgba is None:
                    rgba = self._resolve_tint_rgba(s)

                painted = False
                if rgba is not None:
                    try:
                        cell.set_property("cell-background-rgba", rgba)
                        cell.set_property("cell-background-set", True)
                        painted = True
                    except Exception:
                        painted = False

                if not painted:
                    try:
                        cell.set_property(
                            "cell-background", self._TINT_FALLBACK_HEX.get(s, s)
                        )
                        cell.set_property("cell-background-set", True)
                    except Exception:
                        pass

                if is_indicator_col and isinstance(cell, Gtk.CellRendererText):
                    try:
                        cell.set_property("text", "")
                    except Exception:
                        pass

            return _func

        cols = tv.get_columns() or []
        for idx, col in enumerate(cols):
            is_indicator = idx == 0
            try:
                cells = col.get_cells() or []
            except Exception:
                cells = []
            for cell in cells:
                if not isinstance(cell, Gtk.CellRendererText):
                    continue
                try:
                    col.set_cell_data_func(cell, make_func(is_indicator), None)
                except Exception:
                    pass

        try:
            if cols:
                cols[0].set_sizing(Gtk.TreeViewColumnSizing.FIXED)
                cols[0].set_fixed_width(18)
        except Exception:
            pass

    def _build_legend(self) -> Gtk.Widget:
        wrap = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        wrap.get_style_context().add_class("fs-compare-legend")

        def pill(token: str, text: str) -> Gtk.Widget:
            css_name = self._TINT_COLOR_NAME.get(token, "")
            color = self._css_define_value(css_name) or self._TINT_FALLBACK_HEX.get(
                token, "#CCCCCC"
            )
            label = Gtk.Label()
            label.set_use_markup(True)
            label.set_markup(
                '<span background="{color}">&#160;&#160;&#160;</span> {text}'.format(
                    color=GLib.markup_escape_text(color),
                    text=GLib.markup_escape_text(text),
                )
            )
            label.get_style_context().add_class("fs-legend-label")
            return label

        wrap.pack_start(pill("green", _("Match")), False, False, 0)
        wrap.pack_start(pill("orange", _("Different")), False, False, 0)
        wrap.pack_start(pill("yellow", _("Only in Gramps")), False, False, 0)
        wrap.pack_start(pill("yellow3", _("Only in FamilySearch")), False, False, 0)
        wrap.pack_start(pill("red", _("Critical mismatch")), False, False, 0)

        hint = Gtk.Label(
            label=_(
                "Tip: resize columns by dragging headers | scroll inside tabs | refresh to re-check FamilySearch"
            )
        )
        hint.set_xalign(1.0)
        try:
            hint.set_ellipsize(3)
        except Exception:
            pass
        wrap.pack_end(hint, True, True, 0)
        return wrap

    def _on_compare(self, _btn: Any) -> None:
        active = self.get_active("Person")
        if not active:
            WarningDialog(_("Select a person first."))
            return

        if not (tree._fs_session and tree._fs_session.logged):
            WarningDialog(_("You must login first."))
            return

        # active may be a handle or a Person instance depending on caller
        gr_handle = getattr(active, "handle", None) or active

        def _get_gr() -> Optional[Person]:
            try:
                return self.dbstate.db.get_person_from_handle(gr_handle)
            except Exception:
                if isinstance(active, Person):
                    return active
                return None

        gr = _get_gr()
        if not gr:
            WarningDialog(_("Could not resolve the selected person in the database."))
            return

        fsid = fs_utilities.get_fsftid(gr)
        if not fsid:
            WarningDialog(
                _(
                    "This Gramps person is not linked to FamilySearch yet. Use 'Link person'."
                )
            )
            return

        self._ensure_person_cached(fsid, with_relatives=True)
        self._install_compare_css()

        # ---- Window ----
        win = Gtk.Window()
        win.set_title(_("FamilySearch Compare"))
        win.set_transient_for(self.uistate.window)
        win.set_default_size(1180, 740)
        win.get_style_context().add_class("fs-compare-window")

        # headerbar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = _("FamilySearch Compare")
        try:
            gid = gr.get_gramps_id() or ""
        except Exception:
            gid = ""
        subtitle = ("%s  <->  %s" % (gid, fsid)) if gid else fsid
        hb.props.subtitle = subtitle
        win.set_titlebar(hb)

        # Action buttons
        btn_refresh = Gtk.Button()
        btn_refresh.set_tooltip_text(_("Refresh from FamilySearch"))
        btn_refresh.add(
            Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        )
        hb.pack_end(btn_refresh)

        btn_import_sources = Gtk.Button()
        btn_import_sources.set_tooltip_text(_("Import sources..."))
        btn_import_sources.add(
            Gtk.Image.new_from_icon_name(
                "document-import-symbolic", Gtk.IconSize.BUTTON
            )
        )
        hb.pack_end(btn_import_sources)

        btn_close = Gtk.Button()
        btn_close.set_tooltip_text(_("Close"))
        btn_close.add(
            Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.BUTTON)
        )
        hb.pack_end(btn_close)

        # ---- Main layout ---
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        outer.get_style_context().add_class("fs-compare-wrap")
        win.add(outer)

        notebook = Gtk.Notebook()
        notebook.get_style_context().add_class("fs-compare-notebook")
        outer.pack_start(notebook, True, True, 0)

        # overview tab
        tv_overview, model_overview = self._make_overview_tree_model()
        tv_overview.get_style_context().add_class("fs-compare-treeview")
        self._tune_treeview(tv_overview, "overview")
        self._install_treeview_row_tints(tv_overview)
        notebook.append_page(
            self._wrap_scroller(tv_overview), Gtk.Label(label=_("Overview"))
        )

        # notes tab
        tv_notes, model_notes = self._make_notes_tree()
        tv_notes.get_style_context().add_class("fs-compare-treeview")
        self._tune_treeview(tv_notes, "notes")
        self._install_treeview_row_tints(tv_notes)
        notebook.append_page(self._wrap_scroller(tv_notes), Gtk.Label(label=_("Notes")))

        # sources tab
        tv_sources, model_sources = self._make_sources_tree()
        tv_sources.get_style_context().add_class("fs-compare-treeview")
        try:
            tv_sources.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        except Exception:
            pass
        self._tune_treeview(tv_sources, "sources")
        self._install_treeview_row_tints(tv_sources)
        notebook.append_page(
            self._wrap_scroller(tv_sources), Gtk.Label(label=_("Sources"))
        )

        # key/legend row
        outer.pack_end(self._build_legend(), False, False, 0)

        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        action_box.set_halign(Gtk.Align.END)

        btn_refresh_text = Gtk.Button(label=_("Refresh"))
        btn_import_sources_text = Gtk.Button(label=_("Import sources..."))
        btn_close_text = Gtk.Button(label=_("Close"))

        action_box.pack_end(btn_close_text, False, False, 0)
        action_box.pack_end(btn_import_sources_text, False, False, 0)
        action_box.pack_end(btn_refresh_text, False, False, 0)

        outer.pack_end(action_box, False, False, 0)

        def do_fill_all(force: bool = False) -> None:
            if force:
                self._ensure_person_cached(fsid, with_relatives=True, force=True)

            gr_local = _get_gr()
            if not gr_local:
                return

            model_overview.clear()
            self._fill_overview(model_overview, gr_local, fsid)

            model_notes.clear()
            self._fill_notes(model_notes, gr_local, fsid)

            model_sources.clear()
            self._fill_sources(model_sources, gr_local, fsid)

            # auto-tag after each refresh/fill
            try:
                payload = self._build_compare_json(gr_local, fsid)
                is_synced = fs_tags.compute_sync_from_payload(payload)
                fs_tags.set_sync_status_for_person(
                    self.dbstate.db, gr_local, is_synced=is_synced
                )
            except Exception:
                pass

        def do_import_sources(_btn: Any) -> None:
            self._import_sources_dialog(_get_gr(), fsid)
            model_sources.clear()
            self._fill_sources(model_sources, _get_gr(), fsid)

        btn_refresh.connect("clicked", lambda *_: do_fill_all(True))
        btn_refresh_text.connect("clicked", lambda *_: do_fill_all(True))

        btn_import_sources.connect("clicked", do_import_sources)
        btn_import_sources_text.connect("clicked", do_import_sources)

        btn_close.connect("clicked", lambda *_: win.destroy())
        btn_close_text.connect("clicked", lambda *_: win.destroy())

        do_fill_all(False)

        # auto-tag on initial open
        try:
            gr_local = _get_gr()
            if gr_local:
                payload = self._build_compare_json(gr_local, fsid)
                is_synced = fs_tags.compute_sync_from_payload(payload)
                fs_tags.set_sync_status_for_person(
                    self.dbstate.db, gr_local, is_synced=is_synced
                )
        except Exception:
            pass

        win.show_all()

    def _canon_fs_web(self, url: Optional[str]) -> str:
        if not url:
            return ""
        try:
            sess = getattr(tree, "_fs_session", None)
            if sess and hasattr(sess, "canonical_web_url"):
                return sess.canonical_web_url(url)
        except Exception:
            pass
        return url

    # ------------------ models / columns ------------------

    def _make_overview_tree_model(self):
        titles = [
            (" ", 1, 18, COLOR),  # color pill column
            (_("Property"), 2, 180),
            (_("Gramps date"), 3, 115),
            (_("Gramps value"), 4, 420),
            (_("FS date"), 5, 115),
            (_("FamilySearch value"), 6, 420),
            (" ", NOSORT, 1),
            ("x", 8, 5, TOGGLE, True, self._toggle_noop),
            (_("xType"), NOSORT, 0),
            (_("xGr"), NOSORT, 0),
            (_("xFs"), NOSORT, 0),
            (_("xGr2"), NOSORT, 0),
            (_("xFs2"), NOSORT, 0),
        ]
        treeview = Gtk.TreeView()
        model = ListModel(treeview, titles, list_mode="tree")
        return treeview, model

    def _make_notes_tree(self):
        treeview = Gtk.TreeView()
        titles = [
            (" ", 1, 18, COLOR),
            (_("Scope"), 2, 110),
            (_("Title"), 3, 220),
            (_("Gramps"), 4, 460),
            (_("FS Title"), 5, 220),
            (_("FamilySearch"), 6, 460),
        ]
        model = ListModel(treeview, titles, list_mode="tree")
        return treeview, model

    def _make_sources_tree(self):
        treeview = Gtk.TreeView()
        titles = [
            (" ", 1, 18, COLOR),
            (_("Kind"), 2, 90),
            (_("Gramps date"), 3, 110),
            (_("Gramps title"), 4, 260),
            (_("Gramps URL"), 5, 280),
            (_("FS date"), 6, 110),
            (_("FS title"), 7, 260),
            (_("FS URL"), 8, 280),
            (_("Tags"), 9, 220),
            (_("Contributor"), 10, 130),
            (_("Modified"), 11, 165),
            (_("FS ID"), NOSORT, 0),
        ]
        model = ListModel(treeview, titles, list_mode="tree")
        return treeview, model

    # ------------------ fills ------------------

    def _fill_overview(self, model: ListModel, gr: Person, fsid: str):
        fs_person = deserialize.Person.index.get(fsid) or deserialize.Person()
        try:
            compare_fs_to_gramps(
                fs_person, gr, self.dbstate.db, model=model, dupdoc=True
            )
        except Exception as e:
            WarningDialog(_("Compare failed: {e}").format(e=str(e)))

    def _fill_notes(self, model: Any, gr: Person, fsid: str):
        self._ensure_notes_cached(fsid)
        fs_person = deserialize.Person.index.get(fsid) or deserialize.Person()
        if not fs_person:
            return

        em = "_"
        fs_placeholder = (
            em if self.__class__.fs_Tree else _("Not connected to FamilySearch")
        )

        note_handles = gr.get_note_list()
        fs_notes_remaining = fs_person.notes.copy()

        def _take_matching_note(notes: Any, note_id: Optional[str], subject: str):
            match = None
            if note_id:
                for fs_note in notes:
                    if getattr(fs_note, "id", None) == note_id:
                        match = fs_note
                        break
            if match is None:
                for fs_note in notes:
                    if getattr(fs_note, "subject", None) == subject:
                        match = fs_note
                        break
            if match is not None:
                try:
                    notes.remove(match)
                except Exception:
                    pass
            return match

        # person notes
        for nh in note_handles:
            n = self.dbstate.db.get_note_from_handle(nh)
            note_text = n.get()
            title = _(n.type.xml_str())
            fs_text = fs_placeholder
            fs_title = ""
            gr_note_id = None
            try:
                for t in n.text.get_tags():
                    if t.name.name == "LINK" and t.value.startswith("_fsftid="):
                        gr_note_id = t.value[8:]
                        break
            except Exception:
                pass

            found = _take_matching_note(fs_notes_remaining, gr_note_id, title)
            if found:
                fs_title = found.subject or ""
                fs_text = found.text or ""
                color = (
                    "green"
                    if (
                        fs_title == title
                        and (
                            fs_text == note_text
                            or (
                                note_text.startswith("\ufeff")
                                and fs_text == note_text[1:]
                            )
                        )
                    )
                    else "orange"
                )
            else:
                color = "yellow"

            model.add(
                self._ui_row(
                    [
                        color,
                        _("Person"),
                        title,
                        note_text,
                        fs_title or em,
                        fs_text or em,
                    ]
                )
            )

        # FS-only person notes
        for fs_note in fs_notes_remaining:
            model.add(
                self._ui_row(
                    [
                        "yellow3",
                        _("Person"),
                        _("(missing in Gramps)"),
                        em,
                        fs_note.subject or "",
                        fs_note.text or "",
                    ]
                )
            )

        # family (spouse) notes
        fs_couples_remaining = fs_person._spouses.copy()
        for fam_h in gr.get_family_handle_list():
            fam = self.dbstate.db.get_family_from_handle(fam_h)
            if not fam:
                continue
            spouse_h = (
                fam.mother_handle
                if fam.mother_handle != gr.handle
                else fam.father_handle
            )
            spouse = (
                self.dbstate.db.get_person_from_handle(spouse_h) if spouse_h else None
            )
            spouse_fsid = fs_utilities.get_fsftid(spouse) if spouse else ""
            fs_rel = None
            for rel in list(fs_couples_remaining):
                p1 = rel.person1.resourceId if rel.person1 else ""
                p2 = rel.person2.resourceId if rel.person2 else ""
                if spouse_fsid in (p1, p2):
                    fs_rel = rel
                    fs_couples_remaining.remove(rel)
                    break

            rel_notes: set = set()
            if fs_rel:
                rel_notes = fs_rel.notes.copy()

            for nh in fam.get_note_list():
                n = self.dbstate.db.get_note_from_handle(nh)
                note_text = n.get()
                title = _(n.type.xml_str())
                fs_text = fs_placeholder
                fs_title = ""
                gr_note_id = None
                try:
                    for t in n.text.get_tags():
                        if t.name.name == "LINK" and t.value.startswith("_fsftid="):
                            gr_note_id = t.value[8:]
                            break
                except Exception:
                    pass

                found = _take_matching_note(rel_notes, gr_note_id, title)
                if found:
                    fs_title = found.subject or ""
                    fs_text = found.text or ""
                    color = (
                        "green"
                        if (
                            fs_title == title
                            and (
                                fs_text == note_text
                                or (
                                    note_text.startswith("\ufeff")
                                    and fs_text == note_text[1:]
                                )
                            )
                        )
                        else "orange"
                    )
                else:
                    color = "yellow"

                model.add(
                    self._ui_row(
                        [
                            color,
                            _("Family"),
                            title,
                            note_text,
                            fs_title or em,
                            fs_text or em,
                        ]
                    )
                )

            for fs_note in rel_notes:
                model.add(
                    self._ui_row(
                        [
                            "yellow3",
                            _("Family"),
                            _("(missing in Gramps)"),
                            em,
                            fs_note.subject or "",
                            fs_note.text or "",
                        ]
                    )
                )

        for rel in fs_couples_remaining:
            for fs_note in rel.notes:
                model.add(
                    self._ui_row(
                        [
                            "yellow3",
                            _("Family"),
                            _("(missing in Gramps)"),
                            em,
                            fs_note.subject or "",
                            fs_note.text or "",
                        ]
                    )
                )

    def _fill_sources(self, model: Any, gr: Person, fsid: str) -> None:
        self._ensure_sources_cached(fsid)

        fs_person = deserialize.Person.index.get(fsid) or deserialize.Person()
        em = "_"
        fs_placeholder = (
            em if self.__class__.fs_Tree else _("Not connected to FamilySearch")
        )

        source_meta = self._gather_sr_meta(fsid)

        # Collect FS SourceDescription IDs referenced by person + spouse relationships
        fs_source_ids: dict[str, None] = {}
        for sr in getattr(fs_person, "sources", []) or []:
            sdid = getattr(sr, "descriptionId", "") or ""
            if sdid:
                fs_source_ids[sdid] = None

        for rel in getattr(fs_person, "_spouses", []) or []:
            for sr in getattr(rel, "sources", []) or []:
                sdid = getattr(sr, "descriptionId", "") or ""
                if sdid:
                    fs_source_ids[sdid] = None

        # Ensure SourceDescription objects exist in index and (if connected) add to fs_Tree
        for sdid in list(fs_source_ids.keys()):
            if not sdid:
                continue
            if sdid not in deserialize.SourceDescription._index:
                sd_new = deserialize.SourceDescription()
                sd_new.id = sdid
                deserialize.SourceDescription._index[sdid] = sd_new
                try:
                    if self.__class__.fs_Tree is not None:
                        self.__class__.fs_Tree.sourceDescriptions.add(sd_new)
                except Exception:
                    pass

        # Populate FS dates if possible
        try:
            if self.__class__.fs_Tree is not None:
                fs_import.fetch_source_dates(self.__class__.fs_Tree)
        except Exception:
            pass

        # Collect Gramps citations across person + events + families
        citation_handles: set[str] = set(gr.get_citation_list() or [])

        for er in gr.get_event_ref_list() or []:
            try:
                ev = self.dbstate.db.get_event_from_handle(er.ref)
                if ev:
                    citation_handles.update(ev.get_citation_list() or [])
            except Exception:
                pass

        for fam_h in gr.get_family_handle_list() or []:
            try:
                fam = self.dbstate.db.get_family_from_handle(fam_h)
            except Exception:
                fam = None
            if not fam:
                continue

            try:
                citation_handles.update(fam.get_citation_list() or [])
            except Exception:
                pass

            for er in fam.get_event_ref_list() or []:
                try:
                    ev = self.dbstate.db.get_event_from_handle(er.ref)
                    if ev:
                        citation_handles.update(ev.get_citation_list() or [])
                except Exception:
                    pass

        # Row-per-Gramps-citation
        for ch in citation_handles:
            c = self.dbstate.db.get_citation_from_handle(ch)
            if not c:
                continue

            src_gr = fs_import.IntermediateSource()
            src_gr.from_gramps(self.dbstate.db, c)

            title: str = src_gr.citation_title or ""
            note_text = (src_gr.note_text or "").strip()
            gr_url: str = self._canon_fs_web(getattr(src_gr, "url", None))
            date: str = fs_utilities.gramps_date_to_formal(c.date)

            sd_id: str = fs_utilities.get_fsftid(c) or ""

            color = "yellow"
            fs_title: str = ""
            fs_date: str = ""
            fs_url: str = ""
            fs_text: str = fs_placeholder
            kind: str = ""
            tags_disp: str = ""
            contributor: str = ""
            modified: str = ""

            sd_obj: Optional[deserialize.SourceDescription] = (
                deserialize.SourceDescription._index.get(sd_id) if sd_id else None
            )

            if sd_obj is not None:
                src_fs = fs_import.IntermediateSource()
                src_fs.from_fs(sd_obj, None)

                fs_title = src_fs.citation_title or ""
                fs_text = src_fs.note_text or ""
                fs_date = str(src_fs.date)
                fs_url = self._canon_fs_web(getattr(src_fs, "url", None))

                meta = source_meta.get(sd_id, {}) or {}
                kind = str(meta.get("kind") or "")
                tags_disp = self._pretty_tags(meta.get("tags", []))
                contributor = str(meta.get("contributor") or "")
                modified = str(meta.get("modified") or "")

                color = "orange"
                if (
                    fs_date == date
                    and fs_title == title
                    and fs_url == gr_url
                    and (fs_text or "").strip() == note_text
                ):
                    color = "green"

                fs_source_ids.pop(sd_id, None)
            else:
                fs_date = fs_title = fs_url = em

            model.add(
                self._ui_row(
                    [
                        color,
                        kind,
                        date,
                        title,
                        gr_url,
                        fs_date,
                        fs_title or em,
                        fs_url or em,
                        tags_disp,
                        contributor,
                        modified,
                        sd_id,
                    ]
                )
            )

        # FS-only sources
        for sdid in list(fs_source_ids.keys()):
            if not sdid:
                continue

            sd_obj2: Optional[deserialize.SourceDescription] = (
                deserialize.SourceDescription._index.get(sdid)
            )

            fs_title = ""
            if sd_obj2 is not None and getattr(sd_obj2, "titles", None):
                try:
                    for t in sd_obj2.titles:
                        fs_title += getattr(t, "value", None) or ""
                except Exception:
                    pass

            fs_date_val = getattr(sd_obj2, "_date", "") if sd_obj2 is not None else ""
            fs_url2 = self._canon_fs_web(
                getattr(sd_obj2, "about", None) if sd_obj2 is not None else None
            )

            meta = source_meta.get(sdid, {}) or {}
            kind = str(meta.get("kind") or _("Mention"))
            tags_disp = self._pretty_tags(meta.get("tags", []))
            contributor = str(meta.get("contributor") or "")
            modified = str(meta.get("modified") or "")

            model.add(
                self._ui_row(
                    [
                        "yellow3",
                        kind,
                        em,
                        em,
                        em,
                        str(fs_date_val) or em,
                        fs_title or em,
                        fs_url2 or em,
                        tags_disp,
                        contributor,
                        modified,
                        sdid,
                    ]
                )
            )
