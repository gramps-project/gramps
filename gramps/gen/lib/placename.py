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
Place name class for Gramps
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .datebase import DateBase
from .citationbase import CitationBase
from .placeabbrev import PlaceAbbrev
from .const import IDENTICAL, EQUAL, DIFFERENT
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


#-------------------------------------------------------------------------
#
# Place Name
#
#-------------------------------------------------------------------------
class PlaceName(SecondaryObject, CitationBase, DateBase):
    """
    Place name class.

    This class is for keeping information about place names.
    """

    def __init__(self, source=None, **kwargs):
        """
        Create a new PlaceName instance, copying from the source if present.
        """
        DateBase.__init__(self, source)
        CitationBase.__init__(self, source)
        if source:
            self.value = source.value
            self.lang = source.lang
            self.abbrev_list = list(map(PlaceAbbrev, self.abbrev_list))
        else:
            self.value = ''
            self.lang = ''
            self.abbrev_list = []
        for key in kwargs:
            if key in ["value", "lang", "abbrev_list"]:
                setattr(self, key, kwargs[key])
            else:
                raise AttributeError(
                    "PlaceName does not have property '%s'" % key)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            self.value,
            DateBase.serialize(self),
            self.lang,
            [abb.serialize() for abb in self.abbrev_list],
            CitationBase.serialize(self), )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.value, date, self.lang, abbrs, citation_list) = data
        DateBase.unserialize(self, date)
        self.abbrev_list = [PlaceAbbrev().unserialize(abb) for abb in abbrs]
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
                "value": {"type": "string",
                          "title": _("Text")},
                "date": {"oneOf": [{"type": "null"}, Date.get_schema()],
                         "title": _("Date")},
                "lang": {"type": "string",
                         "title": _("Language")},
                "abbrev_list": {"type": "array",
                                "items": PlaceAbbrev.get_schema(),
                                "title": _("Abbrevs")},
                "citation_list": {"type": "array",
                                  "title": _("Citations"),
                                  "items": {"type": "string",
                                            "maxLength": 50}},
            }
        }

    def get_abbrevs(self):
        """
        Return a list of abbrevs for the current Place name.

        :returns: Returns the abbrevs for the Place name
        :rtype: list of PlaceAbbrev
        """
        return self.abbrev_list

    def set_abbrevs(self, abbrev_list):
        """
        Replace the current abbrevs list with the new one.

        :param abbrev_list: The list of abbrevs to assign to the Place's
                            internal abbrevs list.
        :type abbrev_list: list of PlaceAbbrev
        """
        self.abbrev_list = abbrev_list

    def add_abbrev(self, abbrev):
        """
        Add a abbrev to the abbrevs list.

        :param abbrev: abbrev to add
        :type abbrev: string
        """
        if abbrev not in self.abbrev_list:
            self.abbrev_list.append(abbrev)

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: list of all textual attributes of the object.
        :rtype: list
        """
        return [self.value]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: list of child objects that may carry textual data.
        :rtype: list
        """
        return [self.abbrev_list]

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        :returns: list of child secondary child objects that may
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
        Return if this placename is equivalent, that is agrees in type and
        value, to other.

        :param other: The eventref to compare this one to.
        :type other: PlaceName
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if(self.value != other.value or self.date != other.date or
           self.lang != other.lang):
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

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this placename.

        Lost: lang, date and value of acquisition.

        :param acquisition: the placename to merge with.
        :type acquisition: PlaceName
        """
        self._merge_citation_list(acquisition)
        for abb in acquisition.abbrev_list:
            if abb not in self.abbrev_list:
                self.abbrev_list.append(abb)
