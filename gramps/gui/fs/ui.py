# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025-2026  Gabriel Rios
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

from typing import Optional, Protocol, Sequence, Tuple

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango  # noqa: E402

from gramps.gui.dialog import ErrorDialog, OkDialog, WarningDialog

# ----------------------------------------------------------------------
# CSS install
# ----------------------------------------------------------------------

_CSS_KEYS: set[str] = set()


def install_css_once(key: str, css: bytes) -> bool:
    k = (key or "fs.css").strip() or "fs.css"
    if k in _CSS_KEYS:
        return True
    try:
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        if screen is not None:
            Gtk.StyleContext.add_provider_for_screen(
                screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        _CSS_KEYS.add(k)
        return True
    except Exception:
        return False


# ----------------------------------------------------------------------
# Headerbar helpers
# ----------------------------------------------------------------------


class _HasTitlebar(Protocol):
    def set_titlebar(self, titlebar: Gtk.Widget) -> None: ...


def set_headerbar(widget: _HasTitlebar, title: str, subtitle: str = "") -> None:
    try:
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = title or ""
        if subtitle:
            hb.props.subtitle = subtitle
        widget.set_titlebar(hb)
    except Exception:
        pass


def wrap_scroller(child: Gtk.Widget, min_h: int = 360) -> Gtk.ScrolledWindow:
    sw = Gtk.ScrolledWindow()
    sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    try:
        sw.set_min_content_height(min_h)
    except Exception:
        pass
    sw.add(child)
    return sw


def tune_treeview(
    tv: Gtk.TreeView, *, headers: bool = True, grid: bool = True, rules: bool = True
) -> None:
    try:
        tv.set_headers_visible(bool(headers))
    except Exception:
        pass

    if grid:
        try:
            tv.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        except Exception:
            pass

    if rules:
        try:
            tv.set_rules_hint(True)
        except Exception:
            pass

    cols = tv.get_columns() or []
    for col in cols:
        try:
            col.set_resizable(True)
            col.set_reorderable(True)
        except Exception:
            pass

        try:
            for r in col.get_cells() or []:
                if isinstance(r, Gtk.CellRendererText):
                    try:
                        r.set_property("ellipsize", Pango.EllipsizeMode.END)
                    except Exception:
                        pass
        except Exception:
            pass


# ----------------------------------------------------------------------
# Color resolution: from gramps.css
# ----------------------------------------------------------------------

_TOKEN_TO_DEFINE_COLOR = {
    "match": "fs_compare_match_bg",
    "different": "fs_compare_different_bg",
    "only-gramps": "fs_compare_only_gramps_bg",
    "only_fs": "fs_compare_only_fs_bg",
    "only-fs": "fs_compare_only_fs_bg",
    "critical": "fs_compare_critical_bg",
    # legacy palette tokens
    "green": "fs_compare_match_bg",
    "orange": "fs_compare_different_bg",
    "yellow": "fs_compare_only_gramps_bg",
    "blue": "fs_compare_only_fs_bg",
    "yellow3": "fs_compare_only_fs_bg",
    "red": "fs_compare_critical_bg",
}

_DEFINE_COLOR_FALLBACK_HEX = {
    "fs_compare_match_bg": "#D8F3DC",
    "fs_compare_different_bg": "#FFE8CC",
    "fs_compare_only_gramps_bg": "#FFF3BF",
    "fs_compare_only_fs_bg": "#D0EBFF",
    "fs_compare_critical_bg": "#FFE3E3",
}

# used when caller passes "green"/etc directly and CSS lookup fails
_LEGACY_TOKEN_FALLBACK_HEX = {
    "green": "#D8F3DC",
    "orange": "#FFE8CC",
    "yellow": "#FFF3BF",
    "yellow3": "#D0EBFF",
    "blue": "#D0EBFF",
    "red": "#FFE3E3",
}


def _lookup_defined_color(
    name: str, *, widget: Optional[Gtk.Widget] = None
) -> Optional[Gdk.RGBA]:
    if not name:
        return None
    try:
        w = widget or Gtk.Label()
        ctx = w.get_style_context()
        ok, rgba = ctx.lookup_color(name)
        if ok and isinstance(rgba, Gdk.RGBA):
            return rgba
    except Exception:
        pass
    return None


def _parse_color_literal(s: str) -> Optional[Gdk.RGBA]:
    if not s:
        return None
    try:
        rgba = Gdk.RGBA()
        if rgba.parse(s.strip()):
            return rgba
    except Exception:
        pass
    return None


def resolve_fs_bg_color(
    token_or_color: str, *, widget: Optional[Gtk.Widget] = None
) -> Optional[Gdk.RGBA]:
    s = (token_or_color or "").strip()
    if not s:
        return None

    name = _TOKEN_TO_DEFINE_COLOR.get(s, "")

    if not name and s.startswith("fs_"):
        name = s

    if name:
        rgba = _lookup_defined_color(name, widget=widget)
        if rgba is not None:
            return rgba

        hx = _DEFINE_COLOR_FALLBACK_HEX.get(name)
        if hx:
            rgba = _parse_color_literal(hx)
            if rgba is not None:
                return rgba

    if s in _LEGACY_TOKEN_FALLBACK_HEX:
        return _parse_color_literal(_LEGACY_TOKEN_FALLBACK_HEX[s])

    return _parse_color_literal(s)


def set_cell_bg(
    cell: Gtk.CellRenderer, color_token: str, *, widget: Optional[Gtk.Widget] = None
) -> None:
    rgba = resolve_fs_bg_color(color_token, widget=widget)
    if rgba is None:
        clear_cell_bg(cell)
        return

    try:
        cell.set_property("cell-background-rgba", rgba)
        cell.set_property("cell-background-set", True)
        return
    except Exception:
        pass

    try:
        cell.set_property("cell-background", rgba.to_string())
        cell.set_property("cell-background-set", True)
    except Exception:
        pass


def clear_cell_bg(cell: Gtk.CellRenderer) -> None:
    try:
        cell.set_property("cell-background-set", False)
        return
    except Exception:
        pass

    try:
        cell.set_property("cell-background", "")
        cell.set_property("cell-background-set", False)
    except Exception:
        pass


def build_legend_row(
    items: Sequence[Tuple[str, str]],
    *,
    hint: str = "",
    wrap_class: str = "",
) -> Gtk.Widget:
    wrap = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    if wrap_class:
        try:
            wrap.get_style_context().add_class(wrap_class)
        except Exception:
            pass

    token_to_pill_class = {
        "match": "fs-match",
        "different": "fs-different",
        "only-gramps": "fs-only-gramps",
        "only-fs": "fs-only-fs",
        "critical": "fs-critical",
        "green": "fs-match",
        "orange": "fs-different",
        "yellow": "fs-only-gramps",
        "blue": "fs-only-fs",
        "yellow3": "fs-only-fs",
        "red": "fs-critical",
    }

    def pill(kind: str, text: str) -> Gtk.Widget:
        kind = (kind or "").strip()

        if kind in token_to_pill_class:
            kind_class = token_to_pill_class[kind]
        elif kind.startswith("fs-"):
            kind_class = kind
        else:
            kind_class = ""

        eb = Gtk.EventBox()
        eb.set_visible_window(True)

        ctx = eb.get_style_context()
        ctx.add_class("fs-legend-pill")
        if kind_class:
            ctx.add_class(kind_class)

        lbl = Gtk.Label(label=text)
        lbl.get_style_context().add_class("fs-legend-label")
        eb.add(lbl)
        return eb

    for kind, label in items:
        wrap.pack_start(pill(kind, label), False, False, 0)

    if hint:
        h = Gtk.Label(label=hint)
        h.set_xalign(1.0)
        try:
            h.set_ellipsize(Pango.EllipsizeMode.END)
        except Exception:
            pass
        wrap.pack_end(h, True, True, 0)

    return wrap


def set_button_icon_and_label(btn: Gtk.Button, icon_name: str, label: str) -> None:
    try:
        img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        btn.set_image(img)
        btn.set_always_show_image(True)
        btn.set_label(label)
        return
    except Exception:
        pass

    try:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        box.pack_start(img, False, False, 0)
        box.pack_start(Gtk.Label(label=label), False, False, 0)
        btn.add(box)
    except Exception:
        pass


def info_dialog(parent: Optional[Gtk.Window], title: str, body: str) -> None:
    OkDialog(title or "", body or "", parent=parent)


def error_dialog(parent: Optional[Gtk.Window], title: str, body: str) -> None:
    ErrorDialog(title or "", body or "", parent=parent)


def warn_dialog(parent: Optional[Gtk.Window], title: str, body: str) -> None:
    WarningDialog(title or "", body or "", parent=parent)
