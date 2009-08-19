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

# $Id: read.py 12786 2009-07-11 15:32:37Z gburto01 $

"""
Read class for the GRAMPS databases.
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
from gen.db.cursor import GrampsCursor
from gen.db.iterator import CursorIterator
from gen.db.base import GrampsDbBase
from Utils import create_id
import Errors

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

class GrampsDbBookmarks(object):
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
class GrampsDbReadCursor(GrampsCursor):

    def __init__(self, source, txn=None):
        self.cursor = source.db.cursor(txn)
        self.source = source

class GrampsDbRead(GrampsDbBase, Callback):
    """
    GRAMPS database read access object. 
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
        Create a new GrampsDbRead instance. 
        """
        
        GrampsDbBase.__init__(self)
        #Callback.__init__(self)

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
        self.bookmarks = GrampsDbBookmarks()
        self.family_bookmarks = GrampsDbBookmarks()
        self.event_bookmarks = GrampsDbBookmarks()
        self.place_bookmarks = GrampsDbBookmarks()
        self.source_bookmarks = GrampsDbBookmarks()
        self.repo_bookmarks = GrampsDbBookmarks()
        self.media_bookmarks = GrampsDbBookmarks()
        self.note_bookmarks = GrampsDbBookmarks()
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

    def __get_cursor(self, table):
        try:
            return GrampsDbReadCursor(table, self.txn)
        except DBERRS, msg:
            self.__log_error()
            raise Errors.DbError(msg)

    def get_person_cursor(self):
        return self.__get_cursor(self.person_map)

    def get_family_cursor(self):
        return self.__get_cursor(self.family_map)

    def get_event_cursor(self):
        return self.__get_cursor(self.event_map)

    def get_place_cursor(self):
        return self.__get_cursor(self.place_map)

    def get_source_cursor(self):
        return self.__get_cursor(self.source_map)

    def get_media_cursor(self):
        return self.__get_cursor(self.media_map)

    def get_repository_cursor(self):
        return self.__get_cursor(self.repository_map)

    def get_note_cursor(self):
        return self.__get_cursor(self.note_map)

    def get_person_cursor_iter(self, msg=_("Processing Person records")):
        return CursorIterator(self, self.get_person_cursor(), msg)

    def get_family_cursor_iter(self, msg=_("Processing Family records")):
        return CursorIterator(self, self.get_family_cursor(), msg)

    def get_event_cursor_iter(self, msg=_("Processing Event records")):
        return CursorIterator(self, self.get_event_cursor(), msg)

    def get_place_cursor_iter(self, msg=_("Processing Place records")):
        return CursorIterator(self, self.get_place_cursor(), msg)

    def get_source_cursor_iter(self, msg=_("Processing Source records")):
        return CursorIterator(self, self.get_source_cursor(), msg)

    def get_media_cursor_iter(self, msg=_("Processing Media records")):
        return CursorIterator(self, self.get_media_cursor(), msg)

    def get_repository_cursor_iter(self, msg=_("Processing Repository records")):
        return CursorIterator(self, self.get_repository_cursor(), msg)

    def get_note_cursor_iter(self, msg=_("Processing Note records")):
        return CursorIterator(self, self.get_note_cursor(), msg)

    def load(self, name, callback, mode=DBMODE_R):
        """
        Open the specified database. 
        
        The method needs to be overridden in the derived class.
        """
        raise NotImplementedError

    def load_from(self, other_database, filename, callback):
        """
        Load data from the other database into itself.
        
        The filename is the name of the file for the newly created database.
        The method needs to be overridden in the derived class.
        """
        raise NotImplementedError

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

    def set_name_group_mapping(self, name, group):
        """
        Set the default grouping name for a surname. 
        
        Needs to be overridden in the derived class.
        """
        raise NotImplementedError
        
    @staticmethod
    def get_number_of_records(table):
        return len(table)

    def get_number_of_people(self):
        """
        Return the number of people currently in the database.
        """
        if self.db_is_open:
            return self.get_number_of_records(self.person_map)
            #return len(self.person_map)
        else:
            return 0

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
        return len(self.media_map)

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
            if sort_handles:
                with self.get_person_cursor() as cursor:
                    slist = sorted((data[3][5], key) for key, data in cursor)
                return [x[1] for x in slist]
            else:
                return self.all_handles(self.person_map)
        return []

    def iter_person_handles(self):
        """
        Return an iterator over handles for Persons in the database
        """
        with self.get_person_cursor() as cursor:
            for key, data in cursor:
                yield key
                
    def iter_people(self):
        """
        Return an iterator over handles and objects for Persons in the database
        """
        with self.get_person_cursor() as cursor:
            for handle, data in cursor:
                person = Person()
                person.unserialize(data)
                yield handle, person

    def get_place_handles(self, sort_handles=True):
        """
        Return a list of database handles, one handle for each Place in
        the database. 
        
        If sort_handles is True, the list is sorted by Place title.
        """
        if self.db_is_open:
            if sort_handles:
                with self.get_place_cursor() as cursor:
                    slist = sorted((data[2], key) for key, data in cursor)
                return [x[1] for x in slist]
            else:
                return self.all_handles(self.place_map)
        return []
        
    def iter_place_handles(self):
        """
        Return an iterator over handles for Places in the database
        """
        with self.get_place_cursor() as cursor:
            for key, data in cursor:
                yield key
                
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
        
    def iter_source_handles(self):
        """
        Return an iterator over handles for Sources in the database
        """
        with self.get_source_cursor() as cursor:
            for key, data in cursor:
                yield key
                
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
        
    def iter_media_object_handles(self):
        """
        Return an iterator over handles for Media in the database
        """
        with self.get_media_cursor() as cursor:
            for key, data in cursor:
                yield key

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in the 
        database. 
        """
        if self.db_is_open:
            return self.all_handles(self.event_map)
        return []
        
    def iter_event_handles(self):
        """
        Return an iterator over handles for Events in the database
        """
        with self.get_event_cursor() as cursor:
            for key, data in cursor:
                yield key

    def get_family_handles(self):
        """
        Return a list of database handles, one handle for each Family in
        the database.
        """
        if self.db_is_open:
            return self.all_handles(self.family_map)
        return []
        
    def iter_family_handles(self):
        """
        Return an iterator over handles for Families in the database
        """
        with self.get_family_cursor() as cursor:
            for key, data in cursor:
                yield key        

    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository in
        the database.
        """
        if self.db_is_open:
            return self.all_handles(self.repository_map)
        return []
        
    def iter_repository_handles(self):
        """
        Return an iterator over handles for Repositories in the database
        """
        with self.get_repository_cursor() as cursor:
            for key, data in cursor:
                yield key 

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in the 
        database.
        """
        if self.db_is_open:
            return self.all_handles(self.note_map)
        return []
        
    def iter_note_handles(self):
        """
        Return an iterator over handles for Notes in the database
        """
        with self.get_note_cursor() as cursor:
            for key, data in cursor:
                yield key

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

    def _validated_id_prefix(self, val, default):
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

    def build_surname_list(self):
        """
        Build the list of locale-sorted surnames contained in the database.
        
        The function must be overridden in the derived class.
        """
        raise NotImplementedError

    def sort_surname_list(self):
        """
        Sort the surname list in place.
        """
        raise NotImplementedError

    def add_to_surname_list(self, person, batch_transaction):
        """
        Check to see if the surname of the given person is already in
        the surname list. 
        
        If not then we need to add the name to the list.
        The function must be overridden in the derived class.
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

    def __get_column_order(self, name, default):
        if self.metadata is None:
            return default
        else:
            cols = self.metadata.get(name, default)
            if len(cols) != len(default):
                return cols + default[len(cols):]
            else:
                return cols

    def get_person_column_order(self):
        """
        Return the Person display common information stored in the database's 
        metadata.
        """
        default = [(1, 1, 100), (1, 2, 100), (1, 3, 150), (0, 4, 150),
                   (1, 5, 150), (0, 6, 150), (0, 7, 100), (0, 8, 100),
                   ]
        return self.__get_column_order(PERSON_COL_KEY, default)

    def __get_columns(self, key, default):
        values = self.__get_column_order(key, default)
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
        default = [(1, 0, 75), (1, 1, 200), (1, 2, 200), (1, 3, 100),
                   (0, 4, 100)]
        return self.__get_columns(FAMILY_COL_KEY, default)

    def get_child_column_order(self):
        """
        Return the Person display common information stored in the database's 
        metadata.
        """
        default = [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
                   (0, 6), (0, 7)]
        return self.__get_column_order(CHILD_COL_KEY, default)

    def get_place_column_order(self):
        """
        Return the Place display common information stored in thedatabase's 
        metadata.
        """
        default = [(1, 0, 250), (1, 1, 75), (1, 11, 100), (0, 3, 100),
                   (1, 4, 100, ), (0, 5, 150), (1, 6, 150), (0, 7, 150),
                   (0, 8, 150), (0, 9, 150), (0, 10, 150),(0,2,100)]
        return self.__get_columns(PLACE_COL_KEY, default)

    def get_source_column_order(self):
        """
        Return the Source display common information stored in the database's 
        metadata.
        """
        default = [(1, 0, 200), (1, 1, 75), (1, 2, 150), (0, 3, 100),
                   (1, 4, 150), (0, 5, 100)]
        return self.__get_columns(SOURCE_COL_KEY, default)

    def get_media_column_order(self):
        """
        Return the MediaObject display common information stored in the
        database's metadata.
        """
        default = [(1, 0, 200, ), (1, 1, 75), (1, 2, 100), (1, 3, 200),
                   (1, 5, 150), (0, 4, 150)]
        return self.__get_columns(MEDIA_COL_KEY, default)

    def get_event_column_order(self):
        """
        Return the Event display common information stored in the database's 
        metadata.
        """
        default = [(1, 0, 200), (1, 1, 75), (1, 2, 100), (1, 3, 150),
                   (1, 4, 200), (0, 5, 100)]
        return self.__get_columns(EVENT_COL_KEY, default)

    def get_repository_column_order(self):
        """
        Return the Repository display common information stored in the
        database's metadata.
        """
        default = [(1, 0, 200), (1, 1, 75), (0, 5, 100), (0, 6, 100),
                   (1, 2, 100), (1, 3, 250), (1, 4, 100), (0, 7, 100),
                   (0, 8, 100), (0, 9, 100), (0, 10, 100), (0, 12, 100)]
        return self.__get_columns(REPOSITORY_COL_KEY, default)

    def get_note_column_order(self):
        """
        Return the Note display common information stored in the database's 
        metadata.
        """
        default = [(1, 0, 350), (1, 1, 75), (1, 2, 100), (1, 3, 100)]
        return self.__get_columns(NOTE_COL_KEY, default)

    def delete_primary_from_reference_map(self, handle, transaction):
        """
        Called each time an object is removed from the database. 
        
        This can be used by subclasses to update any additional index tables 
        that might need to be changed.
        """
        pass

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

        >    result_list = list(ind_backlink_handles(handle))
        """
        assert False, "read:find_backlink_handles -- shouldn't get here!!!"
        # Make a dictionary of the functions and classes that we need for
        # each of the primary object tables.
        primary_tables = {
            'Person': {'cursor_func': self.get_person_cursor, 
                       'class_func': Person}, 
            'Family': {'cursor_func': self.get_family_cursor, 
                       'class_func': Family}, 
            'Event': {'cursor_func': self.get_event_cursor, 
                      'class_func': Event}, 
            'Place': {'cursor_func': self.get_place_cursor, 
                      'class_func': Place}, 
            'Source': {'cursor_func': self.get_source_cursor, 
                       'class_func': Source}, 
            'MediaObject': {'cursor_func': self.get_media_cursor, 
                            'class_func': MediaObject}, 
            'Repository': {'cursor_func': self.get_repository_cursor, 
                           'class_func': Repository},
            'Note':   {'cursor_func': self.get_note_cursor, 
                       'class_func': Note},
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

