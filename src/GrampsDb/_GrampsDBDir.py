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

# $Id: _GrampsDBDir.py 8221 2007-02-24 00:24:57Z rshura $

"""
Provides the Berkeley DB (DBDir) database backend for GRAMPS
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import cPickle as pickle
import os
import shutil
import re
import time
from gettext import gettext as _
from bsddb import dbshelve, db
import logging

log = logging.getLogger(".GrampsDb")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *
from _GrampsDbBase import *
from _DbUtils import db_copy
import _GrampsDbConst as const
from _GrampsDbExceptions import FileVersionError
from BasicUtils import UpdateCallback

_MINVERSION = 9
_DBVERSION = 13

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

def find_surname(key,data):
    return str(data[3][5])

def find_idmap(key,data):
    return str(data[1])

# Secondary database key lookups for reference_map table
# reference_map data values are of the form:
#   ((primary_object_class_name, primary_object_handle),
#    (referenced_object_class_name, referenced_object_handle))

def find_primary_handle(key,data):
    return str((data)[0][1])

def find_referenced_handle(key,data):
    return str((data)[1][1])

class GrampsDBDirCursor(GrampsCursor):

    def __init__(self,source,txn=None):
        self.cursor = source.db.cursor(txn)
        self.source = source
        
    def first(self):
        d = self.cursor.first()
        if d:
            return (d[0],pickle.loads(d[1]))
        return None

    def next(self):
        d = self.cursor.next()
        if d:
            return (d[0],pickle.loads(d[1]))
        return None

    def close(self):
        self.cursor.close()

    def delete(self):
        self.cursor.delete()
        
    def get_length(self):
        return self.source.stat()['ndata']

class GrampsDBDirAssocCursor(GrampsCursor):

    def __init__(self,source,txn=None):
        self.cursor = source.cursor(txn)
        self.source = source
        
    def first(self):
        d = self.cursor.first()
        if d:
            return (d[0],pickle.loads(d[1]))
        return None

    def next(self):
        d = self.cursor.next()
        if d:
            return (d[0],pickle.loads(d[1]))
        return None

    def close(self):
        self.cursor.close()

    def delete(self):
        self.cursor.delete()
        
    def get_length(self):
        return self.source.stat()['ndata']

class GrampsDBDirDupCursor(GrampsDBDirAssocCursor):
    """Cursor that includes handling for duplicate keys"""

    def set(self,key):
        return self.cursor.set(str(key))

    def next_dup(self):
        return self.cursor.next_dup()


#-------------------------------------------------------------------------
#
# GrampsDBDir
#
#-------------------------------------------------------------------------
class GrampsDBDir(GrampsDbBase,UpdateCallback):
    """GRAMPS database object. This object is a base class for other
    objects."""

    def __init__(self, use_txn = True):
        """creates a new GrampsDB"""
        
        GrampsDbBase.__init__(self)
        self.txn = None
        self.secondary_connected = False
        self.UseTXN = use_txn

    def open_flags(self):
        if self.UseTXN:
            return db.DB_CREATE | db.DB_AUTO_COMMIT
        else:
            return db.DB_CREATE

    def open_table(self, file_name, table_name, dbtype=db.DB_HASH):
        dbmap = dbshelve.DBShelf(self.env)
        dbmap.db.set_pagesize(16384)

        fname = os.path.join(file_name, table_name + ".db")

        if self.readonly:
            dbmap.open(fname, table_name, dbtype, db.DB_RDONLY)
        else:
            dbmap.open(fname, table_name, dbtype, self.open_flags(), 0666)
        return dbmap

    def _all_handles(self,table):
        return table.keys(self.txn)
    
    def get_person_cursor(self):
        return GrampsDBDirCursor(self.person_map, self.txn)

    def get_family_cursor(self):
        return GrampsDBDirCursor(self.family_map, self.txn)

    def get_event_cursor(self):
        return GrampsDBDirCursor(self.event_map, self.txn)

    def get_place_cursor(self):
        return GrampsDBDirCursor(self.place_map, self.txn)

    def get_source_cursor(self):
        return GrampsDBDirCursor(self.source_map, self.txn)

    def get_media_cursor(self):
        return GrampsDBDirCursor(self.media_map, self.txn)

    def get_repository_cursor(self):
        return GrampsDBDirCursor(self.repository_map, self.txn)

    def get_note_cursor(self):
        return GrampsDBDirCursor(self.note_map, self.txn)

    def has_person_handle(self,handle):
        """
        returns True if the handle exists in the current Person database.
        """
        return self.person_map.get(str(handle), txn=self.txn) != None

    def has_family_handle(self,handle):            
        """
        returns True if the handle exists in the current Family database.
        """
        return self.family_map.get(str(handle),txn=self.txn) != None

    def has_object_handle(self,handle):
        """
        returns True if the handle exists in the current MediaObjectdatabase.
        """
        return self.media_map.get(str(handle),txn=self.txn) != None

    def has_repository_handle(self,handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return self.repository_map.get(str(handle), txn=self.txn) != None

    def has_note_handle(self,handle):
        """
        returns True if the handle exists in the current Note database.
        """
        return self.note_map.get(str(handle), txn=self.txn) != None

    def has_event_handle(self,handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return self.event_map.get(str(handle), txn=self.txn) != None

    def has_place_handle(self,handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return self.place_map.get(str(handle), txn=self.txn) != None

    def has_source_handle(self,handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return self.source_map.get(str(handle), txn=self.txn) != None

    def get_raw_person_data(self,handle):
        return self.person_map.get(str(handle), txn=self.txn)

    def get_raw_family_data(self,handle):
        return self.family_map.get(str(handle), txn=self.txn)

    def get_raw_object_data(self,handle):
        return self.media_map.get(str(handle), txn=self.txn)

    def get_raw_place_data(self,handle):
        return self.place_map.get(str(handle), txn=self.txn)

    def get_raw_event_data(self,handle):
        return self.event_map.get(str(handle), txn=self.txn)

    def get_raw_source_data(self,handle):
        return self.source_map.get(str(handle), txn=self.txn)

    def get_raw_repository_data(self,handle):
        return self.repository_map.get(str(handle), txn=self.txn)

    def get_raw_note_data(self,handle):
        return self.note_map.get(str(handle), txn=self.txn)

    # cursors for lookups in the reference_map for back reference
    # lookups. The reference_map has three indexes:
    # the main index: a tuple of (primary_handle,referenced_handle)
    # the primary_handle index: the primary_handle
    # the referenced_handle index: the referenced_handle
    # the main index is unique, the others allow duplicate entries.

    def get_reference_map_cursor(self):
        return GrampsDBDirAssocCursor(self.reference_map, self.txn)

    def get_reference_map_primary_cursor(self):
        return GrampsDBDirDupCursor(self.reference_map_primary_map, self.txn)

    def get_reference_map_referenced_cursor(self):
        return GrampsDBDirDupCursor(self.reference_map_referenced_map, self.txn)

    # These are overriding the GrampsDbBase's methods of saving metadata
    # because we now have txn-capable metadata table
    def set_default_person_handle(self, handle):
        """sets the default Person to the passed instance"""
        if not self.readonly:
            if self.UseTXN:
                # Start transaction if needed
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self.metadata.put('default', str(handle), txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            else:
                self.metadata.sync()

    def get_default_person(self):
        """returns the default Person of the database"""
        person = self.get_person_from_handle(self.get_default_handle())
        if person:
            return person
        elif (self.metadata) and (not self.readonly):
            if self.UseTXN:
                # Start transaction if needed
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self.metadata.put('default', None, txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            else:
                self.metadata.sync()
        return None

    def _set_column_order(self, col_list, name):
        if self.metadata and not self.readonly: 
            if self.UseTXN:
                # Start transaction if needed
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self.metadata.put(name, col_list, txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            else:
                self.metadata.sync()

    def version_supported(self):
        dbversion = self.metadata.get('version',default=0)
        return ((dbversion <= _DBVERSION) and (dbversion >= _MINVERSION))
    
    def need_upgrade(self):
        dbversion = self.metadata.get('version',default=0)
        return not self.readonly and dbversion < _DBVERSION

    def load(self, name, callback,mode="w"):
        if self.db_is_open:
            self.close()

        self.readonly = mode == "r"
        if self.readonly:
            self.UseTXN = False

        callback(12)

        self.full_name = os.path.abspath(name)
        self.brief_name = os.path.basename(name)

        self.env = db.DBEnv()
        self.env.set_cachesize(0,0x4000000)         # 32MB

        if self.UseTXN:
            # These env settings are only needed for Txn environment
            self.env.set_lk_max_locks(25000)
            self.env.set_lk_max_objects(25000)
            self.env.set_flags(db.DB_LOG_AUTOREMOVE, 1)  # clean up unused logs

            # The DB_PRIVATE flag must go if we ever move to multi-user setup
            env_flags = db.DB_CREATE | db.DB_PRIVATE |\
                        db.DB_INIT_MPOOL | db.DB_INIT_LOCK |\
                        db.DB_INIT_LOG | db.DB_INIT_TXN | db.DB_THREAD

            # Only do recovery for existing databases
            if os.path.isfile(self.full_name):
                env_flags = env_flags | db.DB_RECOVER

            # Environment name is now based on the filename
            env_name = name
        else:
            env_flags = db.DB_CREATE | db.DB_PRIVATE | db.DB_INIT_MPOOL
            env_name = os.path.expanduser('~')

        self.env.open(env_name,env_flags)
        if self.UseTXN:
            self.env.txn_checkpoint()

        callback(25)
        self.metadata  = self.open_table(self.full_name, META)

        # If we cannot work with this DB version,
        # it makes no sense to go further
        if not self.version_supported:
            self._close_early()

        self.family_map     = self.open_table(self.full_name, FAMILY_TBL)
        self.place_map      = self.open_table(self.full_name, PLACES_TBL)
        self.source_map     = self.open_table(self.full_name, SOURCES_TBL)
        self.media_map      = self.open_table(self.full_name, MEDIA_TBL)
        self.event_map      = self.open_table(self.full_name, EVENTS_TBL)
        self.person_map     = self.open_table(self.full_name, PERSON_TBL)
        self.repository_map = self.open_table(self.full_name, REPO_TBL)
        self.note_map       = self.open_table(self.full_name, NOTE_TBL)
        self.reference_map  = self.open_table(self.full_name, REF_MAP,
                                              dbtype=db.DB_BTREE)
        callback(37)

        self._load_metadata()

        gstats = self.metadata.get('gender_stats', default=None)

        if not self.readonly:
            if self.UseTXN:
                # Start transaction if needed
                the_txn = self.env.txn_begin()
            else:
                the_txn = None

            if gstats == None:
                # New database. Set up the current version.
                self.metadata.put('version', _DBVERSION, txn=the_txn)
            elif not self.metadata.has_key('version'):
                # Not new database, but the version is missing.
                # Use 0, but it is likely to fail anyway.
                self.metadata.put('version', 0, txn=the_txn)

            if self.UseTXN:
                the_txn.commit()
            else:
                self.metadata.sync()
            
        self.genderStats = GenderStats(gstats)

        # Here we take care of any changes in the tables related to new code.
        # If secondary indices change, then they should removed
        # or rebuilt by upgrade as well. In any case, the
        # self.secondary_connected flag should be set accordingly.
        
        if self.need_upgrade():
            self.gramps_upgrade(callback)

        callback(50)

        if not self.secondary_connected:
            self.connect_secondary()

        callback(75)

        self.open_undodb()
        self.db_is_open = True

        callback(87)
        
        # Re-set the undo history to a fresh session start
        self.undoindex = -1
        self.translist = [None] * len(self.translist)
        self.abort_possible = True
        self.undo_history_timestamp = time.time()

        return 1

    def load_from(self, other_database, filename, callback):
        self.load(filename,callback)
        db_copy(other_database,self,callback)
        return 1

    def _load_metadata(self):
        # name display formats
        self.name_formats = self.metadata.get('name_formats', default=[])
        # upgrade formats if they were saved in the old way
        for format_ix in range(len(self.name_formats)):
            format = self.name_formats[format_ix]
            if len(format) == 3:
                format = format + (True,)
                self.name_formats[format_ix] = format
        
        # database owner
        self.set_researcher(self.metadata.get('researcher', default=self.owner))
        
        # bookmarks
        self.bookmarks.set(self.metadata.get('bookmarks',default=[]))
        self.family_bookmarks.set(self.metadata.get('family_bookmarks',
                                                    default=[]))
        self.event_bookmarks.set(self.metadata.get('event_bookmarks',
                                                   default=[]))
        self.source_bookmarks.set(self.metadata.get('source_bookmarks',
                                                    default=[]))
        self.repo_bookmarks.set(self.metadata.get('repo_bookmarks',
                                                  default=[]))
        self.media_bookmarks.set(self.metadata.get('media_bookmarks',
                                                   default=[]))
        self.place_bookmarks.set(self.metadata.get('place_bookmarks',
                                                   default=[]))
        self.note_bookmarks.set(self.metadata.get('note_bookmarks',
                                                   default=[]))

        # Custom type values
        self.family_event_names = set(self.metadata.get('fevent_names',
                                                        default=[]))
        self.individual_event_names = set(self.metadata.get('pevent_names',
                                                            default=[]))
        self.family_attributes = set(self.metadata.get('fattr_names',
                                                       default=[]))
        self.individual_attributes = set(self.metadata.get('pattr_names',
                                                           default=[]))
        self.marker_names = set(self.metadata.get('marker_names',default=[]))
        self.child_ref_types = set(self.metadata.get('child_refs',
                                                     default=[]))
        self.family_rel_types = set(self.metadata.get('family_rels',
                                                      default=[]))
        self.event_role_names = set(self.metadata.get('event_roles',
                                                      default=[]))
        self.name_types = set(self.metadata.get('name_types',default=[]))
        self.repository_types = set(self.metadata.get('repo_types',
                                                      default=[]))
        self.note_types = set(self.metadata.get('note_types',
                                                default=[]))
        self.source_media_types = set(self.metadata.get('sm_types',
                                                        default=[]))
        self.url_types = set(self.metadata.get('url_types',default=[]))
        self.media_attributes = set(self.metadata.get('mattr_names',
                                                      default=[]))

        # surname list
        self.surname_list = self.metadata.get('surname_list', default=[])

    def connect_secondary(self):
        """
        This method connects or creates secondary index tables.
        It assumes that the tables either exist and are in the right
        format or do not exist (in which case they get created).

        It is the responsibility of upgrade code to either create
        or remove invalid secondary index tables.
        """
        
        # index tables used just for speeding up searches
        if self.readonly:
            table_flags = db.DB_RDONLY
        else:
            table_flags = self.open_flags()

        self.surnames = db.DB(self.env)
        self.surnames.set_flags(db.DB_DUP | db.DB_DUPSORT)
        self.surnames.open(_mkname(self.full_name, SURNAMES), SURNAMES, 
                           db.DB_BTREE, flags=table_flags)

        self.name_group = db.DB(self.env)
        self.name_group.set_flags(db.DB_DUP)
        self.name_group.open(_mkname(self.full_name, NAME_GROUP), NAME_GROUP,
                             db.DB_HASH, flags=table_flags)

        self.id_trans = db.DB(self.env)
        self.id_trans.set_flags(db.DB_DUP)
        self.id_trans.open(_mkname(self.full_name, IDTRANS), IDTRANS,
                           db.DB_HASH, flags=table_flags)

        self.fid_trans = db.DB(self.env)
        self.fid_trans.set_flags(db.DB_DUP)
        self.fid_trans.open(_mkname(self.full_name, FIDTRANS), FIDTRANS,
                            db.DB_HASH, flags=table_flags)

        self.eid_trans = db.DB(self.env)
        self.eid_trans.set_flags(db.DB_DUP)
        self.eid_trans.open(_mkname(self.full_name, EIDTRANS), EIDTRANS,
                            db.DB_HASH, flags=table_flags)

        self.pid_trans = db.DB(self.env)
        self.pid_trans.set_flags(db.DB_DUP)
        self.pid_trans.open(_mkname(self.full_name, PIDTRANS), PIDTRANS,
                            db.DB_HASH, flags=table_flags)

        self.sid_trans = db.DB(self.env)
        self.sid_trans.set_flags(db.DB_DUP)
        self.sid_trans.open(_mkname(self.full_name, SIDTRANS), SIDTRANS,
                            db.DB_HASH, flags=table_flags)

        self.oid_trans = db.DB(self.env)
        self.oid_trans.set_flags(db.DB_DUP)
        self.oid_trans.open(_mkname(self.full_name, OIDTRANS), OIDTRANS,
                            db.DB_HASH, flags=table_flags)

        self.rid_trans = db.DB(self.env)
        self.rid_trans.set_flags(db.DB_DUP)
        self.rid_trans.open(_mkname(self.full_name, RIDTRANS), RIDTRANS,
                            db.DB_HASH, flags=table_flags)

        self.nid_trans = db.DB(self.env)
        self.nid_trans.set_flags(db.DB_DUP)
        self.nid_trans.open(_mkname(self.full_name, NIDTRANS), NIDTRANS,
                            db.DB_HASH, flags=table_flags)

        self.reference_map_primary_map = db.DB(self.env)
        self.reference_map_primary_map.set_flags(db.DB_DUP)
        self.reference_map_primary_map.open(
            _mkname(self.full_name, REF_PRI),
            REF_PRI, db.DB_BTREE, flags=table_flags)

        self.reference_map_referenced_map = db.DB(self.env)
        self.reference_map_referenced_map.set_flags(db.DB_DUP|db.DB_DUPSORT)
        self.reference_map_referenced_map.open(
            _mkname(self.full_name, REF_REF),
            REF_REF, db.DB_BTREE, flags=table_flags)

        if not self.readonly:
            self.person_map.associate(self.surnames, find_surname, table_flags)
            self.person_map.associate(self.id_trans, find_idmap, table_flags)
            self.family_map.associate(self.fid_trans,find_idmap, table_flags)
            self.event_map.associate(self.eid_trans, find_idmap,  table_flags)
            self.repository_map.associate(self.rid_trans, find_idmap,
                                          table_flags)
            self.note_map.associate(self.nid_trans, find_idmap, table_flags)
            self.place_map.associate(self.pid_trans,  find_idmap, table_flags)
            self.media_map.associate(self.oid_trans, find_idmap, table_flags)
            self.source_map.associate(self.sid_trans, find_idmap, table_flags)
            self.reference_map.associate(self.reference_map_primary_map,
                                         find_primary_handle,
                                         table_flags)
            self.reference_map.associate(self.reference_map_referenced_map,
                                         find_referenced_handle,
                                         table_flags)
        self.secondary_connected = True

        self.smap_index = len(self.source_map)
        self.emap_index = len(self.event_map)
        self.pmap_index = len(self.person_map)
        self.fmap_index = len(self.family_map)
        self.lmap_index = len(self.place_map)
        self.omap_index = len(self.media_map)
        self.rmap_index = len(self.repository_map)
        self.nmap_index = len(self.note_map)

    def rebuild_secondary(self,callback):
        if self.readonly:
            return

        table_flags = self.open_flags()

        # remove existing secondary indices
        
        index = 1

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

        for (db, name) in items:
            db.close()
            env = db.DB(self.env)
            env.remove(_mkname(self.full_name, name), name)
            callback(index)
            index += 1

        callback(11)

        # Set flag saying that we have removed secondary indices
        # and then call the creating routine
        self.secondary_connected = False
        self.connect_secondary()
        callback(12)

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        Returns an interator over a list of (class_name,handle) tuples.

        @param handle: handle of the object to search for.
        @type handle: database handle
        @param include_classes: list of class names to include in the results.
                                Default: None means include all classes.
        @type include_classes: list of class names

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use:

        >       result_list = [i for i in find_backlink_handles(handle)]
        """


        # Use the secondary index to locate all the reference_map entries
        # that include a reference to the object we are looking for.
        referenced_cur = self.get_reference_map_referenced_cursor()

        try:
            ret = referenced_cur.set(handle)
        except:
            ret = None
            
        while (ret is not None):
            (key,data) = ret
            
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
            if include_classes == None or \
                   KEY_TO_CLASS_MAP[data[0][0]] in include_classes:
                yield (KEY_TO_CLASS_MAP[data[0][0]],data[0][1])
                
            ret = referenced_cur.next_dup()

        referenced_cur.close()

        return 

    def _delete_primary_from_reference_map(self,handle,transaction,txn=None):
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
            (key,data) = ret
            
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
            self._remove_reference(main_key,transaction,txn)
        
    def _update_reference_map(self, obj, transaction, txn=None):
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
            # list of (class_name,handle) pairs.
            # The primary_map sec index allows us to look this up quickly.

            existing_references = set()

            primary_cur = self.get_reference_map_primary_cursor()

            try:
                ret = primary_cur.set(handle)
            except:
                ret = None

            while (ret is not None):
                (key,data) = ret

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
        for (ref_class_name,ref_handle) in new_references:
            data = ((CLASS_TO_KEY_MAP[obj.__class__.__name__],handle),
                    (CLASS_TO_KEY_MAP[ref_class_name],ref_handle),)
            self._add_reference((handle,ref_handle),data,transaction,txn)

        # handle deletion of old references
        for (ref_class_name,ref_handle) in no_longer_required_references:
            try:
                self._remove_reference((handle,ref_handle),transaction,txn)
            except:
                # ignore missing old reference
                pass

    def _remove_reference(self,key,transaction,txn=None):
        """
        Removes the reference specified by the key,
        preserving the change in the passed transaction.
        """
        if not self.readonly:
            if transaction.batch:
                self.reference_map.delete(str(key),txn=txn)
                if not self.UseTXN:
                    self.reference_map.sync()
            else:
                old_data = self.reference_map.get(str(key),txn=self.txn)
                transaction.add(REFERENCE_KEY,str(key),old_data,None)
                transaction.reference_del.append(str(key))

    def _add_reference(self,key,data,transaction,txn=None):
        """
        Adds the reference specified by the key and the data,
        preserving the change in the passed transaction.
        """

        if self.readonly or not key:
            return
        
        if transaction.batch:
            self.reference_map.put(str(key),data,txn=txn)
            if not self.UseTXN:
                self.reference_map.sync()
        else:
            transaction.add(REFERENCE_KEY,str(key),None,data)
            transaction.reference_add.append((str(key),data))

    def reindex_reference_map(self,callback):
        """
        Reindex all primary records in the database.
        This will be a slow process for large databases.

        """

        # First, remove the reference map and related tables
        self.reference_map_referenced_map.close()
        junk = db.DB(self.env)
        junk.remove(_mkname(self.full_name, REF_REF), REF_REF)
        callback(1)

        self.reference_map_primary_map.close()
        junk = db.DB(self.env)
        junk.remove(_mkname(self.full_name, REF_PRI), REF_PRI)
        callback(2)

        self.reference_map.close()
        junk = db.DB(self.env)
        junk.remove(_mkname(self.full_name, REF_MAP), REF_MAP)
        callback(3)

        # Open reference_map and primapry map
        self.reference_map  = self.open_table(
            _mkname(self.full_name, REF_MAP), REF_MAP, dbtype=db.DB_BTREE)
        
        open_flags = self.open_flags()
        self.reference_map_primary_map = db.DB(self.env)
        self.reference_map_primary_map.set_flags(db.DB_DUP)
        self.reference_map_primary_map.open(
            _mkname(self.full_name, REF_PRI), REF_PRI,  db.DB_BTREE, flags=open_flags)

        self.reference_map.associate(self.reference_map_primary_map,
                                     find_primary_handle,
                                     open_flags)

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
            'Note': {'cursor_func': self.get_note_cursor,
                           'class_func': Note},
            }

        transaction = self.transaction_begin(batch=True,no_magic=True)
        callback(4)

        # Now we use the functions and classes defined above
        # to loop through each of the primary object tables.
        for primary_table_name in primary_tables.keys():
            
            cursor = primary_tables[primary_table_name]['cursor_func']()
            data = cursor.first()

            # Grab the real object class here so that the lookup does
            # not happen inside the cursor loop.
            class_func = primary_tables[primary_table_name]['class_func']
            while data:
                found_handle,val = data
                obj = class_func()
                obj.unserialize(val)

                if self.UseTXN:
                    the_txn = self.env.txn_begin()
                else:
                    the_txn = None
                self._update_reference_map(obj,transaction,the_txn)
                if not self.UseTXN:
                    self.reference_map.sync()
                if the_txn:
                    the_txn.commit()
                
                data = cursor.next()

            cursor.close()
        callback(5)
        self.transaction_commit(transaction,_("Rebuild reference map"))

        self.reference_map_referenced_map = db.DB(self.env)
        self.reference_map_referenced_map.set_flags(db.DB_DUP|db.DB_DUPSORT)
        self.reference_map_referenced_map.open(
            _mkname(self.full_name, REF_REF),
            REF_REF, db.DB_BTREE,flags=open_flags)
        self.reference_map.associate(self.reference_map_referenced_map,
                                     find_referenced_handle,open_flags)
        callback(6)

        return
        
    def _close_metadata(self):
        if not self.readonly:
            if self.UseTXN:
                # Start transaction if needed
                the_txn = self.env.txn_begin()
            else:
                the_txn = None

            # name display formats
            self.metadata.put('name_formats',self.name_formats,txn=the_txn)
            
            # database owner
            self.metadata.put('researcher', self.owner, txn=the_txn)

            # bookmarks
            self.metadata.put('bookmarks',self.bookmarks.get(),txn=the_txn)
            self.metadata.put('family_bookmarks',self.family_bookmarks.get(),
                              txn=the_txn)
            self.metadata.put('event_bookmarks',self.event_bookmarks.get(),
                              txn=the_txn)
            self.metadata.put('source_bookmarks',self.source_bookmarks.get(),
                              txn=the_txn)
            self.metadata.put('place_bookmarks',self.place_bookmarks.get(),
                              txn=the_txn)
            self.metadata.put('repo_bookmarks',self.repo_bookmarks.get(),
                              txn=the_txn)
            self.metadata.put('media_bookmarks',self.media_bookmarks.get(),
                              txn=the_txn)
            self.metadata.put('note_bookmarks',self.note_bookmarks.get(),
                              txn=the_txn)

            # gender stats
            self.metadata.put('gender_stats',self.genderStats.save_stats(),
                              txn=the_txn)
            # Custom type values
            self.metadata.put('fevent_names',list(self.family_event_names),
                              txn=the_txn)
            self.metadata.put('pevent_names',list(self.individual_event_names),
                              txn=the_txn)
            self.metadata.put('fattr_names',list(self.family_attributes),
                              txn=the_txn)
            self.metadata.put('pattr_names',list(self.individual_attributes),
                              txn=the_txn)
            self.metadata.put('marker_names',list(self.marker_names),
                              txn=the_txn)
            self.metadata.put('child_refs',list(self.child_ref_types),
                              txn=the_txn)
            self.metadata.put('family_rels',list(self.family_rel_types),
                              txn=the_txn)
            self.metadata.put('event_roles',list(self.event_role_names),
                              txn=the_txn)
            self.metadata.put('name_types',list(self.name_types),
                              txn=the_txn)
            self.metadata.put('repo_types',list(self.repository_types),
                              txn=the_txn)
            self.metadata.put('note_types',list(self.note_types),
                              txn=the_txn)
            self.metadata.put('sm_types',list(self.source_media_types),
                              txn=the_txn)
            self.metadata.put('url_types',list(self.url_types),
                              txn=the_txn)
            self.metadata.put('mattr_names',list(self.media_attributes),
                              txn=the_txn)
            # name display formats
            self.metadata.put('surname_list',self.surname_list,txn=the_txn)

            if self.UseTXN:
                the_txn.commit()
            else:
                self.metadata.sync()

        self.metadata.close()

    def _close_early(self):
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
            "The database version is not supported by this "
            "version of GRAMPS.\nPlease upgrade to the "
            "corresponding version or use XML for porting"
            "data between different database versions.")

    def close(self):
        if not self.db_is_open:
            return

        if self.UseTXN:
            self.env.txn_checkpoint()

        self._close_metadata()
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

        # Attempt to clear log sequence numbers, to make database portable
        # This will only work for python2.5 and higher
