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
import os
import time
import locale
from gettext import gettext as _
from bsddb import dbshelve, db

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *
from GrampsDbBase import *

_DBVERSION = 5

def find_surname(key,data):
    return str(data[3].get_surname())

def find_idmap(key,data):
    return str(data[1])

def find_fidmap(key,data):
    return str(data[1])

def find_eventname(key,data):
    return str(data[2])

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

    def get_event_cursor(self):
        return GrampsBSDDBCursor(self.event_map)

    def get_place_cursor(self):
        return GrampsBSDDBCursor(self.place_map)

    def get_source_cursor(self):
        return GrampsBSDDBCursor(self.source_map)

    def get_media_cursor(self):
        return GrampsBSDDBCursor(self.media_map)

    def need_upgrade(self):
        return not self.readonly and self.metadata.get('version',0) < _DBVERSION

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

        if not self.readonly:
            if gstats == None:
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
        if self.person_map == None:
            return
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

    def _del_person(self,handle):
        self.person_map.delete(str(handle))

    def _del_source(self,handle):
        self.source_map.delete(str(handle))

    def _del_place(self,handle):
        self.place_map.delete(str(handle))

    def _del_media(self,handle):
        self.media_map.delete(str(handle))

    def _del_family(self,handle):
        self.family_map.delete(str(handle))

    def _del_event(self,handle):
        self.event_map.delete(str(handle))

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
        
        version = self.metadata.get('version',0)
        if version < 2:
            self.upgrade_2(child_rel_notrans)
        if version < 3:
            self.upgrade_3()
        if version < 4:
            self.upgrade_4(child_rel_notrans)
        if version < 5:
            self.upgrade_5()
        self.metadata['version'] = _DBVERSION
        print 'Successfully finished all upgrades'

    def upgrade_2(self,child_rel_notrans):
        print "Upgrading to DB version 2"
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

    def upgrade_3(self):
        print "Upgrading to DB version 3"
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

    def upgrade_4(self,child_rel_notrans):
        print "Upgrading to DB version 4"
        cursor = self.get_person_cursor()
        data = cursor.first()
        while data:
            handle,info = data
            person = Person()
            person.unserialize(info)
                
            plist = person.get_parent_family_handle_list()
            new_list = []
            change = False
            for (f,mrel,frel) in plist:
                if type(mrel) == str:
                    mrel = child_rel_notrans.index(mrel)
                    change = True
                if type(frel) == str:
                    frel = child_rel_notrans.index(frel)
                    change = True
                new_list.append((f,mrel,frel))
            if change:
                person.parent_family_list = new_list
                self.commit_person(person,None)
            data = cursor.next()
        cursor.close()

    def upgrade_5(self):
        print "Upgrading to DB version 5 -- this may take a while"
        # Need to rename:
        #       attrlist into attribute_list in MediaRefs
        #       comments into note in SourceRefs
        # in all primary and secondary objects
        # Also MediaObject gets place attribute removed

        cursor = self.get_media_cursor()
        data = cursor.first()
        while data:
            changed = False
            handle,info = data
            obj = MediaObject()
            # can't use unserialize here, since the new class
            # defines tuples one element short
            if len(info) == 11:
                (obj.handle, obj.gramps_id, obj.path, obj.mime, obj.desc,
                obj.attribute_list, obj.source_list, obj.note, obj.change,
                obj.date, junk) = info
                changed = True
            else:
                obj.unserialize(info)
            for src_ref in obj.source_list:
                if 'comments' in dir(src_ref):
                    src_ref.note = src_ref.comments
                    del src_ref.comments
                    changed = True
            for attr in obj.attribute_list:
                for src_ref in attr.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
            if changed:
                self.commit_media_object(obj,None)
            data = cursor.next()
        cursor.close()
        # person
        cursor = self.get_person_cursor()
        data = cursor.first()
        while data:
            changed = False
            handle,info = data
            person = Person()
            person.unserialize(info)
            for media_ref in person.media_list:
                if 'attrlist' in dir(media_ref):
                    media_ref.attribute_list = media_ref.attrlist
                    del media_ref.attrlist
                    changed = True
                for src_ref in media_ref.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
                for attr in media_ref.attribute_list:
                    for src_ref in attr.source_list:
                        if 'comments' in dir(src_ref):
                            src_ref.note = src_ref.comments
                            del src_ref.comments
                            changed = True
            for src_ref in person.source_list:
                if 'comments' in dir(src_ref):
                    src_ref.note = src_ref.comments
                    del src_ref.comments
                    changed = True
            for attr in person.attribute_list:
                for src_ref in attr.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
            for o in [o for o in [person.lds_bapt,
                                person.lds_endow,
                                person.lds_seal] if o]:
                for src_ref in o.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
            for name in person.alternate_names + [person.primary_name]:
                for src_ref in name.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
            for addr in person.address_list:
                for src_ref in addr.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
            if changed:
                self.commit_person(person,None)
            data = cursor.next()
        cursor.close()
        # family
        cursor = self.get_family_cursor()
        data = cursor.first()
        while data:
            changed = False
            handle,info = data
            family = Family()
            family.unserialize(info)
            for media_ref in family.media_list:
                if 'attrlist' in dir(media_ref):
                    media_ref.attribute_list = media_ref.attrlist
                    del media_ref.attrlist
                    changed = True
                for src_ref in media_ref.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
                for attr in media_ref.attribute_list:
                    for src_ref in attr.source_list:
                        if 'comments' in dir(src_ref):
                            src_ref.note = src_ref.comments
                            del src_ref.comments
                            changed = True
            for src_ref in family.source_list:
                if 'comments' in dir(src_ref):
                    src_ref.note = src_ref.comments
                    del src_ref.comments
                    changed = True
            for attr in family.attribute_list:
                for src_ref in attr.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
            if family.lds_seal:
                for src_ref in family.lds_seal.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
            if changed:
                self.commit_family(family,None)
            data = cursor.next()
        cursor.close()
        # event
        cursor = self.get_event_cursor()
        data = cursor.first()
        while data:
            changed = False
            handle,info = data
            event = Event()
            event.unserialize(info)
            changed = event.media_list or event.source_list
            for media_ref in event.media_list:
                if 'attrlist' in dir(media_ref):
                    media_ref.attribute_list = media_ref.attrlist
                    del media_ref.attrlist
                    changed = True
                for src_ref in media_ref.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
                for attr in media_ref.attribute_list:
                    for src_ref in attr.source_list:
                        if 'comments' in dir(src_ref):
                            src_ref.note = src_ref.comments
                            del src_ref.comments
                            changed = True
            for src_ref in event.source_list:
                if 'comments' in dir(src_ref):
                    src_ref.note = src_ref.comments
                    del src_ref.comments
                    changed = True
            if changed:
                self.commit_event(event,None)
            data = cursor.next()
        cursor.close()
        # place
        cursor = self.get_place_cursor()
        data = cursor.first()
        while data:
            changed = False
            handle,info = data
            place = Place()
            place.unserialize(info)
            for media_ref in place.media_list:
                if 'attrlist' in dir(media_ref):
                    media_ref.attribute_list = media_ref.attrlist
                    del media_ref.attrlist
                    changed = True
                for src_ref in media_ref.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
                for attr in media_ref.attribute_list:
                    for src_ref in attr.source_list:
                        if 'comments' in dir(src_ref):
                            src_ref.note = src_ref.comments
                            del src_ref.comments
                            changed = True
            for src_ref in place.source_list:
                if 'comments' in dir(src_ref):
                    src_ref.note = src_ref.comments
                    del src_ref.comments
                    changed = True
            if changed:
                self.commit_place(place,None)
            data = cursor.next()
        cursor.close()
        # source
        cursor = self.get_source_cursor()
        data = cursor.first()
        while data:
            changed = False
            handle,info = data
            source = Source()
            source.unserialize(info)
            for media_ref in source.media_list:
                if 'attrlist' in dir(media_ref):
                    media_ref.attribute_list = media_ref.attrlist
                    del media_ref.attrlist
                    changed = True
                for src_ref in media_ref.source_list:
                    if 'comments' in dir(src_ref):
                        src_ref.note = src_ref.comments
                        del src_ref.comments
                        changed = True
                for attr in media_ref.attribute_list:
                    for src_ref in attr.source_list:
                        if 'comments' in dir(src_ref):
                            src_ref.note = src_ref.comments
                            del src_ref.comments
                            changed = True
            if changed:
                self.commit_source(source,None)
            data = cursor.next()
        cursor.close()
