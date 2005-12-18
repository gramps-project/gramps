#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
from GrampsDbBase import *

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

    def __init__(self,source):
        self.cursor = source.cursor()
        
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

    def dbopen(self,name,dbname):
        dbmap = dbshelve.DBShelf(self.env)
        dbmap.db.set_pagesize(16384)
        if self.readonly:
            dbmap.open(name, dbname, db.DB_HASH, db.DB_RDONLY)
        else:
            dbmap.open(name, dbname, db.DB_HASH, db.DB_CREATE, 0666)
        return dbmap
    
    def get_person_cursor(self):
        return GrampsBSDDBCursor(self.person_map)

    def get_family_cursor(self):
        return GrampsBSDDBCursor(self.family_map)

    def get_event_cursor(self):
        return GrampsBSDDBCursor(self.event_map)

    def get_place_cursor(self):
        return GrampsBSDDBCursor(self.place_map)

    def get_source_cursor(self):
        return GrampsBSDDBCursor(self.source_map)

    def get_media_cursor(self):
        return GrampsBSDDBCursor(self.media_map)

    def get_repository_cursor(self):
        return GrampsBSDDBCursor(self.repository_map)

    # cursors for lookups in the reference_map for back reference
    # lookups. The reference_map has three indexes:
    # the main index: a tuple of (primary_handle,referenced_handle)
    # the primary_handle index: the primary_handle
    # the referenced_handle index: the referenced_handle
    # the main index is unique, the others allow duplicate entries.

    def get_reference_map_cursor(self):
        return GrampsBSDDBCursor(self.reference_map)

    def get_reference_map_primary_cursor(self):
        return GrampsBSDDBDupCursor(self.reference_map_primary_map)

    def get_reference_map_referenced_cursor(self):
        return GrampsBSDDBDupCursor(self.reference_map_referenced_map)

        
    def version_supported(self):
        return (self.metadata.get('version',0) <= _DBVERSION and
                self.metadata.get('version',0) >= _MINVERSION)
    
    def need_upgrade(self):
        return not self.readonly \
               and self.metadata.get('version',0) < _DBVERSION

    def load(self,name,callback,mode="w"):
        if self.person_map:
            self.close()

        self.readonly = mode == "r"

        self.env = db.DBEnv()
        self.env.set_cachesize(0,0x2000000) # 2MB
        flags = db.DB_CREATE|db.DB_INIT_MPOOL|db.DB_PRIVATE

        self.undolog = "%s.log" % name
        self.env.open(os.path.dirname(name), flags)
            
        name = os.path.basename(name)
        self.save_name = name

        self.family_map     = self.dbopen(name, "family")
        self.place_map      = self.dbopen(name, "places")
        self.source_map     = self.dbopen(name, "sources")
        self.media_map      = self.dbopen(name, "media")
        self.event_map      = self.dbopen(name, "events")
        self.metadata       = self.dbopen(name, "meta")
        self.person_map     = self.dbopen(name, "person")
        self.repository_map = self.dbopen(name, "repository")

        # index tables used just for speeding up searches

        self.reference_map = self.dbopen(name, "reference_map")

        if self.readonly:
            openflags = db.DB_RDONLY
        else:
            openflags = db.DB_CREATE

        self.surnames = db.DB(self.env)
        self.surnames.set_flags(db.DB_DUP)
        self.surnames.open(self.save_name, "surnames",
                           db.DB_HASH, flags=openflags)

        self.name_group = db.DB(self.env)
        self.name_group.set_flags(db.DB_DUP)
        self.name_group.open(self.save_name, "name_group",
                             db.DB_HASH, flags=openflags)

        self.id_trans = db.DB(self.env)
        self.id_trans.set_flags(db.DB_DUP)
        self.id_trans.open(self.save_name, "idtrans",
                           db.DB_HASH, flags=openflags)

        self.fid_trans = db.DB(self.env)
        self.fid_trans.set_flags(db.DB_DUP)
        self.fid_trans.open(self.save_name, "fidtrans",
                            db.DB_HASH, flags=openflags)

        self.eid_trans = db.DB(self.env)
        self.eid_trans.set_flags(db.DB_DUP)
        self.eid_trans.open(self.save_name, "eidtrans",
                            db.DB_HASH, flags=openflags)

        self.pid_trans = db.DB(self.env)
        self.pid_trans.set_flags(db.DB_DUP)
        self.pid_trans.open(self.save_name, "pidtrans",
                            db.DB_HASH, flags=openflags)

        self.sid_trans = db.DB(self.env)
        self.sid_trans.set_flags(db.DB_DUP)
        self.sid_trans.open(self.save_name, "sidtrans",
                            db.DB_HASH, flags=openflags)

        self.oid_trans = db.DB(self.env)
        self.oid_trans.set_flags(db.DB_DUP)
        self.oid_trans.open(self.save_name, "oidtrans",
                            db.DB_HASH, flags=openflags)

        self.rid_trans = db.DB(self.env)
        self.rid_trans.set_flags(db.DB_DUP)
        self.rid_trans.open(self.save_name, "ridtrans",
                            db.DB_HASH, flags=openflags)


        self.eventnames = db.DB(self.env)
        self.eventnames.set_flags(db.DB_DUP)
        self.eventnames.open(self.save_name, "eventnames",
                             db.DB_HASH, flags=openflags)

        self.repository_types = db.DB(self.env)
        self.repository_types.set_flags(db.DB_DUP)
        self.repository_types.open(self.save_name, "repostypes",
                                   db.DB_HASH, flags=openflags)

        self.reference_map_primary_map = db.DB(self.env)
        self.reference_map_primary_map.set_flags(db.DB_DUP)
        self.reference_map_primary_map.open(self.save_name,
                                            "reference_map_primary_map",
                                            db.DB_BTREE, flags=openflags)

        self.reference_map_referenced_map = db.DB(self.env)
        self.reference_map_referenced_map.set_flags(db.DB_DUP)
        self.reference_map_referenced_map.open(self.save_name,
                                               "reference_map_referenced_map",
                                               db.DB_BTREE, flags=openflags)


        if not self.readonly:
            self.person_map.associate(self.surnames,  find_surname, openflags)
            self.person_map.associate(self.id_trans,  find_idmap, openflags)
            self.family_map.associate(self.fid_trans, find_idmap, openflags)
            self.event_map.associate(self.eid_trans,  find_idmap,  openflags)
            self.repository_map.associate(self.rid_trans, find_idmap,
                                          openflags)
            self.repository_map.associate(self.repository_types,
                                          find_repository_type, openflags)
            self.place_map.associate(self.pid_trans,  find_idmap, openflags)
            self.media_map.associate(self.oid_trans, find_idmap, openflags)
            self.source_map.associate(self.sid_trans, find_idmap, openflags)
            self.reference_map.associate(self.reference_map_primary_map,
                                         find_primary_handle,
                                         openflags)
            self.reference_map.associate(self.reference_map_referenced_map,
                                         find_referenced_handle,
                                         openflags)

            self.undodb = db.DB()
            self.undodb.open(self.undolog, db.DB_RECNO, db.DB_CREATE)

        self.metadata   = self.dbopen(name, "meta")
        self.bookmarks = self.metadata.get('bookmarks')
        self.family_event_names = sets.Set(self.metadata.get('fevent_names',[]))
        self.individual_event_names = sets.Set(self.metadata.get('pevent_names',[]))
        self.family_attributes = sets.Set(self.metadata.get('fattr_names',[]))
        self.individual_attributes = sets.Set(self.metadata.get('pattr_names',[]))

        gstats = self.metadata.get('gender_stats')

        if not self.readonly:
            if gstats == None:
                self.metadata['version'] = _DBVERSION
            elif not self.metadata.has_key('version'):
                self.metadata['version'] = 0

        if self.bookmarks == None:
            self.bookmarks = []

        self.genderStats = GenderStats(gstats)
        return 1

    def rebuild_secondary(self,callback=None):

        # Repair secondary indices related to person_map
        
        self.id_trans.close()
        self.surnames.close()

        self.id_trans = db.DB(self.env)
        self.id_trans.set_flags(db.DB_DUP)
        self.id_trans.open(self.save_name, "idtrans", db.DB_HASH,
                           flags=db.DB_CREATE)
        self.id_trans.truncate()

        self.surnames = db.DB(self.env)
        self.surnames.set_flags(db.DB_DUP)
        self.surnames.open(self.save_name, "surnames", db.DB_HASH,
                           flags=db.DB_CREATE)
        self.surnames.truncate()

        self.person_map.associate(self.surnames, find_surname, db.DB_CREATE)
        self.person_map.associate(self.id_trans, find_idmap, db.DB_CREATE)

        for key in self.person_map.keys():
            if callback:
                callback()
            self.person_map[key] = self.person_map[key]
        self.person_map.sync()

        # Repair secondary indices related to family_map

        self.fid_trans.close()
        self.fid_trans = db.DB(self.env)
        self.fid_trans.set_flags(db.DB_DUP)
        self.fid_trans.open(self.save_name, "fidtrans", db.DB_HASH,
                            flags=db.DB_CREATE)
        self.fid_trans.truncate()
        self.family_map.associate(self.fid_trans, find_idmap, db.DB_CREATE)

        for key in self.family_map.keys():
            if callback:
                callback()
            self.family_map[key] = self.family_map[key]
        self.family_map.sync()

        # Repair secondary indices related to place_map

        self.pid_trans.close()
        self.pid_trans = db.DB(self.env)
        self.pid_trans.set_flags(db.DB_DUP)
        self.pid_trans.open(self.save_name, "pidtrans", db.DB_HASH,
                            flags=db.DB_CREATE)
        self.pid_trans.truncate()
        self.place_map.associate(self.pid_trans, find_idmap, db.DB_CREATE)

        for key in self.place_map.keys():
            if callback:
                callback()
            self.place_map[key] = self.place_map[key]
        self.place_map.sync()

        # Repair secondary indices related to media_map

        self.oid_trans.close()
        self.oid_trans = db.DB(self.env)
        self.oid_trans.set_flags(db.DB_DUP)
        self.oid_trans.open(self.save_name, "oidtrans", db.DB_HASH,
                            flags=db.DB_CREATE)
        self.oid_trans.truncate()
        self.media_map.associate(self.oid_trans, find_idmap, db.DB_CREATE)

        for key in self.media_map.keys():
            if callback:
                callback()
            self.media_map[key] = self.media_map[key]
        self.media_map.sync()

        # Repair secondary indices related to source_map

        self.sid_trans.close()
        self.sid_trans = db.DB(self.env)
        self.sid_trans.set_flags(db.DB_DUP)
        self.sid_trans.open(self.save_name, "sidtrans", db.DB_HASH,
                            flags=db.DB_CREATE)
        self.sid_trans.truncate()
        self.source_map.associate(self.sid_trans, find_idmap, db.DB_CREATE)

        for key in self.source_map.keys():
            if callback:
                callback()
            self.source_map[key] = self.source_map[key]
        self.source_map.sync()

        # Repair secondary indices related to repository_map

        self.rid_trans.close()
        self.rid_trans = db.DB(self.env)
        self.rid_trans.set_flags(db.DB_DUP)
        self.rid_trans.open(self.save_name, "ridtrans", db.DB_HASH,
                            flags=db.DB_CREATE)
        self.rid_trans.truncate()
        self.repository_map.associate(self.rid_trans, find_idmap, db.DB_CREATE)

        for key in self.repository_map.keys():
            if callback:
                callback()
            self.repository_map[key] = self.repository_map[key]
        self.repository_map.sync()

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

    def _delete_primary_from_reference_map(self, handle):
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

            self.reference_map.delete(str(main_key))
            
            ret = primary_cur.next_dup()

        primary_cur.close()
        
    def _update_reference_map(self, obj):        
        # Add references to the reference_map for all primary object referenced
        # from the primary object 'obj' or any of its secondary objects.
        
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
        
        # handle addition of new references

        if len(new_references) > 0:
            for (ref_class_name,ref_handle) in new_references:
                self.reference_map[str((handle,ref_handle),)] = ((CLASS_TO_KEY_MAP[obj.__class__.__name__],handle),
                                                                 (CLASS_TO_KEY_MAP[ref_class_name],ref_handle),)

        # handle deletion of old references
        if len(no_longer_required_references) > 0:
            for (ref_class_name,ref_handle) in no_longer_required_references:
                self.reference_map.delete(str((handle,ref_handle),))

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

                self._update_reference_map(obj)
                
                data = cursor.next()

            cursor.close()

        return

        
    def abort_changes(self):
        while self.undo():
            pass
        self.close()

    def close(self):
        if self.person_map == None:
            return
        self.name_group.close()
        self.person_map.close()
        self.family_map.close()
        self.repository_map.close()
        self.place_map.close()
        self.source_map.close()
        self.media_map.close()
        self.event_map.close()
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

    def _del_person(self,handle):
        self._delete_primary_from_reference_map(handle)
        self.person_map.delete(str(handle))

    def _del_source(self,handle):
        self._delete_primary_from_reference_map(handle)               
        self.source_map.delete(str(handle))

    def _del_repository(self,handle):
        self._delete_primary_from_reference_map(handle)
        self.repository_map.delete(str(handle))

    def _del_place(self,handle):
        self._delete_primary_from_reference_map(handle)
        self.place_map.delete(str(handle))

    def _del_media(self,handle):
        self._delete_primary_from_reference_map(handle)
        self.media_map.delete(str(handle))

    def _del_family(self,handle):
        self._delete_primary_from_reference_map(handle)
        self.family_map.delete(str(handle))

    def _del_event(self,handle):
        self._delete_primary_from_reference_map(handle)
        self.event_map.delete(str(handle))

    def set_name_group_mapping(self,name,group):
        if not self.readonly:
            name = str(name)
            if not group and self.name_group.has_key(name):
                self.name_group.delete(name)
            else:
                self.name_group[name] = group
            self.emit('person-rebuild')
            
    def get_surname_list(self):
        names = self.surnames.keys()
        a = {}
        for name in names:
            a[unicode(name)] = 1
        vals = a.keys()
        vals.sort(locale.strcoll)
        return vals

    def get_person_event_type_list(self):
        names = self.eventnames.keys()
        a = {}
        for name in names:
            a[unicode(name)] = 1
        vals = a.keys()
        vals.sort()
        return vals

    def get_repository_type_list(self):
        repos_types = self.repository_types.keys()
        a = {}
        for repos_type in repos_types:
            
            a[unicode(repos_type)] = 1
        vals = a.keys()
        vals.sort()
        return vals

    def remove_person(self,handle,transaction):
        if not self.readonly and handle and str(handle) in self.person_map:
            person = self.get_person_from_handle(handle)
            self.genderStats.uncount_person (person)
            if transaction != None:
                transaction.add(PERSON_KEY,handle,person.serialize())
                self.emit('person-delete',([str(handle)],))
            self.person_map.delete(str(handle))
            self._delete_primary_from_reference_map(handle)

    def remove_source(self,handle,transaction):
        if not self.readonly and handle and str(handle) in self.source_map:
            if transaction != None:
                old_data = self.source_map.get(str(handle))
                transaction.add(SOURCE_KEY,handle,old_data)
                self.emit('source-delete',([handle],))
            self.source_map.delete(str(handle))
            self._delete_primary_from_reference_map(handle)

    def remove_repository(self,handle,transaction):
        if not self.readonly and handle and str(handle) in self.repository_map:
            if transaction != None:
                old_data = self.repository_map.get(str(handle))
                transaction.add(REPOSITORY_KEY,handle,old_data)
                self.emit('repository-delete',([handle],))
            self.repository_map.delete(str(handle))
            self._delete_primary_from_reference_map(handle)

    def remove_family(self,handle,transaction):
        if not self.readonly and handle and str(handle) in self.family_map:
            if transaction != None:
                old_data = self.family_map.get(str(handle))
                transaction.add(FAMILY_KEY,handle,old_data)
                self.emit('family-delete',([str(handle)],))
            self.family_map.delete(str(handle))
            self._delete_primary_from_reference_map(handle)

    def remove_event(self,handle,transaction):
        if not self.readonly and handle and str(handle) in self.event_map:
            if transaction != None:
                old_data = self.event_map.get(str(handle))
                transaction.add(EVENT_KEY,handle,old_data)
                self.emit('event-delete',([str(handle)],))
            self.event_map.delete(str(handle))
            self._delete_primary_from_reference_map(handle)

    def remove_place(self,handle,transaction):
        if not self.readonly and handle and str(handle) in self.place_map:
            if transaction != None:
                old_data = self.place_map.get(str(handle))
                transaction.add(PLACE_KEY,handle,old_data)
                self.emit('place-delete',([handle],))
            self.place_map.delete(str(handle))
            self._delete_primary_from_reference_map(handle)

    def remove_object(self,handle,transaction):
        if not self.readonly and handle and str(handle) in self.media_map:
            if transaction != None:
                old_data = self.media_map.get(str(handle))
                transaction.add(MEDIA_KEY,handle,old_data)
                self.emit('media-delete',([handle],))
            self.media_map.delete(str(handle))
            self._delete_primary_from_reference_map(handle)

    def get_person_from_gramps_id(self,val):
        """finds a Person in the database from the passed gramps' ID.
        If no such Person exists, None is returned."""

        data = self.id_trans.get(str(val))
        if data:
            person = Person()
            person.unserialize(cPickle.loads(data))
            return person
        else:
            return None

    def get_family_from_gramps_id(self,val):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, None is returned."""

        data = self.fid_trans.get(str(val))
        if data:
            family = Family()
            family.unserialize(cPickle.loads(data))
            return family
        else:
            return None

    def get_event_from_gramps_id(self,val):
        """finds an Event in the database from the passed gramps' ID.
        If no such Event exists, None is returned."""

        data = self.eid_trans.get(str(val))
        if data:
            event = Event()
            event.unserialize(cPickle.loads(data))
            return event
        else:
            return None

    def get_place_from_gramps_id(self,val):
        """finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned."""

        data = self.pid_trans.get(str(val))
        if data:
            place = Place()
            place.unserialize(cPickle.loads(data))
            return place
        else:
            return None

    def get_source_from_gramps_id(self,val):
        """finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned."""

        data = self.sid_trans.get(str(val))
        if data:
            source = Source()
            source.unserialize(cPickle.loads(data))
            return source
        else:
            return None

    def get_repository_from_gramps_id(self,val):
        """finds a Repository in the database from the passed gramps' ID.
        If no such Repository exists, None is returned."""

        data = self.rid_trans.get(str(val))
        if data:
            repository = Repository()
            repository.unserialize(cPickle.loads(data))
            return repository
        else:
            return None

    def get_object_from_gramps_id(self,val):
        """finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, None is returned."""

        data = self.oid_trans.get(str(val))
        if data:
            obj = MediaObject()
            obj.unserialize(cPickle.loads(data))
            return obj
        else:
            return None

    def transaction_commit(self,transaction,msg):
        GrampsDbBase.transaction_commit(self,transaction,msg)
        self.family_map.sync()
        self.place_map.sync()
        self.source_map.sync()
        self.repository_map.sync()
        self.repository_types.sync()
        self.media_map.sync()
        self.event_map.sync()
        self.metadata.sync()
        self.person_map.sync()
        self.surnames.sync()
        self.name_group.sync()
        self.id_trans.sync()
        self.fid_trans.sync()
        self.eid_trans.sync()
        self.pid_trans.sync()
        self.sid_trans.sync()
        self.rid_trans.sync()
        self.oid_trans.sync()
        self.undodb.sync()

    def gramps_upgrade(self):
        child_rel_notrans = [
            "None",      "Birth",  "Adopted", "Stepchild",
            "Sponsored", "Foster", "Unknown", "Other", ]
        
        version = self.metadata.get('version',_MINVERSION)
        print version

        if version < 6:
            self.gramps_upgrade_6()
        if version < 7:
            self.gramps_upgrade_7()
        if version < 8:
            self.gramps_upgrade_8()
        if version < 9:
            self.gramps_upgrade_9()

        self.metadata['version'] = _DBVERSION
        print "set version to %d" % _DBVERSION
        print "actual version now is %d" % self.metadata['version']
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
        cursor = self.get_source_cursor()
        data = cursor.first()
        while data:
            handle,info = data
            source = Source()
            source.handle = handle
            # We already have a new Source object with the reporef_list
            # just fill in the rest of the fields for this source
            (junk_handle, source.gramps_id, source.title, source.author,
             source.pubinfo, source.note, source.media_list,
             source.abbrev, source.change, source.datamap) = info
            self.commit_source(source,trans)
            data = cursor.next()
        cursor.close()

        # Change every event handle to the EventRef
        # in all Person objects
        cursor = self.get_person_cursor()
        data = cursor.first()
        while data:
            handle,info = data
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

            if complete:
                person.marker = (PrimaryObject.MARKER_COMPLETE,"")
                
            if birth_handle:
                event_ref = EventRef()
                event_ref.set_reference_handle(birth_handle)
                event_ref.set_role((EventRef.PRIMARY,''))
                person.birth_ref = event_ref

            if death_handle:
                event_ref = EventRef()
                event_ref.set_reference_handle(death_handle)
                event_ref.set_role((EventRef.PRIMARY,''))
                person.death_ref = event_ref

            event_ref_list = []
            for event_handle in event_list:
                event_ref = EventRef()
                event_ref.set_reference_handle(event_handle)
                event_ref.set_role((EventRef.PRIMARY,''))
                event_ref_list.append(event_ref)

            if event_ref_list:
                person.event_ref_list = event_ref_list[:]

            self.commit_person(person,trans)
            data = cursor.next()
        cursor.close()

        # Change every event handle to the EventRef
        # in all Family objects
        cursor = self.get_family_cursor()
        data = cursor.first()
        while data:
            handle,info = data
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
                
            event_ref_list = []
            for event_handle in event_list:
                event_ref = EventRef()
                event_ref.set_reference_handle(event_handle)
                event_ref.set_role((EventRef.PRIMARY,''))
                event_ref_list.append(event_ref)

            if event_ref_list:
                family.event_ref_list = event_ref_list[:]

            self.commit_family(family,trans)
            data = cursor.next()
        cursor.close()
        
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

        # Remove Witness from every event and convert name to type
        cursor = self.get_event_cursor()
        data = cursor.first()
        while data:
            handle,info = data
            event = Event()
            event.handle = handle
            (junk_handle, event.gramps_id, name, event.date,
             event.description, event.place, event.cause, event.private,
             event.source_list, event.note, witness, event.media_list,
             event.change) = info
            if name:
                if event_conversion.has_key(name):
                    the_type = (event_conversion[name],"")
                else:
                    the_type = (Event.CUSTOM,name)
            else:
                the_type = (Event.UNKNOWN,"")
            
            self.commit_event(event,trans)
            data = cursor.next()
        cursor.close()

        # Work out marker addition to the Place
        cursor = self.get_place_cursor()
        data = cursor.first()
        while data:
            handle,info = data
            place = Place()
            place.handle = handle
            (junk_handle, place.gramps_id, place.title, place.long, place.lat,
             place.main_loc, place.alt_loc, place.urls, place.media_list,
             place.source_list, place.note, place.change) = info
            self.commit_place(place,trans)
            data = cursor.next()
        cursor.close()

        # Work out marker addition to the Media
        cursor = self.get_media_cursor()
        data = cursor.first()
        while data:
            handle,info = data
            media_object = MediaObject()
            media_object.handle = handle
            (junk_handle, media_object.gramps_id, media_object.path,
             media_object.mime, media_object.desc, media_object.attribute_list,
             media_object.source_list, media_object.note, media_object.change,
             media_object.date) = info
            self.commit_media_object(media_object,trans)
            data = cursor.next()
        cursor.close()

        self.transaction_commit(trans,"Upgrade to DB version 9")
        print "Done upgrading to DB version 9"

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
