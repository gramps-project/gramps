#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2014-2015  Nick Hall
# Copyright (C) 2019       Paul Culley
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
""" Edit Place Abbreviation """
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import URL_MANUAL_SECT2
from gramps.gen.const import GRAMPS_LOCALE as glocale
from .editsecondary import EditSecondary
from ..glade import Glade
from ..dialog import ErrorDialog
from ..widgets import MonitoredDataType, MonitoredEntry
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT2
WIKI_HELP_SEC = _('manual|Place_Abbreviation_Editor_dialog')


#-------------------------------------------------------------------------
#
# EditPlaceAbbrev class
#
#-------------------------------------------------------------------------
class EditPlaceAbbrev(EditSecondary):
    """
    Displays a dialog that allows the user to edit a place abbrev.
    """
    def __init__(self, dbstate, uistate, track, abbrev, callback):
        EditSecondary.__init__(self, dbstate, uistate, track, abbrev, callback)

    def _local_init(self):

        self.top = Glade()
        self.set_window(self.top.toplevel,
                        self.top.get_object("title"),
                        _('Place Abbreviation Editor'))
        self.setup_configs('interface.place-abbrev', 450, 150)

    def _setup_fields(self):
        self.value = MonitoredEntry(
            self.top.get_object("value"), self.obj.set_value,
            self.obj.get_value, self.db.readonly)

        custom_place_abbrev_types = sorted(self.db.get_placeabbr_types(),
                                           key=lambda s: s.lower())
        self.place_type = MonitoredDataType(self.top.get_object("abbrev_type"),
                                            self.obj.set_type,
                                            self.obj.get_type,
                                            self.db.readonly,
                                            custom_place_abbrev_types)

    def _connect_signals(self):
        self.define_help_button(self.top.get_object('help'),
                                WIKI_HELP_PAGE, WIKI_HELP_SEC)
        self.define_cancel_button(self.top.get_object('cancel'))
        self.define_ok_button(self.top.get_object('ok'), self.save)

    def build_menu_names(self, obj):
        return (_('Place Abbreviation'), _('Place Abbreviation Editor'))

    def save(self, *obj):
        """ Check for valid and make callback """
        if not self.obj.get_value():
            ErrorDialog(_("Cannot save place abbrev"),
                        _("The place abbrev cannot be empty"),
                        parent=self.window)
            return

        if self.callback:
            self.callback(self.obj)
        self.close()
