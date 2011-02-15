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

from gui.editors import EditSource
from ListModel import ListModel, NOSORT
from gen.plug import Gramplet
from gen.ggettext import gettext as _
import Errors
import gtk

class Sources(Gramplet):
    """
    Displays the sources for an object.
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
        tip = _('Double-click on a row to edit the selected source.')
        self.set_tooltip(tip)
        top = gtk.TreeView()
        titles = [('', NOSORT, 50,),
                  (_('Source'), 1, 200),
                  (_('Reference'), 2, 300),
                  (_('Author'), 3, 100)]
        self.model = ListModel(top, titles, event_func=self.edit_source)
        return top
        
    def display_sources(self, obj):
        """
        Display the sources for the active object.
        """
        for source_ref in obj.get_source_references():
            self.add_source_ref(source_ref)

    def add_source_ref(self, source_ref):
        """
        Add a source reference to the model.
        """
        page = source_ref.get_page()
        source = self.dbstate.db.get_source_from_handle(source_ref.ref)
        title = source.get_title()
        author = source.get_author()
        self.model.add((source_ref.ref, title, page, author))

    def edit_source(self, treeview):
        """
        Edit the selected source.
        """
        model, iter_ = treeview.get_selection().get_selected()
        if iter_:
            handle = model.get_value(iter_, 0)
            try:
                source = self.dbstate.db.get_source_from_handle(handle)
                EditSource(self.dbstate, self.uistate, [], source)
            except Errors.WindowActiveError:
                pass

class PersonSources(Sources):
    """
    Displays the sources for a person.
    """
    def db_changed(self):
        self.dbstate.db.connect('person-update', self.update)
        self.update()

    def active_changed(self, handle):
        self.update()

    def main(self):
        active_handle = self.get_active('Person')
        active = self.dbstate.db.get_person_from_handle(active_handle)
            
        self.model.clear()
        if active:
            self.display_sources(active)

class EventSources(Sources):
    """
    Displays the sources for an event.
    """
    def db_changed(self):
        self.dbstate.db.connect('event-update', self.update)
        self.connect_signal('Event', self.update)
        self.update()

    def main(self):
        active_handle = self.get_active('Event')
        active = self.dbstate.db.get_event_from_handle(active_handle)
            
        self.model.clear()
        if active:
            self.display_sources(active)

class FamilySources(Sources):
    """
    Displays the sources for a family.
    """
    def db_changed(self):
        self.dbstate.db.connect('family-update', self.update)
        self.connect_signal('Family', self.update)
        self.update()

    def main(self):
        active_handle = self.get_active('Family')
        active = self.dbstate.db.get_family_from_handle(active_handle)
            
        self.model.clear()
        if active:
            self.display_sources(active)

class PlaceSources(Sources):
    """
    Displays the sources for a place.
    """
    def db_changed(self):
        self.dbstate.db.connect('place-update', self.update)
        self.connect_signal('Place', self.update)
        self.update()

    def main(self):
        active_handle = self.get_active('Place')
        active = self.dbstate.db.get_place_from_handle(active_handle)
            
        self.model.clear()
        if active:
            self.display_sources(active)

class MediaSources(Sources):
    """
    Displays the sources for a media object.
    """
    def db_changed(self):
        self.dbstate.db.connect('media-update', self.update)
        self.connect_signal('Media', self.update)
        self.update()

    def main(self):
        active_handle = self.get_active('Media')
        active = self.dbstate.db.get_object_from_handle(active_handle)
            
        self.model.clear()
        if active:
            self.display_sources(active)

