# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012         Douglas S. Blank <doug.blank@gmail.com>
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
#

""" Implements a Db interface as a Dictionary """

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
import sys
if sys.version_info[0] < 3:
    import cPickle as pickle
else:
    import pickle
import base64
import time
import re
from . import DbReadBase, DbWriteBase, DbTxn
from . import (PERSON_KEY,
                    FAMILY_KEY,
                    CITATION_KEY,
                    SOURCE_KEY,
                    EVENT_KEY,
                    MEDIA_KEY,
                    PLACE_KEY,
                    REPOSITORY_KEY,
                    NOTE_KEY)
from ..utils.id import create_id
from ..lib.researcher import Researcher
from ..lib.mediaobj import MediaObject
from ..lib.person import Person
from ..lib.family import Family
from ..lib.src import Source
from ..lib.citation import Citation
from ..lib.event import Event
from ..lib.place import Place
from ..lib.repo import Repository
from ..lib.note import Note
from ..lib.tag import Tag
from ..constfunc import STRTYPE

class Cursor(object):
    """
    Iterates through model returning (handle, raw_data)...
    """
    def __init__(self, model, func):
        self.model = model
        self.func = func
    def __enter__(self):
        return self
    def __iter__(self):
        return self.__next__()
    def __next__(self):
        for handle in self.model.keys():
            yield (handle, self.func(handle))
    def __exit__(self, *args, **kwargs):
        pass
    def iter(self):
        for handle in self.model.keys():
            yield (handle, self.func(handle))
        yield None

class Bookmarks:
    def get(self):
        return [] # handles
    def append(self, handle):
        pass

class DictionaryTxn(DbTxn):
    def __init__(self, message, db):
        DbTxn.__init__(self, message, db)

    def get(self, key, default=None, txn=None, **kwargs):
        """
        Returns the data object associated with key
        """
        if txn and key in txn:
            return txn[key]
        else:
            return None

    def put(self, handle, new_data, txn):
        """
        """
        txn[handle] = new_data

