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

#-------------------------------------------------------------------------
#
# libraries
#
#-------------------------------------------------------------------------
from RelLib import *
import cPickle
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
_UNDO_SIZE = 1000
_id_reg    = compile("%\d+d")

#-------------------------------------------------------------------------
#
# GrampsDbBase
#
#-------------------------------------------------------------------------
class GrampsDbBase:
    """GRAMPS database object. This object is a base class for other
    objects."""

    def __init__(self):
        """creates a new GrampsDB"""

        self.set_iprefix(GrampsCfg.get_iprefix())
        self.set_oprefix(GrampsCfg.get_oprefix())
        self.set_fprefix(GrampsCfg.get_fprefix())
        self.set_sprefix(GrampsCfg.get_sprefix())
        self.set_pprefix(GrampsCfg.get_pprefix())
        self.set_eprefix(GrampsCfg.get_eprefix())
        self.open = 0
        self.new()
        self.added_files = []
        self.genderStats = GenderStats()

        self.id_trans = None
        self.env = None
        self.person_map = None
        self.family_map = None
        self.place_map  = None
        self.source_map = None
        self.media_map  = None
        self.event_map  = None
        self.eventnames = None
        self.metadata   = None
        self.undolabel  = None
        self.redolabel  = None
        self.modified   = 0

    def new(self):
        """initializes the GrampsDB to empty values"""

        self.undoindex  = -1
        self.translist  = [None] * _UNDO_SIZE
        self.smap_index = 0
        self.emap_index = 0
        self.pmap_index = 0
        self.fmap_index = 0
        self.lmap_index = 0
        self.omap_index = 0
        self.default = None
        self.owner = Researcher()
        self.bookmarks = []
        self.path = ""
        self.place2title = {}
        self.genderStats = GenderStats()

    def load(self,name,callback):
        assert(0,"Needs to be overridden in the derived class")

    def close(self):
        assert(0,"Needs to be overridden in the derived class")
        
    def is_open(self):
        return self.person_map != None

    def commit_person(self,person,transaction):
        handle = person.get_handle()
        if transaction != None:
            old_data = self.person_map.get(handle)
            transaction.add(PERSON_KEY,handle,old_data)
        self.person_map[handle] = person.serialize()
          
    def commit_media_object(self,obj,transaction):
        handle = str(obj.get_handle())
        if transaction != None:
            old_data = self.media_map.get(handle)
            transaction.add(MEDIA_KEY,handle,old_data)
        self.media_map[str(obj.get_handle())] = obj.serialize()

    def commit_source(self,source,transaction):
        handle = str(source.get_handle())
        if transaction != None:
            old_data = self.source_map.get(handle)
            transaction.add(SOURCE_KEY,handle,old_data)
        self.source_map[str(source.get_handle())] =  source.serialize()

    def commit_place(self,place,transaction):
        handle = str(place.get_handle())
        if transaction != None:
            old_data = self.place_map.get(handle)
            transaction.add(PLACE_KEY,handle,old_data)
        self.place_map[str(place.get_handle())] = place.serialize()

    def commit_event(self,event,transaction):
        handle = str(event.get_handle())
        if transaction != None:
            old_data = self.event_map.get(handle)
            transaction.add(EVENT_KEY,handle,old_data)
        self.event_map[str(event.get_handle())] = event.serialize()

    def commit_family(self,family,transaction):
        handle = str(family.get_handle())
        if transaction != None:
            old_data = self.family_map.get(handle)
            transaction.add(FAMILY_KEY,handle,old_data)
        self.family_map[str(family.get_handle())] = family.serialize()

    def find_next_gramps_id(self):
        index = self.iprefix % self.pmap_index
        while self.id_trans.get(str(index)):
            self.pmap_index += 1
            index = self.iprefix % self.pmap_index
        self.pmap_index += 1
        return index

    def find_next_place_gramps_id(self):
        index = self.pprefix % self.lmap_index
        while self.id_trans.get(str(index)):
            self.lmap_index += 1
            index = self.pprefix % self.lmap_index
        self.lmap_index += 1
        return index

    def find_next_event_gramps_id(self):
        index = self.eprefix % self.emap_index
        while self.id_trans.get(str(index)):
            self.emap_index += 1
            index = self.eprefix % self.emap_index
        self.emap_index += 1
        return index

    def find_next_object_gramps_id(self):
        index = self.oprefix % self.omap_index
        while self.id_trans.get(str(index)):
            self.omap_index += 1
            index = self.oprefix % self.omap_index
        self.omap_index += 1
        return index

    def find_next_source_gramps_id(self):
        index = self.sprefix % self.smap_index
        while self.source_map.get(str(index)):
            self.smap_index += 1
            index = self.sprefix % self.smap_index
        self.fmap_index += 1
        return index

    def find_next_family_gramps_id(self):
        index = self.fprefix % self.fmap_index
        while self.family_map.get(str(index)):
            self.fmap_index += 1
            index = self.fprefix % self.fmap_index
        self.fmap_index += 1
        return index

    def get_person_from_handle(self,val):
        """finds a Person in the database from the passed gramps' ID.
        If no such Person exists, a new Person is added to the database."""

        data = self.person_map.get(val)
        if data:
            person = Person()
            person.unserialize(data)
            return person
        return None

    def get_source_from_handle(self,val):
        """finds a Source in the database from the passed gramps' ID.
        If no such Source exists, None is returned."""

        data = self.source_map.get(val)
        if data:
            source = Source()
            source.unserialize(data)
            return source
        return None

    def get_object_from_handle(self,handle):
        """finds an Object in the database from the passed gramps' ID.
        If no such Object exists, None is returned."""
        data = self.media_map.get(handle)
        if data:
            mobject = MediaObject()
            mobject.unserialize(data)
            return mobject
        return None

    def get_place_from_handle(self,handle):
        """finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned."""
        data = self.place_map.get(handle)
        if data:
            place = Place()
            place.unserialize(data)
            return place
        return None

    def get_event_from_handle(self,handle):
        """finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned."""

        data = self.event_map.get(handle)
        if data:
            event = Event()
            event.unserialize(data)
            return event
        return None

    def get_family_from_handle(self,handle):
        """finds a Place in the database from the passed gramps' ID.
        If no such Place exists, None is returned."""

        data = self.family_map.get(str(handle))
        if data:
            family = Family()
            family.unserialize(data)
            return family
        return None

    def find_person_from_handle(self,val,trans):
        """finds a Person in the database from the passed gramps' ID.
        If no such Person exists, a new Person is added to the database."""

        person = Person()
        data = self.person_map.get(val)
        if data:
            person.unserialize(data)
        else:
            person.set_handle(val)
            if trans != None:
                trans.add(PERSON_KEY, val, None)
            self.person_map[val] = person.serialize()
            self.genderStats.count_person (person, self)
        return person

    def find_source_from_handle(self,val,trans):
        """finds a Source in the database from the passed gramps' ID.
        If no such Source exists, a new Source is added to the database."""

        source = Source()
        if self.source_map.get(str(val)):
            source.unserialize(self.source_map.get(str(val)))
        else:
            source.set_handle(val)
            if trans != None:
                trans.add(SOURCE_KEY,val,None)
            self.source_map[str(val)] = source.serialize()
            self.smap_index = self.smap_index + 1
        return source

    def find_event_from_handle(self,val):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Family is added to the database."""
        data = self.event_map.get(str(val))
        if data:
            event = Event()
            event.unserialize(data)
            return event
        else:
            return None

    def find_object_from_handle(self,handle,trans):
        """finds an Object in the database from the passed gramps' ID.
        If no such Object exists, a new Object is added to the database."""

        obj = MediaObject()
        if self.media_map.get(str(handle)):
            obj.unserialize(self.media_map.get(str(handle)))
        else:
            obj.set_handle(handle)
            self.add_object(obj,trans)
        return obj

    def find_place_from_handle(self,handle,trans):
        """finds a Place in the database from the passed gramps' ID.
        If no such Place exists, a new Place is added to the database."""

        data = self.place_map.get(str(handle))
        place = Place()
        if not data:
            place.handle = handle
            if trans != None:
                trans.add(PLACE_KEY,handle,None)
            self.place_map[str(handle)] = place.serialize()
            self.lmap_index = self.lmap_index + 1
        else:
            place.unserialize(data)
        return place

    def find_family_from_handle(self,val,trans):
        """finds a Family in the database from the passed gramps' ID.
        If no such Family exists, a new Family is added to the database."""

        family = Family()
        data = self.family_map.get(str(val))
        if data:
            family.unserialize(data)
        else:
            family.handle = val
            if trans:
                trans.add(FAMILY_KEY,val,None)
            self.family_map[str(val)] = family.serialize()
            self.fmap_index = self.fmap_index + 1
        return family

    def add_person(self,person,trans):
        """adds a Person to the database, assigning a gramps' ID"""
        if person.get_gramps_id() == "":
            person.set_gramps_id(self.find_next_gramps_id())
        if person.get_handle() == "":
            person.set_handle(Utils.create_id())
        if trans != None:
            trans.add(PERSON_KEY, person.get_handle(),None)
        self.person_map[person.get_handle()] = person.serialize()
        self.genderStats.count_person (person, self)
        return person.get_handle()

    def add_family(self,family,trans):
        """adds a Person to the database, assigning a gramps' ID"""
        if family.get_gramps_id() == "":
            family.set_gramps_id(self.find_next_family_gramps_id())
        if family.get_handle() == "":
            family.set_handle(Utils.create_id())
        if trans != None:
            trans.add(FAMILY_KEY, family.get_handle(),None)
        self.family_map[str(family.get_handle())] = family.serialize()
        return family.get_handle()

    def add_source(self,source,trans):
        """adds a Source instance to the database, assigning it a gramps'
        ID number"""
        if source.get_handle() == "":
            source.set_handle(Utils.create_id())
        if source.get_gramps_id() == "":
            source.set_gramps_id(self.find_next_source_gramps_id())
        if trans != None:
            trans.add(SOURCE_KEY,source.get_handle(),None)
        self.source_map[str(source.get_handle())] = source.serialize()
        return source.get_handle()

    def add_event(self,event,trans):
        """adds a Event instance to the database, assigning it a gramps'
        ID number"""
        if event.get_handle() == "":
            event.set_handle(Utils.create_id())
        if event.get_gramps_id() == "":
            event.set_gramps_id(self.find_next_event_gramps_id())
        if trans != None:
            trans.add(EVENT_KEY,event.get_handle(),None)
        self.event_map[str(event.get_handle())] = event.serialize()
        return event.get_handle()

    def add_place(self,place,trans):
        """adds a Place instance to the database, assigning it a gramps'
        ID number"""

        if place.get_handle() == "":
            index = Utils.create_id()
            place.set_handle(index)
        if place.get_gramps_id() == "":
            place.set_gramps_id(self.find_next_place_gramps_id())
        if trans != None:
            trans.add(PLACE_KEY,place.get_handle(),None)
        self.place_map[place.get_handle()] = place.serialize()
        return place.get_handle()

    def add_object(self,obj,trans):
        """adds an Object instance to the database, assigning it a gramps'
        ID number"""

        index = obj.get_handle()
        if index == "":
            index = Utils.create_id()
            obj.set_handle(index)
        if obj.get_gramps_id() == "":
            obj.set_gramps_id(self.find_next_object_gramps_id())
        if trans != None:
            trans.add(MEDIA_KEY,index,None)
        self.media_map[str(index)] = obj.serialize()
        self.added_files.append(obj)
        return index

    def get_people_view_maps(self):
        if self.metadata:
            return (self.metadata.get('tp_iter'),
                    self.metadata.get('tp_path'),
                    self.metadata.get('p_iter'),
                    self.metadata.get('p_path'),
                    self.metadata.get('sname'))
        else:
            return (None,None,None,None,None)

    def set_people_view_maps(self,maps):
        if self.metadata:
            self.metadata['tp_iter'] = maps[0]
            self.metadata['tp_path'] = maps[1]
            self.metadata['p_iter']  = maps[2]
            self.metadata['p_path']  = maps[3]
            self.metadata['sname']  = maps[4]

    def get_added_media_objects(self):
        return self.added_files

    def clear_added_media_objects(self):
        self.added_files = []
        
    def get_number_of_people(self):
        return len(self.person_map)

    def get_person_keys(self):
        if self.person_map:
            return self.person_map.keys()
        return []

    def get_family_keys(self):
        if self.family_map:
            return self.family_map.keys()
        return []

    def sort_by_name(self,f,s):
        n1 = self.person_map.get(f)[2].sname
        n2 = self.person_map.get(s)[2].sname
        return cmp(n1,n2)

    def sort_person_keys(self):
        if self.person_map:
            keys = self.person_map.keys()
            keys.sort(self.sort_by_name)
            return keys
        return []

    def get_person_display(self,key):
        data = self.person_map.get(key)

        if data[2] == Person.male:
            gender = const.male
        elif data[2] == Person.female:
            gender = const.female
        else:
            gender = const.unknown

        return [ data[3].get_name(),
                 data[1],
                 gender,
                 data[7],
                 data[6],
                 data[3].get_sort_name(),
                 data[7],
                 data[6],
                 GrampsCfg.get_display_surname()(data[3])]

    def set_iprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.iprefix = val
            else:
                self.iprefix = val + "%d"
        else:
            self.iprefix = "I%04d"
            
    def set_sprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.sprefix = val
            else:
                self.sprefix = val + "%d"
        else:
            self.sprefix = "S%04d"
            
    def set_oprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.oprefix = val
            else:
                self.oprefix = val + "%d"
        else:
            self.oprefix = "O%04d"

    def set_pprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.pprefix = val
            else:
                self.pprefix = val + "%d"
        else:
            self.pprefix = "P%04d"

    def set_fprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.fprefix = val
            else:
                self.fprefix = val + "%d"
        else:
            self.fprefix = "F%04d"

    def set_eprefix(self,val):
        if val:
            if _id_reg.search(val):
                self.eprefix = val
            else:
                self.eprefix = val + "%d"
        else:
            self.eprefix = "E%04d"
            
    def start_transaction(self,msg=""):
        return Transaction(msg,self.undodb)

    def add_transaction(self,transaction,msg):
        if not len(transaction):
            return
        transaction.set_description(msg)
        self.undoindex += 1
        if self.undoindex == _UNDO_SIZE:
            self.translist = transaction[0:-1] + [ transaction ]
        else:
            self.translist[self.undoindex] = transaction
            
        if self.undolabel:
            self.undolabel.set_sensitive(1)
            label = self.undolabel.get_children()[0]
            label.set_text(_("_Undo %s") % transaction.get_description())
            label.set_use_underline(1)

    def undo(self):
        if self.undoindex == -1:
            return
        transaction = self.translist[self.undoindex]

        self.undoindex -= 1
        subitems = transaction.get_recnos()
        subitems.reverse()
        for record_id in subitems:
            (key, handle, data) = transaction.get_record(record_id)
            if key == PERSON_KEY:
                if data == None:
                    del self.person_map[str(handle)]
                else:
                    self.person_map[str(handle)] = data
            elif key == FAMILY_KEY:
                if data == None:
                    del self.family_map[str(handle)]
                else:
                    self.family_map[str(handle)] = data
            elif key == SOURCE_KEY:
                if data == None:
                    del self.source_map[str(handle)]
                else:
                    self.source_map[str(handle)] = data
            elif key == EVENT_KEY:
                if data == None:
                    del self.event_map[str(handle)]
                else:
                    self.event_map[str(handle)] = data
            elif key == PLACE_KEY:
                if data == None:
                    del self.place_map[str(handle)]
                else:
                    self.place_map[str(handle)] = data
            elif key == MEDIA_KEY:
                if data == None:
                    del self.media_map[str(handle)]
                else:
                    self.media_map[str(handle)] = data

        if self.undolabel:
            label = self.undolabel.get_children()[0]
            if self.undoindex == -1:
                label.set_text(_("_Undo"))
                self.undolabel.set_sensitive(0)
            else:
                transaction = self.translist[self.undoindex]
                label.set_text(_("_Undo %s") % transaction.get_description())
                self.undolabel.set_sensitive(1)
            label.set_use_underline(1)

    def set_undo_label(self,label):
        self.undolabel = label
        self.undolabel.set_sensitive(0)

    def set_redo_label(self,label):
        self.redolabel = label
        self.redolabel.set_sensitive(0)

    def get_surnames(self):
        assert(0,"Needs to be overridden in the derived class")

    def get_eventnames(self):
        assert(0,"Needs to be overridden in the derived class")

    def get_bookmarks(self):
        """returns the list of Person instances in the bookmarks"""
        return self.bookmarks

    def clean_bookmarks(self):
        """cleans up the bookmark list, removing empty slots"""
        new_bookmarks = []
        for person_handle in self.bookmarks:
            new_bookmarks.append(person_handle)
        self.bookmarks = new_bookmarks
            
    def set_researcher(self,owner):
        """sets the information about the owner of the database"""
        self.owner.set(owner.get_name(),owner.get_address(),owner.get_city(),
                       owner.get_state(),owner.get_country(),
                       owner.get_postal_code(),owner.get_phone(),owner.get_email())

    def get_researcher(self):
        """returns the Researcher instance, providing information about
        the owner of the database"""
        return self.owner

    def set_default_person(self,person):
        """sets the default Person to the passed instance"""
