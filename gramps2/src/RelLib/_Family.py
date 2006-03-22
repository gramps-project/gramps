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
Family object for GRAMPS
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
from _SourceNote import SourceNote
from _MediaBase import MediaBase
from _AttributeBase import AttributeBase
from _EventRef import EventRef

#-------------------------------------------------------------------------
#
# Family class
#
#-------------------------------------------------------------------------
class Family(PrimaryObject,SourceNote,MediaBase,AttributeBase):
    """
    Introduction
    ============
    The Family record is the GRAMPS in-memory representation of the
    relationships between people. It contains all the information
    related to the relationship.
    
    Usage
    =====
    Family objects are usually created in one of two ways.

      1. Creating a new Family object, which is then initialized and
         added to the database.
      2. Retrieving an object from the database using the records
         handle.

    Once a Family object has been modified, it must be committed
    to the database using the database object's commit_family function,
    or the changes will be lost.
    """

    MARRIED     = 0
    UNMARRIED   = 1
    CIVIL_UNION = 2
    UNKNOWN     = 3
    CUSTOM      = 4

    def __init__(self):
        """
        Creates a new Family instance. After initialization, most
        data items have empty or null values, including the database
        handle.
        """
        PrimaryObject.__init__(self)
        SourceNote.__init__(self)
        MediaBase.__init__(self)
        AttributeBase.__init__(self)
        self.father_handle = None
        self.mother_handle = None
        self.child_list = []
        self.type = (Family.MARRIED,'')
        self.event_ref_list = []
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

        @returns: Returns a python tuple containing the data that should
            be considered persistent.
        @rtype: tuple
        """
        if self.lds_seal == None:
            lds_seal = None
        else:
            lds_seal = self.lds_seal.serialize()
        return (self.handle, self.gramps_id, self.father_handle,
                self.mother_handle,self.child_list, self.type,
                [er.serialize() for er in self.event_ref_list],
                MediaBase.serialize(self),
                AttributeBase.serialize(self),
                lds_seal,SourceNote.serialize(self),
                self.change, self.marker, self.private)

    def unserialize(self, data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in a Family structure.
        """
        (self.handle, self.gramps_id, self.father_handle, self.mother_handle,
         self.child_list, self.type,
         event_ref_list, media_list, attribute_list, lds_seal, sn,
         self.change,self.marker, self.private) = data

        self.event_ref_list = [EventRef().unserialize(er)
                               for er in event_ref_list]
        MediaBase.unserialize(self,media_list)
        AttributeBase.unserialize(self,attribute_list)
        SourceNote.unserialize(self,sn)

    def _has_handle_reference(self,classname,handle):
        if classname == 'Event':
            return handle in [ref.ref for ref in self.event_ref_list]
        elif classname == 'Person':
            return handle in self.child_list + [self.father_handle,self.mother_handle]
        elif classname == 'Place':
            return bool(self.lds_seal) and self.lds_seal.place == handle
        return False

    def _remove_handle_references(self,classname,handle_list):
        if classname == 'Event':
            new_list = [ ref for ref in self.event_ref_list \
                                        if ref.ref not in handle_list ]
            self.event_ref_list = new_list
        elif classname == 'Person':
            new_list = [ handle for handle in self.child_list \
                                        if handle not in handle_list ]
            self.child_list = new_list
            if self.father_handle in handle_list:
                self.father_handle = None
            if self.mother_handle in handle_list:
                self.mother_handle = None
        elif classname == 'Place':
            if self.lds_seal and self.lds_seal.place in handle_list:
                self.lds_seal.place = None

    def _replace_handle_reference(self,classname,old_handle,new_handle):
        if classname == 'Event':
            handle_list = [ref.ref for ref in self.event_ref_list]
            while old_handle in handle_list:
                ix = handle_list(old_handle)
                self.event_ref_list[ix].ref = new_handle
                handle_list[ix] = ''
        elif classname == 'Person':
            while old_handle in self.child_list:
                ix = self.child_list.index(old_handle)
                self.child_list[ix] = new_handle
            if self.father_handle == old_handle:
                self.father_handle = new_handle
            if self.mother_handle == old_handle:
                self.mother_handle = new_handle
        elif classname == 'Place':
            if self.lds_seal and self.lds_seal.place == old_handle:
                self.lds_seal.place = new_handle

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
        check_list = [self.lds_seal,self.note]
        add_list = [item for item in check_list if item]
        return self.media_list + self.attribute_list + \
                self.source_list + add_list

    def get_sourcref_child_list(self):
        """
        Returns the list of child secondary objects that may refer sources.

        @return: Returns the list of child secondary child objects that may refer sources.
        @rtype: list
        """
        check_list = self.media_list + self.attribute_list
        if self.lds_seal:
            check_list.append(self.lds_seal)
        return check_list

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        ret = []
        ret += [('Event',ref.ref) for ref in self.event_ref_list]
        ret += [('Person',handle) for handle in 
                    self.child_list + [self.father_handle,self.mother_handle]
                    if handle]
        return ret

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.get_sourcref_child_list() + self.source_list

    def set_complete_flag(self,val):
        """
        Sets or clears the complete flag, which is used to indicate that the
        Family's data is considered to be complete.

        @param val: True indicates the Family object is considered to be
            complete
        @type val: bool
        """
        self.complete = val

    def get_complete_flag(self):
        """
        Returns the complete flag, which is used to indicate that the
        Family's data is considered to be complete.

        @return: True indicates that the Family's record is considered to
            be complete.
        @rtype: bool
        """
        return self.complete

    def set_lds_sealing(self,lds_ord):
        """
        Sets the LDS Sealing ordinance. An ordinance can be removed
        by assigning to None.

        @param lds_ord: L{LdsOrd} to assign as the LDS Sealing ordinance.
        @type lds_ord: L{LdsOrd}
        """
        self.lds_seal = lds_ord

    def get_lds_sealing(self):
        """
        Returns the LDS Sealing ordinance.

        @returns: returns the L{LdsOrd} instance assigned as the LDS
        Sealing ordinance, or None if no ordinance has been assigned.
        @rtype: L{LdsOrd}
        """
        return self.lds_seal

    def set_relationship(self,relationship_type):
        """
        Sets the relationship type between the people identified as the
        father and mother in the relationship. The type is a tuple whose
        first item is an integer constant and whose second item is
        the string. The valid values are:

            - C{Family.MARRIED} : indicates a legally recognized married
                relationship between two individuals. This may be either
                an opposite or a same sex relationship.
            - C{Family.UNMARRIED} : indicates a relationship between two
                individuals that is not a legally recognized relationship.
            - C{Family.CIVIL_UNION} : indicates a legally recongnized,
                non-married relationship between two individuals of the
                same sex.
            - C{Family.UNKNOWN} : indicates that the type of relationship
                between the two individuals is not know.
            - C{Family.CUSTOM} : indicates that the type of relationship
                between the two individuals does not match any of the
                other types.

        @param relationship_type: (int,str) tuple of the relationship type
            between the father and mother of the relationship.
        @type relationship_type: tuple
        """
        if not type(relationship_type) == tuple:
            if relationship_type in [Family.MARRIED,Family.UNMARRIED,
                                     Family.CIVIL_UNION,Family.UNKNOWN,
                                     Family.CUSTOM]:
                warn( "set_relationship now takes a tuple",
                      DeprecationWarning, 2)
                # Wrapper for old API
                # remove when transitition done.
                relationship_type = (relationship_type,'')
            else:
                assert type(relationship_type) == tuple
        self.type = relationship_type

    def get_relationship(self):
        """
        Returns the relationship type between the people identified as the
        father and mother in the relationship.
        """
        return self.type
    
    def set_father_handle(self,person_handle):
        """
        Sets the database handle for L{Person} that corresponds to
        male of the relationship. For a same sex relationship, this
        can represent either of people involved in the relationship.

        @param person_handle: L{Person} database handle
        @type person_handle: str
        """
        self.father_handle = person_handle

    def get_father_handle(self):
        """
        Returns the database handle of the L{Person} identified as
        the father of the Family.

        @returns: L{Person} database handle
        @rtype: str
        """
        return self.father_handle

    def set_mother_handle(self,person_handle):
        """
        Sets the database handle for L{Person} that corresponds to
        male of the relationship. For a same sex relationship, this
        can represent either of people involved in the relationship.

        @param person_handle: L{Person} database handle
        @type person_handle: str
        """
        self.mother_handle = person_handle

    def get_mother_handle(self):
        """
        Returns the database handle of the L{Person} identified as
        the mother of the Family.

        @returns: L{Person} database handle
        @rtype: str
        """
        return self.mother_handle

    def add_child_handle(self,person_handle):
        """
        Adds the database handle for L{Person} to the Family's list
        of children.

        @param person_handle: L{Person} database handle
        @type person_handle: str
        """
        if person_handle not in self.child_list:
            self.child_list.append(person_handle)
            
    def remove_child_handle(self,person_handle):
        """
        Removes the database handle for L{Person} to the Family's list
        of children if the L{Person} is already in the list.

        @param person_handle: L{Person} database handle
        @type person_handle: str
        @return: True if the handle was removed, False if it was not
            in the list.
        @rtype: bool
        """
        if person_handle in self.child_list:
            self.child_list.remove(person_handle)
            return True
        else:
            return False

    def get_child_handle_list(self):
        """
        Returns the list of L{Person} handles identifying the children
        of the Family.

        @return: Returns the list of L{Person} handles assocated with
            the Family.
        @rtype: list
        """
        return self.child_list

    def set_child_handle_list(self, child_list):
        """
        Assigns the passed list to the Family's list children.

        @param child_list: List of L{Person} handles to ba associated
            as the Family's list of children.
        @type child_list: list of L{Person} handles
        """
        self.child_list = child_list

    def add_event_handle(self,event_handle):
        warn( "Use add_event_ref instead of add_event_handle", DeprecationWarning, 2)
        # Wrapper for old API
        # remove when transitition done.
        event_ref = EventRef()
        event_ref.set_reference_handle(event_handle)
        event_ref.set_role((EventRef.PRIMARY,''))
        self.add_event_ref(event_ref)

    def add_event_ref(self,event_ref):
        """
        Adds the L{EventRef} to the Family instance's L{EventRef} list.
        This is accomplished by assigning the L{EventRef} for the valid
        L{Event}in the current database.
        
        @param event_ref: the L{EventRef} to be added to the
            Person's L{EventRef} list.
        @type event_ref: EventRef
        """
        if event_ref and not isinstance(event_ref,EventRef):
            raise ValueError("Expecting EventRef instance")
        self.event_ref_list.append(event_ref)

    def get_event_list(self) :
        warn( "Use get_event_ref_list instead of get_event_list", DeprecationWarning, 2)
        # Wrapper for old API
        # remove when transitition done.
        event_handle_list = []
        for event_ref in self.get_event_ref_list():
            event_handle_list.append( event_ref.get_reference_handle())
        return event_handle_list

    def get_event_ref_list(self) :
        """
        Returns the list of L{EventRef} objects associated with L{Event}
        instances.

        @returns: Returns the list of L{EventRef} objects associated with
            the Family instance.
        @rtype: list
        """
        return self.event_ref_list

    def set_event_list(self,event_list) :
        warn( "Use set_event_ref_list instead of set_event_list", DeprecationWarning, 2)
        # Wrapper for old API
        # remove when transitition done.
        event_ref_list = []
        for event_handle in event_list:
            event_ref = EventRef()
            event_ref.set_reference_handle(event_handle)
            event_ref.set_role((EventRef.PRIMARY,''))
            event_ref_list.append( event_ref)
        self.set_event_ref_list(event_ref_list)

    def set_event_ref_list(self,event_ref_list) :
        """
        Sets the Family instance's L{EventRef} list to the passed list.

        @param event_ref_list: List of valid L{EventRef} objects
        @type event_ref_list: list
        """
        self.event_ref_list = event_ref_list