# Comment this our because it causes crashes.
# To reproduce the crash, create a new DB, import example.gramps, open and close the db a few times.
#        try:
#            self.env.lsn_reset(self.full_name)
#        except AttributeError:
#            pass
        
        self.env.close()

        try:
            self.close_undodb()
        except db.DBNoSuchFileError:
            pass

        self.person_map     = None
        self.family_map     = None
        self.repository_map = None
        self.note_map       = None
        self.place_map      = None
        self.source_map     = None
        self.media_map      = None
        self.event_map      = None
        self.surnames       = None
        self.env            = None
        self.metadata       = None
        self.db_is_open     = False

    def _do_remove_object(self,handle,transaction,data_map,key,del_list):
        if self.readonly or not handle:
            return

        handle = str(handle)
        if transaction.batch:
            if self.UseTXN:
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self._delete_primary_from_reference_map(handle,transaction,
                                                    txn=the_txn)
            data_map.delete(handle,txn=the_txn)
            if not self.UseTXN:
                data_map.sync()
            if the_txn:
                the_txn.commit()
        else:
            self._delete_primary_from_reference_map(handle,transaction)
            old_data = data_map.get(handle,txn=self.txn)
            transaction.add(key,handle,old_data,None)
            del_list.append(handle)

    def _del_person(self,handle):
        self.person_map.delete(str(handle),txn=self.txn)
        if not self.UseTXN:
            self.person_map.sync()

    def _del_source(self,handle):
        self.source_map.delete(str(handle),txn=self.txn)
        if not self.UseTXN:
            self.source_map.sync()

    def _del_repository(self,handle):
        self.repository_map.delete(str(handle),txn=self.txn)
        if not self.UseTXN:
            self.repository_map.sync()

    def _del_note(self,handle):
        self.note_map.delete(str(handle),txn=self.txn)
        if not self.UseTXN:
            self.note_map.sync()

    def _del_place(self,handle):
        self.place_map.delete(str(handle),txn=self.txn)
        if not self.UseTXN:
            self.place_map.sync()

    def _del_media(self,handle):
        self.media_map.delete(str(handle),txn=self.txn)
        if not self.UseTXN:
            self.media_map.sync()

    def _del_family(self,handle):
        self.family_map.delete(str(handle),txn=self.txn)
        if not self.UseTXN:
            self.family_map.sync()

    def _del_event(self,handle):
        self.event_map.delete(str(handle),txn=self.txn)
        if not self.UseTXN:
            self.event_map.sync()

    def set_name_group_mapping(self,name,group):
        if not self.readonly:
            if self.UseTXN:
                # Start transaction if needed
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            name = str(name)
            data = self.name_group.get(name,txn=the_txn)
            if not group and data:
                self.name_group.delete(name,txn=the_txn)
            else:
                self.name_group.put(name,group,txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            else:
                self.name_group.sync()
            self.emit('person-rebuild')

    def build_surname_list(self):
        self.surname_list = list(set(self.surnames.keys()))
        self.sort_surname_list()

    def remove_from_surname_list(self,person):
        """
        Check whether there are persons with the same surname left in
        the database. If not then we need to remove the name from the list.
        The function must be overridden in the derived class.
        """
        name = str(person.get_primary_name().get_surname())
        try:
            if self.surnames.keys().count(name) == 1:
                self.surname_list.remove(unicode(name))
        except ValueError:
            pass

    def _get_obj_from_gramps_id(self,val,tbl,class_init,prim_tbl):
        if tbl.has_key(str(val)):
            data = tbl.get(str(val),txn=self.txn)
            obj = class_init()
            ### FIXME: this is a dirty hack that works without no
            ### sensible explanation. For some reason, for a readonly
            ### database, secondary index returns a primary table key
            ### corresponding to the data, not the data.
            if self.readonly:
                tuple_data = prim_tbl.get(data,txn=self.txn)
            else:
                tuple_data = pickle.loads(data)
            obj.unserialize(tuple_data)
            return obj
        else:
            return None

    def get_person_from_gramps_id(self,val):
        """
        Finds a Person in the database from the passed gramps' ID.
        If no such Person exists, None is returned.
        """
        return self._get_obj_from_gramps_id(val,self.id_trans,Person,
                                            self.person_map)

    def get_family_from_gramps_id(self,val):
        """
        Finds a Family in the database from the passed gramps' ID.
        If no such Family exists, None is return.
        """
        return self._get_obj_from_gramps_id(val,self.fid_trans,Family,
                                            self.family_map)

    def get_event_from_gramps_id(self,val):
        """
        Finds an Event in the database from the passed gramps' ID.
        If no such Family exists, None is returned.
        """
        return self._get_obj_from_gramps_id(val,self.eid_trans,Event,
                                            self.event_map)

    def get_place_from_gramps_id(self,val):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        return self._get_obj_from_gramps_id(val,self.pid_trans,Place,
                                            self.place_map)

    def get_source_from_gramps_id(self,val):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        return self._get_obj_from_gramps_id(val,self.sid_trans,Source,
                                            self.source_map)

    def get_object_from_gramps_id(self,val):
        """
        Finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, None is returned.
        """
        return self._get_obj_from_gramps_id(val,self.oid_trans,MediaObject,
                                            self.media_map)

    def get_repository_from_gramps_id(self,val):
        """
        Finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned.
        """
        return self._get_obj_from_gramps_id(val,self.rid_trans,Repository,
                                            self.repository_map)

    def get_note_from_gramps_id(self,val):
        """
        Finds a Note in the database from the passed gramps' ID.
        If no such Note exists, None is returned.
        """
        return self._get_obj_from_gramps_id(val,self.nid_trans,Note,
                                            self.note_map)

    def _commit_base(self, obj, data_map, key, update_list, add_list,
                     transaction, change_time):
        """
        Commits the specified object to the database, storing the changes
        as part of the transaction.
        """
        if self.readonly or not obj or not obj.handle:
            return 

        if change_time:
            obj.change = int(change_time)
        else:
            obj.change = int(time.time())
        handle = str(obj.handle)
        
        if transaction.batch:
            if self.UseTXN:
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self._update_reference_map(obj,transaction,txn=the_txn)
            data_map.put(handle,obj.serialize(),txn=the_txn)
            if not self.UseTXN:
                data_map.sync()
            if the_txn:
                the_txn.commit()
            old_data = None
        else:
            self._update_reference_map(obj,transaction)
            old_data = data_map.get(handle,txn=self.txn)
            new_data = obj.serialize()
            transaction.add(key,handle,old_data,new_data)
            if old_data:
                update_list.append((handle,new_data))
            else:
                add_list.append((handle,new_data))
        return old_data

    def _do_commit(self, add_list, db_map):
        retlist = []
        for (handle, data) in add_list:
            db_map.put(handle, data, self.txn)
            if not self.UseTXN:
                db_map.sync()
            retlist.append(str(handle))
        return retlist

    def _get_from_handle(self, handle, class_type, data_map):
        try:
            data = data_map.get(str(handle),txn=self.txn)
        except:
            data = None
            # under certain circumstances during a database reload,
            # data_map can be none. If so, then don't report an error
            if data_map:
                log.error("Failed to get from handle",exc_info=True)
        if data:
            newobj = class_type()
            newobj.unserialize(data)
            return newobj
        return None

    def _find_from_handle(self,handle,transaction,class_type,dmap,add_func):
        obj = class_type()
        handle = str(handle)
        if dmap.has_key(handle):
            data = dmap.get(handle,txn=self.txn)
            obj.unserialize(data)
        else:
            obj.set_handle(handle)
            add_func(obj,transaction)
        return obj

    def transaction_begin(self,msg="",batch=False,no_magic=False):
        """
        Creates a new Transaction tied to the current UNDO database. The
        transaction has no effect until it is committed using the
        transaction_commit function of the this database object.
        """

        if batch:
            # A batch transaction does not store the commits
            # Aborting the session completely will become impossible.
            self.abort_possible = False
            # Undo is also impossible after batch transaction
            self.undoindex = -1
            self.translist = [None] * len(self.translist)
        transaction = BdbTransaction(msg,self.undodb,batch,no_magic)
        if transaction.batch:
            if self.UseTXN:
                self.env.txn_checkpoint()
                self.env.set_flags(db.DB_TXN_NOSYNC,1)      # async txn

            if self.secondary_connected and not transaction.no_magic:
                # Disconnect unneeded secondary indices
                self.surnames.close()
                junk = db.DB(self.env)
                junk.remove(_mkname(self.full_name, SURNAMES), SURNAMES)

                self.reference_map_referenced_map.close()
                junk = db.DB(self.env)
                junk.remove(_mkname(self.full_name, REF_REF), REF_REF)
            
        return transaction

    def transaction_commit(self,transaction,msg):

        # Start BSD DB transaction -- DBTxn
        if self.UseTXN:
            self.txn = self.env.txn_begin()
        else:
            self.txn = None

        GrampsDbBase.transaction_commit(self,transaction,msg)

        for (key,data) in transaction.reference_add:
            self.reference_map.put(str(key),data,txn=self.txn)

        for key in transaction.reference_del:
            self.reference_map.delete(str(key),txn=self.txn)

        if (len(transaction.reference_add)+len(transaction.reference_del)) > 0\
               and not self.UseTXN:
            self.reference_map.sync()

        # Commit BSD DB transaction -- DBTxn
        if self.UseTXN:
            self.txn.commit()
        if transaction.batch:
            if self.UseTXN:
                self.env.txn_checkpoint()
                self.env.set_flags(db.DB_TXN_NOSYNC,0)      # sync txn

            if not transaction.no_magic:
                # create new secondary indices to replace the ones removed
                open_flags = self.open_flags()
                dupe_flags = db.DB_DUP|db.DB_DUPSORT

                self.surnames = db.DB(self.env)
                self.surnames.set_flags(dupe_flags)
                self.surnames.open(
                    _mkname(self.full_name, "surnames"),
                    'surnames', db.DB_BTREE,flags=open_flags)
                self.person_map.associate(self.surnames,find_surname,
                                          open_flags)
            
                self.reference_map_referenced_map = db.DB(self.env)
                self.reference_map_referenced_map.set_flags(dupe_flags)
                self.reference_map_referenced_map.open(
                    _mkname(self.full_name, REF_REF),
                    REF_REF, db.DB_BTREE,flags=open_flags)
                self.reference_map.associate(self.reference_map_referenced_map,
                                             find_referenced_handle,open_flags)

            # Only build surname list after surname index is surely back
            self.build_surname_list()

        self.txn = None

    def undo(self,update_history=True):
        print "Undoing it"
        if self.UseTXN:
            self.txn = self.env.txn_begin()
        status = GrampsDbBase.undo(self,update_history)
        if self.UseTXN:
            if status:
                self.txn.commit()
            else:
                self.txn.abort()
        self.txn = None
        return status

    def redo(self,update_history=True):
        print "Redoing it"
        if self.UseTXN:
            self.txn = self.env.txn_begin()
        status = GrampsDbBase.redo(self,update_history)
        if self.UseTXN:
            if status:
                self.txn.commit()
            else:
                self.txn.abort()
        self.txn = None
        return status

    def undo_reference(self,data,handle):
        if data == None:
            self.reference_map.delete(handle,txn=self.txn)
        else:
            self.reference_map.put(handle,data,txn=self.txn)

    def undo_data(self,data,handle,db_map,signal_root):
        if data == None:
            self.emit(signal_root + '-delete',([handle],))
            db_map.delete(handle,txn=self.txn)
        else:
            ex_data = db_map.get(handle,txn=self.txn)
            if ex_data:
                signal = signal_root + '-update'
            else:
                signal = signal_root + '-add'
            db_map.put(handle,data,txn=self.txn)
            self.emit(signal,([handle],))

    def gramps_upgrade(self,callback=None):
        UpdateCallback.__init__(self,callback)
        
        child_rel_notrans = [
            "None",      "Birth",  "Adopted", "Stepchild",
            "Sponsored", "Foster", "Unknown", "Other", ]
        
        version = self.metadata.get('version',default=_MINVERSION)

        t = time.time()
#        if version < 13:
#            self.gramps_upgrade_13()
        print "Upgrade time:", int(time.time()-t), "seconds"
            

class BdbTransaction(Transaction):
    def __init__(self,msg,db,batch=False,no_magic=False):
        Transaction.__init__(self,msg,db,batch,no_magic)
        self.reference_del = []
        self.reference_add = []

def _mkname(path, name):
    return os.path.join(path, name + ".db")


if __name__ == "__main__":

    import sys
    
    d = GrampsDBDir()
    d.load(sys.argv[1],lambda x: x)

    c = d.get_person_cursor()
    data = c.first()
    while data:
        person = Person(data[1])
        print data[0], person.get_primary_name().get_name(),
        data = c.next()
    c.close()

    print d.surnames.keys()
