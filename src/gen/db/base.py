#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Base class for the GRAMPS databases. All database interfaces should inherit
from this class.
"""
from __future__ import with_statement
#-------------------------------------------------------------------------
#
# libraries
#
#-------------------------------------------------------------------------
import cPickle
import time
import random
import locale
import os
from sys import maxint
from bsddb import db
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
from gen.lib import (MediaObject, Person, Family, Source, Event, Place, 
                     Repository, Note, GenderStats, Researcher)
from gen.utils.callback import Callback
from gen.db.iterator import CursorIterator
class GrampsDbBase(object):
    """
    GRAMPS database object. This object is a base class for all
    database interfaces.  All methods raise NotImplementedError
    and must be implemented in the derived class as required.
    """

    def __init__(self):
        """
        Create a new GrampsDbBase instance. 
        
        A new GrampDbBase class should never be directly created. Only classes 
        derived from this class should be created.
        """

        super(GrampsDbBase, self).__init__()

    def set_prefixes(self, person, media, family, source, place, event,
                     repository, note):
        """
        Set the prefixes for the gramps ids for all gramps objects
        """
        raise NotImplementedError

    def rebuild_secondary(self, callback):
        """
        Rebuild secondary indices
        """
        raise NotImplementedError

    def version_supported(self):
        """Return True when the file has a supported version."""
        raise NotImplementedError

    def need_upgrade(self):
        """
        Return True if database needs to be upgraded
        """
        raise NotImplementedError

    def gramps_upgrade(self):
        """
        Return True if database is upgraded
        """
        raise NotImplementedError        

    def del_person(self, handle):
        """
        Delete a Person object given the handle
        """
        raise NotImplementedError        

    def del_source(self, handle):
        """
        Delete a Source object given the handle
        """
        raise NotImplementedError 

    def del_repository(self, handle):
        """
        Delete a Repository object given the handle
        """
        raise NotImplementedError 

    def del_note(self, handle):
        """
        Delete a Person object given the handle
        """
        raise NotImplementedError 

    def del_place(self, handle):
        """
        Delete a Place object given the handle
        """
        raise NotImplementedError 

    def del_media(self, handle):
        """
        Delete a Media object given the handle
        """
        raise NotImplementedError 

    def del_family(self, handle):
        """
        Delete a Family object given the handle
        """
        raise NotImplementedError 

    def del_event(self, handle):
        """
        Delete an Event object given the handle
        """
        raise NotImplementedError 

    def create_id(self):
        """
        Create an id
        """
        raise NotImplementedError 

    def get_person_cursor(self):
        """
        Return a reference to a cursor over Person objects
        """
        raise NotImplementedError 

    def get_person_cursor_iter(self, msg=None):
        """
        Return a reference to a cursor iterator over Person objects
        """
        raise NotImplementedError

    def get_family_cursor(self):
        """
        Return a reference to a cursor over Family objects
        """
        raise NotImplementedError

    def get_family_cursor_iter(self, msg=None):
        """
        Return a reference to a cursor iterator over Family objects
        """
        raise NotImplementedError

    def get_event_cursor(self):
        """
        Return a reference to a cursor over Family objects
        """
        raise NotImplementedError

    def get_event_cursor_iter(self, msg=None):
        """
        Return a reference to a cursor iterator over Family objects
        """
        raise NotImplementedError

    def get_place_cursor(self):
        """
        Return a reference to a cursor over Place objects
        """
        raise NotImplementedError

    def get_place_cursor_iter(self, msg=None):
        """
        Return a reference to a cursor iterator over Place objects
        """
        raise NotImplementedError

    def get_source_cursor(self):
        """
        Return a reference to a cursor over Source objects
        """
        raise NotImplementedError

    def get_source_cursor_iter(self, msg=None):
        """
        Return a reference to a cursor iterator over Source objects
        """
        raise NotImplementedError

    def get_media_cursor(self):
        """
        Return a reference to a cursor over Media objects
        """
        raise NotImplementedError

    def get_media_cursor_iter(self, msg=None):
        """
        Return a reference to a cursor iterator over Media objects
        """
        raise NotImplementedError

    def get_repository_cursor(self):
        """
        Return a reference to a cursor over Repository objects
        """
        raise NotImplementedError

    def get_repository_cursor_iter(self, msg=None):
        """
        Return a reference to a cursor iterator over Repository objects
        """
        raise NotImplementedError

    def get_note_cursor(self):
        """
        Return a reference to a cursor over Note objects
        """
        raise NotImplementedError

    def get_note_cursor_iter(self, msg=None):
        """
        Return a reference to a cursor iterator over Note objects
        """
        raise NotImplementedError

    def open_undodb(self):
        """
        Open the undo database
        """
        raise NotImplementedError

    def close_undodb(self):
        """
        Close the undo database
        """
        raise NotImplementedError

    def load(self, name, callback, mode=None):
        """
        Open the specified database. 
        """
        raise NotImplementedError

    def load_from(self, other_database, filename, callback):
        """
        Load data from the other database into itself.
        
        The filename is the name of the file for the newly created database.
        """
        raise NotImplementedError

    def close(self):
        """
        Close the specified database. 
        """
        pass
        
    def is_open(self):
        """
        Return True if the database has been opened.
        """
        raise NotImplementedError

    def request_rebuild(self):
        """
        Notify clients that the data has changed significantly, and that all
        internal data dependent on the database should be rebuilt.
        Note that all rebuild signals on all objects are emitted at the same
        time. It is correct to assume that this is always the case.
        TODO: it might be better to replace these rebuild signals by one single
                database-rebuild signal.
        """
        raise NotImplementedError
            
    def commit_base(self, obj, data_map, key, update_list, add_list, 
                     transaction, change_time):
        """
        Commit the specified object to the database, storing the changes as 
        part of the transaction.
        """
        raise NotImplementedError

    def commit_person(self, person, transaction, change_time=None):
        """
        Commit the specified Person to the database, storing the changes as 
        part of the transaction.
        """
        raise NotImplementedError

    def commit_media_object(self, obj, transaction, change_time=None):
        """
        Commit the specified MediaObject to the database, storing the changes
        as part of the transaction.
        """
        raise NotImplementedError
            
    def commit_source(self, source, transaction, change_time=None):
        """
        Commit the specified Source to the database, storing the changes as 
        part of the transaction.
        """
        raise NotImplementedError

    def commit_place(self, place, transaction, change_time=None):
        """
        Commit the specified Place to the database, storing the changes as 
        part of the transaction.
        """
        raise NotImplementedError

    def commit_personal_event(self, event, transaction, change_time=None):
        """
        Commit the specified personal Event to the database, storing the
        changes as part of the transaction.
        """
        raise NotImplementedError

    def commit_family_event(self, event, transaction, change_time=None):
        """
        Commit the specified family Event to the database, storing the
        changes as part of the transaction.
        """
        raise NotImplementedError

    def commit_event(self, event, transaction, change_time=None):
        """
        Commit the specified Event to the database, storing the changes as 
        part of the transaction.
        """
        raise NotImplementedError

    def commit_family(self, family, transaction, change_time=None):
        """
        Commit the specified Family to the database, storing the changes as 
        part of the transaction.
        """
        raise NotImplementedError

    def commit_repository(self, repository, transaction, change_time=None):
        """
        Commit the specified Repository to the database, storing the changes
        as part of the transaction.
        """
        raise NotImplementedError

    def commit_note(self, note, transaction, change_time=None):
        """
        Commit the specified Note to the database, storing the changes as part 
        of the transaction.
        """
        raise NotImplementedError

    def find_next_person_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Person object based off the 
        person ID prefix.
        """
        raise NotImplementedError

    def find_next_place_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Place object based off the 
        place ID prefix.
        """
        raise NotImplementedError

    def find_next_event_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Event object based off the 
        event ID prefix.
        """
        raise NotImplementedError

    def find_next_object_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a MediaObject object based
        off the media object ID prefix.
        """
        raise NotImplementedError

    def find_next_source_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Source object based off the 
        source ID prefix.
        """
        raise NotImplementedError

    def find_next_family_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Family object based off the 
        family ID prefix.
        """
        raise NotImplementedError

    def find_next_repository_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Respository object based 
        off the repository ID prefix.
        """
        raise NotImplementedError

    def find_next_note_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Note object based off the 
        note ID prefix.
        """
        raise NotImplementedError

    def get_from_handle(self, handle, class_type, data_map):
        """
        Return unserialized data from database given handle and object class
        """
        raise NotImplementedError

    def get_person_from_handle(self, handle):
        """
        Find a Person in the database from the passed gramps' ID.
        
        If no such Person exists, None is returned.
        """
        raise NotImplementedError

    def get_source_from_handle(self, handle):
        """
        Find a Source in the database from the passed gramps' ID.
        
        If no such Source exists, None is returned.
        """
        raise NotImplementedError

    def get_object_from_handle(self, handle):
        """
        Find an Object in the database from the passed gramps' ID.
        
        If no such Object exists, None is returned.
        """
        raise NotImplementedError

    def get_place_from_handle(self, handle):
        """
        Find a Place in the database from the passed gramps' ID.
        
        If no such Place exists, None is returned.
        """
        raise NotImplementedError

    def get_event_from_handle(self, handle):
        """
        Find a Event in the database from the passed gramps' ID.
        
        If no such Event exists, None is returned.
        """
        raise NotImplementedError

    def get_family_from_handle(self, handle):
        """
        Find a Family in the database from the passed gramps' ID.
        
        If no such Family exists, None is returned.
        """
        raise NotImplementedError

    def get_repository_from_handle(self, handle):
        """
        Find a Repository in the database from the passed gramps' ID.
        
        If no such Repository exists, None is returned.
        """
        raise NotImplementedError

    def get_note_from_handle(self, handle):
        """
        Find a Note in the database from the passed gramps' ID.
        
        If no such Note exists, None is returned.
        """
        raise NotImplementedError

    def find_from_handle(self, handle, transaction, class_type, dmap,
                          add_func):
        """
        Find a object of class_type in the database from the passed handle.
        
        If no object exists, a new object is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        raise NotImplementedError

    def find_person_from_handle(self, handle, transaction):
        """
        Find a Person in the database from the passed handle.
        
        If no such Person exists, a new Person is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        raise NotImplementedError

    def find_source_from_handle(self, handle, transaction):
        """
        Find a Source in the database from the passed handle.
        
        If no such Source exists, a new Source is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        raise NotImplementedError

    def find_event_from_handle(self, handle, transaction):
        """
        Find a Event in the database from the passed handle.
        
        If no such Event exists, a new Event is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        raise NotImplementedError

    def find_object_from_handle(self, handle, transaction):
        """
        Find a MediaObject in the database from the passed handle.
        
        If no such MediaObject exists, a new Object is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        raise NotImplementedError

    def find_place_from_handle(self, handle, transaction):
        """
        Find a Place in the database from the passed handle.
        
        If no such Place exists, a new Place is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        raise NotImplementedError

    def find_family_from_handle(self, handle, transaction):
        """
        Find a Family in the database from the passed handle.
        
        If no such Family exists, a new Family is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        raise NotImplementedError

    def find_repository_from_handle(self, handle, transaction):
        """
        Find a Repository in the database from the passed handle.
        
        If no such Repository exists, a new Repository is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        raise NotImplementedError

    def find_note_from_handle(self, handle, transaction):
        """
        Find a Note in the database from the passed handle.
        
        If no such Note exists, a new Note is added to the database.
        
        @return: Returns a tuple, first the object, second a bool which is True
                 if the object is new
        @rtype: tuple
        """
        raise NotImplementedError

    def check_person_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Person with the passed handle exists in the database.
        
        If no such Person exists, a new Person is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        raise NotImplementedError
        
    def check_source_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Source with the passed handle exists in the database.
        
        If no such Source exists, a new Source is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        raise NotImplementedError
                                
    def check_event_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether an Event with the passed handle exists in the database.
        
        If no such Event exists, a new Event is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        raise NotImplementedError

    def check_object_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a MediaObject with the passed handle exists in the 
        database. 
        
        If no such MediaObject exists, a new Object is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        raise NotImplementedError

    def check_place_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Place with the passed handle exists in the database.
        
        If no such Place exists, a new Place is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        raise NotImplementedError

    def check_family_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Family with the passed handle exists in the database.
        
        If no such Family exists, a new Family is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        raise NotImplementedError

    def check_repository_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Repository with the passed handle exists in the
        database. 
        
        If no such Repository exists, a new Repository is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        raise NotImplementedError

    def check_note_from_handle(self, handle, transaction, set_gid=True):
        """
        Check whether a Note with the passed handle exists in the database. 
        
        If no such Note exists, a new Note is added to the database.
        If set_gid then a new gramps_id is created, if not, None is used.
        """
        raise NotImplementedError

    def get_person_from_gramps_id(self, val):
        """
        Find a Person in the database from the passed GRAMPS ID.
        
        If no such Person exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_family_from_gramps_id(self, val):
        """
        Find a Family in the database from the passed GRAMPS ID.
        
        If no such Family exists, None is returned.
        Need to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_event_from_gramps_id(self, val):
        """
        Find an Event in the database from the passed GRAMPS ID.
        
        If no such Event exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_place_from_gramps_id(self, val):
        """
        Find a Place in the database from the passed gramps' ID.
        
        If no such Place exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_source_from_gramps_id(self, val):
        """
        Find a Source in the database from the passed gramps' ID.
        
        If no such Source exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_object_from_gramps_id(self, val):
        """
        Find a MediaObject in the database from the passed gramps' ID.

        If no such MediaObject exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_repository_from_gramps_id(self, val):
        """
        Find a Repository in the database from the passed gramps' ID.

        If no such Repository exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_note_from_gramps_id(self, val):
        """
        Find a Note in the database from the passed gramps' ID.

        If no such Note exists, None is returned.
        Needs to be overridden by the derived classderri.
        """
        raise NotImplementedError

    def add_person(self, person, transaction, set_gid=True):
        """
        Add a Person to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_family(self, family, transaction, set_gid=True):
        """
        Add a Family to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_source(self, source, transaction, set_gid=True):
        """
        Add a Source to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError
       
    def add_event(self, event, transaction, set_gid=True):
        """
        Add an Event to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_person_event(self, event, transaction):
        """
        Add an Event to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_family_event(self, event, transaction):
        """
        Add an Event to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_place(self, place, transaction, set_gid=True):
        """
        Add a Place to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_object(self, obj, transaction, set_gid=True):
        """
        Add a MediaObject to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_repository(self, obj, transaction, set_gid=True):
        """
        Add a Repository to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_note(self, obj, transaction, set_gid=True):
        """
        Add a Note to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def get_name_group_mapping(self, name):
        """
        Return the default grouping name for a surname.
        """
        raise NotImplementedError

    def get_name_group_keys(self):
        """
        Return the defined names that have been assigned to a default grouping.
        """
        raise NotImplementedError

    def has_name_group_key(self, name):
        """
        Return if a key exists in the name_group table.
        """
        raise NotImplementedError

    def set_name_group_mapping(self, name, group):
        """
        Set the default grouping name for a surname. 
        
        Needs to be overridden in the derived class.
        """
        raise NotImplementedError
        
    def get_number_of_people(self):
        """
        Return the number of people currently in the database.
        """
        raise NotImplementedError

    def get_number_of_families(self):
        """
        Return the number of families currently in the database.
        """
        raise NotImplementedError

    def get_number_of_events(self):
        """
        Return the number of events currently in the database.
        """
        raise NotImplementedError

    def get_number_of_places(self):
        """
        Return the number of places currently in the database.
        """
        raise NotImplementedError

    def get_number_of_sources(self):
        """
        Return the number of sources currently in the database.
        """
        raise NotImplementedError

    def get_number_of_media_objects(self):
        """
        Return the number of media objects currently in the database.
        """
        raise NotImplementedError

    def get_number_of_repositories(self):
        """
        Return the number of source repositories currently in the database.
        """
        raise NotImplementedError

    def get_number_of_notes(self):
        """
        Return the number of notes currently in the database.
        """
        raise NotImplementedError

    def all_handles(self, table):
        """
        Return all handles from the specified table as a list
        """
        return table.keys()
        
    def get_person_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Person in
        the database. 
        
        If sort_handles is True, the list is sorted by surnames.
        """
        raise NotImplementedError

    def iter_person_handles(self):
        """
        Return an iterator over handles for Persons in the database
        """
        raise NotImplementedError
                
    def iter_people(self):
        """
        Return an iterator over handles and objects for Persons in the database
        """
        raise NotImplementedError

    def get_place_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Place in
        the database. 
        
        If sort_handles is True, the list is sorted by Place title.
        """
        raise NotImplementedError
        
    def iter_place_handles(self):
        """
        Return an iterator over handles for Places in the database
        """
        raise NotImplementedError
                
    def get_source_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Source in
        the database.
        
        If sort_handles is True, the list is sorted by Source title.
        """
        raise NotImplementedError
        
    def iter_source_handles(self):
        """
        Return an iterator over handles for Sources in the database
        """
        raise NotImplementedError
                
    def get_media_object_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each MediaObject in
        the database. 
        
        If sort_handles is True, the list is sorted by title.
        """
        raise NotImplementedError
        
    def iter_media_object_handles(self):
        """
        Return an iterator over handles for Media in the database
        """
        raise NotImplementedError

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in the 
        database. 
        """
        raise NotImplementedError
        
    def iter_event_handles(self):
        """
        Return an iterator over handles for Events in the database
        """
        raise NotImplementedError

    def get_family_handles(self):
        """
        Return a list of database handles, one handle for each Family in
        the database.
        """
        raise NotImplementedError
        
    def iter_family_handles(self):
        """
        Return an iterator over handles for Families in the database
        """
        raise NotImplementedError     

    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository in
        the database.
        """
        raise NotImplementedError
        
    def iter_repository_handles(self):
        """
        Return an iterator over handles for Repositories in the database
        """
        raise NotImplementedError

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in the 
        database.
        """
        raise NotImplementedError
        
    def iter_note_handles(self):
        """
        Return an iterator over handles for Notes in the database
        """
        raise NotImplementedError

    def get_gramps_ids(self, obj_key):
        """
        Returns all the keys from a table given a table name
        """
        raise NotImplementedError
        
    def has_gramps_id(self, obj_key, gramps_id):
        """
        Returns True if the key exists in table given a table name

        Not used in current codebase
        """
        raise NotImplementedError

    def find_initial_person(self):
        """
        Returns first person in the database 
        """
        raise NotImplementedError        

    def set_person_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Person ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as I%d or I%04d.
        """
        raise NotImplementedError
            
    def set_source_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Source ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as S%d or S%04d.
        """
        raise NotImplementedError 
            
    def set_object_id_prefix(self, val):
        """
        Set the naming template for GRAMPS MediaObject ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as O%d or O%04d.
        """
        raise NotImplementedError

    def set_place_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Place ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as P%d or P%04d.
        """
        raise NotImplementedError

    def set_family_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Family ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as F%d
        or F%04d.
        """
        raise NotImplementedError

    def set_event_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Event ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as E%d or E%04d.
        """
        raise NotImplementedError

    def set_repository_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Repository ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as R%d or R%04d.
        """
        raise NotImplementedError

    def set_note_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Note ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as N%d or N%04d.
        """
        raise NotImplementedError

    def transaction_begin(self, msg="", batch=False, no_magic=False):
        """
        Create a new Transaction tied to the current UNDO database. 
        
        The transaction has no effect until it is committed using the
        transaction_commit function of the this database object.
        """
        raise NotImplementedError

    def transaction_commit(self, transaction, msg):
        """
        Commit the transaction to the associated UNDO database.
        """
        raise NotImplementedError

    def set_undo_callback(self, callback):
        """
        Define the callback function that is called whenever an undo operation
        is executed. 
        
        The callback function receives a single argument that is a text string 
        that defines the operation.
        """
        raise NotImplementedError

    def set_redo_callback(self, callback):
        """
        Define the callback function that is called whenever an redo operation
        is executed. 
        
        The callback function receives a single argument that is a text string 
        that defines the operation.
        """
        raise NotImplementedError

    def get_surname_list(self):
        """
        Return the list of locale-sorted surnames contained in the database.
        """
        raise NotImplementedError

    def build_surname_list(self):
        """
        Build the list of locale-sorted surnames contained in the database.
        """
        raise NotImplementedError

    def sort_surname_list(self):
        """
        Sort the list of surnames contained in the database by locale ordering.
        """
        raise NotImplementedError        

    def add_to_surname_list(self, person, batch_transaction):
        """
        Add surname from given person to list of surnames
        """
        raise NotImplementedError            
        if batch_transaction:
            return
        name = unicode(person.get_primary_name().get_surname())
        if name not in self.surname_list:
            self.surname_list.append(name)
            self.sort_surname_list()

    def remove_from_surname_list(self, person):
        """
        Check whether there are persons with the same surname left in
        the database. 
        
        If not then we need to remove the name from the list.
        The function must be overridden in the derived class.
        """
        raise NotImplementedError

    def get_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        raise NotImplementedError

    def get_family_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        raise NotImplementedError

    def get_event_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        raise NotImplementedError

    def get_place_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        raise NotImplementedError

    def get_source_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        raise NotImplementedError

    def get_media_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        raise NotImplementedError

    def get_repo_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        raise NotImplementedError

    def get_note_bookmarks(self):
        """Return the list of Note handles in the bookmarks."""
        raise NotImplementedError

    def set_researcher(self, owner):
        """Set the information about the owner of the database."""
        raise NotImplementedError

    def get_researcher(self):
        """
        Return the Researcher instance, providing information about the owner 
        of the database.
        """
        raise NotImplementedError

    def set_default_person_handle(self, handle):
        """Set the default Person to the passed instance."""
        raise NotImplementedError

    def get_default_person(self):
        """Return the default Person of the database."""
        raise NotImplementedError

    def get_default_handle(self):
        """Return the default Person of the database."""
        raise NotImplementedError

    def get_save_path(self):
        """Return the save path of the file, or "" if one does not exist."""
        raise NotImplementedError

    def set_save_path(self, path):
        """Set the save path for the database."""
        raise NotImplementedError

    def get_person_event_types(self):
        """
        Return a list of all Event types associated with Person instances in 
        the database.
        """
        raise NotImplementedError
        
    def get_person_attribute_types(self):
        """
        Return a list of all Attribute types associated with Person instances 
        in the database.
        """
        raise NotImplementedError
        
    def get_family_attribute_types(self):
        """
        Return a list of all Attribute types associated with Family instances 
        in the database.
        """
        raise NotImplementedError
        
    def get_family_event_types(self):
        """
        Return a list of all Event types associated with Family instances in 
        the database.
        """
        raise NotImplementedError
        
    def get_marker_types(self):
        """
        Return a list of all marker types available in the database.
        """
        raise NotImplementedError
        
    def get_media_attribute_types(self):
        """
        Return a list of all Attribute types associated with Media and MediaRef 
        instances in the database.
        """
        raise NotImplementedError

    def get_family_relation_types(self):
        """
        Return a list of all relationship types associated with Family
        instances in the database.
        """
        raise NotImplementedError

    def get_child_reference_types(self):
        """
        Return a list of all child reference types associated with Family
        instances in the database.
        """
        raise NotImplementedError

    def get_event_roles(self):
        """
        Return a list of all custom event role names associated with Event
        instances in the database.
        """
        raise NotImplementedError

    def get_name_types(self):
        """
        Return a list of all custom names types associated with Person
        instances in the database.
        """
        raise NotImplementedError

    def get_repository_types(self):
        """
        Return a list of all custom repository types associated with Repository 
        instances in the database.
        """
        raise NotImplementedError

    def get_note_types(self):
        """
        Return a list of all custom note types associated with Note instances 
        in the database.
        """
        raise NotImplementedError

    def get_source_media_types(self):
        """
        Return a list of all custom source media types associated with Source 
        instances in the database.
        """
        raise NotImplementedError

    def get_url_types(self):
        """
        Return a list of all custom names types associated with Url instances 
        in the database.
        """
        raise NotImplementedError

    def remove_person(self, handle, transaction):
        """
        Remove the Person specified by the database handle from the database, 
        preserving the change in the passed transaction. 
        
        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def get_del_func(self, key):
        """
        Returns the key of an object to delete
        """
        raise NotImplementedError

    def remove_source(self, handle, transaction):
        """
        Remove the Source specified by the database handle from the
        database, preserving the change in the passed transaction. 
        
        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_event(self, handle, transaction):
        """
        Remove the Event specified by the database handle from the
        database, preserving the change in the passed transaction. 
        
        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_object(self, handle, transaction):
        """
        Remove the MediaObjectPerson specified by the database handle from the
        database, preserving the change in the passed transaction. 
        
        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_place(self, handle, transaction):
        """
        Remove the Place specified by the database handle from the
        database, preserving the change in the passed transaction. 
        
        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_family(self, handle, transaction):
        """
        Remove the Family specified by the database handle from the
        database, preserving the change in the passed transaction. 
        
        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_repository(self, handle, transaction):
        """
        Remove the Repository specified by the database handle from the
        database, preserving the change in the passed transaction. 
        
        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_note(self, handle, transaction):
        """
        Remove the Note specified by the database handle from the
        database, preserving the change in the passed transaction. 
        
        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def get_raw_person_data(self, handle):
        """
        Return raw (serialized and pickled) Person object from handle
        """
        raise NotImplementedError

    def get_raw_family_data(self, handle):
        """
        Return raw (serialized and pickled) Family object from handle
        """
        raise NotImplementedError

    def get_raw_object_data(self, handle):
        """
        Return raw (serialized and pickled) Family object from handle
        """
        raise NotImplementedError

    def get_raw_place_data(self, handle):
        """
        Return raw (serialized and pickled) Place object from handle
        """
        raise NotImplementedError

    def get_raw_event_data(self, handle):
        """
        Return raw (serialized and pickled) Event object from handle
        """
        raise NotImplementedError

    def get_raw_source_data(self, handle):
        """
        Return raw (serialized and pickled) Source object from handle
        """
        raise NotImplementedError

    def get_raw_repository_data(self, handle):
        """
        Return raw (serialized and pickled) Repository object from handle
        """
        raise NotImplementedError

    def get_raw_note_data(self, handle):
        """
        Return raw (serialized and pickled) Note object from handle
        """
        raise NotImplementedError

    def has_person_handle(self, handle):
        """
        Return True if the handle exists in the current Person database.
        """
        raise NotImplementedError

    def has_event_handle(self, handle):
        """
        Return True if the handle exists in the current Event database.
        """
        raise NotImplementedError

    def has_source_handle(self, handle):
        """
        Return True if the handle exists in the current Source database.
        """
        raise NotImplementedError

    def has_place_handle(self, handle):
        """
        Return True if the handle exists in the current Place database.
        """
        raise NotImplementedError

    def has_family_handle(self, handle):            
        """
        Return True if the handle exists in the current Family database.
        """
        raise NotImplementedError

    def has_object_handle(self, handle):
        """
        Return True if the handle exists in the current MediaObjectdatabase.
        """
        raise NotImplementedError

    def has_repository_handle(self, handle):
        """
        Return True if the handle exists in the current Repository database.
        """
        raise NotImplementedError

    def has_note_handle(self, handle):
        """
        Return True if the handle exists in the current Note database.
        """
        raise NotImplementedError

    def set_mediapath(self, path):
        """Set the default media path for database, path should be utf-8."""
        raise NotImplementedError

    def get_mediapath(self):
        """Return the default media path of the database."""
        raise NotImplementedError

    def set_person_column_order(self, col_list):
        """
        Store the Person display common information in the database's metadata.
        """
        raise NotImplementedError

    def set_family_list_column_order(self, col_list):
        """
        Store the Person display common information in the database's metadata.
        """
        raise NotImplementedError

    def set_child_column_order(self, col_list):
        """
        Store the Person display common information in the database's metadata.
        """
        raise NotImplementedError

    def set_place_column_order(self, col_list):
        """
        Store the Place display common information in the database's metadata.
        """
        raise NotImplementedError

    def set_source_column_order(self, col_list):
        """
        Store the Source display common information in the database's metadata.
        """
        raise NotImplementedError

    def set_media_column_order(self, col_list):
        """
        Store the Media display common information in the database's metadata.
        """
        raise NotImplementedError

    def set_event_column_order(self, col_list):
        """
        Store the Event display common information in the database's metadata.
        """
        raise NotImplementedError

    def set_repository_column_order(self, col_list):
        """
        Store the Repository display common information in the database's 
        metadata.
        """
        raise NotImplementedError

    def set_note_column_order(self, col_list):
        """
        Store the Note display common information in the database's metadata.
        """
        raise NotImplementedError

    def get_person_column_order(self):
        """
        Return the Person display common information stored in the database's 
        metadata.
        """
        raise NotImplementedError

    def get_family_list_column_order(self):
        """
        Return the Person display common information stored in the database's 
        metadata.
        """
        raise NotImplementedError

    def get_child_column_order(self):
        """
        Return the Person display common information stored in the database's 
        metadata.
        """
        raise NotImplementedError

    def get_place_column_order(self):
        """
        Return the Place display common information stored in thedatabase's 
        metadata.
        """
        raise NotImplementedError

    def get_source_column_order(self):
        """
        Return the Source display common information stored in the database's 
        metadata.
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
        Return the Event display common information stored in the database's 
        metadata.
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
        Return the Note display common information stored in the database's 
        metadata.
        """
        raise NotImplementedError

    def delete_primary_from_reference_map(self, handle, transaction):
        """
        Called each time an object is removed from the database. 
        
        This can be used by subclasses to update any additional index tables 
        that might need to be changed.
        """
        raise NotImplementedError

    def update_reference_map(self, obj, transaction):
        """
        Called each time an object is writen to the database. 
        
        This can be used by subclasses to update any additional index tables 
        that might need to be changed.
        """
        raise NotImplementedError

    def reindex_reference_map(self, callback):
        """
        Reindex all primary records in the database.
        """
        raise NotImplementedError

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        
        Returns an iterator over a list of (class_name, handle) tuples.

        @param handle: handle of the object to search for.
        @type handle: database handle
        @param include_classes: list of class names to include in the results.
                                Default: None means include all classes.
        @type include_classes: list of class names
        
        This default implementation does a sequential scan through all
        the primary object databases and is very slow. Backends can
        override this method to provide much faster implementations that
        make use of additional capabilities of the backend.

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use:

        >    result_list = list(find_backlink_handles(handle))
        """
        raise NotImplementedError

    def report_bm_change(self):
        """
        Add 1 to the number of bookmark changes during this session.
        """
        raise NotImplementedError

    def db_has_bm_changes(self):
        """
        Return whethere there were bookmark changes during the session.
        """
        raise NotImplementedError
