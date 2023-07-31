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

# -------------------------------------------------------------------------
#
# Python libraries
#
# -------------------------------------------------------------------------
import re
import time
from operator import itemgetter
import logging

# -------------------------------------------------------------------------
#
# Gramps libraries
#
# -------------------------------------------------------------------------
from ..db.dbconst import DBLOGNAME
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from ..lib.childreftype import ChildRefType
from ..lib.childref import ChildRef
from .txn import DbTxn
from .exceptions import DbTransactionCancel, DbException

_LOG = logging.getLogger(DBLOGNAME)

# -------------------------------------------------------------------------
#
# Gramps libraries
#
# -------------------------------------------------------------------------


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
        self.__feature = {}  # {"feature": VALUE, ...}

    def get_feature(self, feature):
        """
        Databases can implement certain features or not. The default is
        None, unless otherwise explicitly stated.
        """
        return self.__feature.get(feature, None)  # can also be explicitly None

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
        :type handle: str database handle
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

    def find_next_citation_gramps_id(self):
        """
        Return the next available Gramps ID for a Event object based off the
        event ID prefix.
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

    def find_next_media_gramps_id(self):
        """
        Return the next available Gramps ID for a Media object based
        off the media object ID prefix.
        """
        raise NotImplementedError

    def find_next_note_gramps_id(self):
        """
        Return the next available Gramps ID for a Note object based off the
        note ID prefix.
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

    def get_citation_bookmarks(self):
        """
        Return the list of Citation handles in the bookmarks.
        """
        raise NotImplementedError

    def get_event_bookmarks(self):
        """
        Return the list of Event handles in the bookmarks.
        """
        raise NotImplementedError

    def get_family_bookmarks(self):
        """
        Return the list of Family handles in the bookmarks.
        """
        raise NotImplementedError

    def get_media_bookmarks(self):
        """
        Return the list of Media handles in the bookmarks.
        """
        raise NotImplementedError

    def get_note_bookmarks(self):
        """
        Return the list of Note handles in the bookmarks.
        """
        raise NotImplementedError

    def get_place_bookmarks(self):
        """
        Return the list of Place handles in the bookmarks.
        """
        raise NotImplementedError

    def get_repo_bookmarks(self):
        """
        Return the list of Repository handles in the bookmarks.
        """
        raise NotImplementedError

    def get_source_bookmarks(self):
        """
        Return the list of Source handles in the bookmarks.
        """
        raise NotImplementedError

    def get_citation_cursor(self):
        """
        Return a reference to a cursor over Citation objects.  Example use::

            with get_citation_cursor() as cursor:
                for handle, citation in cursor:
                    # process citation object pointed to by the handle
        """
        raise NotImplementedError

    def get_event_cursor(self):
        """
        Return a reference to a cursor over Family objects.  Example use::

            with get_event_cursor() as cursor:
                for handle, event in cursor:
                    # process event object pointed to by the handle
        """
        raise NotImplementedError

    def get_family_cursor(self):
        """
        Return a reference to a cursor over Family objects.  Example use::

            with get_family_cursor() as cursor:
                for handle, family in cursor:
                    # process family object pointed to by the handle
        """
        raise NotImplementedError

    def get_media_cursor(self):
        """
        Return a reference to a cursor over Media objects.  Example use::

            with get_media_cursor() as cursor:
                for handle, media in cursor:
                    # process media object pointed to by the handle
        """
        raise NotImplementedError

    def get_note_cursor(self):
        """
        Return a reference to a cursor over Note objects.  Example use::

            with get_note_cursor() as cursor:
                for handle, note in cursor:
                    # process note object pointed to by the handle
        """
        raise NotImplementedError

    def get_person_cursor(self):
        """
        Return a reference to a cursor over Person objects.  Example use::

            with get_person_cursor() as cursor:
                for handle, person in cursor:
                    # process person object pointed to by the handle
        """
        raise NotImplementedError

    def get_place_cursor(self):
        """
        Return a reference to a cursor over Place objects.  Example use::

            with get_place_cursor() as cursor:
                for handle, place in cursor:
                    # process place object pointed to by the handle
        """
        raise NotImplementedError

    def get_place_tree_cursor(self):
        """
        Return a reference to a cursor that iterates over Place objects in the
        order they appear in the place hierarchy.  Example use::

            with get_place_tree_cursor() as cursor:
                for handle, place in cursor:
                    # process place object pointed to by the handle
        """
        raise NotImplementedError

    def get_repository_cursor(self):
        """
        Return a reference to a cursor over Repository objects.  Example use::

            with get_repository_cursor() as cursor:
                for handle, repository in cursor:
                    # process repository object pointed to by the handle
        """
        raise NotImplementedError

    def get_source_cursor(self):
        """
        Return a reference to a cursor over Source objects.  Example use::

            with get_source_cursor() as cursor:
                for handle, source in cursor:
                    # process source object pointed to by the handle
        """
        raise NotImplementedError

    def get_tag_cursor(self):
        """
        Return a reference to a cursor over Tag objects.  Example use::

            with get_tag_cursor() as cursor:
                for handle, tag in cursor:
                    # process tag object pointed to by the handle
        """
        raise NotImplementedError

    def get_citation_from_gramps_id(self, val):
        """
        Find a Citation in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Citation exists, None is returned.
        """
        raise NotImplementedError

    def get_event_from_gramps_id(self, val):
        """
        Find an Event in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Event exists, None is returned.
        """
        raise NotImplementedError

    def get_family_from_gramps_id(self, val):
        """
        Find a Family in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Family exists, None is returned.
        """
        raise NotImplementedError

    def get_media_from_gramps_id(self, val):
        """
        Find a Media in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Media exists, None is returned.
        """
        raise NotImplementedError

    def get_note_from_gramps_id(self, val):
        """
        Find a Note in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Note exists, None is returned.
        """
        raise NotImplementedError

    def get_person_from_gramps_id(self, val):
        """
        Find a Person in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Person exists, None is returned.
        """
        raise NotImplementedError

    def get_place_from_gramps_id(self, val):
        """
        Find a Place in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Place exists, None is returned.
        """
        raise NotImplementedError

    def get_repository_from_gramps_id(self, val):
        """
        Find a Repository in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Repository exists, None is returned.
        """
        raise NotImplementedError

    def get_source_from_gramps_id(self, val):
        """
        Find a Source in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Source exists, None is returned.
        """
        raise NotImplementedError

    def get_citation_from_handle(self, handle):
        """
        Return a Citation in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Citation exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Citation is filtered out.
        """
        raise NotImplementedError

    def get_event_from_handle(self, handle):
        """
        Return an Event in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Event exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Event is filtered out.
        """
        raise NotImplementedError

    def get_family_from_handle(self, handle):
        """
        Return a Family in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Family exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Family is filtered out.
        """
        raise NotImplementedError

    def get_media_from_handle(self, handle):
        """
        Return a Media in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Object exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Media is filtered out.
        """
        raise NotImplementedError

    def get_note_from_handle(self, handle):
        """
        Return a Note in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Note exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Note is filtered out.
        """
        raise NotImplementedError

    def get_person_from_handle(self, handle):
        """
        Return a Person in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Person exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Person is filtered out.
        """
        raise NotImplementedError

    def get_place_from_handle(self, handle):
        """
        Return a Place in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Place exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Place is filtered out.
        """
        raise NotImplementedError

    def get_repository_from_handle(self, handle):
        """
        Return a Repository in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Repository exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Repository is filtered out.
        """
        raise NotImplementedError

    def get_source_from_handle(self, handle):
        """
        Return a Source in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Source exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Source is filtered out.
        """
        raise NotImplementedError

    def get_tag_from_handle(self, handle):
        """
        Return a Tag in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Tag exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Tag is filtered out.
        """
        raise NotImplementedError

    def get_citation_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Citation in
        the database.

        :param sort_handles: If True, the list is sorted by Citation title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        raise NotImplementedError

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in the
        database.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_family_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Family in
        the database.

        :param sort_handles: If True, the list is sorted by surnames.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_media_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Media in
        the database.

        :param sort_handles: If True, the list is sorted by title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in the
        database.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_person_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Person in
        the database.

        :param sort_handles: If True, the list is sorted by surnames.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_place_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Place in
        the database.

        :param sort_handles: If True, the list is sorted by Place title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository in
        the database.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_source_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Source in
        the database.

        :param sort_handles: If True, the list is sorted by Source title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_tag_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Tag in
        the database.

        :param sort_handles: If True, the list is sorted by Tag name.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
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

    def get_family_attribute_types(self):
        """
        Return a list of all Attribute types associated with Family instances
        in the database.
        """
        raise NotImplementedError

    def get_media_attribute_types(self):
        """
        Return a list of all Attribute types associated with Media and MediaRef
        instances in the database.
        """
        raise NotImplementedError

    def get_person_attribute_types(self):
        """
        Return a list of all Attribute types associated with Person instances
        in the database.
        """
        raise NotImplementedError

    def get_source_attribute_types(self):
        """
        Return a list of all Attribute types associated with Source/Citation
        instances in the database.
        """
        raise NotImplementedError

    def get_event_types(self):
        """
        Return a list of all event types in the database.
        """
        raise NotImplementedError

    def get_family_event_types(self):
        """
        Deprecated:  Use get_event_types
        """
        raise NotImplementedError

    def get_family_relation_types(self):
        """
        Return a list of all relationship types associated with Family
        instances in the database.
        """
        raise NotImplementedError

    def get_name_types(self):
        """
        Return a list of all custom names types associated with Person
        instances in the database.
        """
        raise NotImplementedError

    def get_note_types(self):
        """
        Return a list of all custom note types associated with Note instances
        in the database.
        """
        raise NotImplementedError

    def get_origin_types(self):
        """
        Return a list of all custom origin types associated with Person/Surname
        instances in the database.
        """
        raise NotImplementedError

    def get_place_types(self):
        """
        Return a list of all custom place types assocated with Place instances
        in the database.
        """
        raise NotImplementedError

    def get_repository_types(self):
        """
        Return a list of all custom repository types associated with Repository
        instances in the database.
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

    def get_number_of_citations(self):
        """
        Return the number of citations currently in the database.
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

    def get_person_event_types(self):
        """
        Deprecated:  Use get_event_types
        """
        raise NotImplementedError

    def get_raw_citation_data(self, handle):
        """
        Return raw (serialized and pickled) Citation object from handle
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

    def get_raw_media_data(self, handle):
        """
        Return raw (serialized and pickled) Family object from handle
        """
        raise NotImplementedError

    def get_raw_note_data(self, handle):
        """
        Return raw (serialized and pickled) Note object from handle
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

    def get_raw_tag_data(self, handle):
        """
        Return raw (serialized and pickled) Tag object from handle
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

    def get_surname_list(self):
        """
        Return the list of locale-sorted surnames contained in the database.
        """
        raise NotImplementedError

    def get_tag_from_name(self, val):
        """
        Find a Tag in the database from the passed Tag name.

        If no such Tag exists, None is returned.
        """
        raise NotImplementedError

    def has_citation_gramps_id(self, gramps_id):
        """
        Return True if the Gramps ID exists in the Citation table.
        """
        raise NotImplementedError

    def has_event_gramps_id(self, gramps_id):
        """
        Return True if the Gramps ID exists in the Event table.
        """
        raise NotImplementedError

    def has_family_gramps_id(self, gramps_id):
        """
        Return True if the Gramps ID exists in the Family table.
        """
        raise NotImplementedError

    def has_media_gramps_id(self, gramps_id):
        """
        Return True if the Gramps ID exists in the Media table.
        """
        raise NotImplementedError

    def has_note_gramps_id(self, gramps_id):
        """
        Return True if the Gramps ID exists in the Note table.
        """
        raise NotImplementedError

    def has_person_gramps_id(self, gramps_id):
        """
        Return True if the Gramps ID exists in the Person table.
        """
        raise NotImplementedError

    def has_place_gramps_id(self, gramps_id):
        """
        Return True if the Gramps ID exists in the Place table.
        """
        raise NotImplementedError

    def has_repository_gramps_id(self, gramps_id):
        """
        Return True if the Gramps ID exists in the Repository table.
        """
        raise NotImplementedError

    def has_source_gramps_id(self, gramps_id):
        """
        Return True if the Gramps ID exists in the Source table.
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

    def has_media_handle(self, handle):
        """
        Return True if the handle exists in the current Mediadatabase.
        """
        raise NotImplementedError

    def has_note_handle(self, handle):
        """
        Return True if the handle exists in the current Note database.
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

    def has_citation_handle(self, handle):
        """
        Return True if the handle exists in the current Citation database.
        """
        raise NotImplementedError

    def has_tag_handle(self, handle):
        """
        Return True if the handle exists in the current Tag database.
        """
        raise NotImplementedError

    def has_name_group_key(self, name):
        """
        Return if a key exists in the name_group table.
        """
        raise NotImplementedError

    def is_open(self):
        """
        Return True if the database has been opened.
        """
        raise NotImplementedError

    def iter_citations(self):
        """
        Return an iterator over objects for Citations in the database
        """
        raise NotImplementedError

    def iter_events(self):
        """
        Return an iterator over objects for Events in the database
        """
        raise NotImplementedError

    def iter_families(self):
        """
        Return an iterator over objects for Families in the database
        """
        raise NotImplementedError

    def iter_media(self):
        """
        Return an iterator over objects for Medias in the database
        """
        raise NotImplementedError

    def iter_notes(self):
        """
        Return an iterator over objects for Notes in the database
        """
        raise NotImplementedError

    def iter_people(self):
        """
        Return an iterator over objects for Persons in the database
        """
        raise NotImplementedError

    def iter_places(self):
        """
        Return an iterator over objects for Places in the database
        """
        raise NotImplementedError

    def iter_repositories(self):
        """
        Return an iterator over objects for Repositories in the database
        """
        raise NotImplementedError

    def iter_sources(self):
        """
        Return an iterator over objects for Sources in the database
        """
        raise NotImplementedError

    def iter_tags(self):
        """
        Return an iterator over objects for Tags in the database
        """
        raise NotImplementedError

    def iter_citation_handles(self):
        """
        Return an iterator over handles for Citations in the database
        """
        raise NotImplementedError

    def iter_event_handles(self):
        """
        Return an iterator over handles for Events in the database
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

    def iter_note_handles(self):
        """
        Return an iterator over handles for Notes in the database
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

    def iter_tag_handles(self):
        """
        Return an iterator over handles for Tags in the database
        """
        raise NotImplementedError

    def load(
        self,
        name,
        callback,
        mode=None,
        force_schema_upgrade=False,
        force_bsddb_upgrade=False,
    ):
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

    def set_prefixes(
        self, person, media, family, source, citation, place, event, repository, note
    ):
        """
        Set the prefixes for the gramps ids for all gramps objects
        """
        raise NotImplementedError

    def set_citation_id_prefix(self, val):
        """
        Set the naming template for Gramps Citation ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as C%d or C%04d.
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
        Set the naming template for Gramps Family ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as F%d or F%04d.
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
        Set the default media path for database.
        """
        raise NotImplementedError

    def set_researcher(self, owner):
        """
        Set the information about the owner of the database.
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

    def get_summary(self):
        """
        Returns dictionary of summary item.
        Should include, if possible:

        _("Number of people")
        _("Version")
        _("Data version")
        """
        raise NotImplementedError

    def requires_login(self):
        """
        Returns True for backends that require a login dialog, else False.
        """
        return False

    def method(self, fmt, *args):
        """
        Convenience function to return database methods.

        :param fmt: Method format string.
        :type fmt: str
        :param args: Substitutions arguments.
        :type args: str
        :returns: Returns a database method or None.
        :rtype: method

        Examples::

            db.method('get_%s_from_handle, 'Person')
            Returns the get_person_from_handle method.

            db.method('get_%s_from_%s, 'Event', 'gramps_id')
            Returns the get_event_from_gramps_id method.

            db.method('get_%s_handles, 'Attribute')
            Returns None.  Attribute is not a primary object.

        .. warning::  Formats 'iter_%s' and 'get_number_of_%s' are not yet
                      implemented.
        """
        return getattr(self, fmt % tuple([arg.lower() for arg in args]), None)


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

    def add_citation(self, event, transaction, set_gid=True):
        """
        Add an Citation to the database, assigning internal IDs if they have
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

    def add_family(self, family, transaction, set_gid=True):
        """
        Add a Family to the database, assigning internal IDs if they have
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

    def add_note(self, obj, transaction, set_gid=True):
        """
        Add a Note to the database, assigning internal IDs if they have
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

    def commit_citation(self, event, transaction, change_time=None):
        """
        Commit the specified Event to the database, storing the changes as
        part of the transaction.
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

    def remove_citation(self, handle, transaction):
        """
        Remove the Event specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_event(self, handle, transaction):
        """
        Remove the Event specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_family(self, handle, transaction):
        """
        Remove the Family specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_media(self, handle, transaction):
        """
        Remove the MediaPerson specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_note(self, handle, transaction):
        """
        Remove the Note specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_person(self, handle, transaction):
        """
        Remove the Person specified by the database handle from the database,
        preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_place(self, handle, transaction):
        """
        Remove the Place specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_repository(self, handle, transaction):
        """
        Remove the Repository specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_source(self, handle, transaction):
        """
        Remove the Source specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_tag(self, handle, transaction):
        """
        Remove the Tag specified by the database handle from the
        database, preserving the change in the passed transaction.
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

    def undo(self, update_history=True):
        """
        Undo last transaction.
        """
        raise NotImplementedError

    def redo(self, update_history=True):
        """
        Redo last transaction.
        """
        raise NotImplementedError

    def add_child_to_family(
        self, family, child, mrel=ChildRefType(), frel=ChildRefType(), trans=None
    ):
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
            with DbTxn(_("Add child to family"), self) as trans:
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
                self.__remove_child_from_family(person_handle, family_handle, trans)
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

        if (
            not family.get_father_handle()
            and not family.get_mother_handle()
            and not family.get_child_ref_list()
        ):
            self.remove_family_relationships(family_handle, trans)
        else:
            self.commit_family(family, trans)
        self.commit_person(person, trans)

    def delete_person_from_database(self, person, trans):
        """
        Deletes a person from the database, cleaning up all associated
        references.
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

            if (
                not family.get_father_handle()
                and not family.get_mother_handle()
                and not family.get_child_ref_list()
            ):
                self.remove_family_relationships(family_handle, trans)
            else:
                self.commit_family(family, trans)

        for family_handle in person.get_parent_family_handle_list():
            if family_handle:
                family = self.get_family_from_handle(family_handle)
                family.remove_child_handle(person.get_handle())
                if (
                    not family.get_father_handle()
                    and not family.get_mother_handle()
                    and not family.get_child_ref_list()
                ):
                    self.remove_family_relationships(family_handle, trans)
                else:
                    self.commit_family(family, trans)

        handle = person.get_handle()

        for obj_type, ohandle in self.find_backlink_handles(handle):
            obj = self.method("get_%s_from_handle", obj_type)(ohandle)
            obj.remove_handle_references("Person", [handle])
            self.method("commit_%s", obj_type)(obj, trans)
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
        for obj_type, ohandle in self.find_backlink_handles(family_handle):
            obj = self.method("get_%s_from_handle", obj_type)(ohandle)
            if obj:
                obj.remove_handle_references("Family", [family_handle])
                self.method("commit_%s", obj_type)(obj, trans)
        self.remove_family(family_handle, trans)

    def remove_parent_from_family(self, person_handle, family_handle, trans=None):
        """
        Remove a person as either the father or mother of a family,
        deleting the family if it becomes empty.
        """
        if trans is None:
            with DbTxn("", self) as trans:
                msg = self.__remove_parent_from_family(
                    person_handle, family_handle, trans
                )
                trans.set_description(msg)
        else:
            msg = self.__remove_parent_from_family(person_handle, family_handle, trans)
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
            raise DbTransactionCancel(
                "The relation between the person and "
                "the family you try to remove is not consistent, please fix "
                "that first, for example from the family editor or by running "
                "the database repair tool, before removing the family."
            )

        if (
            not family.get_father_handle()
            and not family.get_mother_handle()
            and not family.get_child_ref_list()
        ):
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
        place_len = self.get_number_of_places()
        repo_len = self.get_number_of_repositories()
        source_len = self.get_number_of_sources()
        citation_len = self.get_number_of_citations()
        media_len = self.get_number_of_media()
        note_len = self.get_number_of_notes()
        tag_len = self.get_number_of_tags()

        return (
            person_len
            + family_len
            + event_len
            + place_len
            + repo_len
            + source_len
            + citation_len
            + media_len
            + note_len
            + tag_len
        )

    def set_birth_death_index(self, person):
        """
        Set the birth and death indices for a person.
        """
        birth_ref_index = -1
        death_ref_index = -1
        event_ref_list = person.get_event_ref_list()
        for index, ref in enumerate(event_ref_list):
            event = self.get_event_from_handle(ref.ref)
            if (
                event.type.is_birth()
                and ref.role.is_primary()
                and (birth_ref_index == -1)
            ):
                birth_ref_index = index
            elif (
                event.type.is_death()
                and ref.role.is_primary()
                and (death_ref_index == -1)
            ):
                death_ref_index = index

        person.birth_ref_index = birth_ref_index
        person.death_ref_index = death_ref_index
