#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2013,2017  Nick Hall
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
Place Reference class for Gramps
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .const import DIFFERENT, EQUAL, IDENTICAL
from .datebase import DateBase
from .refbase import RefBase
from .secondaryobj import SecondaryObject
from .citationbase import CitationBase
from .placehiertype import PlaceHierType
from .placegrouptype import PlaceGroupType as P_G

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# PlaceRef
#
# -------------------------------------------------------------------------
class PlaceRef(RefBase, DateBase, CitationBase, SecondaryObject):
    """
    Place reference class.

    This class is for keeping information about how places link to other places
    in the place hierarchy.
    """

    def __init__(self, source=None):
        """
        Create a new PlaceRef instance, copying from the source if present.
        """
        RefBase.__init__(self, source)
        DateBase.__init__(self, source)
        CitationBase.__init__(self, source)
        if source:
            self.type = PlaceHierType(source)
        else:
            self.type = PlaceHierType()

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            RefBase.serialize(self),
            DateBase.serialize(self),
            CitationBase.serialize(self),
            self.type.serialize(),
        )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (ref, date, citation_list, h_type) = data
        RefBase.unserialize(self, ref)
        DateBase.unserialize(self, date)
        CitationBase.unserialize(self, citation_list)
        self.type = PlaceHierType()
        self.type.unserialize(h_type)
        return self

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        # pylint: disable=import-outside-toplevel
        from .date import Date

        return {
            "type": "object",
            "title": _("Place ref"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "ref": {"type": "string", "title": _("Handle"), "maxLength": 50},
                "date": {
                    "oneOf": [{"type": "null"}, Date.get_schema()],
                    "title": _("Date"),
                },
                "citation_list": {
                    "type": "array",
                    "title": _("Citations"),
                    "items": {"type": "string", "maxLength": 50},
                },
                "type": PlaceHierType.get_schema(),
            },
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

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: Returns the list of (classname, handle) tuples for referenced
                  objects.
        :rtype: list
        """
        return [("Place", self.ref)] + self.get_referenced_citation_handles()

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through their
        children, reference primary objects..

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return []

    def set_type_for_place(self, place):
        """
        Set the hierarchy type for the PlaceRef based on the group of the
        enclosing place.  If place group is a likely ADMIN candidate,
        set to ADMIN.
        If ref.type is already set, skip.
        """
        if self.type == PlaceHierType.UNKNOWN:
            group = place.get_group()
            groups = (P_G.PLACE, P_G.UNPOP, P_G.REGION, P_G.COUNTRY)
            if group in groups:
                self.type.set(PlaceHierType.ADMIN)

    def set_type(self, p_type):
        """
        Set the type for the PlaceRef instance.
        """
        self.type.set(p_type)

    def get_type(self):
        """Return the type for the PlaceRef instance."""
        return self.type

    def is_equivalent(self, other):
        """
        Return if this placeref is equivalent, that is agrees in handle and
        role, to other.

        :param other: The placeref to compare this one to.
        :type other: PlaceRef
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if (
            self.ref != other.ref
            or self.get_date_object() != other.get_date_object()
            or self.type != other.type
        ):
            return DIFFERENT
        if self.is_equal(other):
            return IDENTICAL
        return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this placeref.

        Lost: hlink and role of acquisition.

        :param acquisition: The placeref to merge with the present placeref.
        :type acquisition: PlaceRef
        """
        self._merge_citation_list(acquisition)
