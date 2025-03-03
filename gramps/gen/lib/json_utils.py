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

from __future__ import annotations
import json
import orjson

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------

import gramps.gen.lib as lib


NoneType = type(None)


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
                # Data is actually a Gramps object
                self.update(object_to_data(data))

    def __str__(self):
        if "_object" not in self:
            self["_object"] = data_to_object(self)
        return str(self["_object"])

    def __getattr__(self, key):
        if key.startswith("_"):
            raise AttributeError(
                "this method cannot be used to access hidden attributes"
            )

        if key in self:
            value = self[key]
            if isinstance(value, dict):
                return DataDict(value)
            elif isinstance(value, list):
                return DataList(value)
            else:
                return value
        else:
            # Some method or attribute not available
            # otherwise. Cache it:
            self["_object"] = data_to_object(self)
            # And return the attr from the object:
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

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index >= len(self):
            raise StopIteration

        result = self[self.index]
        self.index += 1
        return result

    def __add__(self, value):
        return DataList([x for x in self] + [x for x in value])

    def __radd__(self, value):
        return DataList([x for x in self] + [x for x in value])


def remove_object(data):
    """
    Remove _object, if any, from dicts.
    """
    if isinstance(data, dict):
        return {
            key: remove_object(value) for key, value in data.items() if key != "_object"
        }
    elif isinstance(data, (list, tuple)):
        return [remove_object(item) for item in data]
    else:
        return data


def convert_state_to_object(obj_dict):
    _class = obj_dict.pop("_class")
    cls = lib.__dict__[_class]
    obj = cls.__new__(cls)
    obj.set_object_state(obj_dict)
    return obj


def convert_object_to_state(obj):
    return obj.get_object_state()


def string_to_data(string: str | bytes) -> DataDict:
    """
    Convert a JSON string into its data representation.
    """
    return DataDict(orjson.loads(string))


def string_to_dict(string: str | bytes) -> dict:
    """
    Convert a JSON string into its dict representation.
    """
    return orjson.loads(string)


def dict_to_string(dict: dict) -> str:
    """
    Convert a dict into its JSON string representation.
    """
    return orjson.dumps(dict).decode()


def object_to_dict(obj):
    """
    Convert any Gramps lib object into a dict representation.
    """
    if isinstance(obj, (float, int, str, NoneType)):
        return obj

    elif isinstance(obj, (list, tuple)):
        return [object_to_dict(item) for item in obj]

    state = obj.get_object_state()
    return {k: object_to_dict(v) for k, v in state.items()}


def object_to_data(obj):
    """
    Convert any Gramps lib object or other value into
    its dict or list representation or value, respectively.
    """
    if isinstance(obj, (float, int, str, NoneType)):
        return obj

    elif isinstance(obj, (list, tuple)):
        return DataList([object_to_data(item) for item in obj])

    state = obj.get_object_state()
    data = {k: object_to_data(v) for k, v in state.items()}
    # Stash the object in case we need it later:
    data["_object"] = obj
    return DataDict(data)


def data_to_object(data):
    """
    Convert any object dict representation to a Gramps lib object
    or other value.
    """
    if isinstance(data, dict):
        if "_object" in data:
            return data["_object"]

        data = {k: data_to_object(v) for k, v in data.items()}
        return convert_state_to_object(data)

    elif isinstance(data, (list, tuple)):
        return [data_to_object(item) for item in data]

    return data


def object_to_string(obj: object) -> str:
    """
    Convert any Gramps object into a JSON string/bytes.
    """
    return orjson.dumps(obj, default=convert_object_to_state).decode()


def data_to_string(data: DataDict) -> str:
    """
    Convert a DataDict into a string.
    """
    return orjson.dumps(remove_object(data)).decode()


def string_to_object(string: str | bytes):
    """
    Convert a JSON string/bytes into a Gramps lib object.
    """
    return data_to_object(orjson.loads(string))
