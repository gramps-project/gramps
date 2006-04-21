#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

from _GrampsType import GrampsType, init_map
from gettext import gettext as _

class AttributeType(GrampsType):

    UNKNOWN     = -1
    CUSTOM      = 0
    CASTE       = 1
    DESCRIPTION = 2
    ID          = 3
    NATIONAL    = 4
    NUM_CHILD   = 5
    SSN         = 6

    _CUSTOM = CUSTOM
    _DEFAULT = ID

    _DATAMAP = [
        (UNKNOWN     , _("Unknown"), "Unknown"),
        (CUSTOM      , _("Custom"), "Custom"),
        (CASTE       , _("Caste"), "Caste"),
        (DESCRIPTION , _("Description"), "Description"),
        (ID          , _("Identification Number"), "Identification Number"),
        (NATIONAL    , _("National Origin"), "National Origin"),
        (NUM_CHILD   , _("Number of Children"), "Number of Children"),
        (SSN         , _("Social Security Number"), "Social Security Number"),
        (NUM_CHILD   , _("Number of Children"), "Number of Children"),
        ]

    _I2SMAP = init_map(_DATAMAP, 0, 1)
    _S2IMAP = init_map(_DATAMAP, 1, 0)
    _I2EMAP = init_map(_DATAMAP, 0, 2)
    _E2IMAP = init_map(_DATAMAP, 2, 0)

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
        
