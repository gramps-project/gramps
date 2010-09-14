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

# $Id: nametype.py 14091 2010-01-18 04:42:17Z pez4brian $

"""
Name types.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import sgettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.grampstype import GrampsType

class NameOriginType(GrampsType):
    """
    Name Origina Types
    
    .. attribute UNKNOWN:   Unknown origin
    .. attribute CUSTOM:    Custom user defined origin
    .. attribute NONE:      no given origin
    .. attribute INHERITED: name was inherited from parents
    .. attribute GIVEN:     name was bestowed on the individual
    .. attribute TAKEN:     name was chosen by the individual
    .. attribute PATRONYMIC: name is derived from father's given name
    .. attribute MATRONYMIC: name is derived from mother's given name
    .. attribute FEUDAL:    name refers to the holding of land in a fief
    .. attribute PSEUDONYM: name is fictitious
    """

    UNKNOWN    = -1
    CUSTOM     = 0
    NONE       = 1
    INHERITED  = 2
    GIVEN      = 3
    TAKEN      = 4
    PATRONYMIC = 5
    MATRONYMIC = 6
    FEUDAL     = 7
    PSEUDONYM  = 8

    _CUSTOM = CUSTOM
    _DEFAULT = NONE

    _DATAMAP = [
        (UNKNOWN   , _("Unknown"),           "Unknown"),
        (CUSTOM    , _("Custom"),            "Custom"),
        (NONE      , "",                     ""),
        (INHERITED , _("Surname|Inherited"), "Inherited"),
        (GIVEN     , _("Surname|Given"),     "Given"),
        (TAKEN     , _("Surname|Taken"),     "Taken"),
        (PATRONYMIC, _("Patronymic"),        "Patronymic"),
        (MATRONYMIC, _("Matronymic"),        "Matronymic"),
        (FEUDAL    , _("Surname|Feudal"),    "Feudal"),
        (PSEUDONYM , _("Pseudonym"),         "Pseudonym"),
        
        ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

