#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002  Donald N. Allingham
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

from ZODB import Persistent
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
from BTrees.OOBTree import OOBTree
from UserDict import UserDict
from RelLib import GrampsDB, Person
import const

class PersistentReference(Persistent):

    def __init__(self, ob):
        self.ob = ob

    def getOb(self):
        return self.ob

class PersonWrapper:

    _real = None

    def __init__(self, real, map):
        self._real = real
        self._map_ref = PersistentReference(map)
        self.id = real.getId()
        self.PrimaryName = real.getPrimaryName()
        self.gender = real.getGender()
        self.birth = real.getBirth()
        self.death = real.getDeath()

    def _notifyChange(self):
        # Trigger a change to the PersonMap.
        self._map_ref.getOb()[self.id] = self

    def getId(self):
        return self.id

    def setId(self, id):
        self._real.setId(id)
        self.id = self._real.getId()
        self._notifyChange()

    def getPrimaryName(self):
        return self.PrimaryName

    def setPrimaryName(self, name):
        self._real.setPrimaryName(name)
        self.PrimaryName = self._real.getPrimaryName()
        self._notifyChange()

    def getGender(self):
        return self.gender

    def setGender(self, gender):
        self._real.setGender(gender)
        self.gender = self._real.getGender()
        self._notifyChange()

    def getBirth(self):
        return self.birth

    def setBirth(self, birth):
        self._real.setBirth(birth)
        self.birth = self._real.getBirth()
        self._notifyChange()

    def getDeath(self):
        return self.death

    def setDeath(self, death):
        self._real.setDeath(death)
        self.death = self._real.getDeath()
        self._notifyChange()


for key, value in Person.__dict__.items():
    if not key.startswith('_'):
        code = ("def %s(self, *args, **kw): "
                "return apply(self._real.%s, args, kw)") % (key, key)
        d = {}
        exec code in d
        PersonWrapper.__dict__[key] = d[key]


class PersonMap(Persistent, UserDict):

    def __init__(self):
        self.data = OOBTree()

    def __setitem__(self, key, value):
        if not isinstance(value, PersonWrapper):
            # Create the PersonWrapper.
            assert isinstance(value, Person)
            value = PersonWrapper(value, self)
        self.data[key] = value

    def update(self):
        # This probably shouldn't be called anyway.
        raise NotImplementedError

    def copy(self):
        # This probably shouldn't be called anyway.
        raise NotImplementedError
    

