#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Brian G. Matherly
# Copyright (C) 2010  Jakim Friant
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
The "plug" package for handling plugins in Gramps.
"""

from ._plugin import Plugin
from ._pluginreg import (
    PluginData,
    PluginRegister,
    REPORT,
    TOOL,
    CATEGORY_TEXT,
    CATEGORY_DRAW,
    CATEGORY_CODE,
    CATEGORY_WEB,
    CATEGORY_BOOK,
    CATEGORY_GRAPHVIZ,
    CATEGORY_TREE,
    TOOL_DEBUG,
    TOOL_ANAL,
    TOOL_DBPROC,
    TOOL_DBFIX,
    TOOL_REVCTL,
    TOOL_UTILS,
    CATEGORY_QR_MISC,
    CATEGORY_QR_PERSON,
    CATEGORY_QR_FAMILY,
    CATEGORY_QR_EVENT,
    CATEGORY_QR_SOURCE,
    CATEGORY_QR_PLACE,
    CATEGORY_QR_REPOSITORY,
    CATEGORY_QR_NOTE,
    CATEGORY_QR_DATE,
    PTYPE_STR,
    CATEGORY_QR_MEDIA,
    CATEGORY_QR_CITATION,
    CATEGORY_QR_SOURCE_OR_CITATION,
    START,
    END,
    make_environment,
    AUDIENCETEXT,
    STATUSTEXT,
)
from ._import import ImportPlugin
from ._export import ExportPlugin
from ._docgenplugin import DocGenPlugin
from ._manager import BasePluginManager
from ._gramplet import Gramplet
from ._thumbnailer import Thumbnailer
from .utils import *
from ._options import (
    Options,
    OptionListCollection,
    OptionList,
    OptionHandler,
    MenuOptions,
)

__all__ = [
    "docbackend",
    "docgen",
    "menu",
    "Plugin",
    "PluginData",
    "PluginRegister",
    "BasePluginManager",
    "ImportPlugin",
    "ExportPlugin",
    "DocGenPlugin",
    "REPORT",
    "TOOL",
    "CATEGORY_TEXT",
    "CATEGORY_DRAW",
    "CATEGORY_CODE",
    "CATEGORY_WEB",
    "CATEGORY_BOOK",
    "CATEGORY_GRAPHVIZ",
    "CATEGORY_TREE",
    "TOOL_DEBUG",
    "TOOL_ANAL",
    "TOOL_DBPROC",
    "TOOL_DBFIX",
    "TOOL_REVCTL",
    "TOOL_UTILS",
    "CATEGORY_QR_MISC",
    "CATEGORY_QR_PERSON",
    "CATEGORY_QR_FAMILY",
    "CATEGORY_QR_EVENT",
    "CATEGORY_QR_SOURCE",
    "CATEGORY_QR_PLACE",
    "CATEGORY_QR_REPOSITORY",
    "CATEGORY_QR_NOTE",
    "CATEGORY_QR_DATE",
    "PTYPE_STR",
    "CATEGORY_QR_MEDIA",
    "CATEGORY_QR_CITATION",
    "CATEGORY_QR_SOURCE_OR_CITATION",
    "START",
    "END",
    "make_environment",
]
