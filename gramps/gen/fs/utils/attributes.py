#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2025  Gabriel Rios
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
from typing import Optional

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


def _iter_attrs(gr_obj):
    if not gr_obj:
        return []
    try:
        if hasattr(gr_obj, "get_attribute_list"):
            return gr_obj.get_attribute_list() or []
        return getattr(gr_obj, "attribute_list", []) or []
    except Exception:
        return getattr(gr_obj, "attribute_list", []) or []


def _type_names(t) -> list[str]:
    out: list[str] = []
    if t is None:
        return out
    try:
        if hasattr(t, "xml_str"):
            s = t.xml_str()
            if s:
                out.append(str(s))
    except Exception:
        pass
    try:
        s = str(t)
        if s:
            out.append(s)
    except Exception:
        pass
    return out


def get_fsftid(gr_obj) -> str:
    # return the value of the _FSFTID attribute in a Gramps object, else ''
    if not gr_obj:
        return ""
    for attr in _iter_attrs(gr_obj):
        try:
            t = attr.get_type()
            if any(name == "_FSFTID" for name in _type_names(t)):
                return attr.get_value() or ""
        except Exception:
            pass
    return ""


def get_internet_address(gr_obj) -> Optional[str]:
    # return the value of the 'Internet Address' attribute
    if not gr_obj:
        return None

    want = _("Internet Address")
    for attr in _iter_attrs(gr_obj):
        try:
            t = attr.get_type()
            names = _type_names(t)
            if any(n == want or n == "Internet Address" for n in names):
                return attr.get_value()
        except Exception:
            pass
    return None
