#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2013       Nick Hall
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

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .editsecondary import EditSecondary
from ..glade import Glade
from ..widgets import MonitoredDate
from .objectentries import PlaceEntry
from ..dialog import ErrorDialog
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# EditPlaceRef class
#
#-------------------------------------------------------------------------
class EditPlaceRef(EditSecondary):

    def __init__(self, dbstate, uistate, track, placeref, handle, callback):
        self.handle = handle
        EditSecondary.__init__(self, dbstate, uistate, track,
                               placeref, callback)

    def _local_init(self):
        self.width_key = 'interface.place-ref-width'
        self.height_key = 'interface.place-ref-height'
        self.top = Glade()
        self.set_window(self.top.toplevel, None, _('Place Reference Editor'))

        self.share_btn = self.top.get_object('select_place')
        self.add_del_btn = self.top.get_object('add_del_place')

    def _setup_fields(self):

        self.date_field = MonitoredDate(self.top.get_object("date_entry"),
                                        self.top.get_object("date_stat"),
                                        self.obj.get_date_object(),
                                        self.uistate, self.track, 
                                        self.db.readonly)

        self.place_field = PlaceEntry(self.dbstate, self.uistate, self.track,
                                      self.top.get_object("place"),
                                      self.obj.set_reference_handle,
                                      self.obj.get_reference_handle,
                                      self.add_del_btn, self.share_btn,
                                      skip=self.get_skip_list(self.handle))

    def get_skip_list(self, handle):
        todo = [handle]
        skip = [handle]
        while todo:
            handle = todo.pop()
            for child in self.db.find_backlink_handles(handle, ['Place']):
                if child[1] not in skip:
                    todo.append(child[1])
                    skip.append(child[1])
        return skip

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object('cancel_button'))
        self.ok_button = self.top.get_object('ok_button')
        self.define_ok_button(self.ok_button, self.save)
        self.define_help_button(self.top.get_object('help_button'))

    def save(self, *obj):
        self.ok_button.set_sensitive(False)
        if not self.obj.ref:
            ErrorDialog(_("Cannot save place reference"),
                        _("No place selected. Please select a place "
                          " or cancel the edit."))
            self.ok_button.set_sensitive(True)
            return

        if self.callback:
            self.callback(self.obj)
        self.close()
