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
Read classes for the GRAMPS databases.
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

import logging

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
from gen.lib import (MediaObject, Person, Family, Source, Event, Place, 
                     Repository, Note, GenderStats, Researcher)
from gen.db.dbconst import *
from gen.utils.callback import Callback
from gen.db import (GrampsCursor, DbReadBase)
from Utils import create_id
import Errors
import config

LOG = logging.getLogger(DBLOGNAME)
#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
from gen.db.dbconst import *

_SIGBASE = ('person', 'family', 'source', 'event', 
            'media', 'place', 'repository', 'reference', 'note')

DBERRS      = (db.DBRunRecoveryError, db.DBAccessError, 
               db.DBPageNotFoundError, db.DBInvalidArgError)

class DbBookmarks(object):
    def __init__(self, default=[]):
        self.bookmarks = list(default) # want a copy (not an alias)

    def set(self, new_list):
        self.bookmarks = list(new_list)

    def get(self):
        return self.bookmarks

    def append(self, item):
        self.bookmarks.append(item)

    def append_list(self, blist):
        self.bookmarks += blist

    def remove(self, item):
        self.bookmarks.remove(item)

    def pop(self, item):
        return self.bookmarks.pop(item)

    def insert(self, pos, item):
        self.bookmarks.insert(pos, item)

#-------------------------------------------------------------------------
#
# GrampsDBReadCursor
#
#-------------------------------------------------------------------------
class DbReadCursor(GrampsCursor):

    def __init__(self, source, txn=None, **kwargs):
        GrampsCursor.__init__(self, txn=txn, **kwargs)
        self.cursor = source.db.cursor(txn)
        self.source = source

class DbEngine(object):
    """
    A collection of DbTables and related methods.
    """
    def __init__(self, *tables):
        self.tables = {}
        for table in tables:
            self.tables[table.name] = table

    def __getattr__(self, table):
        if table in self.tables:
            return self.tables[table]

    def __getitem__(self, item):
        if item in self.tables:
            return self.tables[item]

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        for item in self.tables.keys():
            yield item

    def __exit__(self, *args, **kwargs):
        pass

class DbTable(object):
    """
    An object to hold data related to a primary database schema.
    """
    def __init__(self, name, **kwargs):
        self.name = name
        self.settings = {}
        self.settings.update(kwargs)

    def update(self, **kwargs):
        self.settings.update(kwargs)

    def __getattr__(self, attr):
        if attr in self.settings:
            return self.settings[attr]

    def __getitem__(self, item):
        if item in self.settings:
            return self.settings[attr]

    def get(self, **kwargs):
        for keyword in kwargs:
            if keyword in self.settings:
                return self.settings[keyword](kwargs[keyword])


