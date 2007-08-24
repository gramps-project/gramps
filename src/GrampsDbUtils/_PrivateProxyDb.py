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

__author__ = "Brian Matherly"
__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
from RelLib import *

class PrivateProxyDb:
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all data marked private will be hidden from the user.
    """

    def __init__(self,db):
        """
        Creates a new PrivateProxyDb instance. 
        """
        self.db = db

    def set_prefixes(self, person, media, family, source, place, event,
                     repository, note):
        raise NotImplementedError

    def rebuild_secondary(self, callback):
        raise NotImplementedError

    def version_supported(self):
        """ Returns True when the file has a supported version"""
        raise NotImplementedError

    def need_upgrade(self):
        raise NotImplementedError

    def gramps_upgrade(self):
        raise NotImplementedError

    def del_person(self, handle):
        raise NotImplementedError

    def del_source(self, handle):
        raise NotImplementedError

    def del_repository(self, handle):
        raise NotImplementedError

    def del_note(self, handle):
        raise NotImplementedError

    def del_place(self, handle):
        raise NotImplementedError

    def del_media(self, handle):
        raise NotImplementedError

    def del_family(self, handle):
        raise NotImplementedError

    def del_event(self, handle):
        raise NotImplementedError

    def create_id(self):
        raise NotImplementedError

    def get_person_cursor(self):
        raise NotImplementedError

    def get_person_cursor_iter(self, msg=_("Processing Person records")):
        raise NotImplementedError

    def get_family_cursor(self):
        raise NotImplementedError

    def get_family_cursor_iter(self, msg=_("Processing Family records")):
        raise NotImplementedError

    def get_event_cursor(self):
        raise NotImplementedError

    def get_event_cursor_iter(self, msg=_("Processing Event records")):
        raise NotImplementedError

    def get_place_cursor(self):
        raise NotImplementedError

    def get_place_cursor_iter(self, msg=_("Processing Place records")):
        raise NotImplementedError

    def get_source_cursor(self):
        raise NotImplementedError

    def get_source_cursor_iter(self, msg=_("Processing Source records")):
        raise NotImplementedError

    def get_media_cursor(self):
        raise NotImplementedError

    def get_media_cursor_iter(self, msg=_("Processing Media records")):
        raise NotImplementedError

    def get_repository_cursor(self):
        raise NotImplementedError

    def get_repository_cursor_iter(self, msg=_("Processing Repository records")):
        raise NotImplementedError

    def get_note_cursor(self):
        raise NotImplementedError

    def get_note_cursor_iter(self, msg=_("Processing Note records")):
        raise NotImplementedError

    def open_undodb(self):
        raise NotImplementedError

    def close_undodb(self):
        raise NotImplementedError

    def load(self, name, callback, mode="w"):
        """
        Opens the specified database. The method needs to be overridden
        in the derived class.
        """
        raise NotImplementedError

    def load_from(self, other_database, filename, callback):
        """
        Loads data from the other database into itself.
        The filename is the name of the file for the newly created database.
        The method needs to be overridden in the derived class.
        """
        raise NotImplementedError

    def close(self):
        """
        Closes the specified database. The method needs to be overridden
        in the derived class.
        """
        raise NotImplementedError
        
    def is_open(self):
        """
        Returns 1 if the database has been opened.
        """
        return self.db.is_open

    def request_rebuild(self):
        raise NotImplementedError
            
    def commit_base(self, obj, data_map, key, update_list, add_list, 
                     transaction, change_time):
        raise NotImplementedError

    def commit_person(self, person, transaction, change_time=None):
        raise NotImplementedError

    def commit_media_object(self, obj, transaction, change_time=None):
        raise NotImplementedError
            
    def commit_source(self, source, transaction, change_time=None):
        raise NotImplementedError

    def commit_place(self, place, transaction, change_time=None):
        raise NotImplementedError

    def commit_personal_event(self, event, transaction, change_time=None):
        raise NotImplementedError

    def commit_family_event(self, event, transaction, change_time=None):
        raise NotImplementedError

    def commit_event(self, event, transaction, change_time=None):
        raise NotImplementedError

    def commit_family(self, family, transaction, change_time=None):
        raise NotImplementedError

    def commit_repository(self, repository, transaction, change_time=None):
        raise NotImplementedError

    def commit_note(self, note, transaction, change_time=None):
        raise NotImplementedError

    def find_next_person_gramps_id(self):
        raise NotImplementedError

    def find_next_place_gramps_id(self):
        raise NotImplementedError

    def find_next_event_gramps_id(self):
        raise NotImplementedError

    def find_next_object_gramps_id(self):
        raise NotImplementedError

    def find_next_source_gramps_id(self):
        raise NotImplementedError

    def find_next_family_gramps_id(self):
        raise NotImplementedError

    def find_next_repository_gramps_id(self):
        raise NotImplementedError

    def find_next_note_gramps_id(self):
        raise NotImplementedError

    def get_person_from_handle(self, handle):
        """
        Finds a Person in the database from the passed gramps' ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_handle(handle)
        if person and person.get_privacy() == False:
            return sanitize_person(self.db,person)
        return None

    def get_source_from_handle(self, handle):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        source = self.db.get_source_from_handle(handle)
        if source and source.get_privacy() == False:
            return sanitize_source(self.db,source)
        return None

    def get_object_from_handle(self, handle):
        """
        Finds an Object in the database from the passed gramps' ID.
        If no such Object exists, None is returned.
        """
        media = self.db.get_object_from_handle(handle)
        if media and media.get_privacy() == False:
            return sanitize_media(self.db,media)
        return None

    def get_place_from_handle(self, handle):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        place = self.db.get_place_from_handle(handle)
        if place and place.get_privacy() == False:
            return sanitize_place(self.db,place)
        return None

    def get_event_from_handle(self, handle):
        """
        Finds a Event in the database from the passed gramps' ID.
        If no such Event exists, None is returned.
        """
        event = self.db.get_event_from_handle(handle)
        if event and event.get_privacy() == False:
            return sanitize_event(self.db,event)
        return None

    def get_family_from_handle(self, handle):
        """
        Finds a Family in the database from the passed gramps' ID.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_handle(handle)
        if family and family.get_privacy() == False:
            return sanitize_family(self.db,family)
        return None

    def get_repository_from_handle(self, handle):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        repository = self.db.get_repository_from_handle(handle)
        if repository and repository.get_privacy() == False:
            return sanitize_repository(self.db,repository)
        return None

    def get_note_from_handle(self, handle):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        return self.db.get_note_from_handle(handle)

    def find_person_from_handle(self, handle, transaction):
        """
        Finds a Person in the database from the passed GRAMPS ID.
        If no such Person exists, a new Person is added to the database.
        """
        raise NotImplementedError

    def find_source_from_handle(self, handle, transaction):
        """
        Finds a Source in the database from the passed handle.
        If no such Source exists, a new Source is added to the database.
        """
        raise NotImplementedError

    def find_event_from_handle(self, handle, transaction):
        """
        Finds a Event in the database from the passed handle.
        If no such Event exists, a new Event is added to the database.
        """
        raise NotImplementedError

    def find_object_from_handle(self, handle, transaction):
        """
        Finds an MediaObject in the database from the passed handle.
        If no such MediaObject exists, a new Object is added to the database.
        """
        raise NotImplementedError

    def find_place_from_handle(self, handle, transaction):
        """
        Finds a Place in the database from the passed handle.
        If no such Place exists, a new Place is added to the database.
        """
        raise NotImplementedError

    def find_family_from_handle(self, handle, transaction):
        """
        Finds a Family in the database from the passed handle.
        If no such Family exists, a new Family is added to the database.
        """
        raise NotImplementedError

    def find_repository_from_handle(self, handle, transaction):
        """
        Finds a Repository in the database from the passed handle.
        If no such Repository exists, a new Repository is added to the database.
        """
        raise NotImplementedError

    def find_note_from_handle(self, handle, transaction):
        """
        Finds a Note in the database from the passed handle.
        If no such Note exists, a new Note is added to the database.
        """
        raise NotImplementedError

    def check_person_from_handle(self, handle, transaction):
        """
        Checks whether a Person with the passed handle exists in the database.
        If no such Person exists, a new Person is added to the database.
        """
        raise NotImplementedError

    def check_source_from_handle(self, handle, transaction):
        """
        Checks whether a Source with the passed handle exists in the database.
        If no such Source exists, a new Source is added to the database.
        """
        raise NotImplementedError

    def check_event_from_handle(self, handle, transaction):
        """
        Checks whether an Event with the passed handle exists in the database.
        If no such Event exists, a new Event is added to the database.
        """
        raise NotImplementedError

    def check_object_from_handle(self, handle, transaction):
        """
        Checks whether a MediaObject with the passed handle exists in
        the database. If no such MediaObject exists, a new Object is
        added to the database.
        """
        raise NotImplementedError

    def check_place_from_handle(self, handle, transaction):
        """
        Checks whether a Place with the passed handle exists in the database.
        If no such Place exists, a new Place is added to the database.
        """
        raise NotImplementedError

    def check_family_from_handle(self, handle, transaction):
        """
        Checks whether a Family with the passed handle exists in the database.
        If no such Family exists, a new Family is added to the database.
        """
        raise NotImplementedError

    def check_repository_from_handle(self, handle, transaction):
        """
        Checks whether a Repository with the passed handle exists in the
        database. If no such Repository exists, a new Repository is added
        to the database.
        """
        raise NotImplementedError

    def check_note_from_handle(self, handle, transaction):
        """
        Checks whether a Note with the passed handle exists in the
        database. If no such Note exists, a new Note is added
        to the database.
        """
        raise NotImplementedError

    def get_person_from_gramps_id(self, val):
        """
        Finds a Person in the database from the passed GRAMPS ID.
        If no such Person exists, None is returned.
        """
        person = self.db.get_person_from_gramps_id(val)
        if person.get_privacy() == False:
            return sanitize_person(self.db,person)
        return None

    def get_family_from_gramps_id(self, val):
        """
        Finds a Family in the database from the passed GRAMPS ID.
        If no such Family exists, None is returned.
        """
        family = self.db.get_family_from_gramps_id(val)
        if family.get_privacy() == False:
            return sanitize_family(self.db,family)
        return None

    def get_event_from_gramps_id(self, val):
        """
        Finds an Event in the database from the passed GRAMPS ID.
        If no such Event exists, None is returned.
        """
        event = self.db.get_event_from_gramps_id(val)
        if event.get_privacy() == False:
            return sanitize_event(self.db,event)
        return None

    def get_place_from_gramps_id(self, val):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        place = self.db.get_place_from_gramps_id(val)
        if place.get_privacy() == False:
            return sanitize_place(self.db,place)
        return None

    def get_source_from_gramps_id(self, val):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        source = self.db.get_source_from_gramps_id(val)
        if source.get_privacy() == False:
            return sanitize_source(self.db,source)
        return None

    def get_object_from_gramps_id(self, val):
        """
        Finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, None is returned.
        """
        object = self.db.get_object_from_gramps_id(val)
        if object.get_privacy() == False:
            return sanitize_media(self.db,object)
        return None

    def get_repository_from_gramps_id(self, val):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        repository = self.db.get_repository_from_gramps_id(val)
        if repository.get_privacy() == False:
            return sanitize_repository(self.db,repository)
        return None

    def get_note_from_gramps_id(self, val):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        note = self.db.get_note_from_gramps_id(val)
        if note.get_privacy() == False:
            return note
        return None

    def add_person(self, person, transaction):
        """
        Adds a Person to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_family(self, family, transaction):
        """
        Adds a Family to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_source(self, source, transaction):
        """
        Adds a Source to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_event(self, event, transaction):
        """
        Adds an Event to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_person_event(self, event, transaction):
        """
        Adds an Event to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_family_event(self, event, transaction):
        """
        Adds an Event to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_place(self, place, transaction):
        """
        Adds a Place to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_object(self, obj, transaction):
        """
        Adds a MediaObject to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_repository(self, obj, transaction):
        """
        Adds a Repository to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

    def add_note(self, obj, transaction):
        """
        Adds a Note to the database, assigning internal IDs if they have
        not already been defined.
        """
        raise NotImplementedError

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

    def set_name_group_mapping(self, name, group):
        """
        Sets the default grouping name for a surname. Needs to be overridden
        in the derived class.
        """
        raise NotImplementedError

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
        return len(self.get_object_handles())

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

    def get_person_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each Person in
        the database. If sort_handles is True, the list is sorted by surnames
        """
        handles = []
        for handle in self.db.get_person_handles(sort_handles):
            person = self.db.get_person_from_handle(handle)
            if person.get_privacy() == False:
                handles.append(handle)
        return handles

    def get_place_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each Place in
        the database. If sort_handles is True, the list is sorted by
        Place title.
        """
        handles = []
        for handle in self.db.get_place_handles(sort_handles):
            place = self.db.get_place_from_handle(handle)
            if place.get_privacy() == False:
                handles.append(handle)
        return handles

    def get_source_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each Source in
        the database. If sort_handles is True, the list is sorted by
        Source title.
        """
        handles = []
        for handle in self.db.get_source_handles(sort_handles):
            source = self.db.get_source_from_handle(handle)
            if source.get_privacy() == False:
                handles.append(handle)
        return handles

    def get_media_object_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each MediaObject in
        the database. If sort_handles is True, the list is sorted by title.
        """
        handles = []
        for handle in self.db.get_media_object_handles(sort_handles):
            object = self.db.get_object_from_handle(handle)
            if object.get_privacy() == False:
                handles.append(handle)
        return handles

    def get_event_handles(self):
        """
        Returns a list of database handles, one handle for each Event in
        the database. 
        """
        handles = []
        for handle in self.db.get_event_handles():
            event = self.db.get_event_from_handle(handle)
            if event.get_privacy() == False:
                handles.append(handle)
        return handles

    def get_family_handles(self):
        """
        Returns a list of database handles, one handle for each Family in
        the database.
        """
        handles = []
        for handle in self.db.get_family_handles():
            family = self.db.get_family_from_handle(handle)
            if family.get_privacy() == False:
                handles.append(handle)
        return handles

    def get_repository_handles(self):
        """
        Returns a list of database handles, one handle for each Repository in
        the database.
        """
        handles = []
        for handle in self.db.get_repository_handles():
            repository = self.db.get_repository_from_handle(handle)
            if repository.get_privacy() == False:
                handles.append(handle)
        return handles

    def get_note_handles(self):
        """
        Returns a list of database handles, one handle for each Note in
        the database.
        """
        handles = []
        for handle in self.db.get_note_handles():
            note = self.db.get_note_from_handle(handle)
            if note.get_privacy() == False:
                handles.append(handle)
        return handles

    def get_gramps_ids(self, obj_key):
        raise NotImplementedError

    def has_gramps_id(self, obj_key, gramps_id):
        raise NotImplementedError

    def find_initial_person(self):
        raise NotImplementedError

    def set_person_id_prefix(self, val):
        """
        Sets the naming template for GRAMPS Person ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as I%d
        or I%04d.
        """
        raise NotImplementedError
            
    def set_source_id_prefix(self, val):
        """
        Sets the naming template for GRAMPS Source ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as S%d
        or S%04d.
        """
        raise NotImplementedError
            
    def set_object_id_prefix(self, val):
        """
        Sets the naming template for GRAMPS MediaObject ID values. The string
        is expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as O%d
        or O%04d.
        """
        raise NotImplementedError

    def set_place_id_prefix(self, val):
        """
        Sets the naming template for GRAMPS Place ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as P%d
        or P%04d.
        """
        raise NotImplementedError

    def set_family_id_prefix(self, val):
        """
        Sets the naming template for GRAMPS Family ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as F%d
        or F%04d.
        """
        raise NotImplementedError

    def set_event_id_prefix(self, val):
        """
        Sets the naming template for GRAMPS Event ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as E%d
        or E%04d.
        """
        raise NotImplementedError

    def set_repository_id_prefix(self, val):
        """
        Sets the naming template for GRAMPS Repository ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as R%d
        or R%04d.
        """
        raise NotImplementedError

    def set_note_id_prefix(self, val):
        """
        Sets the naming template for GRAMPS Note ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as N%d
        or N%04d.
        """
        raise NotImplementedError

    def transaction_begin(self, msg="", batch=False, no_magic=False):
        """
        Creates a new Transaction tied to the current UNDO database. The
        transaction has no effect until it is committed using the
        transaction_commit function of the this database object.
        """
        raise NotImplementedError

    def transaction_commit(self, transaction, msg):
        """
        Commits the transaction to the assocated UNDO database.
        """
        raise NotImplementedError

    def do_commit(self, add_list, db_map):
        raise NotImplementedError

    def undo_available(self):
        """
        returns boolean of whether or not there's a possibility of undo
        """
        raise NotImplementedError
        
    def redo_available(self):
        """
        returns boolean of whether or not there's a possibility of redo
        """
        raise NotImplementedError
        
    def undo(self, update_history=True):
        """
        Accesses the last committed transaction, and reverts the data to
        the state before the transaction was committed.
        """
        raise NotImplementedError

    def redo(self, update_history=True):
        """
        Accesses the last undone transaction, and reverts the data to
        the state before the transaction was undone.
        """
        raise NotImplementedError

    def undo_reference(self, data, handle):
        raise NotImplementedError
    
    def set_undo_callback(self, callback):
        """
        Defines the callback function that is called whenever an undo operation
        is executed. The callback function recieves a single argument that is a
        text string that defines the operation.
        """
        raise NotImplementedError

    def set_redo_callback(self, callback):
        """
        Defines the callback function that is called whenever an redo operation
        is executed. The callback function recieves a single argument that is a
        text string that defines the operation.
        """
        raise NotImplementedError

    def get_surname_list(self):
        """
        Returns the list of locale-sorted surnames contained in the database.
        """
        raise NotImplementedError

    def build_surname_list(self):
        """
        Builds the list of locale-sorted surnames contained in the database.
        The function must be overridden in the derived class.
        """
        raise NotImplementedError

    def add_to_surname_list(self, person, batch_transaction):
        raise NotImplementedError

    def remove_from_surname_list(self, person):
        """
        Check whether there are persons with the same surname left in
        the database. If not then we need to remove the name from the list.
        The function must be overridden in the derived class.
        """
        raise NotImplementedError

    def get_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        raise NotImplementedError

    def get_family_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        raise NotImplementedError

    def get_event_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        raise NotImplementedError

    def get_place_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        raise NotImplementedError

    def get_source_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        raise NotImplementedError

    def get_media_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        raise NotImplementedError

    def get_repo_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        raise NotImplementedError

    def get_note_bookmarks(self):
        """returns the list of Note handles in the bookmarks"""
        raise NotImplementedError

    def set_researcher(self, owner):
        """sets the information about the owner of the database"""
        raise NotImplementedError

    def get_researcher(self):
        """returns the Researcher instance, providing information about
        the owner of the database"""
        raise NotImplementedError

    def set_default_person_handle(self, handle):
        """sets the default Person to the passed instance"""
        raise NotImplementedError

    def get_default_person(self):
        """returns the default Person of the database"""
        person = self.db.get_default_person()
        if person and person.get_privacy() == False:
            return sanitize_person(self.db,person)
        return None

    def get_default_handle(self):
        """returns the default Person of the database"""
        handle = self.db.get_default_handle()
        person = self.db.get_person_from_handle(handle)
        if person and person.get_privacy() == False:
            return handle
        return None

    def get_save_path(self):
        """returns the save path of the file, or "" if one does not exist"""
        return self.db.get_save_path()

    def set_save_path(self, path):
        """sets the save path for the database"""
        raise NotImplementedError

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

    def remove_person(self, handle, transaction):
        """
        Removes the Person specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_source(self, handle, transaction):
        """
        Removes the Source specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_event(self, handle, transaction):
        """
        Removes the Event specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_object(self, handle, transaction):
        """
        Removes the MediaObjectPerson specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_place(self, handle, transaction):
        """
        Removes the Place specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_family(self, handle, transaction):
        """
        Removes the Family specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_repository(self, handle, transaction):
        """
        Removes the Repository specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_note(self, handle, transaction):
        """
        Removes the Note specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        raise NotImplementedError

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
        return self.db.has_person_handle(handle)

    def has_event_handle(self, handle):
        """
        returns True if the handle exists in the current Event database.
        """
        return self.db.has_event_handle(handle)

    def has_source_handle(self, handle):
        """
        returns True if the handle exists in the current Source database.
        """
        return self.db.has_source_handle(handle)

    def has_place_handle(self, handle):
        """
        returns True if the handle exists in the current Place database.
        """
        return self.db.has_place_handle(handle)

    def has_family_handle(self, handle):            
        """
        returns True if the handle exists in the current Family database.
        """
        return self.db.has_family_handle(handle)

    def has_object_handle(self, handle):
        """
        returns True if the handle exists in the current MediaObjectdatabase.
        """
        return self.dbhas_object_handle(handle)

    def has_repository_handle(self, handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return self.db.has_repository_handle(handle)

    def has_note_handle(self, handle):
        """
        returns True if the handle exists in the current Note database.
        """
        return self.db.has_note_handle(handle)

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
        # This isn't done yet because it doesn't check if references are
        # private (like a SourceRef or MediaRef). It only checks if the 
        # referenced object is private.

        handle_itr = self.db.find_backlink_handles(handle, include_classes)
        for (class_name, handle) in handle_itr:
            if class_name == 'Person':
                obj = self.db.get_person_from_handle(handle)
            elif class_name == 'Family':
                obj = self.db.get_family_from_handle(handle)
            elif class_name == 'Event':
                obj = self.db.get_event_from_handle(handle)
            elif class_name == 'Source':
                obj = self.db.get_source_from_handle(handle)
            elif class_name == 'Place':
                obj = self.db.get_place_from_handle(handle)
            elif class_name == 'MediaObject':
                obj = self.db.get_object_from_handle(handle)
            elif class_name == 'Note':
                obj = self.db.get_note_from_handle(handle)
            elif class_name == 'Repository':
                obj = self.db.get_repository_from_handle(handle)
            else:
                raise NotImplementedError
            
            if obj.get_privacy() == False:
                yield (class_name,handle)
        return


def copy_media_ref_list(db,original_obj,clean_obj):
    """
    Copies media references from one object to another - excluding private 
    references and references to private objects.

    @param db: GRAMPS database to which the references belongs
    @type db: GrampsDbBase
    @param original_obj: Object that may have private references
    @type original_obj: MediaBase
    @param clean_obj: Object that will have only non-private references
    @type original_obj: MediaBase
    @returns: Nothing
    """
    for media_ref in original_obj.get_media_list():
        if media_ref.get_privacy() == False:
            handle = media_ref.get_reference_handle()
            media_object = db.get_object_from_handle(handle)
            if media_object.get_privacy() == False:
                clean_obj.add_media_reference(MediaRef(media_ref))

def copy_source_ref_list(db,original_obj,clean_obj):
    """
    Copies source references from one object to another - excluding private 
    references and references to private objects.

    @param db: GRAMPS database to which the references belongs
    @type db: GrampsDbBase
    @param original_obj: Object that may have private references
    @type original_obj: SourceBase
    @param clean_obj: Object that will have only non-private references
    @type original_obj: SourceBase
    @returns: Nothing
    """
    for ref in original_obj.get_source_references():
        if not ref.get_privacy():
            handle = ref.get_reference_handle()
            source = db.get_source_from_handle(handle)
            if source.get_privacy() == False:
                clean_obj.add_source_reference(SourceRef(ref))
                
def copy_notes(db,original_obj,clean_obj):
    """
    Copies notes from one object to another - excluding references to private
    notes.

    @param db: GRAMPS database to which the references belongs
    @type db: GrampsDbBase
    @param original_obj: Object that may have private references
    @type original_obj: NoteBase
    @param clean_obj: Object that will have only non-private references
    @type original_obj: NoteBase
    @returns: Nothing
    """     
    for note_handle in original_obj.get_note_list():
        note = db.get_note_from_handle(note_handle)
        if note.get_privacy() == False:
            clean_obj.add_note(note_handle)
            
def copy_attributes(db,original_obj,clean_obj):
    """
    Copies attributes from one object to another - excluding references to 
    private attributes.

    @param db: GRAMPS database to which the references belongs
    @type db: GrampsDbBase
    @param original_obj: Object that may have private references
    @type original_obj: AttributeBase
    @param clean_obj: Object that will have only non-private references
    @type original_obj: AttributeBase
    @returns: Nothing
    """   
    for attribute in original_obj.get_attribute_list():
        if not attribute.get_privacy():
            new_attribute = Attribute()
            new_attribute.set_type(attribute.get_type())
            new_attribute.set_value(attribute.get_value())
            copy_notes(db,attribute,new_attribute)
            copy_source_ref_list(db,attribute,new_attribute)
            clean_obj.add_attribute(new_attribute)
      
def copy_urls(db,original_obj,clean_obj):
    """
    Copies urls from one object to another - excluding references to 
    private urls.

    @param db: GRAMPS database to which the references belongs
    @type db: GrampsDbBase
    @param original_obj: Object that may have urls
    @type original_obj: UrlBase
    @param clean_obj: Object that will have only non-private urls
    @type original_obj: UrlBase
    @returns: Nothing
    """         
    for url in original_obj.get_url_list():
        if not url.get_privacy():
            clean_obj.add_url(url)
            
def copy_lds_ords(db,original_obj,clean_obj):
    """
    Copies LDS ORDs from one object to another - excluding references to 
    private LDS ORDs.

    @param db: GRAMPS database to which the references belongs
    @type db: GrampsDbBase
    @param original_obj: Object that may have LDS ORDs
    @type original_obj: LdsOrdBase
    @param clean_obj: Object that will have only non-private LDS ORDs
    @type original_obj: LdsOrdBase
    @returns: Nothing
    """         
    for lds_ord in original_obj.get_lds_ord_list():
        if lds_ord.get_privacy() == False:
           clean_obj.add_lds_ord( lds_ord )
           
def copy_addresses(db,original_obj,clean_obj):
    """
    Copies addresses from one object to another - excluding references to 
    private addresses.

    @param db: GRAMPS database to which the references belongs
    @type db: GrampsDbBase
    @param original_obj: Object that may have addresses
    @type original_obj: AddressBase
    @param clean_obj: Object that will have only non-private addresses
    @type original_obj: AddressBase
    @returns: Nothing
    """         
    for address in original_obj.get_address_list():
        if not address.get_privacy():
            clean_obj.add_address(Address(address))
            
def sanitize_name(db,name):
    """
    Creates a new Name instance based off the passed Name
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param name: source Name object that will be copied with
    privacy records removed
    @type name: Name
    @returns: 'cleansed' Name object
    @rtype: Name
    """
    new_name = Name()
    new_name.set_group_as(name.get_group_as())
    new_name.set_sort_as(name.get_sort_as())
    new_name.set_display_as(name.get_display_as())
    new_name.set_call_name(name.get_call_name())
    new_name.set_surname_prefix(name.get_surname_prefix())
    new_name.set_type(name.get_type())
    new_name.set_first_name(name.get_first_name())
    new_name.set_patronymic(name.get_patronymic())
    new_name.set_surname(name.get_surname())
    new_name.set_suffix(name.get_suffix())
    new_name.set_title(name.get_title())
    new_name.set_date_object(name.get_date_object())
    
    copy_source_ref_list(db,name,new_name)
    copy_notes(db,name,new_name)
    
    return new_name
    
def sanitize_event_ref(db,event_ref):
    """
    Creates a new EventRef instance based off the passed EventRef
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param event_ref: source EventRef object that will be copied with
    privacy records removed
    @type event_ref: EventRef
    @returns: 'cleansed' EventRef object
    @rtype: EventRef
    """
    new_ref = EventRef()
    
    new_ref.set_reference_handle(event_ref.get_reference_handle())
    new_ref.set_role(event_ref.get_role())
    copy_notes(db,event_ref,new_ref)
    copy_attributes(db,event_ref,new_ref)
    
    return new_ref

def sanitize_person(db,person):
    """
    Creates a new Person instance based off the passed Person
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: source Person object that will be copied with
    privacy records removed
    @type person: Person
    @returns: 'cleansed' Person object
    @rtype: Person
    """
    new_person = Person()

    # copy gender
    new_person.set_gender(person.get_gender())
    new_person.set_gramps_id(person.get_gramps_id())
    new_person.set_handle(person.get_handle())
    
    # copy names if not private
    name = person.get_primary_name()
    if name.get_privacy() or person.get_privacy():
        # Do this so a person always has a primary name of some sort.
        name = Name()
        name.set_surname(_('Private'))
    else:
        name = sanitize_name(db,name)
    new_person.set_primary_name(name)

    # copy Family reference list
    for handle in person.get_family_handle_list():
        family = db.get_family_from_handle(handle)
        if family.get_privacy() == False:
            new_person.add_family_handle(handle)

    # copy Family reference list
    for handle in person.get_parent_family_handle_list():
        family = db.get_family_from_handle(handle)
        if family.get_privacy() == True:
            continue
        child_ref_list = family.get_child_ref_list()
        for child_ref in child_ref_list:
            if child_ref.get_reference_handle() == person.get_handle():
                if child_ref.get_privacy() == False:
                    new_person.add_parent_family_handle(handle)
                break

    for name in person.get_alternate_names():
        if not name.get_privacy():
            new_person.add_alternate_name(sanitize_name(db,name))

    # set complete flag
    new_person.set_marker(person.get_marker())

    # copy event list
    for event_ref in person.get_event_ref_list():
        if event_ref and event_ref.get_privacy() == False:
            event = db.get_event_from_handle(event_ref.ref)
            if not event.get_privacy():
                new_person.add_event_ref(sanitize_event_ref(db,event_ref))

    # Copy birth and death after event list to maintain the order.
    # copy birth event
    event_ref = person.get_birth_ref()
    if event_ref and event_ref.get_privacy() == False:
        event = db.get_event_from_handle(event_ref.ref)
        if not event.get_privacy():
            new_person.set_birth_ref(sanitize_event_ref(db,event_ref))

    # copy death event
    event_ref = person.get_death_ref()
    if event_ref and event_ref.get_privacy() == False:
        event = db.get_event_from_handle(event_ref.ref)
        if not event.get_privacy():
            new_person.set_death_ref(sanitize_event_ref(db,event_ref))

    copy_addresses(db,person,new_person)
    copy_attributes(db,person,new_person)
    copy_source_ref_list(db,person,new_person)
    copy_urls(db,person,new_person)
    copy_media_ref_list(db,person,new_person)
    copy_lds_ords(db,person,new_person)
    copy_notes(db,person,new_person)
    
    return new_person

def sanitize_source(db,source):
    """
    Creates a new Source instance based off the passed Source
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param source: source Source object that will be copied with
    privacy records removed
    @type source: Source
    @returns: 'cleansed' Source object
    @rtype: Source
    """
    new_source = Source()
    
    new_source.set_author(source.get_author())
    new_source.set_title(source.get_title())
    new_source.set_publication_info(source.get_publication_info())
    new_source.set_abbreviation(source.get_abbreviation())
    new_source.set_gramps_id(source.get_gramps_id())
    new_source.set_handle(source.get_handle())
    new_source.set_marker(source.get_marker())
    new_source.set_data_map(source.get_data_map())
    
    for repo_ref in source.get_reporef_list():
        if not repo_ref.get_privacy():
            handle = repo_ref.get_reference_handle()
            repo = db.get_repository_from_handle(handle)
            if repo.get_privacy() == False:
                new_source.add_repo_reference(RepoRef(repo_ref))

    copy_media_ref_list(db,source,new_source)
    copy_notes(db,source,new_source)
    
    return new_source

def sanitize_media(db,media):
    """
    Creates a new MediaObject instance based off the passed Media
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param media: source Media object that will be copied with
    privacy records removed
    @type media: MediaObject
    @returns: 'cleansed' Media object
    @rtype: MediaObject
    """
    new_media = MediaObject()
    
    new_media.set_mime_type(media.get_mime_type())
    new_media.set_path(media.get_path())
    new_media.set_description(media.get_description())
    new_media.set_gramps_id(media.get_gramps_id())
    new_media.set_handle(media.get_handle())
    new_media.set_date_object(media.get_date_object())
    new_media.set_marker(media.get_marker())

    copy_source_ref_list(db,media,new_media)
    copy_attributes(db,media,new_media)
    copy_notes(db,media,new_media)
    
    return new_media

def sanitize_place(db,place):
    """
    Creates a new Place instance based off the passed Place
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param place: source Place object that will be copied with
    privacy records removed
    @type place: Place
    @returns: 'cleansed' Place object
    @rtype: Place
    """
    new_place = Place()
    
    new_place.set_title(place.get_title())
    new_place.set_gramps_id(place.get_gramps_id())
    new_place.set_handle(place.get_handle())
    new_place.set_longitude(place.get_longitude())
    new_place.set_latitude(place.get_latitude())
    new_place.set_main_location(place.get_main_location())
    new_place.set_alternate_locations(place.get_alternate_locations())
    new_place.set_marker(place.get_marker())

    copy_source_ref_list(db,place,new_place)
    copy_notes(db,place,new_place)
    copy_media_ref_list(db,place,new_place)
    copy_urls(db,place,new_place)
    
    return new_place

def sanitize_event(db,event):
    """
    Creates a new Event instance based off the passed Event
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param event: source Event object that will be copied with
    privacy records removed
    @type event: Event
    @returns: 'cleansed' Event object
    @rtype: Event
    """
    new_event = Event()
    
    new_event.set_type(event.get_type())
    new_event.set_description(event.get_description())
    new_event.set_gramps_id(event.get_gramps_id())
    new_event.set_handle(event.get_handle())
    new_event.set_date_object(event.get_date_object())
    new_event.set_marker(event.get_marker())

    copy_source_ref_list(db,event,new_event)
    copy_notes(db,event,new_event)
    copy_media_ref_list(db,event,new_event)
    copy_attributes(db,event,new_event)
    
    place_handle = event.get_place_handle()
    place = db.get_place_from_handle(place_handle)
    if place and place.get_privacy() == False:
        new_event.set_place_handle(place_handle)
    
    return new_event
            
def sanitize_family(db,family):
    """
    Creates a new Family instance based off the passed Family
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param family: source Family object that will be copied with
    privacy records removed
    @type family: Family
    @returns: 'cleansed' Family object
    @rtype: Family
    """
    new_family = Family()
    
    new_family.set_gramps_id(family.get_gramps_id())
    new_family.set_handle(family.get_handle())
    new_family.set_marker(family.get_marker())    
    new_family.set_relationship(family.get_relationship())
    
    # Copy the father handle.
    father_handle = family.get_father_handle()
    if father_handle:
        father = db.get_person_from_handle(father_handle)
        if father.get_privacy() == False:
            new_family.set_father_handle(father_handle)

    # Copy the mother handle.
    mother_handle = family.get_mother_handle()
    if mother_handle:
        mother = db.get_person_from_handle(mother_handle)
        if mother.get_privacy() == False:
            new_family.set_mother_handle(mother_handle)
        
    # Copy child references.
    for child_ref in family.get_child_ref_list():
        if child_ref.get_privacy() == True:
            continue
        child_handle = child_ref.get_reference_handle()
        child = db.get_person_from_handle(child_handle)
        if child.get_privacy() == True:
            continue
        # Copy this reference
        new_ref = ChildRef()
        new_ref.set_reference_handle(child_ref.get_reference_handle())
        new_ref.set_father_relation(child_ref.get_father_relation())
        new_ref.set_mother_relation(child_ref.get_mother_relation())
        copy_notes(db,child_ref,new_ref)
        copy_source_ref_list(db,child_ref,new_ref)
        new_family.add_child_ref(new_ref)
        
    # Copy event ref list.
    for event_ref in family.get_event_ref_list():
        if event_ref and event_ref.get_privacy() == False:
            event = db.get_event_from_handle(event_ref.ref)
            if not event.get_privacy():
                new_family.add_event_ref(sanitize_event_ref(db,event_ref))

    copy_source_ref_list(db,family,new_family)
    copy_notes(db,family,new_family)
    copy_media_ref_list(db,family,new_family)
    copy_attributes(db,family,new_family)
    copy_lds_ords(db,family,new_family)
    
    return new_family

def sanitize_repository(db,repository):
    """
    Creates a new Repository instance based off the passed Repository
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param repository: source Repsitory object that will be copied with
    privacy records removed
    @type repository: Repository
    @returns: 'cleansed' Repository object
    @rtype: Repository
    """
    new_repository = Repository()
    
    new_repository.set_type(repository.get_type())
    new_repository.set_name(repository.get_name())
    new_repository.set_gramps_id(repository.get_gramps_id())
    new_repository.set_handle(repositofy.get_handle())
    new_repository.set_marker(repository.get_marker())

    copy_notes(db,repository,new_repository)
    copy_addresses(db,repository,new_repository)
    copy_urls(db,repository,new_repository)
    
    return new_repository