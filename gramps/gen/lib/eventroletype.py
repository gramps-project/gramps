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
Provide the different event roles.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .grampstype import GrampsType

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# EventRoleType
#
# -------------------------------------------------------------------------
class EventRoleType(GrampsType):
    """
    Class representing role a participant played in an event.
    """

    UNKNOWN = -1
    CUSTOM = 0
    PRIMARY = 1
    CLERGY = 2
    CELEBRANT = 3
    AIDE = 4
    BRIDE = 5
    GROOM = 6
    WITNESS = 7
    FAMILY = 8
    INFORMANT = 9
    GODPARENT = 10
    FATHER = 11
    MOTHER = 12
    PARENT = 13
    CHILD = 14
    MULTIPLE = 15
    FRIEND = 16
    NEIGHBOR = 17
    OFFICIATOR = 18
    PLACE = 19

    _CUSTOM = CUSTOM
    _DEFAULT = PRIMARY

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (PRIMARY, _("Primary", "Role"), "Primary"),
        (CLERGY, _("Clergy"), "Clergy"),
        (CELEBRANT, _("Celebrant"), "Celebrant"),
        (AIDE, _("Aide"), "Aide"),
        (BRIDE, _("Bride"), "Bride"),
        (GROOM, _("Groom"), "Groom"),
        (WITNESS, _("Witness"), "Witness"),
        (FAMILY, _("Family", "Role"), "Family"),
        (INFORMANT, _("Informant"), "Informant"),
        (GODPARENT, _("Godparent"), "Godparent"),
        (FATHER, _("Father"), "Father"),
        (MOTHER, _("Mother"), "Mother"),
        (PARENT, _("Parent"), "Parent"),
        (CHILD, _("Child"), "Child"),
        (MULTIPLE, _("Multiple birth"), "Multiple birth"),
        (FRIEND, _("Friend"), "Friend"),
        (NEIGHBOR, _("Neighbor"), "Neighbor"),
        (OFFICIATOR, _("Officiator"), "Officiator"),
        (PLACE, _("Place"), "Place"),
    ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

    def is_primary(self):
        """
        Returns True if EventRoleType is PRIMARY, False otherwise.
        """
        return self.value == self.PRIMARY

    def is_family(self):
        """
        Returns True if EventRoleType is FAMILY, False otherwise.
        """
        return self.value == self.FAMILY

    def is_place(self):
        """
        Returns True if EventRoleType is PLACE, False otherwise.
        """
        return self.value == self.PLACE