class DbBsddbRead(DbReadBase, Callback):
    """
    Read class for the GRAMPS databases.  Implements methods necessary to read
    the various object classes. Currently, there are eight (8) classes:

    Person, Family, Event, Place, Source, MediaObject, Repository and Note

    For each object class, there are methods to retrieve data in various ways.
    In the methods described below, <object> can be one of person, family,
    event, place, source, media_object, respository or note unless otherwise
    specified.

    .. method:: get_<object>_from_handle()
    
        returns an object given its handle

    .. method:: get_<object>_from_gramps_id()

        returns an object given its gramps id

    .. method:: get_<object>_cursor()

        returns a cursor over an object.  Example use::

            with get_person_cursor() as cursor:
                for handle, person in cursor:
                    # process person object pointed to by the handle

    .. method:: get_<object>_handles()

        returns a list of handles for the object type, optionally sorted
        (for Person, Place, Source and Media objects)

    .. method:: iter_<object>_handles()

        returns an iterator that yields one object handle per call.

    .. method:: iter_<objects>()

        returns an iterator that yields one object per call.
        The objects available are: people, families, events, places,
        sources, media_objects, repositories and notes.

    .. method:: get_<object>_event_types()

        returns a list of all Event types assocated with instances of <object>
        in the database.

    .. method:: get_<object>_attribute_types()

        returns a list of all Event types assocated with instances of <object>
        in the database.

    .. method:: get_<object>_column_order()

        returns the object's display common information.

    """

    # This holds a reference to the gramps Config module if
    # it is available, it is setup by the factory methods.
    __config__ = None
    __signals__ = {}
    # If this is True logging will be turned on.
    try:
        _LOG_ALL = int(os.environ.get('GRAMPS_SIGNAL', "0")) == 1
    except:
        _LOG_ALL = False

    def __init__(self):
        """
        Create a new DbBsddbRead instance. 
        """
        
        DbReadBase.__init__(self)
        Callback.__init__(self)

        self.engine = DbEngine(
            DbTable(
                "Person", 
                handle=self.get_person_from_handle, 
                gramps_id=self.get_person_from_gramps_id,
                _class=Person,
                _cursor=self.get_person_cursor,
                ),
            DbTable(
                'Family', 
                handle=self.get_family_from_handle, 
                gramps_id=self.get_family_from_gramps_id,
                _class=Family,
                _cursor=self.get_family_cursor,
                ),
            DbTable(
                'Source', 
                handle=self.get_source_from_handle, 
                gramps_id=self.get_source_from_gramps_id,
                _class=Source,
                _cursor=self.get_source_cursor,
                ),
            DbTable(
                'Event', 
                handle=self.get_event_from_handle, 
                gramps_id=self.get_event_from_gramps_id,
                _class=Event,
                _cursor=self.get_event_cursor,
                ),
            DbTable(
                'Media', 
                handle=self.get_object_from_handle, 
                gramps_id=self.get_object_from_gramps_id,
                _class=MediaObject,
                cursor=self.get_media_cursor,
                ),
            DbTable(
                'Place', 
                handle=self.get_place_from_handle, 
                gramps_id=self.get_place_from_gramps_id,
                _class=Place,
                _cursor=self.get_place_cursor,
                ),
            DbTable(
                'Repository', 
                handle=self.get_repository_from_handle, 
                gramps_id=self.get_repository_from_gramps_id,
                _class=Repository,
                _cursor=self.get_repository_cursor,
                ),
            DbTable(
                'Note', 
                handle=self.get_note_from_handle, 
                gramps_id=self.get_note_from_gramps_id,
                _class=Note,
                _cursor=self.get_note_cursor,
                ),
            )

        self.set_person_id_prefix('I%04d')
        self.set_object_id_prefix('O%04d')
        self.set_family_id_prefix('F%04d')
        self.set_source_id_prefix('S%04d')
        self.set_place_id_prefix('P%04d')
        self.set_event_id_prefix('E%04d')
        self.set_repository_id_prefix('R%04d')
        self.set_note_id_prefix('N%04d')

        self.readonly = False
        self.rand = random.Random(time.time())
        self.smap_index = 0
        self.emap_index = 0
        self.pmap_index = 0
        self.fmap_index = 0
        self.lmap_index = 0
        self.omap_index = 0
        self.rmap_index = 0
        self.nmap_index = 0
        self.db_is_open = False

        self.family_event_names = set()
        self.individual_event_names = set()
        self.individual_attributes = set()
        self.family_attributes = set()
        self.marker_names = set()
        self.child_ref_types = set()
        self.family_rel_types = set()
        self.event_role_names = set()
        self.name_types = set()
        self.repository_types = set()
        self.note_types = set()
        self.source_media_types = set()
        self.url_types = set()
        self.media_attributes = set()

        self.open = 0
        self.genderStats = GenderStats()

        self.undodb    = []
        self.id_trans  = {}
        self.fid_trans = {}
        self.pid_trans = {}
        self.sid_trans = {}
        self.oid_trans = {}
        self.rid_trans = {}
        self.nid_trans = {}
        self.eid_trans = {}
        self.env = None
        self.person_map = {}
        self.family_map = {}
        self.place_map  = {}
        self.source_map = {}
        self.repository_map  = {}
        self.note_map = {}
        self.media_map  = {}
        self.event_map  = {}
        self.metadata   = {}
        self.name_group = {}
        self.undo_callback = None
        self.redo_callback = None
        self.undo_history_callback = None
        self.modified   = 0

        #self.undoindex  = -1
        #self.translist  = [None] * DBUNDO
        self.abort_possible = True
        #self.undo_history_timestamp = 0
        self.default = None
        self.owner = Researcher()
        self.name_formats = []
        self.bookmarks = DbBookmarks()
        self.family_bookmarks = DbBookmarks()
        self.event_bookmarks = DbBookmarks()
        self.place_bookmarks = DbBookmarks()
        self.source_bookmarks = DbBookmarks()
        self.repo_bookmarks = DbBookmarks()
        self.media_bookmarks = DbBookmarks()
        self.note_bookmarks = DbBookmarks()
        self._bm_changes = 0
        self.path = ""
        self.surname_list = []
        self.txn = None
        self.has_changed = False

    def set_prefixes(self, person, media, family, source, place, event,
                     repository, note):
        self.person_prefix = self._validated_id_prefix(person, 'I')
        self.mediaobject_prefix = self._validated_id_prefix(media, 'M')
        self.family_prefix = self._validated_id_prefix(family, 'F')
        self.source_prefix = self._validated_id_prefix(source, 'S')
        self.place_prefix = self._validated_id_prefix(place, 'P')
        self.event_prefix = self._validated_id_prefix(event, 'E')
        self.repository_prefix = self._validated_id_prefix(repository, 'R')
        self.note_prefix = self._validated_id_prefix(note, 'N')

    def version_supported(self):
        """Return True when the file has a supported version."""
        return True

    def get_cursor(self, table, *args, **kwargs):
        try:
            return DbReadCursor(table, self.txn)
        except DBERRS, msg:
            self.__log_error()
            raise Errors.DbError(msg)

    def get_person_cursor(self, *args, **kwargs):
        return self.get_cursor(self.person_map, *args, **kwargs)

    def get_family_cursor(self, *args, **kwargs):
        return self.get_cursor(self.family_map, *args, **kwargs)

    def get_event_cursor(self, *args, **kwargs):
        return self.get_cursor(self.event_map, *args, **kwargs)

    def get_place_cursor(self, *args, **kwargs):
        return self.get_cursor(self.place_map, *args, **kwargs)

    def get_source_cursor(self, *args, **kwargs):
        return self.get_cursor(self.source_map, *args, **kwargs)

    def get_media_cursor(self, *args, **kwargs):
        return self.get_cursor(self.media_map, *args, **kwargs)

    def get_repository_cursor(self, *args, **kwargs):
        return self.get_cursor(self.repository_map, *args, **kwargs)

    def get_note_cursor(self, *args, **kwargs):
        return self.get_cursor(self.note_map, *args, **kwargs)

    def close(self):
        """
        Close the specified database. 
        
        The method needs to be overridden in the derived class.
        """
        pass
        
    def is_open(self):
        """
        Return 1 if the database has been opened.
        """
        return self.db_is_open

    def request_rebuild(self):
        """
        Notify clients that the data has changed significantly, and that all
        internal data dependent on the database should be rebuilt.
        """
        self.emit('person-rebuild')
        self.emit('family-rebuild')
        self.emit('place-rebuild')
        self.emit('source-rebuild')
        self.emit('media-rebuild')
        self.emit('event-rebuild')
        self.emit('repository-rebuild')
        self.emit('note-rebuild')

    @staticmethod
    def __find_next_gramps_id(prefix, map_index, trans):
        """
        Helper function for find_next_<object>_gramps_id methods
        """
        index = prefix % map_index
        while trans.has_key(str(index)):
            map_index += 1
            index = prefix % map_index
        map_index += 1
        return index
        
    def find_next_person_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Person object based off the 
        person ID prefix.
        """
        return self.__find_next_gramps_id(self.person_prefix,
                                          self.pmap_index, self.id_trans)

    def find_next_place_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Place object based off the 
        place ID prefix.
        """
        return self.__find_next_gramps_id(self.place_prefix,
                                          self.lmap_index, self.pid_trans)

    def find_next_event_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Event object based off the 
        event ID prefix.
        """
        return self.__find_next_gramps_id(self.event_prefix,
                                          self.emap_index, self.eid_trans)

    def find_next_object_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a MediaObject object based
        off the media object ID prefix.
        """
        return self.__find_next_gramps_id(self.mediaobject_prefix,
                                          self.omap_index, self.oid_trans)        

    def find_next_source_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Source object based off the 
        source ID prefix.
        """
        return self.__find_next_gramps_id(self.source_prefix,
                                          self.smap_index, self.sid_trans)

    def find_next_family_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Family object based off the 
        family ID prefix.
        """
        return self.__find_next_gramps_id(self.family_prefix,
                                          self.fmap_index, self.fid_trans)

    def find_next_repository_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Respository object based 
        off the repository ID prefix.
        """
        return self.__find_next_gramps_id(self.repository_prefix,
                                          self.rmap_index, self.rid_trans)        

    def find_next_note_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Note object based off the 
        note ID prefix.
        """
        return self.__find_next_gramps_id(self.note_prefix,
                                          self.nmap_index, self.nid_trans)          

    def get_by_name(self, name, handle):
        """
        Given one of the object names (not class_type) lookup the
        object by handle.
        """
        return self.engine[name].get(handle=handle)

    def get_by_gramps_id(self, name, gramps_id):
        """
        Given one of the object names (not class_type) lookup the
        object by handle.
        """
        return self.engine[name].get(gramps_id=gramps_id)

    def get_from_handle(self, handle, class_type, data_map):
        data = data_map.get(str(handle))
        if data:
            newobj = class_type()
            newobj.unserialize(data)
            return newobj
        return None

    def get_person_from_handle(self, handle):
        """
        Find a Person in the database from the passed gramps' ID.
        
        If no such Person exists, None is returned.
        """
        return self.get_from_handle(handle, Person, self.person_map)

    def get_source_from_handle(self, handle):
        """
        Find a Source in the database from the passed gramps' ID.
        
        If no such Source exists, None is returned.
        """
        return self.get_from_handle(handle, Source, self.source_map)

    def get_object_from_handle(self, handle):
        """
        Find an Object in the database from the passed gramps' ID.
        
        If no such Object exists, None is returned.
        """
        return self.get_from_handle(handle, MediaObject, self.media_map)

    def get_place_from_handle(self, handle):
        """
        Find a Place in the database from the passed gramps' ID.
        
        If no such Place exists, None is returned.
        """
        return self.get_from_handle(handle, Place, self.place_map)

    def get_event_from_handle(self, handle):
        """
        Find a Event in the database from the passed gramps' ID.
        
        If no such Event exists, None is returned.
        """
        return self.get_from_handle(handle, Event, self.event_map)

    def get_family_from_handle(self, handle):
        """
        Find a Family in the database from the passed gramps' ID.
        
        If no such Family exists, None is returned.
        """
        return self.get_from_handle(handle, Family, self.family_map)

    def get_repository_from_handle(self, handle):
        """
        Find a Repository in the database from the passed gramps' ID.
        
        If no such Repository exists, None is returned.
        """
        return self.get_from_handle(handle, Repository, self.repository_map)

    def get_note_from_handle(self, handle):
        """
        Find a Note in the database from the passed gramps' ID.
        
        If no such Note exists, None is returned.
        """
        return self.get_from_handle(handle, Note, self.note_map)

    def __get_obj_from_gramps_id(self, val, tbl, class_, prim_tbl):
        try:
            if tbl.has_key(str(val)):
                data = tbl.get(str(val), txn=self.txn)
                obj = class_()
                ### FIXME: this is a dirty hack that works without no
                ### sensible explanation. For some reason, for a readonly
                ### database, secondary index returns a primary table key
                ### corresponding to the data, not the data.
                if self.readonly:
                    tuple_data = prim_tbl.get(data, txn=self.txn)
                else:
                    tuple_data = cPickle.loads(data)
                obj.unserialize(tuple_data)
                return obj
            else:
                return None
        except DBERRS, msg:
            self.__log_error()
            raise Errors.DbError(msg)

    def get_person_from_gramps_id(self, val):
        """
        Find a Person in the database from the passed gramps' ID.
        
        If no such Person exists, None is returned.
        """
        return self.__get_obj_from_gramps_id(val, self.id_trans, Person,
                                             self.person_map)

    def get_family_from_gramps_id(self, val):
        """
        Find a Family in the database from the passed gramps' ID.
        
        If no such Family exists, None is return.
        """
        return self.__get_obj_from_gramps_id(val, self.fid_trans, Family,
                                             self.family_map)
    
    def get_event_from_gramps_id(self, val):
        """
        Find an Event in the database from the passed gramps' ID.
        
        If no such Family exists, None is returned.
        """
        return self.__get_obj_from_gramps_id(val, self.eid_trans, Event,
                                             self.event_map)

    def get_place_from_gramps_id(self, val):
        """
        Find a Place in the database from the passed gramps' ID.
        
        If no such Place exists, None is returned.
        """
        return self.__get_obj_from_gramps_id(val, self.pid_trans, Place,
                                             self.place_map)

    def get_source_from_gramps_id(self, val):
        """
        Find a Source in the database from the passed gramps' ID.
        
        If no such Source exists, None is returned.
        """
        return self.__get_obj_from_gramps_id(val, self.sid_trans, Source,
                                              self.source_map)

    def get_object_from_gramps_id(self, val):
        """
        Find a MediaObject in the database from the passed gramps' ID.
        
        If no such MediaObject exists, None is returned.
        """
        return self.__get_obj_from_gramps_id(val, self.oid_trans, MediaObject,
                                              self.media_map)

    def get_repository_from_gramps_id(self, val):
        """
        Find a Repository in the database from the passed gramps' ID.
        
        If no such Repository exists, None is returned.
        """
        return self.__get_obj_from_gramps_id(val, self.rid_trans, Repository,
                                              self.repository_map)

    def get_note_from_gramps_id(self, val):
        """
        Find a Note in the database from the passed gramps' ID.
        
        If no such Note exists, None is returned.
        """
        return self.__get_obj_from_gramps_id(val, self.nid_trans, Note,
                                              self.note_map)
 
    def get_name_group_mapping(self, name):
        """
        Return the default grouping name for a surname.
        """
        return unicode(self.name_group.get(str(name), name))

    def get_name_group_keys(self):
        """
        Return the defined names that have been assigned to a default grouping.
        """
        return [unicode(k) for k in self.name_group.keys()]

    def has_name_group_key(self, name):
        """
        Return if a key exists in the name_group table.
        """
        return self.name_group.has_key(str(name))

    def get_number_of_records(self, table):
        if not self.db_is_open:
            return 0
        if self.txn is None:
            return len(table)
        else:
            return table.stat(flags=db.DB_FAST_STAT, txn=self.txn)['nkeys']

    def get_number_of_people(self):
        """
        Return the number of people currently in the database.
        """
        return self.get_number_of_records(self.person_map)

    def get_number_of_families(self):
        """
        Return the number of families currently in the database.
        """
        return self.get_number_of_records(self.family_map)

    def get_number_of_events(self):
        """
        Return the number of events currently in the database.
        """
        return self.get_number_of_records(self.event_map)

    def get_number_of_places(self):
        """
        Return the number of places currently in the database.
        """
        return self.get_number_of_records(self.place_map)

    def get_number_of_sources(self):
        """
        Return the number of sources currently in the database.
        """
        return self.get_number_of_records(self.source_map)

    def get_number_of_media_objects(self):
        """
        Return the number of media objects currently in the database.
        """
        return self.get_number_of_records(self.media_map)

    def get_number_of_repositories(self):
        """
        Return the number of source repositories currently in the database.
        """
        return self.get_number_of_records(self.repository_map)

    def get_number_of_notes(self):
        """
        Return the number of notes currently in the database.
        """
        return self.get_number_of_records(self.note_map)

    def all_handles(self, table):
        return table.keys()
        
    def get_person_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Person in
        the database. 
        
        If sort_handles is True, the list is sorted by surnames.
        """
        if self.db_is_open:
            handle_list = self.all_handles(self.person_map)
            if sort_handles:
                handle_list.sort(key=self.__sortbyperson_key)
            return handle_list
        return []

        # Old code: does the same as above, but more complicated
        if self.db_is_open:
            if sort_handles:
                with self.get_person_cursor() as cursor:
                    slist = sorted((data[3][5], key) for key, data in cursor)
                return [x[1] for x in slist]
            else:
                return self.all_handles(self.person_map)
        return []

    def get_place_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Place in
        the database. 
        
        If sort_handles is True, the list is sorted by Place title.
        """

        if self.db_is_open:
            handle_list = self.all_handles(self.place_map)
            if sort_handles:
                handle_list.sort(key=self.__sortbyplace_key)
            return handle_list
        return []

        # Old code: does the same as above, but more complicated
        if self.db_is_open:
            if sort_handles:
                with self.get_place_cursor() as cursor:
                    slist = sorted((data[2], key) for key, data in cursor)
                return [x[1] for x in slist]
            else:
                return self.all_handles(self.place_map)
        return []
        
    def get_source_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Source in
        the database.
        
         If sort_handles is True, the list is sorted by Source title.
        """
        if self.db_is_open:
            handle_list = self.all_handles(self.source_map)
            if sort_handles:
                handle_list.sort(key=self.__sortbysource_key)
            return handle_list
        return []
        
    def get_media_object_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each MediaObject in
        the database. 
        
        If sort_handles is True, the list is sorted by title.
        """
        if self.db_is_open:
            handle_list = self.all_handles(self.media_map)
            if sort_handles:
                handle_list.sort(key=self.__sortbymedia_key)
            return handle_list
        return []
        
    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in the 
        database. 
        """
        if self.db_is_open:
            return self.all_handles(self.event_map)
        return []
        
    def get_family_handles(self):
        """
        Return a list of database handles, one handle for each Family in
        the database.
        """
        if self.db_is_open:
            return self.all_handles(self.family_map)
        return []
        
    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository in
        the database.
        """
        if self.db_is_open:
            return self.all_handles(self.repository_map)
        return []
        
    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in the 
        database.
        """
        if self.db_is_open:
            return self.all_handles(self.note_map)
        return []

    def _f(curs_):
        """
        Closure that returns an iterator over handles in the database.
        """
        def g(self):
            with curs_(self) as cursor:
                for key, data in cursor:
                    yield key
        return g

    # Use closure to define iterators for each primary object type

    iter_person_handles       = _f(get_person_cursor)
    iter_family_handles       = _f(get_family_cursor)
    iter_event_handles        = _f(get_event_cursor)
    iter_place_handles        = _f(get_place_cursor)
    iter_source_handles       = _f(get_source_cursor)
    iter_media_object_handles = _f(get_media_cursor)
    iter_repository_handles   = _f(get_repository_cursor)
    iter_note_handles         = _f(get_note_cursor)
    del _f
    
    def _f(curs_, obj_):
        """
        Closure that returns an iterator over objects in the database.
        """
        def g(self):
            with curs_(self) as cursor:
                for key, data in cursor:
                    obj = obj_()
                    obj.unserialize(data)
                    yield obj
        return g

    # Use closure to define iterators for each primary object type
    
    iter_people        = _f(get_person_cursor, Person)
    iter_families      = _f(get_family_cursor, Family)
    iter_events        = _f(get_event_cursor, Event)
    iter_places        = _f(get_place_cursor, Place)
    iter_sources       = _f(get_source_cursor, Source)
    iter_media_objects = _f(get_media_cursor, MediaObject)
    iter_repositories  = _f(get_repository_cursor, Repository)
    iter_notes         = _f(get_note_cursor, Note)
    del _f

    def get_gramps_ids(self, obj_key):
        key2table = {
            PERSON_KEY:     self.id_trans, 
            FAMILY_KEY:     self.fid_trans, 
            SOURCE_KEY:     self.sid_trans, 
            EVENT_KEY:      self.eid_trans, 
            MEDIA_KEY:      self.oid_trans, 
            PLACE_KEY:      self.pid_trans, 
            REPOSITORY_KEY: self.rid_trans, 
            NOTE_KEY:       self.nid_trans, 
            }

        table = key2table[obj_key]
        return table.keys()

    def has_gramps_id(self, obj_key, gramps_id):
        key2table = {
            PERSON_KEY:     self.id_trans, 
            FAMILY_KEY:     self.fid_trans, 
            SOURCE_KEY:     self.sid_trans, 
            EVENT_KEY:      self.eid_trans, 
            MEDIA_KEY:      self.oid_trans, 
            PLACE_KEY:      self.pid_trans, 
            REPOSITORY_KEY: self.rid_trans, 
            NOTE_KEY:       self.nid_trans, 
            }

        table = key2table[obj_key]
        #return str(gramps_id) in table
        return table.has_key(str(gramps_id))

    def find_initial_person(self):
        person = self.get_default_person()
        if not person:
            the_ids = self.get_gramps_ids(PERSON_KEY)
            if the_ids:
                person = self.get_person_from_gramps_id(min(the_ids))
        return person

    @staticmethod
    def _validated_id_prefix(val, default):
        if isinstance(val, basestring) and val:
            try:
                str_ = val % 1
            except TypeError:           # missing conversion specifier
                prefix_var = val + "%d"
            else:
                prefix_var = val        # OK as given
        else:
            prefix_var = default+"%04d" # not a string or empty string
        return prefix_var

    def set_person_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Person ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as I%d or I%04d.
        """
        self.person_prefix = self._validated_id_prefix(val, "I")

    def set_source_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Source ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as S%d or S%04d.
        """
        self.source_prefix = self._validated_id_prefix(val, "S")
            
    def set_object_id_prefix(self, val):
        """
        Set the naming template for GRAMPS MediaObject ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as O%d or O%04d.
        """
        self.mediaobject_prefix = self._validated_id_prefix(val, "O")

    def set_place_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Place ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as P%d or P%04d.
        """
        self.place_prefix = self._validated_id_prefix(val, "P")

    def set_family_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Family ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as F%d
        or F%04d.
        """
        self.family_prefix = self._validated_id_prefix(val, "F")

    def set_event_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Event ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as E%d or E%04d.
        """
        self.event_prefix = self._validated_id_prefix(val, "E")

    def set_repository_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Repository ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as R%d or R%04d.
        """
        self.repository_prefix = self._validated_id_prefix(val, "R")

    def set_note_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Note ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as N%d or N%04d.
        """
        self.note_prefix = self._validated_id_prefix(val, "N")

    def set_undo_callback(self, callback):
        """
        Define the callback function that is called whenever an undo operation
        is executed. 
        
        The callback function receives a single argument that is a text string 
        that defines the operation.
        """
        self.undo_callback = callback

    def set_redo_callback(self, callback):
        """
        Define the callback function that is called whenever an redo operation
        is executed. 
        
        The callback function receives a single argument that is a text string 
        that defines the operation.
        """
        self.redo_callback = callback

    def get_surname_list(self):
        """
        Return the list of locale-sorted surnames contained in the database.
        """
        return self.surname_list

    def get_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        return self.bookmarks

    def get_family_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        return self.family_bookmarks

    def get_event_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        return self.event_bookmarks

    def get_place_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        return self.place_bookmarks

    def get_source_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        return self.source_bookmarks

    def get_media_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        return self.media_bookmarks

    def get_repo_bookmarks(self):
        """Return the list of Person handles in the bookmarks."""
        return self.repo_bookmarks

    def get_note_bookmarks(self):
        """Return the list of Note handles in the bookmarks."""
        return self.note_bookmarks

    def set_researcher(self, owner):
        """Set the information about the owner of the database."""
        self.owner.set_from(owner)

    def get_researcher(self):
        """
        Return the Researcher instance, providing information about the owner 
        of the database.
        """
        return self.owner

    def get_default_person(self):
        """Return the default Person of the database."""
        person = self.get_person_from_handle(self.get_default_handle())
        if person:
            return person
        elif (self.metadata is not None) and (not self.readonly):
            self.metadata['default'] = None
        return None

    def get_default_handle(self):
        """Return the default Person of the database."""
        if self.metadata is not None:
            return self.metadata.get('default')
        return None

    def get_save_path(self):
        """Return the save path of the file, or "" if one does not exist."""
        return self.path

    def set_save_path(self, path):
        """Set the save path for the database."""
        self.path = path

    def get_person_event_types(self):
        """
        Return a list of all Event types assocated with Person instances in 
        the database.
        """
        return list(self.individual_event_names)

    def get_person_attribute_types(self):
        """
        Return a list of all Attribute types assocated with Person instances 
        in the database.
        """
        return list(self.individual_attributes)

    def get_family_attribute_types(self):
        """
        Return a list of all Attribute types assocated with Family instances 
        in the database.
        """
        return list(self.family_attributes)

    def get_family_event_types(self):
        """
        Return a list of all Event types assocated with Family instances in 
        the database.
        """
        return list(self.family_event_names)

    def get_marker_types(self):
        """
        Return a list of all marker types available in the database.
        """
        return list(self.marker_names)
        
    def get_media_attribute_types(self):
        """
        Return a list of all Attribute types assocated with Media and MediaRef 
        instances in the database.
        """
        return list(self.media_attributes)

    def get_family_relation_types(self):
        """
        Return a list of all relationship types assocated with Family
        instances in the database.
        """
        return list(self.family_rel_types)

    def get_child_reference_types(self):
        """
        Return a list of all child reference types assocated with Family
        instances in the database.
        """
        return list(self.child_ref_types)

    def get_event_roles(self):
        """
        Return a list of all custom event role names assocated with Event
        instances in the database.
        """
        return list(self.event_role_names)

    def get_name_types(self):
        """
        Return a list of all custom names types assocated with Person
        instances in the database.
        """
        return list(self.name_types)

    def get_repository_types(self):
        """
        Return a list of all custom repository types assocated with Repository 
        instances in the database.
        """
        return list(self.repository_types)

    def get_note_types(self):
        """
        Return a list of all custom note types assocated with Note instances 
        in the database.
        """
        return list(self.note_types)

    def get_source_media_types(self):
        """
        Return a list of all custom source media types assocated with Source 
        instances in the database.
        """
        return list(self.source_media_types)

    def get_url_types(self):
        """
        Return a list of all custom names types assocated with Url instances 
        in the database.
        """
        return list(self.url_types)

    def __log_error(self):
        pass            

    def __get_raw_data(self, table, handle):
        """
        Helper method for get_raw_<object>_data methods
        """
        try:
            return table.get(str(handle), txn=self.txn)
        except DBERRS, msg:
            self.__log_error()
            raise Errors.DbError(msg)
    
    def get_raw_person_data(self, handle):
        return self.__get_raw_data(self.person_map, handle)

    def get_raw_family_data(self, handle):
        return self.__get_raw_data(self.family_map, handle)

    def get_raw_object_data(self, handle):
        return self.__get_raw_data(self.media_map, handle)

    def get_raw_place_data(self, handle):
        return self.__get_raw_data(self.place_map, handle)

    def get_raw_event_data(self, handle):
        return self.__get_raw_data(self.event_map, handle)

    def get_raw_source_data(self, handle):
        return self.__get_raw_data(self.source_map, handle)

    def get_raw_repository_data(self, handle):
        return self.__get_raw_data(self.repository_map, handle)

    def get_raw_note_data(self, handle):
        return self.__get_raw_data(self.note_map, handle)
        
    def __has_handle(self, table, handle):
        """
        Helper function for has_<object>_handle methods
        """
        try:
            return table.get(str(handle), txn=self.txn) is not None
        except DBERRS, msg:
            self.__log_error()
            raise Errors.DbError(msg)
        
    def has_person_handle(self, handle):
        """
        Return True if the handle exists in the current Person database.
        """
        return self.__has_handle(self.person_map, handle)

    def has_family_handle(self, handle):            
        """
        Return True if the handle exists in the current Family database.
        """
        return self.__has_handle(self.family_map, handle)

    def has_object_handle(self, handle):
        """
        Return True if the handle exists in the current MediaObjectdatabase.
        """
        return self.__has_handle(self.media_map, handle)

    def has_repository_handle(self, handle):
        """
        Return True if the handle exists in the current Repository database.
        """
        return self.__has_handle(self.repository_map, handle)

    def has_note_handle(self, handle):
        """
        Return True if the handle exists in the current Note database.
        """
        return self.__has_handle(self.note_map, handle)

    def has_event_handle(self, handle):
        """
        Return True if the handle exists in the current Event database.
        """
        return self.__has_handle(self.event_map, handle)

    def has_place_handle(self, handle):
        """
        Return True if the handle exists in the current Place database.
        """
        return self.__has_handle(self.place_map, handle)

    def has_source_handle(self, handle):
        """
        Return True if the handle exists in the current Source database.
        """
        return self.__has_handle(self.source_map, handle)

    def __sortbyperson_key(self, person):
        return locale.strxfrm(self.person_map.get(str(person))[3][5])

    def __sortbyplace(self, first, second):
        return locale.strcoll(self.place_map.get(str(first))[2], 
                              self.place_map.get(str(second))[2])

    def __sortbyplace_key(self, place):
        return locale.strxfrm(self.place_map.get(str(place))[2])

    def __sortbysource(self, first, second):
        source1 = unicode(self.source_map[str(first)][2])
        source2 = unicode(self.source_map[str(second)][2])
        return locale.strcoll(source1, source2)
        
    def __sortbysource_key(self, key):
        source = unicode(self.source_map[str(key)][2])
        return locale.strxfrm(source)

    def __sortbymedia(self, first, second):
        media1 = self.media_map[str(first)][4]
        media2 = self.media_map[str(second)][4]
        return locale.strcoll(media1, media2)

    def __sortbymedia_key(self, key):
        media = self.media_map[str(key)][4]
        return locale.strxfrm(media)

    def set_mediapath(self, path):
        """Set the default media path for database, path should be utf-8."""
        if (self.metadata is not None) and (not self.readonly):
            self.metadata['mediapath'] = path

    def get_mediapath(self):
        """Return the default media path of the database."""
        if self.metadata is not None:
            return self.metadata.get('mediapath', None)
        return None

    def set_column_order(self, col_list, name):
        if (self.metadata is not None) and (not self.readonly):
            self.metadata[name] = col_list

    def set_person_column_order(self, col_list):
        """
        Store the Person display common information in the database's metadata.
        """
        self.set_column_order(col_list, PERSON_COL_KEY)

    def set_family_list_column_order(self, col_list):
        """
        Store the Person display common information in the database's metadata.
        """
        self.set_column_order(col_list, FAMILY_COL_KEY)

    def set_child_column_order(self, col_list):
        """
        Store the Person display common information in the database's metadata.
        """
        self.set_column_order(col_list, CHILD_COL_KEY)

    def set_place_column_order(self, col_list):
        """
        Store the Place display common information in the database's metadata.
        """
        self.set_column_order(col_list, PLACE_COL_KEY)

    def set_source_column_order(self, col_list):
        """
        Store the Source display common information in the database's metadata.
        """
        self.set_column_order(col_list, SOURCE_COL_KEY)

    def set_media_column_order(self, col_list):
        """
        Store the Media display common information in the database's metadata.
        """
        self.set_column_order(col_list, MEDIA_COL_KEY)

    def set_event_column_order(self, col_list):
        """
        Store the Event display common information in the database's metadata.
        """
        self.set_column_order(col_list, EVENT_COL_KEY)

    def set_repository_column_order(self, col_list):
        """
        Store the Repository display common information in the database's 
        metadata.
        """
        self.set_column_order(col_list, REPOSITORY_COL_KEY)

    def set_note_column_order(self, col_list):
        """
        Store the Note display common information in the database's metadata.
        """
        self.set_column_order(col_list, NOTE_COL_KEY)

    def __get_column_order(self, name):
        default = config.get_default(name)
        cols = config.get(name)
        if len(cols) != len(default):
            return cols + default[len(cols):]
        else:
            return cols
        
    def get_person_column_order(self):
        """
        Return the Person display common information stored in the database's 
        metadata.
        """
        return self.__get_column_order(PERSON_COL_KEY)

    def __get_columns(self, key):
        default = config.get_default(key)
        values = self.__get_column_order(key)
        new = []
        for val in values:
            if len(val) == 2:
                for x in default:
                    if val[1] == x[1]:
                        new.append((val[0], val[1], x[2]))
                        break
            else:
                new.append(val)
        return new
        
    def get_family_list_column_order(self):
        """
        Return the Person display common information stored in the database's 
        metadata.
        """
        return self.__get_columns(FAMILY_COL_KEY)

    def get_child_column_order(self):
        """
        Return the Person display common information stored in the database's 
        metadata.
        """
        return self.__get_column_order(CHILD_COL_KEY)

    def get_place_column_order(self):
        """
        Return the Place display common information stored in thedatabase's 
        metadata.
        """
        return self.__get_columns(PLACE_COL_KEY)

    def get_source_column_order(self):
        """
        Return the Source display common information stored in the database's 
        metadata.
        """
        return self.__get_columns(SOURCE_COL_KEY)

    def get_media_column_order(self):
        """
        Return the MediaObject display common information stored in the
        database's metadata.
        """
        return self.__get_columns(MEDIA_COL_KEY)

    def get_event_column_order(self):
        """
        Return the Event display common information stored in the database's 
        metadata.
        """
        return self.__get_columns(EVENT_COL_KEY)

    def get_repository_column_order(self):
        """
        Return the Repository display common information stored in the
        database's metadata.
        """
        return self.__get_columns(REPOSITORY_COL_KEY)

    def get_note_column_order(self):
        """
        Return the Note display common information stored in the database's 
        metadata.
        """
        return self.__get_columns(NOTE_COL_KEY)

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        
        Returns an interator over alist of (class_name, handle) tuples.

        :param handle: handle of the object to search for.
        :type handle: database handle
        :param include_classes: list of class names to include in the results.
            Defaults to None, which includes all classes.
        :type include_classes: list of class names
        
        This default implementation does a sequencial scan through all
        the primary object databases and is very slow. Backends can
        override this method to provide much faster implementations that
        make use of additional capabilities of the backend.

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use::

            result_list = list(find_backlink_handles(handle))
        """
        assert False, "read:find_backlink_handles -- shouldn't get here!!!"
        # Make a dictionary of the functions and classes that we need for
        # each of the primary object tables.
        primary_tables = {
            'Person': {
                'cursor_func': self.get_person_cursor, 
                'class_func': Person,
                }, 
            'Family': {
                'cursor_func': self.get_family_cursor, 
                'class_func': Family,
                }, 
            'Event': {
                'cursor_func': self.get_event_cursor, 
                'class_func': Event,
                }, 
            'Place': {
                'cursor_func': self.get_place_cursor, 
                'class_func': Place,
                }, 
            'Source': {
                'cursor_func': self.get_source_cursor, 
                'class_func': Source,
                }, 
            'MediaObject': {
                'cursor_func': self.get_media_cursor, 
                'class_func': MediaObject,
                }, 
            'Repository': {
                'cursor_func': self.get_repository_cursor, 
                'class_func': Repository,
                },
            'Note':   {
                'cursor_func': self.get_note_cursor, 
                'class_func': Note,
                },
            }

        # Find which tables to iterate over
        if (include_classes is None):
            the_tables = primary_tables.keys()
        else:
            the_tables = include_classes
        
        # Now we use the functions and classes defined above to loop through
        # each of the existing primary object tables
        for primary_table_name, funcs in the_tables.iteritems():
            with funcs['cursor_func']() as cursor:

            # Grab the real object class here so that the lookup does
            # not happen inside the main loop.
                class_func = funcs['class_func']
                for found_handle, val in cursor:
                    obj = class_func()
                    obj.unserialize(val)

                    # Now we need to loop over all object types
                    # that have been requests in the include_classes list
                    for classname in primary_tables:               
                        if obj.has_handle_reference(classname, handle):
                            yield (primary_table_name, found_handle)
        return

    def report_bm_change(self):
        """
        Add 1 to the number of bookmark changes during this session.
        """
        self._bm_changes += 1

    def db_has_bm_changes(self):
        """
        Return whethere there were bookmark changes during the session.
        """
        return self._bm_changes > 0

