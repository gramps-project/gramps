
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

"""The core library of the GRAMPS database"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from re import compile
import os
import os.path
import types
import accent
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Date import Date, SingleDate, compare_dates, not_too_old
import GrampsCfg
import const
import Utils

#-------------------------------------------------------------------------
#
# Confidence levels
#
#-------------------------------------------------------------------------

CONF_VERY_HIGH = 4
CONF_HIGH      = 3
CONF_NORMAL    = 2
CONF_LOW       = 1
CONF_VERY_LOW  = 0

#-------------------------------------------------------------------------
#
# Class definitions
#
#-------------------------------------------------------------------------

class PrimaryObject:
    """
    The base class for all primary objects in the database. Primary objects
    are the core objects in the database. Each object has a database handle
    and a GRAMPS ID value. The database handle is used as the record number
    for the database, and the GRAMPS ID is the user visible version.
    """

    def __init__(self,source=None):
        """
        Initialize a PrimaryObject. If source is None, both the ID and handle
        are assigned as empty strings. If source is not None, then object
        is initialized from values of the source object.
        """
        if source:
            self.gramps_id = source.gramps_id
            self.handle = source.handle
        else:
            self.gramps_id = None
            self.handle = None

    def set_handle(self,handle):
        """Sets the database handle for the primary object"""
        self.handle = handle

    def get_handle(self):
        """Returns the database handle for the primary object"""
        return self.handle

    def set_gramps_id(self,gramps_id):
        """Sets the GRAMPS ID for the primary object"""
        self.gramps_id = gramps_id

    def get_gramps_id(self):
        """Returns the GRAMPS ID for the primary object"""
        return self.gramps_id

class SourceNote:
    """Base class for storing source references and notes"""
    
    def __init__(self,source=None):
        """Create a new SourceNote, copying from source if not None"""
        
        self.source_list = []
        self.note = None

        if source:
            for sref in source.source_list:
                self.source_list.append(SourceRef(sref))
            if source.note:
                self.note = Note(source.note.get())

    def add_source_reference(self,handle) :
        """Set the source reference"""
        self.source_list.append(handle)

    def get_source_references(self) :
        """Return the source reference"""
        return self.source_list

    def set_source_reference_list(self,list) :
        """Replaces the source reference"""
        self.source_list = list

    def set_note(self,text):
        """Set the note to the given text"""
        if self.note == None:
            self.note = Note()
        self.note.set(text)

    def get_note(self):
        """Return the current note"""
        if self.note == None:
            return ""
        else:
            return self.note.get() 

    def set_note_format(self,val):
        """Set the note's format to the given value"""
        if self.note:
            self.note.set_format(val)

    def get_note_format(self):
        """Return the current note's format"""
        if self.note == None:
            return 0
        else:
            return self.note.get_format()

    def set_note_object(self,obj):
        """Change the note object instance to obj"""
        self.note = obj

    def get_note_object(self):
        """Return in note instance, not just the text"""
        return self.note

    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.note = Note(self.note.get())

class DataObj(SourceNote):
    """Base class for data elements, providing source, note, and privacy data"""

    def __init__(self,source=None):
        """Create a new DataObj, copying data from a source object if provided"""
        SourceNote.__init__(self,source)
        
        if source:
            self.private = source.private
        else:
            self.private = 0

    def set_privacy(self,val):
        """Sets or clears the privacy flag of the data"""
        self.private = val

    def get_privacy(self):
        """Returns the privacy level of the data"""
        return self.private

