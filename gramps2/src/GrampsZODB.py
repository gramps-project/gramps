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
from ZODB.PersistentList import PersistentList
from ZODB.dbmStorage import gdbmStorage
from ZODB.DB import DB
from BTrees.OOBTree import OOBTree
from UserDict import UserDict
import RelLib
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
        self.id = real.get_id()
        self.PrimaryName = real.get_primary_name()
        self.gender = real.get_gender()
        self.birth = real.get_birth()
        self.death = real.get_death()

    def _notifyChange(self):
        # Trigger a change to the PersonMap.
        self._map_ref.getOb()[self.id] = self

    def get_id(self):
        return self.id

    def set_id(self, id):
        self._real.set_id(id)
        self.id = self._real.get_id()
        self._notifyChange()

    def get_primary_name(self):
        return self.PrimaryName

    def set_primary_name(self, name):
        self._real.set_primary_name(name)
        self.PrimaryName = self._real.get_primary_name()
        self._notifyChange()

    def get_gender(self):
        return self.gender

    def set_gender(self, gender):
        self._real.set_gender(gender)
        self.gender = self._real.get_gender()
        self._notifyChange()

    def get_birth(self):
        return self.birth

    def set_birth(self, birth):
        self._real.set_birth(birth)
        self.birth = self._real.get_birth()
        self._notifyChange()

    def get_death(self):
        return self.death

    def set_death(self, death):
        self._real.set_death(death)
        self.death = self._real.get_death()
        self._notifyChange()


for key, value in RelLib.Person.__dict__.items():
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
            assert isinstance(value, RelLib.Person)
            value = PersonWrapper(value, self)
        self.data[key] = value

    def update(self):
        # This probably shouldn't be called anyway.
        raise NotImplementedError

    def copy(self):
        # This probably shouldn't be called anyway.
        raise NotImplementedError
    
class GrampsZODB(RelLib.GrampsDB):

    def __init__(self):
        self.conn = None
        RelLib.GrampsDB.__init__(self)

    def get_type(self):
        return 'GrampsZODB'

    def close(self):
        self.db.close()

    def get_base(self):
        return const.zodbFile

    def need_autosave(self):
        return 0
        
    def new(self):
        RelLib.GrampsDB.new(self)
        self.familyMap = OOBTree()
        self.personMap = PersonMap()
        self.sourceMap = OOBTree()
        self.placeMap = OOBTree()
        self.personTable = OOBTree()
        self.placeTable = OOBTree()
        self.sourceTable = OOBTree()
        self.need_commit = 0
        
        if self.conn:
            self.db.close()
            self.conn.close()
            self.conn = None

    def save(self,name,callback):
        get_transaction().commit()
        if self.conn == None:
            self.load(name,callback)

    def get_object(self,tag):
        if self.root.has_key(tag):
            item = self.root[tag]
        else:
            item = OOBTree()
            self.root[tag] = item
            self.need_commit = 1
        return item

    def get_display_table(self,src,tag):
        if self.root.has_key(tag):
            table = self.root[tag]
        else:
            table = OOBTree()
            for key in src.keys():
                obj = src[key]
                table[key] = obj.get_display_info()
            self.root[tag] = table
            self.need_commit = 1
        return table

    def load(self,name,callback):
        self.db = DB(gdbmStorage(name,'w'))
        self.conn = self.db.open()
        self.root = self.conn.root()
        self.need_commit = 0

        self.familyMap = self.get_object('familyMap')

        if self.root.has_key('personMap'):
            self.personMap = self.root['personMap']
        else:
            self.personMap = PersonMap()
            self.root['personMap'] = self.personMap
            self.need_commit = 1

        self.personTable = self.get_display_table(self.personMap,'personTable')

        if self.root.has_key('surnames'):
            self.surnames = self.root['surnames']
        else:
            self.surnames = PersistentList()
            for key in self.personMap.keys():
                person = self.personMap[key]
                self.add_surname(person.get_primary_name().get_surname())
            self.root['surnames'] = self.surnames
            self.need_commit = 1

        self.sourceMap = self.get_object('sourceMap')
        self.sourceTable = self.get_display_table(self.sourceMap,'sourceTable')

        self.placeMap = self.get_object('placeMap')
        self.placeTable = self.get_display_table(self.placeMap,'placeTable')
        
        if self.root.has_key('default'):
            self.default = self.root['default']
        else:
            self.default = None
            self.root['default'] = self.default
            self.need_commit = 1

        if self.root.has_key('bookmarks'):
            self.bookmarks = self.root['bookmarks']
        else:
            self.bookmarks = []
            self.root['bookmarks'] = self.bookmarks
            self.need_commit = 1
        if self.need_commit:
            get_transaction().commit()
        return 1

    def set_default_person(self,person):
        """sets the default Person to the passed instance"""
        RelLib.GrampsDB.set_default_person(self,person)
        self.root['default'] = person
        




















