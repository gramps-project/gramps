#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2017,2024  Nick Hall
# Copyright (C) 2024       Doug Blank
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
Base type for all gramps types.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
from functools import singledispatchmethod
from typing import Any

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

_UNKNOWN = _("Unknown")


# -------------------------------------------------------------------------
#
# GrampsTypeMeta
#
# -------------------------------------------------------------------------
class GrampsTypeMeta(type):
    """
    Metaclass for :class:`~.grampstype.GrampsType`.

    Create the class-specific integer/string maps.
    """

    def __init__(cls, name, bases, namespace):
        # Helper function to create the maps
        def init_map(data, key_col, data_col, blacklist=None):
            """
            Initialize the map, building a new map from the specified
            columns.
            """
            if blacklist:
                return {
                    item[key_col]: item[data_col]
                    for item in data
                    if item[0] not in blacklist
                }
            return {item[key_col]: item[data_col] for item in data}

        # Call superclass initialization
        type.__init__(cls, name, bases, namespace)

        # Build the integer/string maps
        if hasattr(cls, "_DATAMAP"):
            cls._I2SMAP = init_map(cls._DATAMAP, 0, 1, cls._BLACKLIST)
            cls._S2IMAP = init_map(cls._DATAMAP, 1, 0, cls._BLACKLIST)
            cls._I2EMAP = init_map(cls._DATAMAP, 0, 2, cls._BLACKLIST)
            cls._E2IMAP = init_map(cls._DATAMAP, 2, 0, cls._BLACKLIST)


