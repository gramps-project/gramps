#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015 Douglas S. Blank <doug.blank@gmail.com>
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

#------------------------------------------------------------------------
#
# Python Modules
#
#------------------------------------------------------------------------
import random
import pickle
import base64
import time
import re
import os
import logging
import shutil
import bisect
import ast

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
import gramps
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.db import (DbReadBase, DbWriteBase, DbTxn, DbUndo,
                           KEY_TO_NAME_MAP, KEY_TO_CLASS_MAP,
                           CLASS_TO_KEY_MAP, TXNADD, TXNUPD, TXNDEL)
from gramps.gen.utils.callback import Callback
from gramps.gen.updatecallback import UpdateCallback
from gramps.gen.db.dbconst import *
from gramps.gen.db import (PERSON_KEY,
                           FAMILY_KEY,
                           CITATION_KEY,
                           SOURCE_KEY,
                           EVENT_KEY,
                           MEDIA_KEY,
                           PLACE_KEY,
                           REPOSITORY_KEY,
                           NOTE_KEY,
                           TAG_KEY)

from gramps.gen.utils.id import create_id
from gramps.gen.lib.researcher import Researcher
from gramps.gen.lib import (Tag, MediaObject, Person, Family, Source, Citation, Event,
                            Place, Repository, Note, NameOriginType)
from gramps.gen.lib.genderstats import GenderStats

LOG = logging.getLogger(DBLOGNAME)

SIGBASE = ('person', 'family', 'source', 'event', 'media',
           'place', 'repository', 'reference', 'note', 'tag', 'citation')

def touch(fname, mode=0o666, dir_fd=None, **kwargs):
    ## After http://stackoverflow.com/questions/1158076/implement-touch-using-python
    flags = os.O_CREAT | os.O_APPEND
    with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
        os.utime(f.fileno() if os.utime in os.supports_fd else fname,
                 dir_fd=None if os.supports_fd else dir_fd, **kwargs)

class DbGenericUndo(DbUndo):
    def __init__(self, grampsdb, path):
        super(DbGenericUndo, self).__init__(grampsdb)
        self.undodb = []

    def open(self, value=None):
        """
        Open the backing storage.  Needs to be overridden in the derived
        class.
        """
        pass

    def close(self):
        """
        Close the backing storage.  Needs to be overridden in the derived
        class.
        """
        pass

    def append(self, value):
        """
        Add a new entry on the end.  Needs to be overridden in the derived
        class.
        """
        self.undodb.append(value)

    def __getitem__(self, index):
        """
        Returns an entry by index number.  Needs to be overridden in the
        derived class.
        """
        return self.undodb[index]

    def __setitem__(self, index, value):
        """
        Set an entry to a value.  Needs to be overridden in the derived class.
        """
        self.undodb[index] = value

    def __len__(self):
        """
        Returns the number of entries.  Needs to be overridden in the derived
        class.
        """
        return len(self.undodb)

    def _redo(self, update_history):
        """
        Access the last undone transaction, and revert the data to the state
        before the transaction was undone.
        """
        txn = self.redoq.pop()
        self.undoq.append(txn)
        transaction = txn
        db = self.db
        subitems = transaction.get_recnos()

        # Process all records in the transaction
        for record_id in subitems:
            (key, trans_type, handle, old_data, new_data) = \
                pickle.loads(self.undodb[record_id])

            if key == REFERENCE_KEY:
                self.undo_reference(new_data, handle, self.mapbase[key])
            else:
                self.undo_data(new_data, handle, self.mapbase[key],
                                    db.emit, SIGBASE[key])
        # Notify listeners
        if db.undo_callback:
            db.undo_callback(_("_Undo %s")
                                   % transaction.get_description())

        if db.redo_callback:
            if self.redo_count > 1:
                new_transaction = self.redoq[-2]
                db.redo_callback(_("_Redo %s")
                                   % new_transaction.get_description())
            else:
                db.redo_callback(None)

        if update_history and db.undo_history_callback:
            db.undo_history_callback()
        return True

    def _undo(self, update_history):
        """
        Access the last committed transaction, and revert the data to the
        state before the transaction was committed.
        """
        txn = self.undoq.pop()
        self.redoq.append(txn)
        transaction = txn
        db = self.db
        subitems = transaction.get_recnos(reverse=True)

        # Process all records in the transaction
        for record_id in subitems:
            (key, trans_type, handle, old_data, new_data) = \
                    pickle.loads(self.undodb[record_id])

            if key == REFERENCE_KEY:
                self.undo_reference(old_data, handle, self.mapbase[key])
            else:
                self.undo_data(old_data, handle, self.mapbase[key],
                                db.emit, SIGBASE[key])
        # Notify listeners
        if db.undo_callback:
            if self.undo_count > 0:
                db.undo_callback(_("_Undo %s")
                                   % self.undoq[-1].get_description())
            else:
                db.undo_callback(None)

        if db.redo_callback:
            db.redo_callback(_("_Redo %s")
                                   % transaction.get_description())

        if update_history and db.undo_history_callback:
            db.undo_history_callback()
        return True

class Environment(object):
    """
    Implements the Environment API.
    """
    def __init__(self, db):
        self.db = db

    def txn_begin(self):
        return DbGenericTxn("DbGenericDb Transaction", self.db)

    def txn_checkpoint(self):
        pass

class Table(object):
    """
    Implements Table interface.
    """
    def __init__(self, db, table_name, funcs=None):
        self.db = db
        self.table_name = table_name
        if funcs:
            self.funcs = funcs
        else:
            self.funcs = db._tables[table_name]

    def cursor(self):
        """
        Returns a Cursor for this Table.
        """
        return self.funcs["cursor_func"]()

    def put(self, key, data, txn=None):
        self.funcs["add_func"](data, txn)

