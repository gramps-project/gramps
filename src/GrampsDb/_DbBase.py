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

class DbBase:
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all data marked private will be hidden from the user.
    """

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
        raise NotImplementedError

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
        raise NotImplementedError

    def get_source_from_handle(self, handle):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        raise NotImplementedError

    def get_object_from_handle(self, handle):
        """
        Finds an Object in the database from the passed gramps' ID.
        If no such Object exists, None is returned.
        """
        raise NotImplementedError

    def get_place_from_handle(self, handle):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        raise NotImplementedError

    def get_event_from_handle(self, handle):
        """
        Finds a Event in the database from the passed gramps' ID.
        If no such Event exists, None is returned.
        """
        raise NotImplementedError

    def get_family_from_handle(self, handle):
        """
        Finds a Family in the database from the passed gramps' ID.
        If no such Family exists, None is returned.
        """
        raise NotImplementedError

    def get_repository_from_handle(self, handle):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        raise NotImplementedError

    def get_note_from_handle(self, handle):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def get_family_from_gramps_id(self, val):
        """
        Finds a Family in the database from the passed GRAMPS ID.
        If no such Family exists, None is returned.
        """
        raise NotImplementedError

    def get_event_from_gramps_id(self, val):
        """
        Finds an Event in the database from the passed GRAMPS ID.
        If no such Event exists, None is returned.
        """
        raise NotImplementedError

    def get_place_from_gramps_id(self, val):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        raise NotImplementedError

    def get_source_from_gramps_id(self, val):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        raise NotImplementedError

    def get_object_from_gramps_id(self, val):
        """
        Finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, None is returned.
        """
        raise NotImplementedError

    def get_repository_from_gramps_id(self, val):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        raise NotImplementedError

    def get_note_from_gramps_id(self, val):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def get_name_group_keys(self):
        """
        Returns the defined names that have been assigned to a default grouping
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def get_number_of_families(self):
        """
        Returns the number of families currently in the databse.
        """
        raise NotImplementedError

    def get_number_of_events(self):
        """
        Returns the number of events currently in the databse.
        """
        raise NotImplementedError

    def get_number_of_places(self):
        """
        Returns the number of places currently in the databse.
        """
        raise NotImplementedError

    def get_number_of_sources(self):
        """
        Returns the number of sources currently in the databse.
        """
        raise NotImplementedError

    def get_number_of_media_objects(self):
        """
        Returns the number of media objects currently in the databse.
        """
        raise NotImplementedError

    def get_number_of_repositories(self):
        """
        Returns the number of source repositories currently in the databse.
        """
        raise NotImplementedError

    def get_number_of_notes(self):
        """
        Returns the number of notes currently in the databse.
        """
        raise NotImplementedError

    def get_person_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each Person in
        the database. If sort_handles is True, the list is sorted by surnames
        """
        raise NotImplementedError

    def get_place_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each Place in
        the database. If sort_handles is True, the list is sorted by
        Place title.
        """
        raise NotImplementedError

    def get_source_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each Source in
        the database. If sort_handles is True, the list is sorted by
        Source title.
        """
        raise NotImplementedError

    def get_media_object_handles(self, sort_handles=True):
        """
        Returns a list of database handles, one handle for each MediaObject in
        the database. If sort_handles is True, the list is sorted by title.
        """
        raise NotImplementedError

    def get_event_handles(self):
        """
        Returns a list of database handles, one handle for each Event in
        the database. 
        """
        raise NotImplementedError

    def get_family_handles(self):
        """
        Returns a list of database handles, one handle for each Family in
        the database.
        """
        raise NotImplementedError

    def get_repository_handles(self):
        """
        Returns a list of database handles, one handle for each Repository in
        the database.
        """
        raise NotImplementedError

    def get_note_handles(self):
        """
        Returns a list of database handles, one handle for each Note in
        the database.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def get_default_handle(self):
        """returns the default Person of the database"""
        raise NotImplementedError

    def get_save_path(self):
        """returns the save path of the file, or "" if one does not exist"""
        raise NotImplementedError

    def set_save_path(self, path):
        """sets the save path for the database"""
        raise NotImplementedError

    def get_person_event_types(self):
        """returns a list of all Event types assocated with Person
        instances in the database"""
        raise NotImplementedError

    def get_person_attribute_types(self):
        """returns a list of all Attribute types assocated with Person
        instances in the database"""
        raise NotImplementedError

    def get_family_attribute_types(self):
        """returns a list of all Attribute types assocated with Family
        instances in the database"""
        raise NotImplementedError

    def get_family_event_types(self):
        """returns a list of all Event types assocated with Family
        instances in the database"""
        raise NotImplementedError

    def get_marker_types(self):
        """return a list of all marker types available in the database"""
        raise NotImplementedError
        
    def get_media_attribute_types(self):
        """returns a list of all Attribute types assocated with Media
        and MediaRef instances in the database"""
        raise NotImplementedError

    def get_family_relation_types(self):
        """returns a list of all relationship types assocated with Family
        instances in the database"""
        raise NotImplementedError

    def get_child_reference_types(self):
        """returns a list of all child reference types assocated with Family
        instances in the database"""
        raise NotImplementedError

    def get_event_roles(self):
        """returns a list of all custom event role names assocated with Event
        instances in the database"""
        raise NotImplementedError

    def get_name_types(self):
        """returns a list of all custom names types assocated with Person
        instances in the database"""
        raise NotImplementedError

    def get_repository_types(self):
        """returns a list of all custom repository types assocated with
        Repository instances in the database"""
        raise NotImplementedError

    def get_note_types(self):
        """returns a list of all custom note types assocated with
        Note instances in the database"""
        raise NotImplementedError

    def get_source_media_types(self):
        """returns a list of all custom source media types assocated with
        Source instances in the database"""
        raise NotImplementedError

    def get_url_types(self):
        """returns a list of all custom names types assocated with Url
        instances in the database"""
        raise NotImplementedError

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
        raise NotImplementedError

    def get_raw_family_data(self, handle):
        raise NotImplementedError

    def get_raw_object_data(self, handle):
        raise NotImplementedError

    def get_raw_place_data(self, handle):
        raise NotImplementedError

    def get_raw_event_data(self, handle):
        raise NotImplementedError

    def get_raw_source_data(self, handle):
        raise NotImplementedError

    def get_raw_repository_data(self, handle):
        raise NotImplementedError

    def get_raw_note_data(self, handle):
        raise NotImplementedError

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
