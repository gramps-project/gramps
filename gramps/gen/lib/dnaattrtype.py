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
DNA Attribute Type class for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .grampstype import GrampsType

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# DNAAttributeType
#
# -------------------------------------------------------------------------
class DNAAttributeType(GrampsType):
    """
    Type enumeration for DNA attributes.

    Only UNKNOWN and CUSTOM are defined; specific marker or locus names
    (DYS393, HVR1, etc.) are stored as CUSTOM type strings and tracked
    separately in the database as previously used values.
    """

    UNKNOWN = -1
    CUSTOM = 0

    _CUSTOM = CUSTOM
    _DEFAULT = UNKNOWN

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
    ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
