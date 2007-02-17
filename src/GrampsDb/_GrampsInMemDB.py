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
Provides the common infrastructure for database formats that
must hold all of their data in memory.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import time

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from RelLib import *
from _GrampsDbBase import *

class GrampsInMemCursor(GrampsCursor):
    """
    Cursor class for in-memory database classes. Since the in-memory
    classes use python dictionaries, the python iter class is used
    to provide the cursor function.
    """
    def __init__(self,src_map):
        self.src_map = src_map
        self.current = iter(src_map)
        
    def first(self):
        self.current = iter(self.src_map)
        return self.next()

    def next(self):
        try:
            index = self.current.next()
            return (index,self.src_map[index])
        except StopIteration:
            return None

    def close(self):
        pass
    
    def get_length(self):
        return len(self.src_map)
        
#-------------------------------------------------------------------------
#
# GrampsInMemDB
#
#-------------------------------------------------------------------------
class GrampsInMemDB(GrampsDbBase):
    """GRAMPS database object. This object is a base class for other
    objects."""

    ID_INDEX = 1 # an index of the gramps id in the data tuple

    def __init__(self):
        """creates a new GrampsDB"""
        GrampsDbBase.__init__(self)
        self.person_map       = {}
        self.name_group       = {}
        self.family_map       = {}
        self.place_map        = {}
        self.source_map       = {}
        self.repository_map   = {}
        self.media_map        = {}
        self.event_map        = {}
        self.metadata         = {}
        self.filename         = ""
        self.id_trans         = {}
        self.pid_trans        = {}
        self.fid_trans        = {}
        self.eid_trans        = {}
        self.sid_trans        = {}
        self.rid_trans        = {}
        self.oid_trans        = {}
        self.undodb           = []

    def load(self,name,callback,mode="w"):
        self.full_name = name
        self.readonly = mode == "r"
        self.open_undodb()

        # Re-set the undo history to a fresh session start
        self.undoindex = -1
        self.translist = [None] * len(self.translist)
        self.abort_possible = True
        self.undo_history_timestamp = time.time()

    def transaction_commit(self,transaction,msg):
        GrampsDbBase.transaction_commit(self,transaction,msg)
        if transaction.batch:
            self.build_surname_list()

    def get_person_cursor(self):
        return GrampsInMemCursor(self.person_map)

    def get_family_cursor(self):
        return GrampsInMemCursor(self.family_map)

    def get_event_cursor(self):
        return GrampsInMemCursor(self.event_map)

    def get_place_cursor(self):
        return GrampsInMemCursor(self.place_map)

    def get_source_cursor(self):
        return GrampsInMemCursor(self.source_map)

    def get_repository_cursor(self):
        return GrampsInMemCursor(self.repository_map)

    def get_media_cursor(self):
        return GrampsInMemCursor(self.media_map)

    def close(self):
        self.close_undodb()

    def set_name_group_mapping(self,name,group):
        if group == None and self.name_group.has_key(name):
            del self.name_group[name]
        else:
            self.name_group[name] = group

    def build_surname_list(self):
        a = set()
        for person_id in iter(self.person_map):
            p = self.get_person_from_handle(person_id)
            a.add(unicode(p.get_primary_name().get_surname()))
        self.surname_list = list(a)
        self.sort_surname_list()

    def remove_from_surname_list(self,person):
        """
        Check whether there are persons with the same surname left in
        the database. If not then we need to remove the name from the list.
        The function must be overridden in the derived class.
        """
        name = str(person.get_primary_name().get_surname())
        count = 0
        do_remove = True
        
        for person_id in iter(self.person_map):
            p = self.get_person_from_handle(person_id)
            pn = str(p.get_primary_name().get_surname())
            if pn == name:
                count += 1
            if count > 1:
                do_remove = False
                break

        if do_remove:
            self.surname_list.remove(unicode(name))

    def _del_person(self,handle):
        person = self.get_person_from_handle(str(handle))
        del self.id_trans[person.get_gramps_id()]
        del self.person_map[str(handle)]

    def _del_source(self,handle):
        source = self.get_source_from_handle(str(handle))
        del self.sid_trans[source.get_gramps_id()]
        del self.source_map[str(handle)]

    def _del_repository(self,handle):
        repository = self.get_repository_from_handle(str(handle))
        del self.rid_trans[repository.get_gramps_id()]
        del self.repository_map[str(handle)]

    def _del_place(self,handle):
        place = self.get_place_from_handle(str(handle))
        del self.pid_trans[place.get_gramps_id()]
        del self.place_map[str(handle)]

    def _del_media(self,handle):
        obj = self.get_object_from_handle(str(handle))
        del self.oid_trans[obj.get_gramps_id()]
        del self.media_map[str(handle)]

    def _del_family(self,handle):
        family = self.get_family_from_handle(str(handle))
        del self.fid_trans[family.get_gramps_id()]
        del self.family_map[str(handle)]

    def _del_event(self,handle):
        event = self.get_event_from_handle(str(handle))
        del self.eid_trans[event.get_gramps_id()]
        del self.event_map[str(handle)]

    def get_trans_map(self,signal_root):
        """
        A silly method to get the secondary index map based on the
        signal name root for a given object type. The BDB backend
        manages this transparently, but we need to manually take
        care of secondary indices in the InMem backend.
        """
        trans_maps = {
            'person': self.id_trans,
            'family': self.fid_trans,
            'source': self.sid_trans,
            'event' : self.eid_trans,
            'media' : self.oid_trans,
            'place' : self.pid_trans,
            'repository': self.rid_trans}
        return trans_maps[signal_root]

    def undo_data(self, data, handle, db_map, signal_root):
        """
        The BDB backend manages secondary indices transparently,
        but we need to manually take care of secondary indices
        in the InMem backend.
        """
        trans_map = self.get_trans_map(signal_root)
        obj = db_map.get(handle)
        if data == None:
            self.emit(signal_root + '-delete', ([handle], ))
            del trans_map[obj[self.ID_INDEX]]
            del db_map[handle]
        else:
            if obj:
                signal = signal_root + '-update'
                if obj[self.ID_INDEX] != data[self.ID_INDEX]:
                    del trans_map[obj[self.ID_INDEX]]
            else:
                signal = signal_root + '-add'
            db_map[handle] = data
            trans_map[data[self.ID_INDEX]] = str(handle)
            self.emit(signal, ([handle], ))
    
    def _commit_inmem_base(self,obj,db_map,trans_map):
        if self.readonly or not obj or not obj.get_handle():
            return False
        gid = obj.gramps_id
        old_data = db_map.get(obj.handle)
        if old_data:
            old_id = old_data[self.ID_INDEX]
            if obj.gramps_id != old_id:
                del trans_map[old_id]
        trans_map[gid] = obj.handle
        return True

    def commit_person(self,person,transaction,change_time=None):
        if not self._commit_inmem_base(person,self.person_map,self.id_trans):
            return
        GrampsDbBase.commit_person(self,person,transaction,change_time)

    def commit_place(self,place,transaction,change_time=None):
        if not self._commit_inmem_base(place,self.place_map,self.pid_trans):
            return
        GrampsDbBase.commit_place(self,place,transaction,change_time)

    def commit_family(self,family,transaction,change_time=None):
        if not self._commit_inmem_base(family,self.family_map,self.fid_trans):
            return
        GrampsDbBase.commit_family(self,family,transaction,change_time)

    def commit_event(self,event,transaction,change_time=None):
        if not self._commit_inmem_base(event,self.event_map,self.eid_trans):
            return
        GrampsDbBase.commit_event(self,event,transaction,change_time)

    def commit_media_object(self,obj,transaction,change_time=None):
        if not self._commit_inmem_base(obj,self.media_map,self.oid_trans):
            return
        GrampsDbBase.commit_media_object(self,obj,transaction,change_time)

    def commit_source(self,source,transaction,change_time=None):
        if not self._commit_inmem_base(source,self.source_map,self.sid_trans):
            return
        GrampsDbBase.commit_source(self,source,transaction,change_time)

    def commit_repository(self,repository,transaction,change_time=None):
        if not self._commit_inmem_base(repository,self.repository_map,
                                       self.rid_trans):
            return
        GrampsDbBase.commit_repository(self,repository,transaction,change_time)

    def get_person_from_gramps_id(self,val):
        handle = self.id_trans.get(str(val))
        if handle:
            data = self.person_map[handle]
            if data:
                person = Person()
                person.unserialize(data)
                return person
        return None

    def get_family_from_gramps_id(self,val):
        handle = self.fid_trans.get(str(val))
        if handle:
            data = self.family_map[handle]
            if data:
                family = Family()
                family.unserialize(data)
                return family
        return None

    def get_event_from_gramps_id(self,val):
        handle = self.eid_trans.get(str(val))
        if handle:
            data = self.event_map[handle]
            if data:
                event = Event()
                event.unserialize(data)
                return event
        return None

    def get_place_from_gramps_id(self,val):
        handle = self.pid_trans.get(str(val))
        if handle:
            data = self.place_map[handle]
            if data:
                place = Place()
                place.unserialize(data)
                return place
        return None

    def get_source_from_gramps_id(self,val):
        handle = self.sid_trans.get(str(val))
        if handle:
            data = self.source_map[handle]
            if data:
                source = Source()
                source.unserialize(data)
                return source
        return None

    def get_repository_from_gramps_id(self,val):
        handle = self.rid_trans.get(str(val))
        if handle:
            data = self.repository_map[handle]
            if data:
                repository = Repository()
                repository.unserialize(data)
                return repository
        return None

    def get_object_from_gramps_id(self,val):
        handle = self.oid_trans.get(str(val))
        if handle:
            data = self.media_map[handle]
            if data:
                obj = MediaObject()
                obj.unserialize(data)
                return obj
        return None
