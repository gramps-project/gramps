#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
DNA Attribute class for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .attribute import AttributeRoot
from .citationbase import CitationBase
from .dnaattrtype import DNAAttributeType
from .notebase import NoteBase
from .privacybase import PrivacyBase

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# DNAAttribute
#
# -------------------------------------------------------------------------
class DNAAttribute(AttributeRoot, CitationBase, NoteBase):
    """
    A key/value attribute for a DNA test or match.

    Used for STR markers, mtDNA mutations, and other typed metadata.
    The type is always a CUSTOM string (e.g. "DYS393", "HVR1"); there are
    no predefined non-custom type codes beyond UNKNOWN.

    Supports citation and note annotations so individual markers and
    mutations can carry their own source evidence.
    """

    def __init__(self, source=None):
        AttributeRoot.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)

        if source:
            self.type = DNAAttributeType(source.type)
            self.value = source.value
        else:
            self.type = DNAAttributeType()
            self.value = ""

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            PrivacyBase.serialize(self),
            CitationBase.serialize(self),
            NoteBase.serialize(self),
            self.type.serialize(),
            self.value,
        )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        privacy, citation_list, note_list, the_type, self.value = data
        PrivacyBase.unserialize(self, privacy)
        CitationBase.unserialize(self, citation_list)
        NoteBase.unserialize(self, note_list)
        self.type.unserialize(the_type)
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
            "title": _("Attribute"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "private": {"type": "boolean", "title": _("Private")},
                "citation_list": {
                    "type": "array",
                    "title": _("Citations"),
                    "items": {"type": "string", "maxLength": 50},
                },
                "note_list": {
                    "type": "array",
                    "items": {"type": "string", "maxLength": 50},
                    "title": _("Notes"),
                },
                "type": DNAAttributeType.get_schema(),
                "value": {"type": "string", "title": _("Value")},
            },
        }

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return (
            self.get_referenced_note_handles() + self.get_referenced_citation_handles()
        )

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this attribute.

        Lost: type and value of acquisition.

        :param acquisition: the attribute to merge with the present attribute.
        :type acquisition: DNAAttribute
        """
        AttributeRoot.merge(self, acquisition)
        self._merge_citation_list(acquisition)
        self._merge_note_list(acquisition)