class GrampsZODB(GrampsDB):

    def __init__(self):
        self.conn = None
        GrampsDB.__init__(self)

    def get_base(self):
        return const.zodbFile

    def need_autosave(self):
        return 0
        
    def new(self):
        GrampsDB.new(self)
        self.familyMap = OOBTree()
        self.personMap = PersonMap()
        self.sourceMap = OOBTree()
        self.placeMap = OOBTree()
        self.personTable = OOBTree()
        self.placeTable = OOBTree()
        if self.conn:
            self.db.close()
            self.conn.close()
            self.conn = None

    def save(self,name,callback):
        get_transaction().commit()
        if self.conn == None:
            self.load(name,callback)

    def load(self,name,callback):
        import time
        t = time.time()
        print 'opening storage'
        s = FileStorage(name)
        t1 = time.time()
        print t1 - t
        print 'getting DB'
        self.db = DB(s)
        t = time.time()
        print t - t1
        print 'establishing connect'
        self.conn = self.db.open()
        t1 = time.time()
        print t1 -t
        print 'getting root'
        root = self.conn.root()
        t = time.time()
        print t - t1
        print 'family map'
        need_commit = 0
        if root.has_key('fm'):
            self.familyMap = root['fm']
        else:
            self.familyMap = OOBTree()
            root['fm'] = self.familyMap
            need_commit = 1
        t1 = time.time()
        print t1 - t
        
        print 'person map'
        if root.has_key('pm'):
            self.personMap = root['pm']
        else:
            self.personMap = PersonMap()
            root['pm'] = self.personMap
            need_commit = 1
        t = time.time()
        print t - t1

        print 'person index table'
        if root.has_key('pmt'):
            self.personTable = root['pmt']
        else:
            for key in self.personMap.keys():
                person = self.personMap[key]
                self.personTable[key] = person.getDisplayInfo()
            root['pmt'] = self.personTable
            need_commit = 1
        t1 = time.time()
        print t1 - t

        print 'surnames'
        if root.has_key('surnames'):
            self.surnames = root['surnames']
        else:
            for key in self.personMap.keys():
                person = self.personMap[key]
                self.addSurname(person.getPrimaryName().getSurname())
            root['surnames'] = self.surnames
            need_commit = 1
        t = time.time()
        print t - t1

        print 'source map'
        if root.has_key('sm'):
            self.sourceMap = root['sm']
        else:
            self.sourceMap = OOBTree()
            root['sm'] = self.sourceMap
            need_commit = 1
        t1 = time.time()
        print t1 - t

        print 'source index table'
        if root.has_key('smt'):
            self.sourceTable = root['smt']
        else:
            for key in self.sourceMap.keys():
                src = self.sourceMap[key]
                self.sourceTable[key] = src.getDisplayInfo()
            root['smt'] = self.sourceTable
            need_commit = 1
        t = time.time()
        print t - t1

        print 'place map'
        if root.has_key('plm'):
            self.placeMap = root['plm']
        else:
            self.placeMap = OOBTree()
            root['plm'] = self.placeMap
            need_commit = 1
        t1 = time.time()
        print t1 - t

        print 'place index'
        if root.has_key('plmt'):
            self.placeTable = root['plmt']
        else:
            for key in self.placeMap.keys():
                place = self.placeMap[key]
                self.placeTable[key] = place.getDisplayInfo()
            root['plmt'] = self.placeTable
            need_commit = 1
        t = time.time()
        print t - t1

        print 'default person'
        if root.has_key('default'):
            self.default = root['default']
        else:
            self.default = None
            root['default'] = self.default
            need_commit = 1
        t1 = time.time()
        print t1 - t

        print 'bookmarks'
        if root.has_key('bookmarks'):
            self.bookmarks = root['bookmarks']
        else:
            self.bookmarks = []
            root['bookmarks'] = self.bookmarks
            need_commit = 1
        t = time.time()
        print t - t1

        if need_commit:
            print 'committing'
            get_transaction().commit()
        t1 = time.time()
        print t1 - t
        print 'done'
        return 1

    def setDefaultPerson(self,person):
        """sets the default Person to the passed instance"""
        GrampsDB.setDefaultPerson(self,person)
        self.conn.root()['default'] = person
        
    def removePerson(self,id):
        GrampsDB.removePerson(self,id)
        del self.personTable[id]

    def removeSource(self,id):
        GrampsDB.removeSource(self,id)
        del self.sourceTable[id]

    def removePlace(self,id):
        GrampsDB.removePlace(self,id)
        del self.placeTable[id]

    def addPersonAs(self,person):
        GrampsDB.addPersonAs(self,person)
        self.personTable[person.getId()] = person.getDisplayInfo()

    def addPlaceAs(self,place):
        GrampsDB.addPlaceAs(self,place)
        self.placeTable[place.getId()] = place.getDisplayInfo()

    def addPerson(self,person):
        i = GrampsDB.addPerson(self,person)
        self.personTable[i] = person.getDisplayInfo()
        return i

    def addPlace(self,place):
        i = GrampsDB.addPlace(self,place)
        self.placeTable[i] = place.getDisplayInfo()
        return i

    def addPersonNoMap(self,person,id):
        GrampsDB.addPersonNoMap(self,person,id)
        self.personTable[id] = person.getDisplayInfo()
        return id

    def addPlaceNoMap(self,place,id):
        GrampsDB.addPlaceNoMap(self,place,id)
        self.placeTable[id] = place.getDisplayInfo()
        return id
    
    def findPersonNoMap(self,val):
        p = GrampsDB.findPersonNoMap(self,val)
        self.personTable[p.getId()] = p.getDisplayInfo()
        return p

    def findPlaceNoMap(self,val):
        p = GrampsDB.findPlaceNoMap(self,val)
        self.placeTable[p.getId()] = p.getDisplayInfo()
        return p
    
    def findPerson(self,idVal,map):
        p = GrampsDB.findPerson(self,idVal,map)
        self.personTable[p.getId()] = p.getDisplayInfo()
        return p

    def findPlace(self,idVal,map):
        p = GrampsDB.findPlace(self,idVal,map)
        self.placeTable[p.getId()] = p.getDisplayInfo()
        return p

    def addSource(self,source):
        i = GrampsDB.addSource(self,source)
        self.sourceTable[i] = source.getDisplayInfo()
        return i

    def addSourceNoMap(self,source,id):
        GrampsDB.addSourceNoMap(self,source,id)
        self.sourceTable[id] = source.getDisplayInfo()
        return id

    def findSourceNoMap(self,val):
        p = GrampsDB.findSourceNoMap(self,val)
        self.sourceTable[p.getId()] = p.getDisplayInfo()
        return p

    def findSource(self,idVal,map):
        p = GrampsDB.findSource(self,idVal,map)
        self.sourceTable[p.getId()] = p.getDisplayInfo()
        return p
