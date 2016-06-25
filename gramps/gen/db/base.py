#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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

"""
Base class for the Gramps databases. All database interfaces should inherit
from this class.
"""

#-------------------------------------------------------------------------
#
# Python libraries
#
#-------------------------------------------------------------------------
import re
import time
from operator import itemgetter
import logging

#-------------------------------------------------------------------------
#
# Gramps libraries
#
#-------------------------------------------------------------------------
from ..db.dbconst import DBLOGNAME
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from ..lib.childreftype import ChildRefType
from ..lib.childref import ChildRef
from .txn import DbTxn
from .exceptions import DbTransactionCancel

_LOG = logging.getLogger(DBLOGNAME)

def eval_order_by(order_by, obj, db):
    """
    Given a list of [[field, DIRECTION], ...]
    return the list of values of the fields
    """
    values = []
    for (field, direction) in order_by:
        values.append(obj.get_field(field, db, ignore_errors=True))
    return values

def sort_objects(objects, order_by, db):
    """
    Python-based sorting.
    """
    # first build sort order:
    sorted_items = []
    map_items = {}
    for obj in objects:
        # just use values and handle to keep small:
        sorted_items.append((eval_order_by(order_by, obj, db), obj.handle))
        map_items[obj.handle] = obj
    # next we sort by fields and direction
    pos = len(order_by) - 1
    for (field, order) in reversed(order_by): # sort the lasts parts first
        sorted_items.sort(key=itemgetter(pos), reverse=(order=="DESC"))
        pos -= 1
    for (order_by_values, handle) in sorted_items:
        yield map_items[handle]

#-------------------------------------------------------------------------
#
# Gramps libraries
#
#-------------------------------------------------------------------------

