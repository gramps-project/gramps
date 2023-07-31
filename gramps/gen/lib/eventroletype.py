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
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


class EventRoleType(GrampsType):
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
