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

from __future__ import annotations

from gramps.gen.plug.menu import StringOption, BooleanOption, NumberOption
from gramps.gui.plug import MenuToolOptions

from . import _
import gramps.gui.fs.person.fsg_sync as FSG_Sync


class FSImportOptions(MenuToolOptions):
    # options panel for FS Import tool

    def __init__(self, name, person_id=None, dbstate=None):
        super().__init__(name, person_id, dbstate)

    def add_menu_options(self, menu):
        category = _("FamilySearch Import Options")

        self._FS_ID = StringOption(_("FamilySearch ID"), "XXXX-XXX")
        self._FS_ID.set_help(_("identifier to be copied from the FamilySearch website"))
        menu.add_option(category, "FS_ID", self._FS_ID)

        self._gui_asc = NumberOption(_("Ancestor generations"), 0, 0, 99)
        self._gui_asc.set_help(_("Number of generations to fetch upwards"))
        menu.add_option(category, "gui_asc", self._gui_asc)

        self._gui_desc = NumberOption(_("Descendant generations"), 0, 0, 99)
        self._gui_desc.set_help(_("Number of generations to fetch downwards"))
        menu.add_option(category, "gui_desc", self._gui_desc)

        self._gui_noreimport = BooleanOption(
            _("Do not re-import existing persons"), True
        )
        self._gui_noreimport.set_help(_("Only import persons not already present"))
        menu.add_option(category, "gui_noreimport", self._gui_noreimport)

        self._gui_spouses = BooleanOption(_("Include spouses"), False)
        self._gui_spouses.set_help(_("Include spouse information"))
        menu.add_option(category, "gui_include_spouses", self._gui_spouses)

        self._gui_sources = BooleanOption(_("Include sources"), False)
        self._gui_sources.set_help(_("Import sources"))
        menu.add_option(category, "gui_include_sources", self._gui_sources)

        self._gui_notes = BooleanOption(_("Include notes"), False)
        self._gui_notes.set_help(_("Import notes"))
        menu.add_option(category, "gui_include_notes", self._gui_notes)

        self._gui_verbosity = NumberOption(_("Verbosity"), 0, 0, 3)
        self._gui_verbosity.set_help(
            _("Verbosity level from 0 (min) to 3 (very verbose)")
        )
        menu.add_option(category, "gui_verbosity", self._gui_verbosity)

    def load_previous_values(self):
        super().load_previous_values()
        if FSG_Sync.FSG_Sync.FSID:
            self.handler.options_dict["FS_ID"] = FSG_Sync.FSG_Sync.FSID
