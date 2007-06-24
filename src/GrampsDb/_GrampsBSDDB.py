#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
Provides the Berkeley DB (BSDDB) database backend for GRAMPS
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
import const
import Errors
from BasicUtils import UpdateCallback

_MINVERSION = 5
_DBVERSION = 12

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

class GrampsBSDDBCursor(GrampsCursor):

    def __init__(self,source,txn=None):
        self.cursor = source.db.cursor(txn)
        
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

class GrampsBSDDBAssocCursor(GrampsCursor):

    def __init__(self,source,txn=None):
        self.cursor = source.cursor(txn)
        
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

class GrampsBSDDBDupCursor(GrampsBSDDBAssocCursor):
    """Cursor that includes handling for duplicate keys"""

    def set(self,key):
        return self.cursor.set(str(key))

    def next_dup(self):
        return self.cursor.next_dup()


#-------------------------------------------------------------------------
#
# GrampsBSDDB
#
#-------------------------------------------------------------------------
class GrampsBSDDB(GrampsDbBase,UpdateCallback):
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
            return db.DB_CREATE|db.DB_AUTO_COMMIT
        else:
            return db.DB_CREATE

    def open_table(self,file_name,table_name,dbtype=db.DB_HASH):
        dbmap = dbshelve.DBShelf(self.env)
        dbmap.db.set_pagesize(16384)
        if self.readonly:
            dbmap.open(file_name, table_name, dbtype, db.DB_RDONLY)
        else:
            dbmap.open(file_name, table_name, dbtype, self.open_flags(), 0666)
        return dbmap

    def _all_handles(self,table):
        return table.keys(self.txn)
    
    def get_person_cursor(self):
        return GrampsBSDDBCursor(self.person_map,self.txn)

    def get_family_cursor(self):
        return GrampsBSDDBCursor(self.family_map,self.txn)

    def get_event_cursor(self):
        return GrampsBSDDBCursor(self.event_map,self.txn)

    def get_place_cursor(self):
        return GrampsBSDDBCursor(self.place_map,self.txn)

    def get_source_cursor(self):
        return GrampsBSDDBCursor(self.source_map,self.txn)

    def get_media_cursor(self):
        return GrampsBSDDBCursor(self.media_map,self.txn)

    def get_repository_cursor(self):
        return GrampsBSDDBCursor(self.repository_map,self.txn)

    def has_person_handle(self,handle):
        """
        returns True if the handle exists in the current Person database.
        """
        return self.person_map.get(str(handle),txn=self.txn) != None

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
        return self.repository_map.get(str(handle),txn=self.txn) != None

    def has_event_handle(self,handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return self.event_map.get(str(handle),txn=self.txn) != None

    def has_place_handle(self,handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return self.place_map.get(str(handle),txn=self.txn) != None

    def has_source_handle(self,handle):
        """
        returns True if the handle exists in the current Repository database.
        """
        return self.source_map.get(str(handle),txn=self.txn) != None

    def get_raw_person_data(self,handle):
        return self.person_map.get(str(handle),txn=self.txn)

    def get_raw_family_data(self,handle):
        return self.family_map.get(str(handle),txn=self.txn)

    def get_raw_object_data(self,handle):
        return self.media_map.get(str(handle),txn=self.txn)

    def get_raw_place_data(self,handle):
        return self.place_map.get(str(handle),txn=self.txn)

    def get_raw_event_data(self,handle):
        return self.event_map.get(str(handle),txn=self.txn)

    def get_raw_source_data(self,handle):
        return self.source_map.get(str(handle),txn=self.txn)

    def get_raw_repository_data(self,handle):
        return self.repository_map.get(str(handle),txn=self.txn)

    # cursors for lookups in the reference_map for back reference
    # lookups. The reference_map has three indexes:
    # the main index: a tuple of (primary_handle,referenced_handle)
    # the primary_handle index: the primary_handle
    # the referenced_handle index: the referenced_handle
    # the main index is unique, the others allow duplicate entries.

    def get_reference_map_cursor(self):
        return GrampsBSDDBAssocCursor(self.reference_map,self.txn)

    def get_reference_map_primary_cursor(self):
        return GrampsBSDDBDupCursor(self.reference_map_primary_map,self.txn)

    def get_reference_map_referenced_cursor(self):
        return GrampsBSDDBDupCursor(self.reference_map_referenced_map,self.txn)

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
            self.metadata.put('default',str(handle),txn=the_txn)
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
            self.metadata.put('default',None,txn=the_txn)
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
            self.metadata.put(name,col_list,txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            else:
                self.metadata.sync()

    def version_supported(self):
        dbversion = self.metadata.get('version',default=0)
        print dbversion
        return ((dbversion <= _DBVERSION) and (dbversion >= _MINVERSION))
    
    def need_upgrade(self):
        dbversion = self.metadata.get('version',default=0)
        return not self.readonly and dbversion < _DBVERSION

    def load(self,name,callback,mode="w"):
        if self.db_is_open:
            self.close()

        self.readonly = mode == "r"
        if self.readonly:
            self.UseTXN = False

        callback(12)

        self.full_name = os.path.abspath(name)
        self.brief_name = os.path.basename(name)

        self.env = db.DBEnv()
        self.env.set_cachesize(0,0x2000000)         # 16MB

        if self.UseTXN:
            # These env settings are only needed for Txn environment
            self.env.set_lk_max_locks(25000)
            self.env.set_lk_max_objects(25000)
            self.env.set_flags(db.DB_LOG_AUTOREMOVE,1)  # clean up unused logs

            # The DB_PRIVATE flag must go if we ever move to multi-user setup
            env_flags = db.DB_CREATE|db.DB_PRIVATE|\
                        db.DB_INIT_MPOOL|db.DB_INIT_LOCK|\
                        db.DB_INIT_LOG|db.DB_INIT_TXN|db.DB_THREAD
            # Only do recovery for existing databases
            if os.path.isfile(self.full_name):
                env_flags = env_flags | db.DB_RECOVER

            # Environment name is now based on the filename
            drive, tmp_name = os.path.splitdrive(self.full_name)
            tmp_name = tmp_name.lstrip(os.sep)
            env_name = os.path.join(os.path.expanduser(const.env_dir),
                                    tmp_name)

            # Create the env dir if it does not exist
            if not os.path.isdir(env_name):
                os.makedirs(env_name)
                # If this is not a new db, see about copying old env dir
                if os.path.isfile(self.full_name):
                    common_env_name = os.path.expanduser(const.bsddbenv_dir)
                    # Copy the old env dir contents into the new one
                    # ONLY if the old env dir exists
                    if os.path.isdir(common_env_name):
                        shutil.rmtree(env_name)
                        shutil.copytree(common_env_name,env_name)
            else:
                # For existing env and new database, clean the env
                # (means the env dir remains from previous db
                # with the same name)
                if not os.path.isfile(self.full_name):
                    shutil.rmtree(env_name)
                    os.mkdir(env_name)

        else:
            env_flags = db.DB_CREATE|db.DB_PRIVATE|db.DB_INIT_MPOOL
            env_name = os.path.expanduser('~')

        self.env.open(env_name,env_flags)
        if self.UseTXN:
            self.env.txn_checkpoint()

        callback(25)
        self.metadata     = self.open_table(self.full_name,"meta")

        # If we cannot work with this DB version,
        # it makes no sense to go further
        if not self.version_supported():
            self._close_early()

        self.family_map     = self.open_table(self.full_name, "family")
        self.place_map      = self.open_table(self.full_name, "places")
        self.source_map     = self.open_table(self.full_name, "sources")
        self.media_map      = self.open_table(self.full_name, "media")
        self.event_map      = self.open_table(self.full_name, "events")
        self.person_map     = self.open_table(self.full_name, "person")
        self.repository_map = self.open_table(self.full_name, "repository")
        self.reference_map  = self.open_table(self.full_name, "reference_map",
                                              dbtype=db.DB_BTREE)
        callback(37)

        self._load_metadata()

        gstats = self.metadata.get('gender_stats',default=None)

        if not self.readonly:
            if self.UseTXN:
                # Start transaction if needed
                the_txn = self.env.txn_begin()
            else:
                the_txn = None

            if gstats == None:
                # New database. Set up the current version.
                self.metadata.put('version',_DBVERSION,txn=the_txn)
            elif not self.metadata.has_key('version'):
                # Not new database, but the version is missing.
                # Use 0, but it is likely to fail anyway.
                self.metadata.put('version',0,txn=the_txn)

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
        self.name_formats = self.metadata.get('name_formats',default=[])
        # upgrade formats if they were saved in the old way
        for format_ix in range(len(self.name_formats)):
            format = self.name_formats[format_ix]
            if len(format) == 3:
                format = format + (True,)
                self.name_formats[format_ix] = format
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
        self.source_media_types = set(self.metadata.get('sm_types',
                                                        default=[]))
        self.url_types = set(self.metadata.get('url_types',default=[]))
        self.media_attributes = set(self.metadata.get('mattr_names',
                                                      default=[]))
        # surname list
        self.surname_list = self.metadata.get('surname_list',default=[])

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
        self.surnames.set_flags(db.DB_DUP|db.DB_DUPSORT)
        self.surnames.open(self.full_name, "surnames", db.DB_BTREE,
                           flags=table_flags)

        self.name_group = db.DB(self.env)
        self.name_group.set_flags(db.DB_DUP)
        self.name_group.open(self.full_name, "name_group",
                             db.DB_HASH, flags=table_flags)

        self.id_trans = db.DB(self.env)
        self.id_trans.set_flags(db.DB_DUP)
        self.id_trans.open(self.full_name, "idtrans",
                           db.DB_HASH, flags=table_flags)

        self.fid_trans = db.DB(self.env)
        self.fid_trans.set_flags(db.DB_DUP)
        self.fid_trans.open(self.full_name, "fidtrans",
                            db.DB_HASH, flags=table_flags)

        self.eid_trans = db.DB(self.env)
        self.eid_trans.set_flags(db.DB_DUP)
        self.eid_trans.open(self.full_name, "eidtrans",
                            db.DB_HASH, flags=table_flags)

        self.pid_trans = db.DB(self.env)
        self.pid_trans.set_flags(db.DB_DUP)
        self.pid_trans.open(self.full_name, "pidtrans",
                            db.DB_HASH, flags=table_flags)

        self.sid_trans = db.DB(self.env)
        self.sid_trans.set_flags(db.DB_DUP)
        self.sid_trans.open(self.full_name, "sidtrans",
                            db.DB_HASH, flags=table_flags)

        self.oid_trans = db.DB(self.env)
        self.oid_trans.set_flags(db.DB_DUP)
        self.oid_trans.open(self.full_name, "oidtrans",
                            db.DB_HASH, flags=table_flags)

        self.rid_trans = db.DB(self.env)
        self.rid_trans.set_flags(db.DB_DUP)
        self.rid_trans.open(self.full_name, "ridtrans",
                            db.DB_HASH, flags=table_flags)

        self.reference_map_primary_map = db.DB(self.env)
        self.reference_map_primary_map.set_flags(db.DB_DUP)
        self.reference_map_primary_map.open(self.full_name,
                                            "reference_map_primary_map",
                                            db.DB_BTREE, flags=table_flags)

        self.reference_map_referenced_map = db.DB(self.env)
        self.reference_map_referenced_map.set_flags(db.DB_DUP|db.DB_DUPSORT)
        self.reference_map_referenced_map.open(self.full_name,
                                               "reference_map_referenced_map",
                                               db.DB_BTREE, flags=table_flags)

        if not self.readonly:
            self.person_map.associate(self.surnames, find_surname, table_flags)
            self.person_map.associate(self.id_trans, find_idmap, table_flags)
            self.family_map.associate(self.fid_trans,find_idmap, table_flags)
            self.event_map.associate(self.eid_trans, find_idmap,  table_flags)
            self.repository_map.associate(self.rid_trans, find_idmap,
                                          table_flags)
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


    def rebuild_secondary(self,callback):
        if self.readonly:
            return

        table_flags = self.open_flags()

        # remove existing secondary indices
        self.id_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"idtrans")
        callback(1)

        self.surnames.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"surnames")
        callback(2)

        # Repair secondary indices related to family_map
        self.fid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"fidtrans")
        callback(3)

        # Repair secondary indices related to place_map
        self.pid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"pidtrans")
        callback(4)

        # Repair secondary indices related to media_map
        self.oid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"oidtrans")
        callback(5)

        # Repair secondary indices related to source_map
        self.sid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"sidtrans")
        callback(6)

        # Repair secondary indices related to event_map
        self.eid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"eidtrans")
        callback(7)

        # Repair secondary indices related to repository_map
        self.rid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"ridtrans")
        callback(8)

        # Repair secondary indices related to reference_map
        self.reference_map_primary_map.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"reference_map_primary_map")
        callback(9)

        self.reference_map_referenced_map.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"reference_map_referenced_map")
        callback(10)

        # Set flag saying that we have removed secondary indices
        # and then call the creating routine
        self.secondary_connected = False
        self.connect_secondary()
        callback(11)

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
        junk.remove(self.full_name,"reference_map_referenced_map")
        callback(1)

        self.reference_map_primary_map.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"reference_map_primary_map")
        callback(2)

        self.reference_map.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"reference_map")
        callback(3)

        # Open reference_map and primapry map
        self.reference_map  = self.open_table(self.full_name, "reference_map",
                                              dbtype=db.DB_BTREE)
        
        open_flags = self.open_flags()
        self.reference_map_primary_map = db.DB(self.env)
        self.reference_map_primary_map.set_flags(db.DB_DUP)
        self.reference_map_primary_map.open(self.full_name,
                                            "reference_map_primary_map",
                                            db.DB_BTREE, flags=open_flags)
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
            self.full_name,"reference_map_referenced_map",
            db.DB_BTREE,flags=open_flags)
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
        raise Errors.FileVersionError(
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
        If no such MediaObject exists, None is returned.
        """
        return self._get_obj_from_gramps_id(val,self.rid_trans,Repository,
                                            self.repository_map)

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

    def _do_commit(self,add_list,db_map):
        retlist = []
        for (handle,data) in add_list:
            db_map.put(handle,data,self.txn)
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
                junk.remove(self.full_name,"surnames")

                self.reference_map_referenced_map.close()
                junk = db.DB(self.env)
                junk.remove(self.full_name,"reference_map_referenced_map")
            
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
                self.surnames.open(self.full_name,"surnames",
                                   db.DB_BTREE,flags=open_flags)
                self.person_map.associate(self.surnames,find_surname,
                                          open_flags)
            
                self.reference_map_referenced_map = db.DB(self.env)
                self.reference_map_referenced_map.set_flags(dupe_flags)
                self.reference_map_referenced_map.open(
                    self.full_name,"reference_map_referenced_map",
                    db.DB_BTREE,flags=open_flags)
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
        if self.UseTXN and self.txn:
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
        if version < 6:
            self.gramps_upgrade_6()
        if version < 7:
            self.gramps_upgrade_7()
        if version < 8:
            self.gramps_upgrade_8()
        if version < 9:
            self.gramps_upgrade_9()
        else:
            if version < 10:
                self.gramps_upgrade_10()
            if version < 11:
                self.gramps_upgrade_11()
            if version < 12:
                self.gramps_upgrade_12()
        print "Upgrade time:", int(time.time()-t), "seconds"

    def gramps_upgrade_6(self):
        print "Upgrading to DB version 6"
        order = []
        for val in self.get_media_column_order():
            if val[1] != 6:
                order.append(val)
        self.set_media_column_order(order)
        if self.UseTXN:
            # Start transaction if needed
            the_txn = self.env.txn_begin()
        else:
            the_txn = None
        self.metadata.put('version',6,txn=the_txn)
        if self.UseTXN:
            the_txn.commit()
        else:
            self.metadata.sync()

    def gramps_upgrade_7(self):
        print "Upgrading to DB version 7"

        self.genderStats = GenderStats()
        cursor = self.get_person_cursor()
        data = cursor.first()
        while data:
            handle,val = data
            p = Person(val)
            self.genderStats.count_person(p)
            data = cursor.next()
        cursor.close()
        if self.UseTXN:
            # Start transaction if needed
            the_txn = self.env.txn_begin()
        else:
            the_txn = None
        self.metadata.put('version',7,txn=the_txn)
        if self.UseTXN:
            the_txn.commit()
        else:
            self.metadata.sync()

    def gramps_upgrade_8(self):
        print "Upgrading to DB version 8"
        cursor = self.get_person_cursor()
        data = cursor.first()
        while data:
            handle,val = data
            handle_list = val[8]
            if type(handle_list) == list:
            # Check to prevent crash on corrupted data (event_list=None)
                for handle in handle_list:
                    event = self.get_event_from_handle(handle)
                    self.individual_event_names.add(event.name)
            data = cursor.next()
        cursor.close()

        cursor = self.get_family_cursor()
        data = cursor.first()
        while data:
            handle,val = data
            handle_list = val[6]
            if type(handle_list) == list:
            # Check to prevent crash on corrupted data (event_list=None)
                for handle in handle_list:
                    event = self.get_event_from_handle(handle)
                    self.family_event_names.add(event.name)
            data = cursor.next()
        cursor.close()
        if self.UseTXN:
            # Start transaction if needed
            the_txn = self.env.txn_begin()
        else:
            the_txn = None
        self.metadata.put('version',8,txn=the_txn)
        if self.UseTXN:
            the_txn.commit()
        else:
            self.metadata.sync()

    def gramps_upgrade_9(self):
        """
        This is the PIVOTAL upgrade point. Before this, things were
        stored as pickled class and attribute names. After this, things
        are stored as builtin Python objects: every class serializes
        its members recursively, up until everything is in terms of builtins.
        So we have tuples with numbers, strings, and tuples, etc.

        Because of this, every subsequent upgrade must also be included
        into this routine. Otherwise this routine will fail when trying
        to commit the objects, because the unpickled objects will lack
        some attributes that are necessary for serialization on commit.
        """
        print "Upgrading to DB version 12 -- this may take a while"
        # The very very first thing is to check for duplicates in the
        # primary tables and remove them. 
        self.set_total(7)
        status,length = low_level_9(self,self.update)
        self.reset()

        self.set_total(length)

        # Remove column metadata, since columns have changed.
        # This will reset all columns to defaults
        for name in (PERSON_COL_KEY,CHILD_COL_KEY,PLACE_COL_KEY,SOURCE_COL_KEY,
                     MEDIA_COL_KEY,EVENT_COL_KEY,FAMILY_COL_KEY):
            try:
                if self.UseTXN:
                    # Start transaction if needed
                    the_txn = self.env.txn_begin()
                else:
                    the_txn = None
                self.metadata.delete(name,txn=the_txn)
                if self.UseTXN:
                    the_txn.commit()
                else:
                    self.metadata.sync()
            except KeyError:
                if self.UseTXN:
                    the_txn.abort()

        # Then we remove the surname secondary index table
        # because its format changed from HASH to DUPSORTed BTREE.
        junk = db.DB(self.env)
        junk.remove(self.full_name,"surnames")

        # Create one secondary index for reference_map
        # because every commit will require this to exist
        table_flags = self.open_flags()
        self.reference_map_primary_map = db.DB(self.env)
        self.reference_map_primary_map.set_flags(db.DB_DUP)
        self.reference_map_primary_map.open(self.full_name,
                                            "reference_map_primary_map",
                                            db.DB_BTREE, flags=table_flags)
        self.reference_map.associate(self.reference_map_primary_map,
                                     find_primary_handle,
                                     table_flags)

        ### Now we're ready to proceed with the normal upgrade.
        # First, make sure the stored default person handle is str, not unicode
        try:
            if self.UseTXN:
                # Start transaction if needed
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            handle = self.metadata.get('default',txn=the_txn)
            self.metadata.put('default',str(handle),txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            else:
                self.metadata.sync()
        except KeyError:
            # default person was not stored in database
            if self.UseTXN:
                the_txn.abort()

        # The rest of the upgrade deals with real data, not metadata
        # so starting (batch) transaction here.
        trans = self.transaction_begin("",True)

        # Numerous changes were made between dbversions 8 and 9.
        # If nothing else, we switched from storing pickled gramps classes
        # to storing builtin objects, via running serialize() recursively
        # until the very bottom.
        # Every stored object needs to be re-committed here.

        # Change every Source to have reporef_list
        for handle in self.source_map.keys():
            info = self.source_map[handle]        
            source = Source()
            source.handle = handle
            # We already have a new Source object with the reporef_list
            # just fill in the rest of the fields for this source
            (junk_handle, source.gramps_id, source.title, source.author,
             source.pubinfo, source.note, source.media_list,
             source.abbrev, source.change, source.datamap) = info

            # Cover attributes contained in MediaRefs
            for media_ref in source.media_list:
                convert_mediaref_9(media_ref)

            self.commit_source(source,trans)
            self.update()

        # Family upgrade
        for handle in self.family_map.keys():
            info = self.family_map[handle]
            family = Family()
            family.handle = handle
            # Restore data from dbversion 8 (gramps 2.0.9)
            (junk_handle, family.gramps_id, family.father_handle,
             family.mother_handle, child_list, the_type,
             event_list, family.media_list, family.attribute_list,
             lds_seal, complete, family.source_list,
             family.note, family.change) = info

            if complete:
                family.marker.set(MarkerType.COMPLETE)
                
            # Change every event handle to the EventRef
            for event_handle in event_list:
                event_ref = EventRef()
                event_ref.ref = event_handle
                event_ref.role.set(EventRoleType.FAMILY)
                family.event_ref_list.append(event_ref)

            # Change child_list into child_ref_list
            for child_handle in child_list:
                child_ref = ChildRef()
                child_ref.ref = child_handle
                family.child_ref_list.append(child_ref)

            # Change relationship type from int to tuple
            family.type.set(the_type)

            # In all Attributes, convert type from string to a tuple
            for attribute in family.attribute_list:
                convert_attribute_9(attribute)

            # Cover attributes contained in MediaRefs
            for media_ref in family.media_list:
                convert_mediaref_9(media_ref)
            
            # Switch from fixed lds ords to a list
            if lds_seal:
                lds_seal.type = LdsOrd.SEAL_TO_SPOUSE
                lds_seal.private = False
                lds_seal.status = lds_seal_spouse_dict_9[lds_seal.status]
                family.lds_ord_list = [lds_seal]

            self.commit_family(family,trans)
            self.update()

        # Person upgrade
        # Needs to be run after the family upgrade completed.
        def_rel = ChildRefType._DEFAULT
        for handle in self.person_map.keys():
            info = self.person_map[handle]
            person = Person()
            person.handle = handle
            # Restore data from dbversion 8 (gramps 2.0.9--2.0.11)
            (junk_handle, person.gramps_id, person.gender,
             person.primary_name, person.alternate_names, nickname,
             death_handle, birth_handle, event_list,
             person.family_list, parent_family_list,
             person.media_list, person.address_list, person.attribute_list,
             person.urls, lds_bapt, lds_endow, lds_seal,
             complete, person.source_list, person.note,
             person.change, person.private) = (info + (False,))[0:23]

            # Convert complete flag into marker
            if complete:
                person.marker.set(MarkerType.COMPLETE)
            
            # Change every event handle to the EventRef
            if birth_handle:
                event_ref = EventRef()
                event_ref.ref = birth_handle
                person.event_ref_list.append(event_ref)
                person.birth_ref_index = len(person.event_ref_list) - 1

            if death_handle:
                event_ref = EventRef()
                event_ref.ref = death_handle
                person.event_ref_list.append(event_ref)
                person.death_ref_index = len(person.event_ref_list) - 1

            for event_handle in event_list:
                event_ref = EventRef()
                event_ref.ref = event_handle
                person.event_ref_list.append(event_ref)

            # In all Name instances, convert type from string to a tuple
            for name in [person.primary_name] + person.alternate_names:
                old_type = name.type
                new_type = NameType()
                # Mapping "Other Name" from gramps 2.0.x to Unknown
                if old_type == 'Other Name':
                    new_type.set(NameType.UNKNOWN)
                else:
                    new_type.set_from_xml_str(old_type)
                name.type = new_type
                name.call = ''

            # Change parent_family_list into list of handles
            # and transfer the relationship info into the family's
            # child_ref (in family.child_ref_list) as tuples.
            for (family_handle,mrel,frel) in parent_family_list:
                person.parent_family_list.append(family_handle)
                # Only change family is the relations are non-default
                if (mrel,frel) != (def_rel,def_rel):
                    family = self.get_family_from_handle(family_handle)
                    child_handle_list = [ref.ref for ref in
                                         family.child_ref_list]
                    index = child_handle_list.index(person.handle)
                    child_ref = family.child_ref_list[index]
                    child_ref.frel.set(frel)
                    child_ref.mrel.set(mrel)
                    self.commit_family(family,trans)

            # In all Attributes, convert type from string to a tuple
            for attribute in person.attribute_list:
                convert_attribute_9(attribute)

            # Nickname becomes an attribute
            if nickname.strip():
                attr = Attribute()
                attr.set_type(AttributeType.NICKNAME)
                attr.set_value(nickname)
                person.attribute_list.append(attr)

            # Cover attributes contained in MediaRefs
            for media_ref in person.media_list:
                convert_mediaref_9(media_ref)

            # In all Urls, add type attribute
            for url in person.urls:
                convert_url_9(url)

            # Switch from fixed lds ords to a list
            if lds_bapt:
                lds_bapt.type = LdsOrd.BAPTISM
                lds_bapt.status = lds_bapt_dict_9[lds_bapt.status]
                person.lds_ord_list.append(lds_bapt)
            if lds_endow:
                lds_endow.type = LdsOrd.ENDOWMENT
                lds_endow.status = lds_bapt_dict_9[lds_endow.status]
                person.lds_ord_list.append(lds_endow)
            if lds_seal:
                lds_seal.type = LdsOrd.SEAL_TO_PARENTS
                lds_seal.status = lds_seal_parent_dict_9[lds_seal.status]
                person.lds_ord_list.append(lds_seal)
            # Old lds ords did not have private attribute
            for item in person.lds_ord_list:
                item.private = False

            # Upgrade addresses: this is an upgrade_11 step
            for addr in person.address_list:
                addr.county = u''
            
            self.commit_person(person,trans)
            self.update()

        # Event upgrade
        # Turns out that a lof ot events have duplicate gramps IDs
        # We need to fix this. For some reason secondary index gets confused
        # so we resolve duplicate IDs manually.
        # First a quick pass via the cursor to get a list of event ids
        eid_list = []
        cursor = self.get_event_cursor()
        data = cursor.first()
        while data:
            handle,val = data
            eid_list.append(val[1])
            data = cursor.next()
        cursor.close()

        # Find the largest ID and extract the integer:
        # We can do this because in 2.0.x the event id is never exposed
        eid_list.sort()
        if len(eid_list) == 0:
            max_id_number = 0
        else:
            last_id = eid_list[-1]
            nre = re.compile("\D+(\d+)")
            max_id_number = int(nre.match(last_id).groups()[0])

        # get the list of all IDs that are non-unique
        dup_ids = [eid for eid in eid_list if eid_list.count(eid) > 1 ]
        
        for handle in self.event_map.keys():
            info = self.event_map[handle]        
            event = Event()
            event.handle = handle
            (junk_handle, event.gramps_id, old_type, event.date,
             event.description, event.place, cause, event.private,
             event.source_list, event.note, witness_list,
             event.media_list, event.change) = info

            # Change ID if it is non-unique
            if event.gramps_id in dup_ids:
                max_id_number += 1
                event.gramps_id = self.eprefix % max_id_number

            # Convert old string-based type to GrampsType
            event.type.set_from_xml_str(old_type)
            
            # Cover attributes contained in MediaRefs
            for media_ref in event.media_list:
                convert_mediaref_9(media_ref)

            # Upgrade witness -- no more Witness class
            if type(witness_list) != list:
                witness_list = []
            for witness in witness_list:
                if witness.type == 0:     # witness name recorded
                    # Add name and comment to the event note
                    note_text = event.get_note() + "\n" + \
                                _("Witness name: %s") % witness.val
                    if witness.comment:
                        note_text += "\n" + _("Witness comment: %s") \
                                     % witness.comment
                    event.set_note(note_text)
                elif witness.type == 1:   # witness ID recorded
                    person = self.get_person_from_handle(witness.val)
                    if person:
                        # Add an EventRef from that person
                        # to this event using ROLE_WITNESS role
                        event_ref = EventRef()
                        event_ref.ref = event.handle
                        event_ref.role.set(EventRoleType.WITNESS)
                        # Add privacy and comment
                        event_ref.private = witness.private
                        if witness.comment:
                            event_ref.set_note(witness.comment)
                        person.event_ref_list.append(event_ref)
                        self.commit_person(person,trans)
                    else:
                        # Broken witness: dangling witness handle
                        # with no corresponding person in the db
                        note_text = event.get_note() + "\n" + \
                                    _("Broken witness reference detected "
                                      "while upgrading database to version 9.")
                        event.set_note(note_text)

            # This is an upgrade_10 step
            if cause.strip():
                attr = Attribute()
                attr.set_type(AttributeType.CAUSE)
                attr.set_value(cause)
                event.add_attribute(attr)

            self.commit_event(event,trans)
            self.update()
        
        # Place upgrade
        for handle in self.place_map.keys():
            info = self.place_map[handle]        
            place = Place()
            place.handle = handle
            (junk_handle, place.gramps_id, place.title, place.long, place.lat,
             place.main_loc, place.alt_loc, place.urls, place.media_list,
             place.source_list, place.note, place.change) = info

            # Cover attributes contained in MediaRefs
            for media_ref in place.media_list:
                convert_mediaref_9(media_ref)

            # In all Urls, add type attribute
            for url in place.urls:
                convert_url_9(url)

            # Upgrade locations: this is an upgrade_11 step
            if place.main_loc:
                place.main_loc.street = u''           
            for l in place.alt_loc:
                l.street = u''

            self.commit_place(place,trans)
            self.update()

        # Media upgrade
        for handle in self.media_map.keys():
            info = self.media_map[handle]        
            media_object = MediaObject()
            media_object.handle = handle
            (junk_handle, media_object.gramps_id, media_object.path,
             media_object.mime, media_object.desc, media_object.attribute_list,
             media_object.source_list, media_object.note, media_object.change,
             media_object.date) = info

            # In all Attributes, convert type from string to a tuple
            for attribute in media_object.attribute_list:
                convert_attribute_9(attribute)

            self.commit_media_object(media_object,trans)
            self.update()

        self.transaction_commit(trans,"Upgrade to DB version 12")
        # Close secodnary index
        self.reference_map_primary_map.close()

        if self.UseTXN:
            # Separate transaction to save metadata
            the_txn = self.env.txn_begin()
        else:
            the_txn = None
        self.metadata.put('version',12,txn=the_txn)
        if self.UseTXN:
            the_txn.commit()
        else:
            self.metadata.sync()

        print "Done upgrading to DB version 12"

    def gramps_upgrade_10(self):
        print "Upgrading to DB version 10..."

        # Remove event column metadata, since columns have changed.
        # This will reset all columns to defaults in event view
        for name in (PERSON_COL_KEY,EVENT_COL_KEY):
            try:
                if self.UseTXN:
                    # Start transaction if needed
                    the_txn = self.env.txn_begin()
                else:
                    the_txn = None
                self.metadata.delete(name,txn=the_txn)
                if self.UseTXN:
                    the_txn.commit()
                else:
                    self.metadata.sync()
            except KeyError:
                if self.UseTXN:
                    the_txn.abort()

        # This upgrade adds attribute lists to Event and EventRef objects
        length = self.get_number_of_events() + len(self.person_map) \
                 + self.get_number_of_families()
        self.set_total(length)

        for handle in self.event_map.keys():
            info = self.event_map[handle]

            (junk_handle, gramps_id, the_type, date,description,
             place, cause,source_list, note, media_list,
             change, marker, private) = info

            # Cause is removed, so we're converting it into an attribute
            if cause.strip():
                attr = Attribute()
                attr.set_type(AttributeType.CAUSE)
                attr.set_value(cause)
                attr_list = [attr.serialize()]
            else:
                attr_list = []

            info = (handle, gramps_id, the_type, date,
                    description, place, source_list, note, media_list,
                    attr_list, change, marker, private)

            if self.UseTXN:
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self.event_map.put(str(handle),info,txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            self.update()

        if not self.UseTXN:
            self.event_map.sync()

        # Personal event references
        for handle in self.person_map.keys():
            info = self.person_map[handle]

            (junk_handle,gramps_id,gender,
             primary_name,alternate_names,death_ref_index,
             birth_ref_index,event_ref_list,family_list,
             parent_family_list,media_list,address_list,attribute_list,
             urls,lds_ord_list,source_list,note,change,marker,
             private,person_ref_list,) = info

            # Names lost the "sname" attribute
            new_primary_name = convert_name_10(primary_name)
            new_alternate_names = [convert_name_10(name)
                                   for name in alternate_names]

            # Events gained attribute_list
            new_event_ref_list = [
                (privacy,note,[],ref,role)
                for (privacy,note,ref,role) in event_ref_list]

            info = (handle,gramps_id,gender,new_primary_name,
                    new_alternate_names,
                    death_ref_index,birth_ref_index,new_event_ref_list,
                    family_list,parent_family_list,media_list,address_list,
                    attribute_list,urls,lds_ord_list,source_list,note,
                    change,marker,private,person_ref_list,)

            if self.UseTXN:
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self.person_map.put(str(handle),info,txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            self.update()

        if not self.UseTXN:
            self.person_map.sync()

        # Family event references
        for handle in self.family_map.keys():
            info = self.family_map[handle]

            (junk_handle,gramps_id,father_handle,
             mother_handle,child_ref_list,the_type,event_ref_list,
             media_list,attribute_list,lds_seal_list,source_list,note,
             change, marker, private) = info

            new_event_ref_list = [
                (privacy,note,[],ref,role)
                for (privacy,note,ref,role) in event_ref_list]

            info = (handle,gramps_id,father_handle,
                        mother_handle,child_ref_list,the_type,
                        new_event_ref_list,
                        media_list,attribute_list,lds_seal_list,
                        source_list,note,change, marker, private)

            if self.UseTXN:
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self.family_map.put(str(handle),info,txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            self.update()
        if not self.UseTXN:
            self.family_map.sync()

        self.reset()

        if self.UseTXN:
            # Separate transaction to save metadata
            the_txn = self.env.txn_begin()
        else:
            the_txn = None
        self.metadata.put('version',10,txn=the_txn)
        if self.UseTXN:
            the_txn.commit()
        else:
            self.metadata.sync()

        print "Done upgrading to DB version 10"

    def gramps_upgrade_11(self):
        print "Upgrading to DB version 11..."

        # This upgrade modifies addresses and locations
        length = len(self.person_map) + len(self.place_map) \
                 + len(self.repository_map)
        self.set_total(length)

        # Personal addresses
        for handle in self.person_map.keys():
            info = self.person_map[handle]

            (junk_handle,gramps_id,gender,
             primary_name,alternate_names,death_ref_index,
             birth_ref_index,event_ref_list,family_list,
             parent_family_list,media_list,address_list,attribute_list,
             urls,lds_ord_list,source_list,note,change,marker,
             private,person_ref_list,) = info

            new_address_list = [convert_address_11(addr)
                                for addr in address_list]

            info = (handle,gramps_id,gender,
                    primary_name,alternate_names,death_ref_index,
                    birth_ref_index,event_ref_list,family_list,
                    parent_family_list,media_list,new_address_list,
                    attribute_list,
                    urls,lds_ord_list,source_list,note,change,marker,
                    private,person_ref_list,)

            if self.UseTXN:
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self.person_map.put(str(handle),info,txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            self.update()

        if not self.UseTXN:
            self.person_map.sync()
        
        # Repositories
        for handle in self.repository_map.keys():
            info = self.repository_map[handle]

            (junk_handle, gramps_id, the_type, name, note,
             address_list, urls, marker, private) = info

            new_address_list = [convert_address_11(addr)
                                for addr in address_list]

            info = (handle, gramps_id, the_type, name, note,
                    new_address_list, urls, marker, private)

            if self.UseTXN:
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self.repository_map.put(str(handle),info,txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            self.update()

        if not self.UseTXN:
            self.repository_map.sync()

        # Places
        for handle in self.place_map.keys():
            info = self.place_map[handle]

            (junk_handle, gramps_id, title, long, lat, main_loc, alt_loc, urls,
             media_list, source_list, note, change, marker, private) = info

            if main_loc:
                main_loc = convert_location_11(main_loc)

            new_alt_loc = [convert_location_11(loc) for loc in alt_loc]

            info = (handle,gramps_id,title,long,lat,main_loc,new_alt_loc,urls,
                    media_list, source_list, note, change, marker, private)

            if self.UseTXN:
                the_txn = self.env.txn_begin()
            else:
                the_txn = None
            self.place_map.put(str(handle),info,txn=the_txn)
            if self.UseTXN:
                the_txn.commit()
            self.update()

        if not self.UseTXN:
            self.place_map.sync()

        self.reset()

        if self.UseTXN:
            # Separate transaction to save metadata
            the_txn = self.env.txn_begin()
        else:
            the_txn = None
        self.metadata.put('version', 11, txn=the_txn)
        if self.UseTXN:
            the_txn.commit()
        else:
            self.metadata.sync()

        print "Done upgrading to DB version 11"

    def gramps_upgrade_12(self):
        print "Upgrading to DB version 12..."
        # Hook up surnames 
        table_flags = self.open_flags()
        self.surnames = db.DB(self.env)
        self.surnames.set_flags(db.DB_DUP|db.DB_DUPSORT)
        self.surnames.open(self.full_name, "surnames", db.DB_BTREE,
                           flags=table_flags)
        self.person_map.associate(self.surnames, find_surname, table_flags)
        
        self.build_surname_list()

        # Close so that we can open it again later
        self.surnames.close()

        if self.UseTXN:
            # Separate transaction to save metadata
            the_txn = self.env.txn_begin()
        else:
            the_txn = None
        self.metadata.put('version', 12, txn=the_txn)
        if self.UseTXN:
            the_txn.commit()
        else:
            self.metadata.sync()

        print "Done upgrading to DB version 12"


class BdbTransaction(Transaction):
    def __init__(self,msg,db,batch=False,no_magic=False):
        Transaction.__init__(self,msg,db,batch,no_magic)
        self.reference_del = []
        self.reference_add = []

def convert_attribute_9(attribute):
    old_type = attribute.type
    new_type = AttributeType()
    new_type.set_from_xml_str(old_type)
    attribute.type = new_type

def convert_mediaref_9(media_ref):
    for attribute in media_ref.attribute_list:
        convert_attribute_9(attribute)

def convert_url_9(url):
    path = url.path.strip()
    if (path.find('mailto:') == 0) or (url.path.find('@') != -1):
        new_type = UrlType.EMAIL
    elif path.find('http://') == 0:
        new_type = UrlType.WEB_HOME
    elif path.find('ftp://') == 0:
        new_type = UrlType.WEB_FTP
    else:
        new_type = UrlType.CUSTOM
    url.type = UrlType(new_type)
    
lds_bapt_dict_9 = {
    0: LdsOrd.STATUS_NONE,
    1: LdsOrd.STATUS_CHILD,
    2: LdsOrd.STATUS_CLEARED,
    3: LdsOrd.STATUS_COMPLETED,
    4: LdsOrd.STATUS_INFANT,
    5: LdsOrd.STATUS_PRE_1970,
    6: LdsOrd.STATUS_QUALIFIED,
    7: LdsOrd.STATUS_STILLBORN,
    8: LdsOrd.STATUS_SUBMITTED,
    9: LdsOrd.STATUS_UNCLEARED,
    }

lds_seal_parent_dict_9 = {
    0: LdsOrd.STATUS_NONE,
    1: LdsOrd.STATUS_BIC,
    2: LdsOrd.STATUS_CLEARED,
    3: LdsOrd.STATUS_COMPLETED,
    4: LdsOrd.STATUS_DNS,
    5: LdsOrd.STATUS_PRE_1970,
    6: LdsOrd.STATUS_QUALIFIED,
    7: LdsOrd.STATUS_STILLBORN,
    8: LdsOrd.STATUS_SUBMITTED,
    9: LdsOrd.STATUS_UNCLEARED,
    }

lds_seal_spouse_dict_9 = {
    0: LdsOrd.STATUS_NONE,
    1: LdsOrd.STATUS_CANCELED,
    2: LdsOrd.STATUS_CLEARED,
    3: LdsOrd.STATUS_COMPLETED,
    4: LdsOrd.STATUS_DNS,
    5: LdsOrd.STATUS_PRE_1970,
    6: LdsOrd.STATUS_QUALIFIED,
    7: LdsOrd.STATUS_DNS_CAN,
    8: LdsOrd.STATUS_SUBMITTED,
    9: LdsOrd.STATUS_UNCLEARED,
    }

def low_level_9(the_db,update):
    """
    This is a low-level repair routine.

    It is fixing DB inconsistencies such as duplicates.
    Returns a (status,name) tuple.
    The boolean status indicates the success of the procedure.
    The name indicates the problematic table (empty if status is True).
    """
    the_length = 0
    for the_map in [('Person',the_db.person_map),
                    ('Family',the_db.family_map),
                    ('Event',the_db.event_map),
                    ('Place',the_db.place_map),
                    ('Source',the_db.source_map),
                    ('Media',the_db.media_map)]:

        # print "Low-level repair: table: %s" % the_map[0]
        status,length = _table_low_level_9(the_db.env,the_map[1])
        if update:
            update()
        if status:
            # print "Done."
            the_length += length
        else:
            print "Low-level repair: Problem with table: %s" % the_map[0]
            return (False,the_map[0])
    return (True,the_length)


def _table_low_level_9(env,table):
    """
    Low level repair for a given db table.
    """
    
    handle_list = table.keys()
    length = len(handle_list)
    dup_handles = set(
        [ handle for handle in handle_list if handle_list.count(handle) > 1 ]
        )

    if not dup_handles:
        # print "    No dupes found for this table"
        return (True,length)

    the_txn = env.txn_begin()
    table_cursor = GrampsBSDDBDupCursor(table,txn=the_txn)
    # Dirty hack to prevent records from unpickling by DBShelve
    table_cursor._extract = lambda rec: rec
    
    for handle in dup_handles:
        print "    Duplicates found for handle: %s" % handle
        try:
            ret = table_cursor.set(handle)
        except:
            print "    Failed setting initial cursor."
            table_cursor.close()
            the_txn.abort()
            return (False,None)

        for count in range(handle_list.count(handle)-1):
            try:
                table_cursor.delete()
                print "    Succesfully deleted dupe #%d" % (count+1)
            except:
                print "    Failed deleting dupe."
                table_cursor.close()
                the_txn.abort()
                return (False,None)

            try:
                ret = table_cursor.next_dup()
            except:
                print "    Failed moving the cursor."
                table_cursor.close()
                the_txn.abort()
                return (False,None)

    table_cursor.close()
    the_txn.commit()
    return (True,length)

def convert_name_10(name):
    # Names lost the "sname" attribute
    (privacy,source_list,note,date,first_name,surname,suffix,title,name_type,
     prefix,patronymic,sname,group_as,sort_as,display_as,call) = name
    return (privacy,source_list,note,date,first_name,surname,suffix,title,
            name_type,prefix,patronymic,group_as,sort_as,display_as,call)

def convert_address_11(addr):
    # addresses got location instead of city,...
    (privacy,source_list,note,date,
     city,state,country,postal,phone,street) = addr
    county = u''
    location_base = (street,city,county,state,country,postal,phone)
    return (privacy,source_list,note,date,location_base)

def convert_location_11(loc):
    (location_base,parish,county) = loc
    (city,state,country,postal,phone) = location_base
    street = u''
    new_location_base = (street,city,county,state,country,postal,phone)
    return (new_location_base,parish)

if __name__ == "__main__":

    import sys
    
    d = GrampsBSDDB()
    d.load(sys.argv[1],lambda x: x)

    c = d.get_person_cursor()
    data = c.first()
    while data:
        person = Person(data[1])
        print data[0], person.get_primary_name().get_name(),
        data = c.next()
    c.close()

    print d.surnames.keys()
