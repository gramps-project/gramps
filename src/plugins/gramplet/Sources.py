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
        
    def add_sources(self, obj):
        for source_ref in obj.get_source_references():
            self.add_source_ref(source_ref)
        
    def add_name_sources(self, obj):
        names = [obj.get_primary_name()] + obj.get_alternate_names()
        for name in names:
            self.add_sources(name)

    def add_attribute_sources(self, obj):
        for attr in obj.get_attribute_list():
            self.add_sources(attr)

    def add_mediaref_sources(self, obj):
        for media_ref in obj.get_media_list():
            self.add_sources(media_ref)
            self.add_attribute_sources(media_ref)
            media = self.dbstate.db.get_object_from_handle(media_ref.ref)
            self.add_media_sources(media)

    def add_media_sources(self, media):
        self.add_sources(media)
        self.add_attribute_sources(media)

    def add_eventref_sources(self, obj):
        for event_ref in obj.get_event_ref_list():
            self.add_attribute_sources(event_ref)
            event = self.dbstate.db.get_event_from_handle(event_ref.ref)
            self.add_event_sources(event)

    def add_event_sources(self, event):
        self.add_sources(event)
        self.add_attribute_sources(event)
        self.add_mediaref_sources(event)
        place_handle = event.get_place_handle()
        place = self.dbstate.db.get_place_from_handle(place_handle)
        if place:
            self.add_place_sources(place)

    def add_place_sources(self, place):
        self.add_sources(place)
        self.add_mediaref_sources(place)

    def add_address_sources(self, obj):
        for address in obj.get_address_list():
            self.add_sources(address)

    def add_lds_sources(self, obj):
        for lds in obj.get_lds_ord_list():
            self.add_sources(lds)
            place_handle = lds.get_place_handle()
            place = self.dbstate.db.get_place_from_handle(place_handle)
            if place:
                self.add_place_sources(place)

    def add_association_sources(self, obj):
        for assoc in obj.get_person_ref_list():
            self.add_sources(assoc)

    def add_source_ref(self, source_ref):
        """
        Add a source reference to the model.
        """
        page = source_ref.get_page()
        source = self.dbstate.db.get_source_from_handle(source_ref.ref)
        title = source.get_title()
        author = source.get_author()
        self.model.add((source_ref.ref, title, page, author))

    def check_sources(self, obj):
        return True if obj.get_source_references() else False
        
    def check_name_sources(self, obj):
        names = [obj.get_primary_name()] + obj.get_alternate_names()
        for name in names:
            if self.check_sources(name):
                return True
        return False

    def check_attribute_sources(self, obj):
        for attr in obj.get_attribute_list():
            if self.check_sources(attr):
                return True
        return False

    def check_mediaref_sources(self, obj):
        for media_ref in obj.get_media_list():
            if self.check_sources(media_ref):
                return True
            if self.check_attribute_sources(media_ref):
                return True
            media = self.dbstate.db.get_object_from_handle(media_ref.ref)
            if self.check_media_sources(media):
                return True
        return False

    def check_media_sources(self, media):
        if self.check_sources(media):
            return True
        if self.check_attribute_sources(media):
            return True
        return False

    def check_eventref_sources(self, obj):
        for event_ref in obj.get_event_ref_list():
            if self.check_attribute_sources(event_ref):
                return True
            event = self.dbstate.db.get_event_from_handle(event_ref.ref)
            if self.check_event_sources(event):
                return True
        return False

    def check_event_sources(self, event):
        if self.check_sources(event):
            return True
        if self.check_attribute_sources(event):
            return True
        if self.check_mediaref_sources(event):
            return True
        place_handle = event.get_place_handle()
        place = self.dbstate.db.get_place_from_handle(place_handle)
        if place and self.check_place_sources(place):
            return True
        return False

    def check_place_sources(self, place):
        if self.check_sources(place):
            return True
        if self.check_mediaref_sources(place):
            return True
        return False

    def check_address_sources(self, obj):
        for address in obj.get_address_list():
            if self.check_sources(address):
                return True
        return False

    def check_lds_sources(self, obj):
        for lds in obj.get_lds_ord_list():
            if self.check_sources(lds):
                return True
            place_handle = lds.get_place_handle()
            place = self.dbstate.db.get_place_from_handle(place_handle)
            if place and self.check_place_sources(place):
                return True
        return False

    def check_association_sources(self, obj):
        for assoc in obj.get_person_ref_list():
            if self.check_sources(assoc):
                return True
        return False

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

    def update_has_data(self):
        active_handle = self.get_active('Person')
        active = self.dbstate.db.get_person_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))
    
    def main(self):
        active_handle = self.get_active('Person')
        active = self.dbstate.db.get_person_from_handle(active_handle)
            
        self.model.clear()
        if active:
            self.display_sources(active)
        else:
            self.set_has_data(False)

    def display_sources(self, person):
        """
        Display the sources for the active person.
        """
        self.add_sources(person)
        self.add_eventref_sources(person)
        for handle in person.get_family_handle_list():
            family = self.dbstate.db.get_family_from_handle(handle)
            self.add_eventref_sources(family)
        self.add_name_sources(person)
        self.add_attribute_sources(person)
        self.add_address_sources(person)
        self.add_mediaref_sources(person)
        self.add_association_sources(person)
        self.add_lds_sources(person)

        self.set_has_data(self.model.count > 0)

    def get_has_data(self, person):
        """
        Return True if the gramplet has data, else return False.
        """
        if person is None:
            return False
        if self.check_sources(person):
            return True
        if self.check_eventref_sources(person):
            return True
        for handle in person.get_family_handle_list():
            family = self.dbstate.db.get_family_from_handle(handle)
            if self.check_eventref_sources(family):
                return True
        if self.check_name_sources(person):
            return True
        if self.check_attribute_sources(person):
            return True
        if self.check_address_sources(person):
            return True
        if self.check_mediaref_sources(person):
            return True
        if self.check_association_sources(person):
            return True
        if self.check_lds_sources(person):
            return True
        return False