# -------------------------------------------------------------------------
#
# GrampsType
#
# -------------------------------------------------------------------------
class GrampsType(metaclass=GrampsTypeMeta):
    """Base class for all Gramps object types.

    :cvar _DATAMAP:
      (list) 3-tuple like (index, localized_string, english_string).
    :cvar _BLACKLIST:
      List of indices to ignore (obsolete/retired entries).
      (gramps policy is never to delete type values, or reuse the name (TOKEN)
      of any specific type value)
    :cvar _CUSTOM:  (int) a custom type object
    :cvar _DEFAULT: (int) the default type, used on creation

    :attribute value: (int) Returns or sets integer value
    :attribute string: (str) Returns or sets string value
    """

    _CUSTOM = 0
    _DEFAULT = 0

    _DATAMAP: list[tuple[int, str, str]] = []
    _BLACKLIST: list[int] | None = None
    _I2SMAP: dict[int, str] = {}
    _S2IMAP: dict[str, int] = {}
    _I2EMAP: dict[int, str] = {}
    _E2IMAP: dict[str, int] = {}
    _MENU: list[list[Any]] = []
    __slots__ = ("__value", "__string")

    def __getstate__(self):
        return {"__value": self.__value, "__string": self.__string}

    def __setstate__(self, dict_):
        self.__value = dict_["__value"]
        if self.__value == self._CUSTOM:
            self.__string = dict_["__string"]
        else:
            self.__string = ""

    def __init__(self, value=None):
        """
        Create a new type, initialize the value from one of several possible
        states.
        """
        self.__value = self._DEFAULT
        self.__string = ""
        if value is not None:
            self.set(value)

    def get_object_state(self):
        """
        Get the current object state as a dictionary.

        We override this method to handle the `value` and `string` properties.
        """
        attr_dict = {"_class": self.__class__.__name__}
        attr_dict["value"] = self.__value
        attr_dict["string"] = self.__string
        return attr_dict

    def set_object_state(self, attr_dict):
        """
        Set the current object state using information provided in the given
        dictionary.

        We override this method to handle the `value` and `string` properties.
        """
        self.__value = attr_dict["value"]
        if self.__value == self._CUSTOM:
            self.__string = attr_dict["string"]
        else:
            self.__string = ""

    @singledispatchmethod
    def set(self, value):
        self.__value = self._DEFAULT
        self.__string = ""

    @set.register
    def __set_dict(self, value: dict):
        "Set the value/string properties from a dict."
        self.__set_tuple((value["value"], value["string"]))

    @set.register
    def __set_tuple(self, value: tuple):
        "Set the value/string properties from a tuple."
        val, strg = self._DEFAULT, ""
        if value:
            val = value[0]
            if len(value) > 1 and val == self._CUSTOM:
                strg = value[1]
        self.__value = val
        self.__string = strg

    @set.register
    def __set_int(self, value: int):
        "Set the value/string properties from an integer."
        self.__value = value
        self.__string = ""

    # This method needs to be registered outside of the class.
    def __set_instance(self, value: GrampsType):
        "Set the value/string properties from another grampstype."
        self.__value = value.value
        if self.__value == self._CUSTOM:
            self.__string = value.string
        else:
            self.__string = ""

    @set.register
    def __set_str(self, value: str):
        "Set the value/string properties from a string."
        self.__value = self._S2IMAP.get(value, self._CUSTOM)
        if self.__value == self._CUSTOM:
            self.__string = value
        else:
            self.__string = ""

    def set_from_xml_str(self, value):
        """
        This method sets the type instance based on the untranslated string
        (obtained e.g. from XML).
        """
        if value in self._E2IMAP:
            self.__value = self._E2IMAP[value]
            self.__string = ""
            if self.__value == self._CUSTOM:
                # if the custom event is actually 'Custom' then we should save it
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
        if self.__value in self._I2EMAP:
            return self._I2EMAP[self.__value]
        return _UNKNOWN

    def serialize(self):
        """Convert the object to a serialized tuple of data."""
        return (self.__value, self.__string)

    @classmethod
    def __get_str(cls, value, string):
        if value == cls._CUSTOM:
            return string
        else:
            return cls._I2SMAP.get(value, _UNKNOWN)

    @classmethod
    def get_str(cls, data):
        """
        Return the translated string corresponding to the type.

        :param data: A dict representation of the type.
        :type data: dict
        :returns: The translated string corresponding to the type.
        :rtype: str
        """
        return cls.__get_str(data.value, data.string)

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        return {
            "type": "object",
            "title": _("Type"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "string": {"type": "string", "title": _("Custom type")},
                "value": {"type": "integer", "title": _("Type code")},
            },
        }

    def unserialize(self, data):
        """Convert a serialized tuple of data to an object."""
        self.__value, self.__string = data
        if self.__value != self._CUSTOM:
            self.__string = ""
        return self

    def __str__(self):
        return type(self).__get_str(self.__value, self.__string)

    def __int__(self):
        return self.__value

    def get_map(self):
        return self._I2SMAP

    def get_standard_names(self):
        """Return the list of localized names for all standard types."""
        return [
            s
            for (i, s) in list(self._I2SMAP.items())
            if (i != self._CUSTOM) and s.strip()
        ]

    def get_standard_xml(self):
        """Return the list of XML (english) names for all standard types."""
        return [
            s
            for (i, s) in list(self._I2EMAP.items())
            if (i != self._CUSTOM) and s.strip()
        ]

    def is_custom(self):
        """Return true if custom type."""
        return self.__value == self._CUSTOM

    def is_default(self):
        """Return true if default type."""
        return self.__value == self._DEFAULT

    def get_custom(self):
        """Return custom type."""
        return self._CUSTOM

    def get_menu(self):
        """Return the list of localized names for the menu."""
        if self._MENU:
            return [[_(i), s] for (i, s) in self._MENU]
        return self._MENU

    def get_menu_standard_xml(self):
        """Return the list of XML (english) names for the menu."""
        return self._MENU

    def __eq__(self, value):
        if isinstance(value, int):
            return self.__value == value
        if isinstance(value, str):
            if self.__value == self._CUSTOM:
                return self.__string == value
            return self._I2SMAP.get(self.__value) == value
        if isinstance(value, tuple):
            if self.__value == self._CUSTOM:
                return (self.__value, self.__string) == value
            return self.__value == value[0]

        if value.value == self._CUSTOM and self.__value == self._CUSTOM:
            return self.__string == value.string
        if self._CUSTOM not in [value.value, self.__value]:
            return self.__value == value.value
        return False

    def __ne__(self, value):
        return not self.__eq__(value)

    value = property(__int__, __set_int, None, "Returns or sets integer value")
    string = property(__str__, __set_str, None, "Returns or sets string value")


GrampsType.set.register(GrampsType, GrampsType._GrampsType__set_instance)  # type: ignore[attr-defined]