class DictionaryDb(DbWriteBase, DbReadBase):
    """
    A Gramps Database Backend. This replicates the grampsdb functions.
    """

    def __init__(self, *args, **kwargs):
        DbReadBase.__init__(self)
        DbWriteBase.__init__(self)
        self._tables = {
            'Person':
                {
                "handle_func": self.get_person_from_handle, 
                "gramps_id_func": self.get_person_from_gramps_id,
                "class_func": Person,
                "cursor_func": self.get_person_cursor,
                "handles_func": self.get_person_handles,
                },
            'Family':
                {
                "handle_func": self.get_family_from_handle, 
                "gramps_id_func": self.get_family_from_gramps_id,
                "class_func": Family,
                "cursor_func": self.get_family_cursor,
                "handles_func": self.get_family_handles,
                },
            'Source':
                {
                "handle_func": self.get_source_from_handle, 
                "gramps_id_func": self.get_source_from_gramps_id,
                "class_func": Source,
                "cursor_func": self.get_source_cursor,
                "handles_func": self.get_source_handles,
                },
            'Citation':
                {
                "handle_func": self.get_citation_from_handle, 
                "gramps_id_func": self.get_citation_from_gramps_id,
                "class_func": Citation,
                "cursor_func": self.get_citation_cursor,
                "handles_func": self.get_citation_handles,
                },
            'Event':
                {
                "handle_func": self.get_event_from_handle, 
                "gramps_id_func": self.get_event_from_gramps_id,
                "class_func": Event,
                "cursor_func": self.get_event_cursor,
                "handles_func": self.get_event_handles,
                },
            'Media':
                {
                "handle_func": self.get_object_from_handle, 
                "gramps_id_func": self.get_object_from_gramps_id,
                "class_func": MediaObject,
                "cursor_func": self.get_media_cursor,
                "handles_func": self.get_media_object_handles,
                },
            'Place':
                {
                "handle_func": self.get_place_from_handle, 
                "gramps_id_func": self.get_place_from_gramps_id,
                "class_func": Place,
                "cursor_func": self.get_place_cursor,
                "handles_func": self.get_place_handles,
                },
            'Repository':
                {
                "handle_func": self.get_repository_from_handle, 
                "gramps_id_func": self.get_repository_from_gramps_id,
                "class_func": Repository,
                "cursor_func": self.get_repository_cursor,
                "handles_func": self.get_repository_handles,
                },
            'Note':
                {
                "handle_func": self.get_note_from_handle, 
                "gramps_id_func": self.get_note_from_gramps_id,
                "class_func": Note,
                "cursor_func": self.get_note_cursor,
                "handles_func": self.get_note_handles,
                },
            'Tag':
                {
                "handle_func": self.get_tag_from_handle, 
                "gramps_id_func": None,
                "class_func": Tag,
                "cursor_func": self.get_tag_cursor,
                "handles_func": self.get_tag_handles,
                },
            }
        # skip GEDCOM cross-ref check for now:
        self.set_feature("skip-check-xref", True)
        self.set_feature("skip-import-additions", True)
        self.readonly = False
        self.db_is_open = True
        self.name_formats = []
        self.bookmarks = Bookmarks()
        self.family_bookmarks = Bookmarks()
        self.event_bookmarks = Bookmarks()
        self.place_bookmarks = Bookmarks()
        self.citation_bookmarks = Bookmarks()
        self.source_bookmarks = Bookmarks()
        self.repo_bookmarks = Bookmarks()
        self.media_bookmarks = Bookmarks()
        self.note_bookmarks = Bookmarks()
        self.set_person_id_prefix('I%04d')
        self.set_object_id_prefix('O%04d')
        self.set_family_id_prefix('F%04d')
        self.set_citation_id_prefix('C%04d')
        self.set_source_id_prefix('S%04d')
        self.set_place_id_prefix('P%04d')
        self.set_event_id_prefix('E%04d')
        self.set_repository_id_prefix('R%04d')
        self.set_note_id_prefix('N%04d')
        # ----------------------------------
        self.id_trans  = DictionaryTxn("ID Transaction", self)
        self.fid_trans = DictionaryTxn("FID Transaction", self)
        self.pid_trans = DictionaryTxn("PID Transaction", self)
        self.cid_trans = DictionaryTxn("CID Transaction", self)
        self.sid_trans = DictionaryTxn("SID Transaction", self)
        self.oid_trans = DictionaryTxn("OID Transaction", self)
        self.rid_trans = DictionaryTxn("RID Transaction", self)
        self.nid_trans = DictionaryTxn("NID Transaction", self)
        self.eid_trans = DictionaryTxn("EID Transaction", self)
        self.cmap_index = 0
        self.smap_index = 0
        self.emap_index = 0
        self.pmap_index = 0
        self.fmap_index = 0
        self.lmap_index = 0
        self.omap_index = 0
        self.rmap_index = 0
        self.nmap_index = 0
        self.env = None
        self.person_map      = {}
        self.family_map      = {}
        self.place_map       = {}
        self.citation_map    = {}
        self.source_map      = {}
        self.repository_map  = {}
        self.note_map        = {}
        self.media_map       = {}
        self.event_map       = {}
        self.tag_map         = {}
        self.metadata   = {}
        self.name_group = {}
        self.undo_callback = None
        self.redo_callback = None
        self.undo_history_callback = None
        self.modified   = 0
        self.txn = DictionaryTxn("DbDictionary Transaction", self)
        self.transaction = None

    def version_supported(self):
        """Return True when the file has a supported version."""
        return True

    def get_table_names(self):
        """Return a list of valid table names."""
        return list(self._tables.keys())

    def get_table_metadata(self, table_name):
        """Return the metadata for a valid table name."""
        if table_name in self._tables:
            return self._tables[table_name]
        return None

    def transaction_commit(self, txn):
        pass

    def enable_signals(self):
        pass

    def get_undodb(self):
        return None

    def transaction_abort(self, txn):
        pass

    @staticmethod
    def _validated_id_prefix(val, default):
        if isinstance(val, STRTYPE) and val:
            try:
                str_ = val % 1
            except TypeError:           # missing conversion specifier
                prefix_var = val + "%d"
            except ValueError:          # incomplete format
                prefix_var = default+"%04d"
            else:
                prefix_var = val        # OK as given
        else:
            prefix_var = default+"%04d" # not a string or empty string
        return prefix_var

    @staticmethod
    def __id2user_format(id_pattern):
        """
        Return a method that accepts a Gramps ID and adjusts it to the users
        format.
        """
        pattern_match = re.match(r"(.*)%[0 ](\d+)[diu]$", id_pattern)
        if False: # pattern_match:
            str_prefix = pattern_match.group(1)
            nr_width = int(pattern_match.group(2))
            def closure_func(gramps_id):
                if gramps_id and gramps_id.startswith(str_prefix):
                    id_number = gramps_id[len(str_prefix):]
                    if id_number.isdigit():
                        id_value = int(id_number, 10)
                        if len(str(id_value)) > nr_width:
                            # The ID to be imported is too large to fit in the
                            # users format. For now just create a new ID,
                            # because that is also what happens with IDs that
                            # are identical to IDs already in the database. If
                            # the problem of colliding import and already
                            # present IDs is solved the code here also needs
                            # some solution.
                            gramps_id = id_pattern % 1
                        else:
                            gramps_id = id_pattern % id_value
                return gramps_id
        else:
            def closure_func(gramps_id):
                return gramps_id
        return closure_func

    def set_person_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Person ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as I%d or I%04d.
        """
        self.person_prefix = self._validated_id_prefix(val, "I")
        self.id2user_format = self.__id2user_format(self.person_prefix)

    def set_citation_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Citation ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as C%d or C%04d.
        """
        self.citation_prefix = self._validated_id_prefix(val, "C")
        self.cid2user_format = self.__id2user_format(self.citation_prefix)
            
    def set_source_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Source ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as S%d or S%04d.
        """
        self.source_prefix = self._validated_id_prefix(val, "S")
        self.sid2user_format = self.__id2user_format(self.source_prefix)
            
    def set_object_id_prefix(self, val):
        """
        Set the naming template for GRAMPS MediaObject ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as O%d or O%04d.
        """
        self.mediaobject_prefix = self._validated_id_prefix(val, "O")
        self.oid2user_format = self.__id2user_format(self.mediaobject_prefix)

    def set_place_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Place ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as P%d or P%04d.
        """
        self.place_prefix = self._validated_id_prefix(val, "P")
        self.pid2user_format = self.__id2user_format(self.place_prefix)

    def set_family_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Family ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as F%d
        or F%04d.
        """
        self.family_prefix = self._validated_id_prefix(val, "F")
        self.fid2user_format = self.__id2user_format(self.family_prefix)

    def set_event_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Event ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as E%d or E%04d.
        """
        self.event_prefix = self._validated_id_prefix(val, "E")
        self.eid2user_format = self.__id2user_format(self.event_prefix)

    def set_repository_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Repository ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as R%d or R%04d.
        """
        self.repository_prefix = self._validated_id_prefix(val, "R")
        self.rid2user_format = self.__id2user_format(self.repository_prefix)

    def set_note_id_prefix(self, val):
        """
        Set the naming template for GRAMPS Note ID values. 
        
        The string is expected to be in the form of a simple text string, or 
        in a format that contains a C/Python style format string using %d, 
        such as N%d or N%04d.
        """
        self.note_prefix = self._validated_id_prefix(val, "N")
        self.nid2user_format = self.__id2user_format(self.note_prefix)

    def __find_next_gramps_id(self, prefix, map_index, trans):
        """
        Helper function for find_next_<object>_gramps_id methods
        """
        index = prefix % map_index
        while trans.get(str(index), txn=self.txn) is not None:
            map_index += 1
            index = prefix % map_index
        map_index += 1
        return (map_index, index)
        
    def find_next_person_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Person object based off the 
        person ID prefix.
        """
        self.pmap_index, gid = self.__find_next_gramps_id(self.person_prefix,
                                          self.pmap_index, self.id_trans)
        return gid

    def find_next_place_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Place object based off the 
        place ID prefix.
        """
        self.lmap_index, gid = self.__find_next_gramps_id(self.place_prefix,
                                          self.lmap_index, self.pid_trans)
        return gid

    def find_next_event_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Event object based off the 
        event ID prefix.
        """
        self.emap_index, gid = self.__find_next_gramps_id(self.event_prefix,
                                          self.emap_index, self.eid_trans)
        return gid

    def find_next_object_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a MediaObject object based
        off the media object ID prefix.
        """
        self.omap_index, gid = self.__find_next_gramps_id(self.mediaobject_prefix,
                                          self.omap_index, self.oid_trans)
        return gid

    def find_next_citation_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Citation object based off the 
        citation ID prefix.
        """
        self.cmap_index, gid = self.__find_next_gramps_id(self.citation_prefix,
                                          self.cmap_index, self.cid_trans)
        return gid

    def find_next_source_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Source object based off the 
        source ID prefix.
        """
        self.smap_index, gid = self.__find_next_gramps_id(self.source_prefix,
                                          self.smap_index, self.sid_trans)
        return gid

    def find_next_family_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Family object based off the 
        family ID prefix.
        """
        self.fmap_index, gid = self.__find_next_gramps_id(self.family_prefix,
                                          self.fmap_index, self.fid_trans)
        return gid

    def find_next_repository_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Respository object based 
        off the repository ID prefix.
        """
        self.rmap_index, gid = self.__find_next_gramps_id(self.repository_prefix,
                                          self.rmap_index, self.rid_trans)
        return gid

    def find_next_note_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Note object based off the 
        note ID prefix.
        """
        self.nmap_index, gid = self.__find_next_gramps_id(self.note_prefix,
                                          self.nmap_index, self.nid_trans)
        return gid

    def get_mediapath(self):
        return None

    def get_name_group_keys(self):
        return []

    def get_name_group_mapping(self, key):
        return None

    def get_researcher(self):
        obj = Researcher()
        return obj

    def get_person_handles(self, sort_handles=False):
        if sort_handles:
            raise Exception("Implement!")
        else:
            return self.person_map.keys()

    def get_family_handles(self):
        return self.family_map.keys()

    def get_event_handles(self):
        return self.event_map.keys()

    def get_citation_handles(self, sort_handles=False):
        if sort_handles:
            raise Exception("Implement!")
        else:
            return self.citation_map.keys()

    def get_source_handles(self, sort_handles=False):
        if sort_handles:
            raise Exception("Implement!")
        else:
            return self.source_map.keys()

    def get_place_handles(self, sort_handles=False):
        if sort_handles:
            raise Exception("Implement!")
        else:
            return self.place_map.keys()

    def get_repository_handles(self):
        return self.repository_map.keys()

    def get_media_object_handles(self, sort_handles=False):
        if sort_handles:
            raise Exception("Implement!")
        else:
            return self.media_map.keys()

    def get_note_handles(self):
        return self.note_map.keys()

    def get_tag_handles(self, sort_handles=False):
        if sort_handles:
            raise Exception("Implement!")
        else:
            return self.tag_map.keys()

    def get_event_from_handle(self, handle):
        return self.event_map[handle]

    def get_family_from_handle(self, handle): 
        return self.family_map[handle]

    def get_repository_from_handle(self, handle):
        return self.repository_map[handle]

    def get_person_from_handle(self, handle):
        return self.person_map[handle]

    def get_place_from_handle(self, handle):
        place = self.place_map[handle]
        return place

    def get_citation_from_handle(self, handle):
        citation = self.citation_map[handle]
        return citation

    def get_source_from_handle(self, handle):
        source = self.source_map[handle]
        return source

    def get_note_from_handle(self, handle):
        note = self.note_map[handle]
        return note

    def get_object_from_handle(self, handle):
        media = self.media_map[handle]
        return media

    def get_tag_from_handle(self, handle):
        tag = self.tag_map[handle]
        return tag

    def get_default_person(self):
        return None

    def iter_people(self):
        return (person for person in self.person_map.values())

    def iter_person_handles(self):
        return (handle for handle in self.person_map.keys())

    def iter_families(self):
        return (family for family in self.family_map.values())

    def iter_family_handles(self):
        return (handle for handle in self.family_map.keys())

    def get_tag_from_name(self, name):
        for tag in self.tag_map.values():
            if tag.name == name:
                return tag
        return None

    def get_family_from_gramps_id(self, gramps_id):
        for family in self.family_map.values():
            if family.gramps_id == gramps_id:
                return family
        return None

    def get_person_from_gramps_id(self, gramps_id):
        for person in self.person_map.values():
            if person.gramps_id == gramps_id:
                return person
        return person

    def get_number_of_people(self):
        return len(self.person_map)

    def get_number_of_events(self):
        return len(self.event_map)

    def get_number_of_places(self):
        return len(self.place_map)

    def get_number_of_tags(self):
        return 0 # FIXME

    def get_number_of_families(self):
        return len(self.family_map)

    def get_number_of_notes(self):
        return len(self.note_map)

    def get_number_of_citations(self):
        return len(self.citation_map)

    def get_number_of_sources(self):
        return len(self.source_map)

    def get_number_of_media_objects(self):
        return len(self.media_map)

    def get_number_of_repositories(self):
        return len(self.repository_map)

    def get_place_cursor(self):
        return Cursor(self.place_map, self.get_raw_place_data).iter()

    def get_person_cursor(self):
        return Cursor(self.person_map, self.get_raw_person_data).iter()

    def get_family_cursor(self):
        return Cursor(self.family_map, self.get_raw_family_data).iter()

    def get_event_cursor(self):
        return Cursor(self.event_map, self.get_raw_event_data).iter()

    def get_note_cursor(self):
        return Cursor(self.note_map, self.get_raw_note_data).iter()

    def get_tag_cursor(self):
        return Cursor(self.tag_map, self.get_raw_tag_data).iter()

    def get_repository_cursor(self):
        return Cursor(self.repository_map, self.get_raw_repository_data).iter()

    def get_media_cursor(self):
        return Cursor(self.media_map, self.get_raw_object_data).iter()

    def get_citation_cursor(self):
        return Cursor(self.citation_map, self.get_raw_citation_data).iter()

    def get_source_cursor(self):
        return Cursor(self.source_map, self.get_raw_source_data).iter()

    def has_gramps_id(self, obj_key, gramps_id):
        key2table = {
            PERSON_KEY:     self.person_map, 
            FAMILY_KEY:     self.family_map, 
            SOURCE_KEY:     self.source_map, 
            CITATION_KEY:   self.citation_map, 
            EVENT_KEY:      self.event_map, 
            MEDIA_KEY:      self.media_map, 
            PLACE_KEY:      self.place_map, 
            REPOSITORY_KEY: self.repository_map, 
            NOTE_KEY:       self.note_map, 
            }
        map = key2table[obj_key]
        for item in map.values():
            if item.gramps_id == gramps_id:
                return True
        return False

    def has_person_handle(self, handle):
        return handle in self.person_map

    def has_family_handle(self, handle):
        return handle in self.family_map

    def has_citation_handle(self, handle):
        return handle in self.citation_map

    def has_source_handle(self, handle):
        return handle in self.source_map

    def has_repository_handle(self, handle):
        return handle in self.repository_map

    def has_note_handle(self, handle):
        return handle in self.note_map

    def has_place_handle(self, handle):
        return handle in self.place_map

    def has_event_handle(self, handle):
        return handle in self.event_map

    def has_tag_handle(self, handle):
        return handle in self.tag_map

    def has_object_handle(self, handle):
        return handle in self.media_map

    def has_name_group_key(self, key):
        # FIXME:
        return False

    def set_name_group_mapping(self, key, value):
        # FIXME:
        pass

    def set_default_person_handle(self, handle):
        pass

    def set_mediapath(self, mediapath):
        pass

    def get_raw_person_data(self, handle):
        if handle in self.person_map:
            return self.person_map[handle].serialize()
        return None

    def get_raw_family_data(self, handle):
        if handle in self.family_map:
            return self.family_map[handle].serialize()
        return None

    def get_raw_citation_data(self, handle):
        if handle in self.citation_map:
            return self.citation_map[handle].serialize()
        return None

    def get_raw_source_data(self, handle):
        if handle in self.source_map:
            return self.source_map[handle].serialize()
        return None

    def get_raw_repository_data(self, handle):
        if handle in self.repository_map:
            return self.repository_map[handle].serialize()
        return None

    def get_raw_note_data(self, handle):
        if handle in self.note_map:
            return self.note_map[handle].serialize()
        return None

    def get_raw_place_data(self, handle):
        if handle in self.place_map:
            return self.place_map[handle].serialize()
        return None

    def get_raw_object_data(self, handle):
        if handle in self.media_map:
            return self.media_map[handle].serialize()
        return None

    def get_raw_tag_data(self, handle):
        if handle in self.tag_map:
            return self.tag_map[handle].serialize()
        return None

    def add_person(self, person, trans, set_gid=True):
        if not person.handle:
            person.handle = create_id()
        if not person.gramps_id and set_gid:
            person.gramps_id = self.find_next_person_gramps_id()
        self.commit_person(person, trans)
        return person.handle

    def add_family(self, family, trans, set_gid=True):
        if not family.handle:
            family.handle = create_id()
        if not family.gramps_id and set_gid:
            family.gramps_id = self.find_next_family_gramps_id()
        self.commit_family(family, trans)
        return family.handle

    def add_citation(self, citation, trans, set_gid=True):
        if not citation.handle:
            citation.handle = create_id()
        if not citation.gramps_id and set_gid:
            citation.gramps_id = self.find_next_citation_gramps_id()
        self.commit_citation(citation, trans)
        return citation.handle

    def add_source(self, source, trans, set_gid=True):
        if not source.handle:
            source.handle = create_id()
        if not source.gramps_id and set_gid:
            source.gramps_id = self.find_next_source_gramps_id()
        self.commit_source(source, trans)
        return source.handle

    def add_repository(self, repository, trans, set_gid=True):
        if not repository.handle:
            repository.handle = create_id()
        if not repository.gramps_id and set_gid:
            repository.gramps_id = self.find_next_repository_gramps_id()
        self.commit_repository(repository, trans)
        return repository.handle

    def add_note(self, note, trans, set_gid=True):
        if not note.handle:
            note.handle = create_id()
        if not note.gramps_id and set_gid:
            note.gramps_id = self.find_next_note_gramps_id()
        self.commit_note(note, trans)
        return note.handle

    def add_place(self, place, trans, set_gid=True):
        if not place.handle:
            place.handle = create_id()
        if not place.gramps_id and set_gid:
            place.gramps_id = self.find_next_place_gramps_id()
        self.commit_place(place, trans)
        return place.handle

    def add_event(self, event, trans, set_gid=True):
        if not event.handle:
            event.handle = create_id()
        if not event.gramps_id and set_gid:
            event.gramps_id = self.find_next_event_gramps_id()
        self.commit_event(event, trans)
        return event.handle

    def add_tag(self, tag, trans):
        if not tag.handle:
            tag.handle = create_id()
        self.commit_tag(tag, trans)
        return tag.handle

    def add_object(self, obj, transaction, set_gid=True):
        """
        Add a MediaObject to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        if not obj.handle:
            obj.handle = create_id()
        if not obj.gramps_id and set_gid:
            obj.gramps_id = self.find_next_object_gramps_id()
        self.commit_media_object(obj, transaction)
        return obj.handle

    def commit_person(self, person, trans, change_time=None):
        self.person_map[person.handle] = person

    def commit_family(self, family, trans, change_time=None):
        self.family_map[family.handle] = family

    def commit_citation(self, citation, trans, change_time=None):
        self.citation_map[citation.handle] = citation

    def commit_source(self, source, trans, change_time=None):
        self.source_map[source.handle] = source

    def commit_repository(self, repository, trans, change_time=None):
        self.repository_map[repository.handle] = repository

    def commit_note(self, note, trans, change_time=None):
        self.note_map[note.handle] = note

    def commit_place(self, place, trans, change_time=None):
        self.place_map[place.handle] = place

    def commit_event(self, event, trans, change_time=None):
        self.event_map[event.handle] = event

    def commit_tag(self, tag, trans, change_time=None):
        self.tag_map[tag.handle] = tag

    def commit_media_object(self, obj, transaction, change_time=None):
        self.media_map[obj.handle] = obj

    def get_gramps_ids(self, obj_key):
        key2table = {
            PERSON_KEY:     self.person_map, 
            FAMILY_KEY:     self.family_map, 
            CITATION_KEY:   self.citation_map, 
            SOURCE_KEY:     self.source_map, 
            EVENT_KEY:      self.event_map, 
            MEDIA_KEY:      self.media_map, 
            PLACE_KEY:      self.place_map, 
            REPOSITORY_KEY: self.repository_map, 
            NOTE_KEY:       self.note_map, 
            }
        table = key2table[obj_key]
        return [item.gramps_id for item in table.values()]

    def transaction_begin(self, transaction):
        return 

    def disable_signals(self):
        pass

    def set_researcher(self, owner):
        pass

    def request_rebuild(self):
        pass

    def copy_from_db(self, db):
        """
        A (possibily) implementation-specific method to get data from
        db into this database.
        """
        for key in db._tables.keys():
            cursor = db._tables[key]["cursor_func"]
            class_ = db._tables[key]["class_func"]
            for (handle, data) in cursor():
                map = getattr(self, "%s_map" % key.lower())
                map[handle] = class_.create(data)
