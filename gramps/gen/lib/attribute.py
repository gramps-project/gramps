#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
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
Attribute class for Gramps.
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
from .attrtype import AttributeType
from .const import IDENTICAL, EQUAL, DIFFERENT

#-------------------------------------------------------------------------
#
# Root object for Attribute
#
#-------------------------------------------------------------------------
class AttributeRoot(SecondaryObject, PrivacyBase):
    """
    Provide a simple key/value pair for describing properties.
    Used to store descriptive information.

    In GEDCOM only used for Persons:
    Individual attributes should describe situations that may be permanent or
    temporary (start at some date, end at some date, etc.), may be associated
    to a place (a position held, residence, etc.) or may not (eye colour,
    height, caste, profession, etc.).  They may have sources and notes and
    media.
    Compare with :class:`~.event.Event`

    Gramps at the moment does not support this GEDCOM Attribute structure.
    """

    def __init__(self, source=None):
        """
        Create a new Attribute object, copying from the source if provided.
        """
        PrivacyBase.__init__(self, source)

        #type structure depends on inheriting classes
        self.type = None
        self.value = None

    def __str__(self):
        return str(self.value)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (PrivacyBase.serialize(self),
                self.type.serialize(), self.value)

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
        return {"_class": self.__class__.__name__,
                "private": PrivacyBase.serialize(self),
                "type": self.type.to_struct(),
                "value": self.value}

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = Attribute()
        return (PrivacyBase.from_struct(struct.get("private", default.private)),
                AttributeType.from_struct(struct.get("type", {})),
                struct.get("value", default.value))

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (privacy, the_type, self.value) = data
        PrivacyBase.unserialize(self, privacy)
        self.type.unserialize(the_type)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.value]

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

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
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
        return []

    def is_equivalent(self, other):
        """
        Return if this attribute is equivalent, that is agrees in type and
        value, to other.

        :param other: The attribute to compare this one to.
        :type other: Attribute
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if self.type != other.type or self.value != other.value:
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this attribute.

        Lost: type and value of acquisition.

        :param acquisition: the attribute to merge with the present attribute.
        :type acquisition: Attribute
        """
        self._merge_privacy(acquisition)

    def set_type(self, val):
        """Set the type (or key) of the Attribute instance."""
        self.type.set(val)

    def get_type(self):
        """Return the type (or key) or the Attribute instance."""
        return self.type

    def set_value(self, val):
        """Set the value of the Attribute instance."""
        self.value = val

    def get_value(self):
        """Return the value of the Attribute instance."""
        return self.value

#-------------------------------------------------------------------------
#
# Attribute for Person/Family/MediaObject/MediaRef
#
#-------------------------------------------------------------------------
class Attribute(AttributeRoot, CitationBase, NoteBase):

    def __init__(self, source=None):
        """
        Create a new Attribute object, copying from the source if provided.
        """
        AttributeRoot.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)

        if source:
            self.type = AttributeType(source.type)
            self.value = source.value
        else:
            self.type = AttributeType()
            self.value = ""
    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (PrivacyBase.serialize(self),
                CitationBase.serialize(self),
                NoteBase.serialize(self),
                self.type.serialize(), self.value)

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
        return {"_class": "Attribute",
                "private": PrivacyBase.serialize(self),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "type": self.type.to_struct(),
                "value": self.value}

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        return (PrivacyBase.from_struct(struct["private"]),
                CitationBase.from_struct(struct["citation_list"]),
                NoteBase.from_struct(struct["note_list"]),
                AttributeType.from_struct(struct["type"]),
                struct["value"])

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (privacy, citation_list, note_list, the_type, self.value) = data
        PrivacyBase.unserialize(self, privacy)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        self.type.unserialize(the_type)
        return self

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return self.get_referenced_note_handles() + \
                self.get_referenced_citation_handles()

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this attribute.

        Lost: type and value of acquisition.

        :param acquisition: the attribute to merge with the present attribute.
        :type acquisition: Attribute
        """
        AttributeRoot.merge(self, acquisition)
        self._merge_citation_list(acquisition)
        self._merge_note_list(acquisition)