class Map(object):
    """
    Implements the map API for person_map, etc.

    Takes a Table() as argument.
    """
    def __init__(self, table,
                 keys_func="handles_func",
                 contains_func="has_handle_func",
                 raw_func="raw_func",
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = table
        self.keys_func = keys_func
        self.contains_func = contains_func
        self.raw_func = raw_func
        self.txn = DbGenericTxn("Dummy transaction", db=self.table.db, batch=True)

    def keys(self):
        return self.table.funcs[self.keys_func]()

    def get(self, key):
        return self[key]

    def values(self):
        return self.table.funcs["cursor_func"]()

    def __contains__(self, key):
        return self.table.funcs[self.contains_func](key)

    def __getitem__(self, key):
        if self.table.funcs[self.contains_func](key):
            return self.table.funcs[self.raw_func](key)

    def __setitem__(self, key, value):
        """
        This is only done in a low-level raw import.

        value: serialized object
        key: bytes key (ignored in this implementation)
        """
        obj = self.table.funcs["class_func"].create(value)
        self.table.funcs["commit_func"](obj, self.txn)

    def __len__(self):
        return self.table.funcs["count_func"]()

    def delete(self, key):
        self.table.funcs["del_func"](key, self.txn)

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
    def __init__(self, map):
        self.map = map
        self._iter = self.__iter__()
    def __enter__(self):
        return self
    def __iter__(self):
        for item in self.map.keys():
            yield (bytes(item, "utf-8"), self.map[item])
    def __next__(self):
        try:
            return self._iter.__next__()
        except StopIteration:
            return None
    def __exit__(self, *args, **kwargs):
        pass
    def iter(self):
        for item in self.map.keys():
            yield (bytes(item, "utf-8"), self.map[item])
    def first(self):
        self._iter = self.__iter__()
        try:
            return next(self._iter)
        except:
            return
    def next(self):
        try:
            return next(self._iter)
        except:
            return
    def close(self):
        pass

class TreeCursor(Cursor):

    def __init__(self, db, map):
        """
        """
        self.db = db
        Cursor.__init__(self, map)

    def __iter__(self):
        """
        Iterator
        """
        handles = self.db.get_place_handles(sort_handles=True)
        for handle in handles:
            yield (bytes(handle, "utf-8"), self.db._get_raw_place_data(handle))

class Bookmarks(object):
    def __init__(self, default=[]):
        self.handles = list(default)

    def set(self, handles):
        self.handles = list(handles)

    def get(self):
        return self.handles

    def append(self, handle):
        self.handles.append(handle)

    def append_list(self, handles):
        self.handles += handles

    def remove(self, handle):
        self.handles.remove(handle)

    def pop(self, item):
        return self.handles.pop(item)

    def insert(self, pos, item):
        self.handles.insert(pos, item)

    def close(self):
        del self.handles


class DbGenericTxn(DbTxn):
    def __init__(self, message, db, batch=False):
        DbTxn.__init__(self, message, db, batch)

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

class DbGeneric(DbWriteBase, DbReadBase, UpdateCallback, Callback):
    """
    A Gramps Database Backend. This replicates the grampsdb functions.
    """
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
        self._tables['Person'].update(
            {
                "handle_func": self.get_person_from_handle,
                "gramps_id_func": self.get_person_from_gramps_id,
                "class_func": Person,
                "cursor_func": self.get_person_cursor,
                "handles_func": self.get_person_handles,
                "add_func": self.add_person,
                "commit_func": self.commit_person,
                "iter_func": self.iter_people,
                "ids_func": self.get_person_gramps_ids,
                "has_handle_func": self.has_handle_for_person,
                "has_gramps_id_func": self.has_gramps_id_for_person,
                "count_func": self.get_number_of_people,
                "raw_func": self._get_raw_person_data,
                "raw_id_func": self._get_raw_person_from_id_data,
                "del_func": self.remove_person,
            })
        self._tables['Family'].update(
            {
                "handle_func": self.get_family_from_handle,
                "gramps_id_func": self.get_family_from_gramps_id,
                "class_func": Family,
                "cursor_func": self.get_family_cursor,
                "handles_func": self.get_family_handles,
                "add_func": self.add_family,
                "commit_func": self.commit_family,
                "iter_func": self.iter_families,
                "ids_func": self.get_family_gramps_ids,
                "has_handle_func": self.has_handle_for_family,
                "has_gramps_id_func": self.has_gramps_id_for_family,
                "count_func": self.get_number_of_families,
                "raw_func": self._get_raw_family_data,
                "raw_id_func": self._get_raw_family_from_id_data,
                "del_func": self.remove_family,
            })
        self._tables['Source'].update(
            {
                "handle_func": self.get_source_from_handle,
                "gramps_id_func": self.get_source_from_gramps_id,
                "class_func": Source,
                "cursor_func": self.get_source_cursor,
                "handles_func": self.get_source_handles,
                "add_func": self.add_source,
                "commit_func": self.commit_source,
                "iter_func": self.iter_sources,
                "ids_func": self.get_source_gramps_ids,
                "has_handle_func": self.has_handle_for_source,
                "has_gramps_id_func": self.has_gramps_id_for_source,
                "count_func": self.get_number_of_sources,
                "raw_func": self._get_raw_source_data,
                "raw_id_func": self._get_raw_source_from_id_data,
                "del_func": self.remove_source,
                })
        self._tables['Citation'].update(
            {
                "handle_func": self.get_citation_from_handle,
                "gramps_id_func": self.get_citation_from_gramps_id,
                "class_func": Citation,
                "cursor_func": self.get_citation_cursor,
                "handles_func": self.get_citation_handles,
                "add_func": self.add_citation,
                "commit_func": self.commit_citation,
                "iter_func": self.iter_citations,
                "ids_func": self.get_citation_gramps_ids,
                "has_handle_func": self.has_handle_for_citation,
                "has_gramps_id_func": self.has_gramps_id_for_citation,
                "count_func": self.get_number_of_citations,
                "raw_func": self._get_raw_citation_data,
                "raw_id_func": self._get_raw_citation_from_id_data,
                "del_func": self.remove_citation,
            })
        self._tables['Event'].update(
            {
                "handle_func": self.get_event_from_handle,
                "gramps_id_func": self.get_event_from_gramps_id,
                "class_func": Event,
                "cursor_func": self.get_event_cursor,
                "handles_func": self.get_event_handles,
                "add_func": self.add_event,
                "commit_func": self.commit_event,
                "iter_func": self.iter_events,
                "ids_func": self.get_event_gramps_ids,
                "has_handle_func": self.has_handle_for_event,
                "has_gramps_id_func": self.has_gramps_id_for_event,
                "count_func": self.get_number_of_events,
                "raw_func": self._get_raw_event_data,
                "raw_id_func": self._get_raw_event_from_id_data,
                "del_func": self.remove_event,
            })
        self._tables['Media'].update(
            {
                "handle_func": self.get_object_from_handle,
                "gramps_id_func": self.get_object_from_gramps_id,
                "class_func": MediaObject,
                "cursor_func": self.get_media_cursor,
                "handles_func": self.get_media_object_handles,
                "add_func": self.add_object,
                "commit_func": self.commit_media_object,
                "iter_func": self.iter_media_objects,
                "ids_func": self.get_media_gramps_ids,
                "has_handle_func": self.has_handle_for_media,
                "has_gramps_id_func": self.has_gramps_id_for_media,
                "count_func": self.get_number_of_media_objects,
                "raw_func": self._get_raw_media_data,
                "raw_id_func": self._get_raw_media_from_id_data,
                "del_func": self.remove_object,
            })
        self._tables['Place'].update(
            {
                "handle_func": self.get_place_from_handle,
                "gramps_id_func": self.get_place_from_gramps_id,
                "class_func": Place,
                "cursor_func": self.get_place_cursor,
                "handles_func": self.get_place_handles,
                "add_func": self.add_place,
                "commit_func": self.commit_place,
                "iter_func": self.iter_places,
                "ids_func": self.get_place_gramps_ids,
                "has_handle_func": self.has_handle_for_place,
                "has_gramps_id_func": self.has_gramps_id_for_place,
                "count_func": self.get_number_of_places,
                "raw_func": self._get_raw_place_data,
                "raw_id_func": self._get_raw_place_from_id_data,
                "del_func": self.remove_place,
            })
        self._tables['Repository'].update(
            {
                "handle_func": self.get_repository_from_handle,
                "gramps_id_func": self.get_repository_from_gramps_id,
                "class_func": Repository,
                "cursor_func": self.get_repository_cursor,
                "handles_func": self.get_repository_handles,
                "add_func": self.add_repository,
                "commit_func": self.commit_repository,
                "iter_func": self.iter_repositories,
                "ids_func": self.get_repository_gramps_ids,
                "has_handle_func": self.has_handle_for_repository,
                "has_gramps_id_func": self.has_gramps_id_for_repository,
                "count_func": self.get_number_of_repositories,
                "raw_func": self._get_raw_repository_data,
                "raw_id_func": self._get_raw_repository_from_id_data,
                "del_func": self.remove_repository,
            })
        self._tables['Note'].update(
            {
                "handle_func": self.get_note_from_handle,
                "gramps_id_func": self.get_note_from_gramps_id,
                "class_func": Note,
                "cursor_func": self.get_note_cursor,
                "handles_func": self.get_note_handles,
                "add_func": self.add_note,
                "commit_func": self.commit_note,
                "iter_func": self.iter_notes,
                "ids_func": self.get_note_gramps_ids,
                "has_handle_func": self.has_handle_for_note,
                "has_gramps_id_func": self.has_gramps_id_for_note,
                "count_func": self.get_number_of_notes,
                "raw_func": self._get_raw_note_data,
                "raw_id_func": self._get_raw_note_from_id_data,
                "del_func": self.remove_note,
            })
        self._tables['Tag'].update(
            {
                "handle_func": self.get_tag_from_handle,
                "gramps_id_func": None,
                "class_func": Tag,
                "cursor_func": self.get_tag_cursor,
                "handles_func": self.get_tag_handles,
                "add_func": self.add_tag,
                "commit_func": self.commit_tag,
                "has_handle_func": self.has_handle_for_tag,
                "iter_func": self.iter_tags,
                "count_func": self.get_number_of_tags,
                "raw_func": self._get_raw_tag_data,
                "del_func": self.remove_tag,
            })
        self.set_save_path(directory)
        # skip GEDCOM cross-ref check for now:
        self.set_feature("skip-check-xref", True)
        self.set_feature("skip-import-additions", True)
        self.readonly = False
        self.db_is_open = True
        self.name_formats = []
        # Bookmarks:
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
        self.undodb = None
        self.id_trans  = DbGenericTxn("ID Transaction", self)
        self.fid_trans = DbGenericTxn("FID Transaction", self)
        self.pid_trans = DbGenericTxn("PID Transaction", self)
        self.cid_trans = DbGenericTxn("CID Transaction", self)
        self.sid_trans = DbGenericTxn("SID Transaction", self)
        self.oid_trans = DbGenericTxn("OID Transaction", self)
        self.rid_trans = DbGenericTxn("RID Transaction", self)
        self.nid_trans = DbGenericTxn("NID Transaction", self)
        self.eid_trans = DbGenericTxn("EID Transaction", self)
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
        self.person_map = Map(Table(self, "Person"))
        self.person_id_map = Map(Table(self, "Person"),
                                 keys_func="ids_func",
                                 contains_func="has_gramps_id_func",
                                 raw_func="raw_id_func")
        self.family_map = Map(Table(self, "Family"))
        self.family_id_map = Map(Table(self, "Family"),
                                 keys_func="ids_func",
                                 contains_func="has_gramps_id_func",
                                 raw_func="raw_id_func")
        self.place_map  = Map(Table(self, "Place"))
        self.place_id_map = Map(Table(self, "Place"),
                                keys_func="ids_func",
                                contains_func="has_gramps_id_func",
                                raw_func="raw_id_func")
        self.citation_map = Map(Table(self, "Citation"))
        self.citation_id_map = Map(Table(self, "Citation"),
                                   keys_func="ids_func",
                                   contains_func="has_gramps_id_func",
                                   raw_func="raw_id_func")
        self.source_map = Map(Table(self, "Source"))
        self.source_id_map = Map(Table(self, "Source"),
                                 keys_func="ids_func",
                                 contains_func="has_gramps_id_func",
                                 raw_func="raw_id_func")
        self.repository_map  = Map(Table(self, "Repository"))
        self.repository_id_map = Map(Table(self, "Repository"),
                                     keys_func="ids_func",
                                     contains_func="has_gramps_id_func",
                                     raw_func="raw_id_func")
        self.note_map = Map(Table(self, "Note"))
        self.note_id_map = Map(Table(self, "Note"),
                               keys_func="ids_func",
                               contains_func="has_gramps_id_func",
                               raw_func="raw_id_func")
        self.media_map  = Map(Table(self, "Media"))
        self.media_id_map = Map(Table(self, "Media"),
                                keys_func="ids_func",
                                contains_func="has_gramps_id_func",
                                raw_func="raw_id_func")
        self.event_map  = Map(Table(self, "Event"))
        self.event_id_map = Map(Table(self, "Event"),
                                keys_func="ids_func",
                                contains_func="has_gramps_id_func",
                                raw_func="raw_id_func")
        self.tag_map  = Map(Table(self, "Tag"))
        self.metadata   = Map(Table(self, "Metadata", funcs={"cursor_func": lambda: MetaCursor()}))
        self.undo_callback = None
        self.redo_callback = None
        self.undo_history_callback = None
        self.modified   = 0
        self.txn = DbGenericTxn("DbGeneric Transaction", self)
        self.transaction = None
        self.abort_possible = False
        self._bm_changes = 0
        self.has_changed = False
        self.surname_list = []
        self.genderStats = GenderStats() # can pass in loaded stats as dict
        self.owner = Researcher()
        if directory:
            self.load(directory)

    def load(self, directory, callback=None, mode=None,
             force_schema_upgrade=False,
             force_bsddb_upgrade=False,
             force_bsddb_downgrade=False,
             force_python_upgrade=False):
        # run backend-specific code:
        self.initialize_backend(directory)

        # Load metadata
        self.name_formats = self.get_metadata('name_formats')
        self.owner = self.get_metadata('researcher', default=Researcher())

        # Load bookmarks
        self.bookmarks.set(self.get_metadata('bookmarks'))
        self.family_bookmarks.set(self.get_metadata('family_bookmarks'))
        self.event_bookmarks.set(self.get_metadata('event_bookmarks'))
        self.source_bookmarks.set(self.get_metadata('source_bookmarks'))
        self.citation_bookmarks.set(self.get_metadata('citation_bookmarks'))
        self.repo_bookmarks.set(self.get_metadata('repo_bookmarks'))
        self.media_bookmarks.set(self.get_metadata('media_bookmarks'))
        self.place_bookmarks.set(self.get_metadata('place_bookmarks'))
        self.note_bookmarks.set(self.get_metadata('note_bookmarks'))

        # Custom type values
        self.event_names = self.get_metadata('event_names', set())
        self.family_attributes = self.get_metadata('fattr_names', set())
        self.individual_attributes = self.get_metadata('pattr_names', set())
        self.source_attributes = self.get_metadata('sattr_names', set())
        self.marker_names = self.get_metadata('marker_names', set())
        self.child_ref_types = self.get_metadata('child_refs', set())
        self.family_rel_types = self.get_metadata('family_rels', set())
        self.event_role_names = self.get_metadata('event_roles', set())
        self.name_types = self.get_metadata('name_types', set())
        self.origin_types = self.get_metadata('origin_types', set())
        self.repository_types = self.get_metadata('repo_types', set())
        self.note_types = self.get_metadata('note_types', set())
        self.source_media_types = self.get_metadata('sm_types', set())
        self.url_types = self.get_metadata('url_types', set())
        self.media_attributes = self.get_metadata('mattr_names', set())
        self.event_attributes = self.get_metadata('eattr_names', set())
        self.place_types = self.get_metadata('place_types', set())

        # surname list
        self.surname_list = self.get_surname_list()

        self.set_save_path(directory)
        if self._directory:
            self.undolog = os.path.join(self._directory, DBUNDOFN)
        else:
            self.undolog = None
        self.undodb = DbGenericUndo(self, self.undolog)
        self.undodb.open()

        # Other items to load
        gstats = self.get_gender_stats()
        self.genderStats = GenderStats(gstats)

        # Indexes:
        self.cmap_index = self.get_metadata('cmap_index', 0)
        self.smap_index = self.get_metadata('smap_index', 0)
        self.emap_index = self.get_metadata('emap_index', 0)
        self.pmap_index = self.get_metadata('pmap_index', 0)
        self.fmap_index = self.get_metadata('fmap_index', 0)
        self.lmap_index = self.get_metadata('lmap_index', 0)
        self.omap_index = self.get_metadata('omap_index', 0)
        self.rmap_index = self.get_metadata('rmap_index', 0)
        self.nmap_index = self.get_metadata('nmap_index', 0)

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

    def transaction_begin(self, transaction):
        """
        Transactions are handled automatically by the db layer.
        """
        self.transaction = transaction
        return transaction

    def _after_commit(self, transaction):
        """
        Post-transaction commit processing
        """
        if transaction.batch:
            self.env.txn_checkpoint()
            # Only build surname list after surname index is surely back
            self.build_surname_list()

        # Reset callbacks if necessary
        if transaction.batch or not len(transaction):
            return
        if self.undo_callback:
            self.undo_callback(_("_Undo %s") % transaction.get_description())
        if self.redo_callback:
            self.redo_callback(None)
        if self.undo_history_callback:
            self.undo_history_callback()

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
            nr_width = int(pattern_match.group(2))
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

    def _find_next_gramps_id(self, prefix, map_index, map):
        """
        Helper function for find_next_<object>_gramps_id methods
        """
        index = prefix % map_index
        while map.get(str(index)) is not None:
            map_index += 1
            index = prefix % map_index
        map_index += 1
        return (map_index, index)

    def find_next_person_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Person object based off the
        person ID prefix.
        """
        self.pmap_index, gid = self._find_next_gramps_id(self.person_prefix,
                                                         self.pmap_index,
                                                         self.person_id_map)
        return gid

    def find_next_place_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Place object based off the
        place ID prefix.
        """
        self.lmap_index, gid = self._find_next_gramps_id(self.place_prefix,
                                                         self.lmap_index,
                                                         self.place_id_map)
        return gid

    def find_next_event_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Event object based off the
        event ID prefix.
        """
        self.emap_index, gid = self._find_next_gramps_id(self.event_prefix,
                                                         self.emap_index,
                                                         self.event_id_map)
        return gid

    def find_next_object_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a MediaObject object based
        off the media object ID prefix.
        """
        self.omap_index, gid = self._find_next_gramps_id(self.mediaobject_prefix,
                                                         self.omap_index,
                                                         self.media_id_map)
        return gid

    def find_next_citation_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Citation object based off the
        citation ID prefix.
        """
        self.cmap_index, gid = self._find_next_gramps_id(self.citation_prefix,
                                                         self.cmap_index,
                                                         self.citation_id_map)
        return gid

    def find_next_source_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Source object based off the
        source ID prefix.
        """
        self.smap_index, gid = self._find_next_gramps_id(self.source_prefix,
                                                         self.smap_index,
                                                         self.source_id_map)
        return gid

    def find_next_family_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Family object based off the
        family ID prefix.
        """
        self.fmap_index, gid = self._find_next_gramps_id(self.family_prefix,
                                                         self.fmap_index,
                                                         self.family_id_map)
        return gid

    def find_next_repository_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Respository object based
        off the repository ID prefix.
        """
        self.rmap_index, gid = self._find_next_gramps_id(self.repository_prefix,
                                                         self.rmap_index,
                                                         self.repository_id_map)
        return gid

    def find_next_note_gramps_id(self):
        """
        Return the next available GRAMPS' ID for a Note object based off the
        note ID prefix.
        """
        self.nmap_index, gid = self._find_next_gramps_id(self.note_prefix,
                                                         self.nmap_index,
                                                         self.note_id_map)
        return gid

    def get_mediapath(self):
        return self.get_metadata("media-path", "")

    def set_mediapath(self, mediapath):
        return self.set_metadata("media-path", mediapath)

    def get_event_from_handle(self, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        return Event.create(self._get_raw_event_data(handle))

    def get_family_from_handle(self, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        return Family.create(self._get_raw_family_data(handle))

    def get_repository_from_handle(self, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        return Repository.create(self._get_raw_repository_data(handle))

    def get_person_from_handle(self, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        return Person.create(self._get_raw_person_data(handle))

    def get_place_from_handle(self, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        return Place.create(self._get_raw_place_data(handle))

    def get_citation_from_handle(self, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        return Citation.create(self._get_raw_citation_data(handle))

    def get_source_from_handle(self, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        return Source.create(self._get_raw_source_data(handle))

    def get_note_from_handle(self, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        return Note.create(self._get_raw_note_data(handle))

    def get_object_from_handle(self, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        return MediaObject.create(self._get_raw_media_data(handle))

    def get_object_from_gramps_id(self, gramps_id):
        return MediaObject.create(self.media_id_map[gramps_id])

    def get_tag_from_handle(self, handle):
        if isinstance(handle, bytes):
            handle = str(handle, "utf-8")
        return Tag.create(self._get_raw_tag_data(handle))

    def get_default_person(self):
        handle = self.get_default_handle()
        if handle:
            return self.get_person_from_handle(handle)
        else:
            return None

    def iter_people(self):
        return (Person.create(data[1]) for data in self.get_person_cursor())

    def iter_families(self):
        return (Family.create(data[1]) for data in self.get_family_cursor())

    def get_person_from_gramps_id(self, gramps_id):
        return Person.create(self.person_id_map[gramps_id])

    def get_family_from_gramps_id(self, gramps_id):
        return Family.create(self.family_id_map[gramps_id])

    def get_citation_from_gramps_id(self, gramps_id):
        return Citation.create(self.citation_id_map[gramps_id])

    def get_source_from_gramps_id(self, gramps_id):
        return Source.create(self.source_id_map[gramps_id])

    def get_event_from_gramps_id(self, gramps_id):
        return Event.create(self.event_id_map[gramps_id])

    def get_media_from_gramps_id(self, gramps_id):
        return MediaObject.create(self.media_id_map[gramps_id])

    def get_place_from_gramps_id(self, gramps_id):
        return Place.create(self.place_id_map[gramps_id])

    def get_repository_from_gramps_id(self, gramps_id):
        return Repository.create(self.repository_id_map[gramps_id])

    def get_note_from_gramps_id(self, gramps_id):
        return Note.create(self.note_id_map[gramps_id])

    def get_place_cursor(self):
        return Cursor(self.place_map)

    def get_place_tree_cursor(self, *args, **kwargs):
        return TreeCursor(self, self.place_map)

    def get_person_cursor(self):
        return Cursor(self.person_map)

    def get_family_cursor(self):
        return Cursor(self.family_map)

    def get_event_cursor(self):
        return Cursor(self.event_map)

    def get_note_cursor(self):
        return Cursor(self.note_map)

    def get_tag_cursor(self):
        return Cursor(self.tag_map)

    def get_repository_cursor(self):
        return Cursor(self.repository_map)

    def get_media_cursor(self):
        return Cursor(self.media_map)

    def get_citation_cursor(self):
        return Cursor(self.citation_map)

    def get_source_cursor(self):
        return Cursor(self.source_map)

    def has_gramps_id(self, obj_key, gramps_id):
        key2table = {
            PERSON_KEY:     self.person_id_map,
            FAMILY_KEY:     self.family_id_map,
            SOURCE_KEY:     self.source_id_map,
            CITATION_KEY:   self.citation_id_map,
            EVENT_KEY:      self.event_id_map,
            MEDIA_KEY:      self.media_id_map,
            PLACE_KEY:      self.place_id_map,
            REPOSITORY_KEY: self.repository_id_map,
            NOTE_KEY:       self.note_id_map,
            }
        return gramps_id in key2table[obj_key]

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

    def get_raw_person_data(self, handle):
        return self.person_map[handle]

    def get_raw_family_data(self, handle):
        return self.family_map[handle]

    def get_raw_citation_data(self, handle):
        return self.citation_map[handle]

    def get_raw_source_data(self, handle):
        return self.source_map[handle]

    def get_raw_repository_data(self, handle):
        return self.repository_map[handle]

    def get_raw_note_data(self, handle):
        return self.note_map[handle]

    def get_raw_place_data(self, handle):
        return self.place_map[handle]

    def get_raw_object_data(self, handle):
        return self.media_map[handle]

    def get_raw_tag_data(self, handle):
        return self.tag_map[handle]

    def get_raw_event_data(self, handle):
        return self.event_map[handle]

    def add_person(self, person, trans, set_gid=True):
        if not person.handle:
            person.handle = create_id()
        if (not person.gramps_id) and set_gid:
            person.gramps_id = self.find_next_person_gramps_id()
        if (not person.gramps_id):
            # give it a random value for the moment:
            person.gramps_id = str(random.random())
        self.commit_person(person, trans)
        return person.handle

    def add_family(self, family, trans, set_gid=True):
        if not family.handle:
            family.handle = create_id()
        if (not family.gramps_id) and set_gid:
            family.gramps_id = self.find_next_family_gramps_id()
        if (not family.gramps_id):
            # give it a random value for the moment:
            family.gramps_id = str(random.random())
        self.commit_family(family, trans)
        return family.handle

    def add_citation(self, citation, trans, set_gid=True):
        if not citation.handle:
            citation.handle = create_id()
        if (not citation.gramps_id) and set_gid:
            citation.gramps_id = self.find_next_citation_gramps_id()
        if (not citation.gramps_id):
            # give it a random value for the moment:
            citation.gramps_id = str(random.random())
        self.commit_citation(citation, trans)
        return citation.handle

    def add_source(self, source, trans, set_gid=True):
        if not source.handle:
            source.handle = create_id()
        if (not source.gramps_id) and set_gid:
            source.gramps_id = self.find_next_source_gramps_id()
        if (not source.gramps_id):
            # give it a random value for the moment:
            source.gramps_id = str(random.random())
        self.commit_source(source, trans)
        return source.handle

    def add_repository(self, repository, trans, set_gid=True):
        if not repository.handle:
            repository.handle = create_id()
        if (not repository.gramps_id) and set_gid:
            repository.gramps_id = self.find_next_repository_gramps_id()
        if (not repository.gramps_id):
            # give it a random value for the moment:
            repository.gramps_id = str(random.random())
        self.commit_repository(repository, trans)
        return repository.handle

    def add_note(self, note, trans, set_gid=True):
        if not note.handle:
            note.handle = create_id()
        if (not note.gramps_id) and set_gid:
            note.gramps_id = self.find_next_note_gramps_id()
        if (not note.gramps_id):
            # give it a random value for the moment:
            note.gramps_id = str(random.random())
        self.commit_note(note, trans)
        return note.handle

    def add_place(self, place, trans, set_gid=True):
        if not place.handle:
            place.handle = create_id()
        if (not place.gramps_id) and set_gid:
            place.gramps_id = self.find_next_place_gramps_id()
        if (not place.gramps_id):
            # give it a random value for the moment:
            place.gramps_id = str(random.random())
        self.commit_place(place, trans)
        return place.handle

    def add_event(self, event, trans, set_gid=True):
        if not event.handle:
            event.handle = create_id()
        if (not event.gramps_id) and set_gid:
            event.gramps_id = self.find_next_event_gramps_id()
        if (not event.gramps_id):
            # give it a random value for the moment:
            event.gramps_id = str(random.random())
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
        if (not obj.gramps_id) and set_gid:
            obj.gramps_id = self.find_next_object_gramps_id()
        if (not obj.gramps_id):
            # give it a random value for the moment:
            obj.gramps_id = str(random.random())
        self.commit_media_object(obj, transaction)
        return obj.handle

    def add_to_surname_list(self, person, batch_transaction):
        """
        Add surname to surname list
        """
        if batch_transaction:
            return
        name = None
        primary_name = person.get_primary_name()
        if primary_name:
            surname_list = primary_name.get_surname_list()
            if len(surname_list) > 0:
                name = surname_list[0].surname
        if name is None:
            return
        i = bisect.bisect(self.surname_list, name)
        if 0 < i <= len(self.surname_list):
            if self.surname_list[i-1] != name:
                self.surname_list.insert(i, name)
        else:
            self.surname_list.insert(i, name)

    def remove_from_surname_list(self, person):
        """
        Check whether there are persons with the same surname left in
        the database.

        If not then we need to remove the name from the list.
        The function must be overridden in the derived class.
        """
        name = None
        primary_name = person.get_primary_name()
        if primary_name:
            surname_list = primary_name.get_surname_list()
            if len(surname_list) > 0:
                name = surname_list[0].surname
        if name is None:
            return
        if name in self.surname_list:
            self.surname_list.remove(name)

    def get_gramps_ids(self, obj_key):
        key2table = {
            PERSON_KEY:     self.person_id_map,
            FAMILY_KEY:     self.family_id_map,
            CITATION_KEY:   self.citation_id_map,
            SOURCE_KEY:     self.source_id_map,
            EVENT_KEY:      self.event_id_map,
            MEDIA_KEY:      self.media_id_map,
            PLACE_KEY:      self.place_id_map,
            REPOSITORY_KEY: self.repository_id_map,
            NOTE_KEY:       self.note_id_map,
            }
        return list(key2table[obj_key].keys())

    def set_researcher(self, owner):
        self.owner.set_from(owner)

    def get_researcher(self):
        return self.owner

    def request_rebuild(self):
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

    def get_transaction_class(self):
        """
        Get the transaction class associated with this database backend.
        """
        return DbGenericTxn

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

    def get_from_name_and_gramps_id(self, table_name, gramps_id):
        """
        Returns a gen.lib object (or None) given table_name and
        Gramps ID.

        Examples:

        >>> self.get_from_name_and_gramps_id("Person", "I00002")
        >>> self.get_from_name_and_gramps_id("Family", "F056")
        >>> self.get_from_name_and_gramps_id("Media", "M00012")
        """
        if table_name in self._tables:
            return self._tables[table_name]["gramps_id_func"](gramps_id)
        return None

    def remove_source(self, handle, transaction):
        """
        Remove the Source specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, self.source_map,
                         self.source_id_map, SOURCE_KEY)

    def remove_citation(self, handle, transaction):
        """
        Remove the Citation specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, self.citation_map,
                         self.citation_id_map, CITATION_KEY)

    def remove_event(self, handle, transaction):
        """
        Remove the Event specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, self.event_map,
                         self.event_id_map, EVENT_KEY)

    def remove_object(self, handle, transaction):
        """
        Remove the MediaObjectPerson specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, self.media_map,
                         self.media_id_map, MEDIA_KEY)

    def remove_place(self, handle, transaction):
        """
        Remove the Place specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, self.place_map,
                         self.place_id_map, PLACE_KEY)

    def remove_family(self, handle, transaction):
        """
        Remove the Family specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, self.family_map,
                         self.family_id_map, FAMILY_KEY)

    def remove_repository(self, handle, transaction):
        """
        Remove the Repository specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, self.repository_map,
                         self.repository_id_map, REPOSITORY_KEY)

    def remove_note(self, handle, transaction):
        """
        Remove the Note specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, self.note_map,
                         self.note_id_map, NOTE_KEY)

    def remove_tag(self, handle, transaction):
        """
        Remove the Tag specified by the database handle from the
        database, preserving the change in the passed transaction.
        """
        self._do_remove(handle, transaction, self.tag_map,
                         None, TAG_KEY)

    def is_empty(self):
        """
        Return true if there are no [primary] records in the database
        """
        for table in self._tables:
            if len(self._tables[table]["handles_func"]()) > 0:
                return False
        return True

    def close(self):
        if self._directory:
            # This is just a dummy file to indicate last modified time of the
            # database for gramps.cli.clidbman:
            filename = os.path.join(self._directory, "meta_data.db")
            touch(filename)
            # Save metadata
            self.set_metadata('name_formats', self.name_formats)
            self.set_metadata('researcher', self.owner)

            # Bookmarks
            self.set_metadata('bookmarks', self.bookmarks.get())
            self.set_metadata('family_bookmarks', self.family_bookmarks.get())
            self.set_metadata('event_bookmarks', self.event_bookmarks.get())
            self.set_metadata('source_bookmarks', self.source_bookmarks.get())
            self.set_metadata('citation_bookmarks', self.citation_bookmarks.get())
            self.set_metadata('repo_bookmarks', self.repo_bookmarks.get())
            self.set_metadata('media_bookmarks', self.media_bookmarks.get())
            self.set_metadata('place_bookmarks', self.place_bookmarks.get())
            self.set_metadata('note_bookmarks', self.note_bookmarks.get())

            # Custom type values, sets
            self.set_metadata('event_names', self.event_names)
            self.set_metadata('fattr_names', self.family_attributes)
            self.set_metadata('pattr_names', self.individual_attributes)
            self.set_metadata('sattr_names', self.source_attributes)
            self.set_metadata('marker_names', self.marker_names)
            self.set_metadata('child_refs', self.child_ref_types)
            self.set_metadata('family_rels', self.family_rel_types)
            self.set_metadata('event_roles', self.event_role_names)
            self.set_metadata('name_types', self.name_types)
            self.set_metadata('origin_types', self.origin_types)
            self.set_metadata('repo_types', self.repository_types)
            self.set_metadata('note_types', self.note_types)
            self.set_metadata('sm_types', self.source_media_types)
            self.set_metadata('url_types', self.url_types)
            self.set_metadata('mattr_names', self.media_attributes)
            self.set_metadata('eattr_names', self.event_attributes)
            self.set_metadata('place_types', self.place_types)

            # Save misc items:
            self.save_surname_list()
            self.save_gender_stats(self.genderStats)

            # Indexes:
            self.set_metadata('cmap_index', self.cmap_index)
            self.set_metadata('smap_index', self.smap_index)
            self.set_metadata('emap_index', self.emap_index)
            self.set_metadata('pmap_index', self.pmap_index)
            self.set_metadata('fmap_index', self.fmap_index)
            self.set_metadata('lmap_index', self.lmap_index)
            self.set_metadata('omap_index', self.omap_index)
            self.set_metadata('rmap_index', self.rmap_index)
            self.set_metadata('nmap_index', self.nmap_index)

            self.close_backend()

    def get_bookmarks(self):
        return self.bookmarks

    def get_citation_bookmarks(self):
        return self.citation_bookmarks

    def get_default_handle(self):
        return self.get_metadata("default-person-handle", None)

    def get_surname_list(self):
        """
        Return the list of locale-sorted surnames contained in the database.
        """
        return self.surname_list

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

    def get_event_bookmarks(self):
        return self.event_bookmarks

    def get_family_bookmarks(self):
        return self.family_bookmarks

    def get_media_bookmarks(self):
        return self.media_bookmarks

    def get_note_bookmarks(self):
        return self.note_bookmarks

    def get_place_bookmarks(self):
        return self.place_bookmarks

    def get_repo_bookmarks(self):
        return self.repo_bookmarks

    def get_save_path(self):
        return self._directory

    def get_source_bookmarks(self):
        return self.source_bookmarks

    def is_open(self):
        return self._directory is not None

    def iter_citations(self):
        return (Citation.create(data[1]) for data in self.get_citation_cursor())

    def iter_events(self):
        return (Event.create(data[1]) for data in self.get_event_cursor())

    def iter_media_objects(self):
        return (MediaObject.create(data[1]) for data in self.get_media_cursor())

    def iter_notes(self):
        return (Note.create(data[1]) for data in self.get_note_cursor())

    def iter_places(self):
        return (Place.create(data[1]) for data in self.get_place_cursor())

    def iter_repositories(self):
        return (Repository.create(data[1]) for data in self.get_repository_cursor())

    def iter_sources(self):
        return (Source.create(data[1]) for data in self.get_source_cursor())

    def iter_tags(self):
        return (Tag.create(data[1]) for data in self.get_tag_cursor())


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

    def set_save_path(self, directory):
        self._directory = directory
        if directory:
            self.full_name = os.path.abspath(self._directory)
            self.path = self.full_name
            self.brief_name = os.path.basename(self._directory)
        else:
            self.full_name = None
            self.path = None
            self.brief_name = None

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

    def get_summary(self):
        """
        Returns dictionary of summary item.
        Should include, if possible:

        _("Number of people")
        _("Version")
        _("Schema version")
        """
        return {
            _("Number of people"): self.get_number_of_people(),
            _("Number of families"): self.get_number_of_families(),
            _("Number of sources"): self.get_number_of_sources(),
            _("Number of citations"): self.get_number_of_citations(),
            _("Number of events"): self.get_number_of_events(),
            _("Number of media"): self.get_number_of_media_objects(),
            _("Number of places"): self.get_number_of_places(),
            _("Number of repositories"): self.get_number_of_repositories(),
            _("Number of notes"): self.get_number_of_notes(),
            _("Number of tags"): self.get_number_of_tags(),
        }

    def get_dbname(self):
        """
        In DbGeneric, the database is in a text file at the path
        """
        filepath = os.path.join(self._directory, "name.txt")
        try:
            name_file = open(filepath, "r")
            name = name_file.readline().strip()
            name_file.close()
        except (OSError, IOError) as msg:
            LOG.error(str(msg))
            name = None
        return name

    def _order_by_person_key(self, person):
        """
        All non pa/matronymic surnames are used in indexing.
        pa/matronymic not as they change for every generation!
        returns a byte string
        """
        if person.primary_name and person.primary_name.surname_list:
            order_by = " ".join([x.surname for x in person.primary_name.surname_list if not
                                 (int(x.origintype) in [NameOriginType.PATRONYMIC,
                                                        NameOriginType.MATRONYMIC]) ])
        else:
            order_by = ""
        return glocale.sort_key(order_by)

    def _order_by_place_key(self, place):
        return glocale.sort_key(str(int(place.place_type)) + ", " + place.name.value)

    def _order_by_source_key(self, source):
        return glocale.sort_key(source.title)

    def _order_by_citation_key(self, citation):
        return glocale.sort_key(citation.page)

    def _order_by_media_key(self, media):
        return glocale.sort_key(media.desc)

    def _order_by_tag_key(self, key):
        return glocale.sort_key(key)

    def backup(self):
        """
        If you wish to support an optional backup routine, put it here.
        """
        from gramps.plugins.export.exportxml import XmlWriter
        from gramps.cli.user import User
        writer = XmlWriter(self, User(), strip_photos=0, compress=1)
        filename = os.path.join(self._directory, "data.gramps")
        writer.write(filename)

    def get_undodb(self):
        return self.undodb

    def undo(self, update_history=True):
        return self.undodb.undo(update_history)

    def redo(self, update_history=True):
        return self.undodb.redo(update_history)

    def get_dbid(self):
        """
        We use the file directory name as the unique ID for
        this database on this computer.
        """
        return self.brief_name

    def get_person_data(self, person):
        """
        Given a Person, return primary_name.first_name, surname and gender.
        """
        given_name = ""
        surname = ""
        gender_type = Person.UNKNOWN
        if person:
            primary_name = person.get_primary_name()
            if primary_name:
                given_name = primary_name.get_first_name()
                surname_list = primary_name.get_surname_list()
                if len(surname_list) > 0:
                    surname_obj = surname_list[0]
                    if surname_obj:
                        surname = surname_obj.surname
            gender_type = person.gender
        return (given_name, surname, gender_type)

    def set_default_person_handle(self, handle):
        self.set_metadata("default-person-handle", handle)
        self.emit('home-person-changed')
