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
import importlib
from typing import Any

_LAZY_MODULES = {
    "tree": ".tree",
    "session": ".session",
    "constants": ".constants",
    "db_familysearch": ".db_familysearch",
    "tags": ".tags",
    "utils": ".utils",
    "fs_import": ".fs_import",
}

_LAZY_ATTRS = {
    "Session": (".session", "Session"),
    "get_active_session": (".session", "get_active_session"),
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_MODULES:
        mod = importlib.import_module(_LAZY_MODULES[name], package=__name__)
        globals()[name] = mod
        return mod

    if name in _LAZY_ATTRS:
        mod_name, attr = _LAZY_ATTRS[name]
        mod = importlib.import_module(mod_name, package=__name__)
        obj = getattr(mod, attr)
        globals()[name] = obj
        return obj

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(
        set(
            list(globals().keys())
            + list(_LAZY_MODULES.keys())
            + list(_LAZY_ATTRS.keys())
        )
    )


__all__ = [
    "tree",
    "session",
    "constants",
    "db_familysearch",
    "tags",
    "utils",
    "fs_import",
    "Session",
    "get_active_session",
]
