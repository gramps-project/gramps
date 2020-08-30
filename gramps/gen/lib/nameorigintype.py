#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Benny Malengier
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
Name types.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

class NameOriginType(GrampsType):
    """
    Name Origin Types

    .. attribute UNKNOWN:    Unknown origin
    .. attribute CUSTOM:     Custom user defined origin
    .. attribute NONE:       no given origin
    .. attribute INHERITED:  name was inherited from parents
    .. attribute PATRILINEAL:name was inherited from father's family name
    .. attribute MATRILINEAL:name was inherited from mother's family name
    .. attribute GIVEN:      name was bestowed on the individual
    .. attribute TAKEN:      name was chosen by the individual
    .. attribute PATRONYMIC: name is derived from father's given name
    .. attribute MATRONYMIC: name is derived from mother's given name
    .. attribute FEUDAL:     name refers to the holding of land in a fief
    .. attribute PSEUDONYM:  name is fictitious
    .. attribute OCCUPATION: name follows from the occupation of the person
    .. attribute LOCATION:   name follows from the location of the person
    """

    UNKNOWN = -1
    CUSTOM = 0
    NONE = 1
    INHERITED = 2
    GIVEN = 3
    TAKEN = 4
    PATRONYMIC = 5
    MATRONYMIC = 6
    FEUDAL = 7
    PSEUDONYM = 8
    PATRILINEAL = 9
    MATRILINEAL = 10
    OCCUPATION = 11
    LOCATION = 12

    _CUSTOM = CUSTOM
    _DEFAULT = NONE

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown "),
        (CUSTOM, _("Custom"), "Custom"),
        (NONE, "", ""),
        (INHERITED, _("Inherited", "Surname"), "Inherited"),
        (GIVEN, _("Given", "Surname"), "Given"),
        (TAKEN, _("Taken", "Surname"), "Taken"),
        (PATRONYMIC, _("Patronymic"), "Patronymic"),
        (MATRONYMIC, _("Matronymic"), "Matronymic"),
        (FEUDAL, _("Feudal", "Surname"), "Feudal"),
        (PSEUDONYM, _("Pseudonym"), "Pseudonym"),
        (PATRILINEAL, _("Patrilineal"), "Patrilineal"),
        (MATRILINEAL, _("Matrilineal"), "Matrilineal"),
        (OCCUPATION, _("Occupation"), "Occupation"),
        (LOCATION, _("Location"), "Location"),
        ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
