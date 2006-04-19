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

from _GrampsType import GrampsType, init_map
from gettext import gettext as _

class UrlType(GrampsType):

    UNKNOWN    = -1
    CUSTOM     = 0
    EMAIL      = 1
    WEB_HOME   = 2
    WEB_SEARCH = 3
    WEB_FTP    = 4

    _CUSTOM = CUSTOM
    _DEFAULT = UNKNOWN

    _DATAMAP = [
        (UNKNOWN,    _("Unknown"),    "Unknown"),
        (CUSTOM,     _("Custom"),     "Custom"),
        (EMAIL,      _("E-mail"),     "E-mail"),
        (WEB_HOME,   _("Web Home"),   "Web Home"),
        (WEB_SEARCH, _("Web Search"), "Web Search"),
        (WEB_FTP,    _("FTP"),        "FTP"),
        ]

    _I2SMAP = init_map(_DATAMAP, 0, 1)
    _S2IMAP = init_map(_DATAMAP, 1, 0)
    _I2EMAP = init_map(_DATAMAP, 0, 2)
    _E2IMAP = init_map(_DATAMAP, 2, 0)

    def __init__(self, value=None):
        GrampsType.__init__(self, value)


        
