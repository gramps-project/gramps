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

from gettext import gettext as _

def init_map(data, key_col, data_col):
    new_data = {}
    for item in data:
        new_data[item[key_col]] = item[data_col]
    return new_data

class GrampsType:

    _CUSTOM = 0
    _DEFAULT = 0

    _DATAMAP = []
    
    _I2SMAP = init_map(_DATAMAP, 0, 1)
    _S2IMAP = init_map(_DATAMAP, 1, 0)
    _I2EMAP = init_map(_DATAMAP, 0, 2)
    _E2IMAP = init_map(_DATAMAP, 2, 0)

    def __init__(self, value=None):
        self.set(value)

    def set(self, value):
        if isinstance(value,self.__class__):
            self.val = value.val
            self.string = value.string
        elif type(value) == tuple:
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

    def set_from_xml_str(self, value):
        """
        This method sets the type instance based on the untranslated
        string (obtained e.g. from XML).
        """
        if self._E2IMAP.has_key(value):
            self.val = self._E2IMAP[value]
            self.string = ''
        else:
            self.val = self._CUSTOM
            self.string = value

    def xml_str(self):
        if self.val == self._CUSTOM:
            return self.string
        else:
            return self._I2EMAP[self.val]

    def serialize(self):
        return (self.val, self.string)

    def unserialize(self, data):
        self.val, self.string = data

    def __str__(self):
        if self.val == self._CUSTOM:
            return self.string
        else:
            return self._I2SMAP.get(self.val,_('Unknown'))

    def set_from_xml_str(self,the_str):
        return self

    def __int__(self):
        return self.val

    def get_map(self):
        return self._I2SMAP

    def is_custom(self):
        return self.val == self._CUSTOM

    def is_default(self):
        return self.val == self._DEFAULT

    def get_custom(self):
        return self._CUSTOM
    
    def __cmp__(self, value):
        if type(value) == int:
            return cmp(self.val,value)
        elif type(value) == str:
            if self.val == self._CUSTOM:
                return cmp(self.string,value)
            else:
                return cmp(self._I2SMAP.get(self.val),value)
        elif type(value) == tuple:
            return cmp((self.val,self.string),value)
        else:
            if value.val == self._CUSTOM:
                return cmp(self.string,value.string)
            else:
                return cmp(self.val,value.val)
