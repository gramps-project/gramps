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
from TransUtils import gettext as _
_UNKNOWN = _('Unknown')

#-------------------------------------------------------------------------
#
# GrampsTypeMeta class
#
#-------------------------------------------------------------------------
class GrampsTypeMeta(type):
    """Metaclass for :class:`~gen.lib.grampstype.GrampsType`.
    
    Create the class-specific integer/string maps.
    
    """
    def __init__(cls, name, bases, namespace):

        # Helper function to create the maps        
        def init_map(data, key_col, data_col, blacklist=None):
            """Initialize the map, building a new map from the specified columns."""
            if blacklist:
                return dict([(item[key_col], item[data_col]) 
                                for item in data if not item[0] in blacklist])
            else:
                return dict([(item[key_col], item[data_col]) for item in data])
                
        # Call superclass initialization        
        type.__init__(cls, name, bases, namespace)
        
        # Build the integer/string maps
        cls._I2SMAP = init_map(cls._DATAMAP, 0, 1, cls._BLACKLIST)
        cls._S2IMAP = init_map(cls._DATAMAP, 1, 0, cls._BLACKLIST)
        cls._I2EMAP = init_map(cls._DATAMAP, 0, 2, cls._BLACKLIST)
        cls._E2IMAP = init_map(cls._DATAMAP, 2, 0, cls._BLACKLIST)        
      
        
#-------------------------------------------------------------------------
#
# GrampsType class
#
#-------------------------------------------------------------------------
class GrampsType(object):
    """Base class for all Gramps object types.
        
    :cvar _DATAMAP: (list) 3-tuple like (index, localized_string, english_string).
    :cvar _BLACKLIST: 
       List of indices to ignore (obsolete/retired entries).
       (gramps policy is never to delete type values, or reuse the name (TOKEN)
       of any specific type value)
    :cvar POS_<x>: (int) 
      Position of <x> attribute in the serialized format of
      an instance.

    :attention: The POS_<x> class variables reflect the serialized object, they
      have to be updated in case the data structure or the L{serialize} method
      changes!
    
    :cvar _CUSTOM:  (int) a custom type object
    :cvar _DEFAULT: (int) the default type, used on creation
    
    :attribute value: (int) Returns or sets integer value
    :attribute string: (str) Returns or sets string value

    """
    (POS_VALUE, POS_STRING) = range(2)
    
    _CUSTOM = 0
    _DEFAULT = 0

    _DATAMAP = []
    _BLACKLIST = None
    
    __metaclass__ = GrampsTypeMeta
    __slots__ = ('__value','__string')

    def __getstate__(self):
        return {'__value': self.__value,'__string': self.__string}
    def __setstate__(self,dict_):
        self.__value = dict_['__value']
        self.__string = dict_['__string']
    
    def __init__(self, value=None):
        """
        Create a new type, initialize the value from one of several possible 
        states.
        """
        self.set(value)

    def __set_tuple(self, value):
        v, s = self._DEFAULT, u''
        if value:
            v = value[0]
            if len(value) > 1:
                s = value[1]
        self.__value = v
        self.__string = s

    def __set_int(self, value):
        self.__value = value
        self.__string = u''

    def __set_instance(self, value):
        self.__value = value.value
        self.__string = value.string

    def __set_str(self, value):
        self.__value = self._S2IMAP.get(value, self._CUSTOM)
        if self.__value == self._CUSTOM:
            self.__string = value
        else:
            self.__string = u''

    def set(self, value):
        if isinstance(value, tuple):
            self.__set_tuple(value)
        elif isinstance(value, int):
            self.__set_int(value)
        elif isinstance(value, self.__class__):
            self.__set_instance(value)
        elif isinstance(value, basestring):
            self.__set_str(value)
        else:
            self.__value = self._DEFAULT
            self.__string = u''

    def set_from_xml_str(self, value):
        """
        This method sets the type instance based on the untranslated string 
        (obtained e.g. from XML).
        """
        if value in self._E2IMAP:
            self.__value = self._E2IMAP[value]
            self.__string = u''
            if self.__value == self._CUSTOM:
                #if the custom event is actually 'Custom' then we should save it
                # with that string value. That is, 'Custom' is in _E2IMAP
                self.__string = value
        else:
            self.__value = self._CUSTOM
            self.__string = value

    def xml_str(self):
        """
        Return the untranslated string (e.g. suitable for XML) corresponding 
        to the type.
        """
        if self.__value == self._CUSTOM:
            return self.__string
        else:
            return self._I2EMAP[self.__value]

    def serialize(self):
        """Convert the object to a serialized tuple of data. """
        return (self.__value, self.__string)

    def unserialize(self, data):
        """Convert a serialized tuple of data to an object."""
        self.__value, self.__string = data
        return self

    def __str__(self):
        if self.__value == self._CUSTOM:
            return self.__string
        else:
            return self._I2SMAP.get(self.__value, _UNKNOWN)

    def __int__(self):
        return self.__value

    def get_map(self):
        return self._I2SMAP

    def get_standard_names(self):
        """Return the list of localized names for all standard types."""
        return [s for (i, s) in self._I2SMAP.items()
                if (i != self._CUSTOM) and s.strip()]

    def get_standard_xml(self):
        """Return the list of XML (english) names for all standard types."""
        return [s for (i, s) in self._I2EMAP.items()
                if (i != self._CUSTOM) and s.strip()]

    def is_custom(self):
        return self.__value == self._CUSTOM

    def is_default(self):
        return self.__value == self._DEFAULT

    def get_custom(self):
        return self._CUSTOM
    
    def __cmp__(self, value):
        if isinstance(value, int):
            return cmp(self.__value, value)
        elif isinstance(value, basestring):
            if self.__value == self._CUSTOM:
                return cmp(self.__string, value)
            else:
                return cmp(self._I2SMAP.get(self.__value), value)
        elif isinstance(value, tuple):
            return cmp((self.__value, self.__string), value)
        else:
            if value.value == self._CUSTOM:
                return cmp(self.__string, value.string)
            else:
                return cmp(self.__value, value.value)

    value = property(__int__, __set_int, None, "Returns or sets integer value")
    string = property(__str__, __set_str, None, "Returns or sets string value")
