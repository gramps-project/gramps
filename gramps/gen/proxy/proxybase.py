#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
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
Proxy class for the Gramps databases. Filter out all data marked private.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import types

#-------------------------------------------------------------------------
#
# Gramps libraries
#
#-------------------------------------------------------------------------
from ..db.base import DbReadBase, DbWriteBase
from ..lib import (Citation, Event, Family, Media, Note, Person, Place,
                   Repository, Source, Tag)
from ..const import GRAMPS_LOCALE as glocale

class ProxyCursor:
    """
    A cursor for moving through proxied data.
    """
    def __init__(self, get_raw, get_handles):
        self.get_raw = get_raw
        self.get_handles = get_handles

    def __enter__(self):
        """
        Context manager enter method
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        for handle in self.get_handles():
            yield handle, self.get_raw(handle)

class ProxyMap:
    """
    A dictionary-like object for accessing "raw" proxied data. Of
    course, proxied data may have been changed by the proxy.
    """
    def __init__(self, db, get_raw, get_keys):
        self.get_raw = get_raw
        self.get_keys = get_keys
        self.db = db

    def __getitem__(self, handle):
        return self.get_raw(handle)

    def keys(self):
        """ return the keys """
        return self.get_keys()

class ProxyDbBase(DbReadBase):
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
        Create a new ProxyDb instance.
        """
        self.db = self.basedb = db
        while isinstance(self.basedb, ProxyDbBase):
            self.basedb = self.basedb.db
        self.name_formats = db.name_formats
        self.bookmarks = db.bookmarks
        self.family_bookmarks = db.family_bookmarks
        self.event_bookmarks = db.event_bookmarks
        self.place_bookmarks = db.place_bookmarks
        self.source_bookmarks = db.source_bookmarks
        self.citation_bookmarks = db.citation_bookmarks
        self.repo_bookmarks = db.repo_bookmarks
        self.media_bookmarks = db.media_bookmarks
        self.note_bookmarks = db.note_bookmarks

        self.person_map = ProxyMap(self, self.get_raw_person_data,
                                   self.get_person_handles)
        self.family_map = ProxyMap(self, self.get_raw_family_data,
                                   self.get_family_handles)
        self.event_map = ProxyMap(self, self.get_raw_event_data,
                                  self.get_event_handles)
        self.place_map = ProxyMap(self, self.get_raw_place_data,
                                  self.get_place_handles)
        self.source_map = ProxyMap(self, self.get_raw_source_data,
                                   self.get_source_handles)
        self.repository_map = ProxyMap(self, self.get_raw_repository_data,
                                       self.get_repository_handles)
        self.media_map = ProxyMap(self, self.get_raw_media_data,
                                  self.get_media_handles)
        self.note_map = ProxyMap(self, self.get_raw_note_data,
                                 self.get_note_handles)

    def is_open(self):
        """
        Return True if the database has been opened.
        """
        return self.db.is_open()

    def get_researcher(self):
        """returns the Researcher instance, providing information about
        the owner of the database"""
        return self.db.get_researcher()

    def include_something(self, handle, obj=None):
        """
        Model predicate. Returns True if object referred to by handle is to be
        included, otherwise returns False.
        """
        if obj is None:
            obj = self.get_unfiltered_something(handle)

        # Call function to determine if object should be included or not
        return obj.include()

    # Define default predicates for each object type

    include_person = \
    include_family = \
    include_event = \
    include_source = \
    include_citation = \
    include_place = \
    include_media = \
    include_repository = \
    include_note = \
    include_tag = \
        None

    def get_person_cursor(self):
        return ProxyCursor(self.get_raw_person_data,
                           self.get_person_handles)

    def get_family_cursor(self):
        return ProxyCursor(self.get_raw_family_data,
                           self.get_family_handles)

    def get_event_cursor(self):
        return ProxyCursor(self.get_raw_event_data,
                           self.get_event_handles)

    def get_source_cursor(self):
        return ProxyCursor(self.get_raw_source_data,
                           self.get_source_handles)

    def get_citation_cursor(self):
        return ProxyCursor(self.get_raw_citation_data,
                           self.get_citation_handles)

    def get_place_cursor(self):
        return ProxyCursor(self.get_raw_place_data,
                           self.get_place_handles)

    def get_media_cursor(self):
        return ProxyCursor(self.get_raw_media_data,
                           self.get_media_handles)

    def get_repository_cursor(self):
        return ProxyCursor(self.get_raw_repository_data,
                           self.get_repository_handles)

    def get_note_cursor(self):
        return ProxyCursor(self.get_raw_note_data,
                           self.get_note_handles)

    def get_tag_cursor(self):
        return ProxyCursor(self.get_raw_tag_data,
                           self.get_tag_handles)

    def get_person_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Person in
        the database. If sort_handles is True, the list is sorted by surnames
        """
        if (self.db is not None) and self.db.is_open():
            proxied = set(self.iter_person_handles())
            all = self.basedb.get_person_handles(sort_handles=sort_handles,
                                                 locale=locale)
            return [hdl for hdl in all if hdl in proxied]
        else:
            return []

    def get_family_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Family in
        the database. If sort_handles is True, the list is sorted by surnames
        """
        if (self.db is not None) and self.db.is_open():
            proxied = set(self.iter_family_handles())
            all = self.basedb.get_family_handles(sort_handles=sort_handles,
                                                 locale=locale)
            return [hdl for hdl in all if hdl in proxied]
        else:
            return []

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in
        the database.
        """
        if (self.db is not None) and self.db.is_open():
            return list(self.iter_event_handles())
        else:
            return []

    def get_source_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Source in
        the database.
        """
        if (self.db is not None) and self.db.is_open():
            return list(self.iter_source_handles())
        else:
            return []

    def get_citation_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Citation in
        the database.
        """
        if (self.db is not None) and self.db.is_open():
            return list(self.iter_citation_handles())
        else:
            return []

    def get_place_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Place in
        the database.
        """
        if (self.db is not None) and self.db.is_open():
            return list(self.iter_place_handles())
        else:
            return []

    def get_media_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Media in
        the database.
        """
        if (self.db is not None) and self.db.is_open():
            return list(self.iter_media_handles())
        else:
            return []

    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository in
        the database.
        """
        if (self.db is not None) and self.db.is_open():
            return list(self.iter_repository_handles())
        else:
            return []

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in
        the database.
        """
        if (self.db is not None) and self.db.is_open():
            return list(self.iter_note_handles())
        else:
            return []

    def get_tag_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Tag in
        the database.
        """
        if (self.db is not None) and self.db.is_open():
            return list(self.iter_tag_handles())
        else:
            return []

    def get_default_person(self):
        """returns the default Person of the database"""
        return self.db.get_default_person()

    def get_default_handle(self):
        """returns the default Person of the database"""
        return self.db.get_default_handle()

    def iter_person_handles(self):
        """
        Return an iterator over database handles, one handle for each Person in
        the database.
        """
        return filter(self.include_person, self.db.iter_person_handles())

    def iter_family_handles(self):
        """
        Return an iterator over database handles, one handle for each Family in
        the database.
        """
        return filter(self.include_family, self.db.iter_family_handles())

    def iter_event_handles(self):
        """
        Return an iterator over database handles, one handle for each Event in
        the database.
        """
        return filter(self.include_event, self.db.iter_event_handles())

    def iter_source_handles(self):
        """
        Return an iterator over database handles, one handle for each Source in
        the database.
        """
        return filter(self.include_source, self.db.iter_source_handles())

    def iter_citation_handles(self):
        """
        Return an iterator over database handles, one handle for each Citation
        in the database.
        """
        return filter(self.include_citation, self.db.iter_citation_handles())

    def iter_place_handles(self):
        """
        Return an iterator over database handles, one handle for each Place in
        the database.
        """
        return filter(self.include_place, self.db.iter_place_handles())

    def iter_media_handles(self):
        """
        Return an iterator over database handles, one handle for each Media
        Object in the database.
        """
        return filter(self.include_media, self.db.iter_media_handles())

    def iter_repository_handles(self):
        """
        Return an iterator over database handles, one handle for each
        Repository in the database.
        """
        return filter(self.include_repository,
                      self.db.iter_repository_handles())

    def iter_note_handles(self):
        """
        Return an iterator over database handles, one handle for each Note in
        the database.
        """
        return filter(self.include_note, self.db.iter_note_handles())

    def iter_tag_handles(self):
        """
        Return an iterator over database handles, one handle for each Tag in
        the database.
        """
        return filter(self.include_tag, self.db.iter_tag_handles())

    def __iter_object(self, selector, method):
        """ Helper function to return an iterator over an object class """
        retval = filter(lambda obj:
                        ((selector is None) or selector(obj.handle)),
                        method())
        return retval

    def iter_people(self):
        """
        Return an iterator over Person objects in the database
        """
        return self.__iter_object(self.include_person,
                                  self.db.iter_people)

    def iter_families(self):
        """
        Return an iterator over Family objects in the database
        """
        return self.__iter_object(self.include_family,
                                  self.db.iter_families)

    def iter_events(self):
        """
        Return an iterator over Event objects in the database
        """
        return self.__iter_object(self.include_event,
                                  self.db.iter_events)

    def iter_places(self):
        """
        Return an iterator over Place objects in the database
        """
        return self.__iter_object(self.include_place,
                                  self.db.iter_places)

    def iter_sources(self):
        """
        Return an iterator over Source objects in the database
        """
        return self.__iter_object(self.include_source,
                                  self.db.iter_sources)

    def iter_citations(self):
        """
        Return an iterator over Citation objects in the database
        """
        return self.__iter_object(self.include_citation,
                                  self.db.iter_citations)

    def iter_media(self):
        """
        Return an iterator over Media objects in the database
        """
        return self.__iter_object(self.include_media,
                                  self.db.iter_media)

    def iter_repositories(self):
        """
        Return an iterator over Repositories objects in the database
        """
        return self.__iter_object(self.include_repository,
                                  self.db.iter_repositories)

    def iter_notes(self):
        """
        Return an iterator over Note objects in the database
        """
        return self.__iter_object(self.include_note,
                                  self.db.iter_notes)

    def iter_tags(self):
        """
        Return an iterator over Tag objects in the database
        """
        return self.__iter_object(self.include_tag,
                                  self.db.iter_tags)

    @staticmethod
    def gfilter(predicate, obj):
        """
        Returns obj if predicate is True or not callable, else returns None
        """
        if predicate is not None and obj is not None:
            return obj if predicate(obj.handle) else None
        return obj

    def __getattr__(self, name):
        """ Handle unknown attribute lookups """
        if name == "readonly":
            return True
        sname = name.split('_')
        if sname[:2] == ['get', 'unfiltered']:
            """
            Handle get_unfiltered calls.  Return the name of the access
            method for the base database object.  Call setattr before
            returning so that the lookup happens at most once for a given
            method call and a given object.
            """
            attr = getattr(self.basedb, 'get_' + sname[2] + '_from_handle')
            setattr(self, name, attr)
            return attr

        # if a write-method:
        if (name in DbWriteBase.__dict__ and
                not name.startswith("__") and
                type(DbWriteBase.__dict__[name]) is types.FunctionType):
            raise AttributeError
        # Default behaviour: lookup attribute in parent object
        return getattr(self.db, name)

    def get_person_from_handle(self, handle):
        """
        Finds a Person in the database from the passed gramps handle.
        If no such Person exists, None is returned.
        """
        return self.gfilter(self.include_person,
                            self.db.get_person_from_handle(handle))

    def get_family_from_handle(self, handle):
        """
        Finds a Family in the database from the passed gramps handle.
        If no such Family exists, None is returned.
        """
        return self.gfilter(self.include_family,
                            self.db.get_family_from_handle(handle))

    def get_event_from_handle(self, handle):
        """
        Finds a Event in the database from the passed gramps handle.
        If no such Event exists, None is returned.
        """
        return self.gfilter(self.include_event,
                            self.db.get_event_from_handle(handle))

    def get_source_from_handle(self, handle):
        """
        Finds a Source in the database from the passed gramps handle.
        If no such Source exists, None is returned.
        """
        return self.gfilter(self.include_source,
                            self.db.get_source_from_handle(handle))

    def get_citation_from_handle(self, handle):
        """
        Finds a Citation in the database from the passed gramps handle.
        If no such Citation exists, None is returned.
        """
        return self.gfilter(self.include_citation,
                            self.db.get_citation_from_handle(handle))

    def get_place_from_handle(self, handle):
        """
        Finds a Place in the database from the passed gramps handle.
        If no such Place exists, None is returned.
        """
        return self.gfilter(self.include_place,
                            self.db.get_place_from_handle(handle))

    def get_media_from_handle(self, handle):
        """
        Finds an Object in the database from the passed gramps handle.
        If no such Object exists, None is returned.
        """
        return self.gfilter(self.include_media,
                            self.db.get_media_from_handle(handle))

    def get_repository_from_handle(self, handle):
        """
        Finds a Repository in the database from the passed gramps handle.
        If no such Repository exists, None is returned.
        """
        return self.gfilter(self.include_repository,
                            self.db.get_repository_from_handle(handle))

    def get_note_from_handle(self, handle):
        """
        Finds a Note in the database from the passed gramps handle.
        If no such Note exists, None is returned.
        """
        return self.gfilter(self.include_note,
                            self.db.get_note_from_handle(handle))

    def get_tag_from_handle(self, handle):
        """
        Finds a Tag in the database from the passed gramps handle.
        If no such Tag exists, None is returned.
        """
        return self.gfilter(self.include_tag,
                            self.db.get_tag_from_handle(handle))

    def get_person_from_gramps_id(self, val):
        """
        Finds a Person in the database from the passed Gramps ID.
        If no such Person exists, None is returned.
        """
        return self.gfilter(self.include_person,
                            self.db.get_person_from_gramps_id(val))

    def get_family_from_gramps_id(self, val):
        """
        Finds a Family in the database from the passed Gramps ID.
        If no such Family exists, None is returned.
        """
        return self.gfilter(self.include_family,
                            self.db.get_family_from_gramps_id(val))

    def get_event_from_gramps_id(self, val):
        """
        Finds an Event in the database from the passed Gramps ID.
        If no such Event exists, None is returned.
        """
        return self.gfilter(self.include_event,
                            self.db.get_event_from_gramps_id(val))

    def get_place_from_gramps_id(self, val):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        return self.gfilter(self.include_place,
                            self.db.get_place_from_gramps_id(val))

    def get_source_from_gramps_id(self, val):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        return self.gfilter(self.include_source,
                            self.db.get_source_from_gramps_id(val))

    def get_citation_from_gramps_id(self, val):
        """
        Finds a Citation in the database from the passed gramps' ID.
        If no such Citation exists, None is returned.
        """
        return self.gfilter(self.include_citation,
                            self.db.get_citation_from_gramps_id(val))

    def get_media_from_gramps_id(self, val):
        """
        Finds a Media in the database from the passed gramps' ID.
        If no such Media exists, None is returned.
        """
        return self.gfilter(self.include_media,
                            self.db.get_media_from_gramps_id(val))

    def get_repository_from_gramps_id(self, val):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        return self.gfilter(self.include_repository,
                            self.db.get_repository_from_gramps_id(val))

    def get_note_from_gramps_id(self, val):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        return self.gfilter(self.include_note,
                            self.db.get_note_from_gramps_id(val))

    def get_tag_from_name(self, val):
        """
        Finds a Tag in the database from the passed tag name.
        If no such Tag exists, None is returned.
        """
        return self.gfilter(self.include_tag,
                            self.db.get_tag_from_name(val))

    def get_name_group_mapping(self, surname):
        """
        Return the default grouping name for a surname
        """
        return self.db.get_name_group_mapping(surname)

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
        return len(self.get_person_handles())

    def get_number_of_families(self):
        """
        Return the number of families currently in the database.
        """
        return len(self.get_family_handles())

    def get_number_of_events(self):
        """
        Return the number of events currently in the database.
        """
        return len(self.get_event_handles())

    def get_number_of_places(self):
        """
        Return the number of places currently in the database.
        """
        return len(self.get_place_handles())

    def get_number_of_sources(self):
        """
        Return the number of sources currently in the database.
        """
        return len(self.get_source_handles())

    def get_number_of_citations(self):
        """
        Return the number of Citations currently in the database.
        """
        return len(self.get_citation_handles())

    def get_number_of_media(self):
        """
        Return the number of media objects currently in the database.
        """
        return len(self.get_media_handles())

    def get_number_of_repositories(self):
        """
        Return the number of source repositories currently in the database.
        """
        return len(self.get_repository_handles())

    def get_number_of_notes(self):
        """
        Return the number of notes currently in the database.
        """
        return len(self.get_note_handles())

    def get_number_of_tags(self):
        """
        Return the number of tags currently in the database.
        """
        return len(self.get_tag_handles())

    def get_save_path(self):
        """returns the save path of the file, or "" if one does not exist"""
        return self.db.get_save_path()

    def get_event_attribute_types(self):
        """returns a list of all Attribute types associated with Event
        instances in the database"""
        return self.db.get_event_attribute_types()

    def get_event_types(self):
        """returns a list of all event types in the database"""
        return self.db.get_event_types()

    def get_person_event_types(self):
        """Deprecated:  Use get_event_types"""
        return self.db.get_event_types()

    def get_person_attribute_types(self):
        """returns a list of all Attribute types associated with Person
        instances in the database"""
        return self.db.get_person_attribute_types()

    def get_family_attribute_types(self):
        """returns a list of all Attribute types associated with Family
        instances in the database"""
        return self.db.get_family_attribute_types()

    def get_family_event_types(self):
        """Deprecated:  Use get_event_types"""
        return self.db.get_event_types()

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

    def get_origin_types(self):
        """
        returns a list of all custom origin types
        associated with Person/Surname
        instances in the database
        """
        return self.db.get_origin_types()

    def get_repository_types(self):
        """returns a list of all custom repository types associated with
        Repository instances in the database"""
        return self.db.get_repository_types()

    def get_note_types(self):
        """returns a list of all custom note types associated with
        Note instances in the database"""
        return self.db.get_note_types()

    def get_source_attribute_types(self):
        """returns a list of all Attribute types associated with
        Source/Citation instances in the database"""
        return self.db.get_source_attribute_types()

    def get_source_media_types(self):
        """returns a list of all custom source media types associated with
        Source instances in the database"""
        return self.db.get_source_media_types()

    def get_url_types(self):
        """returns a list of all custom names types associated with Url
        instances in the database"""
        return self.db.get_url_types()

    def get_raw_person_data(self, handle):
        return self.get_person_from_handle(handle).serialize()

    def get_raw_family_data(self, handle):
        return self.get_family_from_handle(handle).serialize()

    def get_raw_media_data(self, handle):
        return self.get_media_from_handle(handle).serialize()

    def get_raw_place_data(self, handle):
        return self.get_place_from_handle(handle).serialize()

    def get_raw_event_data(self, handle):
        return self.get_event_from_handle(handle).serialize()

    def get_raw_source_data(self, handle):
        return self.get_source_from_handle(handle).serialize()

    def get_raw_citation_data(self, handle):
        return self.get_citation_from_handle(handle).serialize()

    def get_raw_repository_data(self, handle):
        return self.get_repository_from_handle(handle).serialize()

    def get_raw_note_data(self, handle):
        return self.get_note_from_handle(handle).serialize()

    def get_raw_tag_data(self, handle):
        return self.get_tag_from_handle(handle).serialize()

    def has_person_handle(self, handle):
        """
        Returns True if the handle exists in the current Person database.
        """
        return self.gfilter(self.include_person,
                            self.db.get_person_from_handle(handle)
                           ) is not None

    def has_family_handle(self, handle):
        """
        Returns True if the handle exists in the current Family database.
        """
        return self.gfilter(self.include_family,
                            self.db.get_family_from_handle(handle)
                           ) is not None

    def has_event_handle(self, handle):
        """
        returns True if the handle exists in the current Event database.
        """
        return self.gfilter(self.include_event,
                            self.db.get_event_from_handle(handle)
                           ) is not None

    def has_source_handle(self, handle):
        """
        returns True if the handle exists in the current Source database.
        """
        return self.gfilter(self.include_source,
                            self.db.get_source_from_handle(handle)
                           ) is not None

    def has_citation_handle(self, handle):
        """
        returns True if the handle exists in the current Citation database.
        """
        return self.gfilter(self.include_citation,
                            self.db.get_citation_from_handle(handle)
                           ) is not None

    def has_place_handle(self, handle):
        """
        returns True if the handle exists in the current Place database.
        """
        return self.gfilter(self.include_place,
                            self.db.get_place_from_handle(handle)
                           ) is not None

    def has_media_handle(self, handle):
        """
        returns True if the handle exists in the current Mediadatabase.
        """
        return self.gfilter(self.include_media,
                            self.db.get_media_from_handle(handle)
                           ) is not None

    def has_repository_handle(self, handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return self.gfilter(self.include_repository,
                            self.db.get_repository_from_handle(handle)
                           ) is not None

    def has_note_handle(self, handle):
        """
        returns True if the handle exists in the current Note database.
        """
        return self.gfilter(self.include_note,
                            self.db.get_note_from_handle(handle)
                           ) is not None

    def has_tag_handle(self, handle):
        """
        returns True if the handle exists in the current Tag database.
        """
        return self.gfilter(self.include_tag,
                            self.db.get_tag_from_handle(handle)
                           ) is not None

    def get_mediapath(self):
        """returns the default media path of the database"""
        return self.db.get_mediapath()

    def get_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        return self.bookmarks

    def get_family_bookmarks(self):
        """returns the list of Family handles in the bookmarks"""
        return self.family_bookmarks

    def get_event_bookmarks(self):
        """returns the list of Event handles in the bookmarks"""
        return self.event_bookmarks

    def get_place_bookmarks(self):
        """returns the list of Place handles in the bookmarks"""
        return self.place_bookmarks

    def get_source_bookmarks(self):
        """returns the list of Source handles in the bookmarks"""
        return self.source_bookmarks

    def get_citation_bookmarks(self):
        """returns the list of Citation handles in the bookmarks"""
        return self.citation_bookmarks

    def get_media_bookmarks(self):
        """returns the list of Media handles in the bookmarks"""
        return self.media_bookmarks

    def get_repo_bookmarks(self):
        """returns the list of Repository handles in the bookmarks"""
        return self.repo_bookmarks

    def get_note_bookmarks(self):
        """returns the list of Note handles in the bookmarks"""
        return self.note_bookmarks

    def close(self):
        """
        Close on a proxy closes real database.
        """
        self.basedb.close()

    def find_initial_person(self):
        """
        Find an initial person, given that they might not be
        available.
        """
        person = self.basedb.find_initial_person()
        if person and self.has_person_handle(person.handle):
            return person
        else:
            return None

    def get_dbid(self):
        """
        Return the database ID.
        """
        return self.basedb.get_dbid()

