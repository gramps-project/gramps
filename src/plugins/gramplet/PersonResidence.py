# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
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
# $Id$
#

from gen.lib import EventType, EventRoleType
from gui.editors import EditEvent
from ListModel import ListModel, NOSORT
from gen.plug import Gramplet
from gen.ggettext import gettext as _
import DateHandler
import Errors
import gtk

class PersonResidence(Gramplet):
    """
    Displays residence events for a person.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        tip = _('Double-click on a row to edit the selected event.')
        self.set_tooltip(tip)
        top = gtk.TreeView()
        titles = [('', NOSORT, 50,),
                  (_('Date'), 1, 200),
                  (_('Place'), 2, 200)]
        self.model = ListModel(top, titles, event_func=self.edit_event)
        return top
        
    def db_changed(self):
        self.dbstate.db.connect('person-update', self.update)

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active('Person')
        active = self.dbstate.db.get_person_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))

    def get_has_data(self, active_person):
        """
        Return True if the gramplet has data, else return False.
        """
        if active_person:
            for event_ref in active_person.get_event_ref_list():
                if int(event_ref.get_role()) == EventRoleType.PRIMARY:
                    event = self.dbstate.db.get_event_from_handle(event_ref.ref)
                    if int(event.get_type()) == EventType.RESIDENCE:
                        return True
        return False

    def main(self): # return false finishes
        active_handle = self.get_active('Person')
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
            
        self.model.clear()
        if active_person:
            self.display_person(active_person)
        else:
            self.set_has_data(False)

    def display_person(self, active_person):
        """
        Display the residence events of the active person.
        """
        count = 0
        for event_ref in active_person.get_event_ref_list():
            if int(event_ref.get_role()) == EventRoleType.PRIMARY:
                event = self.dbstate.db.get_event_from_handle(event_ref.ref)
                if int(event.get_type()) == EventType.RESIDENCE:
                    self.add_residence(event)
                    count += 1
        self.set_has_data(count > 0)

    def add_residence(self, event):
        """
        Add a residence event to the model.
        """
        date = DateHandler.get_date(event)
        place = ''
        handle = event.get_place_handle()
        if handle:
            place = self.dbstate.db.get_place_from_handle(handle).get_title()
        self.model.add((event.get_handle(), date, place))

    def edit_event(self, treeview):
        """
        Edit the selected event.
        """
        model, iter_ = treeview.get_selection().get_selected()
        if iter_:
            handle = model.get_value(iter_, 0)
            try:
                event = self.dbstate.db.get_event_from_handle(handle)
                EditEvent(self.dbstate, self.uistate, [], event)
            except Errors.WindowActiveError:
                pass