class Person(PrimaryObject,SourceNote):
    """
    GRAMPS Person record. Represents an individual person. Contains all
    information about the person, including names, events, attributes,
    and other information.
    """
    
    unknown = 2
    male = 1
    female = 0

    def __init__(self,handle=""):
        """creates a new Person instance"""
        PrimaryObject.__init__(self)
        SourceNote.__init__(self)
        self.primary_name = Name()
        self.event_list = []
        self.family_list = []
        self.parent_family_list = []
        self.media_list = []
        self.nickname = ""
        self.alternate_names = []
        self.gender = Person.unknown
        self.death_handle = None
        self.birth_handle = None
        self.address_list = []
        self.attribute_list = []
        self.urls = []
        self.lds_bapt = None
        self.lds_endow = None
        self.lds_seal = None
        self.complete = 0

        # We hold a reference to the GrampsDB so that we can maintain
        # its genderStats.  It doesn't get set here, but from
        # GenderStats.count_person.
        self.db = None
        
    def serialize(self):
        """
        Converts the data held in the event to a Python tuple that
        represents all the data elements. This method is used to convert
        the object into a form that can easily be saved to a database.

        These elements may be primative Python types (string, integers),
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objectes or
        lists), the database is responsible for converting the data into
        a form that it can use.
        """
        return (self.handle, self.gramps_id, self.gender, 
                self.primary_name, self.alternate_names, self.nickname, 
                self.death_handle, self.birth_handle, self.event_list,
                self.family_list, self.parent_family_list,
                self.media_list, self.address_list, self.attribute_list,
                self.urls, self.lds_bapt, self.lds_endow, self.lds_seal,
                self.complete, self.source_list, self.note)

    def unserialize(self,data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in an Event structure.
        """
        (self.handle, self.gramps_id, self.gender, self.primary_name,
         self.alternate_names, self.nickname, self.death_handle,
         self.birth_handle, self.event_list, self.family_list,
         self.parent_family_list, self.media_list, self.address_list,
         self.attribute_list, self.urls, self.lds_bapt, self.lds_endow,
         self.lds_seal, self.complete, self.source_list, self.note) = data
            
    def set_complete_flag(self,val):
        """
        Sets or clears the complete flag, which is used to indicate that the
        Person's data is considered to be complete.
        """
        self.complete = val

    def get_complete_flag(self):
        """
        Gets the complete flag, which is used to indicate that the
        Person's data is considered to be complete.
        """
        return self.complete

    def get_display_info(self):
        """
        Returns a list consisting of the information typically used for a display.
        The data consists of: Display Name, ID, Gender, Date of Birth,
        Date of Death, sort name, etc.
        """
        if self.gender == Person.male:
            gender = const.male
        elif self.gender == Person.female:
            gender = const.female
        else:
            gender = const.unknown
        bday = self.birth_handle
        dday = self.death_handle
        return [ GrampsCfg.get_display_name()(self), self.gramps_id,
                 gender, bday, dday, self.get_primary_name().get_sort_name(),
                 GrampsCfg.get_display_surname()(self.primary_name)]
                                          
    def set_primary_name(self,name):
        """sets the primary name of the Person to the specified
        Name instance"""
        db = self.db
        if db:
            db.genderStats.uncount_person (self)
        self.primary_name = name
        if db:
            db.genderStats.count_person (self, db)

    def get_primary_name(self):
        """returns the Name instance marked as the Person's primary name"""
        return self.primary_name

    def get_alternate_names(self):
        """returns the list of alternate Names"""
        return self.alternate_names

    def set_alternate_names(self,list):
        """changes the list of alternate names to the passed list"""
        self.alternate_names = list

    def add_alternate_name(self,name):
        """adds an alternate Name instance to the list"""
        self.alternate_names.append(name)

    def get_url_list(self):
        """returns the list of URL instances"""
        return self.urls

    def set_url_list(self,list):
        """sets the list of URL instances to list"""
        self.urls = list

    def add_url(self,url):
        """adds a URL instance to the list"""
        self.urls.append(url)
    
    def set_nick_name(self,name):
        """sets the nickname for the Person"""
        self.nickname = name

    def get_nick_name(self) :
        """returns the nickname for the Person"""
        return self.nickname

    def set_gender(self,val) :
        """sets the gender of the Person"""
        db = self.db
        if db:
            db.genderStats.uncount_person (self)
        self.gender = val
        if db:
            db.genderStats.count_person (self, db)

    def get_gender(self) :
        """returns the gender of the Person"""
        return self.gender

    def set_birth_handle(self,event_handle) :
        """sets the birth event to the passed event"""
        self.birth_handle = event_handle

    def set_death_handle(self,event_handle) :
        """sets the death event to the passed event"""
        self.death_handle = event_handle

    def get_birth_handle(self) :
        """returns the birth event"""
        return self.birth_handle

    def get_death_handle(self) :
        """returns the death event"""
        return self.death_handle

    def add_media_reference(self,media_id):
        """adds a MediaObject instance to the image list"""
        self.media_list.append(media_id)

    def get_media_list(self):
        """returns the list of MediaObjects"""
        return self.media_list

    def set_media_list(self,list):
        """Sets the list of MediaObject objects"""
        self.media_list = list

    def add_event_handle(self,event_handle):
        """adds an Event to the event list"""
        self.event_list.append(event_handle)

    def get_event_list(self):
        """returns the list of Event instances"""
        return self.event_list

    def set_event_list(self,elist):
        """sets the event list to the passed list"""
        self.event_list = elist

    def add_family_handle(self,family_handle):
        """adds the specified Family instance to the list of
        families/marriages/partnerships in which the person is a
        parent or spouse"""

        self.family_list.append(family_handle)

    def set_preferred_family_handle(self,family):
        if family in self.family_list:
            self.family_list.remove(family)
            self.family_list = [family] + self.family_list

    def get_family_handle_list(self) :
        """returns the list of Family instances in which the
        person is a parent or spouse"""
        return self.family_list

    def clear_family_handle_list(self) :
        """
        Removes all familyts from the family list.
        """
        self.family_list = []

    def remove_family_handle(self,family):
        """removes the specified Family instance from the list
        of marriages/partnerships"""
        if family in self.family_list:
            self.family_list.remove(family)

    def add_address(self,address):
        """adds the Address instance to the list of addresses"""
        self.address_list.append(address)

    def remove_address(self,address):
        """removes the Address instance from the list of addresses"""
        if address in self.address_list:
            self.address_list.remove(address)

    def get_address_list(self):
        """returns the list of addresses"""
        return self.address_list

    def set_address_list(self,alist):
        """sets the address list to the specified list"""
        self.address_list = alist

    def add_attribute(self,attribute):
        """adds an Attribute instance to the attribute list"""
        self.attribute_list.append(attribute)

    def remove_attribute(self,attribute):
        """removes the specified Attribute instance from the attribute list"""
        if attribute in self.attribute_list:
            self.attribute_list.remove(attribute)

    def get_attribute_list(self):
        """returns the attribute list"""
        return self.attribute_list

    def set_attribute_list(self,list):
        """sets the attribute list to the specified list"""
        self.attribute_list = list

    def get_parent_family_handle_list(self):
        """returns the list of alternate Family instances, in which the Person
        is a child of the family, but not a natural child of both parents"""
        return self.parent_family_list

    def add_parent_family_handle(self,family,mrel,frel):
        """adds a Family to the alternate family list, indicating the
        relationship to the mother (mrel) and the father (frel)"""
        self.parent_family_list.append((family,mrel,frel))

    def clear_parent_family_handle_list(self):
        self.parent_family_list = []

    def remove_parent_family_handle(self,family):
        """removes a Family instance from the alternate family list"""
        for f in self.parent_family_list[:]:
            if f[0] == family:
                self.parent_family_list.remove(f)
                return f
        else:
            return None

    def change_parent_family_handle(self,family,mrel,frel):
        """removes a Family instance from the alternate family list"""
        index = 0
        for f in self.parent_family_list[:]:
            if f[0] == family:
                self.parent_family_list[index] = (family,mrel,frel)
            index += 1

    def has_family(self,family):
        for f in self.parent_family_list:
            if f[0] == family:
                return f
        else:
            return None

    def set_main_parent_family_handle(self,family):
        """sets the main Family of the Person, the Family in which the
        Person is a natural born child"""
        f = self.remove_parent_family_handle(family)
        if f:
            self.parent_family_list = [f] + self.parent_family_list
        
    def get_main_parents_family_handle(self):
        """returns the main Family of the Person, the Family in which the
        Person is a natural born child"""
        if len(self.parent_family_list) == 0:
            return None
        else:
            return self.parent_family_list[0][0]

    def set_lds_baptism(self,ord):
        """Sets the LDS Baptism ordinance"""
        self.lds_bapt = ord

    def get_lds_baptism(self):
        """Gets the LDS Baptism ordinance"""
        return self.lds_bapt

    def set_lds_endowment(self,ord):
        """Sets the LDS Endowment ordinance"""
        self.lds_endow = ord

    def get_lds_endowment(self):
        """Gets the LDS Endowment ordinance"""
        return self.lds_endow

    def set_lds_sealing(self,ord):
        """Sets the LDS Sealing ordinance"""
        self.lds_seal = ord

    def get_lds_sealing(self):
        """Gets the LDS Sealing ordinance"""
        return self.lds_seal

    def probably_alive(self,db):
        """Returns true if the person may be alive."""
        if self.death_handle:
            return False
        if self.birth_handle:
            birth = db.get_event_from_handle(self.birth_handle)
            if birth.get_date() != "":
                return not_too_old(birth.get_date_object().get_start_date())

        # Neither birth nor death events are available.  Try looking
        # for descendants that were born more than a lifespan ago.

        min_generation = 13
        max_generation = 60
        max_age_difference = 60
        def descendants_too_old (person, years):
            for family_handle in person.get_family_handle_list():
                family = db.get_family_from_handle(family_handle)
                for child_handle in family.get_child_handle_list():
                    child = db.get_person_from_handle(child_handle)
                    if child.birth_handle:
                        child_birth = db.get_event_from_handle(child.birth_handle)
                        if child_birth.get_date() != "":
                            d = SingleDate (child_birth.get_date_object().get_start_date())
                            d.set_year (d.get_year() - years)
                            if not not_too_old (d):
                                return True

                    if child.death_handle:
                        child_death = db.get_event_from_handle(child.death_handle)
                        if child_death.get_date() != "":
                            d = SingleDate (child_death.get_date_object().get_start_date())
                            if not not_too_old (d):
                                return True

                    if descendants_too_old (child, years + min_generation):
                        return True

        if descendants_too_old (self, min_generation):
            return False

        # What about their parents?
        def parents_too_old (person, age_difference):
            family_handle = person.get_main_parents_family_handle()
            if family_handle:
                family = db.get_family_from_handle(family_handle)
                for parent_id in [family.get_father_handle(), family.get_mother_handle()]:
                    if not parent_id:
                        continue

                    parent = db.get_person_from_handle(parent_id)
                    if parent.birth_handle:
                        parent_birth = db.get_event_from_handle(parent.birth_handle)
                        if parent_birth.get_date():
                            d = SingleDate (parent_birth.get_date_object().get_start_date())
                            d.set_year (d.get_year() + max_generation + age_difference)
                            if not not_too_old (d):
                                return True

                    if parent.death_handle:
                        parent_death = db.get_event_from_handle(parent.death_handle)
                        if parent_death.get_date() != "":
                            d = SingleDate (parent_death.get_date_object().
                                        get_start_date())
                            d.set_year (d.get_year() + age_difference)
                            if not not_too_old (d):
                                return True

        if parents_too_old (self, 0):
            return False

        # As a last resort, trying seeing if their spouse's age gives
        # any clue.
        for family_handle in self.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            for spouse_id in [family.get_father_handle(), family.get_mother_handle()]:
                if not spouse_id or spouse_id == self.handle:
                    continue
                spouse = db.get_person_from_handle(spouse_id)
                sp_birth_handle = spouse.get_birth_handle()
                sp_death_handle = spouse.get_death_handle()
                if sp_birth_handle:
                    spouse_birth = db.find_event_from_handle(sp_birth_handle)
                    if spouse_birth.get_date() != "":
                        d = SingleDate (spouse_birth.get_date_object().get_start_date())
                        d.set_year (d.get_year() + max_age_difference)
                        if not not_too_old (d):
                            return False

                if sp_death_handle:
                    spouse_death = db.find_event_from_handle(sp_death_handle)
                    if spouse_death.get_date() != "":
                        d = SingleDate (spouse_birth.get_date_object().get_start_date())
                        d.set_year (d.get_year() - min_generation)
                        if not not_too_old (d):
                            return False

                if parents_too_old (spouse, max_age_difference):
                    return False
        return True

class Family(PrimaryObject,SourceNote):
    """
    GRAMPS Family record. Represents a family unit, which defines the
    relationship between people. This can consist of a single person and
    a set of children, or two people with a defined relationship and an
    optional set of children. The relationship between people may be either
    opposite sex or same sex.
    """

    def __init__(self):
        """creates a new Family instance"""
        PrimaryObject.__init__(self)
        SourceNote.__init__(self)
        self.father_handle = None
        self.mother_handle = None
        self.child_list = []
        self.type = const.FAMILY_MARRIED
        self.event_list = []
        self.media_list = []
        self.attribute_list = []
        self.lds_seal = None
        self.complete = 0


    def serialize(self):
        """
        Converts the data held in the event to a Python tuple that
        represents all the data elements. This method is used to convert
        the object into a form that can easily be saved to a database.

        These elements may be primative Python types (string, integers),
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objectes or
        lists), the database is responsible for converting the data into
        a form that it can use.
        """
        return (self.handle, self.gramps_id, self.father_handle, self.mother_handle,
                self.child_list, self.type, self.event_list,
                self.media_list, self.attribute_list, self.lds_seal,
                self.complete, self.source_list, self.note)

    def unserialize(self, data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in an Event structure.
        """
        (self.handle, self.gramps_id, self.father_handle, self.mother_handle,
         self.child_list, self.type, self.event_list,
         self.media_list, self.attribute_list, self.lds_seal,
         self.complete, self.source_list, self.note) = data

    def set_complete_flag(self,val):
        self.complete = val

    def get_complete_flag(self):
        return self.complete

    def set_lds_sealing(self,ord):
        self.lds_seal = ord

    def get_lds_sealing(self):
        return self.lds_seal

    def add_attribute(self,attribute) :
        """adds an Attribute instance to the attribute list"""
        self.attribute_list.append(attribute)

    def remove_attribute(self,attribute):
        """removes the specified Attribute instance from the attribute list"""
        if attribute in self.attribute_list:
            self.attribute_list.remove(attribute)

    def get_attribute_list(self) :
        """returns the attribute list"""
        return self.attribute_list

    def set_attribute_list(self,list) :
        """sets the attribute list to the specified list"""
        self.attribute_list = list

    def set_relationship(self,type):
        """assigns a string indicating the relationship between the
        father and the mother"""
        self.type = type

    def get_relationship(self):
        """returns a string indicating the relationship between the
        father and the mother"""
        return self.type
    
    def set_father_handle(self,person_handle):
        """sets the father of the Family to the specfied Person"""
        self.father_handle = person_handle

    def get_father_handle(self):
        """returns the father of the Family"""
       	return self.father_handle

    def set_mother_handle(self,person):
        """sets the mother of the Family to the specfied Person"""
        self.mother_handle = person

    def get_mother_handle(self):
        """returns the mother of the Family"""
       	return self.mother_handle

    def add_child_handle(self,person):
        """adds the specfied Person as a child of the Family, adding it
        to the child list"""
        if person not in self.child_list:
            self.child_list.append(person)
            
    def remove_child_handle(self,person):
        """removes the specified Person from the child list"""
        if person in self.child_list:
            self.child_list.remove(person)

    def get_child_handle_list(self):
        """returns the list of children"""
        return self.child_list

    def set_child_handle_list(self, list):
        """sets the list of children"""
        self.child_list = list[:]

    def add_event_handle(self,event_handle):
        """adds an Event to the event list"""
        self.event_list.append(event_handle)

    def get_event_list(self) :
        """returns the list of Event instances"""
        return self.event_list

    def set_event_list(self,list) :
        """sets the event list to the passed list"""
        self.event_list = list

    def add_media_reference(self,media_id):
        """Adds a MediaObject object to the Family instance's image list"""
        self.media_list.append(media_id)

    def get_media_list(self):
        """Returns the list of MediaObject objects"""
        return self.media_list

    def set_media_list(self,list):
        """Sets the list of MediaObject objects"""
        self.media_list = list

class Event(PrimaryObject,DataObj):
    """
    GRAMPS Event record. A GRAMPS event is some type of action that occurred
    at a particular place at a particular time, such as a birth, death, or
    marriage.
    """

    NAME = 0
    ID = 1
    
    def __init__(self,source=None):
        """creates a new Event instance, copying from the source if present"""

        PrimaryObject.__init__(self,source)
        DataObj.__init__(self,source)
        
        if source:
            self.place = source.place
            self.date = Date(source.date)
            self.description = source.description
            self.name = source.name
            self.cause = source.cause
            self.media_list = [MediaRef(media_id) for media_id in source.media_list]
            if source.witness != None:
                self.witness = source.witness[:]
            else:
                self.witness = None
        else:
            self.place = u''
            self.date = None
            self.description = ""
            self.name = ""
            self.cause = ""
            self.witness = None
            self.media_list = []

    def serialize(self):
        """
        Converts the data held in the event to a Python tuple that
        represents all the data elements. This method is used to convert
        the object into a form that can easily be saved to a database.

        These elements may be primative Python types (string, integers),
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objectes or
        lists), the database is responsible for converting the data into
        a form that it can use.
        """
        return (self.handle, self.gramps_id, self.name, self.date,
                self.description, self.place, self.cause, self.private,
                self.source_list, self.note, self.witness, self.media_list)

    def unserialize(self,data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in an Event structure.
        """
        (self.handle, self.gramps_id, self.name, self.date, self.description,
         self.place, self.cause, self.private, self.source_list,
         self.note, self.witness, self.media_list) = data

    def add_media_reference(self,media_id):
        """Adds a MediaObject object to the Event object's image list"""
        self.media_list.append(media_id)

    def get_media_list(self):
        """Returns the list of MediaObject objects"""
        return self.media_list

    def set_media_list(self,mlist):
        """Sets the list of MediaObject objects"""
        self.media_list = mlist

    def get_witness_list(self):
        """Returns the list of Witness objects associated with the Event"""
        return self.witness

    def set_witness_list(self,list):
        """
        Sets the Witness list to a copy of the list passed to the method.
        """
        if list:
            self.witness = list[:]
        else:
            self.witness = None

    def add_witness(self,value):
        """
        Adds a Witness object to the current witness list.
        """
        if self.witness:
            self.witness.append(value)
        else:
            self.witness = [value]
        
    def is_empty(self):
        
        date = self.get_date_object()
        place = self.get_place_handle()
        description = self.description
        cause = self.cause
        name = self.name
        return (not name or name == "Birth" or name == "Death") and \
                   date.is_empty() and not place and not description and not cause

    def set(self,name,date,place,description):
        """sets the name, date, place, and description of an Event instance"""
        self.name = name
        self.place = place
        self.description = description
        self.set_date(date)
        
    def are_equal(self,other):
        """returns 1 if the specified event is the same as the instance"""
        if other == None:
            other = Event (None)
        if (self.name != other.name or self.place != other.place or
            self.description != other.description or self.cause != other.cause or
            self.private != other.private or
            compare_dates(self.get_date_object(),other.get_date_object()) or
            len(self.get_source_references()) != len(other.get_source_references())):
            return 0

        index = 0
        olist = other.get_source_references()
        for a in self.get_source_references():
            if not a.are_equal(olist[index]):
                return 0
            index = index + 1

        witness_list = self.get_witness_list()
        other_list = other.get_witness_list()
        if (not witness_list) and (not other_list):
            return 1
        elif not (witness_list and other_list):
            return 0
        for a in witness_list:
            if a in other_list:
                other_list.remove(a)
            else:
                return 0
        if other_list:
            return 0

        return 1
        
    def set_name(self,name):
        """sets the name of the Event"""
        self.name = name

    def get_name(self):
        """returns the name of the Event"""
        return self.name

    def set_place_handle(self,place):
        """sets the Place instance of the Event"""
        self.place = place

    def get_place_handle(self):
        """returns the Place instance of the Event"""
        return self.place 

    def set_cause(self,cause):
        """sets the cause of the Event"""
        self.cause = cause

    def get_cause(self):
        """returns the cause of the Event"""
        return self.cause 

    def set_description(self,description):
        """sets the description of the Event instance"""
        self.description = description

    def get_description(self) :
        """returns the description of the Event instance"""
        return self.description 

    def set_date(self, date) :
        """attempts to sets the date of the Event instance"""
        if not self.date:
            self.date = Date()
        self.date.set(date)

    def get_date(self) :
        """returns a string representation of the date of the Event instance"""
        if self.date:
            return self.date.get_date()
        return ""

    def get_preferred_date(self) :
        """returns a string representation of the date of the Event instance"""
        if self.date:
            return self.date.get_date()
        return ""

    def get_quote_date(self) :
        """returns a string representation of the date of the Event instance,
        enclosing the results in quotes if it is not a valid date"""
        if self.date:
            return self.date.get_quote_date()
        return ""

    def get_date_object(self):
        """returns the Date object associated with the Event"""
        if not self.date:
            self.date = Date()
       	return self.date

    def set_date_object(self,date):
        """sets the Date object associated with the Event"""
        self.date = date

class Place(PrimaryObject,SourceNote):
    """Contains information related to a place, including multiple address
    information (since place names can change with time), longitude, latitude,
    a collection of images and URLs, a note and a source"""
    
    def __init__(self,source=None):
        """Creates a new Place object.

        source - Object to copy. If none supplied, create an empty place object"""
        PrimaryObject.__init__(self,source)
        SourceNote.__init__(self,source)
        if source:
            self.long = source.long
            self.lat = source.lat
            self.title = source.title
            self.main_loc = Location(source.main_loc)
            self.alt_loc = []
            for loc in source.alt_loc:
                self.alt_loc = Location(loc)
            self.urls = []
            for u in source.urls:
                self.urls.append(Url(u))
            self.media_list = []
            for media_id in source.media_list:
                self.media_list.append(MediaRef(media_id))
        else:
            self.long = ""
            self.lat = ""
            self.title = ""
            self.main_loc = None
            self.alt_loc = []
            self.urls = []
            self.media_list = []

    def serialize(self):
        """
        Converts the data held in the event to a Python tuple that
        represents all the data elements. This method is used to convert
        the object into a form that can easily be saved to a database.

        These elements may be primative Python types (string, integers),
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objectes or
        lists), the database is responsible for converting the data into
        a form that it can use.
        """
        return (self.handle, self.gramps_id, self.title, self.long, self.lat,
                self.main_loc, self.alt_loc, self.urls, self.media_list,
                self.source_list, self.note)

    def unserialize(self,data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in an Event structure.
        """
        (self.handle, self.gramps_id, self.title, self.long, self.lat, self.main_loc,
         self.alt_loc, self.urls, self.media_list, self.source_list,
         self.note) = data
            
    def get_url_list(self):
        """Return the list of URLs"""
        return self.urls

    def set_url_list(self,list):
        """Replace the current URL list with the new one"""
        self.urls = list

    def add_url(self,url):
        """Add a URL to the URL list"""
        self.urls.append(url)
    
    def set_title(self,name):
        """Sets the title of the place object"""
        self.title = name

    def get_title(self):
        """Returns the title of the place object"""
        return self.title

    def set_longitude(self,long):
        """Sets the longitude of the place"""
        self.long = long

    def get_longitude(self):
        """Returns the longitude of the place"""
        return self.long

    def set_latitude(self,long):
        """Sets the latitude of the place"""
        self.lat = long

    def get_latitude(self):
        """Returns the latitude of the place"""
        return self.lat

    def get_main_location(self):
        """Returns the Location object representing the primary information"""
        if not self.main_loc:
            self.main_loc = Location()
        return self.main_loc

    def set_main_location(self,loc):
        """Assigns the main location to the Location object passed"""
        self.main_loc = loc

    def get_alternate_locations(self):
        """Returns a list of alternate location information objects"""
        return self.alt_loc

    def set_alternate_locations(self,list):
        """Replaces the current alternate location list with the new one"""
        self.alt_loc = list

    def add_alternate_locations(self,loc):
        """Adds a Location to the alternate location list"""
        if loc not in self.alt_loc:
            self.alt_loc.append(loc)

    def add_media_reference(self,media_id):
        """Adds a MediaObject object to the place object's image list"""
        self.media_list.append(media_id)

    def get_media_list(self):
        """Returns the list of MediaObject objects"""
        return self.media_list

    def set_media_list(self,list):
        """Sets the list of MediaObject objects"""
        self.media_list = list

    def get_display_info(self):
        """Gets the display information associated with the object. This includes
        the information that is used for display and for sorting. Returns a list
        consisting of 13 strings. These are: Place Title, Place ID, Main Location
        Parish, Main Location County, Main Location City, Main Location State/Province,
        Main Location Country, upper case Place Title, upper case Parish, upper
        case city, upper case county, upper case state, upper case country"""
        
        if self.main_loc:
            return [self.title,self.gramps_id,self.main_loc.parish,self.main_loc.city,
                    self.main_loc.county,self.main_loc.state,self.main_loc.country,
                    self.title.upper(), self.main_loc.parish.upper(),
                    self.main_loc.city.upper(), self.main_loc.county.upper(),
                    self.main_loc.state.upper(), self.main_loc.country.upper()]
        else:
            return [self.title,self.gramps_id,'','','','','',
                    self.title.upper(), '','','','','']
        
class MediaObject(PrimaryObject,SourceNote):
    """Containter for information about an image file, including location,
    description and privacy"""
    
    def __init__(self,source=None):
        """Create a new MediaObject object, copying from the source if provided"""
        PrimaryObject.__init__(self,source)
        SourceNote.__init__(self,source)

        self.attrlist = []
        if source:
            self.path = source.path
            self.mime = source.mime
            self.desc = source.desc
            self.thumb = source.thumb
            for attr in source.attrlist:
                self.attrlist.append(Attribute(attr))
        else:
            self.path = ""
            self.mime = ""
            self.desc = ""
            self.thumb = None

    def serialize(self):
        """
        Converts the data held in the event to a Python tuple that
        represents all the data elements. This method is used to convert
        the object into a form that can easily be saved to a database.

        These elements may be primative Python types (string, integers),
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objectes or
        lists), the database is responsible for converting the data into
        a form that it can use.
        """
        return (self.handle, self.gramps_id, self.path, self.mime,
                self.desc, self.attrlist, self.source_list, self.note)

    def unserialize(self,data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in an Event structure.
        """
        (self.handle, self.gramps_id, self.path, self.mime, self.desc,
         self.attrlist, self.source_list, self.note) = data
    
    def set_mime_type(self,type):
        self.mime = type

    def get_mime_type(self):
        return self.mime
    
    def set_path(self,path):
        """set the file path to the passed path"""
        self.path = os.path.normpath(path)

    def get_path(self):
        """return the file path"""
        return self.path

    def set_description(self,text):
        """sets the description of the image"""
        self.desc = text

    def get_description(self):
        """returns the description of the image"""
        return self.desc

    def add_attribute(self,attr):
        """Adds a propery to the MediaObject object. This is not used by gramps,
        but provides a means for XML users to attach other properties to
        the image"""
        self.attrlist.append(attr)

    def get_attribute_list(self):
        """returns the property list associated with the image"""
        return self.attrlist

    def set_attribute_list(self,list):
        self.attrlist = list

class Source(PrimaryObject):
    """A record of a source of information"""
    
    def __init__(self):
        """creates a new Source instance"""
        PrimaryObject.__init__(self)
        self.title = ""
        self.author = ""
        self.pubinfo = ""
        self.note = Note()
        self.media_list = []
        self.abbrev = ""

    def serialize(self):
        return (self.handle, self.gramps_id, self.title, self.author,
                self.pubinfo, self.note, self.media_list, self.abbrev)

    def unserialize(self,data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in an Event structure.
        """
        (self.handle, self.gramps_id, self.title, self.author,
         self.pubinfo, self.note, self.media_list, self.abbrev) = data
        
    def get_display_info(self):
        return [self.title,self.gramps_id,self.author,self.title.upper(),self.author.upper()]

    def add_media_reference(self,media_id):
        """Adds a MediaObject object to the Source instance's image list"""
        self.media_list.append(media_id)

    def get_media_list(self):
        """Returns the list of MediaObject objects"""
        return self.media_list

    def set_media_list(self,list):
        """Sets the list of MediaObject objects"""
        self.media_list = list

    def set_title(self,title):
        """sets the title of the Source"""
        self.title = title

    def get_title(self):
        """returns the title of the Source"""
        return self.title

    def set_note(self,text):
        """sets the text of the note attached to the Source"""
        self.note.set(text)

    def get_note(self):
        """returns the text of the note attached to the Source"""
        return self.note.get()

    def set_note_format(self,val):
        """Set the note's format to the given value"""
        self.note.set_format(val)

    def get_note_format(self):
        """Return the current note's format"""
        return self.note.get_format()

    def set_note_object(self,obj):
        """sets the Note instance attached to the Source"""
        self.note = obj

    def get_note_object(self):
        """returns the Note instance attached to the Source"""
        return self.note

    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.note = Note(self.note.get())

    def set_author(self,author):
        """sets the author of the Source"""
        self.author = author

    def get_author(self):
        """returns the author of the Source"""
        return self.author

    def set_publication_info(self,text):
        """sets the publication information of the Source"""
        self.pubinfo = text

    def get_publication_info(self):
        """returns the publication information of the Source"""
        return self.pubinfo

    def set_abbreviation(self,abbrev):
        """sets the title abbreviation of the Source"""
        self.abbrev = abbrev

    def get_abbreviation(self):
        """returns the title abbreviation of the Source"""
        return self.abbrev

class LdsOrd(SourceNote):
    """
    Class that contains information about LDS Ordinances. LDS
    ordinances are similar to events, but have very specific additional
    information related to data collected by the Church of Jesus Christ
    of Latter Day Saints (Morman church). The LDS church is the largest
    source of genealogical information in the United States.
    """
    def __init__(self,source=None):
        """Creates a LDS Ordinance instance"""
        SourceNote.__init__(self,source)
        if source:
            self.famc = source.famc
            self.date = Date(source.date)
            self.temple = source.temple
            self.status = source.status
            self.place = source.place
        else:
            self.famc = None
            self.date = None
            self.temple = ""
            self.status = 0
            self.place = None

    def set_place_handle(self,place):
        """sets the Place database handle of the ordinance"""
        self.place = place

    def get_place_handle(self):
        """returns the Place handle of the ordinance"""
        return self.place 

    def set_family_handle(self,family):
        """Sets the Family database handle associated with the LDS ordinance"""
        self.famc = family

    def get_family_handle(self):
        """Gets the Family database handle associated with the LDS ordinance"""
        return self.famc

    def set_status(self,val):
        """
        Sets the status of the LDS ordinance. The status is a text string
        that matches a predefined set of strings."""
        self.status = val

    def get_status(self):
        """Gets the status of the LDS ordinance"""
        return self.status

    def set_date(self, date) :
        """attempts to sets the date of the ordinance"""
        if not self.date:
            self.date = Date()
        self.date.set(date)

    def get_date(self) :
        """returns a string representation of the date of the ordinance"""
        if self.date:
            return self.date.get_date()
        return ""

    def get_date_object(self):
        """returns the Date object associated with the ordinance"""
        if not self.date:
            self.date = Date()
       	return self.date

    def set_date_object(self,date):
        """sets the Date object associated with the ordinance"""
        self.date = date

    def set_temple(self,temple):
        """Sets the temple assocated with the ordinance"""
        self.temple = temple

    def get_temple(self):
        """Gets the temple assocated with the ordinance"""
        return self.temple

    def is_empty(self):
        """Returns 1 if the ordidance is actually empty"""
        if (self.famc or 
                (self.date and not self.date.is_empty()) or 
                self.temple or 
                self.status or 
                self.place):
            return 0
        else:
            return 1
        
    def are_equal(self,other):
        """returns 1 if the specified ordinance is the same as the instance"""
        if other == None:
            return self.is_empty()
        if (self.famc != other.famc or
            self.place != other.place or
            self.status != other.status or
            self.temple != other.temple or
            compare_dates(self.get_date_object(),other.get_date_object()) or
            len(self.get_source_references()) != len(other.get_source_references())):
            return 0

        index = 0
        olist = other.get_source_references()
        for a in self.get_source_references():
            if not a.are_equal(olist[index]):
                return 0
            index = index + 1
        return 1

class Researcher:
    """Contains the information about the owner of the database"""
    
    def __init__(self):
        """Initializes the Researcher object"""
        self.name = ""
        self.addr = ""
        self.city = ""
        self.state = ""
        self.country = ""
        self.postal = ""
        self.phone = ""
        self.email = ""

    def get_name(self):
        """returns the database owner's name"""
        return self.name

    def get_address(self):
        """returns the database owner's address"""
        return self.addr

    def get_city(self):
        """returns the database owner's city"""
        return self.city

    def get_state(self):
        """returns the database owner's state"""
        return self.state

    def get_country(self):
        """returns the database owner's country"""
        return self.country

    def get_postal_code(self):
        """returns the database owner's postal code"""
        return self.postal

    def get_phone(self):
        """returns the database owner's phone number"""
        return self.phone

    def get_email(self):
        """returns the database owner's email"""
        return self.email

    def set(self,name,addr,city,state,country,postal,phone,email):
        """sets the information about the database owner"""
        if name:
            self.name = name.strip()
        if addr:
            self.addr = addr.strip()
        if city:
            self.city = city.strip()
        if state:
            self.state = state.strip()
        if country:
            self.country = country.strip()
        if postal:
            self.postal = postal.strip()
        if phone:
            self.phone = phone.strip()
        if email:
            self.email = email.strip()

class Location:
    """Provides information about a place, including city, county, state,
    and country. Multiple Location objects can represent the same place,
    since names of citys, countys, states, and even countries can change
    with time"""
    
    def __init__(self,source=None):
        """creates a Location object, copying from the source object if it exists"""
        if source:
            self.city = source.city
            self.parish = source.parish
            self.county = source.county
            self.state = source.state
            self.country = source.country
            self.postal = source.postal
            self.phone = source.phone
        else:
            self.city = ""
            self.parish = ""
            self.county = ""
            self.state = ""
            self.country = ""
            self.postal = ""
            self.phone = ""

    def is_empty(self):
        return not self.city and not self.county and not self.state and \
               not self.country and not self.postal and not self.phone
        
    def set_city(self,data):
        """sets the city name of the Location object"""
        self.city = data

    def get_postal_code(self):
        """returns the postal code of the Location object"""
        return self.postal

    def set_postal_code(self,data):
        """sets the postal code of the Location object"""
        self.postal = data

    def get_phone(self):
        """returns the phone number of the Location object"""
        return self.phone

    def set_phone(self,data):
        """sets the phone number of the Location object"""
        self.phone = data

    def get_city(self):
        """returns the city name of the Location object"""
        return self.city

    def set_parish(self,data):
        """sets the religious parish name"""
        self.parish = data

    def get_parish(self):
        """gets the religious parish name"""
        return self.parish

    def set_county(self,data):
        """sets the county name of the Location object"""
        self.county = data

    def get_county(self):
        """returns the county name of the Location object"""
        return self.county

    def set_state(self,data):
        """sets the state name of the Location object"""
        self.state = data

    def get_state(self):
        """returns the state name of the Location object"""
        return self.state

    def set_country(self,data):
        """sets the country name of the Location object"""
        self.country = data

    def get_country(self):
        """returns the country name of the Location object"""
        return self.country

class Note:
    """Provides general text information"""
    
    def __init__(self,text = ""):
        """create a new Note object from the passed string"""
        self.text = text
        self.format = 0

    def set(self,text):
        """set the note contents to the passed string"""
        self.text = text

    def get(self):
        """return the note contents"""
        return self.text

    def append(self,text):
        """adds the text to the note's contents"""
        self.text = self.text + text

    def set_format(self,format):
        """set the format to the passed value"""
        self.format = format

    def get_format(self):
        """return the note's format"""
        return self.format

class MediaRef(SourceNote):
    """Media reference class"""
    def __init__(self,source=None):

        SourceNote.__init__(self,source)

        self.attrlist = []
        if source:
            self.private = source.private
            self.ref = source.ref
            self.note = Note(source.note)
            for attr in source.attrlist:
                self.attrlist.append(Attribute(attr))
        else:
            self.private = 0
            self.ref = None
            self.note = None

    def set_privacy(self,val):
        """Sets or clears the privacy flag of the data"""
        self.private = val

    def get_privacy(self):
        """Returns the privacy level of the data"""
        return self.private

    def set_reference_handle(self,obj_id):
        self.ref = obj_id

    def get_reference_handle(self):
        return self.ref

    def add_attribute(self,attr):
        """Adds a propery to the MediaObject object. This is not used by gramps,
        but provides a means for XML users to attach other properties to
        the image"""
        self.attrlist.append(attr)

    def get_attribute_list(self):
        """returns the property list associated with the image"""
        return self.attrlist

    def set_attribute_list(self,list):
        """sets the property list associated with the image"""
        self.attrlist = list

class Attribute(DataObj):
    """Provides a simple key/value pair for describing properties. Used
    by the Person and Family objects to store descriptive information."""
    
    def __init__(self,source=None):
        """creates a new Attribute object, copying from the source if provided"""
        DataObj.__init__(self,source)
        
        if source:
            self.type = source.type
            self.value = source.value
        else:
            self.type = ""
            self.value = ""

    def set_type(self,val):
        """sets the type (or key) of the Attribute instance"""
        self.type = val

    def get_type(self):
        """returns the type (or key) or the Attribute instance"""
        return self.type

    def set_value(self,val):
        """sets the value of the Attribute instance"""
        self.value = val

    def get_value(self):
        """returns the value of the Attribute instance"""
        return self.value

class Address(DataObj):
    """Provides address information for a person"""

    def __init__(self,source=None):
        """Creates a new Address instance, copying from the source
        if provided"""
        DataObj.__init__(self,source)
        
        if source:
            self.street = source.street
            self.city = source.city
            self.state = source.state
            self.country = source.country
            self.postal = source.postal
            self.date = Date(source.date)
            self.phone = source.phone
        else:
            self.street = ""
            self.city = ""
            self.state = ""
            self.country = ""
            self.postal = ""
            self.date = Date()
            self.phone = ""

    def set_date(self,text):
        """attempts to sets the date that the person lived at the address
        from the passed string"""
        self.date.set(text)

    def get_date(self):
        """returns a string representation of the date that the person
        lived at the address"""
        return self.date.get_date()

    def get_preferred_date(self):
        """returns a string representation of the date that the person
        lived at the address"""
        return self.date.get_preferred_date()

    def get_date_object(self):
        """returns the Date object associated with the Address"""
        return self.date

    def set_date_object(self,obj):
        """sets the Date object associated with the Address"""
        self.date = obj

    def set_street(self,val):
        """sets the street portion of the Address"""
        self.street = val

    def get_street(self):
        """returns the street portion of the Address"""
        return self.street

    def set_phone(self,val):
        """sets the phone number portion of the Address"""
        self.phone = val

    def get_phone(self):
        """returns the phone number portion of the Address"""
        return self.phone

    def set_city(self,val):
        """sets the city portion of the Address"""
        self.city = val

    def get_city(self):
        """returns the city portion of the Address"""
        return self.city

    def set_state(self,val):
        """sets the state portion of the Address"""
        self.state = val

    def get_state(self):
        """returns the state portion of the Address"""
        return self.state

    def set_country(self,val):
        """sets the country portion of the Address"""
        self.country = val

    def get_country(self):
        """returns the country portion of the Address"""
        return self.country

    def set_postal_code(self,val):
        """sets the postal code of the Address"""
        self.postal = val

    def get_postal_code(self):
        """returns the postal code of the Address"""
        return self.postal

class Name(DataObj):
    """Provides name information about a person. A person may have more
    that one name throughout his or her life."""
    
    def __init__(self,source=None):
        """creates a new Name instance, copying from the source if provided"""
        DataObj.__init__(self,source)
        
        if source:
            self.first_name = source.first_name
            self.surname = source.surname
            self.suffix = source.suffix
            self.title = source.title
            self.type = source.type
            self.prefix = source.prefix
            self.sname = source.sname
        else:
            self.first_name = ""
            self.surname = ""
            self.suffix = ""
            self.title = ""
            self.type = "Birth Name"
            self.prefix = ""
            self.sname = '@'

    def get_surname_prefix(self):
        return self.prefix

    def set_surname_prefix(self,val):
        self.prefix = val

    def set_type(self,type):
        """sets the type of the Name instance"""
        self.type = type

    def get_type(self):
        """returns the type of the Name instance"""
        return self.type

    def build_sort_name(self):
        if self.surname:
            self.sname = accent.deaccent("%-25s%-30s%s" % (self.surname.upper(),self.first_name.upper(),self.suffix.upper()))
        else:
            self.sname = "@"

    def set_first_name(self,name):
        """sets the given name for the Name instance"""
        self.first_name = name
        self.build_sort_name()

    def set_surname(self,name):
        """sets the surname (or last name) for the Name instance"""
        self.surname = name
        self.build_sort_name()

    def set_suffix(self,name):
        """sets the suffix (such as Jr., III, etc.) for the Name instance"""
        self.suffix = name
        self.build_sort_name()

    def get_sort_name(self):
        return self.sname
    
    def get_first_name(self):
        """returns the given name for the Name instance"""
        return self.first_name

    def get_surname(self):
        """returns the surname (or last name) for the Name instance"""
        return self.surname

    def get_upper_surname(self):
        """returns the surname (or last name) for the Name instance"""
        return self.surname.upper()

    def get_suffix(self):
        """returns the suffix for the Name instance"""
        return self.suffix

    def set_title(self,title):
        """sets the title (Dr., Reverand, Captain) for the Name instance"""
        self.title = title

    def get_title(self):
        """returns the title for the Name instance"""
        return self.title

    def get_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of surname, Firstname"""
        
        if self.suffix:
            if self.prefix:
                return "%s %s, %s %s" % (self.prefix, self.surname, self.first_name, self.suffix)
            else:
                return "%s, %s %s" % (self.surname, self.first_name, self.suffix)
        else:
            if self.prefix:
                return "%s %s, %s" % (self.prefix,self.surname, self.first_name)
            else:
                return "%s, %s" % (self.surname, self.first_name)

    def get_upper_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of surname, Firstname"""
        
        if self.suffix:
            if self.prefix:
                return "%s %s, %s %s" % (self.prefix.upper(), self.surname.upper(), self.first_name, self.suffix)
            else:
                return "%s, %s %s" % (self.surname.upper(), self.first_name, self.suffix)
        else:
            if self.prefix:
                return "%s %s, %s" % (self.prefix.upper(), self.surname.upper(), self.first_name)
            else:
                return "%s, %s" % (self.surname.upper(), self.first_name)

    def get_regular_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of Firstname surname"""
        if (self.suffix == ""):
            if self.prefix:
                return "%s %s %s" % (self.first_name, self.prefix, self.surname)
            else:
                return "%s %s" % (self.first_name, self.surname)
        else:
            if self.prefix:
                return "%s %s %s, %s" % (self.first_name, self.prefix, self.surname, self.suffix)
            else:
                return "%s %s, %s" % (self.first_name, self.surname, self.suffix)

    def get_regular_upper_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of Firstname surname"""
        if (self.suffix == ""):
            if self.prefix:
                return "%s %s %s" % (self.first_name, self.prefix.upper(), self.surname.upper())
            else:
                return "%s %s" % (self.first_name, self.surname.upper())
        else:
            if self.prefix:
                return "%s %s %s, %s" % (self.first_name, self.prefix.upper(), self.surname.upper(), self.suffix)
            else:
                return "%s %s, %s" % (self.first_name, self.surname.upper(), self.suffix)

    def are_equal(self,other):
        """compares to names to see if they are equal, return 0 if they
        are not"""
        if self.first_name != other.first_name:
            return 0
        if self.surname != other.surname:
            return 0
        if self.prefix != other.prefix:
            return 0
        if self.suffix != other.suffix:
            return 0
        if self.title != other.title:
            return 0
        if self.type != other.type:
            return 0
        if self.private != other.private:
            return 0
        if self.get_note() != other.get_note():
            return 0
        if len(self.get_source_references()) != len(other.get_source_references()):
            return 0
        index = 0
        olist = other.get_source_references()
        for a in self.get_source_references():
            if not a.are_equal(olist[index]):
                return 0
            index = index + 1
        return 1

class Url:
    """Contains information related to internet Uniform Resource Locators,
    allowing gramps to store information about internet resources"""

    def __init__(self,source=None):
        """creates a new URL instance, copying from the source if present"""
        if source:
            self.path = source.path
            self.desc = source.desc
            self.private = source.private
        else:
            self.path = ""
            self.desc = ""
            self.private = 0

    def set_privacy(self,val):
        """sets the privacy flag for the URL instance"""
        self.private = val

    def get_privacy(self):
        """returns the privacy flag for the URL instance"""
        return self.private

    def set_path(self,path):
        """sets the URL path"""
        self.path = path

    def get_path(self):
        """returns the URL path"""
        return self.path

    def set_description(self,description):
        """sets the description of the URL"""
        self.desc = description

    def get_description(self):
        """returns the description of the URL"""
        return self.desc

    def are_equal(self,other):
        """returns 1 if the specified URL is the same as the instance"""
        if other == None:
            return 0
        if self.path != other.path:
            return 0
        if self.desc != other.desc:
            return 0
        return 1

class Witness:
    """
    The Witness class is used to represent a person who may or may
    not be in the database. If the person is in the database, the
    type will be Event.ID, and the value with be the database handle
    for the person. If the person is not in the database, the type
    will be Event.NAME, and the value will be a string representing
    the person's name.
    """
    def __init__(self,type=Event.NAME,val="",comment=""):
        self.set_type(type)
        self.set_value(val)
        self.set_comment(comment)

    def set_type(self,type):
        self.type = type

    def get_type(self):
        return self.type

    def set_value(self,val):
        self.val = val

    def get_value(self):
        return self.val

    def set_comment(self,comment):
        self.comment = comment

    def get_comment(self):
        return self.comment

class SourceRef:
    """Source reference, containing detailed information about how a
    referenced source relates to it"""
    
    def __init__(self,source=None):
        """creates a new SourceRef, copying from the source if present"""
        if source:
            self.confidence = source.confidence
            self.ref = source.ref
            self.page = source.page
            self.date = Date(source.date)
            self.comments = Note(source.comments.get())
            self.text = source.text
        else:
            self.confidence = CONF_NORMAL
            self.ref = None
            self.page = ""
            self.date = Date()
            self.comments = Note()
            self.text = ""

    def set_confidence_level(self,val):
        """Sets the confidence level"""
        self.confidence = val

    def get_confidence_level(self):
        """Returns the confidence level"""
        return self.confidence
        
    def set_base_handle(self,ref):
        """sets the Source instance to which the SourceRef refers"""
        self.ref = ref

    def get_base_handle(self):
        """returns the Source instance to which the SourceRef refers"""
        return self.ref
    
    def set_date(self,date):
        """sets the Date instance of the SourceRef"""
        self.date = date

    def get_date(self):
        """returns the Date instance of the SourceRef"""
        return self.date

    def set_page(self,page):
        """sets the page indicator of the SourceRef"""
        self.page = page

    def get_page(self):
        """gets the page indicator of the SourceRef"""
        return self.page

    def set_text(self,text):
        """sets the text related to the SourceRef"""
        self.text = text

    def get_text(self):
        """returns the text related to the SourceRef"""
        return self.text

    def set_note_object(self,note):
        """Change the Note instance to obj"""
        self.comments = note

    def set_comments(self,comments):
        """sets the comments about the SourceRef"""
        self.comments.set(comments)

    def get_comments(self):
        """returns the comments about the SourceRef"""
        return self.comments.get()

    def are_equal(self,other):
        """returns 1 if the passed SourceRef is equal to the current"""
        if self.ref and other.ref:
            if self.page != other.page:
                return 0
            if compare_dates(self.date,other.date) != 0:
                return 0
            if self.get_text() != other.get_text():
                return 0
            if self.get_comments() != other.get_comments():
                return 0
            if self.confidence != other.confidence:
                return 0
            return 1
        elif not self.ref and not other.ref:
            return 1
        else:
            return 0
        
    def unique_note(self):
        """Creates a unique instance of the current note"""
        self.comments = Note(self.comments.get())

class GenderStats:
    """
    Class for keeping track of statistics related to Given Name vs.
    Gender. This allows the tracking of the liklihood of a person's
    given name indicating the gender of the person.
    """
    def __init__ (self,stats={}):
        if stats == None:
            self.stats = {}
        else:
            self.stats = stats

    def save_stats(self):
        return self.stats

    def _get_key (self, person):
        name = person.get_primary_name().get_first_name()
        return self._get_key_from_name (name)

    def _get_key_from_name (self, name):
        return name.split (' ')[0].replace ('?', '')

    def name_stats (self, name):
        if self.stats.has_key (name):
            return self.stats[name]
        return (0, 0, 0)

    def count_person (self, person, db, undo = 0):
        # Let the Person do their own counting later
        person.db = db

        name = self._get_key (person)
        if not name:
            return

        gender = person.get_gender()
        (male, female, unknown) = self.name_stats (name)
        if not undo:
            increment = 1
        else:
            increment = -1

        if gender == Person.male:
            male += increment
        elif gender == Person.female:
            female += increment
        elif gender == Person.unknown:
            unknown += increment

        self.stats[name] = (male, female, unknown)
        return

    def uncount_person (self, person):
        return self.count_person (person, None, undo = 1)

    def guess_gender (self, name):
        name = self._get_key_from_name (name)
        if not name or not self.stats.has_key (name):
            return Person.unknown

        (male, female, unknown) = self.stats[name]
        if unknown == 0:
            if male and not female:
                return Person.male
            if female and not male:
                return Person.female

        if male > (2 * female):
            return Person.male

        if female > (2 * male):
            return Person.female

        return Person.unknown


