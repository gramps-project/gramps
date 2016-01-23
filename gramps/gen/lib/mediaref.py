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
Media Reference class for Gramps.
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
from .attrbase import AttributeBase
from .const import IDENTICAL, EQUAL, DIFFERENT
from .handle import Handle

#-------------------------------------------------------------------------
#
# Media References for Person/Place/Source
#
#-------------------------------------------------------------------------
class MediaRef(SecondaryObject, PrivacyBase, CitationBase, NoteBase, RefBase,
               AttributeBase):
    """Media reference class."""
    def __init__(self, source=None):
        PrivacyBase.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)
        RefBase.__init__(self, source)
        AttributeBase.__init__(self, source)

        if source:
            self.rect = source.rect
        else:
            self.rect = None

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (PrivacyBase.serialize(self),
                CitationBase.serialize(self),
                NoteBase.serialize(self),
                AttributeBase.serialize(self),
                RefBase.serialize(self),
                self.rect)

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
        return {"_class": "MediaRef",
                "private": PrivacyBase.serialize(self),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "attribute_list": AttributeBase.to_struct(self),
                "ref": Handle("Media", self.ref),
                "rect": self.rect if self.rect != (0, 0, 0, 0) else None}

    @classmethod
    def get_schema(cls):
        """
        Returns the schema for MediaRef.

        :returns: Returns a dict containing the fields to types.
        :rtype: dict
        """
        from .attribute import Attribute
        from .citation import Citation
        from .note import Note
        return {
            "private": bool,
            "citation_list": [Citation],
            "note_list": [Note],
            "attribute_list": [Attribute],
            "ref": Handle("Media", "MEDIA-HANDLE"),
            "rect": tuple, # or None if (0,0,0,0)
        }

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = MediaRef()
        return (PrivacyBase.from_struct(struct.get("private", default.private)),
                CitationBase.from_struct(struct.get("citation_list",
                                                    default.citation_list)),
                NoteBase.from_struct(struct.get("note_list",
                                                default.note_list)),
                AttributeBase.from_struct(struct.get("attribute_list",
                                                     default.attribute_list)),
                RefBase.from_struct(struct.get("ref", default.ref)),
                struct.get("rect", default.rect))

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (privacy, citation_list, note_list, attribute_list, ref,
         self.rect) = data
        PrivacyBase.unserialize(self, privacy)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        AttributeBase.unserialize(self, attribute_list)
        RefBase.unserialize(self, ref)
        return self

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.attribute_list

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer Citations.

        :returns: Returns the list of child secondary child objects that may
                  refer Citations.
        :rtype: list
        """
        return self.attribute_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may
                  refer notes.
        :rtype: list
        """
        return self.attribute_list

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
            ret += [('Media', self.ref)]
        return ret

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.get_citation_child_list()

    def is_equivalent(self, other):
        """
        Return if this object reference is equivalent, that is agrees in
        reference and region, to other.

        :param other: The object reference to compare this one to.
        :type other: MediaRef
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if self.ref != other.ref or self.rect != other.rect:
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this object reference.

        Lost: hlink and region or acquisition.

        :param acquisition: The object reference to merge with the present one.
        :type acquisition: MediaRef
        """
        self._merge_privacy(acquisition)
        self._merge_attribute_list(acquisition)
        self._merge_citation_list(acquisition)
        self._merge_note_list(acquisition)

    def set_rectangle(self, coord):
        """Set subsection of an image."""
        self.rect = coord

    def get_rectangle(self):
        """Return the subsection of an image."""
        return self.rect
