#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013       Doug Blank <doug.blank@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
LDS Ordinance class for Gramps.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from warnings import warn

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .citationbase import CitationBase
from .notebase import NoteBase
from .datebase import DateBase
from .placebase import PlaceBase
from .privacybase import PrivacyBase
from .const import IDENTICAL, EQUAL, DIFFERENT

#-------------------------------------------------------------------------
#
# LDS Ordinance class
#
#-------------------------------------------------------------------------
class LdsOrd(SecondaryObject, CitationBase, NoteBase,
             DateBase, PlaceBase, PrivacyBase):
    """
    Class that contains information about LDS Ordinances.

    LDS ordinances are similar to events, but have very specific additional
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
        """Create a LDS Ordinance instance."""
        CitationBase.__init__(self, source)
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
        Convert the object to a serialized tuple of data.
        """
        return (CitationBase.serialize(self),
                NoteBase.serialize(self),
                DateBase.serialize(self),
                self.type, self.place,
                self.famc, self.temple, self.status, self.private)

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.

        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {"_class": "LdsOrd",
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "date": DateBase.to_struct(self),
                "type": self.type,
                "place": self.place,
                "famc": self.famc,
                "temple": self.temple,
                "status": self.status,
                "private": self.private}

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = LdsOrd()
        return (CitationBase.from_struct(struct.get("citation_list", default.citation_list)),
                NoteBase.from_struct(struct.get("note_list", default.note_list)),
                DateBase.from_struct(struct.get("date", {})),
                struct.get("type", {}),
                struct.get("place", default.place),
                struct.get("famc", default.famc),
                struct.get("temple", default.temple),
                struct.get("status", default.status),
                struct.get("private", default.private))

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (citation_list, note_list, date, self.type, self.place,
         self.famc, self.temple, self.status, self.private) = data
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        DateBase.unserialize(self, date)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.temple]
        #return [self.temple,self.get_date()]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return []

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may
                  refer notes.
        :rtype: list
        """
        return []

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        ret = self.get_referenced_note_handles() + \
                self.get_referenced_citation_handles()
        if self.place:
            ret += [('Place', self.place)]
        if self.famc:
            ret += [('Family', self.famc)]
        return ret

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return []

    def is_equivalent(self, other):
        """
        Return if this ldsord is equivalent, that is agrees in date, temple,
        place, status, sealed_to, to other.

        :param other: The ldsord to compare this one to.
        :type other: LdsOrd
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if self.type != other.type or \
            self.get_date_object() != other.get_date_object() or \
            self.temple != other.temple or \
            self.status != other.status or \
            self.famc != other.famc:
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this ldsord.

        Lost: type, date, temple, place, status, sealed_to of acquistion.

        :param acquisition: The ldsord to merge with the present ldsord.
        :type acquisition: LdsOrd
        """
        self._merge_privacy(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)

    def get_type(self):
        """
        Return the type of the Event.

        :returns: Type of the Event
        :rtype: tuple
        """
        return self.type

    def set_type(self, ord_type):
        """
        Set the type of the LdsOrd to the passed (int,str) tuple.

        :param ord_type: Type to assign to the LdsOrd
        :type ord_type: tuple
        """
        self.type = ord_type

    def set_family_handle(self, family):
        """Set the Family database handle associated with the LDS ordinance."""
        self.famc = family

    def get_family_handle(self):
        """Get the Family database handle associated with the LDS ordinance."""
        return self.famc

    def set_status(self, val):
        """
        Set the status of the LDS ordinance.

        The status is a text string that matches a predefined set of strings.
        """
        self.status = val

    def get_status(self):
        """Get the status of the LDS ordinance."""
        return self.status

    def set_temple(self, temple):
        """Set the temple associated with the ordinance."""
        self.temple = temple

    def get_temple(self):
        """Get the temple associated with the ordinance."""
        return self.temple

    def is_empty(self):
        """Return 1 if the ordinance is actually empty."""
        if (self.famc or
                (self.date and not self.date.is_empty()) or
                self.temple or
                self.status or
                self.place):
            return False
        else:
            return True

    def are_equal(self, other):
        """Return 1 if the specified ordinance is the same as the instance."""
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

        Return boolean on success.
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

        Return boolean on success.
        """
        for item in LdsOrd._STATUS_MAP:
            if item[2] == xml_str:
                self.status = item[0]
                return True
        return False