class DbReadBase:
    """
    Gramps database object. This object is a base class for all
    database interfaces.  All methods raise NotImplementedError
    and must be implemented in the derived class as required.
    """

    def __init__(self):
        """
        Create a new DbReadBase instance.

        A new DbReadBase class should never be directly created. Only classes
        derived from this class should be created.
        """
        self.basedb = self
        self.__feature = {} # {"feature": VALUE, ...}

    def get_table_func(self, table=None, func=None):
        """
        Base implementation of get_table_func.
        """
        return None

    def get_feature(self, feature):
        """
        Databases can implement certain features or not. The default is
        None, unless otherwise explicitly stated.
        """
        return self.__feature.get(feature, None) # can also be explicitly None

    def set_feature(self, feature, value):
        """
        Databases can implement certain features.
        """
        self.__feature[feature] = value

    def close(self):
        """
        Close the specified database.
        """
        raise NotImplementedError

    def db_has_bm_changes(self):
        """
        Return whethere there were bookmark changes during the session.
        """
        raise NotImplementedError

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.

        Returns an iterator over a list of (class_name, handle) tuples.

        :param handle: handle of the object to search for.
        :type handle: database handle
        :param include_classes: list of class names to include in the results.
            Default is None which includes all classes.
        :type include_classes: list of class names

        This default implementation does a sequential scan through all
        the primary object databases and is very slow. Backends can
        override this method to provide much faster implementations that
        make use of additional capabilities of the backend.

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use::

            result_list = list(find_backlink_handles(handle))
        """
        raise NotImplementedError

    def find_initial_person(self):
        """
        Returns first person in the database
        """
        raise NotImplementedError

    def find_next_event_gramps_id(self):
        """
        Return the next available Gramps ID for a Event object based off the
        event ID prefix.
        """
        raise NotImplementedError

    def find_next_family_gramps_id(self):
        """
        Return the next available Gramps ID for a Family object based off the
        family ID prefix.
        """
        raise NotImplementedError

    def find_next_note_gramps_id(self):
        """
        Return the next available Gramps ID for a Note object based off the
        note ID prefix.
        """
        raise NotImplementedError

    def find_next_media_gramps_id(self):
        """
        Return the next available Gramps ID for a Media object based
        off the media object ID prefix.
        """
        raise NotImplementedError

    def find_next_person_gramps_id(self):
        """
        Return the next available Gramps ID for a Person object based off the
        person ID prefix.
        """
        raise NotImplementedError

    def find_next_place_gramps_id(self):
        """
        Return the next available Gramps ID for a Place object based off the
        place ID prefix.
        """
        raise NotImplementedError

    def find_next_repository_gramps_id(self):
        """
        Return the next available Gramps ID for a Repository object based
        off the repository ID prefix.
        """
        raise NotImplementedError

    def find_next_source_gramps_id(self):
        """
        Return the next available Gramps ID for a Source object based off the
        source ID prefix.
        """
        raise NotImplementedError

    def get_bookmarks(self):
        """
        Return the list of Person handles in the bookmarks.
        """
        raise NotImplementedError

    def get_child_reference_types(self):
        """
        Return a list of all child reference types associated with Family
        instances in the database.
        """
        raise NotImplementedError

    def get_default_handle(self):
        """
        Return the default Person of the database.
        """
        raise NotImplementedError

    def get_default_person(self):
        """
        Return the default Person of the database.
        """
        raise NotImplementedError

    def get_event_bookmarks(self):
        """
        Return the list of Event handles in the bookmarks.
        """
        raise NotImplementedError

    def get_event_cursor(self):
        """
        Return a reference to a cursor over Family objects
        """
        raise NotImplementedError

    def get_event_from_gramps_id(self, val):
        """
        Find an Event in the database from the passed Gramps ID.

        If no such Event exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_event_from_handle(self, handle):
        """
        Find a Event in the database from the passed Gramps ID.

        If no such Event exists, a HandleError is raised.
        """
        raise NotImplementedError

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in the
        database.
        """
        raise NotImplementedError

    def get_event_roles(self):
        """
        Return a list of all custom event role names associated with Event
        instances in the database.
        """
        raise NotImplementedError

    def get_event_attribute_types(self):
        """
        Return a list of all Attribute types assocated with Event instances
        in the database.
        """
        raise NotImplementedError

    def get_event_types(self):
        """
        Return a list of all event types in the database.
        """
        raise NotImplementedError

    def get_family_attribute_types(self):
        """
        Return a list of all Attribute types associated with Family instances
        in the database.
        """
        raise NotImplementedError

    def get_family_bookmarks(self):
        """
        Return the list of Family handles in the bookmarks.
        """
        raise NotImplementedError

    def get_family_cursor(self):
        """
        Return a reference to a cursor over Family objects
        """
        raise NotImplementedError

    def get_family_event_types(self):
        """
        Deprecated:  Use get_event_types
        """
        raise NotImplementedError

    def get_family_from_gramps_id(self, val):
        """
        Find a Family in the database from the passed Gramps ID.

        If no such Family exists, None is returned.
        Need to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_family_from_handle(self, handle):
        """
        Find a Family in the database from the passed Gramps ID.

        If no such Family exists, a HandleError is raised.
        """
        raise NotImplementedError

    def get_family_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Family in
        the database.

        If sort_handles is True, the list is sorted by surnames.
        """
        raise NotImplementedError

    def get_family_relation_types(self):
        """
        Return a list of all relationship types associated with Family
        instances in the database.
        """
        raise NotImplementedError

    def get_gramps_ids(self, obj_key):
        """
        Returns all the keys from a table given a table name
        """
        raise NotImplementedError

    def get_media_attribute_types(self):
        """
        Return a list of all Attribute types associated with Media and MediaRef
        instances in the database.
        """
        raise NotImplementedError

    def get_media_bookmarks(self):
        """
        Return the list of Media handles in the bookmarks.
        """
        raise NotImplementedError

    def get_media_cursor(self):
        """
        Return a reference to a cursor over Media objects
        """
        raise NotImplementedError

    def get_media_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Media in
        the database.

        If sort_handles is True, the list is sorted by title.
        """
        raise NotImplementedError

    def get_mediapath(self):
        """
        Return the default media path of the database.
        """
        raise NotImplementedError

    def get_name_group_keys(self):
        """
        Return the defined names that have been assigned to a default grouping.
        """
        raise NotImplementedError

    def get_name_group_mapping(self, surname):
        """
        Return the default grouping name for a surname.
        """
        raise NotImplementedError

    def get_name_types(self):
        """
        Return a list of all custom names types associated with Person
        instances in the database.
        """
        raise NotImplementedError

    def get_origin_types(self):
        """
        Return a list of all custom origin types associated with Person/Surname
        instances in the database.
        """
        raise NotImplementedError

    def get_note_bookmarks(self):
        """
        Return the list of Note handles in the bookmarks.
        """
        raise NotImplementedError

    def get_note_cursor(self):
        """
        Return a reference to a cursor over Note objects
        """
        raise NotImplementedError

    def get_note_from_gramps_id(self, val):
        """
        Find a Note in the database from the passed Gramps ID.

        If no such Note exists, None is returned.
        Needs to be overridden by the derived classderri.
        """
        raise NotImplementedError

    def get_note_from_handle(self, handle):
        """
        Find a Note in the database from the passed Gramps ID.

        If no such Note exists, a HandleError is raised.
        """
        raise NotImplementedError

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in the
        database.
        """
        raise NotImplementedError

    def get_note_types(self):
        """
        Return a list of all custom note types associated with Note instances
        in the database.
        """
        raise NotImplementedError

    def get_number_of_events(self):
        """
        Return the number of events currently in the database.
        """
        raise NotImplementedError

    def get_number_of_families(self):
        """
        Return the number of families currently in the database.
        """
        raise NotImplementedError

    def get_number_of_media(self):
        """
        Return the number of media objects currently in the database.
        """
        raise NotImplementedError

    def get_number_of_notes(self):
        """
        Return the number of notes currently in the database.
        """
        raise NotImplementedError

    def get_number_of_people(self):
        """
        Return the number of people currently in the database.
        """
        raise NotImplementedError

    def get_number_of_places(self):
        """
        Return the number of places currently in the database.
        """
        raise NotImplementedError

    def get_number_of_repositories(self):
        """
        Return the number of source repositories currently in the database.
        """
        raise NotImplementedError

    def get_number_of_sources(self):
        """
        Return the number of sources currently in the database.
        """
        raise NotImplementedError

    def get_number_of_tags(self):
        """
        Return the number of tags currently in the database.
        """
        raise NotImplementedError

    def get_media_from_gramps_id(self, val):
        """
        Find a Media in the database from the passed Gramps ID.

        If no such Media exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_media_from_handle(self, handle):
        """
        Find an Object in the database from the passed Gramps ID.

        If no such Object exists, a HandleError is raised.
        """
        raise NotImplementedError

    def get_person_attribute_types(self):
        """
        Return a list of all Attribute types associated with Person instances
        in the database.
        """
        raise NotImplementedError

    def get_person_cursor(self):
        """
        Return a reference to a cursor over Person objects
        """
        raise NotImplementedError

    def get_person_event_types(self):
        """
        Deprecated:  Use get_event_types
        """
        raise NotImplementedError

    def get_person_from_gramps_id(self, val):
        """
        Find a Person in the database from the passed Gramps ID.

        If no such Person exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_person_from_handle(self, handle):
        """
        Find a Person in the database from the passed Gramps ID.

        If no such Person exists, a HandleError is raised.
        """
        raise NotImplementedError

    def get_person_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Person in
        the database.

        If sort_handles is True, the list is sorted by surnames.
        """
        raise NotImplementedError

    def get_source_attribute_types(self):
        """
        Return a list of all Attribute types associated with Source/Citation
        instances in the database.
        """
        raise NotImplementedError

    def get_place_bookmarks(self):
        """
        Return the list of Place handles in the bookmarks.
        """
        raise NotImplementedError

    def get_place_cursor(self):
        """
        Return a reference to a cursor over Place objects
        """
        raise NotImplementedError

    def get_place_from_gramps_id(self, val):
        """
        Find a Place in the database from the passed Gramps ID.

        If no such Place exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_place_from_handle(self, handle):
        """
        Find a Place in the database from the passed Gramps ID.

        If no such Place exists, a HandleError is raised.
        """
        raise NotImplementedError

    def get_place_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Place in
        the database.

        If sort_handles is True, the list is sorted by Place title.
        """
        raise NotImplementedError

    def get_raw_event_data(self, handle):
        """
        Return raw (serialized and pickled) Event object from handle
        """
        raise NotImplementedError

    def get_raw_family_data(self, handle):
        """
        Return raw (serialized and pickled) Family object from handle
        """
        raise NotImplementedError

    def get_raw_note_data(self, handle):
        """
        Return raw (serialized and pickled) Note object from handle
        """
        raise NotImplementedError

    def get_raw_media_data(self, handle):
        """
        Return raw (serialized and pickled) Family object from handle
        """
        raise NotImplementedError

    def get_raw_person_data(self, handle):
        """
        Return raw (serialized and pickled) Person object from handle
        """
        raise NotImplementedError

    def get_raw_place_data(self, handle):
        """
        Return raw (serialized and pickled) Place object from handle
        """
        raise NotImplementedError

    def get_raw_repository_data(self, handle):
        """
        Return raw (serialized and pickled) Repository object from handle
        """
        raise NotImplementedError

    def get_raw_source_data(self, handle):
        """
        Return raw (serialized and pickled) Source object from handle
        """
        raise NotImplementedError

    def get_raw_citation_data(self, handle):
        """
        Return raw (serialized and pickled) Citation object from handle
        """
        raise NotImplementedError

    def get_raw_tag_data(self, handle):
        """
        Return raw (serialized and pickled) Tag object from handle
        """
        raise NotImplementedError

    def get_repo_bookmarks(self):
        """
        Return the list of Repository handles in the bookmarks.
        """
        raise NotImplementedError

    def get_repository_cursor(self):
        """
        Return a reference to a cursor over Repository objects
        """
        raise NotImplementedError

    def get_repository_from_gramps_id(self, val):
        """
        Find a Repository in the database from the passed Gramps ID.

        If no such Repository exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_repository_from_handle(self, handle):
        """
        Find a Repository in the database from the passed Gramps ID.

        If no such Repository exists, a HandleError is raised.
        """
        raise NotImplementedError

    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository in
        the database.
        """
        raise NotImplementedError

    def get_repository_types(self):
        """
        Return a list of all custom repository types associated with Repository
        instances in the database.
        """
        raise NotImplementedError

    def get_researcher(self):
        """
        Return the Researcher instance, providing information about the owner
        of the database.
        """
        raise NotImplementedError

    def get_save_path(self):
        """
        Return the save path of the file, or "" if one does not exist.
        """
        raise NotImplementedError

    def get_source_bookmarks(self):
        """
        Return the list of Source handles in the bookmarks.
        """
        raise NotImplementedError

    def get_source_cursor(self):
        """
        Return a reference to a cursor over Source objects
        """
        raise NotImplementedError

    def get_source_from_gramps_id(self, val):
        """
        Find a Source in the database from the passed Gramps ID.

        If no such Source exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_source_from_handle(self, handle):
        """
        Find a Source in the database from the passed Gramps ID.

        If no such Source exists, a HandleError is raised.
        """
        raise NotImplementedError

    def get_source_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Source in
        the database.

        If sort_handles is True, the list is sorted by Source title.
        """
        raise NotImplementedError

    def get_source_media_types(self):
        """
        Return a list of all custom source media types associated with Source
        instances in the database.
        """
        raise NotImplementedError

    def get_citation_bookmarks(self):
        """
        Return the list of Citation handles in the bookmarks.
        """
        raise NotImplementedError

    def get_citation_cursor(self):
        """
        Return a reference to a cursor over Citation objects
        """
        raise NotImplementedError

    def get_citation_from_gramps_id(self, val):
        """
        Find a Citation in the database from the passed Gramps ID.

        If no such Citation exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_citation_from_handle(self, handle):
        """
        Find a Citation in the database from the passed Gramps ID.

        If no such Citation exists, a HandleError is raised.
        """
        raise NotImplementedError

    def get_citation_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Citation in
        the database.

        If sort_handles is True, the list is sorted by Citation title.
        """
        raise NotImplementedError

    def get_surname_list(self):
        """
        Return the list of locale-sorted surnames contained in the database.
        """
        raise NotImplementedError

    def get_tag_cursor(self):
        """
        Return a reference to a cursor over Tag objects
        """
        raise NotImplementedError

    def get_tag_from_handle(self, handle):
        """
        Find a Tag in the database from the passed handle.

        If no such Tag exists, a HandleError is raised.
        """
        raise NotImplementedError

    def get_tag_from_name(self, val):
        """
        Find a Tag in the database from the passed Tag name.

        If no such Tag exists, None is returned.
        Needs to be overridden by the derived class.
        """
        raise NotImplementedError

    def get_tag_handles(self, sort_handles=False):
        """
        Return a list of database handles, one handle for each Tag in
        the database.

        If sort_handles is True, the list is sorted by Tag name.
        """
        raise NotImplementedError

    def get_url_types(self):
        """
        Return a list of all custom names types associated with Url instances
        in the database.
        """
        raise NotImplementedError

    def get_place_types(self):
        """
        Return a list of all custom place types assocated with Place instances
        in the database.
        """
        raise NotImplementedError

    def has_event_handle(self, handle):
        """
        Return True if the handle exists in the current Event database.
        """
        raise NotImplementedError

    def has_family_handle(self, handle):
        """
        Return True if the handle exists in the current Family database.
        """
        raise NotImplementedError

    def has_gramps_id(self, obj_key, gramps_id):
        """
        Returns True if the key exists in table given a table name

        Not used in current codebase
        """
        raise NotImplementedError

    def has_name_group_key(self, name):
        """
        Return if a key exists in the name_group table.
        """
        raise NotImplementedError

    def has_note_handle(self, handle):
        """
        Return True if the handle exists in the current Note database.
        """
        raise NotImplementedError

    def has_media_handle(self, handle):
        """
        Return True if the handle exists in the current Mediadatabase.
        """
        raise NotImplementedError

    def has_person_handle(self, handle):
        """
        Return True if the handle exists in the current Person database.
        """
        raise NotImplementedError

    def has_place_handle(self, handle):
        """
        Return True if the handle exists in the current Place database.
        """
        raise NotImplementedError

    def has_repository_handle(self, handle):
        """
        Return True if the handle exists in the current Repository database.
        """
        raise NotImplementedError

    def has_source_handle(self, handle):
        """
        Return True if the handle exists in the current Source database.
        """
        raise NotImplementedError

    def has_tag_handle(self, handle):
        """
        Return True if the handle exists in the current Tag database.
        """
        raise NotImplementedError

    def is_open(self):
        """
        Return True if the database has been opened.
        """
        raise NotImplementedError

    def iter_citations(self, order_by=None):
        """
        Return an iterator over objects for Citations in the database
        """
        raise NotImplementedError

    def iter_event_handles(self):
        """
        Return an iterator over handles for Events in the database
        """
        raise NotImplementedError

    def iter_events(self, order_by=None):
        """
        Return an iterator over objects for Events in the database
        """
        raise NotImplementedError

    def iter_families(self, order_by=None):
        """
        Return an iterator over objects for Families in the database
        """
        raise NotImplementedError

    def iter_family_handles(self):
        """
        Return an iterator over handles for Families in the database
        """
        raise NotImplementedError

    def iter_media_handles(self):
        """
        Return an iterator over handles for Media in the database
        """
        raise NotImplementedError

    def iter_media(self, order_by=None):
        """
        Return an iterator over objects for Medias in the database
        """
        raise NotImplementedError

    def iter_note_handles(self):
        """
        Return an iterator over handles for Notes in the database
        """
        raise NotImplementedError

    def iter_notes(self, order_by=None):
        """
        Return an iterator over objects for Notes in the database
        """
        raise NotImplementedError

    def iter_people(self, order_by=None):
        """
        Return an iterator over objects for Persons in the database
        """
        raise NotImplementedError

    def iter_person_handles(self):
        """
        Return an iterator over handles for Persons in the database
        """
        raise NotImplementedError

    def iter_place_handles(self):
        """
        Return an iterator over handles for Places in the database
        """
        raise NotImplementedError

    def iter_places(self, order_by=None):
        """
        Return an iterator over objects for Places in the database
        """
        raise NotImplementedError

    def iter_repositories(self, order_by=None):
        """
        Return an iterator over objects for Repositories in the database
        """
        raise NotImplementedError

    def iter_repository_handles(self):
        """
        Return an iterator over handles for Repositories in the database
        """
        raise NotImplementedError

    def iter_source_handles(self):
        """
        Return an iterator over handles for Sources in the database
        """
        raise NotImplementedError

    def iter_sources(self, order_by=None):
        """
        Return an iterator over objects for Sources in the database
        """
        raise NotImplementedError

    def iter_tag_handles(self):
        """
        Return an iterator over handles for Tags in the database
        """
        raise NotImplementedError

    def iter_tags(self, order_by=None):
        """
        Return an iterator over objects for Tags in the database
        """
        raise NotImplementedError

    def load(self, name, callback, mode=None, force_schema_upgrade=False,
             force_bsddb_upgrade=False):
        """
        Open the specified database.
        """
        raise NotImplementedError

    def report_bm_change(self):
        """
        Add 1 to the number of bookmark changes during this session.
        """
        raise NotImplementedError

    def request_rebuild(self):
        """
        Notify clients that the data has changed significantly, and that all
        internal data dependent on the database should be rebuilt.
        Note that all rebuild signals on all objects are emitted at the same
        time. It is correct to assume that this is always the case.

        .. todo:: it might be better to replace these rebuild signals by one
                  single database-rebuild signal.
        """
        raise NotImplementedError

    def version_supported(self):
        """
        Return True when the file has a supported version.
        """
        raise NotImplementedError

    def set_event_id_prefix(self, val):
        """
        Set the naming template for Gramps Event ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as E%d or E%04d.
        """
        raise NotImplementedError

    def set_family_id_prefix(self, val):
        """
        Set the naming template for Gramps Family ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as F%d
        or F%04d.
        """
        raise NotImplementedError

    def set_note_id_prefix(self, val):
        """
        Set the naming template for Gramps Note ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as N%d or N%04d.
        """
        raise NotImplementedError

    def set_media_id_prefix(self, val):
        """
        Set the naming template for Gramps Media ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as O%d or O%04d.
        """
        raise NotImplementedError

    def set_person_id_prefix(self, val):
        """
        Set the naming template for Gramps Person ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as I%d or I%04d.
        """
        raise NotImplementedError

    def set_place_id_prefix(self, val):
        """
        Set the naming template for Gramps Place ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as P%d or P%04d.
        """
        raise NotImplementedError

    def set_prefixes(self, person, media, family, source, citation,
                     place, event, repository, note):
        """
        Set the prefixes for the gramps ids for all gramps objects
        """
        raise NotImplementedError

    def set_repository_id_prefix(self, val):
        """
        Set the naming template for Gramps Repository ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as R%d or R%04d.
        """
        raise NotImplementedError

    def set_source_id_prefix(self, val):
        """
        Set the naming template for Gramps Source ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as S%d or S%04d.
        """
        raise NotImplementedError

    def set_mediapath(self, path):
        """
        Set the default media path for database, path should be utf-8.
        """
        raise NotImplementedError

    def set_researcher(self, owner):
        """
        Set the information about the owner of the database.
        """
        raise NotImplementedError

    def set_save_path(self, path):
        """
        Set the save path for the database.
        """
        raise NotImplementedError

    def get_dbid(self):
        """
        A unique ID for this database on this computer.
        """
        raise NotImplementedError

    def get_dbname(self):
        """
        A name for this database on this computer.
        """
        raise NotImplementedError

    def _select(self, table, fields=None, start=0, limit=-1,
                where=None, order_by=None):
        """
        Default implementation of a select for those databases
        that don't support SQL. Returns a list of dicts, total,
        and time.

        table - Person, Family, etc.
        fields - used by object.get_field()
        start - position to start
        limit - count to get; -1 for all
        where - (field, SQL string_operator, value) |
                 ["AND", [where, where, ...]]      |
                 ["OR",  [where, where, ...]]      |
                 ["NOT",  where]
        order_by - [[fieldname, "ASC" | "DESC"], ...]
        """
        def compare(v, op, value):
            """
            Compare values in a SQL-like way
            """
            if isinstance(v, (list, tuple)) and len(v) > 0: # join, or multi-values
                # If any is true:
                for item in v:
                    if compare(item, op, value):
                        return True
                return False
            if op in ["=", "=="]:
                matched = v == value
            elif op == ">":
                matched = v > value
            elif op == ">=":
                matched = v >= value
            elif op == "<":
                matched = v < value
            elif op == "<=":
                matched = v <= value
            elif op == "IN":
                matched = v in value
            elif op == "IS":
                matched = v is value
            elif op == "IS NOT":
                matched = v is not value
            elif op == "IS NULL":
                matched = v is None
            elif op == "IS NOT NULL":
                matched = v is not None
            elif op == "BETWEEN":
                matched = value[0] <= v <= value[1]
            elif op in ["<>", "!="]:
                matched = v != value
            elif op == "LIKE":
                if value and v:
                    value = value.replace("%", "(.*)").replace("_", ".")
                    ## FIXME: allow a case-insensitive version
                    matched = re.match("^" + value + "$", v, re.MULTILINE)
                else:
                    matched = False
            elif op == "REGEXP":
                if value and v:
                    matched = re.search(value, v, re.MULTILINE) is not None
                else:
                    matched = False
            else:
                raise Exception("invalid select operator: '%s'" % op)
            return True if matched else False

        def evaluate_values(condition, item, db, table, env):
            """
            Evaluates the names in all conditions.
            """
            if len(condition) == 2: # ["AND" [...]] | ["OR" [...]] | ["NOT" expr]
                connector, exprs = condition
                if connector in ["AND", "OR"]:
                    for expr in exprs:
                        evaluate_values(expr, item, db, table, env)
                else: # "NOT"
                    evaluate_values(exprs, item, db, table, env)
            elif len(condition) == 3: # (name, op, value)
                (name, op, value) = condition
                # just the ones we need for where
                hname = self._hash_name(table, name)
                if hname not in env:
                    value = item.get_field(name, db, ignore_errors=True)
                    env[hname] = value

        def evaluate_truth(condition, item, db, table, env):
            if len(condition) == 2: # ["AND"|"OR" [...]]
                connector, exprs = condition
                if connector == "AND": # all must be true
                    for expr in exprs:
                        if not evaluate_truth(expr, item, db, table, env):
                            return False
                    return True
                elif connector == "OR": # any will return true
                    for expr in exprs:
                        if evaluate_truth(expr, item, db, table, env):
                            return True
                    return False
                elif connector == "NOT": # return not of single value
                    return not evaluate_truth(exprs, item, db, table, env)
                else:
                    raise Exception("No such connector: '%s'" % connector)
            elif len(condition) == 3: # (name, op, value)
                (name, op, value) = condition
                v = env.get(self._hash_name(table, name))
                return compare(v, op, value)

        # Fields is None or list, maybe containing "*":
        if fields is None:
            pass # ok
        elif not isinstance(fields, (list, tuple)):
            raise Exception("fields must be a list/tuple of field names")
        elif "*" in fields:
            fields.remove("*")
            fields.extend(self.get_table_func(table,"class_func").get_schema().keys())
        get_count_only = (fields is not None and fields[0] == "count(1)")
        position = 0
        selected = 0
        if get_count_only:
            if where or limit != -1 or start != 0:
                # no need to order for a count
                data = self.get_table_func(table,"iter_func")()
            else:
                yield self.get_table_func(table,"count_func")()
        else:
            data = self.get_table_func(table, "iter_func")(order_by=order_by)
        if where:
            for item in data:
                # Go through all fliters and evaluate the fields:
                env = {}
                evaluate_values(where, item, self, table, env)
                matched = evaluate_truth(where, item, self, table, env)
                if matched:
                    if ((selected < limit) or (limit == -1)) and start <= position:
                        selected += 1
                        if not get_count_only:
                            if fields:
                                row = {}
                                for field in fields:
                                    value = item.get_field(field, self, ignore_errors=True)
                                    row[field.replace("__", ".")] = value
                                yield row
                            else:
                                yield item
                    position += 1
            if get_count_only:
                yield selected
        else: # no where
            for item in data:
                if position >= start:
                    if ((selected >= limit) and (limit != -1)):
                        break
                    selected += 1
                    if not get_count_only:
                        if fields:
                            row = {}
                            for field in fields:
                                value = item.get_field(field, self, ignore_errors=True)
                                row[field.replace("__", ".")] = value
                            yield row
                        else:
                            yield item
                position += 1
            if get_count_only:
                yield selected

    def _hash_name(self, table, name):
        """
        Used in SQL functions to eval expressions involving selected
        data.
        """
        name = self.get_table_func(table,"class_func").get_field_alias(name)
        return name.replace(".", "__")

    Person = property(lambda self: QuerySet(self, "Person"))
    Family = property(lambda self: QuerySet(self, "Family"))
    Note = property(lambda self: QuerySet(self, "Note"))
    Citation = property(lambda self: QuerySet(self, "Citation"))
    Source = property(lambda self: QuerySet(self, "Source"))
    Repository = property(lambda self: QuerySet(self, "Repository"))
    Place = property(lambda self: QuerySet(self, "Place"))
    Event = property(lambda self: QuerySet(self, "Event"))
    Tag = property(lambda self: QuerySet(self, "Tag"))
    Media = property(lambda self: QuerySet(self, "Media"))

