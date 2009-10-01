#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2008  Donald N. Allingham
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

# $Id: write.py 12672 2009-06-16 15:49:17Z gbritton $

"""
Provide the Berkeley DB (DBDir) database backend for GRAMPS.
This is used since GRAMPS version 3.0
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from __future__ import with_statement
import cPickle as pickle
import os
import sys
import time
import locale
import bisect
from types import InstanceType
from functools import wraps

from gettext import gettext as _
from bsddb import dbshelve, db
import logging
from sys import maxint

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.lib import (GenderStats, Person, Family, Event, Place, Source, 
                     MediaObject, Repository, Note)
from gen.db import (GrampsDbRead, BSDDBTxn, GrampsDbTxn, GrampsCursor,
                    FileVersionError, FileVersionDeclineToUpgrade,
                    GrampsDbUndoBSDDB as GrampsDbUndo)
from gen.db.dbconst import *
from gen.utils.callback import Callback
from BasicUtils import UpdateCallback
import Errors
from QuestionDialog import QuestionDialog2

_LOG = logging.getLogger(DBLOGNAME)
_MINVERSION = 9
_DBVERSION = 14

IDTRANS     = "person_id"
FIDTRANS    = "family_id"
PIDTRANS    = "place_id"
OIDTRANS    = "media_id"
EIDTRANS    = "event_id"
RIDTRANS    = "repo_id"
NIDTRANS    = "note_id"
SIDTRANS    = "source_id"
SURNAMES    = "surnames"
NAME_GROUP  = "name_group"
META        = "meta_data"

FAMILY_TBL  = "family"
PLACES_TBL  = "place"
SOURCES_TBL = "source"
MEDIA_TBL   = "media"
EVENTS_TBL  = "event"
PERSON_TBL  = "person"
REPO_TBL    = "repo"
NOTE_TBL    = "note"

REF_MAP     = "reference_map"
REF_PRI     = "primary_map"
REF_REF     = "referenced_map"

DBERRS      = (db.DBRunRecoveryError, db.DBAccessError, 
               db.DBPageNotFoundError, db.DBInvalidArgError)

# The following two dictionaries provide fast translation
# between the primary class names and the keys used to reference
# these classes in the database tables. Beware that changing
# these maps or modifying the values of the keys will break
# existing databases.

CLASS_TO_KEY_MAP = {Person.__name__: PERSON_KEY, 
                    Family.__name__: FAMILY_KEY, 
                    Source.__name__: SOURCE_KEY, 
                    Event.__name__: EVENT_KEY, 
                    MediaObject.__name__: MEDIA_KEY, 
                    Place.__name__: PLACE_KEY, 
                    Repository.__name__:REPOSITORY_KEY,
                    Note.__name__: NOTE_KEY}

KEY_TO_CLASS_MAP = {PERSON_KEY: Person.__name__, 
                    FAMILY_KEY: Family.__name__, 
                    SOURCE_KEY: Source.__name__, 
                    EVENT_KEY: Event.__name__, 
                    MEDIA_KEY: MediaObject.__name__, 
                    PLACE_KEY: Place.__name__, 
                    REPOSITORY_KEY: Repository.__name__,
                    NOTE_KEY: Note.__name__}

#-------------------------------------------------------------------------
#
# Helper functions
#
#-------------------------------------------------------------------------                    

def find_surname(key, data):
    return str(data[3][5])

def find_idmap(key, data):
    return str(data[1])

# Secondary database key lookups for reference_map table
# reference_map data values are of the form:
#   ((primary_object_class_name, primary_object_handle),
#    (referenced_object_class_name, referenced_object_handle))

def find_primary_handle(key, data):
    return str((data)[0][1])

def find_referenced_handle(key, data):
    return str((data)[1][1])

#-------------------------------------------------------------------------
#
# GrampsWriteCursor
#
#-------------------------------------------------------------------------
class GrampsWriteCursor(GrampsCursor):

    def __init__(self, source, txn=None, **kwargs):
        GrampsCursor.__init__(self, txn=txn, **kwargs)
        self.cursor = source.db.cursor(txn)
        self.source = source
        
#-------------------------------------------------------------------------
#
# GrampsDBDirAssocCursor
#
#-------------------------------------------------------------------------
class GrampsDBDirAssocCursor(GrampsCursor):

    def __init__(self, source, txn=None, **kwargs):
        GrampsCursor.__init__(self, txn=txn, **kwargs)
        self.cursor = source.cursor(txn)
        self.source = source
        
#-------------------------------------------------------------------------
#
# GrampsDBDir
#
#-------------------------------------------------------------------------
class GrampsDBDir(GrampsDbRead, Callback, UpdateCallback):
    """
    GRAMPS database write access object. 
    """

    # Set up dictionary for callback signal handler
    # ---------------------------------------------
    # 1. Signals for primary objects
    __signals__ = dict((obj+'-'+op, signal)
            for obj in
                ['person', 'family', 'event', 'place',
                 'source', 'media', 'note', 'repository']
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

    def __init__(self):
        """Create a new GrampsDB."""
        
        self.txn = None
        GrampsDbRead.__init__(self)
        Callback.__init__(self)
        self.secondary_connected = False
        self.has_changed = False

    def catch_db_error(func):
        """
        Decorator function for catching database errors.  If *func* throws
        one of the exceptions in DBERRS, the error is logged and a DbError
        exception is raised.
        """
        @wraps(func)
        def try_(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except DBERRS, msg:
                self.__log_error()
                raise Errors.DbError(msg)
        return try_

    def __open_db(self, file_name, table_name, dbtype=db.DB_HASH, flags=0):
        dbmap = db.DB(self.env)
        dbmap.set_pagesize(DBPAGE)
        dbmap.set_flags(flags)

        fname = os.path.join(file_name, table_name + DBEXT)

        if self.readonly:
            dbmap.open(fname, table_name, dbtype, DBFLAGS_R)
        else:
            dbmap.open(fname, table_name, dbtype, DBFLAGS_O, DBMODE)
        return dbmap

    def __open_shelf(self, file_name, table_name, dbtype=db.DB_HASH):
        dbmap = dbshelve.DBShelf(self.env)
        dbmap.db.set_pagesize(DBPAGE)

        fname = os.path.join(file_name, table_name + DBEXT)

        if self.readonly:
            dbmap.open(fname, table_name, dbtype, DBFLAGS_R)
        else:
            dbmap.open(fname, table_name, dbtype, DBFLAGS_O, DBMODE)
        return dbmap

    def __all_handles(self, table):
        return table.keys(self.txn)
    
    def __log_error(self):
        mypath = os.path.join(self.get_save_path(),DBRECOVFN)
        ofile = open(mypath, "w")
        ofile.close()
        try:
            clear_lock_file(self.get_save_path())
        except:
            pass

    _log_error = __log_error

    # Override get_cursor method from the superclass to add udpate
    # capability

    @catch_db_error
    def get_cursor(self, table, txn=None, update=False, commit=False):
        """ Helper function to return a cursor over a table """
        if update and not txn:
            txn = self.env.txn_begin(self.txn)
        return GrampsWriteCursor(table, txn=txn or self.txn,
                                    update=update, commit=commit)

    # cursors for lookups in the reference_map for back reference
    # lookups. The reference_map has three indexes:
    # the main index: a tuple of (primary_handle, referenced_handle)
    # the primary_handle index: the primary_handle
    # the referenced_handle index: the referenced_handle
    # the main index is unique, the others allow duplicate entries.

    @catch_db_error
    def get_reference_map_cursor(self):
        """
        Returns a reference to a cursor over the reference map
        """
        return GrampsDBDirAssocCursor(self.reference_map, self.txn)

    @catch_db_error
    def get_reference_map_primary_cursor(self):
        """
        Returns a reference to a cursor over the reference map primary map
        """
        return GrampsDBDirAssocCursor(self.reference_map_primary_map, 
                                        self.txn)

    @catch_db_error
    def get_reference_map_referenced_cursor(self):
        """
        Returns a reference to a cursor over the reference map referenced map
        """
        return GrampsDBDirAssocCursor(self.reference_map_referenced_map, 
                                        self.txn)

    # These are overriding the GrampsDbRead's methods of saving metadata
    # because we now have txn-capable metadata table

    @catch_db_error
    def set_default_person_handle(self, handle):
        """Set the default Person to the passed instance."""
        if not self.readonly:
            # Start transaction
            with BSDDBTxn(self.env, self.metadata) as txn:
                txn.put('default', str(handle))
            self.emit('home-person-changed')

    @catch_db_error
    def get_default_person(self):
        """Return the default Person of the database."""
        person = self.get_person_from_handle(self.get_default_handle())
        if person:
            return person
        elif (self.metadata) and (not self.readonly):
            # Start transaction
            with BSDDBTxn(self.env, self.metadata) as txn:
                txn.put('default', None)            
        return None

    def set_mediapath(self, path):
        """Set the default media path for database, path should be utf-8."""
        if self.metadata and not self.readonly:
            # Start transaction
            with BSDDBTxn(self.env, self.metadata) as txn:
                txn.put('mediapath', path)            

    def set_column_order(self, col_list, name):
        if self.metadata and not self.readonly: 
            # Start transaction
            with BSDDBTxn(self.env, self.metadata) as txn:
                txn.put(name, col_list)   

    @catch_db_error
    def version_supported(self):
        dbversion = self.metadata.get('version', default=0)
        return ((dbversion <= _DBVERSION) and (dbversion >= _MINVERSION))

    @catch_db_error
    def need_upgrade(self):
        dbversion = self.metadata.get('version', default=0)
        return not self.readonly and dbversion < _DBVERSION

    def __check_readonly(self, name):
        """
        Return True if we don't have read/write access to the database,
        otherwise return False (that is, we DO have read/write access)
        """

        # See if we write to the target directory at all?
        if not os.access(name, os.W_OK):
            return True

        # See if we lack write access to any files in the directory
        for base in [FAMILY_TBL, PLACES_TBL, SOURCES_TBL, MEDIA_TBL, 
                     EVENTS_TBL, PERSON_TBL, REPO_TBL, NOTE_TBL, REF_MAP, META]:
            path = os.path.join(name, base + DBEXT)
            if os.path.isfile(path) and not os.access(path, os.W_OK):
                return True

        # All tests passed.  Inform caller that we are NOT read only
        return False

    @catch_db_error
    def load(self, name, callback, mode=DBMODE_W):

        if self.__check_readonly(name):
            mode = DBMODE_R
        else:
            write_lock_file(name)        

        if self.db_is_open:
            self.close()

        self.readonly = mode == DBMODE_R
        #super(GrampsDbRead, self).load(name, callback, mode)
        if callback:
            callback(12)

        # Save full path and base file name
        self.full_name = os.path.abspath(name)
        self.path = self.full_name
        self.brief_name = os.path.basename(name)

        # Set up database environment
        self.env = db.DBEnv()
        self.env.set_cachesize(0, DBCACHE)

        # These env settings are only needed for Txn environment
        self.env.set_lk_max_locks(DBLOCKS)
        self.env.set_lk_max_objects(DBOBJECTS)
        
        self.set_auto_remove()

        # The DB_PRIVATE flag must go if we ever move to multi-user setup
        env_flags = db.DB_CREATE | db.DB_PRIVATE |\
                    db.DB_INIT_MPOOL | db.DB_INIT_LOCK |\
                    db.DB_INIT_LOG | db.DB_INIT_TXN | db.DB_THREAD

        # As opposed to before, we always try recovery on databases
        env_flags |= db.DB_RECOVER

        # Environment name is now based on the filename
        env_name = name

        self.env.open(env_name, env_flags)
        self.env.txn_checkpoint()

        if callback:
            callback(25)

        # Process metadata
        self.metadata = self.__open_shelf(self.full_name, META)

        # If we cannot work with this DB version,
        # it makes no sense to go further
        if not self.version_supported():
            self.__close_early()

        self.__load_metadata()
        gstats = self.metadata.get('gender_stats', default=None)

        # Ensure version info in metadata
        if not self.readonly:
            # Start transaction
            with BSDDBTxn(self.env, self.metadata) as txn:
                if gstats is None:
                    # New database. Set up the current version.
                    #self.metadata.put('version', _DBVERSION, txn=the_txn)
                    txn.put('version', _DBVERSION)
                elif 'version' not in self.metadata:
                    # Not new database, but the version is missing.
                    # Use 0, but it is likely to fail anyway.
                    txn.put('version', 0)
            
        self.genderStats = GenderStats(gstats)

        # Open main tables in gramps database
        db_maps = [
                    ("family_map",     FAMILY_TBL,  db.DB_HASH),
                    ("place_map",      PLACES_TBL,  db.DB_HASH),
                    ("source_map",     SOURCES_TBL, db.DB_HASH),
                    ("media_map",      MEDIA_TBL,   db.DB_HASH),
                    ("event_map",      EVENTS_TBL,  db.DB_HASH),
                    ("person_map",     PERSON_TBL,  db.DB_HASH),
                    ("repository_map", REPO_TBL,    db.DB_HASH),
                    ("note_map",       NOTE_TBL,    db.DB_HASH),
                    ("reference_map",  REF_MAP,     db.DB_BTREE),
                  ]

        dbflags = DBFLAGS_R if self.readonly else DBFLAGS_O
        for (dbmap, dbname, dbtype) in db_maps:
            _db = self.__open_shelf(self.full_name, dbname, dbtype)
            setattr(self, dbmap, _db)

        if callback:
            callback(37)

        # Open name grouping database
        self.name_group = self.__open_db(self.full_name, NAME_GROUP,
                              db.DB_HASH, db.DB_DUP)

        # Here we take care of any changes in the tables related to new code.
        # If secondary indices change, then they should removed
        # or rebuilt by upgrade as well. In any case, the
        # self.secondary_connected flag should be set accordingly.
        
        if self.need_upgrade():
            if QuestionDialog2(_("Need to upgrade database!"), 
                               _("You cannot open this database "
                                 "without upgrading it.\n"
                                 "If you upgrade then you won't be able "
                                 "to use previous versions of GRAMPS.\n" 
                                 "You might want to make a backup copy "
                                 "first."), 
                               _("Upgrade now"), 
                               _("Cancel")).run():
                self.gramps_upgrade(callback)
            else:
                raise FileVersionDeclineToUpgrade()

        if callback:
            callback(50)

        # Connect secondary indices
        if not self.secondary_connected:
            self.__connect_secondary()

        if callback:
            callback(75)

        # Open undo database
        self.__open_undodb()
        self.db_is_open = True

        if callback:
            callback(87)
        
        self.abort_possible = True
        return 1

    def __open_undodb(self):
        """
        Open the undo database
        """
        if not self.readonly:
            self.undolog = os.path.join(self.full_name, DBUNDOFN)
            self.undodb = GrampsDbUndo(self, self.undolog)
            self.undodb.open()

    def __close_undodb(self):
        if not self.readonly:
            try:
                self.undodb.close()
            except db.DBNoSuchFileError:
                pass                

    @catch_db_error
    def load_from(self, other_database, filename, callback):
        self.load(filename, callback)
        from gen.utils import db_copy
        db_copy(other_database, self, callback)
        return 1

    def __load_metadata(self):
        # name display formats
        self.name_formats = self.metadata.get('name_formats', default=[])
        # upgrade formats if they were saved in the old way
        for format_ix in range(len(self.name_formats)):
            format = self.name_formats[format_ix]
            if len(format) == 3:
                format = format + (True,)
                self.name_formats[format_ix] = format
        
        # database owner
        try:
            owner_data = self.metadata.get('researcher')
            if owner_data:
                self.owner.unserialize(owner_data)
        except ImportError: #handle problems with pre-alpha 3.0
            pass
        
        # bookmarks
        meta = lambda meta: self.metadata.get(meta, default=[])
        
        self.bookmarks.set(meta('bookmarks'))
        self.family_bookmarks.set(meta('family_bookmarks'))
        self.event_bookmarks.set(meta('event_bookmarks'))
        self.source_bookmarks.set(meta('source_bookmarks'))
        self.repo_bookmarks.set(meta('repo_bookmarks'))
        self.media_bookmarks.set(meta('media_bookmarks'))
        self.place_bookmarks.set(meta('place_bookmarks'))
        self.note_bookmarks.set(meta('note_bookmarks'))

        # Custom type values
        self.family_event_names = set(meta('fevent_names'))
        self.individual_event_names = set(meta('pevent_names'))
        self.family_attributes = set(meta('fattr_names'))
        self.individual_attributes = set(meta('pattr_names'))
        self.marker_names = set(meta('marker_names'))
        self.child_ref_types = set(meta('child_refs'))
        self.family_rel_types = set(meta('family_rels'))
        self.event_role_names = set(meta('event_roles'))
        self.name_types = set(meta('name_types'))
        self.repository_types = set(meta('repo_types'))
        self.note_types = set(meta('note_types'))
        self.source_media_types = set(meta('sm_types'))
        self.url_types = set(meta('url_types'))
        self.media_attributes = set(meta('mattr_names'))

        # surname list
        self.surname_list = meta('surname_list')

    def __connect_secondary(self):
        """
        Connect or creates secondary index tables.
        
        It assumes that the tables either exist and are in the right
        format or do not exist (in which case they get created).

        It is the responsibility of upgrade code to either create
        or remove invalid secondary index tables.
        """
        
        # index tables used just for speeding up searches
        self.surnames = self.__open_db(self.full_name, SURNAMES, db.DB_BTREE,
                            db.DB_DUP | db.DB_DUPSORT)

        db_maps = [
            ("id_trans",  IDTRANS,  db.DB_HASH, 0),
            ("fid_trans", FIDTRANS, db.DB_HASH, 0),
            ("eid_trans", EIDTRANS, db.DB_HASH, 0),
            ("pid_trans", PIDTRANS, db.DB_HASH, 0),
            ("sid_trans", SIDTRANS, db.DB_HASH, 0),
            ("oid_trans", OIDTRANS, db.DB_HASH, 0),
            ("rid_trans", RIDTRANS, db.DB_HASH, 0),
            ("nid_trans", NIDTRANS, db.DB_HASH, 0),
            ("reference_map_primary_map",    REF_PRI, db.DB_BTREE, 0),
            ("reference_map_referenced_map", REF_REF, db.DB_BTREE, db.DB_DUPSORT),            
            ]

        for (dbmap, dbname, dbtype, dbflags) in db_maps:
            _db = self.__open_db(self.full_name, dbname, dbtype,
                db.DB_DUP | dbflags)
            setattr(self, dbmap, _db)

        if not self.readonly:

            assoc = [
                (self.person_map, self.surnames,  find_surname),
                (self.person_map, self.id_trans,  find_idmap),
                (self.family_map, self.fid_trans, find_idmap),
                (self.event_map,  self.eid_trans, find_idmap),
                (self.place_map,  self.pid_trans, find_idmap),
                (self.source_map, self.sid_trans, find_idmap),
                (self.media_map,  self.oid_trans, find_idmap),
                (self.repository_map, self.rid_trans, find_idmap),
                (self.note_map,   self.nid_trans, find_idmap),
                (self.reference_map, self.reference_map_primary_map,
                    find_primary_handle),
                (self.reference_map, self.reference_map_referenced_map,
                    find_referenced_handle),
                ]

            flags = DBFLAGS_R if self.readonly else DBFLAGS_O
            for (dbmap, a_map, a_find) in assoc:
                dbmap.associate(a_map, a_find, flags=flags)

        self.secondary_connected = True
        self.smap_index = len(self.source_map)
        self.emap_index = len(self.event_map)
        self.pmap_index = len(self.person_map)
        self.fmap_index = len(self.family_map)
        self.lmap_index = len(self.place_map)
        self.omap_index = len(self.media_map)
        self.rmap_index = len(self.repository_map)
        self.nmap_index = len(self.note_map)

    @catch_db_error
    def rebuild_secondary(self, callback=None):
        if self.readonly:
            return

        table_flags = DBFLAGS_O

        # remove existing secondary indices

        items = [
            ( self.id_trans,  IDTRANS ),
            ( self.surnames,  SURNAMES ),
            ( self.fid_trans, FIDTRANS ),
            ( self.pid_trans, PIDTRANS ),
            ( self.oid_trans, OIDTRANS ),
            ( self.eid_trans, EIDTRANS ),
            ( self.rid_trans, RIDTRANS ),
            ( self.nid_trans, NIDTRANS ),
            ( self.reference_map_primary_map, REF_PRI),
            ( self.reference_map_referenced_map, REF_REF),
            ]

        index = 1
        for (database, name) in items:
            database.close()
            _db = db.DB(self.env)
            try:
                _db.remove(_mkname(self.full_name, name), name)
            except db.DBNoSuchFileError:
                pass
            if callback:
                callback(index)
            index += 1

        if callback:
            callback(11)

        # Set flag saying that we have removed secondary indices
        # and then call the creating routine
        self.secondary_connected = False
        self.__connect_secondary()
        if callback:
            callback(12)

    @catch_db_error
    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        
        Returns an interator over a list of (class_name, handle) tuples.

        :param handle: handle of the object to search for.
        :type handle: database handle
        :param include_classes: list of class names to include in the results.
            Default: None means include all classes.
        :type include_classes: list of class names

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use::

            result_list = list(find_backlink_handles(handle))
        """

        # Use the secondary index to locate all the reference_map entries
        # that include a reference to the object we are looking for.
        referenced_cur = self.get_reference_map_referenced_cursor()

        try:
            ret = referenced_cur.set(handle)
        except:
            ret = None

        while (ret is not None):
            (key, data) = ret
            
            # data values are of the form:
            #   ((primary_object_class_name, primary_object_handle),
            #    (referenced_object_class_name, referenced_object_handle))
            # so we need the first tuple to give us the type to compare

            ### FIXME: this is a dirty hack that works without no
            ### sensible explanation. For some reason, for a readonly
            ### database, secondary index returns a primary table key
            ### corresponding to the data, not the data.
            if self.readonly:
                data = self.reference_map.get(data)
            else:
                data = pickle.loads(data)

            key, handle = data[0][:2]
            name = KEY_TO_CLASS_MAP[key]
            assert name == KEY_TO_CLASS_MAP[data[0][0]]
            assert handle == data[0][1]                
            if (include_classes is None or
                name in include_classes):
                    yield (name, handle)
                
            ret = referenced_cur.next_dup()

        referenced_cur.close()

    def delete_primary_from_reference_map(self, handle, transaction, txn=None):
        """
        Remove all references to the primary object from the reference_map.
        """
        primary_cur = self.get_reference_map_primary_cursor()

        try:
            ret = primary_cur.set(handle)
        except:
            ret = None
        
        remove_list = set()
        while (ret is not None):
            (key, data) = ret
            
            # data values are of the form:
            #   ((primary_object_class_name, primary_object_handle),
            #    (referenced_object_class_name, referenced_object_handle))
            
            # so we need the second tuple give us a reference that we can
            # combine with the primary_handle to get the main key.

            main_key = (handle, pickle.loads(data)[1][1])
            
            # The trick is not to remove while inside the cursor,
            # but collect them all and remove after the cursor is closed
            remove_list.add(main_key)

            ret = primary_cur.next_dup()

        primary_cur.close()

        # Now that the cursor is closed, we can remove things
        for main_key in remove_list:
            self.__remove_reference(main_key, transaction, txn)
        
    def update_reference_map(self, obj, transaction, txn=None):
        """
        If txn is given, then changes are written right away using txn.
        """
        
        # Add references to the reference_map for all primary object referenced
        # from the primary object 'obj' or any of its secondary objects.
        handle = obj.handle
        update = self.reference_map_primary_map.has_key(str(handle))

        if update:
            # First thing to do is get hold of all rows in the reference_map
            # table that hold a reference from this primary obj. This means
            # finding all the rows that have this handle somewhere in the
            # list of (class_name, handle) pairs.
            # The primary_map sec index allows us to look this up quickly.

            existing_references = set()

            primary_cur = self.get_reference_map_primary_cursor()

            try:
                ret = primary_cur.set(handle)
            except:
                ret = None

            while (ret is not None):
                (key, data) = ret

                # data values are of the form:
                #   ((primary_object_class_name, primary_object_handle),
                #    (referenced_object_class_name, referenced_object_handle))
                # so we need the second tuple give us a reference that we can
                # compare with what is returned from
                # get_referenced_handles_recursively

                # secondary DBs are not DBShelf's, so we need to do pickling
                # and unpicking ourselves here
                existing_reference = pickle.loads(data)[1]
                existing_references.add(
                                    (KEY_TO_CLASS_MAP[existing_reference[0]],
                                     existing_reference[1]))
                ret = primary_cur.next_dup()

            primary_cur.close()

            # Once we have the list of rows that already have a reference
            # we need to compare it with the list of objects that are
            # still references from the primary object.

            current_references = set(obj.get_referenced_handles_recursively())

            no_longer_required_references = existing_references.difference(
                                                            current_references)

            new_references = current_references.difference(existing_references)

        else:
            # No existing refs are found:
            #    all we have is new, nothing to remove
            no_longer_required_references = set()
            new_references = set(obj.get_referenced_handles_recursively())
            
        # handle addition of new references
        for (ref_class_name, ref_handle) in new_references:
            data = ((CLASS_TO_KEY_MAP[obj.__class__.__name__], handle),
                    (CLASS_TO_KEY_MAP[ref_class_name], ref_handle),)
            self.__add_reference((handle, ref_handle), data, transaction, txn)

        # handle deletion of old references
        for (ref_class_name, ref_handle) in no_longer_required_references:
            try:
                self.__remove_reference((handle, ref_handle), transaction, txn)
            except:
                # ignore missing old reference
                pass

    def __remove_reference(self, key, transaction, txn=None):
        """
        Remove the reference specified by the key, preserving the change in 
        the passed transaction.
        """
        if not self.readonly:
            if transaction.batch:
                self.reference_map.delete(str(key), txn=txn)
            else:
                old_data = self.reference_map.get(str(key), txn=self.txn)
                transaction.add(REFERENCE_KEY, TXNDEL, str(key), old_data, None)
                #transaction.reference_del.append(str(key))

    def __add_reference(self, key, data, transaction, txn=None):
        """
        Add the reference specified by the key and the data, preserving the 
        change in the passed transaction.
        """

        if self.readonly or not key:
            return
        
        if transaction.batch:
            self.reference_map.put(str(key), data, txn=txn)
        else:
            transaction.add(REFERENCE_KEY, TXNADD, str(key), None, data)
            #transaction.reference_add.append((str(key), data))

    @catch_db_error
    def reindex_reference_map(self, callback):
        """
        Reindex all primary records in the database.
        
        This will be a slow process for large databases.
        """

        # First, remove the reference map and related tables

        db_maps = [
                    ("reference_map_referenced_map", REF_REF),
                    ("reference_map_primary_map", REF_PRI),
                    ("reference_map", REF_MAP),
                  ]

        for index, (dbmap, dbname) in enumerate(db_maps):
            getattr(self, dbmap).close()
            _db = db.DB(self.env)
            try:
                _db.remove(_mkname(self.full_name, dbname), dbname)
            except db.DBNoSuchFileError:
                pass
            callback(index+1)

        # Open reference_map and primary map
        self.reference_map  = self.__open_shelf(self.full_name, REF_MAP, 
                                  dbtype=db.DB_BTREE)
        
        self.reference_map_primary_map = self.__open_db(self.full_name,
                                            REF_PRI, db.DB_BTREE, db.DB_DUP)

        self.reference_map.associate(self.reference_map_primary_map,
                                     find_primary_handle, DBFLAGS_O)

        # Make a tuple of the functions and classes that we need for
        # each of the primary object tables.

        transaction = self.transaction_begin(batch=True, no_magic=True)
        callback(4)

        primary_table = (
                         (self.get_person_cursor, Person),
                         (self.get_family_cursor, Family),
                         (self.get_event_cursor, Event),
                         (self.get_place_cursor, Place),
                         (self.get_source_cursor, Source),
                         (self.get_media_cursor, MediaObject),
                         (self.get_repository_cursor, Repository),
                         (self.get_note_cursor, Note),
                         )
                         
        # Now we use the functions and classes defined above
        # to loop through each of the primary object tables.
        
        for cursor_func, class_func in primary_table:
            with cursor_func() as cursor:
                for found_handle, val in cursor:
                    obj = class_func()
                    obj.unserialize(val)
                    with BSDDBTxn(self.env) as txn:
                        self.update_reference_map(obj, transaction, txn.txn)

        callback(5)
        self.transaction_commit(transaction, _("Rebuild reference map"))

        self.reference_map_referenced_map = self.__open_db(self.full_name,
            REF_REF, db.DB_BTREE, db.DB_DUP|db.DB_DUPSORT)

        flags = DBFLAGS_R if self.readonly else DBFLAGS_O
        self.reference_map.associate(self.reference_map_referenced_map,
                                     find_referenced_handle, flags=flags)
        callback(6)

    def __close_metadata(self):
        if not self.readonly:
            # Start transaction
            with BSDDBTxn(self.env, self.metadata) as txn:

            # name display formats
                txn.put('name_formats', self.name_formats)
                
                # database owner
                owner_data = self.owner.serialize()
                txn.put('researcher', owner_data)

                # bookmarks
                txn.put('bookmarks', self.bookmarks.get())
                txn.put('family_bookmarks', self.family_bookmarks.get())
                txn.put('event_bookmarks', self.event_bookmarks.get())
                txn.put('source_bookmarks', self.source_bookmarks.get())
                txn.put('place_bookmarks', self.place_bookmarks.get())
                txn.put('repo_bookmarks', self.repo_bookmarks.get())
                txn.put('media_bookmarks', self.media_bookmarks.get())
                txn.put('note_bookmarks', self.note_bookmarks.get())

                # gender stats
                txn.put('gender_stats', self.genderStats.save_stats())

                # Custom type values
                txn.put('fevent_names', list(self.family_event_names))
                txn.put('pevent_names', list(self.individual_event_names))
                txn.put('fattr_names', list(self.family_attributes))
                txn.put('pattr_names', list(self.individual_attributes))
                txn.put('marker_names', list(self.marker_names))
                txn.put('child_refs', list(self.child_ref_types))
                txn.put('family_rels', list(self.family_rel_types))
                txn.put('event_roles', list(self.event_role_names))
                txn.put('name_types', list(self.name_types))
                txn.put('repo_types', list(self.repository_types))
                txn.put('note_types', list(self.note_types))
                txn.put('sm_types', list(self.source_media_types))
                txn.put('url_types', list(self.url_types))
                txn.put('mattr_names', list(self.media_attributes))

                # name display formats
                txn.put('surname_list', self.surname_list)

        self.metadata.close()

    def __close_early(self):
        """
        Bail out if the incompatible version is discovered:
        * close cleanly to not damage data/env
        * raise exception
        """
        self.metadata.close()
        self.env.close()
        self.metadata   = None
        self.env        = None
        self.db_is_open = False
        raise FileVersionError(
            _("The database version is not supported by this "
              "version of GRAMPS.\nPlease upgrade to the "
              "corresponding version or use XML for porting "
              "data between different database versions."))
    
    @catch_db_error
    def close(self):
        if not self.db_is_open:
            return

        self.env.txn_checkpoint()

        self.__close_metadata()
        self.name_group.close()
        self.surnames.close()
        self.id_trans.close()
        self.fid_trans.close()
        self.eid_trans.close()
        self.rid_trans.close()
        self.nid_trans.close()
        self.oid_trans.close()
        self.sid_trans.close()
        self.pid_trans.close()
        self.reference_map_primary_map.close()
        self.reference_map_referenced_map.close()
        self.reference_map.close()
        self.secondary_connected = False

        # primary databases must be closed after secondary indexes, or
        # we run into problems with any active cursors.
        self.person_map.close()
        self.family_map.close()
        self.repository_map.close()
        self.note_map.close()
        self.place_map.close()
        self.source_map.close()
        self.media_map.close()
        self.event_map.close()
        self.env.close()
        self.__close_undodb()

        self.person_map     = None
        self.family_map     = None
        self.repository_map = None
        self.note_map       = None
        self.place_map      = None
        self.source_map     = None
        self.media_map      = None
        self.event_map      = None
        self.surnames       = None
        self.name_group     = None
        self.env            = None
        self.metadata       = None
        self.db_is_open     = False

        try:
            clear_lock_file(self.get_save_path())
        except IOError:
            pass

    def create_id(self):
        return "%08x%08x" % ( int(time.time()*10000), 
                              self.rand.randint(0, maxint))

    def __add_object(self, obj, transaction, find_next_func, commit_func):
        if find_next_func and not obj.gramps_id:
            obj.gramps_id = find_next_func()
        if not obj.handle:
            obj.handle = self.create_id()
        commit_func(obj, transaction)
        return obj.handle

    def add_person(self, person, transaction, set_gid=True):
        """
        Add a Person to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        handle = self.__add_object(person, transaction, 
                    self.find_next_person_gramps_id if set_gid else None, 
                    self.commit_person)
        self.genderStats.count_person(person)
        return handle

    def add_family(self, family, transaction, set_gid=True):
        """
        Add a Family to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(family, transaction, 
                    self.find_next_family_gramps_id if set_gid else None, 
                    self.commit_family)

    def add_source(self, source, transaction, set_gid=True):
        """
        Add a Source to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(source, transaction, 
                    self.find_next_source_gramps_id if set_gid else None, 
                    self.commit_source)

    def add_event(self, event, transaction, set_gid=True):
        """
        Add an Event to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(event, transaction, 
                    self.find_next_event_gramps_id if set_gid else None,
                    self.commit_event)

    def add_person_event(self, event, transaction):
        """
        Add an Event to the database, assigning internal IDs if they have
        not already been defined.
        """
        if event.type.is_custom():
            self.individual_event_names.add(str(event.type))
        return self.add_event(event, transaction)

    def add_family_event(self, event, transaction):
        """
        Add an Event to the database, assigning internal IDs if they have
        not already been defined.
        """
        if event.type.is_custom():
            self.family_event_names.add(str(event.type))
        return self.add_event(event, transaction)

    def add_place(self, place, transaction, set_gid=True):
        """
        Add a Place to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(place, transaction, 
                    self.find_next_place_gramps_id if set_gid else None,
                    self.commit_place)

    def add_object(self, obj, transaction, set_gid=True):
        """
        Add a MediaObject to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(obj, transaction, 
                    self.find_next_object_gramps_id if set_gid else None,
                    self.commit_media_object)

    def add_repository(self, obj, transaction, set_gid=True):
        """
        Add a Repository to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(obj, transaction, 
                    self.find_next_repository_gramps_id if set_gid else None,
                    self.commit_repository)

    def add_note(self, obj, transaction, set_gid=True):
        """
        Add a Note to the database, assigning internal IDs if they have
        not already been defined.
        
        If not set_gid, then gramps_id is not set.
        """
        return self.__add_object(obj, transaction, 
                    self.find_next_note_gramps_id if set_gid else None,
                    self.commit_note)

    def __do_remove(self, handle, transaction, data_map, key):
        if self.readonly or not handle:
            return

        handle = str(handle)
        if transaction.batch:
            with BSDDBTxn(self.env, data_map) as txn:
                self.delete_primary_from_reference_map(handle, transaction,
                                                        txn=txn.txn)
                txn.delete(handle)
        else:
            self.delete_primary_from_reference_map(handle, transaction)
            old_data = data_map.get(handle, txn=self.txn)
            transaction.add(key, TXNDEL, handle, old_data, None)
            #del_list.append(handle)

    def remove_person(self, handle, transaction):
        """
        Remove the Person specified by the database handle from the database, 
        preserving the change in the passed transaction. 
        """

        if self.readonly or not handle:
            return
        self.delete_primary_from_reference_map(handle, transaction)
        person = self.get_person_from_handle(handle)
        self.genderStats.uncount_person (person)
        self.remove_from_surname_list(person)
        if transaction.batch:
            with BSDDBTxn(self.env, self.person_map) as txn:            
                txn.delete(handle)
        else:
            transaction.add(PERSON_KEY, TXNDEL, handle, person.serialize(), None)
            #transaction.person_del.append(str(handle))            

    def remove_source(self, handle, transaction):
        """
        Remove the Source specified by the database handle from the
        database, preserving the change in the passed transaction. 
        """
        self.__do_remove(handle, transaction, self.source_map, 
                              SOURCE_KEY)

    def remove_event(self, handle, transaction):
        """
        Remove the Event specified by the database handle from the
        database, preserving the change in the passed transaction. 
        """
        self.__do_remove(handle, transaction, self.event_map, 
                              EVENT_KEY)

    def remove_object(self, handle, transaction):
        """
        Remove the MediaObjectPerson specified by the database handle from the
        database, preserving the change in the passed transaction. 
        """
        self.__do_remove(handle, transaction, self.media_map, 
                              MEDIA_KEY)

    def remove_place(self, handle, transaction):
        """
        Remove the Place specified by the database handle from the
        database, preserving the change in the passed transaction. 
        """
        self.__do_remove(handle, transaction, self.place_map, 
                              PLACE_KEY)

    def remove_family(self, handle, transaction):
        """
        Remove the Family specified by the database handle from the
        database, preserving the change in the passed transaction. 
        """
        self.__do_remove(handle, transaction, self.family_map, 
                              FAMILY_KEY)

    def remove_repository(self, handle, transaction):
        """
        Remove the Repository specified by the database handle from the
        database, preserving the change in the passed transaction. 
        """
        self.__do_remove(handle, transaction, self.repository_map, 
                              REPOSITORY_KEY)

    def remove_note(self, handle, transaction):
        """
        Remove the Note specified by the database handle from the
        database, preserving the change in the passed transaction. 
        """
        self.__do_remove(handle, transaction, self.note_map, 
                              NOTE_KEY)

    @catch_db_error
    def set_name_group_mapping(self, name, group):
        if not self.readonly:
            # Start transaction
            with BSDDBTxn(self.env, self.name_group) as txn:
                name = str(name)
                data = txn.get(name)
                if data is not None:
                    txn.delete(name)
                if group is not None:
                    txn.put(name, group)
            self.emit('person-rebuild')

    def sort_surname_list(self):
        self.surname_list.sort(key=locale.strxfrm)

    @catch_db_error
    def build_surname_list(self):
        """
        Build surname list for use in autocompletion
        """
        self.surname_list = sorted(map(unicode, set(self.surnames.keys())), key=locale.strxfrm)

    def add_to_surname_list(self, person, batch_transaction):
        """
        Add surname to surname list
        """
        if batch_transaction:
            return
        name = unicode(person.get_primary_name().get_surname())
        i = bisect.bisect(self.surname_list, name)
        if 0 < i < len(self.surname_list):
            if self.surname_list[i-1] != name:
                self.surname_list.insert(i, name)
        else:
            self.surname_list.insert(i, name)

    @catch_db_error
    def remove_from_surname_list(self, person):
        """
        Check whether there are persons with the same surname left in
        the database. 
        
        If not then we need to remove the name from the list.
        The function must be overridden in the derived class.
        """
        name = str(person.get_primary_name().get_surname())
        try:
            cursor = self.surnames.cursor(txn=self.txn)
            cursor.set(name)
            if cursor.count() == 1:
                i = bisect.bisect(self.surname_list, name)
                assert 0 <= i-1 < len(self.surname_list)
                del self.surname_list[i-1]
        except ValueError:
            pass
        finally:
            cursor.close()
        
    def commit_base(self, obj, data_map, key, transaction, change_time):
        """
        Commit the specified object to the database, storing the changes as 
        part of the transaction.
        """
        if self.readonly or not obj or not obj.handle:
            return 

        obj.change = int(change_time if change_time else time.time())
        handle = str(obj.handle)

        self.update_reference_map(obj, transaction)

        # If this is a batch operation, just write the data
        if transaction.batch:
            data_map.put(handle, obj.serialize())
            old_data = None

        # Otherwise, this is a non-batch operation, so queue the transaction
        else:
            old_data = data_map.get(handle, txn=self.txn)
            new_data = obj.serialize()
            op = TXNUPD if old_data else TXNADD
            transaction.add(key, op, handle, old_data, new_data)
        return old_data
        
    def commit_person(self, person, transaction, change_time=None):
        """
        Commit the specified Person to the database, storing the changes as 
        part of the transaction.
        """
        old_data = self.commit_base(
            person, self.person_map, PERSON_KEY, transaction, change_time)

        if old_data:
            old_person = Person(old_data)

            # Update gender statistics if necessary
            if (old_person.gender != person.gender or
                old_person.primary_name.first_name !=
                  person.primary_name.first_name):

                self.genderStats.uncount_person(old_person)
                self.genderStats.count_person(person)

            # Update surname list if necessary
            if (old_person.primary_name.surname !=person.primary_name.surname):
                self.remove_from_surname_list(old_person)
                self.add_to_surname_list(person, transaction.batch)
        else:
            self.genderStats.count_person(person)
            self.add_to_surname_list(person, transaction.batch)

        self.individual_attributes.update(
            [str(attr.type) for attr in person.attribute_list
             if attr.type.is_custom() and str(attr.type)])

        if person.marker.is_custom():
            self.marker_names.add(str(person.marker))

        self.event_role_names.update([str(eref.role)
                                      for eref in person.event_ref_list
                                      if eref.role.is_custom()])

        self.name_types.update([str(name.type)
                                for name in ([person.primary_name]
                                             + person.alternate_names)
                                if name.type.is_custom()])
        
        self.url_types.update([str(url.type) for url in person.urls
                               if url.type.is_custom()])

        attr_list = []
        for mref in person.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)

    def commit_media_object(self, obj, transaction, change_time=None):
        """
        Commit the specified MediaObject to the database, storing the changes
        as part of the transaction.
        """
        self.commit_base(obj, self.media_map, MEDIA_KEY,
                            transaction, change_time)

        self.media_attributes.update(
            [str(attr.type) for attr in obj.attribute_list
             if attr.type.is_custom() and str(attr.type)])
            
    def commit_source(self, source, transaction, change_time=None):
        """
        Commit the specified Source to the database, storing the changes as 
        part of the transaction.
        """
        self.commit_base(source, self.source_map, SOURCE_KEY, 
                          transaction, change_time)

        self.source_media_types.update(
            [str(ref.media_type) for ref in source.reporef_list
             if ref.media_type.is_custom()])       

        attr_list = []
        for mref in source.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)

    def commit_place(self, place, transaction, change_time=None):
        """
        Commit the specified Place to the database, storing the changes as 
        part of the transaction.
        """
        self.commit_base(place, self.place_map, PLACE_KEY, 
                          transaction, change_time)

        self.url_types.update([str(url.type) for url in place.urls
                               if url.type.is_custom()])

        attr_list = []
        for mref in place.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)

    def commit_personal_event(self, event, transaction, change_time=None):
        if event.type.is_custom():
            self.individual_event_names.add(str(event.type))
        self.commit_event(event, transaction, change_time)

    def commit_family_event(self, event, transaction, change_time=None):
        if event.type.is_custom():
            self.family_event_names.add(str(event.type))
        self.commit_event(event, transaction, change_time)

    def commit_event(self, event, transaction, change_time=None):
        """
        Commit the specified Event to the database, storing the changes as 
        part of the transaction.
        """
        self.commit_base(event, self.event_map, EVENT_KEY, 
                  transaction, change_time)
        attr_list = []
        for mref in event.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)

    def commit_family(self, family, transaction, change_time=None):
        """
        Commit the specified Family to the database, storing the changes as 
        part of the transaction.
        """
        self.commit_base(family, self.family_map, FAMILY_KEY, 
                          transaction, change_time)

        self.family_attributes.update(
            [str(attr.type) for attr in family.attribute_list
             if attr.type.is_custom() and str(attr.type)])

        rel_list = []
        for ref in family.child_ref_list:
            if ref.frel.is_custom():
                rel_list.append(str(ref.frel))
            if ref.mrel.is_custom():
                rel_list.append(str(ref.mrel))
        self.child_ref_types.update(rel_list)

        self.event_role_names.update(
            [str(eref.role) for eref in family.event_ref_list
             if eref.role.is_custom()])

        if family.type.is_custom():
            self.family_rel_types.add(str(family.type))

        attr_list = []
        for mref in family.media_list:
            attr_list += [str(attr.type) for attr in mref.attribute_list
                          if attr.type.is_custom() and str(attr.type)]
        self.media_attributes.update(attr_list)

    def commit_repository(self, repository, transaction, change_time=None):
        """
        Commit the specified Repository to the database, storing the changes
        as part of the transaction.
        """
        self.commit_base(repository, self.repository_map, REPOSITORY_KEY, 
                          transaction, change_time)

        if repository.type.is_custom():
            self.repository_types.add(str(repository.type))

        self.url_types.update([str(url.type) for url in repository.urls
                               if url.type.is_custom()])

    def commit_note(self, note, transaction, change_time=None):
        """
        Commit the specified Note to the database, storing the changes as part 
        of the transaction.
        """
        self.commit_base(note, self.note_map, NOTE_KEY, 
                          transaction, change_time)

        if note.type.is_custom():
            self.note_types.add(str(note.type))        

    def get_from_handle(self, handle, class_type, data_map):
        try:
            data = data_map.get(str(handle), txn=self.txn)
        except:
            data = None
            # under certain circumstances during a database reload,
            # data_map can be none. If so, then don't report an error
            if data_map:
                _LOG.error("Failed to get from handle", exc_info=True)
        if data:
            newobj = class_type()
            newobj.unserialize(data)
            return newobj
        return None

    @catch_db_error
    def transaction_begin(self, msg="", batch=False, no_magic=False):
        """
        Create a new Transaction tied to the current UNDO database. 
        
        The transaction has no effect until it is committed using the 
        transaction_commit function of the this database object.
        """

        transaction = BdbTransaction(msg, self.undodb, self, batch, no_magic)
        if batch:
            # A batch transaction does not store the commits
            # Aborting the session completely will become impossible.
            self.abort_possible = False
            # Undo is also impossible after batch transaction
            self.undodb.clear()
            self.env.txn_checkpoint()

            if db.version() < (4, 7):
                self.env.set_flags(db.DB_TXN_NOSYNC, 1)      # async txn

            if self.secondary_connected and not no_magic:
                # Disconnect unneeded secondary indices
                self.surnames.close()
                _db = db.DB(self.env)
                try:
                    _db.remove(_mkname(self.full_name, SURNAMES), SURNAMES)
                except db.DBNoSuchFileError:
                    pass

                self.reference_map_referenced_map.close()
                _db = db.DB(self.env)
                try:
                    _db.remove(_mkname(self.full_name, REF_REF), REF_REF)
                except db.DBNoSuchFileError:
                    pass
        return transaction

    @catch_db_error
    def transaction_commit(self, transaction, msg):
        if self._LOG_ALL:
            LOG.debug("%s: Transaction commit '%s'\n"
                      % (self.__class__.__name__, str(msg)))

        if self.readonly:
            return

        transaction.commit(msg)
        self.undodb.commit(transaction, msg)
        self.__after_commit(transaction, msg)
        self.has_changed = True

    def __after_commit(self, transaction, msg):
        """
        Post-transaction commit processing
        """
        if transaction.batch:
            self.env.txn_checkpoint()
            if db.version() < (4, 7):
                self.env.set_flags(db.DB_TXN_NOSYNC, 0)      # sync txn

            if not transaction.no_magic:
                # create new secondary indices to replace the ones removed

                self.surnames = self.__open_db(self.full_name, SURNAMES,
                                    db.DB_BTREE, db.DB_DUP | db.DB_DUPSORT)

                self.person_map.associate(self.surnames, find_surname,
                                          DBFLAGS_O)

                self.reference_map_referenced_map = self.__open_db(self.full_name,
                    REF_REF, db.DB_BTREE, db.DB_DUP|db.DB_DUPSORT)

                self.reference_map.associate(self.reference_map_referenced_map,
                                             find_referenced_handle, DBFLAGS_O)

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

    def undo(self, update_history=True):
        self.undodb.undo(update_history)
        return

    def redo(self, update_history=True):
        self.undodb.redo(update_history)
        return

    def gramps_upgrade(self, callback=None):
        UpdateCallback.__init__(self, callback)
        
        version = self.metadata.get('version', default=_MINVERSION)

        t = time.time()

        if version < 14:
            import upgrade
            upgrade.gramps_upgrade_14(self)

        print "Upgrade time:", int(time.time()-t), "seconds"

    def set_auto_remove(self):
        """
        BSDDB change log settings using new method with renamed attributes
        """
        if db.version() < (4, 7):
            # by the book: old method with old attribute
            self.env.set_flags(db.DB_LOG_AUTOREMOVE, 1)
        else: # look at python interface
            # TODO test with new version of pybsddb
            try:
                # try numeric compare, just first 2 digits
                # this won't work with something like "4.10a", but
                # hopefully they won't do that
                old_version = map(int, db.__version__.split(".",2)[:2]) < (4, 7)
            except:
                # fallback, weak string compare
                old_version = db.__version__ < "4.7"
            if old_version:
                # undocumented: old method with new attribute
                self.env.set_flags(db.DB_LOG_AUTO_REMOVE, 1)
            else:
                # by the book: new method with new attribute
                self.env.log_set_config(db.DB_LOG_AUTO_REMOVE, 1)

    def write_version(self, name):
        """Write version number for a newly created DB."""
        full_name = os.path.abspath(name)

        self.env = db.DBEnv()
        self.env.set_cachesize(0, DBCACHE)

        # These env settings are only needed for Txn environment
        self.env.set_lk_max_locks(DBLOCKS)
        self.env.set_lk_max_objects(DBOBJECTS)

        # clean up unused logs
        self.set_auto_remove()

        # The DB_PRIVATE flag must go if we ever move to multi-user setup
        env_flags = db.DB_CREATE | db.DB_PRIVATE |\
                    db.DB_INIT_MPOOL | db.DB_INIT_LOCK |\
                    db.DB_INIT_LOG | db.DB_INIT_TXN | db.DB_THREAD

        # As opposed to before, we always try recovery on databases
        env_flags = env_flags | db.DB_RECOVER

        # Environment name is now based on the filename
        env_name = name

        self.env.open(env_name, env_flags)
        self.env.txn_checkpoint()

        self.metadata  = self.__open_shelf(full_name, META)
        
        with BSDDBTxn(self.env, self.metadata) as txn:
            txn.put('version', _DBVERSION)
        
        self.metadata.close()
        self.env.close()
        
#-------------------------------------------------------------------------
#
# BdbTransaction
#
#-------------------------------------------------------------------------
class BdbTransaction(GrampsDbTxn):
    """
    The batch parameter is set to True for large transactions. For such
    transactions, the list of changes is not maintained, and no undo
    is possible.

    The no_magic parameter is ignored for non-batch transactions, and
    is also of no importance for DB backends other than BSD DB. For
    the BSDDB, when this paramter is set to True, some secondary
    indices will be removed at the beginning and then rebuilt at
    the end of such transaction (only if it is batch).    
    """

    __slots__ = ('batch', 'no_magic')
    
    def __init__(self, msg, undodb, grampsdb, batch=False, no_magic=False):
        GrampsDbTxn.__init__(self, msg, undodb, grampsdb)
        self.batch = batch
        self.no_magic = no_magic

    def get_db_txn(self, value):
        return BSDDBTxn(value)

def _mkname(path, name):
    return os.path.join(path, name + DBEXT)

def clear_lock_file(name):
    try:
        os.unlink(os.path.join(name, DBLOCKFN))
    except OSError:
        return

def write_lock_file(name):
    if not os.path.isdir(name):
        os.mkdir(name)
    f = open(os.path.join(name, DBLOCKFN), "w")
    if os.name == 'nt':
        text = os.environ['USERNAME']
    else:
        host = os.uname()[1]
        # An ugly workaround for os.getlogin() issue with Konsole
        try:
            user = os.getlogin()
        except:
            user = os.environ.get('USER')
        text = "%s@%s" % (user, host)
    # Save only the username and host, so the massage can be
    # printed with correct locale in DbManager.py when a lock is found
    f.write(text)
    f.close()

if __name__ == "__main__":

    import os, sys, pdb
    
    d = GrampsDBDir()
    if len(sys.argv) > 1:
        db_name = sys.argv[1]
    else:
        db_home = os.path.join(os.environ['HOME'], '.gramps','grampsdb')
        for dir in os.listdir(db_home):
            db_path = os.path.join(db_home, dir)
            db_fn = os.path.join(db_path, 'name.txt')
            if os.stat(db_fn):
                f = open(db_fn)
                db_name = f.read()
                if db_name == 'Small Example':
                    break
    print "loading", db_path
    d.load(db_path, lambda x: x)

    print d.get_default_person()
    with d.get_person_cursor() as c:
        for key, data in c:
            person = Person(data)
            print key, person.get_primary_name().get_name(),

    print d.surnames.keys()
