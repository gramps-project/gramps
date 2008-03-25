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

# $Id$

"""
Base type for all gramps types.
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

def _init_map(data, key_col, data_col):
    """
    Initialize the map, building a new map from the specified columns.
    """
    new_data = {}
    for item in data:
        new_data[item[key_col]] = item[data_col]
    return new_data

class GrampsTypeMeta(type):
    """Metaclass for L{GrampsType}.
    
    The only thing this metaclass does is calling __class_init__ class method,
    in order to create the class specific integer/string maps.
    
    """
    def __init__(mcs, name, bases, namespace):
        type.__init__(mcs, name, bases, namespace)
        mcs.__class_init__(namespace)
        
class GrampsType(object):
    """Base class for all Gramps object types."""
    (VALUE_POS, STRING_POS) = range(2)
    
    _CUSTOM = 0
    _DEFAULT = 0

    _DATAMAP = []
    
    __metaclass__ = GrampsTypeMeta
    
    def __class_init__(cls, namespace):
        cls._I2SMAP = _init_map(cls._DATAMAP, 0, 1)
        cls._S2IMAP = _init_map(cls._DATAMAP, 1, 0)
        cls._I2EMAP = _init_map(cls._DATAMAP, 0, 2)
        cls._E2IMAP = _init_map(cls._DATAMAP, 2, 0)
    
    __class_init__ = classmethod(__class_init__)
    
    def __init__(self, value=None):
        """
        Create a new type, initialize the value from one of several possible 
        states.
        """
        if value is not None:
            self.set(value)
        else:
            self.val = self._DEFAULT
            self.string = u''

    def __set_tuple(self, value):
        self.val = value[0]
        self.string = value[1]

    def __set_int(self, value):
        self.val = value
        self.string = u''

    def __set_instance(self, value):
        self.val = value.val
        self.string = value.string

    def __set_str(self, value):
        self.val = self._S2IMAP.get(value, self._CUSTOM)
        if self.val == self._CUSTOM:
            self.string = value
        else:
            self.string = u''

    def set(self, value):
        if type(value) == tuple:
            self.__set_tuple(value)
        elif type(value) == int:
            self.__set_int(value)
        elif isinstance(value, self.__class__):
            self.__set_instance(value)
        elif type(value) in (str,unicode):
            self.__set_str(value)
        else:
            self.val = self._DEFAULT
            self.string = u''

    def set_from_xml_str(self, value):
        """
        This method sets the type instance based on the untranslated string 
        (obtained e.g. from XML).
        """
        if self._E2IMAP.has_key(value):
            self.val = self._E2IMAP[value]
            self.string = u''
        else:
            self.val = self._CUSTOM
            self.string = value

    def xml_str(self):
        """
        Return the untranslated string (e.g. suitable for XML) corresponding 
        to the type.
        """
        if self.val == self._CUSTOM:
            return self.string
        else:
            return self._I2EMAP[self.val]

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.val, self.string)

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.val, self.string = data

    def __str__(self):
        if self.val == self._CUSTOM:
            return self.string
        else:
            return self._I2SMAP.get(self.val, _('Unknown'))

    def __int__(self):
        return self.val

    def get_map(self):
        return self._I2SMAP

    def get_standard_names(self):
        """
        Return the list of localized names for all standard types.
        """
        return [s for (i, s) in self._I2SMAP.items()
                if (i != self._CUSTOM) and s.strip()]

    def get_standard_xml(self):
        """
        Return the list of XML (english) names for all standard types.
        """
        return [s for (i, s) in self._I2EMAP.items()
                if (i != self._CUSTOM) and s.strip()]

    def is_custom(self):
        return self.val == self._CUSTOM

    def is_default(self):
        return self.val == self._DEFAULT

    def get_custom(self):
        return self._CUSTOM
    
    def __cmp__(self, value):
        if type(value) == int:
            return cmp(self.val, value)
        elif type(value) in (str, unicode):
            if self.val == self._CUSTOM:
                return cmp(self.string, value)
            else:
                return cmp(self._I2SMAP.get(self.val), value)
        elif type(value) == tuple:
            return cmp((self.val, self.string), value)
        else:
            if value.val == self._CUSTOM:
                return cmp(self.string, value.string)
            else:
                return cmp(self.val, value.val)
