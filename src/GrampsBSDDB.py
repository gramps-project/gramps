#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

import os
import time
import locale
from gettext import gettext as _

from RelLib import *
from GrampsDbBase import *
from bsddb import dbshelve, db

_DBVERSION = 3

def find_surname(key,data):
    return str(data[3].get_surname())

def find_idmap(key,data):
    return str(data[1])

def find_fidmap(key,data):
    return str(data[1])

def find_eventname(key,data):
    return str(data[1])

class GrampsBSDDBCursor(GrampsCursor):

    def __init__(self,source):
        self.cursor = source.cursor()
        
    def first(self):
        return self.cursor.first()

    def next(self):
        return self.cursor.next()

    def close(self):
        self.cursor.close()

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

    def get_place_cursor(self):
        return GrampsBSDDBCursor(self.place_map)

    def get_source_cursor(self):
        return GrampsBSDDBCursor(self.source_map)

    def get_media_cursor(self):
        return GrampsBSDDBCursor(self.media_map)

    def need_upgrade(self):
        return self.metadata['version'] < _DBVERSION

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

        self.family_map = self.dbopen(name, "family")
        self.place_map  = self.dbopen(name, "places")
        self.source_map = self.dbopen(name, "sources")
        self.media_map  = self.dbopen(name, "media")
        self.event_map  = self.dbopen(name, "events")
        self.metadata   = self.dbopen(name, "meta")
        self.person_map = self.dbopen(name, "person")

        if self.readonly:
            openflags = db.DB_RDONLY
        else:
            openflags = db.DB_CREATE

        self.surnames = db.DB(self.env)
        self.surnames.set_flags(db.DB_DUP)
        self.surnames.open(name, "surnames", db.DB_HASH, flags=openflags)

        self.name_group = db.DB(self.env)
        self.name_group.set_flags(db.DB_DUP)
        self.name_group.open(name, "name_group", db.DB_HASH, flags=openflags)

        self.id_trans = db.DB(self.env)
        self.id_trans.set_flags(db.DB_DUP)
        self.id_trans.open(name, "idtrans", db.DB_HASH, flags=openflags)

        self.fid_trans = db.DB(self.env)
        self.fid_trans.set_flags(db.DB_DUP)
        self.fid_trans.open(name, "fidtrans", db.DB_HASH, flags=openflags)

        self.pid_trans = db.DB(self.env)
        self.pid_trans.set_flags(db.DB_DUP)
        self.pid_trans.open(name, "pidtrans", db.DB_HASH, flags=openflags)

        self.sid_trans = db.DB(self.env)
        self.sid_trans.set_flags(db.DB_DUP)
        self.sid_trans.open(name, "sidtrans", db.DB_HASH, flags=openflags)

        self.oid_trans = db.DB(self.env)
        self.oid_trans.set_flags(db.DB_DUP)
        self.oid_trans.open(name, "oidtrans", db.DB_HASH, flags=openflags)

        self.eventnames = db.DB(self.env)
        self.eventnames.set_flags(db.DB_DUP)
        self.eventnames.open(name, "eventnames", db.DB_HASH, flags=openflags)

        if not self.readonly:
            self.person_map.associate(self.surnames,  find_surname, openflags)
            self.person_map.associate(self.id_trans,  find_idmap, openflags)
            self.family_map.associate(self.fid_trans, find_idmap, openflags)
            self.place_map.associate(self.pid_trans,  find_idmap, openflags)
            self.media_map.associate(self.oid_trans, find_idmap, openflags)
            self.source_map.associate(self.sid_trans, find_idmap, openflags)
            self.event_map.associate(self.eventnames, find_eventname, openflags)
            self.undodb = db.DB()
            self.undodb.open(self.undolog, db.DB_RECNO, db.DB_CREATE)

        self.metadata   = self.dbopen(name, "meta")
        self.bookmarks = self.metadata.get('bookmarks')

        gstats = self.metadata.get('gender_stats')

        if not self.readonly and gstats == None:
            self.metadata['version'] = _DBVERSION
        elif not self.metadata.has_key('version'):
            self.metadata['version'] = 0

        if self.bookmarks == None:
            self.bookmarks = []

        self.genderStats = GenderStats(gstats)
        return 1

    def abort_changes(self):
        while self.undo():
            pass
        self.close()

    def close(self):
        self.name_group.close()
        self.person_map.close()
        self.family_map.close()
        self.place_map.close()
        self.source_map.close()
        self.media_map.close()
        self.event_map.close()
        if not self.readonly:
            self.metadata['bookmarks'] = self.bookmarks
            self.metadata['gender_stats'] = self.genderStats.save_stats()
        self.metadata.close()
        self.surnames.close()
        self.eventnames.close()
        self.id_trans.close()
        self.fid_trans.close()
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
        
        self.person_map = None
        self.family_map = None
        self.place_map  = None
        self.source_map = None
        self.media_map  = None
        self.event_map  = None
        self.surnames   = None
        self.env        = None
        self.metadata   = None

    def set_name_group_mapping(self,name,group):
        if not self.readonly:
            name = str(name)
            if not group and self.name_group.has_key(name):
                self.name_group.delete(name)
            else:
                self.name_group[name] = group
            
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

    def remove_person(self,handle,transaction):
        if not self.readonly:
            person = self.get_person_from_handle(handle)
            self.genderStats.uncount_person (person)
            if transaction != None:
                transaction.add(PERSON_KEY,handle,person.serialize())
            self.person_map.delete(str(handle))

    def remove_source(self,handle,transaction):
        if not self.readonly:
            if transaction != None:
                old_data = self.source_map.get(str(handle))
                transaction.add(SOURCE_KEY,handle,old_data)
            self.source_map.delete(str(handle))

    def remove_family(self,handle,transaction):
        if not self.readonly:
            if transaction != None:
                old_data = self.family_map.get(str(handle))
                transaction.add(FAMILY_KEY,handle,old_data)
            self.family_map.delete(str(handle))

    def remove_event(self,handle,transaction):
        if not self.readonly:
            if transaction != None:
                old_data = self.event_map.get(str(handle))
                transaction.add(EVENT_KEY,handle,old_data)
            self.event_map.delete(str(handle))

    def remove_place(self,handle,transaction):
        if not self.readonly:
            if transaction != None:
                old_data = self.place_map.get(handle)
                transaction.add(PLACE_KEY,handle,old_data)
            self.place_map.delete(str(handle))

    def remove_object(self,handle,transaction):
        if not self.readonly:
            if transaction != None:
                old_data = self.media_map.get(handle)
                transaction.add(PLACE_KEY,handle,old_data)
            self.media_map.delete(str(handle))

    def get_person_from_gramps_id(self,val):
        """finds a Person in the database from the passed gramps' ID.
        If no such Person exists, a new Person is added to the database."""

        data = self.id_trans.get(str(val))
        if data:
            person = Person()
            person.unserialize(cPickle.loads(data))
            return person
        else:
            return None

    def get_family_from_gramps_id(self,val):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Person is added to the database."""

        data = self.fid_trans.get(str(val))
        if data:
            family = Family()
            family.unserialize(cPickle.loads(data))
            return family
        else:
            return None

    def get_place_from_gramps_id(self,val):
        """finds a Place in the database from the passed gramps' ID.
        If no such Place exists, a new Person is added to the database."""

        data = self.pid_trans.get(str(val))
        if data:
            place = Place()
            place.unserialize(cPickle.loads(data))
            return place
        else:
            return None

    def get_source_from_gramps_id(self,val):
        """finds a Source in the database from the passed gramps' ID.
        If no such Source exists, a new Person is added to the database."""

        data = self.sid_trans.get(str(val))
        if data:
            source = Source()
            source.unserialize(cPickle.loads(data))
            return source
        else:
            return None

    def get_object_from_gramps_id(self,val):
        """finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, a new Person is added to the database."""

        data = self.oid_trans.get(str(val))
        if data:
            obj = MediaObject()
            obj.unserialize(cPickle.loads(data))
            return obj
        else:
            return None

    def upgrade(self):
        child_rel_notrans = [
            "None",      "Birth",  "Adopted", "Stepchild",
            "Sponsored", "Foster", "Unknown", "Other", ]
        
        version = self.metadata['version']
        if version < 2:
            cursor = self.get_person_cursor()
            data = cursor.first()
            while data:
                handle,info = data
                person = Person()
                person.unserialize(info)
                    
                plist = person.get_parent_family_handle_list()
                new_list = []
                for (f,mrel,frel) in plist:
                    try:
                        mrel = child_rel_notrans.index(mrel)
                    except:
                        mrel = Person.CHILD_REL_BIRTH
                    try:
                        frel = child_rel_notrans.index(frel)
                    except:
                        frel = Person.CHILD_REL_BIRTH
                    new_list.append((f,mrel,frel))
                person.parent_family_list = new_list
                self.commit_person(person,None)
                data = cursor.next()
            cursor.close()
        if version < 3:
            cursor = self.get_person_cursor()
            data = cursor.first()
            while data:
                handle,info = data
                person = Person()
                person.unserialize(info)

                person.primary_name.date = None
                for name in person.alternate_names:
                    name.date = None
                self.commit_person(person,None)
                data = cursor.next()
            cursor.close()
        self.metadata['version'] = 3
