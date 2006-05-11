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

class MarkerType(GrampsType):

    NONE = -1
    CUSTOM = 0
    COMPLETE = 1
    TODO = 2

    _CUSTOM = CUSTOM
    _DEFAULT = NONE

    _DATAMAP = [
        (NONE,    "",   ""),
        (CUSTOM,   _("Custom"),   "Custom"),
        (COMPLETE, _("Complete"), "Complete"),
        (TODO,     _("ToDo"),     "ToDo"),
        ]

    _I2SMAP = init_map(_DATAMAP, 0, 1)
    _S2IMAP = init_map(_DATAMAP, 1, 0)
    _I2EMAP = init_map(_DATAMAP, 0, 2)
    _E2IMAP = init_map(_DATAMAP, 2, 0)

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

    def set(self, value):
        if isinstance(value,self.__class__):
            if value.val == self.CUSTOM and value.string == '':
                self.val = self.NONE
                self.string = ''
            else:
                self.val = value.val
                self.string = value.string
        elif type(value) == tuple:
            if value[0] == self.CUSTOM and value[1] == '':
                self.value = self.NONE
                self.string = ''
            else:
                self.val = value[0]
                self.string = value[1]
        elif type(value) == int:
            self.val = value
            self.string = ''
        elif type(value) == str:
            self.val = self._S2IMAP.get(value,self._CUSTOM)
            if self.val == self._CUSTOM:
                self.string = value
            else:
                self.string = ''
        else:
            self.val = self._DEFAULT
            self.string = ''
