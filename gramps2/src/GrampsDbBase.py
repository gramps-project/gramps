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
Base class for the GRAMPS databases. All database interfaces should inherit
from this class.
"""

#-------------------------------------------------------------------------
#
# libraries
#
#-------------------------------------------------------------------------
import cPickle
import time
import random
import locale
import re
from sys import maxint
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS libraries
#
#-------------------------------------------------------------------------
from RelLib import *
import GrampsKeys
import GrampsDBCallback

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
_UNDO_SIZE = 1000
_id_reg    = re.compile("%\d+d")

PERSON_KEY     = 0
FAMILY_KEY     = 1
SOURCE_KEY     = 2
EVENT_KEY      = 3
MEDIA_KEY      = 4
PLACE_KEY      = 5

PERSON_COL_KEY = 'columns'
CHILD_COL_KEY  = 'child_columns'
PLACE_COL_KEY  = 'place_columns'
SOURCE_COL_KEY = 'source_columns'
MEDIA_COL_KEY  = 'media_columns'

_sigbase = ('person', 'family', 'source', 'event', 'media', 'place')

class GrampsCursor:
    """
    Provides a basic iterator that allows the user to cycle through
    the elements in a particular map. A cursor should never be
    directly instantiated. Instead, in should be created by the
    database class.

    A cursor should only be used for a single pass through the
    database. If multiple passes are needed, multiple cursors
    should be used.
    """

    def first(self):
        """
        Returns the first (index, data) pair in the database. This
        should be called before the first call to next(). Note that
        the data return is in the format of the serialized format
        stored in the database, not in the more usable class object.
        The data should be converted to a class using the class's
        unserialize method.

        If no data is available, None is returned.
        """
        return None

    def next(self):
        """
        Returns the next (index, data) pair in the database. Like
        the first() method, the data return is in the format of the
        serialized format stored in the database, not in the more
        usable class object. The data should be converted to a class
        using the class's unserialize method.

        None is returned when no more data is available.
        """
        return None

    def close(self):
        """
        Closes the cursor. This should be called when the user is
        finished using the cursor, freeing up the cursor's resources.
        """
        pass

class GrampsDbBase(GrampsDBCallback.GrampsDBCallback):
    """
    GRAMPS database object. This object is a base class for all
    database interfaces.
    """

    __signals__ = {
        'person-add'     : (list,),
        'person-update'  : (list,),
        'person-delete'  : (list,),
        'person-rebuild' : None,
        'family-add'     : (list,),
        'family-update'  : (list,),
        'family-delete'  : (list,),
        'family-rebuild' : None,
        'source-add'     : (list,),
        'source-update'  : (list,),
        'source-delete'  : (list,),
        'source-rebuild' : None,
        'place-add'      : (list,),
        'place-update'   : (list,),
        'place-delete'   : (list,),
        'place-rebuild'  : None,
        'media-add'      : (list,),
        'media-update'   : (list,),
        'media-delete'   : (list,),
        'media-rebuild'  : None,
        'event-add'      : (list,),
        'event-update'   : (list,),
        'event-delete'   : (list,),
        'event-rebuild'  : None,
        }
    
    def __init__(self):
        """
        Creates a new GrampsDbBase instance. A new GrampDbBase class should
        never be directly created. Only classes derived from this class should
        be created.
        """

        GrampsDBCallback.GrampsDBCallback.__init__(self)
        
        self.readonly = False
        self.rand = random.Random(time.time())
        self.smap_index = 0
        self.emap_index = 0
        self.pmap_index = 0
        self.fmap_index = 0
        self.lmap_index = 0
        self.omap_index = 0

        self.set_person_id_prefix(GrampsKeys.get_person_id_prefix())
        self.set_object_id_prefix(GrampsKeys.get_object_id_prefix())
        self.set_family_id_prefix(GrampsKeys.get_family_id_prefix())
        self.set_source_id_prefix(GrampsKeys.get_source_id_prefix())
        self.set_place_id_prefix(GrampsKeys.get_place_id_prefix())
        self.set_event_id_prefix(GrampsKeys.get_event_id_prefix())

        self.open = 0
        self.genderStats = GenderStats()

        self.undodb    = None
        self.id_trans  = None
        self.fid_trans = None
        self.pid_trans = None
        self.sid_trans = None
        self.oid_trans = None
        self.env = None
        self.person_map = None
        self.family_map = None
        self.place_map  = None
        self.source_map = None
        self.media_map  = None
        self.event_map  = None
        self.eventnames = None
        self.metadata   = None
        self.name_group = None
        self.undo_callback = None
        self.redo_callback = None
        self.modified   = 0

        self.undoindex  = -1
        self.translist  = [None] * _UNDO_SIZE
        self.default = None
        self.owner = Researcher()
        self.bookmarks = []
        self.path = ""
        self.place2title = {}
        self.name_group = {}

    def need_upgrade(self):
        return False

    def upgrade(self):
        pass

    def create_id(self):
        return "%08x%08x" % ( int(time.time()*10000),
                              self.rand.randint(0,maxint))

    def get_person_cursor(self):
        assert False, "Needs to be overridden in the derived class"

    def get_family_cursor(self):
        assert False, "Needs to be overridden in the derived class"

    def get_place_cursor(self):
        assert False, "Needs to be overridden in the derived class"

    def get_source_cursor(self):
        assert False, "Needs to be overridden in the derived class"

    def get_media_cursor(self):
        assert False, "Needs to be overridden in the derived class"

    def load(self,name,callback):
        """
        Opens the specified database. The method needs to be overridden
        in the derived class.
        """
        assert False, "Needs to be overridden in the derived class"

    def close(self):
        """
        Closes the specified database. The method needs to be overridden
        in the derived class.
        """
        assert False, "Needs to be overridden in the derived class"
        
    def abort_changes(self):
        pass
    
    def is_open(self):
        """
        Returns 1 if the database has been opened.
        """
        return self.person_map != None

    def request_rebuild(self):
        """
        Notifies clients that the data has change significantly, and that all
        internal data dependent on the database should be rebuilt.
        """
        self.emit('person-rebuild')
        self.emit('family-rebuild')
        self.emit('place-rebuild')
        self.emit('source-rebuild')
        self.emit('media-rebuild')
        self.emit('event-rebuild')

    def _commit_base(self, obj, data_map, key, update_list, add_list,
                     transaction, change_time):
        """
        Commits the specified Person to the database, storing the changes
        as part of the transaction.
        """
        if self.readonly or not obj.handle:
            return 
        if change_time:
            obj.change = int(change_time)
        else:
            obj.change = int(time.time())
        handle = str(obj.handle)

        if transaction.batch:
            data_map[handle] = obj.serialize()
        else:
            old_data = data_map.get(handle)
            transaction.add(key,handle,old_data)
            if old_data:
                update_list.append((handle,obj.serialize()))
            else:
                add_list.append((handle,obj.serialize()))
    
    def commit_person(self,person,transaction,change_time=None):
        """
        Commits the specified Person to the database, storing the changes
        as part of the transaction.
        """
        self._commit_base(person, self.person_map, PERSON_KEY,
                          transaction.person_update, transaction.person_add,
                          transaction, change_time)
          
    def commit_media_object(self,obj,transaction,change_time=None):
        """
        Commits the specified MediaObject to the database, storing the changes
        as part of the transaction.
        """
        self._commit_base(obj, self.media_map, MEDIA_KEY,
                          transaction.media_update, transaction.media_add,
                          transaction, change_time)
            
    def commit_source(self,source,transaction,change_time=None):
        """
        Commits the specified Source to the database, storing the changes
        as part of the transaction.
        """
        self._commit_base(source, self.source_map, SOURCE_KEY,
                          transaction.source_update, transaction.source_add,
                          transaction, change_time)

    def commit_place(self,place,transaction,change_time=None):
        """
        Commits the specified Place to the database, storing the changes
        as part of the transaction.
        """
        self._commit_base(place, self.place_map, PLACE_KEY,
                          transaction.place_update, transaction.place_add,
                          transaction, change_time)

    def commit_event(self,event,transaction,change_time=None):
        """
        Commits the specified Event to the database, storing the changes
        as part of the transaction.
        """
        self._commit_base(event, self.event_map, EVENT_KEY,
                          transaction.event_update, transaction.event_add,
                          transaction, change_time)

    def commit_family(self,family,transaction,change_time=None):
        """
        Commits the specified Family to the database, storing the changes
        as part of the transaction.
        """
        self._commit_base(family, self.family_map, FAMILY_KEY,
                          transaction.family_update, transaction.family_add,
                          transaction, change_time)

    def find_next_person_gramps_id(self):
        """
        Returns the next available GRAMPS' ID for a Person object based
        off the person ID prefix.
        """
        index = self.iprefix % self.pmap_index
        while self.id_trans.get(str(index)):
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
        while self.pid_trans.get(str(index)):
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
        self.emap_index += 1
        return index

    def find_next_object_gramps_id(self):
        """
        Returns the next available GRAMPS' ID for a MediaObject object based
        off the person ID prefix.
        """
        index = self.oprefix % self.omap_index
        while self.oid_trans.get(str(index)):
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
        while self.sid_trans.get(str(index)):
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
        while self.fid_trans.get(str(index)):
            self.fmap_index += 1
            index = self.fprefix % self.fmap_index
        self.fmap_index += 1
        return index

    def _get_from_handle(self, handle, class_type, data_map):
        data = data_map.get(str(handle))
        if data:
            newobj = class_type()
            newobj.unserialize(data)
            return newobj
        return None

    def get_person_from_handle(self,handle):
        """
        Finds a Person in the database from the passed gramps' ID.
        If no such Person exists, None is returned.
        """
        return self._get_from_handle(handle,Person,self.person_map)

    def get_source_from_handle(self,handle):
        """
        Finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned.
        """
        return self._get_from_handle(handle,Source,self.source_map)

    def get_object_from_handle(self,handle):
        """
        Finds an Object in the database from the passed gramps' ID.
        If no such Object exists, None is returned.
        """
        return self._get_from_handle(handle,MediaObject,self.media_map)

    def get_place_from_handle(self,handle):
        """
        Finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned.
        """
        return self._get_from_handle(handle,Place,self.place_map)

    def get_event_from_handle(self,handle):
        """
        Finds a Event in the database from the passed gramps' ID.
        If no such Event exists, None is returned.
        """
        return self._get_from_handle(handle,Event,self.event_map)

    def get_family_from_handle(self,handle):
        """
        Finds a Family in the database from the passed gramps' ID.
        If no such Family exists, None is returned.
        """
        return self._get_from_handle(handle,Family,self.family_map)

    def _find_from_handle(self,handle,transaction,class_type,dmap,add_func):
        obj = class_type()
        handle = str(handle)
        if dmap.get(handle):
            obj.unserialize(dmap.get(handle))
        else:
            obj.set_handle(handle)
            add_func(obj,transaction)
        return obj

    def find_person_from_handle(self,handle,transaction):
        """
        Finds a Person in the database from the passed GRAMPS ID.
        If no such Person exists, a new Person is added to the database.
        """
        return self._find_from_handle(handle,transaction,Person,
                                      self.person_map,self.add_person)

    def find_source_from_handle(self,handle,transaction):
        """
        Finds a Source in the database from the passed GRAMPS ID.
        If no such Source exists, a new Source is added to the database.
        """
        return self._find_from_handle(handle,transaction,Source,
                                      self.source_map,self.add_source)

    def find_event_from_handle(self,handle,transaction):
        """
        Finds a Event in the database from the passed GRAMPS ID.
        If no such Event exists, a new Event is added to the database.
        """
        return self._find_from_handle(handle,transaction,Event,
                                      self.event_map,self.add_event)

    def find_object_from_handle(self,handle,transaction):
        """
        Finds an MediaObject in the database from the passed GRAMPS ID.
        If no such MediaObject exists, a new Object is added to the database."""

        return self._find_from_handle(handle,transaction,MediaObject,
                                      self.media_map,self.add_object)

    def find_place_from_handle(self,handle,transaction):
        """
        Finds a Place in the database from the passed GRAMPS ID.
        If no such Place exists, a new Place is added to the database.
        """
        return self._find_from_handle(handle,transaction,Place,
                                      self.place_map,self.add_place)

    def find_family_from_handle(self,handle,transaction):
        """
        Finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Family is added to the database.
        """
        return self._find_from_handle(handle,transaction,Family,
                                      self.family_map,self.add_family)

    def get_person_from_gramps_id(self,val):
        """
        Finds a Person in the database from the passed GRAMPS ID.
        If no such Person exists, None is returned.

        Needs to be overridden by the derrived class.
        """
        assert False, "Needs to be overridden in the derived class"

    def get_family_from_gramps_id(self,val):
        """
        Finds a Family in the database from the passed GRAMPS ID.
        If no such Family exists, None is returned.

        Needs to be overridden by the derrived class.
        """
        assert False, "Needs to be overridden in the derived class"

    def get_place_from_gramps_id(self,val):
        """finds a Place in the database from the passed gramps' ID.
        If no such Place exists, a new Person is added to the database.

        Needs to be overridden by the derrived class.
        """
        assert False, "Needs to be overridden in the derived class"

    def get_source_from_gramps_id(self,val):
        """finds a Source in the database from the passed gramps' ID.
        If no such Source exists, a new Person is added to the database.

        Needs to be overridden by the derrived class.
        """
        assert False, "Needs to be overridden in the derived class" 

    def get_object_from_gramps_id(self,val):
        """finds a MediaObject in the database from the passed gramps' ID.
        If no such MediaObject exists, a new Person is added to the database.

        Needs to be overridden by the derrived class.
        """
        assert False, "Needs to be overridden in the derived class"

    def add_person(self,person,transaction):
        """
        Adds a Person to the database, assigning internal IDs if they have
        not already been defined.
        """
        if not person.gramps_id:
            person.gramps_id = self.find_next_person_gramps_id()
        if not person.handle:
            person.handle = self.create_id()
        self.commit_person(person,transaction)
        self.genderStats.count_person (person, self)
        return person.handle

    def _add_object(self,object,transaction,find_next_func,commit_func):
        if not object.gramps_id:
            object.gramps_id = find_next_func()
        if not object.handle:
            object.handle = self.create_id()
        commit_func(object,transaction)
        return object.handle

    def add_family(self,family,transaction):
        """
        Adds a Family to the database, assigning internal IDs if they have
        not already been defined.
        """
        return self._add_object(family,transaction,
                                self.find_next_family_gramps_id,
                                self.commit_family)

    def add_source(self,source,transaction):
        """
        Adds a Source to the database, assigning internal IDs if they have
        not already been defined.
        """
        return self._add_object(source,transaction,
                                self.find_next_source_gramps_id,
                                self.commit_source)

    def add_event(self,event,transaction):
        """
        Adds an Event to the database, assigning internal IDs if they have
        not already been defined.
        """
        return self._add_object(event,transaction,
                                self.find_next_event_gramps_id,
                                self.commit_event)

    def add_place(self,place,transaction):
        """
        Adds a Place to the database, assigning internal IDs if they have
        not already been defined.
        """
        return self._add_object(place,transaction,
                                self.find_next_place_gramps_id,
                                self.commit_place)

    def add_object(self,obj,transaction):
        """
        Adds a MediaObject to the database, assigning internal IDs if they have
        not already been defined.
        """
        return self._add_object(obj,transaction,
                                self.find_next_object_gramps_id,
                                self.commit_media_object)

    def get_name_group_mapping(self,name):
        """
        Returns the default grouping name for a surname
        """
        return self.name_group.get(str(name),name)

    def get_name_group_keys(self):
        """
        Returns the defined names that have been assigned to a default grouping
        """
        return [unicode(k) for k in self.name_group.keys()]

    def set_name_group_mapping(self,name,group):
        """
        Sets the default grouping name for a surname. Needs to be overridden
        in the derived class.
        """
        assert False, "Needs to be overridden in the derived class"

    def get_number_of_people(self):
        """
        Returns the number of people currently in the databse.
        """
        return len(self.person_map)

    def get_person_handles(self,sort_handles=True):
        """
        Returns a list of database handles, one handle for each Person in
        the database. If sort_handles is True, the list is sorted by surnames
        """
        if self.person_map:
            if sort_handles:
                slist = []
                cursor = self.get_person_cursor()
                data = cursor.first()
                while data:
                    slist.append((data[1][3].sname,data[0]))
                    data = cursor.next()
                cursor.close()
                slist.sort()
                return map(lambda x: x[1], slist)
            else:
                return self.person_map.keys()
        return []

    def get_place_handles(self,sort_handles=True):
        """
        Returns a list of database handles, one handle for each Place in
        the database. If sort_handles is True, the list is sorted by
        Place title.
        """
        if self.place_map:
            if sort_handles:
                slist = []
                cursor = self.get_place_cursor()
                data = cursor.first()
                while data:
                    slist.append((data[1][2],data[0]))
                    data = cursor.next()
                cursor.close()
                slist.sort()
                val = map(lambda x: x[1], slist)
                return val
            else:
                return self.place_map.keys()
        return []

    def get_source_handles(self,sort_handles=True):
        """
        Returns a list of database handles, one handle for each Source in
        the database. If sort_handles is True, the list is sorted by
        Source title.
        """
        if self.source_map:
            handle_list = self.source_map.keys()
            if sort_handles:
                handle_list.sort(self._sortbysource)
            return handle_list
        return []

    def get_media_object_handles(self,sort_handles=True):
        """
        Returns a list of database handles, one handle for each MediaObject in
        the database. If sort_handles is True, the list is sorted by title.
        """
        if self.media_map:
            handle_list = self.media_map.keys()
            if sort_handles:
                handle_list.sort(self._sortbymedia)
            return handle_list
        return []

    def get_event_handles(self):
        """
        Returns a list of database handles, one handle for each Event in
        the database. 
        """
        if self.event_map:
            return self.event_map.keys()
        return []

    def get_family_handles(self):
        """
        Returns a list of database handles, one handle for each Family in
        the database.
        """
        if self.family_map:
            return self.family_map.keys()
        return []

    def set_person_id_prefix(self,val):
        """
        Sets the naming template for GRAMPS Person ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as I%d
        or I%04d.
        """
        if val:
            if _id_reg.search(val):
                self.iprefix = val
            else:
                self.iprefix = val + "%d"
        else:
            self.iprefix = "I%04d"
            
    def set_source_id_prefix(self,val):
        """
        Sets the naming template for GRAMPS Source ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as S%d
        or S%04d.
        """
        if val:
            if _id_reg.search(val):
                self.sprefix = val
            else:
                self.sprefix = val + "%d"
        else:
            self.sprefix = "S%04d"
            
    def set_object_id_prefix(self,val):
        """
        Sets the naming template for GRAMPS MediaObject ID values. The string
        is expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as O%d
        or O%04d.
        """
        if val:
            if _id_reg.search(val):
                self.oprefix = val
            else:
                self.oprefix = val + "%d"
        else:
            self.oprefix = "O%04d"

    def set_place_id_prefix(self,val):
        """
        Sets the naming template for GRAMPS Place ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as P%d
        or P%04d.
        """
        if val:
            if _id_reg.search(val):
                self.pprefix = val
            else:
                self.pprefix = val + "%d"
        else:
            self.pprefix = "P%04d"

    def set_family_id_prefix(self,val):
        """
        Sets the naming template for GRAMPS Family ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as F%d
        or F%04d.
        """
        if val:
            if _id_reg.search(val):
                self.fprefix = val
            else:
                self.fprefix = val + "%d"
        else:
            self.fprefix = "F%04d"

    def set_event_id_prefix(self,val):
        """
        Sets the naming template for GRAMPS Event ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as E%d
        or E%04d.
        """
        if val:
            if _id_reg.search(val):
                self.eprefix = val
            else:
                self.eprefix = val + "%d"
        else:
            self.eprefix = "E%04d"
            
    def transaction_begin(self,msg=""):
        """
        Creates a new Transaction tied to the current UNDO database. The
        transaction has no effect until it is committed using the
        transaction_commit function of the this database object.
        """
        return Transaction(msg,self.undodb)

    def transaction_commit(self,transaction,msg):
        """
        Commits the transaction to the assocated UNDO database.
        """
        if not len(transaction) or self.readonly:
            return
        transaction.set_description(msg)
        self.undoindex += 1
        if self.undoindex == _UNDO_SIZE:
            self.translist = transaction[0:-1] + [ transaction ]
        else:
            self.translist[self.undoindex] = transaction

        person_add = self._do_commit(transaction.person_add,self.person_map)
        family_add = self._do_commit(transaction.family_add,self.family_map)
        source_add = self._do_commit(transaction.source_add,self.source_map)
        place_add  = self._do_commit(transaction.place_add,self.place_map)
        media_add  = self._do_commit(transaction.media_add,self.media_map)
        event_add  = self._do_commit(transaction.event_add,self.event_map)

        person_upd = self._do_commit(transaction.person_update,self.person_map)
        family_upd = self._do_commit(transaction.family_update,self.family_map)
        source_upd = self._do_commit(transaction.source_update,self.source_map)
        place_upd  = self._do_commit(transaction.place_update,self.place_map)
        media_upd  = self._do_commit(transaction.media_update,self.media_map)
        event_upd  = self._do_commit(transaction.event_update,self.event_map)

        self._do_emit('person', person_add, person_upd, transaction.person_del)
        self._do_emit('family', family_add, family_upd, transaction.family_del)
        self._do_emit('event',  event_add,  event_upd,  transaction.event_del)
        self._do_emit('source', source_add, source_upd, transaction.source_del)
        self._do_emit('place',  place_add,  place_upd,  transaction.place_del)
        self._do_emit('media',  media_add,  media_upd,  transaction.media_del)

        self._do_del(transaction.person_del, self._del_person)
        self._do_del(transaction.family_del, self._del_family)
        self._do_del(transaction.place_del,  self._del_place)
        self._do_del(transaction.source_del, self._del_source)
        self._do_del(transaction.event_del,  self._del_event)
        self._do_del(transaction.media_del,  self._del_media)

        if self.undo_callback:
            self.undo_callback(_("_Undo %s") % transaction.get_description())

    def _do_emit(self, objtype, add_list, upd_list, del_list):
        if add_list:
            self.emit(objtype + '-add',(add_list,))
        if upd_list:
            self.emit(objtype + '-update',(upd_list,))
        if del_list:
            self.emit(objtype + '-delete',(del_list,))

    def _do_del(self,del_list,func):
        for handle in del_list:
            func(handle)
        return del_list

    def _do_commit(self,add_list,db_map):
        retlist = []
        for (handle,data) in add_list:
            db_map[handle] = data
            retlist.append(str(handle))
        return retlist

    def undo(self):
        """
        Accesses the last committed transaction, and reverts the data to
        the state before the transaction was committed.
        """
        if self.undoindex == -1 or self.readonly:
            return False
        transaction = self.translist[self.undoindex]

        mapbase = (self.person_map, self.family_map, self.source_map,
                   self.event_map, self.media_map, self.place_map)

        self.undoindex -= 1
        subitems = transaction.get_recnos()
        subitems.reverse()
        for record_id in subitems:
            (key, handle, data) = transaction.get_record(record_id)
            self.undo_data(data,handle,mapbase[key],_sigbase[key])

        if self.undo_callback:
            if self.undoindex == -1:
                self.undo_callback(None)
            else:
                transaction = self.translist[self.undoindex]
                self.undo_callback(_("_Undo %s") % transaction.get_description())
        return True

    def undo_data(self,data,handle,db_map,signal_root):
        if data == None:
            self.emit(signal_root + '-delete',([handle],))
            del db_map[handle]
        else:
            if db_map.has_key(handle):
                signal = signal_root + '-update'
            else:
                signal = signal_root + '-add'
            db_map[handle] = data
            self.emit(signal,([handle],))
    
    def set_undo_callback(self,callback):
        """
        Defines the callback function that is called whenever an undo operation
        is executed. The callback function recieves a single argument that is a
        text string that defines the operation.
        """
        self.undo_callback = callback

    def set_redo_callback(self,callback):
        """
        Defines the callback function that is called whenever an redo operation
        is executed. The callback function recieves a single argument that is a
        text string that defines the operation.
        """
        self.redo_callback = callback

    def get_surname_list(self):
        """
        Returns the list of surnames contained within the database.
        The function must be overridden in the derived class.
        """
        assert False, "Needs to be overridden in the derived class"

    def get_person_event_type_list(self):
        """
        Returns the list of personal event types contained within the
        database. The function must be overridden in the derived class.
        """
        assert False, "Needs to be overridden in the derived class"

    def get_bookmarks(self):
        """returns the list of Person handles in the bookmarks"""
        return self.bookmarks

    def set_researcher(self,owner):
        """sets the information about the owner of the database"""
        self.owner.set(owner.get_name(), owner.get_address(),
                       owner.get_city(), owner.get_state(),
                       owner.get_country(), owner.get_postal_code(),
                       owner.get_phone(), owner.get_email())

    def get_researcher(self):
        """returns the Researcher instance, providing information about
        the owner of the database"""
        return self.owner

    def set_default_person_handle(self,handle):
        """sets the default Person to the passed instance"""
        if not self.readonly:
            self.metadata['default'] = str(handle)

    def get_default_person(self):
        """returns the default Person of the database"""
        if self.metadata:
            key = self.metadata.get('default')
            data = self.person_map.get(key)
            if data:
                person = Person()
                person.unserialize(data)
                return person
            elif not self.readonly:
                self.metadata['default'] = None
                return None
        return None

    def get_save_path(self):
        """returns the save path of the file, or "" if one does not exist"""
        return self.path

    def set_save_path(self,path):
        """sets the save path for the database"""
        self.path = path

    def get_person_event_types(self):
        """returns a list of all Event types assocated with Person
        instances in the database"""
        return []

    def get_person_attribute_types(self):
        """returns a list of all Attribute types assocated with Person
        instances in the database"""
        return []

    def get_family_attribute_types(self):
        """returns a list of all Attribute types assocated with Family
        instances in the database"""
        return []

    def get_family_event_types(self):
        """returns a list of all Event types assocated with Family
        instances in the database"""
        return []

    def get_media_attribute_types(self):
        """returns a list of all Attribute types assocated with Media
        instances in the database"""
        return []

    def get_family_relation_types(self):
        """returns a list of all relationship types assocated with Family
        instances in the database"""
        return []

    def remove_person(self,handle,transaction):
        """
        Removes the Person specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        if not self.readonly:
            person = self.get_person_from_handle(handle)
            self.genderStats.uncount_person (person)
            if not transaction.batch:
                transaction.add(PERSON_KEY,handle,person.serialize())
            transaction.person_del.append(str(handle))

    def _do_remove_object(self,handle,trans,dmap,key,del_list):
        if not self.readonly:
            handle = str(handle)
            if not trans.batch:
                old_data = dmap.get(handle)
                transaction.add(key,handle,old_data)
            del_list.append(handle)

    def remove_source(self,handle,transaction):
        """
        Removes the Source specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        self._do_remove_object(handle,transaction,self.source_map,
                               SOURCE_KEY, transaction.source_del)

    def remove_event(self,handle,transaction):
        """
        Removes the Event specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        self._do_remove_object(handle,transaction,self.event_map,
                               EVENT_KEY, transaction.event_del)

    def remove_object(self,handle,transaction):
        """
        Removes the MediaObjectPerson specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        self._do_remove_object(handle,transaction,self.media_map,
                               MEDIA_KEY, transaction.media_del)

    def remove_place(self,handle,transaction):
        """
        Removes the Place specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        self._do_remove_object(handle,transaction,self.place_map,
                               PLACE_KEY, transaction.place_del)

    def remove_family(self,handle,transaction):
        """
        Removes the Family specified by the database handle from the
        database, preserving the change in the passed transaction. This
        method must be overridden in the derived class.
        """
        self._do_remove_object(handle,transaction,self.family_map,
                               FAMILY_KEY, transaction.family_del)

    def has_person_handle(self,handle):
        """
        returns True if the handle exists in the current Person database.
        """
        return self.person_map.has_key(str(handle))

    def has_family_handle(self,handle):            
        """
        returns True if the handle exists in the current Family database.
        """
        return self.family_map.has_key(str(handle))

    def has_object_handle(self,handle):
        """
        returns True if the handle exists in the current MediaObjectdatabase.
        """
        return self.media_map.has_key(str(handle)) != None

    def _sortbyname(self,f,s):
        n1 = self.person_map.get(str(f))[3].sname
        n2 = self.person_map.get(str(s))[3].sname
        return locale.strcoll(n1,n2)

    def _sortbyplace(self,f,s):
        return locale.strcoll(self.place_map.get(str(f))[2],
                              self.place_map.get(str(s))[2])

    def _sortbysource(self,f,s):
        fp = unicode(self.source_map[str(f)][2])
        sp = unicode(self.source_map[str(s)][2])
        return locale.strcoll(fp,sp)

    def _sortbymedia(self,f,s):
        fp = self.media_map[str(f)][4]
        sp = self.media_map[str(s)][4]
        return locale.strcoll(fp,sp)

    def _set_column_order(self,col_list,name):
        if self.metadata and not self.readonly: 
            self.metadata[name] = col_list

    def set_person_column_order(self,col_list):
        """
        Stores the Person display common information in the
        database's metadata.
        """
        self._set_column_order(col_list,PERSON_COL_KEY)

    def set_child_column_order(self,col_list):
        """
        Stores the Person display common information in the
        database's metadata.
        """
        self._set_column_order(col_list,CHILD_COL_KEY)

    def set_place_column_order(self,col_list):
        """
        Stores the Place display common information in the
        database's metadata.
        """
        self._set_column_order(col_list,PLACE_COL_KEY)

    def set_source_column_order(self,col_list):
        """
        Stores the Source display common information in the
        database's metadata.
        """
        self._set_column_order(col_list,SOURCE_COL_KEY)

    def set_media_column_order(self,list):
        """
        Stores the Media display common information in the
        database's metadata.
        """
        self._set_column_order(col_list,MEDIA_COL_KEY)

    def _get_column_order(self,name,default):
        if self.metadata == None:
            return default
        else:
            cols = self.metadata.get(name,default)
            if len(cols) != len(default):
                return cols + default[len(cols):]
            else:
                return cols

    def get_person_column_order(self):
        """
        Returns the Person display common information stored in the
        database's metadata.
        """
        default = [(1,1),(1,2),(1,3),(0,4),(1,5),(0,6),(0,7),(0,8),(0,9,)]
        return self._get_column_order(PERSON_COL_KEY,default)

    def get_child_column_order(self):
        """
        Returns the Person display common information stored in the
        database's metadata.
        """
        default = [(1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(0,6),(0,7)]
        return self._get_column_order(CHILD_COL_KEY,default)

    def get_place_column_order(self):
        """
        Returns the Place display common information stored in the
        database's metadata.
        """
        default = [(1,1),(1,2),(0,3),(0,4),(1,5),(0,6),(1,7),(0,8),(0,9),(0,10)]
        return self._get_column_order(PLACE_COL_KEY,default)

    def get_source_column_order(self):
        """
        Returns the Source display common information stored in the
        database's metadata.
        """
        default = [(1,1),(1,2),(0,3),(1,4),(0,5)]
        return self._get_column_order(SOURCE_COL_KEY,default)

    def get_media_column_order(self):
        """
        Returns the MediaObject display common information stored in the
        database's metadata.
        """
        default = [(1,1),(0,5),(0,6),(1,2),(1,3),(0,4)]
        return self._get_column_order(MEDIA_COL_KEY,default)

class Transaction:
    """
    Defines a group of database commits that define a single logical
    operation.
    """
    def __init__(self,msg,db):
        """
        Creates a new transaction. A Transaction instance should not be created
        directly, but by the GrampsDbBase class or classes derived from
        GrampsDbBase. The db parameter is a list-like interface that stores
        the commit data. This could be a simple list, or a RECNO-style database
        object.
        """
        self.db = db
        self.first = None
        self.last = None
        self.batch = False
        self.length = 0

        self.person_add = []
        self.person_del = []
        self.person_update = []

        self.family_add = []
        self.family_del = []
        self.family_update = []

        self.source_add = []
        self.source_del = []
        self.source_update = []

        self.event_add = []
        self.event_del = []
        self.event_update = []

        self.media_add = []
        self.media_del = []
        self.media_update = []

        self.place_add = []
        self.place_del = []
        self.place_update = []

    def set_batch(self,batch):
        self.batch = batch

    def get_batch(self):
        return self.batch
    
    def get_description(self):
        """
        Returns the text string that describes the logical operation
        performed by the Transaction.
        """
        return self.msg

    def set_description(self,msg):
        """
        Sets the text string that describes the logical operation
        performed by the Transaction.
        """
        self.msg = msg

    def add(self, type, handle, data):
        """
        Adds a commit operation to the Transaction. The type is a constant
        that indicates what type of PrimaryObject is being added. The handle
        is the object's database handle, and the data is the tuple returned
        by the object's serialize method.
        """
        self.last = self.db.append(cPickle.dumps((type,handle,data),1))
        if self.first == None:
            self.first = self.last

    def get_recnos(self):
        """
        Returns a list of record numbers associated with the transaction.
        While the list is an arbitrary index of integers, it can be used
        to indicate record numbers for a database.
        """
        return range (self.first, self.last+1)

    def get_record(self,recno):
        """
        Returns a tuple representing the PrimaryObject type, database handle
        for the PrimaryObject, and a tuple representing the data created by
        the object's serialize method.
        """
        return cPickle.loads(self.db[recno])

    def __len__(self):
        """
        Returns the number of commits associated with the Transaction.
        """
        if self.last and self.first:
            return self.last - self.first + 1
        return 0

