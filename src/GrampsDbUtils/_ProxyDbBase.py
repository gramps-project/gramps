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

# $Id: _PrivateProxyDb.py 8864 2007-08-25 05:03:23Z dallingham $

"""
Proxy class for the GRAMPS databases. Filter out all data marked private.
"""

__author__ = "Brian Matherly"
__revision__ = "$Revision: 8864 $"

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
from RelLib import *
from GrampsDb import DbBase

class ProxyDbBase(DbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all data marked private will be hidden from the user.
    """

    def __init__(self,db):
        """
        Creates a new PrivateProxyDb instance. 
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
        Returns 1 if the database has been opened.
        """
        return self.db.is_open

    def get_name_group_mapping(self, name):
        """
        Returns the default grouping name for a surname
        """
        return self.db.get_name_group_mapping(name)

    def get_name_group_keys(self):
        """
        Returns the defined names that have been assigned to a default grouping
        """
        return self.db.get_name_group_keys()

    def get_number_of_people(self):
        """
        Returns the number of people currently in the databse.
        """
        return len(self.get_person_handles())

    def get_number_of_families(self):
        """
        Returns the number of families currently in the databse.
        """
        return len(self.get_family_handles())

    def get_number_of_events(self):
        """
        Returns the number of events currently in the databse.
        """
        return len(self.get_event_handles())

    def get_number_of_places(self):
        """
        Returns the number of places currently in the databse.
        """
        return len(self.get_place_handles())

    def get_number_of_sources(self):
        """
        Returns the number of sources currently in the databse.
        """
        return len(self.get_source_handles())

    def get_number_of_media_objects(self):
        """
        Returns the number of media objects currently in the databse.
        """
        return len(self.get_media_object_handles())

    def get_number_of_repositories(self):
        """
        Returns the number of source repositories currently in the databse.
        """
        return len(self.get_repository_handles())

    def get_number_of_notes(self):
        """
        Returns the number of notes currently in the databse.
        """
        return self.db.get_number_of_notes()

    def get_save_path(self):
        """returns the save path of the file, or "" if one does not exist"""
        return self.db.get_save_path()

    def get_person_event_types(self):
        """returns a list of all Event types assocated with Person
        instances in the database"""
        return self.db.get_person_event_types()

    def get_person_attribute_types(self):
        """returns a list of all Attribute types assocated with Person
        instances in the database"""
        return self.db.get_person_attribute_types()

    def get_family_attribute_types(self):
        """returns a list of all Attribute types assocated with Family
        instances in the database"""
        return self.db.get_family_attribute_types()

    def get_family_event_types(self):
        """returns a list of all Event types assocated with Family
        instances in the database"""
        return self.db.get_family_event_types()

    def get_marker_types(self):
        """return a list of all marker types available in the database"""
        return self.db.get_marker_types()
        
    def get_media_attribute_types(self):
        """returns a list of all Attribute types assocated with Media
        and MediaRef instances in the database"""
        return self.db.get_media_attribute_types()

    def get_family_relation_types(self):
        """returns a list of all relationship types assocated with Family
        instances in the database"""
        return self.db.get_family_relation_types()

    def get_child_reference_types(self):
        """returns a list of all child reference types assocated with Family
        instances in the database"""
        return self.db.get_child_reference_types()

    def get_event_roles(self):
        """returns a list of all custom event role names assocated with Event
        instances in the database"""
        return self.db.get_event_roles()

    def get_name_types(self):
        """returns a list of all custom names types assocated with Person
        instances in the database"""
        return self.db.get_name_types()

    def get_repository_types(self):
        """returns a list of all custom repository types assocated with
        Repository instances in the database"""
        return self.db.get_repository_types()

    def get_note_types(self):
        """returns a list of all custom note types assocated with
        Note instances in the database"""
        return self.db.get_note_types()

    def get_source_media_types(self):
        """returns a list of all custom source media types assocated with
        Source instances in the database"""
        return self.db.get_source_media_types()

    def get_url_types(self):
        """returns a list of all custom names types assocated with Url
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
        Returns the Person display common information stored in the
        database's metadata.
        """
        raise NotImplementedError
        
    def get_family_list_column_order(self):
        """
        Returns the Person display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_child_column_order(self):
        """
        Returns the Person display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_place_column_order(self):
        """
        Returns the Place display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_source_column_order(self):
        """
        Returns the Source display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_media_column_order(self):
        """
        Returns the MediaObject display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_event_column_order(self):
        """
        Returns the Event display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_repository_column_order(self):
        """
        Returns the Repository display common information stored in the
        database's metadata.
        """
        raise NotImplementedError

    def get_note_column_order(self):
        """
        Returns the Note display common information stored in the
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

        >    result_list = [i for i in find_backlink_handles(handle)]
        """
        raise NotImplementedError

    def get_gramps_ids(self, obj_key):
        return self.db.get_gramps_ids(obj_key)

    def has_gramps_id(self, obj_key, gramps_id):
        return self.db.has_gramps_ids(obj_key, gramps_id)
