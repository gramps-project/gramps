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
Provide the different place Abbreviation types.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


class PlaceAbbrevType(GrampsType):
    """
    Provide the different place Abbreviation types.
    """

    UNKNOWN = -1
    CUSTOM = 0
    ABBR = 1
    ISO3166 = 2
    ANSI38 = 3

    _CUSTOM = CUSTOM
    _DEFAULT = UNKNOWN

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (ABBR, _("Abbreviation"), "Abbreviation"),
        (ISO3166, _("ISO3166"), "ISO3166"),
        (ANSI38, _("ANSI standard INCITS 38:2009"), "ANSI standard INCITS 38:2009"),
    ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
