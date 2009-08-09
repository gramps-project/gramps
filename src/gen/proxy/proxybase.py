#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
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
Proxy class for the GRAMPS databases. Filter out all data marked private.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from itertools import ifilter

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
from dbbase import DbBase

class ProxyDbBase(DbBase):
    """
    ProxyDbBase is a base class for building a proxy to a Gramps database. 
    This class attempts to implement functions that are likely to be common 
    among proxy classes. Functions that are not likely to be common raise a 
    NotImplementedError to remind the developer to implement those functions.

    Real database proxy classes can inherit from this class to make sure the
    database interface is properly implemented.
    """

    def __init__(self, db):
        """
        Create a new PrivateProxyDb instance. 
        """
        self.db = db
        self.name_formats = db.name_formats
        self.bookmarks = db.bookmarks
        self.family_bookmarks = db.family_bookmarks
        self.event_bookmarks = db.event_bookmarks
        self.place_bookmarks = db.place_bookmarks
        self.source_bookmarks = db.source_bookmarks
        self.repo_bookmarks = db.repo_bookmarks
        self.media_bookmarks = db.media_bookmarks
        self.note_bookmarks = db.note_bookmarks

    def is_open(self):
        """
        Return 1 if the database has been opened.
        """
        return self.db.is_open
        
    def get_researcher(self):
        """returns the Researcher instance, providing information about
        the owner of the database"""
        return self.db.get_researcher()        
        
    def predicate(self, handle):
        """
        Default predicate. Returns True
        """
        return True    
        
    # Define default predicates for each object type
    
    person_predicate = \
    family_predicate = \
    event_predicate = \
    source_predicate = \
    place_predicate = \
    object_predicate = \
    repository_predicate = \
    note_predicate = \
        None
        
    def get_person_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Person in
        the database. 
        """
        if self.db.is_open:
            return list(self.iter_person_handles())
        else:
            return []
        
    def get_family_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Family in
        the database. 
        """
        if self.db.is_open:
            return list(self.iter_family_handles())
        else:
            return []
        
    def get_event_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Event in
        the database. 
        """
        if self.db.is_open:
            return list(self.iter_event_handles())
        else:
            return []

    def get_source_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Source in
        the database. 
        """
        if self.db.is_open:
            return list(self.iter_source_handles())
        else:
            return []
        
    def get_place_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Place in
        the database. 
        """
        if self.db.is_open:
            return list(self.iter_place_handles())
        else:
            return []
        
    def get_media_object_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each MediaObject in
        the database. 
        """
        if self.db.is_open:
            return list(self.iter_media_object_handles())
        else:
            return []

    def get_repository_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Repository in
        the database. 
        """
        if self.db.is_open:
            return list(self.iter_repository_handles())
        else:
            return []
        
    def get_note_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Note in
        the database. 
        """
        if self.db.is_open:
            return list(self.iter_note_handles())
        else:
            return []
            
    def iter_person_handles(self):
        """
        Return an iterator over database handles, one handle for each Person in
        the database.
        """
        return ifilter(self.person_predicate, self.db.iter_person_handles())

    def iter_family_handles(self):
        """
        Return an iterator over database handles, one handle for each Family in
        the database.
        """
        return ifilter(self.family_predicate, self.db.iter_family_handles())

    def iter_event_handles(self):
        """
        Return an iterator over database handles, one handle for each Event in
        the database.
        """
        return ifilter(self.event_predicate, self.db.iter_event_handles())

    def iter_source_handles(self):
        """
        Return an iterator over database handles, one handle for each Source in
        the database.
        """
        return ifilter(self.source_predicate, self.db.iter_source_handles())       

    def iter_place_handles(self):
        """
        Return an iterator over database handles, one handle for each Place in
        the database.
        """
        return ifilter(self.place_predicate, self.db.iter_place_handles())
     
    def iter_media_object_handles(self):
        """
        Return an iterator over database handles, one handle for each Media
        Object in the database.
        """
        return ifilter(self.object_predicate, self.db.iter_media_object_handles())

    def iter_repository_handles(self):
        """
        Return an iterator over database handles, one handle for each 
        Repository in the database.
        """
        return ifilter(self.repository_predicate, self.db.iter_repository_handles())

    def iter_note_handles(self):
        """
        Return an iterator over database handles, one handle for each Note in
        the database.
        """
        return ifilter(self.note_predicate, self.db.iter_note_handles())

    def get_name_group_mapping(self, name):
        """
        Return the default grouping name for a surname
        """
        return self.db.get_name_group_mapping(name)

    def has_name_group_key(self, name):
        """
        Return if a key exists in the name_group table
        """
        return self.db.has_name_group_key(name)

    def get_name_group_keys(self):
        """
        Return the defined names that have been assigned to a default grouping
        """
        return self.db.get_name_group_keys()

    def get_number_of_people(self):
        """
        Return the number of people currently in the database.
        """
        return self.db.get_number_of_people()

    def get_number_of_families(self):
        """
        Return the number of families currently in the database.
        """
        return self.db.get_number_of_families()

    def get_number_of_events(self):
        """
        Return the number of events currently in the database.
        """
        return self.db.get_number_of_events()

    def get_number_of_places(self):
        """
        Return the number of places currently in the database.
        """
        return self.db.get_number_of_places()

    def get_number_of_sources(self):
        """
        Return the number of sources currently in the database.
        """
        return self.db.get_number_of_sources()

    def get_number_of_media_objects(self):
        """
        Return the number of media objects currently in the database.
        """
        return self.db.get_number_of_media_objects()

    def get_number_of_repositories(self):
        """
        Return the number of source repositories currently in the database.
        """
        return self.db.get_number_of_repositories()

    def get_number_of_notes(self):
        """
        Return the number of notes currently in the database.
        """
        return self.db.get_number_of_notes()

    def get_save_path(self):
        """returns the save path of the file, or "" if one does not exist"""
        return self.db.get_save_path()

    def get_person_event_types(self):
        """returns a list of all Event types associated with Person
        instances in the database"""
        return self.db.get_person_event_types()

    def get_person_attribute_types(self):
        """returns a list of all Attribute types associated with Person
        instances in the database"""
        return self.db.get_person_attribute_types()

    def get_family_attribute_types(self):
        """returns a list of all Attribute types associated with Family
        instances in the database"""
        return self.db.get_family_attribute_types()

    def get_family_event_types(self):
        """returns a list of all Event types associated with Family
        instances in the database"""
        return self.db.get_family_event_types()

    def get_marker_types(self):
        """return a list of all marker types available in the database"""
        return self.db.get_marker_types()
        
    def get_media_attribute_types(self):
        """returns a list of all Attribute types associated with Media
        and MediaRef instances in the database"""
        return self.db.get_media_attribute_types()

    def get_family_relation_types(self):
        """returns a list of all relationship types associated with Family
        instances in the database"""
        return self.db.get_family_relation_types()

    def get_child_reference_types(self):
        """returns a list of all child reference types associated with Family
        instances in the database"""
        return self.db.get_child_reference_types()

    def get_event_roles(self):
        """returns a list of all custom event role names associated with Event
        instances in the database"""
        return self.db.get_event_roles()

    def get_name_types(self):
        """returns a list of all custom names types associated with Person
        instances in the database"""
        return self.db.get_name_types()

    def get_repository_types(self):
        """returns a list of all custom repository types associated with
        Repository instances in the database"""
        return self.db.get_repository_types()

    def get_note_types(self):
        """returns a list of all custom note types associated with
        Note instances in the database"""
        return self.db.get_note_types()

    def get_source_media_types(self):
        """returns a list of all custom source media types associated with
        Source instances in the database"""
        return self.db.get_source_media_types()

    def get_url_types(self):
        """returns a list of all custom names types associated with Url
        instances in the database"""
        return self.db.get_url_types()

    def get_raw_person_data(self, handle):
        return self.db.get_raw_person_data(handle)

    def get_raw_family_data(self, handle):
        return self.db.get_raw_family_data(handle)

    def get_raw_object_data(self, handle):
        return self.db.get_raw_object_data(handle)

    def get_raw_place_data(self, handle):
        return self.db.get_raw_place_data(handle)

    def get_raw_event_data(self, handle):
        return self.db.get_raw_event_data(handle)

    def get_raw_source_data(self, handle):
        return self.db.get_raw_source_data(handle)

    def get_raw_repository_data(self, handle):
        return self.db.get_raw_repository_data(handle)

    def get_raw_note_data(self, handle):
        return self.db.get_raw_note_data(handle)

    def has_person_handle(self, handle):
        """
        returns True if the handle exists in the current Person database.
        """
        raise NotImplementedError

    def has_event_handle(self, handle):
        """
        returns True if the handle exists in the current Event database.
        """
        raise NotImplementedError

    def has_source_handle(self, handle):
        """
        returns True if the handle exists in the current Source database.
        """
        raise NotImplementedError

    def has_place_handle(self, handle):
        """
        returns True if the handle exists in the current Place database.
        """
        raise NotImplementedError

    def has_family_handle(self, handle):            
        """
        returns True if the handle exists in the current Family database.
        """
        raise NotImplementedError

    def has_object_handle(self, handle):
        """
        returns True if the handle exists in the current MediaObjectdatabase.
        """
        raise NotImplementedError

    def has_repository_handle(self, handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        raise NotImplementedError

    def has_note_handle(self, handle):
        """
        returns True if the handle exists in the current Note database.
        """
        raise NotImplementedError

    def get_mediapath(self):
        """returns the default media path of the database"""
        return self.db.get_mediapath()

    def set_column_order(self, col_list, name):
        raise NotImplementedError

    def set_person_column_order(self, col_list):
        """
        Stores the Person display common information in the
        database's metadata.
        """
        raise NotImplementedError

    def set_family_list_column_order(self, col_list):
        """
        Stores the Person display common information in the
        database's metadata.
        """
        raise NotImplementedError

    def set_child_column_order(self, col_list):
        """
        Stores the Person display common information in the
        database's metadata.
        """
        raise NotImplementedError

    def set_place_column_order(self, col_list):
        """
        Stores the Place display common information in the
        database's metadata.
        """
        raise NotImplementedError

    def set_source_column_order(self, col_list):
        """
        Stores the Source display common information in the
        database's metadata.
        """
        raise NotImplementedError

    def set_media_column_order(self, col_list):
        """
        Stores the Media display common information in the
        database's metadata.
        """
        raise NotImplementedError

    def set_event_column_order(self, col_list):
        """
        Stores the Event display common information in the
        database's metadata.
        """
        raise NotImplementedError

    def set_repository_column_order(self, col_list):
        """
        Stores the Repository display common information in the
        database's metadata.
        """
        raise NotImplementedError

    def set_note_column_order(self, col_list):
        """
        Stores the Note display common information in the
        database's metadata.
        """
        raise NotImplementedError

    def get_person_column_order(self):
        """
        Return the Person display common information stored in the
        database's metadata.
        """
        raise NotImplementedError
        
    def get_family_list_column_order(self):
        """
        Return the Person display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_child_column_order(self):
        """
        Return the Person display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_place_column_order(self):
        """
        Return the Place display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_source_column_order(self):
        """
        Return the Source display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_media_column_order(self):
        """
        Return the MediaObject display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_event_column_order(self):
        """
        Return the Event display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_repository_column_order(self):
        """
        Return the Repository display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_note_column_order(self):
        """
        Return the Note display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def delete_primary_from_reference_map(self, handle, transaction):
        """Called each time an object is removed from the database. This can
        be used by subclasses to update any additional index tables that might
        need to be changed."""
        raise NotImplementedError

    def update_reference_map(self, obj, transaction):
        """Called each time an object is writen to the database. This can
        be used by subclasses to update any additional index tables that might
        need to be changed."""
        raise NotImplementedError

    def reindex_reference_map(self, callback):
        """
        Reindex all primary records in the database.

        """
        raise NotImplementedError

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
        raise NotImplementedError

    def get_gramps_ids(self, obj_key):
        return self.db.get_gramps_ids(obj_key)

    def has_gramps_id(self, obj_key, gramps_id):
        return self.db.has_gramps_ids(obj_key, gramps_id)

    def get_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        return self.bookmarks

    def get_family_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        return self.family_bookmarks

    def get_event_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        return self.event_bookmarks

    def get_place_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        return self.place_bookmarks

    def get_source_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        return self.source_bookmarks

    def get_media_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        return self.media_bookmarks

    def get_repo_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        return self.repo_bookmarks

    def get_note_bookmarks(self):
        """returns the list of Note handles in the bookmarks"""
        return self.note_bookmarks
