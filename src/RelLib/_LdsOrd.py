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
LDS Ordinance class for GRAMPS
"""

from warnings import warn

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _SecondaryObject import SecondaryObject
from _SourceBase import SourceBase
from _NoteBase import NoteBase
from _DateBase import DateBase
from _PlaceBase import PlaceBase
from _PrivacyBase import PrivacyBase

#-------------------------------------------------------------------------
#
# LDS Ordinance class
#
#-------------------------------------------------------------------------
class LdsOrd(SecondaryObject,SourceBase,NoteBase,DateBase,PlaceBase,PrivacyBase):
    """
    Class that contains information about LDS Ordinances. LDS
    ordinances are similar to events, but have very specific additional
    information related to data collected by the Church of Jesus Christ
    of Latter Day Saints (Morman church). The LDS church is the largest
    source of genealogical information in the United States.
    """

    BAPTISM = 0
    ENDOWMENT = 1
    SEAL_TO_PARENTS = 2
    SEAL_TO_SPOUSE = 3

    STATUS_NONE = 0
    STATUS_BIC  = 1
    STATUS_CANCELED = 2
    STATUS_CHILD = 3
    STATUS_CLEARED = 4
    STATUS_COMPLETED = 5
    STATUS_DNS = 6
    STATUS_INFANT = 7
    STATUS_PRE_1970 = 8
    STATUS_QUALIFIED = 9
    STATUS_DNS_CAN = 10
    STATUS_STILLBORN = 11
    STATUS_SUBMITTED = 12
    STATUS_UNCLEARED = 13

    def __init__(self,source=None):
        """Creates a LDS Ordinance instance"""
        SecondaryObject.__init__(self)
        SourceBase.__init__(self,source)
        NoteBase.__init__(self,source)
        DateBase.__init__(self,source)
        PlaceBase.__init__(self,source)
        PrivacyBase.__init__(self,source)
        
        if source:
            self.type = source.type
            self.famc = source.famc
            self.temple = source.temple
            self.status = source.status
        else:
            self.type = self.BAPTISM
            self.famc = None
            self.temple = ""
            self.status = 0

    def serialize(self):
        return (SourceBase.serialize(self),
                NoteBase.serialize(self),
                DateBase.serialize(self),
                self.type,self.place,
                self.famc,self.temple,self.status)

    def unserialize(self,data):
        (source_list,note,date,self.type,self.place,
         self.famc,self.temple,self.status) = data
        SourceBase.unserialize(self,source_list)
        NoteBase.unserialize(self,note)
        DateBase.unserialize(self,date)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.temple]
        #return [self.temple,self.get_date()]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.source_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        if self.place:
            return [('Place',self.place)]
        else:
            return []

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

    def get_type(self):
        return self.type

    def set_type(self, ord_type):
        self.type = ord_type

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
            return False
        else:
            return True
        
    def are_equal(self,other):
        """returns 1 if the specified ordinance is the same as the instance"""
        warn( "Use is_equal instead are_equal", DeprecationWarning, 2)
        return self.is_equal(other)
