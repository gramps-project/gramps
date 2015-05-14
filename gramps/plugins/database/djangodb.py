# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009         Douglas S. Blank <doug.blank@gmail.com>
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

""" Implements a Db interface """

#------------------------------------------------------------------------
#
# Python Modules
#
#------------------------------------------------------------------------
import sys
import time
import re
import base64
import pickle
import os
import logging
import shutil
from django.db import transaction

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
import gramps
from gramps.gen.lib import (Person, Family, Event, Place, Repository, 
                            Citation, Source, Note, MediaObject, Tag, 
                            Researcher)
from gramps.gen.db import DbReadBase, DbWriteBase, DbTxn
from gramps.gen.utils.callback import Callback
from gramps.gen.updatecallback import UpdateCallback
from gramps.gen.db import (PERSON_KEY,
                    FAMILY_KEY,
                    CITATION_KEY,
                    SOURCE_KEY,
                    EVENT_KEY,
                    MEDIA_KEY,
                    PLACE_KEY,
                    REPOSITORY_KEY,
                    NOTE_KEY)
from gramps.gen.utils.id import create_id
from gramps.gen.db.dbconst import *

## add this directory to sys path, so we can find django_support later:
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

_LOG = logging.getLogger(DBLOGNAME)

class Environment(object):
    """
    Implements the Environment API.
    """
    def __init__(self, db):
        self.db = db

    def txn_begin(self):
        return DjangoTxn("DjangoDb Transaction", self.db)

class Table(object):
    """
    Implements Table interface.
    """
    def __init__(self, funcs):
        self.funcs = funcs

    def cursor(self):
        """
        Returns a Cursor for this Table.
        """
        return self.funcs["cursor_func"]()

    def put(key, data, txn=None):
        self[key] = data

