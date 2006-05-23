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
Person object for GRAMPS
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from warnings import warn

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _PrimaryObject import PrimaryObject
from _SourceBase import SourceBase
from _NoteBase import NoteBase
from _MediaBase import MediaBase
from _AttributeBase import AttributeBase
from _AddressBase import AddressBase
from _LdsOrdBase import LdsOrdBase
from _UrlBase import UrlBase
from _Name import Name
from _EventRef import EventRef
from _LdsOrd import LdsOrd
from _PersonRef import PersonRef
from _MarkerType import MarkerType
from _AttributeType import AttributeType

#-------------------------------------------------------------------------
#
# Person class
#
#-------------------------------------------------------------------------
class Person(PrimaryObject,SourceBase,NoteBase,MediaBase,
             AttributeBase,AddressBase,UrlBase,LdsOrdBase):
    """
    Introduction
    ============
    The Person record is the GRAMPS in-memory representation of an
    individual person. It contains all the information related to
    an individual.
    
    Usage
    =====
    Person objects are usually created in one of two ways.

      1. Creating a new person object, which is then initialized and
         added to the database.
      2. Retrieving an object from the database using the records
         handle.

    Once a Person object has been modified, it must be committed
    to the database using the database object's commit_person function, 
    or the changes will be lost.

    @sort: serialize, unserialize, get_*, set_*, add_*, remove_*
    """
    
    UNKNOWN = 2
    MALE    = 1
    FEMALE  = 0
    
    def __init__(self, data=None):
        """
        Creates a new Person instance. After initialization, most
        data items have empty or null values, including the database
        handle.
        """
        PrimaryObject.__init__(self)
        SourceBase.__init__(self)
        NoteBase.__init__(self)
        MediaBase.__init__(self)
        AttributeBase.__init__(self)
        AddressBase.__init__(self)
        UrlBase.__init__(self)
        LdsOrdBase.__init__(self)
        self.primary_name = Name()
        self.event_ref_list = []
        self.family_list = []
        self.parent_family_list = []
        self.alternate_names = []
        self.person_ref_list = []
        self.gender = Person.UNKNOWN
        self.death_ref_index = -1
        self.birth_ref_index = -1

        if data:
            self.unserialize(data)
        
        # We hold a reference to the GrampsDB so that we can maintain
        # its genderStats.  It doesn't get set here, but from
        # GenderStats.count_person.
        
    def serialize(self):
        """
        Converts the data held in the Person to a Python tuple that
        represents all the data elements. This method is used to convert
        the object into a form that can easily be saved to a database.

        These elements may be primative Python types (string, integers), 
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objectes or
        lists), the database is responsible for converting the data into
        a form that it can use.

        @returns: Returns a python tuple containing the data that should
            be considered persistent.
        @rtype: tuple
        """
        return (
            self.handle,                                         #  0
            self.gramps_id,                                      #  1
            self.gender,                                         #  2
            self.primary_name.serialize(),                       #  3
            [name.serialize() for name in self.alternate_names], #  4
            self.death_ref_index,                                #  5
            self.birth_ref_index,                                #  6
            [er.serialize() for er in self.event_ref_list],      #  7
            self.family_list,                                    #  8
            self.parent_family_list,                             #  9
            MediaBase.serialize(self),                           # 10
            AddressBase.serialize(self),                         # 11
            AttributeBase.serialize(self),                       # 12
            UrlBase.serialize(self),                             # 13
            LdsOrdBase.serialize(self),                          # 14
            SourceBase.serialize(self),                          # 15
            NoteBase.serialize(self),                            # 16
            self.change,                                         # 17
            self.marker.serialize(),                             # 18
            self.private,                                        # 19
            [pr.serialize() for pr in self.person_ref_list]      # 20
            )

    def unserialize(self, data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in a Person object.

        @param data: tuple containing the persistent data associated the
            Person object
        @type data: tuple
        """
        (
            self.handle,             #  0
            self.gramps_id,          #  1
            self.gender,             #  2
            primary_name,            #  3
            alternate_names,         #  4
            self.death_ref_index,    #  5
            self.birth_ref_index,    #  6
            event_ref_list,          #  7
            self.family_list,        #  8
            self.parent_family_list, #  9
            media_list,              # 10
            address_list,            # 11
            attribute_list,          # 12
            urls,                    # 13
            lds_ord_list,            # 14
            source_list,             # 15
            note,                    # 16
            self.change,             # 17
            marker,                  # 18
            self.private,            # 19
            person_ref_list,         # 20
            ) = data

        self.marker.unserialize(marker)
        self.primary_name.unserialize(primary_name)
        self.alternate_names = [Name().unserialize(name)
                                for name in alternate_names]
        self.event_ref_list = [EventRef().unserialize(er)
                               for er in event_ref_list]
        self.person_ref_list = [PersonRef().unserialize(pr)
                                for pr in person_ref_list]
        MediaBase.unserialize(self, media_list)
        LdsOrdBase.unserialize(self, lds_ord_list)
        AddressBase.unserialize(self, address_list)
        AttributeBase.unserialize(self, attribute_list)
        UrlBase.unserialize(self, urls)
        SourceBase.unserialize(self, source_list)
        NoteBase.unserialize(self, note)
            
    def _has_handle_reference(self, classname, handle):
        if classname == 'Event':
            return handle in [ref.ref for ref in self.event_ref_list]
        elif classname == 'Person':
            return handle in [ref.ref for ref in self.person_ref_list]
        elif classname == 'Family':
            return handle in (self.family_list + self.parent_family_list)
        elif classname == 'Place':
            return handle in [ordinance.place for ordinance
                              in self.lds_ord_list]
        return False

    def _remove_handle_references(self, classname, handle_list):
        if classname == 'Event':
            new_list = [ref for ref in self.event_ref_list
                        if ref.ref not in handle_list]
            # If deleting removing the reference to the event
            # to which birth or death ref_index points, unset the index
            if (self.birth_ref_index != -1) \
                   and (self.event_ref_list[self.birth_ref_index]
                        in handle_list):
                self.birth_ref_index = -1
            if (self.death_ref_index != -1) \
                   and (self.event_ref_list[self.death_ref_index]
                        in handle_list):
                self.death_ref_index = -1
            self.event_ref_list = new_list
        elif classname == 'Person':
            new_list = [ref for ref in self.person_ref_list
                        if ref not in handle_list]
            self.person_ref_list = new_list
        elif classname == 'Family':
            new_list = [ handle for handle in self.family_list
                         if handle not in handle_list ]
            self.family_list = new_list
            new_list = [ handle for handle in self.parent_family_list \
                                        if handle not in handle_list ]
            self.parent_family_list = new_list
        elif classname == 'Place':
            new_list = [ordinance for ordinance in self.lds_ord_list
                        if ordinance.place not in handle_list]
            self.lds_ord_list = new_list

    def _replace_handle_reference(self, classname, old_handle, new_handle):
        if classname == 'Event':
            handle_list = [ref.ref for ref in self.event_ref_list]
            while old_handle in handle_list:
                ix = handle_list.index(old_handle)
                self.event_ref_list[ix].ref = new_handle
                handle_list[ix] = ''
        elif classname == 'Person':
            handle_list = [ref.ref for ref in self.person_ref_list]
            while old_handle in handle_list:
                ix = handle_list.index(old_handle)
                self.person_ref_list[ix].ref = new_handle
                handle_list[ix] = ''
        elif classname == 'Family':
            while old_handle in self.family_list:
                ix = self.family_list.index(old_handle)
                self.family_list[ix] = new_handle

            while old_handle in self.parent_family_list:
                ix = self.parent_family_list.index(old_handle)
                self.parent_family_list[ix] = new_handle
        elif classname == 'Place':
            handle_list = [ordinance.place for ordinance in self.lds_ord_list]
            while old_handle in handle_list:
                ix = handle_list.index(old_handle)
                self.lds_ord_list[ix].place = new_handle
                handle_list[ix] = ''

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.gramps_id]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.lds_ord_list + [self.note]
        add_list = [item for item in check_list if item]
        return [self.primary_name] + self.media_list + \
                    self.alternate_names + self.address_list + \
                    self.attribute_list + self.urls + \
                    self.source_list + self.event_ref_list + add_list + \
                    self.person_ref_list

    def get_sourcref_child_list(self):
        """
        Returns the list of child secondary objects that may refer sources.

        @return: Returns the list of child secondary child objects that may refer sources.
        @rtype: list
        """
        return [self.primary_name] + self.media_list + \
                    self.alternate_names + self.address_list + \
                    self.attribute_list + self.lds_ord_list

    def get_referenced_handles(self):
        """
        Returns the list of (classname, handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname, handle) tuples for referenced objects.
        @rtype: list
        """
        return [('Family', handle) for handle in
                (self.family_list + self.parent_family_list)]

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.get_sourcref_child_list() + self.source_list \
               + self.event_ref_list

    def get_complete_flag(self):
        warn( "Use get_marker instead of get_complete_flag",
              DeprecationWarning, 2)
        # Wrapper for old API
        # remove when transitition done.
        return self.marker == MarkerType.COMPLETE

    def set_primary_name(self, name):
        """
        Sets the primary name of the Person to the specified
        L{Name} instance

        @param name: L{Name} to be assigned to the person
        @type name: L{Name}
        """
        self.primary_name = name

    def get_primary_name(self):
        """
        Returns the L{Name} instance marked as the Person's primary name

        @return: Returns the primary name
        @rtype: L{Name}
        """
        return self.primary_name

    def get_alternate_names(self):
        """
        Returns the list of alternate L{Name} instances

        @return: List of L{Name} instances
        @rtype: list
        """
        return self.alternate_names

    def set_alternate_names(self, alt_name_list):
        """
        Changes the list of alternate names to the passed list. 
        @param alt_name_list: List of L{Name} instances
        @type alt_name_list: list
        """
        self.alternate_names = alt_name_list

    def add_alternate_name(self, name):
        """
        Adds a L{Name} instance to the list of alternative names

        @param name: L{Name} to add to the list
        @type name: L{Name}
        """
        self.alternate_names.append(name)

    def get_nick_name(self):
        nicks = [ attr for attr in self.attribute_list \
                  if int(attr.type) == AttributeType.NICKNAME ]
        if len(nicks) == 0:
            return u''
        else:
            return nicks[0].get_value()

    def set_gender(self, gender) :
        """
        Sets the gender of the Person.

        @param gender: Assigns the Person's gender to one of the
            following constants::
                Person.MALE
                Person.FEMALE
                Person.UNKNOWN
        @type gender: int
        """
        self.gender = gender

    def get_gender(self) :
        """
        Returns the gender of the Person

        @returns: Returns one of the following constants::
            Person.MALE
            Person.FEMALE
            Person.UNKNOWN
        @rtype: int
        """
        return self.gender

    def set_birth_ref(self, event_ref):
        """
        Assigns the birth event to the Person object. This is accomplished
        by assigning the L{EventRef} of the birth event in the current
        database.

        @param event_ref: the L{EventRef} object associated with
            the Person's birth.
        @type event_handle: EventRef
        """
        if event_ref and not isinstance(event_ref, EventRef):
            raise ValueError("Expecting EventRef instance")

        # check whether we already have this ref in the list
        matches = [event_ref.is_equal(ref) for ref in self.event_ref_list]
        try:
            self.birth_ref_index = matches.index(True)
        except ValueError:
            self.event_ref_list.append(event_ref)
            self.birth_ref_index = len(self.event_ref_list)-1

    def set_death_ref(self, event_ref):
        """
        Assigns the death event to the Person object. This is accomplished
        by assigning the L{EventRef} of the death event in the current
        database.

        @param event_ref: the L{EventRef} object associated with
            the Person's death.
        @type event_handle: EventRef
        """
        if event_ref and not isinstance(event_ref, EventRef):
            raise ValueError("Expecting EventRef instance")
        # check whether we already have this ref in the list
        matches = [event_ref.is_equal(ref) for ref in self.event_ref_list]
        try:
            self.death_ref_index = matches.index(True)
        except ValueError:
            self.event_ref_list.append(event_ref)
            self.death_ref_index = len(self.event_ref_list)-1

    def get_birth_ref(self):
        """
        Returns the L{EventRef} for Person's birth event. This
        should correspond to an L{Event} in the database's L{Event} list.

        @returns: Returns the birth L{EventRef} or None if no birth
            L{Event} has been assigned.
        @rtype: EventRef
        """
        if self.birth_ref_index == -1:
            return None
        else:
            try:
                return self.event_ref_list[self.birth_ref_index]
            except IndexError:
                return None

    def get_death_ref(self):
        """
        Returns the L{EventRef} for the Person's death event. This
        should correspond to an L{Event} in the database's L{Event} list.

        @returns: Returns the death L{EventRef} or None if no death
            L{Event} has been assigned.
        @rtype: event_ref
        """
        if self.death_ref_index == -1:
            return None
        else:
            try:
                return self.event_ref_list[self.death_ref_index]
            except IndexError:
                return None

    def add_event_ref(self, event_ref):
        """
        Adds the L{EventRef} to the Person instance's L{EventRef} list.
        This is accomplished by assigning the L{EventRef} of a valid
        L{Event} in the current database.
        
        @param event_ref: the L{EventRef} to be added to the
            Person's L{EventRef} list.
        @type event_ref: EventRef
        """
        if event_ref and not isinstance(event_ref, EventRef):
            raise ValueError("Expecting EventRef instance")
        # check whether we already have this ref in the list
        matches = [event_ref.is_equal(ref) for ref in self.event_ref_list]
        if matches.count(True) == 0:
            self.event_ref_list.append(event_ref)

    def get_event_ref_list(self):
        """
        Returns the list of L{EventRef} objects associated with L{Event}
        instances.

        @returns: Returns the list of L{EventRef} objects associated with
            the Person instance.
        @rtype: list
        """
        return self.event_ref_list

    def set_event_ref_list(self, event_ref_list):
        """
        Sets the Person instance's L{EventRef} list to the passed list.

        @param event_ref_list: List of valid L{EventRef} objects
        @type event_ref_list: list
        """
        self.event_ref_list = event_ref_list

    def add_family_handle(self, family_handle):
        """
        Adds the L{Family} handle to the Person instance's L{Family} list.
        This is accomplished by assigning the handle of a valid L{Family}
        in the current database.

        Adding a L{Family} handle to a Person does not automatically update
        the corresponding L{Family}. The developer is responsible to make
        sure that when a L{Family} is added to Person, that the Person is
        assigned to either the father or mother role in the L{Family}.
        
        @param family_handle: handle of the L{Family} to be added to the
            Person's L{Family} list.
        @type family_handle: str
        """
        if family_handle not in self.family_list:
            self.family_list.append(family_handle)

    def set_preferred_family_handle(self, family_handle):
        """
        Sets the family_handle specified to be the preferred L{Family}.
        The preferred L{Family} is determined by the first L{Family} in the
        L{Family} list, and is typically used to indicate the preferred
        L{Family} for navigation or reporting.
        
        The family_handle must already be in the list, or the function
        call has no effect.

        @param family_handle: Handle of the L{Family} to make the preferred
            L{Family}.
        @type family_handle: str
        @returns: True if the call succeeded, False if the family_handle
            was not already in the L{Family} list
        @rtype: bool
        """
        if family_handle in self.family_list:
            self.family_list.remove(family_handle)
            self.family_list = [family_handle] + self.family_list
            return True
        else:
            return False

    def get_family_handle_list(self) :
        """
        Returns the list of L{Family} handles in which the person is a
        parent or spouse.

        @return: Returns the list of handles corresponding to the
        L{Family} records with which the person is associated.
        @rtype: list
        """
        return self.family_list

    def set_family_handle_list(self, family_list) :
        """
        Assigns the passed list to the Person's list of families in
        which it is a parent or spouse.

        @param family_list: List of L{Family} handles to ba associated
            with the Person
        @type family_list: list 
        """
        self.family_list = family_list

    def clear_family_handle_list(self):
        """
        Removes all L{Family} handles from the L{Family} list.
        """
        self.family_list = []

    def remove_family_handle(self, family_handle):
        """
        Removes the specified L{Family} handle from the list
        of marriages/partnerships. If the handle does not
        exist in the list, the operation has no effect.

        @param family_handle: L{Family} handle to remove from the list
        @type family_handle: str

        @return: True if the handle was removed, False if it was not
            in the list.
        @rtype: bool
        """
        if family_handle in self.family_list:
            self.family_list.remove(family_handle)
            return True
        else:
            return False

    def get_parent_family_handle_list(self):
        """
        Returns the list of L{Family} handles in which the person is a
        child.

        @return: Returns the list of handles corresponding to the
        L{Family} records with which the person is a child.
        @rtype: list
        """
        return self.parent_family_list

    def add_parent_family_handle(self, family_handle):
        """
        Adds the L{Family} handle to the Person instance's list of
        families in which it is a child. This is accomplished by
        assigning the handle of a valid L{Family} in the current database.

        Adding a L{Family} handle to a Person does not automatically update
        the corresponding L{Family}. The developer is responsible to make
        sure that when a L{Family} is added to Person, that the Person is
        added to the L{Family} instance's child list.
        
        @param family_handle: handle of the L{Family} to be added to the
            Person's L{Family} list.
        @type family_handle: str
        """
        if type(family_handle) not in (str ,unicode ):
            raise ValueError("expecting handle")
        if family_handle not in self.parent_family_list:
            self.parent_family_list.append(family_handle)

    def clear_parent_family_handle_list(self):
        """
        Removes all L{Family} handles from the parent L{Family} list.
        """
        self.parent_family_list = []

    def remove_parent_family_handle(self, family_handle):
        """
        Removes the specified L{Family} handle from the list of parent
        families (families in which the parent is a child). If the
        handle does not exist in the list, the operation has no effect.

        @param family_handle: L{Family} handle to remove from the list
        @type family_handle: str

        @return: Returns a tuple of three strings, consisting of the
            removed handle, relationship to mother, and relationship
            to father. None is returned if the handle is not in the
            list.
        @rtype: tuple
        """
        if family_handle in self.parent_family_list:
            self.parent_family_list.remove(family_handle)
            return True
        else:
            return False

    def set_main_parent_family_handle(self, family_handle):
        """
        Sets the main L{Family} in which the Person is a child. The
        main L{Family} is the L{Family} typically used for reports and
        navigation. This is accomplished by moving the L{Family} to
        the beginning of the list. The family_handle must be in
        the list for this to have any effect.

        @param family_handle: handle of the L{Family} to be marked
            as the main L{Family}
        @type family_handle: str
        @return: Returns True if the assignment has successful
        @rtype: bool
        """
        if family_handle in self.parent_family_list:
            self.parent_family_list.remove(family_handle)
            self.parent_family_list = [family_handle] + self.parent_family_list
            return True
        else:
            return False
        
    def get_main_parents_family_handle(self):
        """
        Returns the handle of the L{Family} considered to be the main
        L{Family} in which the Person is a child.

        @return: Returns the family_handle if a family_handle exists, 
            If no L{Family} is assigned, None is returned
        @rtype: str
        """
        if len(self.parent_family_list) == 0:
            return None
        else:
            return self.parent_family_list[0]

    def add_person_ref(self,person_ref):
        """
        Adds the L{PersonRef} to the Person instance's L{PersonRef} list.
        
        @param person_ref: the L{PersonRef} to be added to the
            Person's L{PersonRef} list.
        @type person_ref: PersonRef
        """
        if person_ref and not isinstance(person_ref, PersonRef):
            raise ValueError("Expecting PersonRef instance")
        self.person_ref_list.append(person_ref)

    def get_person_ref_list(self):
        """
        Returns the list of L{PersonRef} objects.

        @returns: Returns the list of L{PersonRef} objects.
        @rtype: list
        """
        return self.person_ref_list

    def set_person_ref_list(self, person_ref_list):
        """
        Sets the Person instance's L{PersonRef} list to the passed list.

        @param event_ref_list: List of valid L{PersonRef} objects
        @type event_ref_list: list
        """
        self.person_ref_list = person_ref_list
