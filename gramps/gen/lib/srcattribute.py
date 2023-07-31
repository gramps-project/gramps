#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Benny Malengier
# Copyright (C) 2017       Nick Hall
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
Source Attribute class for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .attribute import AttributeRoot
from .srcattrtype import SrcAttributeType
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Attribute for Source/Citation
#
# -------------------------------------------------------------------------
class SrcAttribute(AttributeRoot):
    """
    Provide a simple key/value pair for describing properties.
    Used to store descriptive information.
    """

    def __init__(self, source=None):
        """
        Create a new Attribute object, copying from the source if provided.
        """
        AttributeRoot.__init__(self, source)

        if source:
            self.type = SrcAttributeType(source.type)
            self.value = source.value
        else:
            self.type = SrcAttributeType()
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
                "type": SrcAttributeType.get_schema(),
                "value": {"type": "string", "title": _("Value")},
            },
        }