class Map(dict):
    """
    Implements the map API for person_map, etc.
    
    Takes a Table() as argument.
    """
    def __init__(self, tbl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = tbl

class MetaCursor(object):
    def __init__(self):
        pass
    def __enter__(self):
        return self
    def __iter__(self):
        return self.__next__()
    def __next__(self):
        yield None
    def __exit__(self, *args, **kwargs):
        pass
    def iter(self):
        yield None
    def first(self):
        self._iter = self.__iter__()
        return self.next()
    def next(self):
        try:
            return next(self._iter)
        except:
            return None
    def close(self):
        pass

class Cursor(object):
    def __init__(self, model, func):
        self.model = model
        self.func = func
    def __enter__(self):
        return self
    def __iter__(self):
        return self.__next__()
    def __next__(self):
        for item in self.model.all():
            yield (bytes(item.handle, "utf-8"), self.func(item.handle))
    def __exit__(self, *args, **kwargs):
        pass
    def iter(self):
        for item in self.model.all():
            yield (bytes(item.handle, "utf-8"), self.func(item.handle))
        yield None
    def first(self):
        self._iter = self.__iter__()
        return self.next()
    def next(self):
        try:
            return next(self._iter)
        except:
            return None
    def close(self):
        pass

class Bookmarks(object):
    def __init__(self):
        self.handles = []
    def get(self):
        return self.handles
    def append(self, handle):
        self.handles.append(handle)

class DjangoTxn(DbTxn):
    def __init__(self, message, db, table=None):
        DbTxn.__init__(self, message, db)
        self.table = table

    def get(self, key, default=None, txn=None, **kwargs):
        """
        Returns the data object associated with key
        """
        try:
            return self.table.objects(handle=key)
        except:
            if txn and key in txn:
                return txn[key]
            else:
                return None

    def put(self, handle, new_data, txn):
        """
        """
        txn[handle] = new_data

    def commit(self):
        pass

class DbDjango(DbWriteBase, DbReadBase, UpdateCallback, Callback):
    """
    A Gramps Database Backend. This replicates the grampsdb functions.
    """
    # Set up dictionary for callback signal handler
    # ---------------------------------------------
    # 1. Signals for primary objects
    __signals__ = dict((obj+'-'+op, signal)
                       for obj in
                       ['person', 'family', 'event', 'place',
                        'source', 'citation', 'media', 'note', 'repository', 'tag']
                       for op, signal in zip(
                               ['add',   'update', 'delete', 'rebuild'],
                               [(list,), (list,),  (list,),   None]
                       )
                   )
    
    # 2. Signals for long operations
    __signals__.update(('long-op-'+op, signal) for op, signal in zip(
        ['start',  'heartbeat', 'end'],
        [(object,), None,       None]
        ))

    # 3. Special signal for change in home person
    __signals__['home-person-changed'] = None

    # 4. Signal for change in person group name, parameters are
    __signals__['person-groupname-rebuild'] = (str, str)

    __callback_map = {}

    def __init__(self, directory=None):
        DbReadBase.__init__(self)
        DbWriteBase.__init__(self)
        Callback.__init__(self)
        self._tables = {
            'Person':
                {
                "handle_func": self.get_person_from_handle, 
                "gramps_id_func": self.get_person_from_gramps_id,
                "class_func": gramps.gen.lib.Person,
                "cursor_func": self.get_person_cursor,
                "handles_func": self.get_person_handles,
                "iter_func": self.iter_people,
                },
            'Family':
                {
                "handle_func": self.get_family_from_handle, 
                "gramps_id_func": self.get_family_from_gramps_id,
                "class_func": gramps.gen.lib.Family,
                "cursor_func": self.get_family_cursor,
                "handles_func": self.get_family_handles,
                "iter_func": self.iter_families,
                },
            'Source':
                {
                "handle_func": self.get_source_from_handle, 
                "gramps_id_func": self.get_source_from_gramps_id,
                "class_func": gramps.gen.lib.Source,
                "cursor_func": self.get_source_cursor,
                "handles_func": self.get_source_handles,
                "iter_func": self.iter_sources,
                },
            'Citation':
                {
                "handle_func": self.get_citation_from_handle, 
                "gramps_id_func": self.get_citation_from_gramps_id,
                "class_func": gramps.gen.lib.Citation,
                "cursor_func": self.get_citation_cursor,
                "handles_func": self.get_citation_handles,
                "iter_func": self.iter_citations,
                },
            'Event':
                {
                "handle_func": self.get_event_from_handle, 
                "gramps_id_func": self.get_event_from_gramps_id,
                "class_func": gramps.gen.lib.Event,
                "cursor_func": self.get_event_cursor,
                "handles_func": self.get_event_handles,
                "iter_func": self.iter_events,
                },
            'Media':
                {
                "handle_func": self.get_object_from_handle, 
                "gramps_id_func": self.get_object_from_gramps_id,
                "class_func": gramps.gen.lib.MediaObject,
                "cursor_func": self.get_media_cursor,
                "handles_func": self.get_media_object_handles,
                "iter_func": self.iter_media_objects,
                },
            'Place':
                {
                "handle_func": self.get_place_from_handle, 
                "gramps_id_func": self.get_place_from_gramps_id,
                "class_func": gramps.gen.lib.Place,
                "cursor_func": self.get_place_cursor,
                "handles_func": self.get_place_handles,
                "iter_func": self.iter_places,
                },
            'Repository':
                {
                "handle_func": self.get_repository_from_handle, 
                "gramps_id_func": self.get_repository_from_gramps_id,
                "class_func": gramps.gen.lib.Repository,
                "cursor_func": self.get_repository_cursor,
                "handles_func": self.get_repository_handles,
                "iter_func": self.iter_repositories,
                },
            'Note':
                {
                "handle_func": self.get_note_from_handle, 
                "gramps_id_func": self.get_note_from_gramps_id,
                "class_func": gramps.gen.lib.Note,
                "cursor_func": self.get_note_cursor,
                "handles_func": self.get_note_handles,
                "iter_func": self.iter_notes,
                },
            'Tag':
                {
                "handle_func": self.get_tag_from_handle, 
                "gramps_id_func": None,
                "class_func": gramps.gen.lib.Tag,
                "cursor_func": self.get_tag_cursor,
                "handles_func": self.get_tag_handles,
                "iter_func": self.iter_tags,
                },
            }
        # skip GEDCOM cross-ref check for now:
        self.set_feature("skip-check-xref", True)
        self.readonly = False
        self.db_is_open = True
        self.name_formats = []
        self.bookmarks = Bookmarks()
        self.undo_callback = None
        self.redo_callback = None
        self.undo_history_callback = None
        self.modified   = 0
        self.txn = DjangoTxn("DbDjango Transaction", self)
        self.transaction = None
        # Import cache for gedcom import, uses transactions, and
        # two step adding of objects.
        self.import_cache = {}
        self.use_import_cache = False
        self.use_db_cache = True
        self._directory = directory
        if directory:
            self.load(directory)

    def load(self, directory, pulse_progress=None, mode=None, 
             force_schema_upgrade=False,
             force_bsddb_upgrade=False,
             force_bsddb_downgrade=False,
             force_python_upgrade=False):
        self._directory = directory
        from django.conf import settings
        default_settings = {"__file__": 
                            os.path.join(directory, "default_settings.py")}
        settings_file = os.path.join(directory, "default_settings.py")
        with open(settings_file) as f:
            code = compile(f.read(), settings_file, 'exec')
            exec(code, globals(), default_settings)

        class Module(object):
            def __init__(self, dictionary):
                self.dictionary = dictionary
            def __getattr__(self, item):
                return self.dictionary[item]

        try:
            settings.configure(Module(default_settings))
        except RuntimeError:
            # already configured; ignore
            pass

        import django
        django.setup()

        from django_support.libdjango import DjangoInterface
        self.dji = DjangoInterface()
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
        self.id_trans  = DjangoTxn("ID Transaction", self, self.dji.Person)
        self.fid_trans = DjangoTxn("FID Transaction", self, self.dji.Family)
        self.pid_trans = DjangoTxn("PID Transaction", self, self.dji.Place)
        self.cid_trans = DjangoTxn("CID Transaction", self, self.dji.Citation)
        self.sid_trans = DjangoTxn("SID Transaction", self, self.dji.Source)
        self.oid_trans = DjangoTxn("OID Transaction", self, self.dji.Media)
        self.rid_trans = DjangoTxn("RID Transaction", self, self.dji.Repository)
        self.nid_trans = DjangoTxn("NID Transaction", self, self.dji.Note)
        self.eid_trans = DjangoTxn("EID Transaction", self, self.dji.Event)
        self.cmap_index = 0
        self.smap_index = 0
        self.emap_index = 0
        self.pmap_index = 0
        self.fmap_index = 0
        self.lmap_index = 0
        self.omap_index = 0
        self.rmap_index = 0
        self.nmap_index = 0
        self.env = Environment(self)
        self.person_map = Map(Table(self._tables["Person"]))
        self.family_map = Map(Table(self._tables["Family"]))
        self.place_map  = Map(Table(self._tables["Place"]))
        self.citation_map = Map(Table(self._tables["Citation"]))
        self.source_map = Map(Table(self._tables["Source"]))
        self.repository_map  = Map(Table(self._tables["Repository"]))
        self.note_map = Map(Table(self._tables["Note"]))
        self.media_map  = Map(Table(self._tables["Media"]))
        self.event_map  = Map(Table(self._tables["Event"]))
        self.tag_map  = Map(Table(self._tables["Tag"]))
        self.metadata   = Map(Table({"cursor_func": lambda: MetaCursor()}))
        self.name_group = {}
        self.event_names = set()
        self.individual_attributes = set()
        self.family_attributes = set()
        self.source_attributes = set()
        self.child_ref_types = set()
        self.family_rel_types = set()
        self.event_role_names = set()
        self.name_types = set()
        self.origin_types = set()
        self.repository_types = set()
        self.note_types = set()
        self.source_media_types = set()
        self.url_types = set()
        self.media_attributes = set()
        self.place_types = set()

    def prepare_import(self):
        """
        DbDjango does not commit data on gedcom import, but saves them
        for later commit.
        """
        self.use_import_cache = True
        self.import_cache = {}

    @transaction.atomic
    def commit_import(self):
        """
        Commits the items that were queued up during the last gedcom
        import for two step adding.
        """
        # First we add the primary objects:
        for key in list(self.import_cache.keys()):
            obj = self.import_cache[key]
            if isinstance(obj, Person):
                self.dji.add_person(obj.serialize())
            elif isinstance(obj, Family):
                self.dji.add_family(obj.serialize())
            elif isinstance(obj, Event):
                self.dji.add_event(obj.serialize())
            elif isinstance(obj, Place):
                self.dji.add_place(obj.serialize())
            elif isinstance(obj, Repository):
                self.dji.add_repository(obj.serialize())
            elif isinstance(obj, Citation):
                self.dji.add_citation(obj.serialize())
            elif isinstance(obj, Source):
                self.dji.add_source(obj.serialize())
            elif isinstance(obj, Note):
                self.dji.add_note(obj.serialize())
            elif isinstance(obj, MediaObject):
                self.dji.add_media(obj.serialize())
            elif isinstance(obj, Tag):
                self.dji.add_tag(obj.serialize())
        # Next we add the links:
        for key in list(self.import_cache.keys()):
            obj = self.import_cache[key]
            if isinstance(obj, Person):
                self.dji.add_person_detail(obj.serialize())
            elif isinstance(obj, Family):
                self.dji.add_family_detail(obj.serialize())
            elif isinstance(obj, Event):
                self.dji.add_event_detail(obj.serialize())
            elif isinstance(obj, Place):
                self.dji.add_place_detail(obj.serialize())
            elif isinstance(obj, Repository):
                self.dji.add_repository_detail(obj.serialize())
            elif isinstance(obj, Citation):
                self.dji.add_citation_detail(obj.serialize())
            elif isinstance(obj, Source):
                self.dji.add_source_detail(obj.serialize())
            elif isinstance(obj, Note):
                self.dji.add_note_detail(obj.serialize())
            elif isinstance(obj, MediaObject):
                self.dji.add_media_detail(obj.serialize())
            elif isinstance(obj, Tag):
                self.dji.add_tag_detail(obj.serialize())
        self.use_import_cache = False
        self.import_cache = {}
        self.dji.update_publics()

    def transaction_commit(self, txn):
        pass

    def request_rebuild(self):
        # caches are ok, but let's compute public's
        self.dji.update_publics()
        self.emit('person-rebuild')
        self.emit('family-rebuild')
        self.emit('place-rebuild')
        self.emit('source-rebuild')
        self.emit('citation-rebuild')
        self.emit('media-rebuild')
        self.emit('event-rebuild')
        self.emit('repository-rebuild')
        self.emit('note-rebuild')
        self.emit('tag-rebuild')

    def get_undodb(self):
        return None

    def transaction_abort(self, txn):
        pass

    @staticmethod
    def _validated_id_prefix(val, default):
        if isinstance(val, str) and val:
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
        if pattern_match:
            str_prefix = pattern_match.group(1)
            nr_width = pattern_match.group(2)
            def closure_func(gramps_id):
                if gramps_id and gramps_id.startswith(str_prefix):
                    id_number = gramps_id[len(str_prefix):]
                    if id_number.isdigit():
                        id_value = int(id_number, 10)
                        #if len(str(id_value)) > nr_width:
                        #    # The ID to be imported is too large to fit in the
                        #    # users format. For now just create a new ID,
                        #    # because that is also what happens with IDs that
                        #    # are identical to IDs already in the database. If
                        #    # the problem of colliding import and already
                        #    # present IDs is solved the code here also needs
                        #    # some solution.
                        #    gramps_id = id_pattern % 1
                        #else:
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

    def get_tag_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Tag.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Tag.all()]

    def get_person_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Person.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Person.all()]

    def get_family_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Family.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Family.all()]

    def get_event_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Event.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Event.all()]

    def get_citation_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Citation.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Citation.all()]

    def get_source_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Source.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Source.all()]

    def get_place_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Place.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Place.all()]

    def get_repository_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Repository.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Repository.all()]

    def get_media_object_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Media.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Media.all()]

    def get_note_handles(self, sort_handles=False):
        if sort_handles:
            return [item.handle for item in self.dji.Note.all().order_by("handle")]
        else:
            return [item.handle for item in self.dji.Note.all()]

    def get_media_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            media = self.dji.Media.get(handle=handle)
        except:
            return None
        return self.make_media(media)

    def get_event_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            event = self.dji.Event.get(handle=handle)
        except:
            return None
        return self.make_event(event)

    def get_family_from_handle(self, handle): 
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            family = self.dji.Family.get(handle=handle)
        except:
            return None
        return self.make_family(family)

    def get_repository_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            repository = self.dji.Repository.get(handle=handle)
        except:
            return None
        return self.make_repository(repository)

    def get_person_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            person = self.dji.Person.get(handle=handle)
        except:
            return None
        return self.make_person(person)

    def get_tag_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            tag = self.dji.Tag.get(handle=handle)
        except:
            return None
        return self.make_tag(tag)

    def make_repository(self, repository):
        if self.use_db_cache and repository.cache:
            data = repository.from_cache()
        else:
            data = self.dji.get_repository(repository)
        return Repository.create(data)

    def make_citation(self, citation):
        if self.use_db_cache and citation.cache:
            data = citation.from_cache()
        else:
            data = self.dji.get_citation(citation)
        return Citation.create(data)

    def make_source(self, source):
        if self.use_db_cache and source.cache:
            data = source.from_cache()
        else:
            data = self.dji.get_source(source)
        return Source.create(data)

    def make_family(self, family):
        if self.use_db_cache and family.cache:
            data = family.from_cache()
        else:
            data = self.dji.get_family(family)
        return Family.create(data)

    def make_person(self, person):
        if self.use_db_cache and person.cache:
            data = person.from_cache()
        else:
            data = self.dji.get_person(person)
        return Person.create(data)

    def make_event(self, event):
        if self.use_db_cache and event.cache:
            data = event.from_cache()
        else:
            data = self.dji.get_event(event)
        return Event.create(data)

    def make_note(self, note):
        if self.use_db_cache and note.cache:
            data = note.from_cache()
        else:
            data = self.dji.get_note(note)
        return Note.create(data)

    def make_tag(self, tag):
        data = self.dji.get_tag(tag)
        return Tag.create(data)

    def make_place(self, place):
        if self.use_db_cache and place.cache:
            data = place.from_cache()
        else:
            data = self.dji.get_place(place)
        return Place.create(data)

    def make_media(self, media):
        if self.use_db_cache and media.cache:
            data = media.from_cache()
        else:
            data = self.dji.get_media(media)
        return MediaObject.create(data)

    def get_place_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            place = self.dji.Place.get(handle=handle)
        except:
            return None
        return self.make_place(place)

    def get_citation_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            citation = self.dji.Citation.get(handle=handle)
        except:
            return None
        return self.make_citation(citation)

    def get_source_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            source = self.dji.Source.get(handle=handle)
        except:
            return None
        return self.make_source(source)

    def get_note_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            note = self.dji.Note.get(handle=handle)
        except:
            return None
        return self.make_note(note)

    def get_object_from_handle(self, handle):
        if handle in self.import_cache:
            return self.import_cache[handle]
        try:
            media = self.dji.Media.get(handle=handle)
        except:
            return None
        return self.make_media(media)

    def get_default_person(self):
        people = self.dji.Person.all()
        if people.count() > 0:
            return self.make_person(people[0])
        return None

    def iter_people(self):
        return (self.get_person_from_handle(person.handle) 
                for person in self.dji.Person.all())

    def iter_person_handles(self):
        return (person.handle for person in self.dji.Person.all())

    def iter_families(self):
        return (self.get_family_from_handle(family.handle) 
                for family in self.dji.Family.all())

    def iter_family_handles(self):
        return (family.handle for family in self.dji.Family.all())

    def iter_notes(self):
        return (self.get_note_from_handle(note.handle) 
                for note in self.dji.Note.all())

    def iter_note_handles(self):
        return (note.handle for note in self.dji.Note.all())

    def iter_events(self):
        return (self.get_event_from_handle(event.handle) 
                for event in self.dji.Event.all())

    def iter_event_handles(self):
        return (event.handle for event in self.dji.Event.all())

    def iter_places(self):
        return (self.get_place_from_handle(place.handle) 
                for place in self.dji.Place.all())

    def iter_place_handles(self):
        return (place.handle for place in self.dji.Place.all())

    def iter_repositories(self):
        return (self.get_repository_from_handle(repository.handle) 
                for repository in self.dji.Repository.all())

    def iter_repository_handles(self):
        return (repository.handle for repository in self.dji.Repository.all())

    def iter_sources(self):
        return (self.get_source_from_handle(source.handle) 
                for source in self.dji.Source.all())

    def iter_source_handles(self):
        return (source.handle for source in self.dji.Source.all())

    def iter_citations(self):
        return (self.get_citation_from_handle(citation.handle) 
                for citation in self.dji.Citation.all())

    def iter_citation_handles(self):
        return (citation.handle for citation in self.dji.Citation.all())

    def iter_tags(self):
        return (self.get_tag_from_handle(tag.handle) 
                for tag in self.dji.Tag.all())

    def iter_tag_handles(self):
        return (tag.handle for tag in self.dji.Tag.all())

    def iter_media_objects(self):
        return (self.get_media_from_handle(media.handle) 
                for media in self.dji.Media.all())

    def get_tag_from_name(self, name):
        try:
            tag = self.dji.Tag.filter(name=name)
            return self.make_tag(tag[0])
        except:
            return None

    def get_person_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        match_list = self.dji.Person.filter(gramps_id=gramps_id)
        if match_list.count() > 0:
            return self.make_person(match_list[0])
        else:
            return None

    def get_family_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        try:
            family = self.dji.Family.get(gramps_id=gramps_id)
        except:
            return None
        return self.make_family(family)

    def get_source_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        match_list = self.dji.Source.filter(gramps_id=gramps_id)
        if match_list.count() > 0:
            return self.make_source(match_list[0])
        else:
            return None

    def get_citation_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        match_list = self.dji.Citation.filter(gramps_id=gramps_id)
        if match_list.count() > 0:
            return self.make_citation(match_list[0])
        else:
            return None

    def get_event_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        match_list = self.dji.Event.filter(gramps_id=gramps_id)
        if match_list.count() > 0:
            return self.make_event(match_list[0])
        else:
            return None

    def get_object_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        match_list = self.dji.Media.filter(gramps_id=gramps_id)
        if match_list.count() > 0:
            return self.make_media(match_list[0])
        else:
            return None

    def get_place_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        match_list = self.dji.Place.filter(gramps_id=gramps_id)
        if match_list.count() > 0:
            return self.make_place(match_list[0])
        else:
            return None

    def get_repository_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        match_list = self.dji.Repsoitory.filter(gramps_id=gramps_id)
        if match_list.count() > 0:
            return self.make_repository(match_list[0])
        else:
            return None

    def get_note_from_gramps_id(self, gramps_id):
        if self.import_cache:
            for handle in self.import_cache:
                if self.import_cache[handle].gramps_id == gramps_id:
                    return self.import_cache[handle]
        match_list = self.dji.Note.filter(gramps_id=gramps_id)
        if match_list.count() > 0:
            return self.make_note(match_list[0])
        else:
            return None

    def get_number_of_people(self):
        return self.dji.Person.count()

    def get_number_of_events(self):
        return self.dji.Event.count()

    def get_number_of_places(self):
        return self.dji.Place.count()

    def get_number_of_tags(self):
        return self.dji.Tag.count()

    def get_number_of_families(self):
        return self.dji.Family.count()

    def get_number_of_notes(self):
        return self.dji.Note.count()

    def get_number_of_citations(self):
        return self.dji.Citation.count()

    def get_number_of_sources(self):
        return self.dji.Source.count()

    def get_number_of_media_objects(self):
        return self.dji.Media.count()

    def get_number_of_repositories(self):
        return self.dji.Repository.count()

    def get_place_cursor(self):
        return Cursor(self.dji.Place, self.get_raw_place_data)

    def get_person_cursor(self):
        return Cursor(self.dji.Person, self.get_raw_person_data)

    def get_family_cursor(self):
        return Cursor(self.dji.Family, self.get_raw_family_data)

    def get_event_cursor(self):
        return Cursor(self.dji.Event, self.get_raw_event_data)

    def get_citation_cursor(self):
        return Cursor(self.dji.Citation, self.get_raw_citation_data)

    def get_source_cursor(self):
        return Cursor(self.dji.Source, self.get_raw_source_data)

    def get_note_cursor(self):
        return Cursor(self.dji.Note, self.get_raw_note_data)

    def get_tag_cursor(self):
        return Cursor(self.dji.Tag, self.get_raw_tag_data)

    def get_repository_cursor(self):
        return Cursor(self.dji.Repository, self.get_raw_repository_data)

    def get_media_cursor(self):
        return Cursor(self.dji.Media, self.get_raw_object_data)

    def has_gramps_id(self, obj_key, gramps_id):
        key2table = {
            PERSON_KEY:     self.dji.Person, 
            FAMILY_KEY:     self.dji.Family, 
            SOURCE_KEY:     self.dji.Source, 
            CITATION_KEY:   self.dji.Citation, 
            EVENT_KEY:      self.dji.Event, 
            MEDIA_KEY:      self.dji.Media, 
            PLACE_KEY:      self.dji.Place, 
            REPOSITORY_KEY: self.dji.Repository, 
            NOTE_KEY:       self.dji.Note, 
            }
        table = key2table[obj_key]
        return table.filter(gramps_id=gramps_id).count() > 0

    def has_person_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Person.filter(handle=handle).count() == 1

    def has_family_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Family.filter(handle=handle).count() == 1

    def has_citation_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Citation.filter(handle=handle).count() == 1

    def has_source_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Source.filter(handle=handle).count() == 1

    def has_repository_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Repository.filter(handle=handle).count() == 1

    def has_note_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Note.filter(handle=handle).count() == 1

    def has_place_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Place.filter(handle=handle).count() == 1

    def has_event_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Event.filter(handle=handle).count() == 1

    def has_tag_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Tag.filter(handle=handle).count() == 1

    def has_object_handle(self, handle):
        if handle in self.import_cache:
            return True
        return self.dji.Media.filter(handle=handle).count() == 1

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
        try:
            return self.dji.get_person(self.dji.Person.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_family_data(self, handle):
        try:
            return self.dji.get_family(self.dji.Family.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_citation_data(self, handle):
        try:
            return self.dji.get_citation(self.dji.Citation.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_source_data(self, handle):
        try:
            return self.dji.get_source(self.dji.Source.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_repository_data(self, handle):
        try:
            return self.dji.get_repository(self.dji.Repository.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_note_data(self, handle):
        try:
            return self.dji.get_note(self.dji.Note.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_place_data(self, handle):
        try:
            return self.dji.get_place(self.dji.Place.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_object_data(self, handle):
        try:
            return self.dji.get_media(self.dji.Media.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_tag_data(self, handle):
        try:
            return self.dji.get_tag(self.dji.Tag.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
                return None

    def get_raw_event_data(self, handle):
        try:
            return self.dji.get_event(self.dji.Event.get(handle=handle))
        except:
            if handle in self.import_cache:
                return self.import_cache[handle].serialize()
            else:
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
        self.commit_event(tag, trans)
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
        if self.use_import_cache:
            self.import_cache[person.handle] = person
        else:
            raw = person.serialize()
            items = self.dji.Person.filter(handle=person.handle)
            if items.count() > 0:
                # Hack, for the moment: delete and re-add
                items[0].delete()
            self.dji.add_person(person.serialize())
            self.dji.add_person_detail(person.serialize())
            if items.count() > 0:
                self.emit("person-update", ([person.handle],))
            else:
                self.emit("person-add", ([person.handle],))

    def commit_family(self, family, trans, change_time=None):
        if self.use_import_cache:
            self.import_cache[family.handle] = family
        else:
            raw = family.serialize()
            items = self.dji.Family.filter(handle=family.handle)
            if items.count() > 0:
                items[0].delete()
            self.dji.add_family(family.serialize())
            self.dji.add_family_detail(family.serialize())
            if items.count() > 0:
                self.emit("family-update", ([family.handle],))
            else:
                self.emit("family-add", ([family.handle],))

    def commit_citation(self, citation, trans, change_time=None):
        if self.use_import_cache:
            self.import_cache[citation.handle] = citation
        else:
            raw = citation.serialize()
            items = self.dji.Citation.filter(handle=citation.handle)
            if items.count() > 0:
                items[0].delete()
            self.dji.add_citation(citation.serialize())
            self.dji.add_citation_detail(citation.serialize())
            if items.count() > 0:
                self.emit("citation-update", ([citation.handle],))
            else:
                self.emit("citation-add", ([citation.handle],))

    def commit_source(self, source, trans, change_time=None):
        if self.use_import_cache:
            self.import_cache[source.handle] = source
        else:
            raw = source.serialize()
            items = self.dji.Source.filter(handle=source.handle)
            if items.count() > 0:
                items[0].delete()
            self.dji.add_source(source.serialize())
            self.dji.add_source_detail(source.serialize())
            if items.count() > 0:
                self.emit("source-update", ([source.handle],))
            else:
                self.emit("source-add", ([source.handle],))

    def commit_repository(self, repository, trans, change_time=None):
        if self.use_import_cache:
            self.import_cache[repository.handle] = repository
        else:
            raw = repository.serialize()
            items = self.dji.Repository.filter(handle=repository.handle)
            if items.count() > 0:
                items[0].delete()
            self.dji.add_repository(repository.serialize())
            self.dji.add_repository_detail(repository.serialize())
            if items.count() > 0:
                self.emit("repository-update", ([repository.handle],))
            else:
                self.emit("repository-add", ([repository.handle],))

    def commit_note(self, note, trans, change_time=None):
        if self.use_import_cache:
            self.import_cache[note.handle] = note
        else:
            raw = note.serialize()
            items = self.dji.Note.filter(handle=note.handle)
            if items.count() > 0:
                items[0].delete()
            self.dji.add_note(note.serialize())
            self.dji.add_note_detail(note.serialize())
            if items.count() > 0:
                self.emit("note-update", ([note.handle],))
            else:
                self.emit("note-add", ([note.handle],))

    def commit_place(self, place, trans, change_time=None):
        if self.use_import_cache:
            self.import_cache[place.handle] = place
        else:
            raw = place.serialize()
            items = self.dji.Place.filter(handle=place.handle)
            if items.count() > 0:
                items[0].delete()
            self.dji.add_place(place.serialize())
            self.dji.add_place_detail(place.serialize())
            if items.count() > 0:
                self.emit("place-update", ([place.handle],))
            else:
                self.emit("place-add", ([place.handle],))

    def commit_event(self, event, trans, change_time=None):
        if self.use_import_cache:
            self.import_cache[event.handle] = event
        else:
            raw = event.serialize()
            items = self.dji.Event.filter(handle=event.handle)
            if items.count() > 0:
                items[0].delete()
            self.dji.add_event(event.serialize())
            self.dji.add_event_detail(event.serialize())
            if items.count() > 0:
                self.emit("event-update", ([event.handle],))
            else:
                self.emit("event-add", ([event.handle],))

    def commit_tag(self, tag, trans, change_time=None):
        if self.use_import_cache:
            self.import_cache[tag.handle] = tag
        else:
            raw = tag.serialize()
            items = self.dji.Tag.filter(handle=tag.handle)
            if items.count() > 0:
                items[0].delete()
            self.dji.add_tag(tag.serialize())
            self.dji.add_tag_detail(tag.serialize())
            if items.count() > 0:
                self.emit("tag-update", ([tag.handle],))
            else:
                self.emit("tag-add", ([tag.handle],))

    def commit_media_object(self, media, transaction, change_time=None):
        """
        Commit the specified MediaObject to the database, storing the changes
        as part of the transaction.
        """
        if self.use_import_cache:
            self.import_cache[obj.handle] = media
        else:
            raw = media.serialize()
            items = self.dji.Media.filter(handle=media.handle)
            if items.count() > 0:
                items[0].delete()
            self.dji.add_media(media.serialize())
            self.dji.add_media_detail(media.serialize())
            if items.count() > 0:
                self.emit("media-update", ([media.handle],))
            else:
                self.emit("media-add", ([media.handle],))

    def get_gramps_ids(self, obj_key):
        key2table = {
            PERSON_KEY:     self.id_trans, 
            FAMILY_KEY:     self.fid_trans, 
            CITATION_KEY:   self.cid_trans, 
            SOURCE_KEY:     self.sid_trans, 
            EVENT_KEY:      self.eid_trans, 
            MEDIA_KEY:      self.oid_trans, 
            PLACE_KEY:      self.pid_trans, 
            REPOSITORY_KEY: self.rid_trans, 
            NOTE_KEY:       self.nid_trans, 
            }

        table = key2table[obj_key]
        return list(table.keys())

    def transaction_begin(self, transaction):
        return 

    def set_researcher(self, owner):
        pass

    def copy_from_db(self, db):
        """
        A (possibily) implementation-specific method to get data from
        db into this database.
        """
        # First we add the primary objects:
        for key in db._tables.keys():
            cursor = db._tables[key]["cursor_func"]
            for (handle, data) in cursor():
                if key == "Person":
                    self.dji.add_person(data)
                elif key == "Family":
                    self.dji.add_family(data)
                elif key == "Event":
                    self.dji.add_event(data)
                elif key == "Place":
                    self.dji.add_place(data)
                elif key == "Repository":
                    self.dji.add_repository(data)
                elif key == "Citation":
                    self.dji.add_citation(data)
                elif key == "Source":
                    self.dji.add_source(data)
                elif key == "Note":
                    self.dji.add_note(data)
                elif key == "Media":
                    self.dji.add_media(data)
                elif key == "Tag":
                    self.dji.add_tag(data)
        for key in db._tables.keys():
            cursor = db._tables[key]["cursor_func"]
            for (handle, data) in cursor():
                if key == "Person":
                    self.dji.add_person_detail(data)
                elif key == "Family":
                    self.dji.add_family_detail(data)
                elif key == "Event":
                    self.dji.add_event_detail(data)
                elif key == "Place":
                    self.dji.add_place_detail(data)
                elif key == "Repository":
                    self.dji.add_repository_detail(data)
                elif key == "Citation":
                    self.dji.add_citation_detail(data)
                elif key == "Source":
                    self.dji.add_source_detail(data)
                elif key == "Note":
                    self.dji.add_note_detail(data)
                elif key == "Media":
                    self.dji.add_media_detail(data)
                elif key == "Tag":
                    self.dji.add_tag_detail(data)
            # Next we add the links:
        self.dji.update_publics()

    def get_from_name_and_handle(self, table_name, handle):
        """
        Returns a gen.lib object (or None) given table_name and
        handle.

        Examples:

        >>> self.get_from_name_and_handle("Person", "a7ad62365bc652387008")
        >>> self.get_from_name_and_handle("Media", "c3434653675bcd736f23")
        """
        if table_name in self._tables:
            return self._tables[table_name]["handle_func"](handle)
        return None

    def is_empty(self):
        """
        Is the database empty?
        """
        return (self.get_number_of_people() == 0 and
                self.get_number_of_events() == 0 and
                self.get_number_of_places() == 0 and
                self.get_number_of_tags() == 0 and
                self.get_number_of_families() == 0 and
                self.get_number_of_notes() == 0 and
                self.get_number_of_citations() == 0 and
                self.get_number_of_sources() == 0 and
                self.get_number_of_media_objects() == 0 and
                self.get_number_of_repositories() == 0)
                
    def set_prefixes(self, person, media, family, source, citation,
                     place, event, repository, note):
        self.set_person_id_prefix(person)
        self.set_object_id_prefix(media)
        self.set_family_id_prefix(family)
        self.set_source_id_prefix(source)
        self.set_citation_id_prefix(citation)
        self.set_place_id_prefix(place)
        self.set_event_id_prefix(event)
        self.set_repository_id_prefix(repository)
        self.set_note_id_prefix(note)

    def has_changed(self):
        return False

    def find_backlink_handles(self, handle, include_classes=None):
        ## FIXME: figure out how to get objects that refer
        ## to this handle
        return []

    def get_note_bookmarks(self):
        return self.note_bookmarks

    def get_media_bookmarks(self):
        return self.media_bookmarks

    def get_repo_bookmarks(self):
        return self.repo_bookmarks

    def get_citation_bookmarks(self):
        return self.citation_bookmarks

    def get_source_bookmarks(self):
        return self.source_bookmarks

    def get_place_bookmarks(self):
        return self.place_bookmarks

    def get_event_bookmarks(self):
        return self.event_bookmarks

    def get_bookmarks(self):
        return self.bookmarks

    def get_family_bookmarks(self):
        return self.family_bookmarks

    def get_save_path(self):
        return self._directory

    def set_save_path(self, directory):
        self._directory = directory

    ## Get types:
    def get_event_attribute_types(self):
        """
        Return a list of all Attribute types assocated with Event instances
        in the database.
        """
        return list(self.event_attributes)

    def get_event_types(self):
        """
        Return a list of all event types in the database.
        """
        return list(self.event_names)

    def get_person_event_types(self):
        """
        Deprecated:  Use get_event_types
        """
        return list(self.event_names)

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
        Deprecated:  Use get_event_types
        """
        return list(self.event_names)

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

    def get_origin_types(self):
        """
        Return a list of all custom origin types assocated with Person/Surname
        instances in the database.
        """
        return list(self.origin_types)

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

    def get_source_attribute_types(self):
        """
        Return a list of all Attribute types assocated with Source/Citation
        instances in the database.
        """
        return list(self.source_attributes)

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

    def get_place_types(self):
        """
        Return a list of all custom place types assocated with Place instances
        in the database.
        """
        return list(self.place_types)

    def get_default_handle(self):
        people = self.dji.Person.all()
        if people.count() > 0:
            return people[0].handle
        return None

    def close(self):
        pass

    def get_surname_list(self):
        return []

    def is_open(self):
        return True

    def get_table_names(self):
        """Return a list of valid table names."""
        return list(self._tables.keys())

    def find_initial_person(self):
        return self.get_default_person()

    # Removals:
    def remove_person(self, handle, txn):
        self.dji.Person.filter(handle=handle)[0].delete()
        self.emit("person-delete", ([handle],))

    def remove_source(self, handle, transaction):
        self.dji.Source.filter(handle=handle)[0].delete()
        self.emit("source-delete", ([handle],))

    def remove_citation(self, handle, transaction):
        self.dji.Citation.filter(handle=handle)[0].delete()
        self.emit("citation-delete", ([handle],))

    def remove_event(self, handle, transaction):
        self.dji.Event.filter(handle=handle)[0].delete()
        self.emit("event-delete", ([handle],))

    def remove_object(self, handle, transaction):
        self.dji.Media.filter(handle=handle)[0].delete()
        self.emit("media-delete", ([handle],))

    def remove_place(self, handle, transaction):
        self.dji.Place.filter(handle=handle)[0].delete()
        self.emit("place-delete", ([handle],))

    def remove_family(self, handle, transaction):
        self.dji.Family.filter(handle=handle)[0].delete()
        self.emit("family-delete", ([handle],))

    def remove_repository(self, handle, transaction):
        self.dji.Repository.filter(handle=handle)[0].delete()
        self.emit("repository-delete", ([handle],))

    def remove_note(self, handle, transaction):
        self.dji.Note.filter(handle=handle)[0].delete()
        self.emit("note-delete", ([handle],))

    def remove_tag(self, handle, transaction):
        self.dji.Tag.filter(handle=handle)[0].delete()
        self.emit("tag-delete", ([handle],))

    def remove_from_surname_list(self, person):
        ## FIXME
        pass
    
    def get_dbname(self):
        return "Django Database"

    ## missing

    def find_place_child_handles(self, handle):
        pass

    def get_cursor(self, table, txn=None, update=False, commit=False):
        pass

    def get_from_name_and_handle(self, table_name, handle):
        """
        Returns a gen.lib object (or None) given table_name and
        handle.

        Examples:

        >>> self.get_from_name_and_handle("Person", "a7ad62365bc652387008")
        >>> self.get_from_name_and_handle("Media", "c3434653675bcd736f23")
        """
        if table_name in self._tables:
            return self._tables[table_name]["handle_func"](handle)
        return None

    def get_number_of_records(self, table):
        pass

    def get_place_parent_cursor(self):
        pass

    def get_place_tree_cursor(self):
        pass

    def get_table_metadata(self, table_name):
        """Return the metadata for a valid table name."""
        if table_name in self._tables:
            return self._tables[table_name]
        return None

    def get_transaction_class(self):
        pass

    def undo(self, update_history=True):
        # FIXME:
        return self.undodb.undo(update_history)

    def redo(self, update_history=True):
        # FIXME:
        return self.undodb.redo(update_history)

    def backup(self):
        pass

    def restore(self):
        pass

    def write_version(self, directory):
        """Write files for a newly created DB."""
        versionpath = os.path.join(directory, str(DBBACKEND))
        _LOG.debug("Write database backend file to 'djangodb'")
        with open(versionpath, "w") as version_file:
            version_file.write("djangodb")
        # Write default_settings, sqlite.db
        defaults = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "django_support", "defaults")
        _LOG.debug("Copy defaults from: " + defaults)
        for filename in os.listdir(defaults):
            fullpath = os.path.abspath(os.path.join(defaults, filename))
            shutil.copy2(fullpath, directory)
