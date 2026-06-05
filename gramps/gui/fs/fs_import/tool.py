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
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.fs import tree
from gramps.gui.plug import PluginWindows
from . import _
from .options import FSImportOptions
from .importer import FSToGrampsImporter
import gramps.gui.fs.person.fsg_sync as FSG_Sync


class FSImportTool(PluginWindows.ToolManagedWindowBatch):
    # tool window wrapper that wires options -> importer and runs the import.

    def __init__(self, dbstate, user, options_class, name, callback):
        self.uistate = user.uistate
        super().__init__(dbstate, user, options_class, name, callback)

    def get_title(self):
        return _("FamilySearch Import Tool")

    def initial_frame(self):
        return _("FamilySearch Import Options")

    def run(self):
        # Ensure a shared Tree exists
        if not FSG_Sync.FSG_Sync.fs_Tree:
            FSG_Sync.FSG_Sync.fs_Tree = tree.Tree()
            FSG_Sync.FSG_Sync.fs_Tree._getsources = False

        importer = FSToGrampsImporter()
        self._apply_menu_options(importer)

        active_handle = self.uistate.get_active("Person")
        importer.import_tree(self, self.FS_ID)
        self.window.hide()
        if active_handle:
            self.uistate.set_active(active_handle, "Person")

    # map UI options to importer instance
    def _apply_menu_options(self, importer: FSToGrampsImporter):
        menu = self.options.menu
        self.FS_ID = menu.get_option_by_name("FS_ID").get_value()
        importer.asc = menu.get_option_by_name("gui_asc").get_value()
        importer.desc = menu.get_option_by_name("gui_desc").get_value()
        importer.include_spouses = menu.get_option_by_name(
            "gui_include_spouses"
        ).get_value()
        importer.include_notes = menu.get_option_by_name(
            "gui_include_notes"
        ).get_value()
        importer.include_sources = menu.get_option_by_name(
            "gui_include_sources"
        ).get_value()
        importer.noreimport = menu.get_option_by_name("gui_noreimport").get_value()
        importer.verbosity = menu.get_option_by_name("gui_verbosity").get_value()
