# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026    Gabriel Rios
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
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from gramps.gen.fs.tags import (
    TAG_LINKED,
    TAG_NOT_LINKED,
    TAG_SYNCED,
    TAG_OUT_OF_SYNC,
    ALL_FS_TAGS,
    DEFAULT_TAG_COLORS,
    EXCLUSIVE_SETS,
    ensure_fs_tags,
    retag_all_link_status,
    set_sync_status_for_person,
    compute_sync_from_payload,
    explain_out_of_sync,
    get_tag_color_ui_note,
)


def build_tag_color_note_widget():
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    try:
        img = Gtk.Image.new_from_icon_name("dialog-information", Gtk.IconSize.MENU)
        box.pack_start(img, False, False, 0)
    except Exception:
        pass

    lbl = Gtk.Label(label=get_tag_color_ui_note())
    lbl.set_xalign(0.0)
    lbl.set_line_wrap(True)
    lbl.set_max_width_chars(80)

    try:
        lbl.set_selectable(True)
    except Exception:
        pass

    box.pack_start(lbl, True, True, 0)
    return box


__all__ = [
    "TAG_LINKED",
    "TAG_NOT_LINKED",
    "TAG_SYNCED",
    "TAG_OUT_OF_SYNC",
    "ALL_FS_TAGS",
    "DEFAULT_TAG_COLORS",
    "EXCLUSIVE_SETS",
    "ensure_fs_tags",
    "retag_all_link_status",
    "set_sync_status_for_person",
    "compute_sync_from_payload",
    "explain_out_of_sync",
    "get_tag_color_ui_note",
    "build_tag_color_note_widget",
]