class DbWriteBase(DbReadBase):
    """
    Gramps database object. This object is a base class for all
    database interfaces.  All methods raise NotImplementedError
    and must be implemented in the derived class as required.
    """

    def __init__(self):
        """
        Create a new DbWriteBase instance.

        A new DbWriteBase class should never be directly created. Only classes
        derived from this class should be created.
        """
        DbReadBase.__init__(self)

    def add_event(self, event, transaction, set_gid=True):
        """
        Add an Event to the database, assigning internal IDs if they have
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

    def add_note(self, obj, transaction, set_gid=True):
        """
        Add a Note to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_media(self, obj, transaction, set_gid=True):
        """
        Add a Media to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_person(self, person, transaction, set_gid=True):
        """
        Add a Person to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_place(self, place, transaction, set_gid=True):
        """
        Add a Place to the database, assigning internal IDs if they have
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

    def add_source(self, source, transaction, set_gid=True):
        """
        Add a Source to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_tag(self, tag, transaction):
        """
        Add a Tag to the database, assigning a handle if it has not already
        been defined.
        """
        raise NotImplementedError

    def add_to_surname_list(self, person, batch_transaction, name):
        """
        Add surname from given person to list of surnames
        """
        raise NotImplementedError

    def build_surname_list(self):
        """
        Build the list of locale-sorted surnames contained in the database.
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

    def commit_media(self, obj, transaction, change_time=None):
        """
        Commit the specified Media to the database, storing the changes
        as part of the transaction.
        """
        raise NotImplementedError

    def commit_note(self, note, transaction, change_time=None):
        """
        Commit the specified Note to the database, storing the changes as part
        of the transaction.
        """
        raise NotImplementedError

    def commit_person(self, person, transaction, change_time=None):
        """
        Commit the specified Person to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def commit_place(self, place, transaction, change_time=None):
        """
        Commit the specified Place to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def commit_repository(self, repository, transaction, change_time=None):
        """
        Commit the specified Repository to the database, storing the changes
        as part of the transaction.
        """
        raise NotImplementedError

    def commit_source(self, source, transaction, change_time=None):
        """
        Commit the specified Source to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def commit_tag(self, tag, transaction, change_time=None):
        """
        Commit the specified Tag to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def get_undodb(self):
        """
        Return the database that keeps track of Undo/Redo operations.
        """
        raise NotImplementedError

    def rebuild_secondary(self, callback):
        """
        Rebuild secondary indices
        """
        raise NotImplementedError

    def reindex_reference_map(self, callback):
        """
        Reindex all primary records in the database.
        """
        raise NotImplementedError

    def remove_event(self, handle, transaction):
        """
        Remove the Event specified by the database handle from the
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

    def remove_from_surname_list(self, person):
        """
        Check whether there are persons with the same surname left in
        the database.

        If not then we need to remove the name from the list.
        The function must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_note(self, handle, transaction):
        """
        Remove the Note specified by the database handle from the
        database, preserving the change in the passed transaction.

        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_media(self, handle, transaction):
        """
        Remove the MediaPerson specified by the database handle from the
        database, preserving the change in the passed transaction.

        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_person(self, handle, transaction):
        """
        Remove the Person specified by the database handle from the database,
        preserving the change in the passed transaction.

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

    def remove_repository(self, handle, transaction):
        """
        Remove the Repository specified by the database handle from the
        database, preserving the change in the passed transaction.

        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_source(self, handle, transaction):
        """
        Remove the Source specified by the database handle from the
        database, preserving the change in the passed transaction.

        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def remove_tag(self, handle, transaction):
        """
        Remove the Tag specified by the database handle from the
        database, preserving the change in the passed transaction.

        This method must be overridden in the derived class.
        """
        raise NotImplementedError

    def set_default_person_handle(self, handle):
        """
        Set the default Person to the passed instance.
        """
        raise NotImplementedError

    def set_name_group_mapping(self, name, group):
        """
        Set the default grouping name for a surname.

        Needs to be overridden in the derived class.
        """
        raise NotImplementedError

    def transaction_begin(self, transaction):
        """
        Prepare the database for the start of a new transaction.

        Two modes should be provided: transaction.batch=False for ordinary
        database operations that will be encapsulated in database transactions
        to make them ACID and that are added to Gramps transactions so that
        they can be undone. And transaction.batch=True for lengthy database
        operations, that benefit from a speedup by making them none ACID, and
        that can't be undone. The user is warned and is asked for permission
        before the start of such database operations.

        :param transaction: Gramps transaction ...
        :type transaction: :py:class:`.DbTxn`
        :returns: Returns the Gramps transaction.
        :rtype: :py:class:`.DbTxn`
        """
        raise NotImplementedError

    def transaction_commit(self, transaction):
        """
        Make the changes to the database final and add the content of the
        transaction to the undo database.
        """
        raise NotImplementedError

    def transaction_abort(self, transaction):
        """
        Revert the changes made to the database so far during the transaction.
        """
        raise NotImplementedError

    def write_version(self, name):
        """
        Write version number for a newly created DB.
        """
        raise NotImplementedError

    def add_child_to_family(self, family, child,
                            mrel=ChildRefType(),
                            frel=ChildRefType(),
                            trans=None):
        """
        Adds a child to a family.
        """
        cref = ChildRef()
        cref.ref = child.handle
        cref.set_father_relation(frel)
        cref.set_mother_relation(mrel)

        family.add_child_ref(cref)
        child.add_parent_family_handle(family.handle)

        if trans is None:
            with DbTxn(_('Add child to family'), self) as trans:
                self.commit_family(family, trans)
                self.commit_person(child, trans)
        else:
            self.commit_family(family, trans)
            self.commit_person(child, trans)

    def remove_child_from_family(self, person_handle, family_handle, trans=None):
        """
        Remove a person as a child of the family, deleting the family if
        it becomes empty.
        """
        if trans is None:
            with DbTxn(_("Remove child from family"), self) as trans:
                self.__remove_child_from_family(person_handle, family_handle,
                                                trans)
        else:
            self.__remove_child_from_family(person_handle, family_handle, trans)
            trans.set_description(_("Remove child from family"))

    def __remove_child_from_family(self, person_handle, family_handle, trans):
        """
        Remove a person as a child of the family, deleting the family if
        it becomes empty; trans is compulsory.
        """
        person = self.get_person_from_handle(person_handle)
        family = self.get_family_from_handle(family_handle)
        person.remove_parent_family_handle(family_handle)
        family.remove_child_handle(person_handle)

        if (not family.get_father_handle() and not family.get_mother_handle()
                and not family.get_child_ref_list()):
            self.remove_family_relationships(family_handle, trans)
        else:
            self.commit_family(family, trans)
        self.commit_person(person, trans)

    def delete_person_from_database(self, person, trans):
        """
        Deletes a person from the database, cleaning up all associated references.
        """

        # clear out the default person if the person is the default person
        if self.get_default_person() == person:
            self.set_default_person_handle(None)

        # loop through the family list
        for family_handle in person.get_family_handle_list():
            if not family_handle:
                continue

            family = self.get_family_from_handle(family_handle)

            if person.get_handle() == family.get_father_handle():
                family.set_father_handle(None)
            else:
                family.set_mother_handle(None)

            if not family.get_father_handle() and \
                    not family.get_mother_handle() and \
                    not family.get_child_ref_list():
                self.remove_family_relationships(family_handle, trans)
            else:
                self.commit_family(family, trans)

        for family_handle in person.get_parent_family_handle_list():
            if family_handle:
                family = self.get_family_from_handle(family_handle)
                family.remove_child_handle(person.get_handle())
                if not family.get_father_handle() and \
                        not family.get_mother_handle() and \
                        not family.get_child_ref_list():
                    self.remove_family_relationships(family_handle, trans)
                else:
                    self.commit_family(family, trans)

        handle = person.get_handle()

        person_list = [
            item[1] for item in
            self.find_backlink_handles(handle,['Person'])]

        for phandle in person_list:
            prsn = self.get_person_from_handle(phandle)
            prsn.remove_handle_references('Person', [handle])
            self.commit_person(prsn, trans)
        self.remove_person(handle, trans)

    def remove_family_relationships(self, family_handle, trans=None):
        """
        Remove a family and its relationships.
        """
        if trans is None:
            with DbTxn(_("Remove Family"), self) as trans:
                self.__remove_family_relationships(family_handle, trans)
        else:
            self.__remove_family_relationships(family_handle, trans)
            trans.set_description(_("Remove Family"))

    def __remove_family_relationships(self, family_handle, trans):
        """
        Remove a family and all that references it; trans is compulsory.
        """
        person_list = [item[1] for item in
                self.find_backlink_handles(family_handle, ['Person'])]
        for phandle in person_list:
            person = self.get_person_from_handle(phandle)
            if person:
                person.remove_handle_references('Family', [family_handle])
                self.commit_person(person, trans)
        self.remove_family(family_handle, trans)

    def remove_parent_from_family(self, person_handle, family_handle,
                                  trans=None):
        """
        Remove a person as either the father or mother of a family,
        deleting the family if it becomes empty.
        """
        if trans is None:
            with DbTxn('', self) as trans:
                msg = self.__remove_parent_from_family(person_handle,
                                                       family_handle, trans)
                trans.set_description(msg)
        else:
            msg = self.__remove_parent_from_family(person_handle,
                                                   family_handle, trans)
            trans.set_description(msg)

    def __remove_parent_from_family(self, person_handle, family_handle, trans):
        """
        Remove a person as either the father or mother of a family,
        deleting the family if it becomes empty; trans is compulsory.
        """
        person = self.get_person_from_handle(person_handle)
        family = self.get_family_from_handle(family_handle)

        person.remove_family_handle(family_handle)
        if family.get_father_handle() == person_handle:
            family.set_father_handle(None)
            msg = _("Remove father from family")
        elif family.get_mother_handle() == person_handle:
            msg = _("Remove mother from family")
            family.set_mother_handle(None)
        else:
            raise DbTransactionCancel("The relation between the person and "
                "the family you try to remove is not consistent, please fix "
                "that first, for example from the family editor or by running "
                "the database repair tool, before removing the family.")

        if (not family.get_father_handle() and not family.get_mother_handle()
                and not family.get_child_ref_list()):
            self.remove_family_relationships(family_handle, trans)
        else:
            self.commit_family(family, trans)
        self.commit_person(person, trans)
        return msg

    def marriage_from_eventref_list(self, eventref_list):
        """
        Get the marriage event from an eventref list.
        """
        for eventref in eventref_list:
            event = self.get_event_from_handle(eventref.ref)
            if event and event.type.is_marriage():
                return event
        return None

    def get_total(self):
        """
        Get the total of primary objects.
        """
        person_len = self.get_number_of_people()
        family_len = self.get_number_of_families()
        event_len = self.get_number_of_events()
        source_len = self.get_number_of_sources()
        place_len = self.get_number_of_places()
        repo_len = self.get_number_of_repositories()
        obj_len = self.get_number_of_media()

        return person_len + family_len + event_len + \
               place_len + source_len + obj_len + repo_len

    def set_birth_death_index(self, person):
        """
        Set the birth and death indices for a person.
        """
        birth_ref_index = -1
        death_ref_index = -1
        event_ref_list = person.get_event_ref_list()
        for index in range(len(event_ref_list)):
            ref = event_ref_list[index]
            event = self.get_event_from_handle(ref.ref)
            if (event.type.is_birth()
                and ref.role.is_primary()
                and (birth_ref_index == -1)):
                birth_ref_index = index
            elif (event.type.is_death()
                  and ref.role.is_primary()
                  and (death_ref_index == -1)):
                death_ref_index = index

        person.birth_ref_index = birth_ref_index
        person.death_ref_index = death_ref_index

    def remove_instance(self, instance, transaction):
        """
        Given the instance of an object, delete it from the database.
        """
        if instance.__class__.__name__ == "Person":
            self.remove_person(instance.handle, transaction)
        elif instance.__class__.__name__ == "Place":
            self.remove_place(instance.handle, transaction)
        elif instance.__class__.__name__ == "Event":
            self.remove_event(instance.handle, transaction)
        elif instance.__class__.__name__ == "Repository":
            self.remove_repository(instance.handle, transaction)
        elif instance.__class__.__name__ == "Citation":
            self.remove_citation(instance.handle, transaction)
        elif instance.__class__.__name__ == "Source":
            self.remove_source(instance.handle, transaction)
        elif instance.__class__.__name__ == "Media":
            self.remove_media(instance.handle, transaction)
        elif instance.__class__.__name__ == "Note":
            self.remove_note(instance.handle, transaction)
        elif instance.__class__.__name__ == "Family":
            self.remove_family(instance.handle, transaction)
        else:
            raise ValueError("invalid instance type: %s" % instance.__class__.__name__)

    def get_queryset_by_table_name(self, table_name):
        """
        Get Person, Family queryset by name.
        """
        return getattr(self, table_name)

    def autobackup(self, user=None):
        """
        Backup the current file as a backup file.
        """
        from gramps.cli.user import User
        if user is None:
            user = User()
        if self.is_open() and self.has_changed:
            if user.uistate:
                user.uistate.set_busy_cursor(True)
                user.uistate.progress.show()
                user.uistate.push_message(user.dbstate, _("Autobackup..."))
            try:
                self.backup(user=user)
            except DbException as msg:
                user.notify_error(_("Error saving backup data"), msg)
            if user.uistate:
                user.uistate.set_busy_cursor(False)
                user.uistate.progress.hide()

