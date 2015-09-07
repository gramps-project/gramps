#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2006-2007  Donald N. Allingham
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
Child Reference class for Gramps.
"""
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .privacybase import PrivacyBase
from .citationbase import CitationBase
from .notebase import NoteBase
from .refbase import RefBase
from .childreftype import ChildRefType
from .const import IDENTICAL, EQUAL, DIFFERENT
from .handle import Handle

#-------------------------------------------------------------------------
#
# Person References for Person/Family
#
#-------------------------------------------------------------------------
class ChildRef(SecondaryObject, PrivacyBase, CitationBase, NoteBase, RefBase):
    """
    Person reference class.

    This class is for keeping information about how the person relates
    to another person from the database, if not through family.
    Examples would be: godparent, friend, etc.
    """

    def __init__(self, source=None):
        PrivacyBase.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)
        RefBase.__init__(self, source)
        if source:
            self.frel = ChildRefType(source.frel)
            self.mrel = ChildRefType(source.mrel)
        else:
            self.frel = ChildRefType()
            self.mrel = ChildRefType()

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (PrivacyBase.serialize(self),
                CitationBase.serialize(self),
                NoteBase.serialize(self),
                RefBase.serialize(self),
                self.frel.serialize(),
                self.mrel.serialize())

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
        return {"_class": "ChildRef",
                "private": PrivacyBase.to_struct(self),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "ref": Handle("Person", self.ref),
                "frel": self.frel.to_struct(),
                "mrel": self.mrel.to_struct()}

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = ChildRef()
        return (PrivacyBase.from_struct(struct.get("private", default.private)),
                CitationBase.from_struct(struct.get("citation_list", default.citation_list)),
                NoteBase.from_struct(struct.get("note_list", default.note_list)),
                RefBase.from_struct(struct.get("ref", default.ref)),
                ChildRefType.from_struct(struct.get("frel", {})),
                ChildRefType.from_struct(struct.get("mrel", {})))

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (privacy, citation_list, note_list, ref, frel, mrel) = data
        PrivacyBase.unserialize(self, privacy)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        RefBase.unserialize(self, ref)
        self.frel = ChildRefType()
        self.frel.unserialize(frel)
        self.mrel = ChildRefType()
        self.mrel.unserialize(mrel)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [str(self.frel), str(self.mrel)]

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
        if self.ref:
            ret += [('Person', self.ref)]
        return ret

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through their
        children, reference primary objects..

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return []

    def is_equivalent(self, other):
        """
        Return if this child reference is equivalent, that is agrees in hlink,
        to other.

        :param other: The childref to compare this one to.
        :type other: ChildRef
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if self.ref != other.ref:
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this child reference.

        Lost: hlink, mrel and frel of acquisition.

        :param acquisition: The childref to merge with the present childref.
        :type acquisition: ChildRef
        """
        self._merge_privacy(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)
        if (self.mrel != acquisition.mrel) or (self.frel != acquisition.frel):
            if self.mrel == ChildRefType.UNKNOWN:
                self.set_mother_relation(acquisition.mrel)
            if self.frel == ChildRefType.UNKNOWN:
                self.set_father_relation(acquisition.frel)

    def set_mother_relation(self, rel):
        """Set relation between the person and mother."""
        self.mrel.set(rel)

    def get_mother_relation(self):
        """Return the relation between the person and mother."""
        return self.mrel

    def set_father_relation(self, frel):
        """Set relation between the person and father."""
        self.frel.set(frel)

    def get_father_relation(self):
        """Return the relation between the person and father."""
        return self.frel
