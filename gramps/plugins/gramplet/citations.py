# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
# Copyright (C) 2011 Tim G L Lyons
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
from gramps.gui.editors import EditSource, EditCitation
from gramps.gui.listmodel import ListModel, NOSORT
from gramps.gen.plug import Gramplet
from gramps.gui.dbguielement import DbGUIElement
from gramps.gen.errors import WindowActiveError
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class Citations(Gramplet, DbGUIElement):

    def __init__(self, gui, nav_group=0):
        Gramplet.__init__(self, gui, nav_group)
        DbGUIElement.__init__(self, self.dbstate.db)

    """
    Displays the citations for an object.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def _connect_db_signals(self):
        """
        called on init of DbGUIElement, connect to db as required.
        """
        self.callman.register_callbacks({'citation-update': self.changed,
                                         'person-update': self.changed,
                                         'family-update': self.changed,
                                         'event-update': self.changed,
                                         'media-update': self.changed,
                                         'place-update': self.changed})
        self.callman.connect_all(keys=['citation', 'family', 'person', 'event',
                                       'media', 'place'])

    def changed(self, handle):
        """
        Called when a registered citation is updated.
        """
        self.update()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        tip = _('Double-click on a row to edit the selected source/citation.')
        self.set_tooltip(tip)
        top = Gtk.TreeView()
        titles = [('', NOSORT, 50,),
                  (_('Source/Citation'), 1, 350),
                  (_('Author'), 2, 200),
                  (_('Publisher'), 3, 150)]
        self.model = ListModel(top, titles, list_mode="tree",
                               event_func=self.invoke_editor)
        return top

    def add_citations(self, obj):
        for citation_handle in obj.get_citation_list():
            self.add_citation_ref(citation_handle)

    def add_name_citations(self, obj):
        names = [obj.get_primary_name()] + obj.get_alternate_names()
        for name in names:
            self.add_citations(name)

    def add_attribute_citations(self, obj):
        for attr in obj.get_attribute_list():
            self.add_citations(attr)

    def add_mediaref_citations(self, obj):
        for media_ref in obj.get_media_list():
            self.add_citations(media_ref)
            self.add_attribute_citations(media_ref)
            media = self.dbstate.db.get_media_from_handle(media_ref.ref)
            self.add_media_citations(media)

    def add_media_citations(self, media):
        self.callman.register_handles({'media': [media.handle]})
        self.add_citations(media)
        self.add_attribute_citations(media)

    def add_eventref_citations(self, obj):
        for event_ref in obj.get_event_ref_list():
            self.add_attribute_citations(event_ref)
            event = self.dbstate.db.get_event_from_handle(event_ref.ref)
            self.add_event_citations(event)

    def add_event_citations(self, event):
        self.callman.register_handles({'event': [event.handle]})
        self.add_citations(event)
        self.add_attribute_citations(event)
        self.add_mediaref_citations(event)
        place_handle = event.get_place_handle()
        if place_handle:
            place = self.dbstate.db.get_place_from_handle(place_handle)
            if place:
                self.add_place_citations(place)

    def add_place_citations(self, place):
        self.callman.register_handles({'place': [place.handle]})
        self.add_citations(place)
        self.add_mediaref_citations(place)

    def add_address_citations(self, obj):
        for address in obj.get_address_list():
            self.add_citations(address)

    def add_lds_citations(self, obj):
        for lds in obj.get_lds_ord_list():
            self.add_citations(lds)
            place_handle = lds.get_place_handle()
            if place_handle:
                place = self.dbstate.db.get_place_from_handle(place_handle)
                if place:
                    self.add_place_citations(place)

    def add_association_citations(self, obj):
        for assoc in obj.get_person_ref_list():
            self.add_citations(assoc)

    def add_citation_ref(self, citation_handle):
        """
        Add a citation to the model.
        """
        self.callman.register_handles({'citation': [citation_handle]})
        citation = self.dbstate.db.get_citation_from_handle(citation_handle)
        page = citation.get_page()
        if not page:
            page = _('<No Citation>')
        source_handle = citation.get_reference_handle()
        source = self.dbstate.db.get_source_from_handle(source_handle)
        title = source.get_title()
        author = source.get_author()
        publisher = source.get_publication_info()

        if source_handle not in self.source_nodes:
            node = self.model.add([source_handle, title, author, publisher])
            self.source_nodes[source_handle] = node

        self.model.add([citation_handle, page, '', ''],
                       node=self.source_nodes[source_handle])

    def check_citations(self, obj):
        return True if obj.get_citation_list() else False

    def check_name_citations(self, obj):
        names = [obj.get_primary_name()] + obj.get_alternate_names()
        for name in names:
            if self.check_citations(name):
                return True
        return False

    def check_attribute_citations(self, obj):
        for attr in obj.get_attribute_list():
            if self.check_citations(attr):
                return True
        return False

    def check_mediaref_citations(self, obj):
        for media_ref in obj.get_media_list():
            if self.check_citations(media_ref):
                return True
            if self.check_attribute_citations(media_ref):
                return True
            media = self.dbstate.db.get_media_from_handle(media_ref.ref)
            if self.check_media_citations(media):
                return True
        return False

    def check_media_citations(self, media):
        if self.check_citations(media):
            return True
        if self.check_attribute_citations(media):
            return True
        return False

    def check_eventref_citations(self, obj):
        if obj:
            for event_ref in obj.get_event_ref_list():
                if self.check_attribute_citations(event_ref):
                    return True
                event = self.dbstate.db.get_event_from_handle(event_ref.ref)
                if self.check_event_citations(event):
                    return True
        return False

    def check_event_citations(self, event):
        if self.check_citations(event):
            return True
        if self.check_attribute_citations(event):
            return True
        if self.check_mediaref_citations(event):
            return True
        place_handle = event.get_place_handle()
        if place_handle:
            place = self.dbstate.db.get_place_from_handle(place_handle)
            if place and self.check_place_citations(place):
                return True
        return False

    def check_place_citations(self, place):
        if self.check_citations(place):
            return True
        if self.check_mediaref_citations(place):
            return True
        return False

    def check_address_citations(self, obj):
        for address in obj.get_address_list():
            if self.check_citations(address):
                return True
        return False

    def check_lds_citations(self, obj):
        for lds in obj.get_lds_ord_list():
            if self.check_citations(lds):
                return True
            place_handle = lds.get_place_handle()
            if place_handle:
                place = self.dbstate.db.get_place_from_handle(place_handle)
                if place and self.check_place_citations(place):
                    return True
        return False

    def check_association_citations(self, obj):
        for assoc in obj.get_person_ref_list():
            if self.check_citations(assoc):
                return True
        return False

    def invoke_editor(self, treeview):
        """
        Edit the selected source or citation.
        """
        model, iter_ = treeview.get_selection().get_selected()
        if iter_:
            handle = model.get_value(iter_, 0)
            # bug 9094.
            # str(model.get_path(iter_)) return something like NNN:MMM
            # So if we have only NNN, it's a node
            # removing the str() solves the problem.
            if len(model.get_path(iter_)) == 1:
                self.edit_source(handle)
            else:
                self.edit_citation(handle)

    def edit_source(self, handle):
        """
        Edit the selected source.
        """
        try:
            source = self.dbstate.db.get_source_from_handle(handle)
            EditSource(self.dbstate, self.uistate, [], source)
        except WindowActiveError:
            pass

    def edit_citation(self, handle):
        """
        Edit the selected citation.
        """
        try:
            citation = self.dbstate.db.get_citation_from_handle(handle)
            source_handle = citation.get_reference_handle()
            source = self.dbstate.db.get_source_from_handle(source_handle)
            EditCitation(self.dbstate, self.uistate, [], citation, source)
        except WindowActiveError:
            pass

class PersonCitations(Citations):
    """
    Displays the citations for a person.
    """
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
        self.callman.unregister_all()
        active_handle = self.get_active('Person')
        if active_handle:
            active = self.dbstate.db.get_person_from_handle(active_handle)
            if active:
                self.display_citations(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

    def display_citations(self, person):
        """
        Display the citations for the active person.
        """
        self.source_nodes = {}
        self.callman.register_handles({'person': [person.handle]})
        self.add_citations(person)
        self.add_eventref_citations(person)
        for handle in person.get_family_handle_list():
            family = self.dbstate.db.get_family_from_handle(handle)
            self.add_eventref_citations(family)
        self.add_name_citations(person)
        self.add_attribute_citations(person)
        self.add_address_citations(person)
        self.add_mediaref_citations(person)
        self.add_association_citations(person)
        self.add_lds_citations(person)

        self.set_has_data(self.model.count > 0)
        self.model.tree.expand_all()

    def get_has_data(self, person):
        """
        Return True if the gramplet has data, else return False.
        """
        if person is None:
            return False
        if self.check_citations(person):
            return True
        if self.check_eventref_citations(person):
            return True
        for handle in person.get_family_handle_list():
            family = self.dbstate.db.get_family_from_handle(handle)
            if self.check_eventref_citations(family):
                return True
        if self.check_name_citations(person):
            return True
        if self.check_attribute_citations(person):
            return True
        if self.check_address_citations(person):
            return True
        if self.check_mediaref_citations(person):
            return True
        if self.check_association_citations(person):
            return True
        if self.check_lds_citations(person):
            return True
        return False

class EventCitations(Citations):
    """
    Displays the citations for an event.
    """
    def db_changed(self):
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
        self.callman.unregister_all()
        active_handle = self.get_active('Event')
        if active_handle:
            active = self.dbstate.db.get_event_from_handle(active_handle)
            if active:
                self.display_citations(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

    def display_citations(self, event):
        """
        Display the citations for the active event.
        """
        self.source_nodes = {}
        self.add_event_citations(event)
        self.set_has_data(self.model.count > 0)
        self.model.tree.expand_all()

    def get_has_data(self, event):
        """
        Return True if the gramplet has data, else return False.
        """
        if event is None:
            return False
        if self.check_event_citations(event):
            return True
        return False

class FamilyCitations(Citations):
    """
    Displays the citations for a family.
    """
    def db_changed(self):
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
        self.callman.unregister_all()
        active_handle = self.get_active('Family')
        if active_handle:
            active = self.dbstate.db.get_family_from_handle(active_handle)
            if active:
                self.display_citations(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

    def display_citations(self, family):
        """
        Display the citations for the active family.
        """
        self.source_nodes = {}
        self.callman.register_handles({'family': [family.handle]})
        self.add_citations(family)
        self.add_eventref_citations(family)
        self.add_attribute_citations(family)
        self.add_mediaref_citations(family)
        self.add_lds_citations(family)

        self.set_has_data(self.model.count > 0)
        self.model.tree.expand_all()

    def get_has_data(self, family):
        """
        Return True if the gramplet has data, else return False.
        """
        if family is None:
            return False
        if self.check_citations(family):
            return True
        if self.check_eventref_citations(family):
            return True
        if self.check_attribute_citations(family):
            return True
        if self.check_mediaref_citations(family):
            return True
        if self.check_lds_citations(family):
            return True
        return False

class PlaceCitations(Citations):
    """
    Displays the citations for a place.
    """
    def db_changed(self):
        self.connect_signal('Place', self.update)

    def update_has_data(self):
        active_handle = self.get_active('Place')
        if active_handle:
            active = self.dbstate.db.get_place_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.model.clear()
        self.callman.unregister_all()
        active_handle = self.get_active('Place')
        if active_handle:
            active = self.dbstate.db.get_place_from_handle(active_handle)
            if active:
                self.display_citations(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

    def display_citations(self, place):
        """
        Display the citations for the active place.
        """
        self.source_nodes = {}
        self.add_place_citations(place)
        self.set_has_data(self.model.count > 0)
        self.model.tree.expand_all()

    def get_has_data(self, place):
        """
        Return True if the gramplet has data, else return False.
        """
        if place is None:
            return False
        if self.check_place_citations(place):
            return True
        return False

class MediaCitations(Citations):
    """
    Displays the citations for a media object.
    """
    def db_changed(self):
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
        self.callman.unregister_all()
        active_handle = self.get_active('Media')
        if active_handle:
            active = self.dbstate.db.get_media_from_handle(active_handle)
            if active:
                self.display_citations(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

    def display_citations(self, media):
        """
        Display the citations for the active media object.
        """
        self.source_nodes = {}
        self.add_media_citations(media)
        self.set_has_data(self.model.count > 0)
        self.model.tree.expand_all()

    def get_has_data(self, media):
        """
        Return True if the gramplet has data, else return False.
        """
        if media is None:
            return False
        if self.check_media_citations(media):
            return True
        return False
