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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Provide the different child reference types.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class ChildRefType(GrampsType):
    """
    Provide the different ChildRef types.

    .. attribute NONE : None - no relationship
    .. attribute BIRTH : Birth - relation by birth. Implicates genetic
            relationship if no other families with other types are present
    .. attribute ADOPTED : Adopted - adopted child. The real parents have
            given up the child for adoption
    .. attribute STEPCHILD : Stepchild - stepchild, the child is from the other
            partner, relationship is due to the forming of the marriage
    .. attribute SPONSORED : Sponsored - parent is sponsoring the child
    .. attribute FOSTER : Foster - taking care of the child while the real
            parents are around and know of it. This can be due to the parents
            not being able to care for the child, or because government has
            ordered this
    .. attribute UNKNOWN : Unknown - unknown relationship
    .. attribute CUSTOM : Custom - a relationship given by the user
    """

    NONE = 0
    BIRTH = 1
    ADOPTED = 2
    STEPCHILD = 3
    SPONSORED = 4
    FOSTER = 5
    UNKNOWN = 6
    CUSTOM = 7

    _CUSTOM = CUSTOM
    _DEFAULT = BIRTH

    _DATAMAP = [
        (NONE, _("None"), "None"),
        (BIRTH, _("Birth"), "Birth"),
        (ADOPTED, _("Adopted"), "Adopted"),
        (STEPCHILD, _("Stepchild"), "Stepchild"),
        (SPONSORED, _("Sponsored"), "Sponsored"),
        (FOSTER, _("Foster"), "Foster"),
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
