#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Provide the different PlaceRef Hierarchy types.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


class PlaceHierType(GrampsType):
    """
    Provide the different PlaceRef Hierarchy types.
    """

    UNKNOWN = -1
    CUSTOM = 0
    ADMIN = 1
    RELI = 2
    GEOG = 3
    CULT = 4
    JUDI = 5

    _CUSTOM = CUSTOM
    _DEFAULT = ADMIN

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (ADMIN, _("Administrative"), "Administrative"),
        (RELI, _("Religious"), "Religious"),
        (GEOG, _("Geographical"), "Geographical"),
        (CULT, _("Cultural"), "Cultural"),
        (JUDI, _("Judicial"), "Judicial"),
    ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        return {
            "type": "object",
            "title": _("Hierarchy"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "string": {"type": "string", "title": _("Type")},
            },
        }
