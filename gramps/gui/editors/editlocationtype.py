#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .editsecondary import EditSecondary
from .displaytabs import CitationEmbedList
from ..glade import Glade
from ..widgets import MonitoredDate, MonitoredDataType
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.const import URL_MANUAL_SECT2

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT2
WIKI_HELP_SEC = _('manual|Place_Type_Editor_dialog')


#-------------------------------------------------------------------------
#
# EditPlaceType class
#
#-------------------------------------------------------------------------
class EditLocationType(EditSecondary):
    """
    Displays a dialog that allows the user to edit a place type.
    """
    def __init__(self, dbstate, uistate, track, ptype, callback):
        EditSecondary.__init__(self, dbstate, uistate, track, ptype, callback)

    def _local_init(self):
        self.top = Glade()
        self.set_window(self.top.toplevel,
                        self.top.get_object("title"),
                        _('Place Type Editor'))
        self.setup_configs('interface.place-type', 450, 450)

    def _setup_fields(self):
        custom_place_types = sorted(self.db.get_place_types(),
                                    key=lambda s: s.lower())
        self.place_type = MonitoredDataType(self.top.get_object("place_type"),
                                            self.obj.set_type,
                                            self.obj.get_type,
                                            self.db.readonly,
                                            custom_place_types)

        self.date = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_stat"),
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)

    def _connect_signals(self):
        self.define_help_button(self.top.get_object('help'),
                                WIKI_HELP_PAGE, WIKI_HELP_SEC)
        self.define_cancel_button(self.top.get_object('cancel'))
        self.define_ok_button(self.top.get_object('ok'), self.save)

    def build_menu_names(self, obj):
        return (_('Place Type'), _('Place Type Editor'))

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.
        """
        notebook = self.top.get_object('notebook3')
        self.citation_list = CitationEmbedList(self.dbstate,
                                               self.uistate,
                                               self.track,
                                               self.obj.get_citation_list(),
                                               _('Place Type Editor'))
        self._add_tab(notebook, self.citation_list)
        self.track_ref_for_deletion("citation_list")

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.top.get_object('vbox').pack_start(notebook, True, True, 0)

    def save(self, *obj):
        """ make the callback """
        if self.callback:
            self.callback(self.obj)
        self.close()