class EventSources(Sources):
    """
    Displays the sources for an event.
    """
    def db_changed(self):
        self.dbstate.db.connect('event-update', self.update)
        self.connect_signal('Event', self.update)
        self.update()

    def update_has_data(self):
        active_handle = self.get_active('Event')
        active = self.dbstate.db.get_event_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))
    
    def main(self):
        active_handle = self.get_active('Event')
        active = self.dbstate.db.get_event_from_handle(active_handle)
            
        self.model.clear()
        if active:
            self.display_sources(active)
        else:
            self.set_has_data(False)

    def display_sources(self, event):
        """
        Display the sources for the active event.
        """
        self.add_event_sources(event)
        self.set_has_data(self.model.count > 0)

    def get_has_data(self, event):
        """
        Return True if the gramplet has data, else return False.
        """
        if event is None:
            return False
        if self.check_event_sources(event):
            return True
        return False

class FamilySources(Sources):
    """
    Displays the sources for a family.
    """
    def db_changed(self):
        self.dbstate.db.connect('family-update', self.update)
        self.connect_signal('Family', self.update)
        self.update()

    def update_has_data(self):
        active_handle = self.get_active('Family')
        active = self.dbstate.db.get_family_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))
    
    def main(self):
        active_handle = self.get_active('Family')
        active = self.dbstate.db.get_family_from_handle(active_handle)
            
        self.model.clear()
        if active:
            self.display_sources(active)
        else:
            self.set_has_data(False)

    def display_sources(self, family):
        """
        Display the sources for the active family.
        """
        self.add_sources(family)
        self.add_eventref_sources(family)
        self.add_attribute_sources(family)
        self.add_mediaref_sources(family)
        self.add_lds_sources(family)

        self.set_has_data(self.model.count > 0)

    def get_has_data(self, family):
        """
        Return True if the gramplet has data, else return False.
        """
        if family is None:
            return False
        if self.check_sources(family):
            return True
        if self.check_eventref_sources(family):
            return True
        if self.check_attribute_sources(family):
            return True
        if self.check_mediaref_sources(family):
            return True
        if self.check_lds_sources(family):
            return True
        return False

class PlaceSources(Sources):
    """
    Displays the sources for a place.
    """
    def db_changed(self):
        self.dbstate.db.connect('place-update', self.update)
        self.connect_signal('Place', self.update)
        self.update()

    def update_has_data(self):
        active_handle = self.get_active('Place')
        active = self.dbstate.db.get_place_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))
    
    def main(self):
        active_handle = self.get_active('Place')
        active = self.dbstate.db.get_place_from_handle(active_handle)
            
        self.model.clear()
        if active:
            self.display_sources(active)
        else:
            self.set_has_data(False)

    def display_sources(self, place):
        """
        Display the sources for the active place.
        """
        self.add_place_sources(place)
        self.set_has_data(self.model.count > 0)

    def get_has_data(self, place):
        """
        Return True if the gramplet has data, else return False.
        """
        if place is None:
            return False
        if self.check_place_sources(place):
            return True
        return False

class MediaSources(Sources):
    """
    Displays the sources for a media object.
    """
    def db_changed(self):
        self.dbstate.db.connect('media-update', self.update)
        self.connect_signal('Media', self.update)
        self.update()

    def update_has_data(self):
        active_handle = self.get_active('Media')
        active = self.dbstate.db.get_object_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))
    
    def main(self):
        active_handle = self.get_active('Media')
        active = self.dbstate.db.get_object_from_handle(active_handle)
            
        self.model.clear()
        if active:
            self.display_sources(active)
        else:
            self.set_has_data(False)

    def display_sources(self, media):
        """
        Display the sources for the active media object.
        """
        self.add_media_sources(media)
        self.set_has_data(self.model.count > 0)

    def get_has_data(self, media):
        """
        Return True if the gramplet has data, else return False.
        """
        if media is None:
            return False
        if self.check_media_sources(media):
            return True
        return False
