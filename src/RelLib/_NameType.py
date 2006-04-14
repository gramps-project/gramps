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

# $Id: _Name.py 6326 2006-04-13 11:21:33Z loshawlos $

from _GrampsType import GrampsType
from gettext import gettext as _

class NameType(GrampsType):

    UNKNOWN = -1
    CUSTOM  = 0
    AKA     = 1
    BIRTH   = 2
    MARRIED = 3

    _CUSTOM = CUSTOM
    _DEFAULT = BIRTH

    _I2SMAP = {
        UNKNOWN : _("Unknown"),
        CUSTOM  : _("Custom"),
        AKA     : _("Also Known As"),
        BIRTH   : _("Birth Name"),
        MARRIED : _("Married Name"),
        }

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
        
        