#        if (self.default):
#            self.default.set_ancestor(0)
        self.metadata['default'] = person.get_handle()
#        if person:
#            self.default.set_ancestor(1)

    def set_default_person_handle(self,handle):
        """sets the default Person to the passed instance"""
        self.metadata['default'] = handle

    def get_default_person(self):
        """returns the default Person of the database"""
        if self.metadata and self.metadata.has_key('default'):
            person = Person()
            handle = self.metadata['default']
            data = self.person_map.get(str(handle))
            person.unserialize(data)
            return person
        return None

    def get_person(self,handle):
        """returns a Person from a GRAMPS's ID"""
        p = Person()
        data = self.person_map.get(str(handle))
        p.unserialize(data)
        return p

    def get_place_handle_map(self):
        """returns a map of gramps's IDs to Place instances"""
        return self.place_map

    def set_place_handle_map(self,map):
        """sets the map of gramps's IDs to Place instances"""
        self.place_map = map

    def get_family_handle(self,handle):
        """returns a map of gramps's IDs to Family instances"""
        return self.family_map.get(str(handle))

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

    def get_place_handles(self):
        """returns a list of Place instances"""
        return self.place_map.keys() 

    def get_family_relation_types(self):
        """returns a list of all relationship types assocated with Family
        instances in the database"""
        return []

    def remove_person_handle(self,handle,transaction):
        assert(0,"Needs to be overridden in the derived class")

    def remove_source_handle(self,handle,transaction):
        assert(0,"Needs to be overridden in the derived class")

    def remove_event_handle(self,handle,transaction):
        assert(0,"Needs to be overridden in the derived class")

    def has_person_handle(self,val):    
        return self.person_map.has_key(str(val))

    def has_family_handle(self,val):            
        return self.family_map.has_key(str(val))

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

    def find_person_from_gramps_id(self,val,trans):
        """finds a Person in the database from the passed gramps' ID.
        If no such Person exists, a new Person is added to the database."""

        person = Person()
        data = self.id_trans.get(str(val))
        if data:
            person.unserialize(cPickle.loads(data))
        else:
            intid = Utils.create_id()
            person.set_handle(intid)
            person.set_gramps_id(val)
            self.add_person(person,trans)
        return person

    def has_object_handle(self,handle):
        """finds an Object in the database from the passed gramps' ID.
        If no such Source exists, a new Source is added to the database."""

        return self.media_map.get(str(handle)) != None

    def remove_object(self,handle,transaction):
        assert(0,"Needs to be overridden in the derived class")

    def remove_place(self,handle,transaction):
        assert(0,"Needs to be overridden in the derived class")

    def add_place_as(self,place,trans):
        if trans != None:
            trans.add(PLACE_KEY,place.get_handle(),None)
        self.place_map[str(place.get_handle())] = place.serialize()
        return place.get_handle()

    def sortbyplace(self,f,s):
        return cmp(self.placesortmap[f], self.placesortmap[s])

    def sortbysource(self,f,s):
        fp = self.source_map[f][2].upper()
        sp = self.source_map[s][2].upper()
        return cmp(fp,sp)

    def sortbymedia(self,f,s):
        fp = self.media_map[f][4].upper()
        sp = self.media_map[s][4].upper()
        return cmp(fp,sp)

    def sort_place_keys(self):
        if self.place_map:
            self.placesortmap = {}
            for key in self.place_map.keys():
                self.placesortmap[key] = self.place_map[key][2].upper()
            keys = self.placesortmap.keys()
            keys.sort(self.sortbyplace)
            del self.placesortmap
            return keys
        return []

    def sort_media_keys(self):
        if self.media_map:
            keys = self.media_map.keys()
            keys.sort(self.sortbymedia)
            return keys
        else:
            return []

    def sort_source_keys(self):
        if self.source_map:
            keys = self.source_map.keys()
            keys.sort(self.sortbysource)
            return keys
        else:
            return []

    def get_place_handle_keys(self):
        if self.place_map:
            return self.place_map.keys()
        else:
            return []

    def get_place_display(self,key):
        # fix this up better
        place = Place()
        place.unserialize(self.place_map[str(key)])
        return place.get_display_info()
        
    def get_source_keys(self):
        if self.source_map:
            return self.source_map.keys()
        return []

    def get_object_keys(self):
        if self.media_map:
            return self.media_map.keys()
        return []

    def get_event_keys(self):
        if self.event_map:
            return self.event_map.keys()
        return []

    def sortbysource(self,f,s):
        f1 = self.source_map[f][1].upper()
        s1 = self.source_map[s][1].upper()
        return cmp(f1,s1)

    def set_source_keys(self):
        keys = self.source_map.keys()
        if type(keys) == type([]):
            keys.sort(self.sortbyplace)
        return keys
    
    def get_source_display(self,key):
        source = Source()
        source.unserialize(self.source_map.get(str(key)))
        return source.get_display_info()

    def build_source_display(self,nkey,okey=None):
        pass
        
    def new_family(self,trans):
        """adds a Family to the database, assigning a gramps' ID"""
        
        index = self.fprefix % self.fmap_index
        while self.family_map.get(str(index)):
            self.fmap_index = self.fmap_index + 1
            index = self.fprefix % self.fmap_index
        self.fmap_index = self.fmap_index + 1
        family = Family()
        family.set_handle(index)
        if trans != None:
            trans.add(FAMILY_KEY, index, None)
        self.family_map[str(index)] = family.serialize()
        return family

    def delete_family(self,family_handle,trans):
        """deletes the Family instance from the database"""
        if self.family_map.get(str(family_handle)):
            if trans != None:
                old_data = self.family_map.get(str(family_handle))
                trans.add(FAMILY_KEY,family_handle,old_data)
            del self.family_map[str(family_handle)]

    def set_column_order(self,list):
        if self.metadata != None:
            self.metadata['columns'] = list

    def set_place_column_order(self,list):
        if self.metadata != None:
            self.metadata['place_columns'] = list

    def set_source_column_order(self,list):
        if self.metadata != None:
            self.metadata['source_columns'] = list

    def set_media_column_order(self,list):
        if self.metadata != None:
            self.metadata['media_columns'] = list

    def get_column_order(self):
        default = [(1,1),(1,2),(1,3),(0,4),(1,5),(0,6),(0,7)]
        if self.metadata == None:
            return default
        else:
            cols = self.metadata.get('columns',default)
            if len(cols) != len(default):
                return cols + default[len(cols):]
            else:
                return cols

    def get_place_column_order(self):
        default = [(1,1),(1,2),(0,3),(1,4),(0,5),(1,6),(0,7),(0,8)]
        if self.metadata == None:
            return default
        else:
            cols = self.metadata.get('place_columns',default)
            if len(cols) != len(default):
                return cols + default[len(cols):]
            else:
                return cols

    def get_source_column_order(self):
        default = [(1,1),(1,2),(1,3),(0,4)]
        if self.metadata == None:
            return default
        else:
            cols = self.metadata.get('source_columns',default)
            if len(cols) != len(default):
                return cols + default[len(cols):]
            else:
                return cols

    def get_media_column_order(self):
        default = [(1,1),(1,2),(1,3)]
        if self.metadata == None:
            return default
        else:
            cols = self.metadata.get('meda_columns',default)
            if len(cols) != len(default):
                return cols + default[len(cols):]
            else:
                return cols
