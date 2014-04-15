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
from ..selectors import SelectorFactory
from ..dialog import ErrorDialog
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

SelectPlace = SelectorFactory('Place')

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

    def _setup_fields(self):

        self.date_field = MonitoredDate(self.top.get_object("date_entry"),
                                        self.top.get_object("date_stat"),
                                        self.obj.get_date_object(),
                                        self.uistate, self.track, 
                                        self.db.readonly)

        self.parent = self.top.get_object('place_label')
        if self.obj.ref is not None:
            place = self.db.get_place_from_handle(self.obj.ref)
            self.parent.set_text(place.get_name())
        else:
            self.parent.set_text(_('Top level place'))
        button = self.top.get_object('place_button')
        button.connect('clicked', self.select_parent)

    def get_skip_list(self, handle):
        todo = [handle]
        skip = [handle]
        while todo:
            handle = todo.pop()
            for child in self.dbstate.db.find_place_child_handles(handle):
                todo.append(child)
                skip.append(child)
        return skip

    def select_parent(self, button):
        if self.handle:
            skip = self.get_skip_list(self.handle)
        else:
            skip = []
        sel = SelectPlace(self.dbstate, self.uistate, self.track, skip=skip)
        parent = sel.run()
        if parent:
            self.parent.set_text(parent.get_name())
            self.obj.ref = parent.get_handle()

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object('cancel_button'))
        self.define_ok_button(self.top.get_object('ok_button'), self.save)
        self.define_help_button(self.top.get_object('help_button'))

    def save(self, *obj):
        if self.callback:
            self.callback(self.obj)
        self.close()
