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

import os
import time
import locale

from RelLib import *
from GrampsDbBase import *
from bsddb import dbshelve, db

def find_surname(key,data):
    return str(data[3].get_surname())

def find_idmap(key,data):
    return str(data[1])

def find_fidmap(key,data):
    return str(data[1])

def find_eventname(key,data):
    return str(data[1])

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

    def load(self,name,callback):
        if self.person_map:
            self.close()

        self.env = db.DBEnv()
        self.env.set_cachesize(0,4*1024*1024) # 2MB
        flags = db.DB_CREATE|db.DB_INIT_MPOOL|db.DB_PRIVATE

        self.undolog = "%s.log" % name
        self.env.open(os.path.dirname(name), flags)
            
        name = os.path.basename(name)
        self.person_map = dbshelve.open(name, dbname="person", dbenv=self.env)
        self.family_map = dbshelve.open(name, dbname="family", dbenv=self.env)
        self.place_map  = dbshelve.open(name, dbname="places", dbenv=self.env)
        self.source_map = dbshelve.open(name, dbname="sources",dbenv=self.env)
        self.media_map  = dbshelve.open(name, dbname="media",  dbenv=self.env)
        self.event_map  = dbshelve.open(name, dbname="events", dbenv=self.env)
        self.metadata   = dbshelve.open(name, dbname="meta",   dbenv=self.env)

        self.surnames = db.DB(self.env)
        self.surnames.set_flags(db.DB_DUP)
        self.surnames.open(name, "surnames", db.DB_HASH, flags=db.DB_CREATE)

        self.id_trans = db.DB(self.env)
        self.id_trans.set_flags(db.DB_DUP)
        self.id_trans.open(name, "idtrans", db.DB_HASH, flags=db.DB_CREATE)

        self.fid_trans = db.DB(self.env)
        self.fid_trans.set_flags(db.DB_DUP)
        self.fid_trans.open(name, "fidtrans", db.DB_HASH, flags=db.DB_CREATE)

        self.pid_trans = db.DB(self.env)
        self.pid_trans.set_flags(db.DB_DUP)
        self.pid_trans.open(name, "pidtrans", db.DB_HASH, flags=db.DB_CREATE)

        self.sid_trans = db.DB(self.env)
        self.sid_trans.set_flags(db.DB_DUP)
        self.sid_trans.open(name, "sidtrans", db.DB_HASH, flags=db.DB_CREATE)

        self.oid_trans = db.DB(self.env)
        self.oid_trans.set_flags(db.DB_DUP)
        self.oid_trans.open(name, "oidtrans", db.DB_HASH, flags=db.DB_CREATE)

        self.eventnames = db.DB(self.env)
        self.eventnames.set_flags(db.DB_DUP)
        self.eventnames.open(name, "eventnames", db.DB_HASH, flags=db.DB_CREATE)
        self.person_map.associate(self.surnames,  find_surname, db.DB_CREATE)
        self.person_map.associate(self.id_trans,  find_idmap, db.DB_CREATE)
        self.family_map.associate(self.fid_trans, find_idmap, db.DB_CREATE)
        self.place_map.associate(self.pid_trans,  find_idmap, db.DB_CREATE)
        self.media_map.associate(self.oid_trans, find_idmap, db.DB_CREATE)
        self.source_map.associate(self.sid_trans, find_idmap, db.DB_CREATE)
        self.event_map.associate(self.eventnames, find_eventname, db.DB_CREATE)

        self.undodb = db.DB()
        self.undodb.open(self.undolog, db.DB_RECNO, db.DB_CREATE)
        
        self.bookmarks = self.metadata.get('bookmarks')
        if self.bookmarks == None:
            self.bookmarks = []

        self.genderStats = GenderStats(self.metadata.get('gender_stats'))
        return 1

    def close(self):
        self.person_map.close()
        self.family_map.close()
        self.place_map.close()
        self.source_map.close()
        self.media_map.close()
        self.event_map.close()
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
        person = self.get_person_from_handle(handle)
        self.genderStats.uncount_person (person)
        if transaction != None:
            transaction.add(PERSON_KEY,handle,person.serialize())
        self.person_map.delete(str(handle))

    def remove_source(self,handle,transaction):
        if transaction != None:
            old_data = self.source_map.get(str(handle))
            transaction.add(SOURCE_KEY,handle,old_data)
        self.source_map.delete(str(handle))

    def remove_family(self,handle,transaction):
        if transaction != None:
            old_data = self.family_map.get(str(handle))
            transaction.add(FAMILY_KEY,handle,old_data)
        self.family_map.delete(str(handle))

    def remove_event(self,handle,transaction):
        if transaction != None:
            old_data = self.event_map.get(str(handle))
            transaction.add(EVENT_KEY,handle,old_data)
        self.event_map.delete(str(handle))

    def remove_place(self,handle,transaction):
        if transaction != None:
            old_data = self.place_map.get(handle)
            transaction.add(PLACE_KEY,handle,old_data)
        self.place_map.delete(str(handle))

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
