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
from .dnaattrtype import DNAAttributeType

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# DNAAttribute
#
# -------------------------------------------------------------------------
class DNAAttribute(AttributeRoot):
    """
    A key/value attribute for a DNA test or match.

    Used for STR markers, mtDNA mutations, and other typed metadata.
    The type is always a CUSTOM string (e.g. "DYS393", "HVR1"); there are
    no predefined non-custom type codes beyond UNKNOWN.
    """

    def __init__(self, source=None):
        AttributeRoot.__init__(self, source)

        if source:
            self.type = DNAAttributeType(source.type)
            self.value = source.value
        else:
            self.type = DNAAttributeType()
            self.value = ""

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
                "type": DNAAttributeType.get_schema(),
                "value": {"type": "string", "title": _("Value")},
            },
        }
