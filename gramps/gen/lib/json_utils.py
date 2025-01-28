#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017,2024       Nick Hall
# Copyright (C) 2024-2025       Doug Blank
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

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------

import orjson

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------

import gramps.gen.lib as lib


NoneType = type(None)


def convert_state_to_object(obj_dict):
    _class = obj_dict.pop("_class")
    cls = lib.__dict__[_class]
    obj = cls.__new__(cls)
    obj.set_object_state(obj_dict)
    return obj


def convert_object_to_state(obj):
    return obj.get_object_state()


def string_to_data(string):
    return DataDict(orjson.loads(string))

def string_to_dict(string):
    return orjson.loads(string)

def dict_to_string(dict):
    return orjson.dumps(dict)

def object_to_data(obj):
    """
    Convert any Gramps lib object into its dict representation.
    """
    if isinstance(obj, (float, int, str, NoneType)):
        return obj

    elif isinstance(obj, (list, tuple)):
        return [object_to_data(item) for item in obj]

    state = convert_object_to_state(obj)
    return {k: object_to_data(v) for k, v in state.items()}


def data_to_object(data):
    """
    Convert any object dict representation to a Gramps lib object.

    """
    if isinstance(data, dict):
        if "_object" in data:
            return data["_object"]

        data = {k: data_to_object(v) for k, v in data.items()}
        return convert_state_to_object(data)

    elif isinstance(data, (list, tuple)):
        return [data_to_object(item) for item in data]

    return data


def object_to_string(obj: object) -> str | bytes:
    """
    Convert any Gramps object into a JSON string/bytes.
    """
    return orjson.dumps(object_to_data(obj))

def data_to_string(data):
    return orjson.dumps(data)


def string_to_object(string: str | bytes):
    """
    Convert a JSON string/bytes into a Gramps lib object.
    """
    return data_to_object(orjson.loads(string))


class DataDict(dict):
    """
    A wrapper around a data dict that also provides an
    object interface.
    """

    def __init__(self, data=None):
        """
        Wrap a data dict (raw data) or object
        with an attribute API. If data is an
        object, we use it to get the attributes.
        """
        if isinstance(data, dict):
            super().__init__(data)
        else:
            super().__init__()
            if data:
                self["_object"] = data

    def __str__(self):
        if "_object" not in self:
            self["_object"] = from_dict(self)
        return str(self["_object"])

    def __getattr__(self, key):
        if key.startswith("_"):
            raise AttributeError(
                "this method cannot be used to access hidden attributes"
            )

        if "_object" in self:
            return getattr(self["_object"], key)
        elif key in self:
            value = self[key]
            if isinstance(value, dict):
                return DataDict(value)
            elif isinstance(value, list):
                return DataList(value)
            else:
                return value
        else:
            self["_object"] = from_dict(self)
            return getattr(self["_object"], key)


class DataList(list):
    """
    A wrapper around a data list.
    """

    def __getitem__(self, position):
        value = super().__getitem__(position)
        if isinstance(value, dict):
            return DataDict(value)
        elif isinstance(value, list):
            return DataList(value)
        else:
            return value


from_json = string_to_object
to_json = object_to_string
from_dict = data_to_object
to_dict = object_to_data
json_loads = orjson.loads
json_dumps = orjson.dumps
