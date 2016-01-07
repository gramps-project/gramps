#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2015       Nick Hall
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
Place name class for Gramps
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .datebase import DateBase
from .const import IDENTICAL, EQUAL, DIFFERENT

#-------------------------------------------------------------------------
#
# Place Name
#
#-------------------------------------------------------------------------
class PlaceName(SecondaryObject, DateBase):
    """
    Place name class.

    This class is for keeping information about place names.
    """

    def __init__(self, source=None, **kwargs):
        """
        Create a new PlaceName instance, copying from the source if present.
        """
        DateBase.__init__(self, source)
        if source:
            self.value = source.value
            self.lang = source.lang
        else:
            self.value = ''
            self.lang = ''
        for key in kwargs:
            if key in ["value", "lang"]:
                setattr(self, key, kwargs[key])
            else:
                raise AttributeError("PlaceName does not have property '%s'" % key)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            self.value,
            DateBase.serialize(self),
            self.lang
            )

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
        return {
            "_class": "PlaceName",
            "value": self.value,
            "date": DateBase.to_struct(self),
            "lang": self.lang
            }

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = PlaceName()
        return (
            struct.get("value", default.value),
            DateBase.from_struct(struct.get("date", {})),
            struct.get("lang", default.lang)
            )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.value, date, self.lang) = data
        DateBase.unserialize(self, date)
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

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        :returns: Returns the list of child secondary child objects that may
                  refer citations.
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

        :returns: Returns the list of (classname, handle) tuples for referenced
                  objects.
        :rtype: list
        """
        return []

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through their
        children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return []

    def is_equivalent(self, other):
        """
        Return if this eventref is equivalent, that is agrees in handle and
        role, to other.

        :param other: The eventref to compare this one to.
        :type other: PlaceName
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if (self.value != other.value or
                self.date != other.date or
                self.lang != other.lang):
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def set_value(self, value):
        """
        Set the name for the PlaceName instance.
        """
        self.value = value

    def get_value(self):
        """
        Return the name for the PlaceName instance.
        """
        return self.value

    def set_language(self, lang):
        """
        Set the language for the PlaceName instance.
        """
        self.lang = lang

    def get_language(self):
        """Return the language for the PlaceName instance."""
        return self.lang
