#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Utility functions to cast types
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import os
import sys
import logging

LOG = logging.getLogger(".")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


def cast_to_bool(val):
    return val in ["True", "true", _("True"), _("true"), "1"]  # 3139


def get_type_converter(val):
    """
    Return function that converts strings into the type of val.
    """
    val_type = type(val)
    if isinstance(val, str):
        return str
    elif val_type == int:
        return int
    elif val_type == float:
        return float
    elif val_type == bool:
        return cast_to_bool
    elif val_type in (list, tuple):
        return list


def type_name(val):
    """
    Return the name the type of val.

    Only numbers and strings are supported.
    The rest becomes strings (unicode).
    """
    val_type = type(val)
    if val_type == int:
        return "int"
    elif val_type == float:
        return "float"
    elif val_type == bool:
        return "bool"
    elif isinstance(val, str):
        return "unicode"
    return "unicode"


def get_type_converter_by_name(val_str):
    """
    Return function that converts strings into the type given by val_str.

    Only numbers and strings are supported.
    The rest becomes strings (unicode).
    """
    if val_str == "int":
        return int
    elif val_str == "float":
        return float
    elif val_str == "bool":
        return cast_to_bool
    elif val_str in ("str", "unicode"):
        return str
    return str
