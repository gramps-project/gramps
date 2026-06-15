#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2025       Steve Youngs
# Copyright (C) 2026       Gabriel Rios
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Base class for the Gramps databases. All database interfaces should inherit
from this class.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from collections.abc import Iterator
import logging
from typing import Any, Generator, Iterator

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from ..db.dbconst import DBLOGNAME
from ..lib import (
    Citation,
    Event,
    Family,
    Media,
    Note,
    Person,
    Place,
    Repository,
    Source,
    Tag,
    EventRef,
)
from ..types import (
    AnyHandle,
    PersonHandle,
    EventHandle,
    FamilyHandle,
    PlaceHandle,
    SourceHandle,
    RepositoryHandle,
    CitationHandle,
    MediaHandle,
    NoteHandle,
    TagHandle,
    PersonGrampsID,
    EventGrampsID,
    FamilyGrampsID,
    PlaceGrampsID,
    SourceGrampsID,
    RepositoryGrampsID,
    CitationGrampsID,
    MediaGrampsID,
    NoteGrampsID,
    PersonDataDict,
    EventDataDict,
    FamilyDataDict,
    PlaceDataDict,
    SourceDataDict,
    RepositoryDataDict,
    CitationDataDict,
    MediaDataDict,
    NoteDataDict,
    TagDataDict,
)
from ..lib.childref import ChildRef
from ..lib.childreftype import ChildRefType
from ..lib.researcher import Researcher
from ..utils.grampslocale import GrampsLocale
from .bookmarks import DbBookmarks
from .exceptions import DbTransactionCancel
from .txn import DbTxn

_ = glocale.translation.gettext

_LOG = logging.getLogger(DBLOGNAME)


