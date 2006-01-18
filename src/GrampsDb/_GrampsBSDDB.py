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
import cPickle
import os
import time
import locale
import sets
from gettext import gettext as _
from bsddb import dbshelve, db
import logging
log = logging.getLogger(".GrampsDb")

# hack to use native set for python2.4
# and module sets for earlier pythons
try:
    set()
except NameError:
    from sets import Set as set

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *
from _GrampsDbBase import *
import const

_MINVERSION = 5
_DBVERSION = 9

def find_surname(key,data):
    return str(data[3].get_surname())

def find_idmap(key,data):
    return str(data[1])

def find_fidmap(key,data):
    return str(data[1])

def find_eventname(key,data):
    return str(data[2])

def find_repository_type(key,data):
    return str(data[2])

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
        self.cursor = source.cursor(txn)
        
    def first(self):
        return self.cursor.first()

    def next(self):
        return self.cursor.next()

    def close(self):
        self.cursor.close()

class GrampsBSDDBDupCursor(GrampsBSDDBCursor):
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
class GrampsBSDDB(GrampsDbBase):
    """GRAMPS database object. This object is a base class for other
    objects."""

    def __init__(self):
        """creates a new GrampsDB"""
        GrampsDbBase.__init__(self)
        self.txn = None

    def open_table(self,name,dbname,no_txn=False):
        dbmap = dbshelve.DBShelf(self.env)
        dbmap.db.set_pagesize(16384)
        if self.readonly:
            dbmap.open(name, dbname, db.DB_HASH, db.DB_RDONLY)
        elif no_txn:
            dbmap.open(name, dbname, db.DB_HASH, db.DB_CREATE, 0666)
        else:
            dbmap.open(name, dbname, db.DB_HASH,
                       db.DB_CREATE|db.DB_AUTO_COMMIT, 0666)
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
        return GrampsBSDDBCursor(self.reference_map,self.txn)

    def get_reference_map_primary_cursor(self):
        return GrampsBSDDBDupCursor(self.reference_map_primary_map,self.txn)

    def get_reference_map_referenced_cursor(self):
        return GrampsBSDDBDupCursor(self.reference_map_referenced_map,self.txn)

        
    def version_supported(self):
        return (self.metadata.get('version',0) <= _DBVERSION and
                self.metadata.get('version',0) >= _MINVERSION)
    
    def need_upgrade(self):
        return not self.readonly \
               and self.metadata.get('version',0) < _DBVERSION

    def load(self,name,callback,mode="w"):
        if self.db_is_open:
            self.close()

        self.readonly = mode == "r"

        callback(12)

        self.env = db.DBEnv()
        self.env.set_cachesize(0,0x2000000)         # 2MB
        self.env.set_flags(db.DB_LOG_AUTOREMOVE,1)  # clean up unused logs
        # The DB_PRIVATE flag must go if we ever move to multi-user setup
        env_flags = db.DB_CREATE|db.DB_PRIVATE|\
                    db.DB_INIT_MPOOL|db.DB_INIT_LOCK|\
                    db.DB_INIT_LOG|db.DB_INIT_TXN

        self.undolog = "%s.undo" % name
        env_name = os.path.expanduser(const.bsddbenv_dir)
        if not os.path.isdir(env_name):
            os.mkdir(env_name)
        self.env.open(env_name,env_flags)
        self.env.txn_checkpoint()

        callback(25)

        self.full_name = os.path.abspath(name)
        self.brief_name = os.path.basename(name)

        self.family_map     = self.open_table(self.full_name, "family")
        self.place_map      = self.open_table(self.full_name, "places")
        self.source_map     = self.open_table(self.full_name, "sources")
        self.media_map      = self.open_table(self.full_name, "media")
        self.event_map      = self.open_table(self.full_name, "events")
        self.metadata       = self.open_table(self.full_name, "meta")
        self.person_map     = self.open_table(self.full_name, "person")
        self.repository_map = self.open_table(self.full_name, "repository")
        self.reference_map  = dbshelve.DBShelf(self.env)
        self.reference_map.db.set_pagesize(16384)
        self.reference_map.open(self.full_name, 'reference_map', db.DB_BTREE,
                       db.DB_CREATE|db.DB_AUTO_COMMIT, 0666)
        
        callback(37)
        
        # index tables used just for speeding up searches
        if self.readonly:
            table_flags = db.DB_RDONLY
        else:
            table_flags = db.DB_CREATE|db.DB_AUTO_COMMIT

        self.surnames = db.DB(self.env)
        self.surnames.set_flags(db.DB_DUP)
        self.surnames.open(self.full_name, "surnames",
                           db.DB_HASH, flags=table_flags)

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

        callback(50)
        
        self.eventnames = db.DB(self.env)
        self.eventnames.set_flags(db.DB_DUP)
        self.eventnames.open(self.full_name, "eventnames",
                             db.DB_HASH, flags=table_flags)

        self.repository_types = db.DB(self.env)
        self.repository_types.set_flags(db.DB_DUP)
        self.repository_types.open(self.full_name, "repostypes",
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

        callback(62)
        if not self.readonly:
            self.person_map.associate(self.surnames,  find_surname, table_flags)
            self.person_map.associate(self.id_trans,  find_idmap, table_flags)
            self.family_map.associate(self.fid_trans, find_idmap, table_flags)
            self.event_map.associate(self.eid_trans,  find_idmap,  table_flags)
            self.repository_map.associate(self.rid_trans, find_idmap,
                                          table_flags)
            self.repository_map.associate(self.repository_types,
                                          find_repository_type, table_flags)
            self.place_map.associate(self.pid_trans,  find_idmap, table_flags)
            self.media_map.associate(self.oid_trans, find_idmap, table_flags)
            self.source_map.associate(self.sid_trans, find_idmap, table_flags)
            self.reference_map.associate(self.reference_map_primary_map,
                                         find_primary_handle,
                                         table_flags)
            self.reference_map.associate(self.reference_map_referenced_map,
                                         find_referenced_handle,
                                         table_flags)

            self.undodb = db.DB()
            self.undodb.open(self.undolog, db.DB_RECNO, db.DB_CREATE)

        callback(75)
        self.metadata   = self.open_table(self.full_name, "meta", no_txn=True)
        self.bookmarks = self.metadata.get('bookmarks')
        self.family_event_names = set(self.metadata.get('fevent_names',[]))
        self.individual_event_names = set(self.metadata.get('pevent_names',[]))
        self.family_attributes = set(self.metadata.get('fattr_names',[]))
        self.individual_attributes = set(self.metadata.get('pattr_names',[]))

        gstats = self.metadata.get('gender_stats')

        if not self.readonly:
            if gstats == None:
                self.metadata['version'] = _DBVERSION
            elif not self.metadata.has_key('version'):
                self.metadata['version'] = 0

        if self.bookmarks == None:
            self.bookmarks = []

        self.genderStats = GenderStats(gstats)
        self.db_is_open = True
        callback(87)
        return 1

    def rebuild_secondary(self,callback=None):
        table_flags = db.DB_CREATE|db.DB_AUTO_COMMIT

        # Repair secondary indices related to person_map
        self.id_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"idtrans")
        self.id_trans = db.DB(self.env)
        self.id_trans.set_flags(db.DB_DUP)
        self.id_trans.open(self.full_name, "idtrans", db.DB_HASH,
                           flags=table_flags)
        self.person_map.associate(self.id_trans,find_idmap,table_flags)

        self.surnames.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"surnames")
        self.surnames = db.DB(self.env)
        self.surnames.set_flags(db.DB_DUP)
        self.surnames.open(self.full_name, "surnames", db.DB_HASH,
                           flags=table_flags)
        self.person_map.associate(self.surnames,  find_surname, table_flags)


        # Repair secondary indices related to family_map
        self.fid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"fidtrans")
        self.fid_trans = db.DB(self.env)
        self.fid_trans.set_flags(db.DB_DUP)
        self.fid_trans.open(self.full_name, "fidtrans", db.DB_HASH,
                            flags=table_flags)
        self.family_map.associate(self.fid_trans, find_idmap, table_flags)

        # Repair secondary indices related to place_map
        self.pid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"pidtrans")
        self.pid_trans = db.DB(self.env)
        self.pid_trans.set_flags(db.DB_DUP)
        self.pid_trans.open(self.full_name, "pidtrans", db.DB_HASH,
                            flags=table_flags)
        self.place_map.associate(self.pid_trans, find_idmap, table_flags)

        # Repair secondary indices related to media_map
        self.oid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"oidtrans")
        self.oid_trans = db.DB(self.env)
        self.oid_trans.set_flags(db.DB_DUP)
        self.oid_trans.open(self.full_name, "oidtrans", db.DB_HASH,
                            flags=table_flags)
        self.media_map.associate(self.oid_trans, find_idmap, table_flags)

        # Repair secondary indices related to source_map
        self.sid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"sidtrans")
        self.sid_trans = db.DB(self.env)
        self.sid_trans.set_flags(db.DB_DUP)
        self.sid_trans.open(self.full_name, "sidtrans", db.DB_HASH,
                            flags=table_flags)
        self.source_map.associate(self.sid_trans, find_idmap, table_flags)

        # Repair secondary indices related to event_map
        self.eid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"eidtrans")
        self.eid_trans = db.DB(self.env)
        self.eid_trans.set_flags(db.DB_DUP)
        self.eid_trans.open(self.full_name, "eidtrans", db.DB_HASH,
                            flags=table_flags)
        self.event_map.associate(self.eid_trans, find_idmap, table_flags)

        # Repair secondary indices related to repository_map
        self.rid_trans.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"ridtrans")
        self.rid_trans = db.DB(self.env)
        self.rid_trans.set_flags(db.DB_DUP)
        self.rid_trans.open(self.full_name, "ridtrans", db.DB_HASH,
                            flags=table_flags)
        self.repository_map.associate(self.rid_trans, find_idmap, table_flags)


        # Repair secondary indices related to reference_map
        self.reference_map_primary_map.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"reference_map_primary_map")
        self.reference_map_primary_map = db.DB(self.env)
        self.reference_map_primary_map.set_flags(db.DB_DUP)
        self.reference_map_primary_map.open(self.full_name,
                                            "reference_map_primary_map",
                                            db.DB_BTREE,
                                            flags=table_flags)
        self.reference_map.associate(self.reference_map_primary_map,
                                     find_primary_handle,
                                     table_flags)

        self.reference_map_referenced_map.close()
        junk = db.DB(self.env)
        junk.remove(self.full_name,"reference_map_referenced_map")
        self.reference_map_referenced_map = db.DB(self.env)
        self.reference_map_referenced_map.set_flags(db.DB_DUP|db.DB_DUPSORT)
        self.reference_map_referenced_map.open(self.full_name,
                                               "reference_map_referenced_map",
                                               db.DB_BTREE,
                                               flags=table_flags)
        self.reference_map.associate(self.reference_map_referenced_map,
                                     find_referenced_handle,
                                     table_flags)

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        Returns an interator over alist of (class_name,handle) tuples.

        @param handle: handle of the object to search for.
        @type handle: database handle
        @param include_classes: list of class names to include in the results.
                                Default: None means include all classes.
        @type include_classes: list of class names

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use:

               result_list = [i for i in find_backlink_handles(handle)]
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

            data = cPickle.loads(data)
            if include_classes == None or KEY_TO_CLASS_MAP[data[0][0]] in include_classes:
                yield (KEY_TO_CLASS_MAP[data[0][0]],data[0][1])
                
            ret = referenced_cur.next_dup()

        referenced_cur.close()

        return 

    def _delete_primary_from_reference_map(self, handle, transaction):
        """Remove all references to the primary object from the reference_map"""

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
            # combine with the primary_handle to get the main key.

            main_key = (handle, cPickle.loads(data)[1][1])

            self._remove_reference(main_key,transaction)
            
            ret = primary_cur.next_dup()

        primary_cur.close()
        
    def _update_reference_map(self, obj, transaction, update=True):
        """
        If update = True old references are cleaned up and only new references are added
        if update = False then it is assumed that the object is not already referenced.
        """
        
        # Add references to the reference_map for all primary object referenced
        # from the primary object 'obj' or any of its secondary objects.

        if update:
            # FIXME: this needs to be properly integrated into the transaction
            # framework so that the reference_map changes are part of the
            # transaction

            handle = obj.get_handle()

            # First thing to do is get hold of all rows in the reference_map
            # table that hold a reference from this primary obj. This means finding
            # all the rows that have this handle somewhere in the list of (class_name,handle)
            # pairs.
            # The primary_map secondary index allows us to look this up quickly.

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
                # compare with what is returned from get_referenced_handles_recursively

                # Looks like there is a bug in the set() and next_dup() methods
                # because they do not run the data through cPickle.loads before
                # returning it, so we have to here.
                existing_reference = cPickle.loads(data)[1]
                existing_references.add((KEY_TO_CLASS_MAP[existing_reference[0]],
                                         existing_reference[1]))
                ret = primary_cur.next_dup()

            primary_cur.close()

            # Once we have the list of rows that already have a reference we need to compare
            # it with the list of objects that are still references from the primary object.

            current_references = set(obj.get_referenced_handles_recursively())

            no_longer_required_references = existing_references.difference(current_references)


            new_references = current_references.difference(existing_references)

        else:
            new_references = set(obj.get_referenced_handles_recursively())
            
        # handle addition of new references

        if len(new_references) > 0:
            for (ref_class_name,ref_handle) in new_references:
                data = ((CLASS_TO_KEY_MAP[obj.__class__.__name__],handle),
                        (CLASS_TO_KEY_MAP[ref_class_name],ref_handle),)
                self._add_reference((handle,ref_handle),data,transaction)

        if update:
            # handle deletion of old references
            if len(no_longer_required_references) > 0:
                for (ref_class_name,ref_handle) in no_longer_required_references:
                    try:
                        self._remove_reference((handle,ref_handle),transaction)
                        #self.reference_map.delete(str((handle,ref_handle),),
                        #                          txn=self.txn)
                    except: # ignore missing old reference
                        pass

    def _remove_reference(self,key,transaction):
        """
        Removes the reference specified by the key,
        preserving the change in the passed transaction.
        """
        if not self.readonly:
            old_data = self.reference_map.get(str(main_key),txn=self.txn)
            if not transaction.batch:
                transaction.add(REFERENCE_KEY,str(key),old_data,None)
            transaction.reference_del.append(str(key))

    def _add_reference(self,key,data,transaction):
        """
        Adds the reference specified by the key and the data,
        preserving the change in the passed transaction.
        """

        if self.readonly or not key:
            return
        
        if transaction.batch:
            the_txn = self.env.txn_begin()
            self.reference_map.put(str(key),data,txn=the_txn)
            the_txn.commit()
        else:
            transaction.add(REFERENCE_KEY,str(key),None,data)
            transaction.reference_add.append((str(key),data))

    def reindex_reference_map(self):
        """Reindex all primary records in the database. This will be a
        slow process for large databases.

        At present this method does not clear the reference_map before it
        reindexes. This is fine when if reindex is run to index new content or
        when upgrading from a non-reference_map version of the database. But it
        might be a problem if reindex is used to repair a broken index because any
        references to primary objects that are no longer in the database will
        remain in the reference_map index. So if you want to reindex for repair
        purposes you need to clear the reference_map first.
        """


        # Make a dictionary of the functions and classes that we need for
        # each of the primary object tables.
        primary_tables = {'Person': {'cursor_func': self.get_person_cursor,
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

        # Now we use the functions and classes defined above to loop through each of the
        # primary object tables.
        for primary_table_name in primary_tables.keys():
            
            cursor = primary_tables[primary_table_name]['cursor_func']()
            data = cursor.first()

            # Grap the real object class here so that the lookup does
            # not happen inside the main loop.
            class_func = primary_tables[primary_table_name]['class_func']

            while data:
                found_handle,val = data
                obj = class_func()
                obj.unserialize(val)

                self._update_reference_map(obj,transaction)
                
                data = cursor.next()

            cursor.close()

        return
        
    def abort_changes(self):
        while self.undo():
            pass
        self.close()

    def close(self):
        if not self.db_is_open:
            return
        self.name_group.close()
        self.person_map.close()
        self.family_map.close()
        self.repository_map.close()
        self.place_map.close()
        self.source_map.close()
        self.media_map.close()
        self.event_map.close()
        self.reference_map.close()
        if not self.readonly:
            self.metadata['bookmarks'] = self.bookmarks
            self.metadata['gender_stats'] = self.genderStats.save_stats()
            self.metadata['fevent_names'] = list(self.family_event_names)
            self.metadata['pevent_names'] = list(self.individual_event_names)
            self.metadata['fattr_names'] = list(self.family_attributes)
            self.metadata['pattr_names'] = list(self.individual_attributes)
        self.metadata.close()
        self.surnames.close()
        self.eventnames.close()
        self.repository_types.close()
        self.id_trans.close()
        self.fid_trans.close()
        self.eid_trans.close()
        self.rid_trans.close()
        self.oid_trans.close()
        self.sid_trans.close()
        self.pid_trans.close()
        self.reference_map_primary_map.close()
        self.reference_map_referenced_map.close()
        self.env.txn_checkpoint()
        self.env.close()

        if not self.readonly:
            self.undodb.close()
            try:
                os.remove(self.undolog)
            except:
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

    def _do_remove_object(self,handle,trans,dmap,key,del_list):
        self._delete_primary_from_reference_map(handle,trans)
        if not self.readonly:
            handle = str(handle)
            if not trans.batch:
                old_data = dmap.get(handle,txn=self.txn)
                trans.add(key,handle,old_data,None)
            del_list.append(handle)

    def _del_person(self,handle):
        self.person_map.delete(str(handle),txn=self.txn)

    def _del_source(self,handle):
        self.source_map.delete(str(handle),txn=self.txn)

    def _del_repository(self,handle):
        self.repository_map.delete(str(handle),txn=self.txn)

    def _del_place(self,handle):
        self.place_map.delete(str(handle),txn=self.txn)

    def _del_media(self,handle):
        self.media_map.delete(str(handle),txn=self.txn)

    def _del_family(self,handle):
        self.family_map.delete(str(handle),txn=self.txn)

    def _del_event(self,handle):
        self.event_map.delete(str(handle),txn=self.txn)

    def set_name_group_mapping(self,name,group):
        if not self.readonly:
            name = str(name)
            data = self.name_group.get(name,txn=self.txn)
            if not group and data:
                self.name_group.delete(name,txn=self.txn)
            else:
                self.name_group.put(name,group,txn=self.txn)
            self.emit('person-rebuild')
            
    def get_surname_list(self):
        vals = [ unicode(val) for val in set(self.surnames.keys()) ]
        vals.sort(locale.strcoll)
        return vals

    def get_person_event_type_list(self):
        vals = [ unicode(val) for val in set(self.eventnames.keys()) ]
        vals.sort(locale.strcoll)
        return vals

    def get_repository_type_list(self):
        vals = list(set(self.repository_types.keys()))
        vals.sort(locale.strcoll)
        return vals

    def _get_obj_from_gramps_id(self,val,tbl,class_init):
        data = tbl.get(str(val),txn=self.txn)
        if data:
            obj = class_init()
            obj.unserialize(cPickle.loads(data))
            return obj
        else:
            return None

    def get_person_from_gramps_id(self,val):
        """finds a Person in the database from the passed gramps' ID.
        If no such Person exists, a new Person is added to the database."""
        return self._get_obj_from_gramps_id(val,self.id_trans,Person)

    def get_family_from_gramps_id(self,val):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Person is added to the database."""
        return self._get_obj_from_gramps_id(val,self.fid_trans,Family)

    def get_place_from_gramps_id(self,val):
        """finds a Place in the database from the passed gramps' ID.
        If no such Place exists, a new Person is added to the database."""
        return self._get_obj_from_gramps_id(val,self.pid_trans,Place)

    def get_source_from_gramps_id(self,val):
        """finds a Source in the database from the passed gramps' ID.
        If no such Source exists, a new Person is added to the database."""
        return self._get_obj_from_gramps_id(val,self.sid_trans,Source)

    def get_object_from_gramps_id(self,val):
        """finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, a new Person is added to the database."""
        return self._get_obj_from_gramps_id(val,self.oid_trans,MediaObject)

    def get_repository_from_gramps_id(self,val):
        """finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, a new Person is added to the database."""
        return self._get_obj_from_gramps_id(val,self.rid_trans,Repository)

    def _commit_base(self, obj, data_map, key, update_list, add_list,
                     transaction, change_time):
        """
        Commits the specified Person to the database, storing the changes
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
            the_txn = self.env.txn_begin()
            data_map.put(handle,obj.serialize(),txn=the_txn)
            the_txn.commit()
            old_data = None
        else:
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
            retlist.append(str(handle))
        return retlist

    def _get_from_handle(self, handle, class_type, data_map):
        try:
            data = data_map.get(str(handle),txn=self.txn)
        except:
            data = None
            log.error("Failed to get from handle",exc_info=True)
        if data:
            newobj = class_type()
            newobj.unserialize(data)
            return newobj
        return None

    def _find_from_handle(self,handle,transaction,class_type,dmap,add_func):
        obj = class_type()
        handle = str(handle)
        data = dmap.get(handle,txn=self.txn)
        if data:
            obj.unserialize(data)
        else:
            obj.set_handle(handle)
            add_func(obj,transaction)
        return obj

    def find_next_person_gramps_id(self):
        """
        Returns the next available GRAMPS' ID for a Person object based
        off the person ID prefix.
        """
        index = self.iprefix % self.pmap_index
        while self.id_trans.get(str(index),txn=self.txn):
            self.pmap_index += 1
            index = self.iprefix % self.pmap_index
        self.pmap_index += 1
        return index

    def find_next_place_gramps_id(self):
        """
        Returns the next available GRAMPS' ID for a Place object based
        off the person ID prefix.
        """
        index = self.pprefix % self.lmap_index
        while self.pid_trans.get(str(index),txn=self.txn):
            self.lmap_index += 1
            index = self.pprefix % self.lmap_index
        self.lmap_index += 1
        return index

    def find_next_event_gramps_id(self):
        """
        Returns the next available GRAMPS' ID for a Event object based
        off the person ID prefix.
        """
        index = self.eprefix % self.emap_index
        while self.eid_trans.get(str(index),txn=self.txn):
            self.emap_index += 1
            index = self.eprefix % self.emap_index
        self.emap_index += 1
        return index

    def find_next_object_gramps_id(self):
        """
        Returns the next available GRAMPS' ID for a MediaObject object based
        off the person ID prefix.
        """
        index = self.oprefix % self.omap_index
        while self.oid_trans.get(str(index),txn=self.txn):
            self.omap_index += 1
            index = self.oprefix % self.omap_index
        self.omap_index += 1
        return index

    def find_next_source_gramps_id(self):
        """
        Returns the next available GRAMPS' ID for a Source object based
        off the person ID prefix.
        """
        index = self.sprefix % self.smap_index
        while self.sid_trans.get(str(index),txn=self.txn):
            self.smap_index += 1
            index = self.sprefix % self.smap_index
        self.smap_index += 1
        return index

    def find_next_family_gramps_id(self):
        """
        Returns the next available GRAMPS' ID for a Family object based
        off the person ID prefix.
        """
        index = self.fprefix % self.fmap_index
        while self.fid_trans.get(str(index),txn=self.txn):
            self.fmap_index += 1
            index = self.fprefix % self.fmap_index
        self.fmap_index += 1
        return index

    def find_next_repository_gramps_id(self):
        """
        Returns the next available GRAMPS' ID for a Respository object based
        off the repository ID prefix.
        """
        index = self.rprefix % self.rmap_index
        while self.rid_trans.get(str(index),txn=self.txn):
            self.rmap_index += 1
            index = self.rprefix % self.rmap_index
        self.rmap_index += 1
        return index

    def transaction_begin(self,msg="",batch=False):
        """
        Creates a new Transaction tied to the current UNDO database. The
        transaction has no effect until it is committed using the
        transaction_commit function of the this database object.
        """

        transaction = BdbTransaction(msg,self.undodb,batch)
        if transaction.batch:
            self.env.txn_checkpoint()
            self.env.set_flags(db.DB_TXN_NOSYNC,1)      # async txn
        return transaction

    def transaction_commit(self,transaction,msg):

        # Start BSD DB transaction -- DBTxn
        self.txn = self.env.txn_begin()

        GrampsDbBase.transaction_commit(self,transaction,msg)

        for (key,data) in transaction.reference_add:
            self.reference_map.put(str(key),data,txn=self.txn)

        for (key,data) in transaction.reference_del:
            self.reference_map.delete(str(key),txn=self.txn)

        # Commit BSD DB transaction -- DBTxn
        self.txn.commit()
        if transaction.batch:
            self.env.txn_checkpoint()
            self.env.set_flags(db.DB_TXN_NOSYNC,0)      # sync txn
        self.txn = None

    def undo(self):
        print "Undoing it"
        self.txn = self.env.txn_begin()
        GrampsDbBase.undo(self)
        self.txn.commit()
        self.txn = None

    def redo(self):
        print "Redoing it"
        self.txn = self.env.txn_begin()
        GrampsDbBase.redo(self)
        self.txn.commit()
        self.txn = None        

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

    def gramps_upgrade(self):
        child_rel_notrans = [
            "None",      "Birth",  "Adopted", "Stepchild",
            "Sponsored", "Foster", "Unknown", "Other", ]
        
        version = self.metadata.get('version',_MINVERSION)

        if version < 6:
            self.gramps_upgrade_6()
        if version < 7:
            self.gramps_upgrade_7()
        if version < 8:
            self.gramps_upgrade_8()
        if version < 9:
            self.gramps_upgrade_9()

        self.metadata['version'] = _DBVERSION
        self.metadata.sync()

    def gramps_upgrade_6(self):
        print "Upgrading to DB version 6"
        order = []
        for val in self.get_media_column_order():
            if val[1] != 6:
                order.append(val)
        self.set_media_column_order(order)

    def gramps_upgrade_7(self):
        print "Upgrading to DB version 7"

        self.genderStats = GenderStats()
        cursor = self.get_person_cursor()
        data = cursor.first()
        while data:
            handle,val = data
            p = Person(val)
            self.genderStats.count_person(p,self)
            data = cursor.next()
        cursor.close()

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

    def gramps_upgrade_9(self):
        print "Upgrading to DB version 9 -- this may take a while"
        # First, make sure the stored default person handle is str, not unicode
        try:
            handle = self.metadata['default']
            self.metadata['default'] = str(handle)
        except KeyError:
            # default person was not stored in database
            pass

        # The rest of the upgrade deals with real data, not metadata
        # so starting transaction here.
        trans = Transaction("",self)
        trans.set_batch(True)

        # This upgrade adds marker to every primary object.
        # We need to extract and commit every primary object
        # even if no other changes are made.

        # Change every Source to have reporef_list
#        cursor = self.get_source_cursor()
#        data = cursor.first()
#        while data:
#            handle,info = data
        for handle in self.source_map.keys():
            info = self.source_map[handle]        
            source = Source()
            source.handle = handle
            # We already have a new Source object with the reporef_list
            # just fill in the rest of the fields for this source
            (junk_handle, source.gramps_id, source.title, source.author,
             source.pubinfo, source.note, source.media_list,
             source.abbrev, source.change, source.datamap) = info
            self.commit_source(source,trans)
#            data = cursor.next()
#        cursor.close()

        #cursor = self.get_person_cursor()
        #data = cursor.first()
        #while data:
        #    handle,info = data
        for handle in self.person_map.keys():
            info = self.person_map[handle]
            person = Person()
            person.handle = handle
            # Restore data from dbversion 8 (gramps 2.0.9)
            (junk_handle, person.gramps_id, person.gender,
             person.primary_name, person.alternate_names, person.nickname,
             death_handle, birth_handle, event_list,
             person.family_list, person.parent_family_list,
             person.media_list, person.address_list, person.attribute_list,
             person.urls, person.lds_bapt, person.lds_endow, person.lds_seal,
             complete, person.source_list, person.note,
             person.change, person.private) = (info + (False,))[0:23]

            # Convert complete flag into marker
            if complete:
                person.marker = (PrimaryObject.MARKER_COMPLETE,"")
            
            # Change every event handle to the EventRef
            if birth_handle:
                event_ref = EventRef()
                event_ref.ref = birth_handle
                event_ref.role = (EventRef.PRIMARY,'')
                person.birth_ref = event_ref

            if death_handle:
                event_ref = EventRef()
                event_ref.ref = death_handle
                event_ref.role = (EventRef.PRIMARY,'')
                person.death_ref = event_ref

            for event_handle in event_list:
                event_ref = EventRef()
                event_ref.ref = event_handle
                event_ref.role = (EventRef.PRIMARY,'')
                person.event_ref_list.append(event_ref)

            # In all Name instances, convert type from string to a tuple
            name_conversion = {
                "Also Known As" : (Name.AKA,""),
                "Birth Name"    : (Name.BIRTH,""),
                "Married Name"  : (Name.MARRIED,""),
                "Other Name"    : (Name.CUSTOM,_("Other Name")),
                }
            for name in [person.primary_name] + person.alternate_names:
                old_type = name.type
                if old_type:
                    if name_conversion.has_key(old_type):
                        new_type = name_conversion[old_type]
                    else:
                        new_type = (Name.CUSTOM,old_type)
                else:
                    new_type = (Name.UNKNOWN,"")
                name.type = new_type

            # In all Attributes, convert type from string to a tuple
            for attribute in person.attribute_list:
                convert_attribute_9(attribute)
            # Cover attributes contained in MediaRefs
            for media_ref in person.media_list:
                convert_mediaref_9(media_ref)

            # In all Urls, add type attribute
            for url in person.urls:
                convert_url_9(url)
            
            self.commit_person(person,trans)
            #data = cursor.next()
        #cursor.close()

        #cursor = self.get_family_cursor()
        #data = cursor.first()
        #while data:
        #    handle,info = data
        for handle in self.family_map.keys():
            info = self.family_map[handle]
            family = Family()
            family.handle = handle
            # Restore data from dbversion 8 (gramps 2.0.9)
            (junk_handle, family.gramps_id, family.father_handle,
             family.mother_handle, family.child_list, family.type,
             event_list, family.media_list, family.attribute_list,
             family.lds_seal, complete, family.source_list,
             family.note, family.change) = info

            if complete:
                family.marker = (PrimaryObject.MARKER_COMPLETE,"")
                
            # Change every event handle to the EventRef
            for event_handle in event_list:
                event_ref = EventRef()
                event_ref.ref = event_handle
                event_ref.role = (EventRef.PRIMARY,'')
                family.event_ref_list.append(event_ref)

            # In all Attributes, convert type from string to a tuple
            for attribute in family.attribute_list:
                convert_attribute_9(attribute)
            # Cover attributes contained in MediaRefs
            for media_ref in family.media_list:
                convert_mediaref_9(media_ref)
            
            self.commit_family(family,trans)
#            data = cursor.next()
#        cursor.close()
        
        event_conversion = {
            "Alternate Marriage"  : (Event.MARR_ALT,""),
            "Annulment"           : (Event.ANNULMENT,""),
            "Divorce"             : (Event.DIVORCE,""),
            "Engagement"          : (Event.ENGAGEMENT,""),
            "Marriage Banns"      : (Event.MARR_BANNS,""),
            "Marriage Contract"   : (Event.MARR_CONTR,""),
            "Marriage License"    : (Event.MARR_LIC,""),
            "Marriage Settlement" : (Event.MARR_SETTL,""),
            "Marriage"            : (Event.MARRIAGE,""),
            "Adopted"             : (Event.ADOPT,""),
            "Birth"               : (Event.BIRTH,""),
            "Alternate Birth"     : (Event.BIRTH,""),
            "Death"               : (Event.DEATH,""),
            "Alternate Death"     : (Event.DEATH,""),
            "Adult Christening"   : (Event.ADULT_CHRISTEN,""),
            "Baptism"             : (Event.BAPTISM,""),
            "Bar Mitzvah"         : (Event.BAR_MITZVAH,""),
            "Bas Mitzvah"         : (Event.BAS_MITZVAH,""),
            "Blessing"            : (Event.BLESS,""),
            "Burial"              : (Event.BURIAL,""),
            "Cause Of Death"      : (Event.CAUSE_DEATH,""),
            "Census"              : (Event.CENSUS,""),
            "Christening"         : (Event.CHRISTEN,""),
            "Confirmation"        : (Event.CONFIRMATION,""),
            "Cremation"           : (Event.CREMATION,""),
            "Degree"              : (Event.DEGREE,""),
            "Divorce Filing"      : (Event.DIV_FILING,""),
            "Education"           : (Event.EDUCATION,""),
            "Elected"             : (Event.ELECTED,""),
            "Emigration"          : (Event.EMIGRATION,""),
            "First Communion"     : (Event.FIRST_COMMUN,""),
            "Immigration"         : (Event.IMMIGRATION,""),
            "Graduation"          : (Event.GRADUATION,""),
            "Medical Information" : (Event.MED_INFO,""),
            "Military Service"    : (Event.MILITARY_SERV,""),
            "Naturalization"      : (Event.NATURALIZATION,""),
            "Nobility Title"      : (Event.NOB_TITLE,""),
            "Number of Marriages" : (Event.NUM_MARRIAGES,""),
            "Occupation"          : (Event.OCCUPATION,""),
            "Ordination"          : (Event.ORDINATION,""),
            "Probate"             : (Event.PROBATE,""),
            "Property"            : (Event.PROPERTY,""),
            "Religion"            : (Event.RELIGION,""),
            "Residence"           : (Event.RESIDENCE,""),
            "Retirement"          : (Event.RETIREMENT,""),
            "Will"                : (Event.WILL,""),
            }

#        cursor = self.get_event_cursor()
#        data = cursor.first()
#        while data:
        #    handle,info = data
        for handle in self.event_map.keys():
            info = self.event_map[handle]        
            event = Event()
            event.handle = handle
            (junk_handle, event.gramps_id, old_type, event.date,
             event.description, event.place, event.cause, event.private,
             event.source_list, event.note, witness_list,
             event.media_list, event.change) = info

            if old_type:
                if event_conversion.has_key(old_type):
                    new_type = event_conversion[old_type]
                else:
                    new_type = (Event.CUSTOM,old_type)
            else:
                new_type = (Event.UNKNOWN,"")
            event.type = new_type
            
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
                    # Add an EventRef from that person
                    # to this event using ROLE_WITNESS role
                    event_ref = EventRef()
                    event_ref.ref = event.handle
                    event_ref.role = (EventRef.WITNESS,'')
                    # Add privacy and comment
                    event_ref.private = witness.private
                    if witness.comment:
                        event_ref.set_note(witness.comment)
                    person = self.get_person_from_handle(witness.val)
                    person.event_ref_list.append(event_ref)
                    self.commit_person(person,trans)
            self.commit_event(event,trans)
#            data = cursor.next()
#        cursor.close()

        # Work out marker addition to the Place
#        cursor = self.get_place_cursor()
#        data = cursor.first()
#        while data:
#            handle,info = data
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

            self.commit_place(place,trans)
#            data = cursor.next()
#        cursor.close()

        # Work out marker addition to the Media
#        cursor = self.get_media_cursor()
#        data = cursor.first()
#        while data:
#            handle,info = data
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
#            data = cursor.next()
#        cursor.close()

        self.transaction_commit(trans,"Upgrade to DB version 9")
        print "Done upgrading to DB version 9"


class BdbTransaction(Transaction):
    def __init__(self,msg,db,batch=False):
        Transaction.__init__(self,msg,db,batch)
        self.reference_del = []
        self.reference_add = []

_attribute_conversion_9 = {
    "Caste"                  : (Attribute.CASTE,""),
    "Description"            : (Attribute.DESCRIPTION,""),
    "Identification Number"  : (Attribute.ID,""),
    "National Origin"        : (Attribute.NATIONAL,""),
    "Number of Children"     : (Attribute.NUM_CHILD,""),
    "Social Security Number" : (Attribute.SSN,""),
    }

def convert_attribute_9(attribute):
    old_type = attribute.type
    if old_type:
        if _attribute_conversion_9.has_key(old_type):
            new_type = _attribute_conversion_9[old_type]
        else:
            new_type = (Attribute.CUSTOM,old_type)
    else:
        new_type = (Attribute.UNKNOWN,"")
    attribute.type = new_type

def convert_mediaref_9(media_ref):
    for attribute in media_ref.attribute_list:
        convert_attribute_9(attribute)

def convert_url_9(url):
    path = url.path.strip()
    if path.find('mailto:') == 0 or url.path.find('@') != -1:
        url.type = (Url.EMAIL,'')
    elif path.find('http://') == 0:
        url.type = (Url.WEB_HOME,'')
    elif path.find('ftp://') == 0:
        url.type = (Url.WEB_FTP,'')
    else:
        url.type = (Url.CUSTOM,'')

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
