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
Place Location Type class for Gramps
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .datebase import DateBase
from .citationbase import CitationBase
from .placetype import PlaceType
from .const import IDENTICAL, EQUAL, DIFFERENT
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


#-------------------------------------------------------------------------
#
# Place Name
#
#-------------------------------------------------------------------------
class LocationType(SecondaryObject, CitationBase, DateBase):
    """
    Place Location Type class.

    This class is for keeping information about place names.
    """

    def __init__(self, source=None, **kwargs):
        """
        Create a new LocationType instance, copying from the source if present.
        """
        DateBase.__init__(self, source)
        CitationBase.__init__(self, source)
        if source:
            self.type = source.type
        else:
            self.type = PlaceType()
        for key in kwargs:
            if key in ["type", "date", "citation_list"]:
                setattr(self, key, kwargs[key])
            else:
                raise AttributeError(
                    "LocationType does not have property '%s'" % key)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            self.type.serialize(),
            DateBase.serialize(self),
            CitationBase.serialize(self),
        )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (p_type, date, citation_list) = data
        self.type = PlaceType()
        self.type.unserialize(p_type)
        DateBase.unserialize(self, date)
        CitationBase.unserialize(self, citation_list)
        return self

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        from .date import Date
        return {
            "type": "object",
            "title": _("Place Name"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "type": PlaceType.get_schema(),
                "date": {"oneOf": [{"type": "null"}, Date.get_schema()],
                         "title": _("Date")},
                "citation_list": {"type": "array",
                                  "title": _("Citations"),
                                  "items": {"type": "string",
                                            "maxLength": 50}},
            }
        }

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return []

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: list of child objects that may carry textual data.
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
        Return if this LocationType is equivalent, that is agrees in type and
        value, to other.

        :param other: The eventref to compare this one to.
        :type other: LocationType
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if(self.type != other.type or self.date != other.date):
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

    def set_type(self, p_type):
        """
        Set the type for the LocationType instance.
        """
        self.type.set(p_type)

    def get_type(self):
        """
        Return the type for the LocationType instance.
        """
        return self.type

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this LocationType.

        Lost: type, date of acquisition.

        :param acquisition: the LocationType to merge with.
        :type acquisition: LocationType
        """
        self._merge_citation_list(acquisition)