# -------------------------------------------------------------------------
#
# DbReadBase class
#
# -------------------------------------------------------------------------
class DbReadBase:
    """
    Gramps database object. This object is a base class for all
    database interfaces.  All methods raise NotImplementedError
    and must be implemented in the derived class as required.
    """

    __feature: dict[str, Any]

    def __init__(self) -> None:
        """
        Create a new DbReadBase instance.

        A new DbReadBase class should never be directly created. Only classes
        derived from this class should be created.
        """
        self.basedb = self
        self.__feature = {}  # {"feature": VALUE, ...}

    def get_feature(self, feature: str) -> Any:
        """
        Databases can implement certain features or not. The default is
        None, unless otherwise explicitly stated.
        """
        return self.__feature.get(feature, None)  # can also be explicitly None

    def set_feature(self, feature: str, value: Any) -> None:
        """
        Databases can implement certain features.
        """
        self.__feature[feature] = value

    def close(self) -> None:
        """
        Close the specified database.
        """
        raise NotImplementedError

    def db_has_bm_changes(self) -> bool:
        """
        Return whether there were bookmark changes during the session.
        """
        raise NotImplementedError

    def find_backlink_handles(
        self, handle: AnyHandle, include_classes: list[str] | None = None
    ) -> Iterator[tuple[str, AnyHandle]]:
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

    def find_initial_person(self) -> Person | None:
        """
        Returns first person in the database
        """
        raise NotImplementedError

    def get_child_reference_types(self) -> list[str]:
        """
        Return a list of all child reference types associated with Family
        instances in the database.
        """
        raise NotImplementedError

    def get_default_handle(self) -> PersonHandle | None:
        """
        Return the default Person of the database.
        """
        raise NotImplementedError

    def get_default_person(self) -> Person | None:
        """
        Return the default Person of the database.
        """
        raise NotImplementedError

    def find_next_citation_gramps_id(self) -> CitationGrampsID:
        """
        Return the next available Gramps ID for a Event object based off the
        event ID prefix.
        """
        raise NotImplementedError

    def find_next_event_gramps_id(self) -> EventGrampsID:
        """
        Return the next available Gramps ID for a Event object based off the
        event ID prefix.
        """
        raise NotImplementedError

    def find_next_family_gramps_id(self) -> FamilyGrampsID:
        """
        Return the next available Gramps ID for a Family object based off the
        family ID prefix.
        """
        raise NotImplementedError

    def find_next_media_gramps_id(self) -> MediaGrampsID:
        """
        Return the next available Gramps ID for a Media object based
        off the media object ID prefix.
        """
        raise NotImplementedError

    def find_next_note_gramps_id(self) -> NoteGrampsID:
        """
        Return the next available Gramps ID for a Note object based off the
        note ID prefix.
        """
        raise NotImplementedError

    def find_next_person_gramps_id(self) -> PersonGrampsID:
        """
        Return the next available Gramps ID for a Person object based off the
        person ID prefix.
        """
        raise NotImplementedError

    def find_next_place_gramps_id(self) -> PlaceGrampsID:
        """
        Return the next available Gramps ID for a Place object based off the
        place ID prefix.
        """
        raise NotImplementedError

    def find_next_repository_gramps_id(self) -> RepositoryGrampsID:
        """
        Return the next available Gramps ID for a Repository object based
        off the repository ID prefix.
        """
        raise NotImplementedError

    def find_next_source_gramps_id(self) -> SourceGrampsID:
        """
        Return the next available Gramps ID for a Source object based off the
        source ID prefix.
        """
        raise NotImplementedError

    def get_bookmarks(self) -> DbBookmarks:
        """
        Return the list of Person handles in the bookmarks.
        """
        raise NotImplementedError

    def get_citation_bookmarks(self) -> DbBookmarks:
        """
        Return the list of Citation handles in the bookmarks.
        """
        raise NotImplementedError

    def get_event_bookmarks(self) -> DbBookmarks:
        """
        Return the list of Event handles in the bookmarks.
        """
        raise NotImplementedError

    def get_family_bookmarks(self) -> DbBookmarks:
        """
        Return the list of Family handles in the bookmarks.
        """
        raise NotImplementedError

    def get_media_bookmarks(self) -> DbBookmarks:
        """
        Return the list of Media handles in the bookmarks.
        """
        raise NotImplementedError

    def get_note_bookmarks(self) -> DbBookmarks:
        """
        Return the list of Note handles in the bookmarks.
        """
        raise NotImplementedError

    def get_place_bookmarks(self) -> DbBookmarks:
        """
        Return the list of Place handles in the bookmarks.
        """
        raise NotImplementedError

    def get_repo_bookmarks(self) -> DbBookmarks:
        """
        Return the list of Repository handles in the bookmarks.
        """
        raise NotImplementedError

    def get_source_bookmarks(self) -> DbBookmarks:
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

    def get_citation_from_gramps_id(
        self, gramps_id: CitationGrampsID
    ) -> Citation | None:
        """
        Find a Citation in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Citation exists, None is returned.
        """
        raise NotImplementedError

    def get_event_from_gramps_id(self, gramps_id: EventGrampsID) -> Event | None:
        """
        Find an Event in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Event exists, None is returned.
        """
        raise NotImplementedError

    def get_family_from_gramps_id(self, gramps_id: FamilyGrampsID) -> Family | None:
        """
        Find a Family in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Family exists, None is returned.
        """
        raise NotImplementedError

    def get_media_from_gramps_id(self, gramps_id: MediaGrampsID) -> Media | None:
        """
        Find a Media in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Media exists, None is returned.
        """
        raise NotImplementedError

    def get_note_from_gramps_id(self, gramps_id: NoteGrampsID) -> Note | None:
        """
        Find a Note in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Note exists, None is returned.
        """
        raise NotImplementedError

    def get_person_from_gramps_id(self, gramps_id: PersonGrampsID) -> Person | None:
        """
        Find a Person in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Person exists, None is returned.
        """
        raise NotImplementedError

    def get_place_from_gramps_id(self, gramps_id: PlaceGrampsID) -> Place | None:
        """
        Find a Place in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Place exists, None is returned.
        """
        raise NotImplementedError

    def get_repository_from_gramps_id(
        self, gramps_id: RepositoryGrampsID
    ) -> Repository | None:
        """
        Find a Repository in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Repository exists, None is returned.
        """
        raise NotImplementedError

    def get_source_from_gramps_id(self, gramps_id: SourceGrampsID) -> Source | None:
        """
        Find a Source in the database from the passed Gramps ID.

        :param val: gramps_id of the object to search for.
        :type val: str or bytes

        If no such Source exists, None is returned.
        """
        raise NotImplementedError

    def get_citation_from_handle(self, handle: CitationHandle) -> Citation:
        """
        Return a Citation in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Citation exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Citation is filtered out.
        """
        raise NotImplementedError

    def get_event_from_handle(self, handle: EventHandle) -> Event:
        """
        Return an Event in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Event exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Event is filtered out.
        """
        raise NotImplementedError

    def get_family_from_handle(self, handle: FamilyHandle) -> Family:
        """
        Return a Family in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Family exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Family is filtered out.
        """
        raise NotImplementedError

    def get_media_from_handle(self, handle: MediaHandle) -> Media:
        """
        Return a Media in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Object exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Media is filtered out.
        """
        raise NotImplementedError

    def get_note_from_handle(self, handle: NoteHandle) -> Note:
        """
        Return a Note in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Note exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Note is filtered out.
        """
        raise NotImplementedError

    def get_person_from_handle(self, handle: PersonHandle) -> Person:
        """
        Return a Person in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Person exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Person is filtered out.
        """
        raise NotImplementedError

    def get_place_from_handle(self, handle: PlaceHandle) -> Place:
        """
        Return a Place in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Place exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Place is filtered out.
        """
        raise NotImplementedError

    def get_repository_from_handle(self, handle: RepositoryHandle) -> Repository:
        """
        Return a Repository in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Repository exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Repository is filtered out.
        """
        raise NotImplementedError

    def get_source_from_handle(self, handle: SourceHandle) -> Source:
        """
        Return a Source in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Source exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Source is filtered out.
        """
        raise NotImplementedError

    def get_tag_from_handle(self, handle: TagHandle) -> Tag:
        """
        Return a Tag in the database from the passed handle.

        :param handle: handle of the object to search for.
        :type handle: str or bytes

        If no such Tag exists, a HandleError is raised.
        Note: if used through a proxy (Filter for reports etc.) a 'None' is
        returned in cases where the Tag is filtered out.
        """
        raise NotImplementedError

    def get_citation_handles(
        self, sort_handles: bool = False, locale: GrampsLocale = glocale
    ) -> list[CitationHandle]:
        """
        Return a list of database handles, one handle for each Citation in
        the database.

        :param sort_handles: If True, the list is sorted by Citation title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        raise NotImplementedError

    def get_event_handles(self) -> list[EventHandle]:
        """
        Return a list of database handles, one handle for each Event in the
        database.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_family_handles(
        self, sort_handles: bool = False, locale: GrampsLocale = glocale
    ) -> list[FamilyHandle]:
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

    def get_media_handles(
        self, sort_handles: bool = False, locale: GrampsLocale = glocale
    ) -> list[MediaHandle]:
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

    def get_note_handles(self) -> list[NoteHandle]:
        """
        Return a list of database handles, one handle for each Note in the
        database.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_person_handles(
        self, sort_handles: bool = False, locale: GrampsLocale = glocale
    ) -> list[PersonHandle]:
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

    def get_place_handles(
        self, sort_handles: bool = False, locale: GrampsLocale = glocale
    ) -> list[PlaceHandle]:
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

    def get_repository_handles(self) -> list[RepositoryHandle]:
        """
        Return a list of database handles, one handle for each Repository in
        the database.

        .. warning:: For speed the keys are directly returned, so handles are
                     bytes type
        """
        raise NotImplementedError

    def get_source_handles(
        self, sort_handles: bool = False, locale: GrampsLocale = glocale
    ) -> list[SourceHandle]:
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

    def get_tag_handles(
        self, sort_handles: bool = False, locale: GrampsLocale = glocale
    ) -> list[TagHandle]:
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

    def get_event_roles(self) -> list[str]:
        """
        Return a list of all custom event role names associated with Event
        instances in the database.
        """
        raise NotImplementedError

    def get_event_attribute_types(self) -> list[str]:
        """
        Return a list of all Attribute types assocated with Event instances
        in the database.
        """
        raise NotImplementedError

    def get_family_attribute_types(self) -> list[str]:
        """
        Return a list of all Attribute types associated with Family instances
        in the database.
        """
        raise NotImplementedError

    def get_media_attribute_types(self) -> list[str]:
        """
        Return a list of all Attribute types associated with Media and MediaRef
        instances in the database.
        """
        raise NotImplementedError

    def get_person_attribute_types(self) -> list[str]:
        """
        Return a list of all Attribute types associated with Person instances
        in the database.
        """
        raise NotImplementedError

    def get_source_attribute_types(self) -> list[str]:
        """
        Return a list of all Attribute types associated with Source/Citation
        instances in the database.
        """
        raise NotImplementedError

    def get_event_types(self) -> list[str]:
        """
        Return a list of all event types in the database.
        """
        raise NotImplementedError

    def get_family_event_types(self) -> list[str]:
        """
        Deprecated:  Use get_event_types
        """
        raise NotImplementedError

    def get_family_relation_types(self) -> list[str]:
        """
        Return a list of all relationship types associated with Family
        instances in the database.
        """
        raise NotImplementedError

    def get_name_types(self) -> list[str]:
        """
        Return a list of all custom names types associated with Person
        instances in the database.
        """
        raise NotImplementedError

    def get_note_types(self) -> list[str]:
        """
        Return a list of all custom note types associated with Note instances
        in the database.
        """
        raise NotImplementedError

    def get_origin_types(self) -> list[str]:
        """
        Return a list of all custom origin types associated with Person/Surname
        instances in the database.
        """
        raise NotImplementedError

    def get_place_types(self) -> list[str]:
        """
        Return a list of all custom place types assocated with Place instances
        in the database.
        """
        raise NotImplementedError

    def get_repository_types(self) -> list[str]:
        """
        Return a list of all custom repository types associated with Repository
        instances in the database.
        """
        raise NotImplementedError

    def get_source_media_types(self) -> list[str]:
        """
        Return a list of all custom source media types associated with Source
        instances in the database.
        """
        raise NotImplementedError

    def get_url_types(self) -> list[str]:
        """
        Return a list of all custom url types associated with Url instances
        in the database.
        """
        raise NotImplementedError

    def get_mediapath(self) -> str | None:
        """
        Return the default media path of the database.
        """
        raise NotImplementedError

    def get_name_group_keys(self):
        """
        Return the defined names that have been assigned to a default grouping.
        """
        raise NotImplementedError

    def get_name_group_mapping(self, surname: str) -> str:
        """
        Return the default grouping name for a surname.
        """
        raise NotImplementedError

    def get_number_of_citations(self) -> int:
        """
        Return the number of citations currently in the database.
        """
        raise NotImplementedError

    def get_number_of_events(self) -> int:
        """
        Return the number of events currently in the database.
        """
        raise NotImplementedError

    def get_number_of_families(self) -> int:
        """
        Return the number of families currently in the database.
        """
        raise NotImplementedError

    def get_number_of_media(self) -> int:
        """
        Return the number of media objects currently in the database.
        """
        raise NotImplementedError

    def get_number_of_notes(self) -> int:
        """
        Return the number of notes currently in the database.
        """
        raise NotImplementedError

    def get_number_of_people(self) -> int:
        """
        Return the number of people currently in the database.
        """
        raise NotImplementedError

    def get_number_of_places(self) -> int:
        """
        Return the number of places currently in the database.
        """
        raise NotImplementedError

    def get_number_of_repositories(self) -> int:
        """
        Return the number of source repositories currently in the database.
        """
        raise NotImplementedError

    def get_number_of_sources(self) -> int:
        """
        Return the number of sources currently in the database.
        """
        raise NotImplementedError

    def get_number_of_tags(self) -> int:
        """
        Return the number of tags currently in the database.
        """
        raise NotImplementedError

    def get_person_event_types(self) -> list[str]:
        """
        Deprecated:  Use get_event_types
        """
        raise NotImplementedError

    def get_raw_citation_data(self, handle: CitationHandle) -> CitationDataDict:
        """
        Return raw (serialized and pickled) Citation object from handle
        """
        raise NotImplementedError

    def get_raw_event_data(self, handle: EventHandle) -> EventDataDict:
        """
        Return raw (serialized and pickled) Event object from handle
        """
        raise NotImplementedError

    def get_raw_family_data(self, handle: FamilyHandle) -> FamilyDataDict:
        """
        Return raw (serialized and pickled) Family object from handle
        """
        raise NotImplementedError

    def get_raw_media_data(self, handle: MediaHandle) -> MediaDataDict:
        """
        Return raw (serialized and pickled) Media object from handle
        """
        raise NotImplementedError

    def get_raw_note_data(self, handle: NoteHandle) -> NoteDataDict:
        """
        Return raw (serialized and pickled) Note object from handle
        """
        raise NotImplementedError

    def get_raw_person_data(self, handle: PersonHandle) -> PersonDataDict:
        """
        Return raw (serialized and pickled) Person object from handle
        """
        raise NotImplementedError

    def get_raw_place_data(self, handle: PlaceHandle) -> PlaceDataDict:
        """
        Return raw (serialized and pickled) Place object from handle
        """
        raise NotImplementedError

    def get_raw_repository_data(self, handle: RepositoryHandle) -> RepositoryDataDict:
        """
        Return raw (serialized and pickled) Repository object from handle
        """
        raise NotImplementedError

    def get_raw_source_data(self, handle: SourceHandle) -> SourceDataDict:
        """
        Return raw (serialized and pickled) Source object from handle
        """
        raise NotImplementedError

    def get_raw_tag_data(self, handle: TagHandle) -> TagDataDict:
        """
        Return raw (serialized and pickled) Tag object from handle
        """
        raise NotImplementedError

    def get_researcher(self) -> Researcher:
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

    def get_tag_from_name(self, name: str):
        """
        Find a Tag in the database from the passed Tag name.

        If no such Tag exists, None is returned.
        """
        raise NotImplementedError

    def has_citation_gramps_id(self, gramps_id: CitationGrampsID) -> bool:
        """
        Return True if the Gramps ID exists in the Citation table.
        """
        raise NotImplementedError

    def has_event_gramps_id(self, gramps_id: EventGrampsID) -> bool:
        """
        Return True if the Gramps ID exists in the Event table.
        """
        raise NotImplementedError

    def has_family_gramps_id(self, gramps_id: FamilyGrampsID) -> bool:
        """
        Return True if the Gramps ID exists in the Family table.
        """
        raise NotImplementedError

    def has_media_gramps_id(self, gramps_id: MediaGrampsID) -> bool:
        """
        Return True if the Gramps ID exists in the Media table.
        """
        raise NotImplementedError

    def has_note_gramps_id(self, gramps_id: NoteGrampsID) -> bool:
        """
        Return True if the Gramps ID exists in the Note table.
        """
        raise NotImplementedError

    def has_person_gramps_id(self, gramps_id: PersonGrampsID) -> bool:
        """
        Return True if the Gramps ID exists in the Person table.
        """
        raise NotImplementedError

    def has_place_gramps_id(self, gramps_id: PlaceGrampsID) -> bool:
        """
        Return True if the Gramps ID exists in the Place table.
        """
        raise NotImplementedError

    def has_repository_gramps_id(self, gramps_id: RepositoryGrampsID) -> bool:
        """
        Return True if the Gramps ID exists in the Repository table.
        """
        raise NotImplementedError

    def has_source_gramps_id(self, gramps_id: SourceGrampsID) -> bool:
        """
        Return True if the Gramps ID exists in the Source table.
        """
        raise NotImplementedError

    def has_event_handle(self, handle: EventHandle) -> bool:
        """
        Return True if the handle exists in the current Event database.
        """
        raise NotImplementedError

    def has_family_handle(self, handle: FamilyHandle) -> bool:
        """
        Return True if the handle exists in the current Family database.
        """
        raise NotImplementedError

    def has_media_handle(self, handle: MediaHandle) -> bool:
        """
        Return True if the handle exists in the current Mediadatabase.
        """
        raise NotImplementedError

    def has_note_handle(self, handle: NoteHandle) -> bool:
        """
        Return True if the handle exists in the current Note database.
        """
        raise NotImplementedError

    def has_person_handle(self, handle: PersonHandle) -> bool:
        """
        Return True if the handle exists in the current Person database.
        """
        raise NotImplementedError

    def has_place_handle(self, handle: PlaceHandle) -> bool:
        """
        Return True if the handle exists in the current Place database.
        """
        raise NotImplementedError

    def has_repository_handle(self, handle: RepositoryHandle) -> bool:
        """
        Return True if the handle exists in the current Repository database.
        """
        raise NotImplementedError

    def has_source_handle(self, handle: SourceHandle) -> bool:
        """
        Return True if the handle exists in the current Source database.
        """
        raise NotImplementedError

    def has_citation_handle(self, handle: CitationHandle) -> bool:
        """
        Return True if the handle exists in the current Citation database.
        """
        raise NotImplementedError

    def has_tag_handle(self, handle: TagHandle) -> bool:
        """
        Return True if the handle exists in the current Tag database.
        """
        raise NotImplementedError

    def has_name_group_key(self, key):
        """
        Return if a key exists in the name_group table.
        """
        raise NotImplementedError

    def is_open(self) -> bool:
        """
        Return True if the database has been opened.
        """
        raise NotImplementedError

    def iter_citations(self) -> Iterator[Citation]:
        """
        Return an iterator over objects for Citations in the database
        """
        raise NotImplementedError

    def iter_events(self) -> Iterator[Event]:
        """
        Return an iterator over objects for Events in the database
        """
        raise NotImplementedError

    def iter_families(self) -> Iterator[Family]:
        """
        Return an iterator over objects for Families in the database
        """
        raise NotImplementedError

    def iter_media(self) -> Iterator[Media]:
        """
        Return an iterator over objects for Medias in the database
        """
        raise NotImplementedError

    def iter_notes(self) -> Iterator[Note]:
        """
        Return an iterator over objects for Notes in the database
        """
        raise NotImplementedError

    def iter_people(self) -> Iterator[Person]:
        """
        Return an iterator over objects for Persons in the database
        """
        raise NotImplementedError

    def iter_places(self) -> Iterator[Place]:
        """
        Return an iterator over objects for Places in the database
        """
        raise NotImplementedError

    def iter_repositories(self) -> Iterator[Repository]:
        """
        Return an iterator over objects for Repositories in the database
        """
        raise NotImplementedError

    def iter_sources(self) -> Iterator[Source]:
        """
        Return an iterator over objects for Sources in the database
        """
        raise NotImplementedError

    def iter_tags(self) -> Iterator[Tag]:
        """
        Return an iterator over objects for Tags in the database
        """
        raise NotImplementedError

    def iter_citation_handles(self) -> Iterator[CitationHandle]:
        """
        Return an iterator over handles for Citations in the database
        """
        raise NotImplementedError

    def iter_event_handles(self) -> Iterator[EventHandle]:
        """
        Return an iterator over handles for Events in the database
        """
        raise NotImplementedError

    def iter_family_handles(self) -> Iterator[FamilyHandle]:
        """
        Return an iterator over handles for Families in the database
        """
        raise NotImplementedError

    def iter_media_handles(self) -> Iterator[MediaHandle]:
        """
        Return an iterator over handles for Media in the database
        """
        raise NotImplementedError

    def iter_note_handles(self) -> Iterator[NoteHandle]:
        """
        Return an iterator over handles for Notes in the database
        """
        raise NotImplementedError

    def iter_person_handles(self) -> Iterator[PersonHandle]:
        """
        Return an iterator over handles for Persons in the database
        """
        raise NotImplementedError

    def iter_place_handles(self) -> Iterator[PlaceHandle]:
        """
        Return an iterator over handles for Places in the database
        """
        raise NotImplementedError

    def iter_repository_handles(self) -> Iterator[RepositoryHandle]:
        """
        Return an iterator over handles for Repositories in the database
        """
        raise NotImplementedError

    def iter_source_handles(self) -> Iterator[SourceHandle]:
        """
        Return an iterator over handles for Sources in the database
        """
        raise NotImplementedError

    def iter_tag_handles(self) -> Iterator[TagHandle]:
        """
        Return an iterator over handles for Tags in the database
        """
        raise NotImplementedError

    def load(
        self,
        directory,
        callback,
        mode=None,
        force_schema_upgrade=False,
        force_bsddb_upgrade=False,
    ):
        """
        Open the specified database.
        """
        raise NotImplementedError

    def report_bm_change(self) -> None:
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
        self,
        person: str,
        media: str,
        family: str,
        source: str,
        citation: str,
        place: str,
        event: str,
        repository: str,
        note: str,
    ) -> None:
        """
        Set the prefixes for the gramps ids for all gramps objects
        """
        raise NotImplementedError

    def set_citation_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Citation ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as C%d or C%05d.
        """
        raise NotImplementedError

    def set_event_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Event ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as E%d or E%05d.
        """
        raise NotImplementedError

    def set_family_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Family ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as F%d or F%05d.
        """
        raise NotImplementedError

    def set_note_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Note ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as N%d or N%05d.
        """
        raise NotImplementedError

    def set_media_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Media ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as O%d or O%05d.
        """
        raise NotImplementedError

    def set_person_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Person ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as I%d or I%05d.
        """
        raise NotImplementedError

    def set_place_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Place ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as P%d or P%05d.
        """
        raise NotImplementedError

    def set_repository_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Repository ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as R%d or R%05d.
        """
        raise NotImplementedError

    def set_source_id_prefix(self, val: str) -> None:
        """
        Set the naming template for Gramps Source ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as S%d or S%05d.
        """
        raise NotImplementedError

    def set_mediapath(self, mediapath: str | None) -> None:
        """
        Set the default media path for database.
        """
        raise NotImplementedError

    def set_researcher(self, owner: Researcher) -> None:
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

    def get_summary(self) -> dict[str, int | str]:
        """
        Returns dictionary of summary item.
        Should include, if possible:

        _("Number of people")
        _("Version")
        _("Data version")
        """
        raise NotImplementedError

    def requires_login(self) -> bool:
        """
        Returns True for backends that require a login dialog, else False.
        """
        return False

    def method(self, fmt: str, *args):
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

    def get_familysearch_person_status(self, person_handle, default=None):
        """
        Return FamilySearch sync status for the given Person handle

        Returns a dict with these keys when present:
            fsid
            is_root
            status_ts
            confirmed_ts
            gramps_modified_ts
            fs_modified_ts
            essential_conflict
            conflict
        """
        raise NotImplementedError


# -------------------------------------------------------------------------
#
# DbWriteBase class
#
# -------------------------------------------------------------------------
class DbWriteBase(DbReadBase):
    """
    Gramps database object. This object is a base class for all
    database interfaces.  All methods raise NotImplementedError
    and must be implemented in the derived class as required.
    """

    def __init__(self) -> None:
        """
        Create a new DbWriteBase instance.

        A new DbWriteBase class should never be directly created. Only classes
        derived from this class should be created.
        """
        DbReadBase.__init__(self)

    def add_citation(
        self, citation: Citation, transaction: DbTxn, set_gid: bool = True
    ) -> CitationHandle:
        """
        Add an Citation to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_event(
        self, event: Event, transaction: DbTxn, set_gid: bool = True
    ) -> EventHandle:
        """
        Add an Event to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_family(
        self, family: Family, transaction: DbTxn, set_gid: bool = True
    ) -> FamilyHandle:
        """
        Add a Family to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_media(
        self, media: Media, transaction: DbTxn, set_gid: bool = True
    ) -> MediaHandle:
        """
        Add a Media to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_note(
        self, note: Note, transaction: DbTxn, set_gid: bool = True
    ) -> NoteHandle:
        """
        Add a Note to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_person(
        self, person: Person, transaction: DbTxn, set_gid: bool = True
    ) -> PersonHandle:
        """
        Add a Person to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_place(
        self, place: Place, transaction: DbTxn, set_gid: bool = True
    ) -> PlaceHandle:
        """
        Add a Place to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_repository(
        self, repository: Repository, transaction: DbTxn, set_gid: bool = True
    ) -> RepositoryHandle:
        """
        Add a Repository to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_source(
        self, source: Source, transaction: DbTxn, set_gid: bool = True
    ) -> SourceHandle:
        """
        Add a Source to the database, assigning internal IDs if they have
        not already been defined.

        If not set_gid, then gramps_id is not set.
        """
        raise NotImplementedError

    def add_tag(self, tag: Tag, transaction: DbTxn) -> TagHandle:
        """
        Add a Tag to the database, assigning a handle if it has not already
        been defined.
        """
        raise NotImplementedError

    def add_to_surname_list(self, person: Person, batch_transaction: bool) -> None:
        """
        Add surname from given person to list of surnames
        """
        raise NotImplementedError

    def commit_citation(
        self, citation: Citation, transaction: DbTxn, change_time: int | None = None
    ) -> None:
        """
        Commit the specified Event to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def commit_event(
        self, event: Event, transaction: DbTxn, change_time: int | None = None
    ) -> None:
        """
        Commit the specified Event to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def commit_family(
        self, family: Family, transaction: DbTxn, change_time: int | None = None
    ) -> None:
        """
        Commit the specified Family to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def commit_media(
        self, media: Media, transaction: DbTxn, change_time: int | None = None
    ) -> None:
        """
        Commit the specified Media to the database, storing the changes
        as part of the transaction.
        """
        raise NotImplementedError

    def commit_note(
        self, note, transaction: DbTxn, change_time: int | None = None
    ) -> None:
        """
        Commit the specified Note to the database, storing the changes as part
        of the transaction.
        """
        raise NotImplementedError

    def commit_person(
        self, person: Person, transaction: DbTxn, change_time: int | None = None
    ) -> None:
        """
        Commit the specified Person to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def commit_place(
        self, place: Place, transaction: DbTxn, change_time: int | None = None
    ) -> None:
        """
        Commit the specified Place to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def commit_repository(
        self,
        repository: Repository,
        transaction: DbTxn,
        change_time: int | None = None,
    ) -> None:
        """
        Commit the specified Repository to the database, storing the changes
        as part of the transaction.
        """
        raise NotImplementedError

    def commit_source(
        self, source: Source, transaction: DbTxn, change_time: int | None = None
    ) -> None:
        """
        Commit the specified Source to the database, storing the changes as
        part of the transaction.
        """
        raise NotImplementedError

    def commit_tag(
        self, tag: Tag, transaction: DbTxn, change_time: int | None = None
    ) -> None:
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

    def rebuild_secondary(self, callback) -> None:
        """
        Rebuild secondary indices
        """
        raise NotImplementedError

    def reindex_reference_map(self, callback) -> None:
        """
        Reindex all primary records in the database.
        """
        raise NotImplementedError

    def remove_citation(self, handle: CitationHandle, transaction: DbTxn):
        """
        Remove the Event specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_event(self, handle: EventHandle, transaction: DbTxn):
        """
        Remove the Event specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_family(self, handle: FamilyHandle, transaction: DbTxn):
        """
        Remove the Family specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_media(self, handle: MediaHandle, transaction: DbTxn):
        """
        Remove the MediaPerson specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_note(self, handle: NoteHandle, transaction: DbTxn):
        """
        Remove the Note specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_person(self, handle: PersonHandle, transaction: DbTxn):
        """
        Remove the Person specified by the database handle from the database,
        preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_place(self, handle: PlaceHandle, transaction: DbTxn):
        """
        Remove the Place specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_repository(self, handle: RepositoryHandle, transaction: DbTxn):
        """
        Remove the Repository specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_source(self, handle: SourceHandle, transaction: DbTxn):
        """
        Remove the Source specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_tag(self, handle: TagHandle, transaction: DbTxn):
        """
        Remove the Tag specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        raise NotImplementedError

    def remove_from_surname_list(self, person: Person):
        """
        Check whether there are persons with the same surname left in
        the database.

        If not then we need to remove the name from the list.
        The function must be overridden in the derived class.
        """
        raise NotImplementedError

    def set_default_person_handle(self, handle: PersonHandle | None) -> None:
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

    def transaction_begin(self, transaction: DbTxn) -> DbTxn:
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

    def transaction_commit(self, transaction: DbTxn) -> None:
        """
        Make the changes to the database final and add the content of the
        transaction to the undo database.
        """
        raise NotImplementedError

    def transaction_abort(self, transaction: DbTxn) -> None:
        """
        Revert the changes made to the database so far during the transaction.
        """
        raise NotImplementedError

    def undo(self, update_history: bool = True) -> bool:
        """
        Undo last transaction.
        """
        raise NotImplementedError

    def redo(self, update_history: bool = True) -> bool:
        """
        Redo last transaction.
        """
        raise NotImplementedError

    def add_child_to_family(
        self,
        family: Family,
        child: Person,
        mrel: ChildRefType = ChildRefType(),
        frel: ChildRefType = ChildRefType(),
        trans: DbTxn | None = None,
    ) -> None:
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
            with DbTxn(_("Add child to family"), self) as transaction:
                self.commit_family(family, transaction)
                self.commit_person(child, transaction)
        else:
            self.commit_family(family, trans)
            self.commit_person(child, trans)

    def remove_child_from_family(
        self,
        person_handle: PersonHandle,
        family_handle: FamilyHandle,
        trans: DbTxn | None = None,
    ) -> None:
        """
        Remove a person as a child of the family, deleting the family if
        it becomes empty.
        """
        if trans is None:
            with DbTxn(_("Remove child from family"), self) as transaction:
                self.__remove_child_from_family(
                    person_handle, family_handle, transaction
                )
        else:
            self.__remove_child_from_family(person_handle, family_handle, trans)
            trans.set_description(_("Remove child from family"))

    def __remove_child_from_family(
        self, person_handle: PersonHandle, family_handle: FamilyHandle, trans: DbTxn
    ) -> None:
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

    def delete_person_from_database(self, person: Person, trans: DbTxn) -> None:
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

    def remove_family_relationships(
        self, family_handle: FamilyHandle, trans: DbTxn | None = None
    ) -> None:
        """
        Remove a family and its relationships.
        """
        if trans is None:
            with DbTxn(_("Remove Family"), self) as transaction:
                self.__remove_family_relationships(family_handle, transaction)
        else:
            self.__remove_family_relationships(family_handle, trans)
            trans.set_description(_("Remove Family"))

    def __remove_family_relationships(
        self, family_handle: FamilyHandle, trans: DbTxn
    ) -> None:
        """
        Remove a family and all that references it; trans is compulsory.
        """
        for obj_type, ohandle in self.find_backlink_handles(family_handle):
            obj = self.method("get_%s_from_handle", obj_type)(ohandle)
            if obj:
                obj.remove_handle_references("Family", [family_handle])
                self.method("commit_%s", obj_type)(obj, trans)
        self.remove_family(family_handle, trans)

    def remove_parent_from_family(
        self,
        person_handle: PersonHandle,
        family_handle: FamilyHandle,
        trans: DbTxn | None = None,
    ) -> None:
        """
        Remove a person as either the father or mother of a family,
        deleting the family if it becomes empty.
        """
        if trans is None:
            with DbTxn("", self) as transaction:
                msg = self.__remove_parent_from_family(
                    person_handle, family_handle, transaction
                )
                transaction.set_description(msg)
        else:
            msg = self.__remove_parent_from_family(person_handle, family_handle, trans)
            trans.set_description(msg)

    def __remove_parent_from_family(
        self, person_handle: PersonHandle, family_handle: FamilyHandle, trans: DbTxn
    ) -> str:
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

    def marriage_from_eventref_list(
        self, eventref_list: list[EventRef]
    ) -> Event | None:
        """
        Get the marriage event from an eventref list.
        """
        for eventref in eventref_list:
            event = self.get_event_from_handle(eventref.ref)
            if event and event.type.is_marriage():
                return event
        return None

    def get_total(self) -> int:
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

    def set_birth_death_index(self, person: Person) -> None:
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

    def set_familysearch_person_status(self, person_handle, status, transaction=None):
        """
        Persist FamilySearch sync status for the given Person handle.

        status must be a dict with any of these keys:
            fsid
            is_root
            status_ts
            confirmed_ts
            gramps_modified_ts
            fs_modified_ts
            essential_conflict
            conflict

        Passing an empty dict removes the stored status row.
        """
        raise NotImplementedError

    def delete_familysearch_person_status(self, person_handle, transaction=None):
        """
        Remove FamilySearch sync status for the given Person handle.
        """
        raise NotImplementedError
