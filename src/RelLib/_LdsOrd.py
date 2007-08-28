#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
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
class LdsOrd(SecondaryObject, SourceBase, NoteBase,
             DateBase, PlaceBase, PrivacyBase):
    """
    Class that contains information about LDS Ordinances. LDS
    ordinances are similar to events, but have very specific additional
    information related to data collected by the Church of Jesus Christ
    of Latter Day Saints (Mormon church). The LDS church is the largest
    source of genealogical information in the United States.
    """

    BAPTISM         = 0
    ENDOWMENT       = 1
    SEAL_TO_PARENTS = 2
    SEAL_TO_SPOUSE  = 3
    CONFIRMATION    = 4
    
    DEFAULT_TYPE = BAPTISM


    STATUS_NONE      = 0
    STATUS_BIC       = 1
    STATUS_CANCELED  = 2
    STATUS_CHILD     = 3
    STATUS_CLEARED   = 4
    STATUS_COMPLETED = 5
    STATUS_DNS       = 6
    STATUS_INFANT    = 7
    STATUS_PRE_1970  = 8
    STATUS_QUALIFIED = 9
    STATUS_DNS_CAN   = 10
    STATUS_STILLBORN = 11
    STATUS_SUBMITTED = 12
    STATUS_UNCLEARED = 13

    DEFAULT_STATUS = STATUS_NONE


    _TYPE_MAP = [
        (BAPTISM,         _('Baptism'),           'baptism'),
        (ENDOWMENT,       _('Endowment'),         'endowment'),
        (CONFIRMATION,    _('Confirmation'),      'confirmation'),
        (SEAL_TO_PARENTS, _('Sealed to Parents'), 'sealed_to_parents'),
        (SEAL_TO_SPOUSE,  _('Sealed to Spouse'),  'sealed_to_spouse' ),
    ]
    
    _STATUS_MAP = [
        (STATUS_NONE,      _("<No Status>"), ""),
        (STATUS_BIC,       _("BIC"),         "BIC"),
        (STATUS_CANCELED,  _("Canceled"),    "Canceled"),
        (STATUS_CHILD,     _("Child"),       "Child"),
        (STATUS_CLEARED,   _("Cleared"),     "Cleared"),
        (STATUS_COMPLETED, _("Completed"),   "Completed"),
        (STATUS_DNS,       _("DNS"),         "DNS"),
        (STATUS_INFANT,    _("Infant"),      "Infant"),
        (STATUS_PRE_1970,  _("Pre-1970"),    "Pre-1970"),
        (STATUS_QUALIFIED, _("Qualified"),   "Qualified"),
        (STATUS_DNS_CAN,   _("DNS/CAN"),     "DNS/CAN"),
        (STATUS_STILLBORN, _("Stillborn"),   "Stillborn"),
        (STATUS_SUBMITTED, _("Submitted"),   "Submitted"),
        (STATUS_UNCLEARED, _("Uncleared"),   "Uncleared"),
        ]

    def __init__(self, source=None):
        """Creates a LDS Ordinance instance"""
        SourceBase.__init__(self, source)
        NoteBase.__init__(self, source)
        DateBase.__init__(self, source)
        PlaceBase.__init__(self, source)
        PrivacyBase.__init__(self, source)
        
        if source:
            self.type = source.type
            self.famc = source.famc
            self.temple = source.temple
            self.status = source.status
        else:
            self.type = LdsOrd.DEFAULT_TYPE
            self.famc = None
            self.temple = ""
            self.status = LdsOrd.DEFAULT_STATUS

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return (SourceBase.serialize(self),
                NoteBase.serialize(self),
                DateBase.serialize(self),
                self.type, self.place,
                self.famc, self.temple, self.status, self.private)

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        (source_list, note_list, date, self.type, self.place,
         self.famc, self.temple, self.status, self.private) = data
        SourceBase.unserialize(self, source_list)
        NoteBase.unserialize(self, note_list)
        DateBase.unserialize(self, date)
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
        return self.source_list

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: List of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        ret = self.get_referenced_note_handles()
        if self.place:
            ret += [('Place', self.place)]
        return ret

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

    def get_type(self):
        """
        Returns the type of the Event.

        @return: Type of the Event
        @rtype: tuple
        """
        return self.type

    def set_type(self, ord_type):
        """
        Sets the type of the LdsOrd to the passed (int,str) tuple.

        @param ord_type: Type to assign to the LdsOrd
        @type ord_type: tuple
        """
        self.type = ord_type

    def set_family_handle(self, family):
        """Sets the Family database handle associated with the LDS ordinance"""
        self.famc = family

    def get_family_handle(self):
        """Gets the Family database handle associated with the LDS ordinance"""
        return self.famc

    def set_status(self, val):
        """
        Sets the status of the LDS ordinance. The status is a text string
        that matches a predefined set of strings."""
        self.status = val

    def get_status(self):
        """Gets the status of the LDS ordinance"""
        return self.status

    def set_temple(self, temple):
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
        
    def are_equal(self, other):
        """returns 1 if the specified ordinance is the same as the instance"""
        warn( "Use is_equal instead are_equal", DeprecationWarning, 2)
        return self.is_equal(other)

    def type2xml(self):
        """
        Return type-representing string suitable for XML.
        """
        for item in LdsOrd._TYPE_MAP:
            if item[0] == self.type:
                return item[2]
        return ""

    def type2str(self):
        """
        Return type-representing string suitable for UI (translated).
        """
        for item in LdsOrd._TYPE_MAP:
            if item[0] == self.type:
                return item[1]
        return ""

    def set_type_from_xml(self, xml_str):
        """
        Set type based on a given string from XML.
        Return boolean of success.
        """
        for item in LdsOrd._TYPE_MAP:
            if item[2] == xml_str:
                self.type = item[0]
                return True
        return False

    def status2xml(self):
        """
        Return status-representing string suitable for XML.
        """
        for item in LdsOrd._STATUS_MAP:
            if item[0] == self.status:
                return item[2]
        return ""

    def status2str(self):
        """
        Return status-representing string suitable for UI (translated).
        """
        for item in LdsOrd._STATUS_MAP:
            if item[0] == self.status:
                return item[1]
        return ""

    def set_status_from_xml(self, xml_str):
        """
        Set status based on a given string from XML.
        Return boolean of success.
        """
        for item in LdsOrd._STATUS_MAP:
            if item[2] == xml_str:
                self.status = item[0]
                return True
        return False
