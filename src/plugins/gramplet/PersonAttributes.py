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

from ListModel import ListModel, NOSORT
from QuickReports import run_quick_report_by_name
from gen.plug import Gramplet
from gen.ggettext import gettext as _
import gtk

class PersonAttributes(Gramplet):
    """
    Displays the attributes of a person.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        tip = _('Double-click on a row to view a quick report showing ' + \
                'all people with the selected attribute.')
        self.gui.tooltip = tip
        top = gtk.TreeView()
        titles = [(_('Key'), 1, 100),
                  (_('Value'), 2, 100)]
        self.model = ListModel(top, titles, event_func=self.display_report)
        return top
        
    def db_changed(self):
        self.dbstate.db.connect('person-update', self.update)
        self.update()

    def active_changed(self, handle):
        self.update()

    def main(self): # return false finishes
        active_handle = self.get_active('Person')
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        if not active_person:
            return
            
        self.model.clear()
        for attr in active_person.get_attribute_list():
            self.model.add((attr.get_type(), attr.get_value()))

    def display_report(self, treeview):
        """
        Display the quick report for matching attribute key.
        """
        model, iter_ = treeview.get_selection().get_selected()
        if iter_:
            key = model.get_value(iter_, 0)
            run_quick_report_by_name(self.dbstate, 
                                     self.uistate, 
                                     'attribute_match', 
                                     key)
