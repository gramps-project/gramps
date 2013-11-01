#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$

"""
Provide the different place types.
"""
#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .grampstype import GrampsType

class PlaceType(GrampsType):

    UNKNOWN     = -1
    CUSTOM      = 0
    COUNTRY     = 1
    STATE       = 2
    COUNTY      = 3
    CITY        = 4
    PARISH      = 5
    LOCALITY    = 6
    STREET      = 7

    _CUSTOM = CUSTOM
    _DEFAULT = COUNTRY

    _DATAMAP = [
        (UNKNOWN,  _("Unknown"),  "Unknown"),
        (CUSTOM,   _("Custom"),   "Custom"),
        (COUNTRY,  _("Country"),  "Country"),
        (STATE,    _("State"),    "State"),
        (COUNTY,   _("County"),   "County"),
        (CITY,     _("City"),     "City"),
        (PARISH,   _("Parish"),   "Parish"),
        (LOCALITY, _("Locality"), "Locality"),
        (STREET,   _("Street"),   "Street"),
        ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
