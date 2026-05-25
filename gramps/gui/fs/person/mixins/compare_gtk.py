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

from dataclasses import dataclass
import os
import re
from typing import Any, ClassVar, Optional, TYPE_CHECKING

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

from gramps.gen.const import DATA_DIR, GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.utils.file import media_path_full
from gramps.gui.dialog import OkDialog, QuestionDialog2, WarningDialog
from gramps.gui.listmodel import ListModel, NOSORT, COLOR, TOGGLE
from gramps.gui.utils import ProgressMeter
from gramps.gen.lib import EventRef, EventRoleType, EventType, Name, Person

from gramps.gen.fs import tree
from gramps.gen.fs import utils as fs_utilities
from gramps.gen.fs.compare import compare_fs_to_gramps
from gramps.gen.fs.compare.comparators import (
    compare_fact,
    compare_gender,
    compare_names,
    compare_other_facts,
    compare_parents,
    compare_spouses,
)
from gramps.gen.fs.compare.formatters import person_dates_str
import gramps.gen.fs.fs_import as fs_import
from gramps.gui.fs import tags as fs_tags
from gramps.gen.fs.fs_import import deserializer as deserialize

_ = glocale.translation.gettext


@dataclass
class _FSMergeRow:
    """One selectable FamilySearch-to-Gramps merge row."""

    status: str
    section: str
    field: str
    gramps_date: str
    gramps_value: str
    fs_date: str
    fs_value: str
    selected: bool
    selectable: bool
    kind: str
    gr_handle: str
    fs_id: str
    gr_extra: str
    fs_extra: str


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

        def _ensure_sources_cached(
            self,
            fsid: str,
            progress_callback: Any | None = None,
        ) -> None: ...

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
    _FS_PHOTO_CACHE: ClassVar[dict[str, Any]] = {}

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

    def _merge_value_text(self, date: Any, value: Any) -> str:
        """
        Combine a date and value into the compact merge-column display text.
        """
        parts = []
        for part in (date, value):
            text = str(part or "").strip()
            if text and text != "_":
                parts.append(text)
        return "\n".join(parts)

    def _merge_row_selectable(self, status: str, kind: str, fs_text: str) -> bool:
        """
        Return whether a compare row can be copied from FamilySearch to Gramps.
        """
        if not fs_text.strip():
            return False
        if status not in ("red", "orange", "yellow3"):
            return False
        return kind in {
            "gender",
            "primary_name",
            "name",
            "fact",
            "father",
            "mother",
            "spouse",
            "spouse_fact",
            "child",
        }

    def _merge_row_from_compare(self, section: str, row: Any) -> _FSMergeRow:
        """
        Convert an existing compare tuple into a merge preview row.
        """
        data = list(row) + [""] * 13
        status = str(data[0] or "")
        kind = str(data[8] or "")
        gramps_text = self._merge_value_text(data[2], data[3])
        fs_text = self._merge_value_text(data[4], data[5])
        selectable = self._merge_row_selectable(status, kind, fs_text)
        selected = selectable and status == "yellow3"
        return _FSMergeRow(
            status=status,
            section=section,
            field=str(data[1] or "").strip(),
            gramps_date=str(data[2] or ""),
            gramps_value=str(data[3] or ""),
            fs_date=str(data[4] or ""),
            fs_value=str(data[5] or ""),
            selected=selected,
            selectable=selectable,
            kind=kind,
            gr_handle=str(data[9] or ""),
            fs_id=str(data[10] or ""),
            gr_extra=str(data[11] or ""),
            fs_extra=str(data[12] or ""),
        )

    def _collect_merge_rows(self, gr: Person, fsid: str) -> list[_FSMergeRow]:
        """
        Build the side-by-side FamilySearch-to-Gramps merge rows.
        """
        fs_person = deserialize.Person.index.get(fsid) or deserialize.Person()
        rows: list[_FSMergeRow] = []

        essentials: list[Any] = []
        gender_row = compare_gender(gr, fs_person)
        if gender_row:
            essentials.append(gender_row)

        name_rows = compare_names(gr, fs_person)
        if name_rows:
            essentials.append(name_rows[0])

        for gr_event, fs_fact_tag in (
            (EventType.BIRTH, "http://gedcomx.org/Birth"),
            (EventType.BAPTISM, "http://gedcomx.org/Baptism"),
            (EventType.DEATH, "http://gedcomx.org/Death"),
            (EventType.BURIAL, "http://gedcomx.org/Burial"),
        ):
            fact_row = compare_fact(
                self.dbstate.db, gr, fs_person, gr_event, fs_fact_tag
            )
            if fact_row:
                essentials.append(fact_row)

        rows.extend(
            self._merge_row_from_compare(_("Essentials"), line)
            for line in essentials
        )

        rows.extend(
            self._merge_row_from_compare(_("Other names"), line)
            for line in name_rows[1:]
        )

        rows.extend(
            self._merge_row_from_compare(_("Parents"), line)
            for line in compare_parents(self.dbstate.db, gr, fs_person)
        )
        rows.extend(
            self._merge_row_from_compare(_("Families"), line)
            for line in compare_spouses(self.dbstate.db, gr, fs_person)
        )
        rows.extend(
            self._merge_row_from_compare(_("Facts"), line)
            for line in compare_other_facts(self.dbstate.db, gr, fs_person)
        )
        return rows

    def _make_merge_tree(self) -> tuple[Gtk.TreeView, Gtk.TreeStore]:
        """
        Create the Compare/Merge tree with Gramps, FamilySearch, and result columns.
        """
        store = Gtk.TreeStore(
            bool,  # 0 selected
            bool,  # 1 selectable
            str,  # 2 status token
            str,  # 3 section
            str,  # 4 field
            str,  # 5 Gramps display
            str,  # 6 FamilySearch display
            str,  # 7 final display
            str,  # 8 row kind
            str,  # 9 Gramps handle/id
            str,  # 10 FamilySearch id
            str,  # 11 Gramps extra
            str,  # 12 FamilySearch extra
            str,  # 13 Gramps date
            str,  # 14 FamilySearch date
            str,  # 15 detail/status text
        )
        treeview = Gtk.TreeView(model=store)
        treeview.get_style_context().add_class("fs-merge-treeview")
        treeview.set_headers_visible(True)
        try:
            treeview.set_grid_lines(Gtk.TreeViewGridLines.VERTICAL)
            treeview.set_rules_hint(True)
        except Exception:
            pass

        toggle = Gtk.CellRendererToggle()
        toggle.set_property("activatable", True)
        col_select = Gtk.TreeViewColumn(_("Use FS"), toggle)
        col_select.add_attribute(toggle, "active", 0)
        col_select.add_attribute(toggle, "activatable", 1)
        col_select.set_fixed_width(78)
        treeview.append_column(col_select)

        for title, column_id, width in (
            (_("Field"), 4, 150),
            (_("Current Gramps"), 5, 300),
            (_("FamilySearch"), 6, 300),
            (_("Final Gramps result"), 7, 320),
            (_("Status"), 15, 150),
        ):
            renderer = Gtk.CellRendererText()
            try:
                renderer.set_property("wrap-mode", 2)
                renderer.set_property("wrap-width", width)
            except Exception:
                pass
            column = Gtk.TreeViewColumn(title, renderer, text=column_id)
            column.set_resizable(True)
            column.set_min_width(width)
            if column_id in (5, 6, 7):
                column.set_expand(True)
            treeview.append_column(column)

        def update_final(tree_iter: Any) -> None:
            selected = bool(store.get_value(tree_iter, 0))
            gramps_text = str(store.get_value(tree_iter, 5) or "")
            fs_text = str(store.get_value(tree_iter, 6) or "")
            store.set_value(tree_iter, 7, fs_text if selected else gramps_text)
            store.set_value(
                tree_iter,
                15,
                _("Will copy from FamilySearch") if selected else _("Kept in Gramps"),
            )

        def cb_toggled(_cell: Gtk.CellRendererToggle, path: str) -> None:
            """Toggle a merge row and refresh its final-result preview."""
            tree_iter = store.get_iter(path)
            if tree_iter is None or not bool(store.get_value(tree_iter, 1)):
                return
            store.set_value(tree_iter, 0, not bool(store.get_value(tree_iter, 0)))
            update_final(tree_iter)

        toggle.connect("toggled", cb_toggled)
        return treeview, store

    def _install_merge_tree_row_tints(self, tv: Gtk.TreeView) -> None:
        """
        Paint merge rows from their explicit status-token column.
        """
        color_col = 2

        def _func(
            _column: Any, cell: Any, model: Any, tree_iter: Any, _data: Any
        ) -> None:
            token = str(model.get_value(tree_iter, color_col) or "").strip()
            rgba = self._resolve_tint_rgba(token)
            if rgba is not None:
                try:
                    cell.set_property("cell-background-rgba", rgba)
                    cell.set_property("cell-background-set", True)
                except Exception:
                    pass
            else:
                try:
                    cell.set_property("cell-background-set", False)
                except Exception:
                    pass

            if isinstance(cell, Gtk.CellRendererText):
                kind = str(model.get_value(tree_iter, 8) or "")
                try:
                    cell.set_property("weight", 700 if kind == "section" else 400)
                except Exception:
                    pass

        for column in tv.get_columns() or []:
            for cell in column.get_cells() or []:
                if isinstance(cell, Gtk.CellRendererText):
                    column.set_cell_data_func(cell, _func, None)

    def _append_merge_row(
        self, store: Gtk.TreeStore, parent: Any, row: _FSMergeRow
    ) -> None:
        """
        Append one merge row under a section header.
        """
        gramps_text = self._merge_value_text(row.gramps_date, row.gramps_value)
        fs_text = self._merge_value_text(row.fs_date, row.fs_value)
        final_text = fs_text if row.selected else gramps_text
        detail = (
            _("Will copy from FamilySearch")
            if row.selected
            else (
                _("Review and select to copy")
                if row.selectable
                else _("Not mergeable in this row")
            )
        )
        store.append(
            parent,
            [
                row.selected,
                row.selectable,
                row.status,
                row.section,
                row.field,
                gramps_text,
                fs_text,
                final_text,
                row.kind,
                row.gr_handle,
                row.fs_id,
                row.gr_extra,
                row.fs_extra,
                row.gramps_date,
                row.fs_date,
                detail,
            ],
        )

    def _fill_merge(self, store: Gtk.TreeStore, gr: Person, fsid: str) -> None:
        """
        Fill the Compare/Merge tree with grouped selectable rows.
        """
        store.clear()
        section_iters: dict[str, Any] = {}
        section_status: dict[str, str] = {}
        rows = self._collect_merge_rows(gr, fsid)

        for row in rows:
            current = section_status.get(row.section, "green")
            if row.status == "red" or current == "red":
                section_status[row.section] = "red"
            elif row.status in ("orange", "yellow3", "yellow") or current != "green":
                section_status[row.section] = "orange"
            else:
                section_status[row.section] = "green"

        for row in rows:
            parent = section_iters.get(row.section)
            if parent is None:
                token = section_status.get(row.section, "green")
                parent = store.append(
                    None,
                    [
                        False,
                        False,
                        token,
                        row.section,
                        row.section,
                        _("Current Gramps"),
                        _("FamilySearch"),
                        _("Final Gramps result"),
                        "section",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ],
                )
                section_iters[row.section] = parent
            self._append_merge_row(store, parent, row)

    def _selected_merge_rows_from_list(
        self, rows: list[_FSMergeRow]
    ) -> list[_FSMergeRow]:
        """
        Return checked merge rows from the FamilySearch-style merge board.
        """
        return [row for row in rows if row.selected and row.selectable]

    def _status_label_text(self, status: str, selectable: bool) -> str:
        """
        Return short status text for a merge card.
        """
        if status == "green":
            return _("Match")
        if status == "red":
            return _("Critical")
        if status == "orange":
            return _("Different")
        if status == "yellow":
            return _("Only in Gramps")
        if status == "yellow3":
            return _("Only in FamilySearch")
        return _("Selectable") if selectable else ""

    def _status_badge(self, status: str, selectable: bool) -> Gtk.Widget:
        """
        Build a small status badge for a merge card.
        """
        text = self._status_label_text(status, selectable)
        label = Gtk.Label(label=text)
        label.get_style_context().add_class("fs-merge-badge")
        if status:
            label.get_style_context().add_class("fs-status-" + status)
        return label

    def _result_text_for_row(self, row: _FSMergeRow) -> str:
        """
        Return the current result preview text for a merge row.
        """
        gramps_text = self._merge_value_text(row.gramps_date, row.gramps_value)
        fs_text = self._merge_value_text(row.fs_date, row.fs_value)
        return fs_text if row.selected and fs_text else gramps_text

    def _make_value_label(self, text: str, *, bold: bool = False) -> Gtk.Label:
        """
        Create a wrapping value label.
        """
        label = Gtk.Label()
        label.set_xalign(0.0)
        label.set_yalign(0.0)
        label.set_line_wrap(True)
        label.set_selectable(True)
        text = text or ""
        if bold:
            label.set_markup("<b>%s</b>" % GLib.markup_escape_text(text))
        else:
            label.set_text(text)
        return label

    def _merge_cell(
        self,
        row: _FSMergeRow,
        side: str,
        result_label: Gtk.Label | None = None,
    ) -> Gtk.Widget:
        """
        Build one side of a FamilySearch-style merge row.
        """
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.get_style_context().add_class("fs-merge-cell")
        if row.status:
            box.get_style_context().add_class("fs-status-" + row.status)
        if side == "result":
            box.get_style_context().add_class("fs-merge-result-cell")

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.set_valign(Gtk.Align.START)

        if side == "fs":
            check = Gtk.CheckButton()
            check.set_active(row.selected)
            check.set_sensitive(row.selectable)
            check.set_tooltip_text(
                _("Copy this FamilySearch value into Gramps")
                if row.selectable
                else _("This row cannot be merged directly")
            )
            header.pack_start(check, False, False, 0)

            def cb_toggled(button: Gtk.CheckButton) -> None:
                """Update the selected state and result preview."""
                row.selected = bool(button.get_active())
                if result_label is not None:
                    result_label.set_text(self._result_text_for_row(row))

            check.connect("toggled", cb_toggled)

        title = self._make_value_label(row.field or row.section, bold=True)
        header.pack_start(title, True, True, 0)
        if side != "result":
            header.pack_end(self._status_badge(row.status, row.selectable), False, False, 0)
        box.pack_start(header, False, False, 0)

        if side == "gramps":
            text = self._merge_value_text(row.gramps_date, row.gramps_value)
        elif side == "fs":
            text = self._merge_value_text(row.fs_date, row.fs_value)
        else:
            text = self._result_text_for_row(row)
        if not text:
            text = "-"

        if side == "result" and result_label is not None:
            value = result_label
            value.set_text(text)
        else:
            value = self._make_value_label(text)
        value.get_style_context().add_class("fs-merge-value")
        box.pack_start(value, True, True, 0)
        return box

    def _merge_inconsistency_box(self, row: _FSMergeRow) -> Gtk.Widget:
        """
        Build a FamilySearch-style inconsistency warning.
        """
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        box.get_style_context().add_class("fs-merge-inconsistency")
        title = self._make_value_label(_("Inconsistencies"), bold=True)
        box.pack_start(title, False, False, 0)
        details = []
        if row.gramps_date and row.fs_date and row.gramps_date != row.fs_date:
            details.append(_("The dates are different."))
        if row.gramps_value and row.fs_value and row.gramps_value != row.fs_value:
            details.append(_("The values are different."))
        if not details:
            details.append(_("Review this difference before merging."))
        body = self._make_value_label("- " + "\n- ".join(details))
        box.pack_start(body, False, False, 0)
        return box

    def _section_title(self, text: str) -> Gtk.Widget:
        """
        Build a section title for a merge column.
        """
        label = self._make_value_label(text, bold=True)
        label.get_style_context().add_class("fs-merge-section-title")
        return label

    def _person_photo_pixbuf(self, person: Person | None, size: int = 56):
        """
        Return a scaled local Gramps person photo if one is available.
        """
        if person is None:
            return None
        for media_ref in list(person.get_media_list() or []):
            handle = getattr(media_ref, "ref", "") or ""
            if not handle:
                continue
            try:
                media = self.dbstate.db.get_media_from_handle(handle)
            except Exception:
                try:
                    media = self.dbstate.db.get_media_object_from_handle(handle)
                except Exception:
                    media = None
            if media is None:
                continue
            mime = str(getattr(media, "mime", "") or "").lower()
            if mime and not mime.startswith("image/"):
                continue
            path = ""
            try:
                path = media_path_full(self.dbstate.db, media.get_path())
            except Exception:
                path = str(getattr(media, "path", "") or "")
            if not path or not os.path.exists(path):
                continue
            try:
                return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    path, size, size, True
                )
            except Exception:
                continue
        return None

    def _fs_photo_pixbuf(self, fs_person: Any, size: int = 56):
        """
        Return a FamilySearch photo pixbuf if the cached payload exposes one.
        """
        fsid = str(getattr(fs_person, "id", "") or "")
        cache_key = "%s:%s" % (fsid, size)
        if cache_key in self.__class__._FS_PHOTO_CACHE:
            return self.__class__._FS_PHOTO_CACHE[cache_key]

        candidates = [
            getattr(fs_person, "portraitUrl", ""),
            getattr(fs_person, "profileImageUrl", ""),
            getattr(getattr(fs_person, "display", None), "portraitUrl", ""),
            getattr(getattr(fs_person, "display", None), "profileImageUrl", ""),
        ]
        for candidate in candidates:
            candidate = str(candidate or "")
            if candidate and os.path.exists(candidate):
                try:
                    return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        candidate, size, size, True
                    )
                except Exception:
                    continue

        session = getattr(tree, "_fs_session", None)
        get_url = getattr(session, "get_url", None)
        if fsid and callable(get_url):
            try:
                response = get_url("/platform/tree/persons/%s/portrait" % fsid)
                content = getattr(response, "content", b"") if response else b""
                if content:
                    loader = GdkPixbuf.PixbufLoader()
                    loader.write(content)
                    loader.close()
                    pixbuf = loader.get_pixbuf()
                    if pixbuf is not None:
                        scaled = pixbuf.scale_simple(
                            size,
                            size,
                            GdkPixbuf.InterpType.BILINEAR,
                        )
                        self.__class__._FS_PHOTO_CACHE[cache_key] = scaled
                        return scaled
            except Exception:
                pass
        self.__class__._FS_PHOTO_CACHE[cache_key] = None
        return None

    def _photo_widget(self, pixbuf: Any, gender: int | None = None) -> Gtk.Widget:
        """
        Build a fixed-size photo/avatar slot.
        """
        image = Gtk.Image()
        image.set_size_request(58, 58)
        image.get_style_context().add_class("fs-person-photo")
        if pixbuf is not None:
            image.set_from_pixbuf(pixbuf)
            return image
        icon_name = "avatar-default-symbolic"
        if gender == Person.MALE:
            icon_name = "avatar-default-symbolic"
        elif gender == Person.FEMALE:
            icon_name = "avatar-default-symbolic"
        image.set_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        return image

    def _fs_gender_value(self, fs_person: Any) -> int:
        """
        Return a Gramps gender value for a FamilySearch person.
        """
        fs_type = getattr(getattr(fs_person, "gender", None), "type", "")
        if fs_type == "http://gedcomx.org/Male":
            return Person.MALE
        if fs_type == "http://gedcomx.org/Female":
            return Person.FEMALE
        return Person.UNKNOWN

    def _gr_header_text(self, gr: Person) -> tuple[str, str, str]:
        """
        Return name, life text, and id text for the Gramps header.
        """
        name = ""
        try:
            name = gr.get_primary_name().get_name()
        except Exception:
            try:
                name = str(gr.get_primary_name())
            except Exception:
                name = _("Gramps person")
        try:
            gid = gr.get_gramps_id() or ""
        except Exception:
            gid = ""
        return name, person_dates_str(self.dbstate.db, gr), gid

    def _fs_header_text(self, fs_person: Any, fsid: str) -> tuple[str, str, str]:
        """
        Return name, life text, and id text for the FamilySearch header.
        """
        name = ""
        try:
            fs_name = fs_person.preferred_name()
            name = (fs_name.akGiven() + " " + fs_name.akSurname()).strip()
        except Exception:
            name = ""
        if not name:
            name = _("FamilySearch person")
        life = ""
        try:
            display = getattr(fs_person, "display", None)
            life = getattr(display, "lifespan", "") or ""
        except Exception:
            life = ""
        return name, life, fsid

    def _merge_person_header(
        self,
        title: str,
        name: str,
        life: str,
        ident: str,
        photo: Gtk.Widget,
        *,
        result: bool = False,
    ) -> Gtk.Widget:
        """
        Build one person header card for the merge board.
        """
        wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        wrap.get_style_context().add_class("fs-merge-person-wrap")
        label = self._make_value_label(title, bold=True)
        label.get_style_context().add_class("fs-merge-column-label")
        wrap.pack_start(label, False, False, 0)

        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        card.get_style_context().add_class("fs-merge-person-card")
        if result:
            card.get_style_context().add_class("fs-merge-result-card")
        card.pack_start(photo, False, False, 0)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        text_box.pack_start(self._make_value_label(name, bold=True), False, False, 0)
        meta = " - ".join(part for part in (life, ident) if part)
        text_box.pack_start(self._make_value_label(meta), False, False, 0)
        card.pack_start(text_box, True, True, 0)
        wrap.pack_start(card, False, False, 0)
        return wrap

    def _build_merge_board(self, gr: Person, fsid: str) -> tuple[Gtk.Widget, list[_FSMergeRow]]:
        """
        Build a FamilySearch-style merge board and its backing rows.
        """
        fs_person = deserialize.Person.index.get(fsid) or deserialize.Person()
        rows = self._collect_merge_rows(gr, fsid)
        grid = Gtk.Grid()
        grid.get_style_context().add_class("fs-merge-board")
        grid.set_row_spacing(0)
        grid.set_column_spacing(10)
        try:
            grid.set_column_homogeneous(False)
        except Exception:
            pass

        gr_name, gr_life, gr_id = self._gr_header_text(gr)
        fs_name, fs_life, fs_id = self._fs_header_text(fs_person, fsid)
        result_name = fs_name or gr_name
        result_life = fs_life or gr_life
        result_id = fs_id or gr_id

        grid.attach(
            self._merge_person_header(
                _("Current Gramps"),
                gr_name,
                gr_life,
                gr_id,
                self._photo_widget(self._person_photo_pixbuf(gr), gr.get_gender()),
            ),
            0,
            0,
            1,
            1,
        )
        grid.attach(
            self._merge_person_header(
                _("FamilySearch"),
                fs_name,
                fs_life,
                fs_id,
                self._photo_widget(
                    self._fs_photo_pixbuf(fs_person),
                    self._fs_gender_value(fs_person),
                ),
            ),
            1,
            0,
            1,
            1,
        )
        arrow = Gtk.Label(label="->")
        arrow.get_style_context().add_class("fs-merge-arrow")
        grid.attach(arrow, 2, 0, 1, 1)
        grid.attach(
            self._merge_person_header(
                _("Result in Gramps"),
                result_name,
                result_life,
                result_id,
                self._photo_widget(
                    self._fs_photo_pixbuf(fs_person) or self._person_photo_pixbuf(gr),
                    self._fs_gender_value(fs_person),
                ),
                result=True,
            ),
            3,
            0,
            1,
            1,
        )

        row_index = 1
        current_section = None
        for row in rows:
            if row.section != current_section:
                current_section = row.section
                grid.attach(self._section_title(row.section), 0, row_index, 1, 1)
                grid.attach(self._section_title(row.section), 1, row_index, 1, 1)
                grid.attach(Gtk.Label(label=""), 2, row_index, 1, 1)
                grid.attach(self._section_title(row.section), 3, row_index, 1, 1)
                row_index += 1

            result_label = self._make_value_label("")
            result_label.get_style_context().add_class("fs-merge-value")
            grid.attach(self._merge_cell(row, "gramps"), 0, row_index, 1, 1)
            grid.attach(self._merge_cell(row, "fs", result_label), 1, row_index, 1, 1)
            grid.attach(Gtk.Label(label=""), 2, row_index, 1, 1)
            grid.attach(self._merge_cell(row, "result", result_label), 3, row_index, 1, 1)
            row_index += 1

            if row.status == "red":
                grid.attach(
                    self._merge_inconsistency_box(row),
                    0,
                    row_index,
                    2,
                    1,
                )
                row_index += 1

        return grid, rows

    def _selected_merge_rows(self, store: Gtk.TreeStore) -> list[_FSMergeRow]:
        """
        Return the currently checked merge rows from a merge tree store.
        """
        rows: list[_FSMergeRow] = []

        def walk(parent: Any | None = None) -> None:
            tree_iter = (
                store.get_iter_first()
                if parent is None
                else store.iter_children(parent)
            )
            while tree_iter is not None:
                if bool(store.get_value(tree_iter, 0)) and bool(
                    store.get_value(tree_iter, 1)
                ):
                    rows.append(
                        _FSMergeRow(
                            status=str(store.get_value(tree_iter, 2) or ""),
                            section=str(store.get_value(tree_iter, 3) or ""),
                            field=str(store.get_value(tree_iter, 4) or ""),
                            gramps_date=str(store.get_value(tree_iter, 13) or ""),
                            gramps_value=str(store.get_value(tree_iter, 5) or ""),
                            fs_date=str(store.get_value(tree_iter, 14) or ""),
                            fs_value=str(store.get_value(tree_iter, 6) or ""),
                            selected=True,
                            selectable=True,
                            kind=str(store.get_value(tree_iter, 8) or ""),
                            gr_handle=str(store.get_value(tree_iter, 9) or ""),
                            fs_id=str(store.get_value(tree_iter, 10) or ""),
                            gr_extra=str(store.get_value(tree_iter, 11) or ""),
                            fs_extra=str(store.get_value(tree_iter, 12) or ""),
                        )
                    )
                if store.iter_has_child(tree_iter):
                    walk(tree_iter)
                tree_iter = store.iter_next(tree_iter)

        walk()
        return rows

    def _fs_name_for_row(self, fs_person: Any, row: _FSMergeRow) -> Any:
        """
        Find the FamilySearch name object represented by a merge row.
        """
        if row.fs_id:
            for name in list(getattr(fs_person, "names", []) or []):
                if getattr(name, "id", "") == row.fs_id:
                    return name
        if row.kind == "primary_name":
            return fs_person.preferred_name()
        return None

    def _name_parts_equal(self, left: Name, right: Any) -> bool:
        """
        Compare a Gramps name to a FamilySearch name by given and surname.
        """
        try:
            left_surname = left.get_surname()
        except Exception:
            left_surname = ""
        return (
            (left_surname or "").strip() == (right.akSurname() or "").strip()
            and (left.first_name or "").strip() == (right.akGiven() or "").strip()
        )

    def _person_has_fs_name(self, gr: Person, fs_name: Any) -> bool:
        """
        Return True when Gramps already has the FamilySearch name.
        """
        names = [gr.get_primary_name()] + list(gr.get_alternate_names() or [])
        return any(name and self._name_parts_equal(name, fs_name) for name in names)

    def _copy_primary_name_to_alternates(self, gr: Person, fs_name: Any) -> None:
        """
        Preserve the current primary Gramps name as an alternate before replacing it.
        """
        primary = gr.get_primary_name()
        if (
            primary is None
            or primary.is_empty()
            or self._name_parts_equal(primary, fs_name)
        ):
            return
        gr.add_alternate_name(Name(source=primary))

    def _merge_name_row(
        self, db: Any, txn: Any, gr: Person, fs_person: Any, row: _FSMergeRow
    ) -> bool:
        """
        Copy one selected FamilySearch name into the Gramps person.
        """
        fs_name = self._fs_name_for_row(fs_person, row)
        if fs_name is None:
            return False
        if row.kind == "primary_name":
            self._copy_primary_name_to_alternates(gr, fs_name)
            fs_import.add_name(db, txn, fs_name, gr)
            return True
        if self._person_has_fs_name(gr, fs_name):
            return False
        fs_import.add_name(db, txn, fs_name, gr)
        return True

    def _merge_gender_row(self, gr: Person, fs_person: Any) -> bool:
        """
        Copy FamilySearch gender into the Gramps person.
        """
        fs_gender = getattr(fs_person, "gender", None)
        fs_type = getattr(fs_gender, "type", "")
        if fs_type == "http://gedcomx.org/Male":
            new_gender = Person.MALE
        elif fs_type == "http://gedcomx.org/Female":
            new_gender = Person.FEMALE
        else:
            new_gender = Person.UNKNOWN
        if gr.get_gender() == new_gender:
            return False
        gr.set_gender(new_gender)
        return True

    def _fs_fact_for_row(self, fs_person: Any, row: _FSMergeRow) -> Any:
        """
        Find the FamilySearch fact object represented by a merge row.
        """
        facts = list(getattr(fs_person, "facts", []) or [])
        if row.fs_id:
            for fact in facts:
                if getattr(fact, "id", "") == row.fs_id:
                    return fact
        return None

    def _fs_couple_for_row(self, fs_person: Any, row: _FSMergeRow) -> Any:
        """
        Find the FamilySearch couple relationship represented by a merge row.
        """
        for couple in list(getattr(fs_person, "_spouses", []) or []):
            if row.fs_extra and getattr(couple, "id", "") == row.fs_extra:
                return couple
            p1 = getattr(getattr(couple, "person1", None), "resourceId", "")
            p2 = getattr(getattr(couple, "person2", None), "resourceId", "")
            if row.fs_id and row.fs_id in (p1, p2):
                return couple
        return None

    def _fs_couple_fact_for_row(
        self, fs_person: Any, row: _FSMergeRow
    ) -> tuple[Any, Any]:
        """
        Find the FamilySearch couple relationship and fact for a spouse event row.
        """
        couple = self._fs_couple_for_row(fs_person, row)
        if couple is None:
            return None, None
        for fact in list(getattr(couple, "facts", []) or []):
            if row.fs_id and getattr(fact, "id", "") == row.fs_id:
                return couple, fact
        return couple, None

    def _ensure_event_ref(
        self, db: Any, txn: Any, gr: Person, event: Any, *, role: int
    ) -> EventRef:
        """
        Ensure the Gramps person has a reference to an event.
        """
        for event_ref in list(gr.get_event_ref_list() or []):
            if event_ref.ref == event.handle:
                return event_ref
        event_ref = EventRef()
        event_ref.set_role(role)
        event_ref.set_reference_handle(event.get_handle())
        db.commit_event(event, txn)
        gr.add_event_ref(event_ref)
        return event_ref

    def _merge_person_fact_row(
        self, db: Any, txn: Any, gr: Person, fs_person: Any, row: _FSMergeRow
    ) -> bool:
        """
        Copy one selected FamilySearch fact into the Gramps person.
        """
        fs_fact = self._fs_fact_for_row(fs_person, row)
        if fs_fact is None:
            return False

        if row.gr_handle:
            event = db.get_event_from_handle(row.gr_handle)
            if event:
                fs_import.update_event(db, txn, fs_fact, event)
                return True

        event = fs_import.add_event(db, txn, fs_fact, gr)
        if event is None:
            return False

        event_ref = self._ensure_event_ref(
            db, txn, gr, event, role=EventRoleType.PRIMARY
        )
        try:
            event_type = (
                int(event.type) if hasattr(event.type, "__int__") else event.type
            )
            if event_type == EventType.BIRTH:
                gr.set_birth_ref(event_ref)
            elif event_type == EventType.DEATH:
                gr.set_death_ref(event_ref)
        except Exception:
            pass
        return True

    def _merge_family_fact_row(
        self, db: Any, txn: Any, fs_person: Any, row: _FSMergeRow
    ) -> bool:
        """
        Copy one selected FamilySearch couple fact into a Gramps family.
        """
        _couple, fs_fact = self._fs_couple_fact_for_row(fs_person, row)
        if fs_fact is None or not row.gr_extra:
            return False
        family = db.get_family_from_handle(row.gr_extra)
        if family is None:
            return False

        if row.gr_handle:
            event = db.get_event_from_handle(row.gr_handle)
            if event:
                fs_import.update_event(db, txn, fs_fact, event)
                return True

        event = fs_import.add_event(db, txn, fs_fact, family)
        if event is None:
            return False
        if not any(
            event_ref.ref == event.handle
            for event_ref in list(family.get_event_ref_list() or [])
        ):
            event_ref = EventRef()
            event_ref.set_role(EventRoleType.FAMILY)
            event_ref.set_reference_handle(event.get_handle())
            db.commit_event(event, txn)
            family.add_event_ref(event_ref)
        db.commit_family(family, txn)
        return True

    def _fs_child_parent_for_row(self, fs_person: Any, row: _FSMergeRow) -> Any:
        """
        Find the FamilySearch child-and-parents relationship for a merge row.
        """
        fsid = getattr(fs_person, "id", "")
        relationships = (
            list(getattr(fs_person, "_parentsCP", []) or [])
            + list(getattr(fs_person, "_childrenCP", []) or [])
        )
        for rel in relationships:
            child_id = getattr(getattr(rel, "child", None), "resourceId", "")
            parent1 = getattr(getattr(rel, "parent1", None), "resourceId", "")
            parent2 = getattr(getattr(rel, "parent2", None), "resourceId", "")
            if row.kind in ("father", "mother"):
                if child_id == fsid and row.fs_id in (parent1, parent2):
                    return rel
            elif row.kind == "child":
                if row.fs_id == child_id and fsid in (parent1, parent2):
                    return rel
        return None

    def _import_related_person(self, importer: Any, fsid: str) -> bool:
        """
        Ensure a FamilySearch relative exists as a Gramps person.
        """
        fsid = (fsid or "").strip()
        if not fsid:
            return False
        self._ensure_person_cached(fsid, with_relatives=False)
        fs_person = deserialize.Person.index.get(fsid)
        if fs_person is None:
            return False
        importer.add_person(self.dbstate.db, importer.txn, fs_person)
        return True

    def _merge_relative_row(
        self, importer: Any, gr: Person, fs_person: Any, row: _FSMergeRow
    ) -> bool:
        """
        Import and link a selected FamilySearch relative row.
        """
        fs_utilities.FS_INDEX_PEOPLE[getattr(fs_person, "id", "")] = gr.handle
        if not self._import_related_person(importer, row.fs_id):
            return False

        if row.kind in ("father", "mother", "child"):
            rel = self._fs_child_parent_for_row(fs_person, row)
            if rel is None:
                return False
            if row.kind == "child":
                parent_ids = [
                    getattr(getattr(rel, "parent1", None), "resourceId", ""),
                    getattr(getattr(rel, "parent2", None), "resourceId", ""),
                ]
                for parent_id in parent_ids:
                    if parent_id and parent_id != getattr(fs_person, "id", ""):
                        self._import_related_person(importer, parent_id)
            importer.add_child(rel)
            return True

        if row.kind == "spouse":
            couple = self._fs_couple_for_row(fs_person, row)
            if couple is None:
                return False
            importer.add_family(couple)
            return True
        return False

    def _apply_selected_merge_rows(
        self, row_source: Any, gr: Optional[Person], fsid: str, parent: Gtk.Window
    ) -> int:
        """
        Apply selected FamilySearch rows into Gramps and return the change count.
        """
        if gr is None:
            WarningDialog(_("Could not resolve the selected person."), parent=parent)
            return 0

        if isinstance(row_source, list):
            rows = self._selected_merge_rows_from_list(row_source)
        else:
            rows = self._selected_merge_rows(row_source)
        if not rows:
            WarningDialog(
                _("Select at least one FamilySearch row to merge."), parent=parent
            )
            return 0

        question = QuestionDialog2(
            _("FamilySearch Compare/Merge"),
            GLib.markup_escape_text(
                _(
                    "Copy {count} selected FamilySearch item(s) into the Gramps person?"
                ).format(count=len(rows))
            ),
            _("_Merge"),
            _("_Cancel"),
            parent=parent,
        )
        if not question.run():
            return 0

        fs_person = deserialize.Person.index.get(fsid) or deserialize.Person()
        db = self.dbstate.db
        changed = 0

        with DbTxn(_("FamilySearch: Merge selected rows"), db) as txn:
            importer = fs_import.FSToGrampsImporter()
            importer.dbstate = self.dbstate
            importer.txn = txn
            importer.noreimport = True
            importer.fs_TreeImp = self.__class__.fs_Tree

            for row in rows:
                try:
                    if row.kind == "gender":
                        changed += int(self._merge_gender_row(gr, fs_person))
                    elif row.kind in ("primary_name", "name"):
                        changed += int(
                            self._merge_name_row(db, txn, gr, fs_person, row)
                        )
                    elif row.kind == "fact":
                        changed += int(
                            self._merge_person_fact_row(
                                db, txn, gr, fs_person, row
                            )
                        )
                    elif row.kind == "spouse_fact":
                        changed += int(
                            self._merge_family_fact_row(db, txn, fs_person, row)
                        )
                    elif row.kind in ("father", "mother", "spouse", "child"):
                        changed += int(
                            self._merge_relative_row(importer, gr, fs_person, row)
                        )
                except Exception:
                    continue

            db.commit_person(gr, txn)

        if changed:
            OkDialog(
                _("FamilySearch Compare/Merge"),
                _("{count} item(s) copied into Gramps.").format(count=changed),
                parent=parent,
            )
        else:
            WarningDialog(
                _("FamilySearch Compare/Merge"),
                _("No selected rows could be copied into Gramps."),
                parent=parent,
            )
        return changed

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
        win.set_title(_("FamilySearch Compare/Merge"))
        win.set_transient_for(self.uistate.window)
        win.set_default_size(1420, 820)
        win.get_style_context().add_class("fs-compare-window")

        # headerbar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = _("FamilySearch Compare/Merge")
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

        instruction = Gtk.Label(
            label=_(
                "Review FamilySearch differences, choose the rows to copy, "
                "then merge them into Gramps. The direction is FamilySearch "
                "to Gramps only."
            )
        )
        instruction.set_xalign(0.0)
        instruction.set_line_wrap(True)
        instruction.get_style_context().add_class("fs-merge-instruction")
        outer.pack_start(instruction, False, False, 0)

        notebook = Gtk.Notebook()
        notebook.get_style_context().add_class("fs-compare-notebook")
        outer.pack_start(notebook, True, True, 0)

        # merge tab
        merge_host = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        merge_state: dict[str, Any] = {"rows": []}
        notebook.append_page(
            self._wrap_scroller(merge_host, min_h=560),
            Gtk.Label(label=_("Merge")),
        )

        # audit/details tab: preserves the original overview table.
        tv_overview, model_overview = self._make_overview_tree_model()
        tv_overview.get_style_context().add_class("fs-compare-treeview")
        self._tune_treeview(tv_overview, "overview")
        self._install_treeview_row_tints(tv_overview)
        notebook.append_page(
            self._wrap_scroller(tv_overview), Gtk.Label(label=_("Audit Details"))
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

        btn_merge_text = Gtk.Button(label=_("Merge selected"))
        btn_refresh_text = Gtk.Button(label=_("Refresh"))
        btn_import_sources_text = Gtk.Button(label=_("Import sources..."))
        btn_close_text = Gtk.Button(label=_("Close"))

        btn_merge_text.get_style_context().add_class("suggested-action")
        action_box.pack_end(btn_close_text, False, False, 0)
        action_box.pack_end(btn_merge_text, False, False, 0)
        action_box.pack_end(btn_import_sources_text, False, False, 0)
        action_box.pack_end(btn_refresh_text, False, False, 0)

        outer.pack_end(action_box, False, False, 0)

        def do_fill_all(force: bool = False) -> None:
            if force:
                self._ensure_person_cached(fsid, with_relatives=True, force=True)

            gr_local = _get_gr()
            if not gr_local:
                return

            for child in list(merge_host.get_children() or []):
                merge_host.remove(child)
            merge_board, merge_rows = self._build_merge_board(gr_local, fsid)
            merge_state["rows"] = merge_rows
            merge_host.pack_start(merge_board, True, True, 0)
            merge_host.show_all()

            model_overview.clear()
            self._fill_overview(model_overview, gr_local, fsid)

            model_notes.clear()
            self._fill_notes(model_notes, gr_local, fsid)

            model_sources.clear()
            self._fill_sources(model_sources, gr_local, fsid, parent=win)

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
            self._fill_sources(model_sources, _get_gr(), fsid, parent=win)

        def do_merge_selected(_btn: Any) -> None:
            changed = self._apply_selected_merge_rows(
                merge_state.get("rows", []), _get_gr(), fsid, win
            )
            if changed:
                do_fill_all(False)

        btn_refresh.connect("clicked", lambda *_: do_fill_all(True))
        btn_refresh_text.connect("clicked", lambda *_: do_fill_all(True))

        btn_import_sources.connect("clicked", do_import_sources)
        btn_import_sources_text.connect("clicked", do_import_sources)
        btn_merge_text.connect("clicked", do_merge_selected)

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
        return fs_import.normalize_source_url(url)

    def _step_progress_meter(self, progress: ProgressMeter, header: str) -> None:
        """
        Advance a progress meter while updating its header text.
        """
        progress.set_header(header)
        progress.step()

    def _collect_compare_source_ids(self, fs_person: Any) -> list[str]:
        """
        Return ordered FamilySearch source description IDs for a compare person.
        """
        source_ids: list[str] = []
        seen: set[str] = set()

        def add_source_refs(source_refs: Any) -> None:
            for source_ref in source_refs or []:
                sdid = getattr(source_ref, "descriptionId", "") or ""
                if sdid and sdid not in seen:
                    seen.add(sdid)
                    source_ids.append(sdid)

        add_source_refs(getattr(fs_person, "sources", []) or [])
        for rel in getattr(fs_person, "_spouses", []) or []:
            add_source_refs(getattr(rel, "sources", []) or [])
        return source_ids

    def _prepare_compare_sources(
        self, fsid: str, parent: Any | None = None
    ) -> tuple[Any, dict[str, Any], list[str]]:
        """
        Load and hydrate FamilySearch sources for the compare dialog.
        """
        parent_window = parent
        try:
            if parent_window and not parent_window.get_visible():
                parent_window = None
        except Exception:
            parent_window = None
        if parent_window is None:
            parent_window = getattr(self.uistate, "window", None)
        progress = ProgressMeter(
            _("FamilySearch Compare"),
            _("Preparing FamilySearch sources"),
            parent=parent_window,
        )
        try:
            fs_person = deserialize.Person.index.get(fsid) or deserialize.Person()
            fetch_total = 1 + len(getattr(fs_person, "_spouses", []) or [])
            progress.set_pass(_("Loading source links (1/2)"), max(fetch_total, 1))
            self._ensure_sources_cached(
                fsid,
                progress_callback=lambda header: self._step_progress_meter(
                    progress, header
                ),
            )

            fs_person = deserialize.Person.index.get(fsid) or deserialize.Person()
            source_ids = self._collect_compare_source_ids(fs_person)
            for sdid in source_ids:
                if sdid in deserialize.SourceDescription._index:
                    continue
                sd_new = deserialize.SourceDescription()
                sd_new.id = sdid
                deserialize.SourceDescription._index[sdid] = sd_new
                try:
                    if self.__class__.fs_Tree is not None:
                        self.__class__.fs_Tree.sourceDescriptions.add(sd_new)
                except Exception:
                    pass
            progress.set_pass(
                _("Parsing source details (2/2)"), max(len(source_ids), 1)
            )
            if self.__class__.fs_Tree is not None and source_ids:
                fs_import.fetch_source_dates(
                    self.__class__.fs_Tree,
                    source_ids=source_ids,
                    progress_callback=lambda header: self._step_progress_meter(
                        progress, header
                    ),
                )

            return fs_person, self._gather_sr_meta(fsid), source_ids
        finally:
            progress.close()

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

    def _fill_sources(
        self, model: Any, gr: Person, fsid: str, parent: Any | None = None
    ) -> None:
        fs_person, source_meta, source_ids = self._prepare_compare_sources(
            fsid, parent=parent
        )
        em = "_"
        fs_placeholder = (
            em if self.__class__.fs_Tree else _("Not connected to FamilySearch")
        )

        # Collect FS SourceDescription IDs referenced by person + spouse relationships
        fs_source_ids: dict[str, None] = {sdid: None for sdid in source_ids}

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
            date: str = fs_import.normalize_source_date(
                fs_utilities.gramps_date_to_formal(c.date)
            )

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
                fs_date = fs_import.normalize_source_date(src_fs.date)
                fs_url = self._canon_fs_web(getattr(src_fs, "url", None))

                meta = source_meta.get(sd_id, {}) or {}
                kind = str(meta.get("kind") or "")
                tags_disp = self._pretty_tags(meta.get("tags", []))
                contributor = str(meta.get("contributor") or "")
                modified = str(meta.get("modified") or "")

                color = "orange"
                if fs_import.source_values_match(
                    date,
                    title,
                    gr_url,
                    note_text,
                    fs_date,
                    fs_title,
                    fs_url,
                    fs_text,
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

            fs_date_val = (
                fs_import.normalize_source_date(getattr(sd_obj2, "_date", ""))
                if sd_obj2 is not None
                else ""
            )
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
                        fs_date_val or em,
                        fs_title or em,
                        fs_url2 or em,
                        tags_disp,
                        contributor,
                        modified,
                        sdid,
                    ]
                )
            )
