#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008       Gary Burton
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

"""
Proxy class for the GRAMPS databases. Returns objects which are referenced
by at least one other object.
"""

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
from proxybase import ProxyDbBase

class ReferencedProxyDb(ProxyDbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but returning all objects which are referenced by at least one other object.
    """

    def __init__(self, dbase):
        """
        Create a new ReferencedProxyDb instance. 
        """
        ProxyDbBase.__init__(self, dbase)
        self.unreferenced_events = []
        self.unreferenced_places = []
        self.unreferenced_sources = []
        self.unreferenced_repositories = []
        self.unreferenced_media_objects = []
        self.unreferenced_notes = []

        # Build lists of unreferenced objects
        self.__find_unreferenced_objects()

    def get_person_from_handle(self, handle):
        """
        Finds a Person in the database from the passed gramps' ID.
        If no such Person exists, None is returned.
        """
        return self.db.get_person_from_handle(handle)

    def get_source_from_handle(self, handle):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        return self.db.get_source_from_handle(handle)

    def get_object_from_handle(self, handle):
        """
        Finds an Object in the database from the passed gramps' ID.
        If no such Object exists, None is returned.
        """
        return self.db.get_object_from_handle(handle)

    def get_place_from_handle(self, handle):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        return self.db.get_place_from_handle(handle)

    def get_event_from_handle(self, handle):
        """
        Finds a Event in the database from the passed gramps' ID.
        If no such Event exists, None is returned.
        """
        return self.db.get_event_from_handle(handle)

    def get_family_from_handle(self, handle):
        """
        Finds a Family in the database from the passed gramps' ID.
        If no such Family exists, None is returned.
        """
        return self.db.get_family_from_handle(handle)

    def get_repository_from_handle(self, handle):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        return self.db.get_repository_from_handle(handle)

    def get_note_from_handle(self, handle):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        return self.db.get_note_from_handle(handle)

    def get_person_from_gramps_id(self, val):
        """
        Finds a Person in the database from the passed GRAMPS ID.
        If no such Person exists, None is returned.
        """
        return self.db.get_person_from_gramps_id(val)

    def get_family_from_gramps_id(self, val):
        """
        Finds a Family in the database from the passed GRAMPS ID.
        If no such Family exists, None is returned.
        """
        return self.db.get_family_from_gramps_id(val)

    def get_event_from_gramps_id(self, val):
        """
        Finds an Event in the database from the passed GRAMPS ID.
        If no such Event exists, None is returned.
        """
        return self.db.get_event_from_gramps_id(val)

    def get_place_from_gramps_id(self, val):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        return self.db.get_place_from_gramps_id(val)

    def get_source_from_gramps_id(self, val):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        return self.db.get_source_from_gramps_id(val)

    def get_object_from_gramps_id(self, val):
        """
        Finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, None is returned.
        """
        return self.db.get_object_from_gramps_id(val)

    def get_repository_from_gramps_id(self, val):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        return self.db.get_repository_from_gramps_id(val)

    def get_note_from_gramps_id(self, val):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        return self.db.get_note_from_gramps_id(val)

    def get_person_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Person in
        the database. If sort_handles is True, the list is sorted by surnames
        """
        return self.db.get_person_handles(sort_handles)

    def iter_person_handles(self):
        """
        Return an iterator over database handles, one handle for each Person in
        the database. If sort_handles is True, the list is sorted by surnames
        """
        return self.db.iter_person_handles()

    def get_place_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Place still
        referenced in the database. If sort_handles is True, the list is
        sorted by Place title.
        """
        return list(set(self.db.get_place_handles(sort_handles)) -
                    set(self.unreferenced_places))

    def get_source_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Source still
        referenced in the database. If sort_handles is True, the list is
        sorted by Source title.
        """
        return list(set(self.db.get_source_handles(sort_handles)) -
                    set(self.unreferenced_sources))

    def get_media_object_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each MediaObject
        still referenced in the database. If sort_handles is True, the list
        is sorted by title.
        """
        return list(set(self.db.get_media_object_handles(sort_handles)) -
                    set(self.unreferenced_media_objects))

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event
        still referenced in the database.
        """
        return list(set(self.db.get_event_handles()) -
                    set(self.unreferenced_events))

    def get_family_handles(self):
        """
        Return a list of database handles, one handle for each Family in
        the database.
        """
        return self.db.get_family_handles()

    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository still
        referenced in the database.
        """
        return list(set(self.db.get_repository_handles()) -
                    set(self.unreferenced_repositories))

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note still
        referenced in the database.
        """
        return list(set(self.db.get_note_handles()) -
                    set(self.unreferenced_notes))

    def get_researcher(self):
        """returns the Researcher instance, providing information about
        the owner of the database"""
        return self.db.get_researcher()

    def get_default_person(self):
        """returns the default Person of the database"""
        return self.db.get_default_person()

    def get_default_handle(self):
        """returns the default Person of the database"""
        return self.db.get_default_handle()
    
    def has_person_handle(self, handle):
        """
        returns True if the handle exists in the current Person database.
        """
        return handle in self.get_person_handles()

    def has_event_handle(self, handle):
        """
        returns True if the handle exists in the current Event database.
        """
        return handle in self.get_event_handles()

    def has_source_handle(self, handle):
        """
        returns True if the handle exists in the current Source database.
        """
        return handle in self.get_source_handles()

    def has_place_handle(self, handle):
        """
        returns True if the handle exists in the current Place database.
        """
        return handle in self.get_place_handles()

    def has_family_handle(self, handle):            
        """
        returns True if the handle exists in the current Family database.
        """
        return handle in self.get_family_handles()

    def has_object_handle(self, handle):
        """
        returns True if the handle exists in the current MediaObjectdatabase.
        """
        return handle in self.get_media_object_handles()

    def has_repository_handle(self, handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return handle in self.get_repository_handles()

    def has_note_handle(self, handle):
        """
        returns True if the handle exists in the current Note database.
        """
        return handle in self.get_note_handles()

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        Returns an interator over alist of (class_name, handle) tuples.

        @param handle: handle of the object to search for.
        @type handle: database handle
        @param include_classes: list of class names to include in the results.
                                Default: None means include all classes.
        @type include_classes: list of class names
        
        This default implementation does a sequencial scan through all
        the primary object databases and is very slow. Backends can
        override this method to provide much faster implementations that
        make use of additional capabilities of the backend.

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use:

        >    result_list = list(find_backlink_handles(handle))
        """
        handle_itr = self.db.find_backlink_handles(handle, include_classes)
        for (class_name, handle) in handle_itr:
            if class_name == 'Person':
                if not self.get_person_from_handle(handle):
                    continue
            elif class_name == 'Family':
                if not self.get_family_from_handle(handle):
                    continue
            elif class_name == 'Event':
                if handle in self.unreferenced_events:
                    continue
            elif class_name == 'Place':
                if handle in self.unreferenced_places:
                    continue
            elif class_name == 'Source':
                if handle in self.unreferenced_sources:
                    continue
            elif class_name == 'Repository':
                if handle in self.unreferenced_repositories:
                    continue
            elif class_name == 'MediaObject':
                if handle in self.unreferenced_media_objects:
                    continue
            elif class_name == 'Note':
                if handle in self.unreferenced_notes:
                    continue
            yield (class_name, handle)
        return

    def __find_unreferenced_objects(self):
        """
        Builds lists of all objects that are not referenced by another object.
        These may be objects that are really unreferenced or because they
        are referenced by something or someone that has already been filtered
        by one of the other proxy decorators.
        By adding an object to a list, other referenced objects could
        effectively become unreferenced, so the action is performed in a loop
        until there are no more objects to unreference.
        """
        object_types = {
            'Event': {'unref_list': self.unreferenced_events,
                      'handle_list': self.get_event_handles},
            'Place': {'unref_list': self.unreferenced_places,
                      'handle_list': self.get_place_handles},
            'Source': {'unref_list': self.unreferenced_sources,
                       'handle_list': self.get_source_handles},
            'Repositories': {'unref_list': self.unreferenced_repositories,
                             'handle_list': self.get_repository_handles},
            'MediaObjects': {'unref_list': self.unreferenced_media_objects,
                             'handle_list': self.get_media_object_handles},
            'Notes': {'unref_list': self.unreferenced_notes,
                      'handle_list': self.get_note_handles}
            }

        last_count = 0
        while True:
            current_count = 0
            for object_type, object_dict in object_types.iteritems():
                unref_list = object_dict['unref_list']
                handle_list = object_dict['handle_list']()
                for handle in handle_list:
                    if not any(self.find_backlink_handles(handle)):
                        unref_list.append(handle)
                current_count += len(unref_list)

            if current_count == last_count:
                break
            last_count = current_count
