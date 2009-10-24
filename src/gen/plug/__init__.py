#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Brian G. Matherly
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
The "plug" package for handling plugins in Gramps.
"""

from _plugin import Plugin
from _pluginreg import (PluginData, PluginRegister, REPORT, TOOL, 
            CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_CODE, 
            CATEGORY_WEB, CATEGORY_BOOK, CATEGORY_GRAPHVIZ,
            TOOL_DEBUG, TOOL_ANAL, TOOL_DBPROC, TOOL_DBFIX, TOOL_REVCTL,
            TOOL_UTILS, CATEGORY_QR_MISC, CATEGORY_QR_PERSON, 
            CATEGORY_QR_FAMILY, CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE,
            CATEGORY_QR_PLACE, CATEGORY_QR_REPOSITORY, CATEGORY_QR_NOTE,
            CATEGORY_QR_DATE, PTYPE_STR )
from _manager import PluginManager
from _import import ImportPlugin
from _export import ExportPlugin
from _docgenplugin import DocGenPlugin
from utils import *

__all__ = [ "docbackend", "docgen", "menu", Plugin, PluginData,
            PluginRegister, PluginManager, 
            ImportPlugin, ExportPlugin, DocGenPlugin,
            REPORT, TOOL, CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_CODE, 
            CATEGORY_WEB, CATEGORY_BOOK, CATEGORY_GRAPHVIZ,
            TOOL_DEBUG, TOOL_ANAL, TOOL_DBPROC, TOOL_DBFIX, TOOL_REVCTL,
            TOOL_UTILS, CATEGORY_QR_MISC, CATEGORY_QR_PERSON, 
            CATEGORY_QR_FAMILY, CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE,
            CATEGORY_QR_PLACE, CATEGORY_QR_REPOSITORY, CATEGORY_QR_NOTE,
            CATEGORY_QR_DATE, PTYPE_STR]
