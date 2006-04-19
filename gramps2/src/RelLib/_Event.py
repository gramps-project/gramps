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
Event object for GRAMPS
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
from _DateBase import DateBase
from _PlaceBase import PlaceBase

#-------------------------------------------------------------------------
#
# Event class
#
#-------------------------------------------------------------------------
class Event(PrimaryObject,SourceBase,NoteBase,MediaBase,DateBase,PlaceBase):
    """
    Introduction
    ============
    The Event record is used to store information about some type of
    action that occurred at a particular place at a particular time,
    such as a birth, death, or marriage.
    """

    UNKNOWN        = -1
    CUSTOM         = 0
    MARRIAGE       = 1
    MARR_SETTL     = 2
    MARR_LIC       = 3
    MARR_CONTR     = 4
    MARR_BANNS     = 5
    ENGAGEMENT     = 6
    DIVORCE        = 7
    DIV_FILING     = 8
    ANNULMENT      = 9
    MARR_ALT       = 10
    ADOPT          = 11
    BIRTH          = 12
    DEATH          = 13
    ADULT_CHRISTEN = 14
    BAPTISM        = 15
    BAR_MITZVAH    = 16
    BAS_MITZVAH    = 17
    BLESS          = 18
    BURIAL         = 19
    CAUSE_DEATH    = 20
    CENSUS         = 21
    CHRISTEN       = 22
    CONFIRMATION   = 23
    CREMATION      = 24
    DEGREE         = 25
    EDUCATION      = 26
    ELECTED        = 27
    EMIGRATION     = 28
    FIRST_COMMUN   = 29
    IMMIGRATION    = 30
    GRADUATION     = 31
    MED_INFO       = 32
    MILITARY_SERV  = 33
    NATURALIZATION = 34
    NOB_TITLE      = 35
    NUM_MARRIAGES  = 36
    OCCUPATION     = 37
    ORDINATION     = 38
    PROBATE        = 39
    PROPERTY       = 40
    RELIGION       = 41
    RESIDENCE      = 42
    RETIREMENT     = 43
    WILL           = 44

    def __init__(self,source=None):
        """
        Creates a new Event instance, copying from the source if present

        @param source: An event used to initialize the new event
        @type source: Event
        """

        PrimaryObject.__init__(self,source)
        SourceBase.__init__(self,source)
        NoteBase.__init__(self,source)
        MediaBase.__init__(self,source)
        DateBase.__init__(self,source)
        PlaceBase.__init__(self,source)

        if source:
            self.description = source.description
            self.type = source.type
            self.cause = source.cause
            self.personal = source.personal
        else:
            self.description = ""
            self.type = (Event.CUSTOM,"")
            self.cause = ""
            self.personal = True

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
        return (self.handle, self.gramps_id, self.type,
                DateBase.serialize(self),
                self.description, self.place, self.cause,
                SourceBase.serialize(self),
                NoteBase.serialize(self),
                MediaBase.serialize(self),
                self.change, self.marker, self.private, self.personal)

    def unserialize(self,data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in an Event structure.

        @param data: tuple containing the persistent data associated the
            Person object
        @type data: tuple
        """
        (self.handle, self.gramps_id, self.type, date,
         self.description, self.place, self.cause,
         source_list, note, media_list,
         self.change, self.marker, self.private, self.personal) = data

        DateBase.unserialize(self,date)
        MediaBase.unserialize(self,media_list)
        SourceBase.unserialize(self,source_list)
        NoteBase.unserialize(self,note)        

    def _has_handle_reference(self,classname,handle):
        if classname == 'Place':
            return self.place == handle
        return False

    def _remove_handle_references(self,classname,handle_list):
        if classname == 'Place' and self.place in handle_list:
            self.place = ""

    def _replace_handle_reference(self,classname,old_handle,new_handle):
        if classname == 'Place' and self.place == old_handle:
            self.place = new_handle

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.description,self.type[1],self.cause,self.gramps_id]
        #return [self.description,self.type[1],self.cause,
        #        self.get_date(),self.gramps_id]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.media_list + self.source_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_sourcref_child_list(self):
        """
        Returns the list of child secondary objects that may refer sources.

        @return: Returns the list of child secondary child objects that may refer sources.
        @rtype: list
        """
        return self.media_list

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        ret = []
        if self.place:
            ret.append(('Place',self.place))
        return ret

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.media_list + self.source_list

    def is_empty(self):
        """
        Returns True if the Event is an empty object (no values set).

        @returns: True if the Event is empty
        @rtype: bool
        """
        date = self.get_date_object()
        place = self.get_place_handle()
        description = self.description
        cause = self.cause
        the_type = self.type
        return (the_type == (Event.CUSTOM,"") and date.is_empty()
                and not place and not description and not cause) 

    def are_equal(self,other):
        """
        Returns True if the passed Event is equivalent to the current Event.

        @param other: Event to compare against
        @type other: Event
        @returns: True if the Events are equal
        @rtype: bool
        """
        if other == None:
            other = Event (None)

        if self.type[0] != other.type[0] or \
           (self.type[0] == Event.CUSTOM and self.type[1] != other.type[1]) or\
           ((self.place or other.place) and (self.place != other.place)) or \
           self.description != other.description or self.cause != other.cause \
           or self.private != other.private or \
           (not self.get_date_object().is_equal(other.get_date_object())) or \
           len(self.get_source_references()) != len(other.get_source_references()):
            return False

        index = 0
        olist = other.get_source_references()
        for a in self.get_source_references():
            if not a.are_equal(olist[index]):
                return False
            index += 1

        return True
        
    def set_name(self,name):
        warn( "Use set_type instead of set_name", DeprecationWarning, 2)
        # INCOMPLETE Wrapper for old API
        # remove when transitition done.
        if name in range(-1,45):
            the_type = (name,'')
        else:
            the_type = (Event.CUSTOM,name)
        self.set_type(the_type)

    def get_name(self):
        warn( "Use get_type instead of get_name", DeprecationWarning, 2)
        # INCOMPLETE Wrapper for old API
        # remove when transitition done.
        type = self.get_type()
        return type[1]
        
    def set_type(self,the_type):
        """
        Sets the type of the Event to the passed (int,str) tuple.

        @param the_type: Type to assign to the Event
        @type the_type: tuple
        """
        if not type(the_type) == tuple:
            warn( "set_type now takes a tuple", DeprecationWarning, 2)
            # Wrapper for old API
            # remove when transitition done.
            if the_type in range(-1,45):
                the_type = (the_type,'')
            else:
                the_type = (Event.CUSTOM,the_type)
        assert(type(the_type[0]) == int)
        assert(type(the_type[1]) == unicode or type(the_type[1]) == str)
        self.type = the_type

    def get_type(self):
        """
        Returns the type of the Event.

        @return: Type of the Event
        @rtype: tuple
        """
        return self.type

    def set_cause(self,cause):
        """
        Sets the cause of the Event to the passed string. The string
        may contain any information.

        @param cause: Cause to assign to the Event
        @type cause: str
        """
        self.cause = cause

    def get_cause(self):
        """
        Returns the cause of the Event.

        @return: Returns the cause of the Event
        @rtype: str
        """
        return self.cause 

    def set_description(self,description):
        """
        Sets the description of the Event to the passed string. The string
        may contain any information.

        @param description: Description to assign to the Event
        @type description: str
        """
        self.description = description

    def get_description(self) :
        """
        Returns the description of the Event.

        @return: Returns the description of the Event
        @rtype: str
        """
        return self.description
