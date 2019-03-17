#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2015,2017  Nick Hall
# Copyright (C) 2019       Paul Culley
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
Place Abbreviation class for Gramps
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .placeabbrevtype import PlaceAbbrevType
from .const import IDENTICAL, EQUAL, DIFFERENT
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


#-------------------------------------------------------------------------
#
# Place Abbreviation
#
#-------------------------------------------------------------------------
class PlaceAbbrev(SecondaryObject):
    """
    Place abbreviation class.

    This class is for keeping information about place abbreviations.
    """

    def __init__(self, source=None, **kwargs):
        """
        Create a new PlaceAbbrev instance, copying from the source if present.
        """
        if source:
            self.value = source.value
            self.type = source.type
        else:
            self.value = ''
            self.type = PlaceAbbrevType()
        for key in kwargs:
            if key in ["value", "type"]:
                setattr(self, key, kwargs[key])
            else:
                raise AttributeError(
                    "PlaceAbbrev does not have property '%s'" % key)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.value, self.type)

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.value, self.type) = data
        return self

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        return {
            "type": "object",
            "title": _("Place Abbrev"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "value": {"type": "string",
                          "title": _("Text")},
                "type": {"type": PlaceAbbrevType.get_schema(),
                         "title": _("Type")}
            }
        }

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.value]

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

    def is_equivalent(self, other):
        """
        Return if this eventref is equivalent, that is agrees in handle and
        role, to other.

        :param other: The eventref to compare this one to.
        :type other: PlaceAbbrev
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if (self.value != other.value or self.type != other.type):
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def __eq__(self, other):
        return self.is_equal(other)

    def __ne__(self, other):
        return not self.is_equal(other)

    def set_value(self, value):
        """
        Set the abbrev for the PlaceAbbrev instance.
        """
        self.value = value

    def get_value(self):
        """
        Return the abbrev for the PlaceAbbrev instance.
        """
        return self.value

    def set_type(self, p_type):
        """
        Set the type for the PlaceAbbrev instance.
        """
        self.type.set(p_type)

    def get_type(self):
        """Return the type for the PlaceAbbrev instance."""
        return self.type
