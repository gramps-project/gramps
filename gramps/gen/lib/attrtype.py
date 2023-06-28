#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2015       Paul Franklin
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
Provide the different Attribute Types for Gramps.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value, context=''): # enable deferred translations
    return "%s\x04%s" % (context, value) if context else value

class AttributeType(GrampsType):

    UNKNOWN = -1
    CUSTOM = 0
    CASTE = 1
    DESCRIPTION = 2
    ID = 3
    NATIONAL = 4
    NUM_CHILD = 5
    SSN = 6
    NICKNAME = 7
    CAUSE = 8
    AGENCY = 9
    AGE = 10
    FATHER_AGE = 11
    MOTHER_AGE = 12
    WITNESS = 13
    TIME = 14
    OCCUPATION = 15

    _CUSTOM = CUSTOM
    _DEFAULT = ID

    _BASEMAP = [ # allow deferred translation of attribute UI strings
        (UNKNOWN, _T_("Unknown"), "Unknown"),
        (CUSTOM, _T_("Custom"), "Custom"),
        (CASTE, _T_("Caste"), "Caste"),
        (DESCRIPTION, _T_("Description"), "Description"),
        (ID, _T_("Identification Number"), "Identification Number"),
        (NATIONAL, _T_("National Origin"), "National Origin"),
        (NUM_CHILD, _T_("Number of Children"), "Number of Children"),
        (SSN, _T_("Social Security Number"), "Social Security Number"),
        (NICKNAME, _T_("Nickname"), "Nickname"),
        (CAUSE, _T_("Cause"), "Cause"),
        (AGENCY, _T_("Agency"), "Agency"),
        (AGE, _T_("Age"), "Age"),
        (FATHER_AGE, _T_("Father's Age"), "Father Age"),
        (MOTHER_AGE, _T_("Mother's Age"), "Mother Age"),
        (WITNESS, _T_("Witness"), "Witness"),
        (TIME, _T_("Time"), "Time"),
        (OCCUPATION, _T_("Occupation"), "Occupation"),
        ]

    _DATAMAP = [(base[0], _(base[1]), base[2]) for base in _BASEMAP]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

    def type2base(self):
        """
        Return the untranslated string suitable for UI (once translated).
        """
        if self.value == self.CUSTOM:
            return str(self)
        elif self._BASEMAP[self.value+1]: # UNKNOWN is before CUSTOM, sigh
            return self._BASEMAP[self.value+1][1]
        else:
            return self.UNKNOWN
