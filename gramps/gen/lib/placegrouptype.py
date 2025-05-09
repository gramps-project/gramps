#
# Gramps - a GTK+/GNOME based genealogy program
#
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
Provide the different Place Group types.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


class PlaceGroupType(GrampsType):
    """
    Provide the different Place Group types.
    """

    CUSTOM = -1
    NONE = 0
    COUNTRY = 1
    REGION = 2
    PLACE = 3
    UNPOP = 4
    BUILDING = 5
    OTHER = 6

    _CUSTOM = CUSTOM
    _DEFAULT = PLACE

    _DATAMAP = [
        (NONE, _("None"), "None"),
        (CUSTOM, "", ""),
        (PLACE, _("Places"), "Place"),
        (UNPOP, _("Unpopulated Places"), "Unpop"),
        (COUNTRY, _("Countries"), "Country"),
        (REGION, _("Regions"), "Region"),
        (BUILDING, _("Buildings"), "Building"),
        (OTHER, _("Other"), "Other"),
    ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
