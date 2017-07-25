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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Gtk modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gui.listmodel import ListModel
from gramps.gui.plug.quick import run_quick_report_by_name
from gramps.gen.plug import Gramplet
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class Attributes(Gramplet):
    """
    Displays the attributes of an object.
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
        tip = _('Double-click on a row to view a quick report showing '
                'all people with the selected attribute.')
        self.set_tooltip(tip)
        top = Gtk.TreeView()
        titles = [(_('Key'), 1, 100),
                  (_('Value'), 2, 100)]
        self.model = ListModel(top, titles, event_func=self.display_report)
        return top

    def display_attributes(self, obj):
        """
        Display the attributes of an object.
        """
        for attr in obj.get_attribute_list():
            self.model.add((str(attr.get_type()), attr.get_value()))
        self.set_has_data(self.model.count > 0)

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

    def get_has_data(self, obj):
        """
        Return True if the gramplet has data, else return False.
        """
        if obj is None:
            return False
        if obj.get_attribute_list():
            return True
        return False

class PersonAttributes(Attributes):
    """
    Displays the attributes of a person.
    """
    def db_changed(self):
        self.connect(self.dbstate.db, 'person-update', self.update)

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active('Person')
        if active_handle:
            active = self.dbstate.db.get_person_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.model.clear()
        active_handle = self.get_active('Person')
        if active_handle:
            active = self.dbstate.db.get_person_from_handle(active_handle)
            if active:
                self.display_attributes(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

class EventAttributes(Attributes):
    """
    Displays the attributes of an event.
    """
    def db_changed(self):
        self.connect(self.dbstate.db, 'event-update', self.update)
        self.connect_signal('Event', self.update)

    def update_has_data(self):
        active_handle = self.get_active('Event')
        if active_handle:
            active = self.dbstate.db.get_event_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.model.clear()
        active_handle = self.get_active('Event')
        if active_handle:
            active = self.dbstate.db.get_event_from_handle(active_handle)
            if active:
                self.display_attributes(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

class FamilyAttributes(Attributes):
    """
    Displays the attributes of an event.
    """
    def db_changed(self):
        self.connect(self.dbstate.db, 'family-update', self.update)
        self.connect_signal('Family', self.update)

    def update_has_data(self):
        active_handle = self.get_active('Family')
        if active_handle:
            active = self.dbstate.db.get_family_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.model.clear()
        active_handle = self.get_active('Family')
        if active_handle:
            active = self.dbstate.db.get_family_from_handle(active_handle)
            if active:
                self.display_attributes(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

class MediaAttributes(Attributes):
    """
    Displays the attributes of a media object.
    """
    def db_changed(self):
        self.connect(self.dbstate.db, 'media-update', self.update)
        self.connect_signal('Media', self.update)

    def update_has_data(self):
        active_handle = self.get_active('Media')
        if active_handle:
            active = self.dbstate.db.get_media_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.model.clear()
        active_handle = self.get_active('Media')
        if active_handle:
            active = self.dbstate.db.get_media_from_handle(active_handle)
            if active:
                self.display_attributes(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

class SourceAttributes(Attributes):
    """
    Displays the attributes of a source object.
    """
    def db_changed(self):
        self.connect(self.dbstate.db, 'source-update', self.update)
        self.connect_signal('Source', self.update)

    def update_has_data(self):
        active_handle = self.get_active('Source')
        if active_handle:
            active = self.dbstate.db.get_source_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.model.clear()
        active_handle = self.get_active('Source')
        if active_handle:
            active = self.dbstate.db.get_source_from_handle(active_handle)
            if active:
                self.display_attributes(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

class CitationAttributes(Attributes):
    """
    Displays the attributes of a citation object.
    """
    def db_changed(self):
        self.connect(self.dbstate.db, 'citation-update', self.update)
        self.connect_signal('Citation', self.update)

    def update_has_data(self):
        active_handle = self.get_active('Citation')
        if active_handle:
            active = self.dbstate.db.get_citation_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.model.clear()
        active_handle = self.get_active('Citation')
        if active_handle:
            active = self.dbstate.db.get_citation_from_handle(active_handle)
            if active:
                self.display_attributes(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)