class QuerySet:
    """
    A container for selection criteria before being actually
    applied to a database.
    """
    def __init__(self, database, table):
        self.database = database
        self.table = table
        self.generator = None
        self.where_by = None
        self.order_by = None
        self.limit_by = -1
        self.start = 0
        self.needs_to_run = False

    def limit(self, start=None, count=None):
        """
        Put limits on the selection.
        """
        if start is not None:
            self.start = start
        if count is not None:
            self.limit_by = count
        self.needs_to_run = True
        return self

    def order(self, *args):
        """
        Put an ordering on the selection.
        """
        for arg in args:
            if self.order_by is None:
                self.order_by = []
            if arg.startswith("-"):
                self.order_by.append((arg[1:], "DESC"))
            else:
                self.order_by.append((arg, "ASC"))
        self.needs_to_run = True
        return self

    def _add_where_clause(self, *args):
        """
        Add a condition to the where clause.
        """
        # First, handle AND, OR, NOT args:
        and_expr = []
        for expr in args:
            and_expr.append(expr)
        # Next, handle kwargs:
        if and_expr:
            if self.where_by:
                self.where_by = ["AND", [self.where_by] + and_expr]
            elif len(and_expr) == 1:
                self.where_by = and_expr[0]
            else:
                self.where_by = ["AND", and_expr]
        self.needs_to_run = True
        return self

    def count(self):
        """
        Run query with just where, start, limit to get count.
        """
        if self.generator and self.needs_to_run:
            raise Exception("Queries in invalid order")
        elif self.generator:
            return len(list(self.generator))
        else:
            generator = self.database._select(self.table,
                                              ["count(1)"],
                                              where=self.where_by,
                                              start=self.start,
                                              limit=self.limit_by)
            return next(generator)

    def _generate(self, args=None):
        """
        Create a generator from current options.
        """
        generator = self.database._select(self.table,
                                          args,
                                          order_by=self.order_by,
                                          where=self.where_by,
                                          start=self.start,
                                          limit=self.limit_by)
        # Reset all criteria
        self.where_by = None
        self.order_by = None
        self.limit_by = -1
        self.start = 0
        self.needs_to_run = False
        return generator

    def select(self, *args):
        """
        Actually touch the database.
        """
        if len(args) == 0:
            args = None
        if self.generator and self.needs_to_run:
            ## problem
            raise Exception("Queries in invalid order")
        elif self.generator:
            if args: # there is a generator, with args
                for i in self.generator:
                    yield [i.get_field(arg) for arg in args]
            else: # generator, no args
                for i in self.generator:
                    yield i
        else: # need to run or not
            self.generator = self._generate(args)
            for i in self.generator:
                yield i

    def proxy(self, proxy_name, *args, **kwargs):
        """
        Apply a named proxy to the db.
        """
        from gramps.gen.proxy import (LivingProxyDb, PrivateProxyDb,
                                      ReferencedBySelectionProxyDb)
        if proxy_name == "living":
            proxy_class = LivingProxyDb
        elif proxy_name == "private":
            proxy_class = PrivateProxyDb
        elif proxy_name == "referenced":
            proxy_class = ReferencedBySelectionProxyDb
        else:
            raise Exception("No such proxy name: '%s'" % proxy_name)
        self.database = proxy_class(self.database, *args, **kwargs)
        return self

    def where(self, where_clause):
        """
        Apply a where_clause (closure) to the selection process.
        """
        from gramps.gen.db.where import eval_where
        # if there is already a generator, then error:
        if self.generator:
            raise Exception("Queries in invalid order")
        where_by = eval_where(where_clause)
        self._add_where_clause(where_by)
        return self

    def filter(self, *args):
        """
        Apply a filter to the database.
        """
        from gramps.gen.proxy import FilterProxyDb
        from gramps.gen.filters import GenericFilter
        from gramps.gen.db.where import eval_where
        for i in range(len(args)):
            arg = args[i]
            if isinstance(arg, GenericFilter):
                self.database = FilterProxyDb(self.database, arg, *args[i+1:])
                if hasattr(arg, "where"):
                    where_by = eval_where(arg.where)
                    self._add_where_clause(where_by)
            elif callable(arg):
                if self.generator and self.needs_to_run:
                    ## error
                    raise Exception("Queries in invalid order")
                elif self.generator:
                    pass # ok
                else:
                    self.generator = self._generate()
                self.generator = filter(arg, self.generator)
            else:
                pass # ignore, may have been arg from previous Filter
        return self

    def map(self, f):
        """
        Apply the function f to the selected items and return results.
        """
        if self.generator and self.needs_to_run:
            raise Exception("Queries in invalid order")
        elif self.generator:
            pass # ok
        else:
            self.generator = self._generate()
        previous_generator = self.generator
        def generator():
            for item in previous_generator:
                yield f(item)
        self.generator = generator()
        return self

    def tag(self, tag_text, remove=False):
        """
        Tag or untag the selected items with the tag name.
        """
        if self.generator and self.needs_to_run:
            raise Exception("Queries in invalid order")
        elif self.generator:
            pass # ok
        else:
            self.generator = self._generate()
        tag = self.database.get_tag_from_name(tag_text)
        if (not tag and remove):
            # no tag by this name, and want to remove it
            # nothing to do
            return
        trans_class = self.database.get_transaction_class()
        with trans_class("Tag Selected Items", self.database, batch=False) as trans:
            if tag is None:
                tag = self.database.get_table_func("Tag","class_func")()
                tag.set_name(tag_text)
                self.database.add_tag(tag, trans)
            commit_func = self.database.get_table_func(self.table,"commit_func")
            for item in self.generator:
                if remove and (tag.handle in item.tag_list):
                    item.remove_tag(tag.handle)
                elif (not remove) and (tag.handle not in item.tag_list):
                    item.add_tag(tag.handle)
                else:
                    continue
                commit_func(item, trans)