#-------------------------------------------------------------------------
#
# Transaction
#
#-------------------------------------------------------------------------
class Transaction:

    def __init__(self,msg,db):
        self.db = db
        self.first = None
        self.last = None

    def get_description(self):
        return self.msg

    def set_description(self,msg):
        self.msg = msg

    def add(self, type, handle, data):
        self.last = self.db.append(cPickle.dumps((type,handle,data),1))
        if self.first == None:
            self.first = self.last

    def get_recnos(self):
        return range (self.first, self.last+1)

    def get_record(self,id):
        return cPickle.loads(self.db[id])

    def __len__(self):
        if self.last and self.first:
            return self.last - self.first + 1
        return 0

    def display(self):
        for record in self.get_recnos():
            (key,handle,val) = self.get_record(record)
            if key == PERSON_KEY:
                if val:
                    print "PERSON %s change" % handle
                else:
                    print "PERSON %s remove" % handle
            elif key == FAMILY_KEY:
                if val:
                    print "FAMILY %s change" % handle
                else:
                    print "FAMILY %s remove" % handle
            elif key == EVENT_KEY:
                if val:
                    print "EVENT %s change" % handle
                else:
                    print "EVENT %s remove" % handle
            elif key == SOURCE_KEY:
                if val:
                    print "SOURCE %s change" % handle
                else:
                    print "SOURCE %s remove" % handle
            elif key == MEDIA_KEY:
                if val:
                    print "MEDIA %s change" % handle
                else:
                    print "MEDIA %s remove" % handle
            elif key == PLACE_KEY:
                if val:
                    print "PLACE %s change" % handle
                else:
                    print "PLACE %s remove" % handle


