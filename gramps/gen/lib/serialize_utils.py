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

import json

try:
    import orjson
except ImportError:
    orjson = None  # type: ignore

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


class JSONConverter:
    # def to_dict(obj):
    @classmethod
    def object_to_data(cls, obj):
        """
        Convert a Gramps object into a struct.

        :param obj: The object to be serialized.
        :type obj: object
        :returns: A dictionary.
        :rtype: dict
        """
        return json.loads(cls.object_to_string(obj))

    # def from_dict(dict):
    @classmethod
    def data_to_object(cls, data):
        """
        Convert a dictionary into a Gramps object.

        :param dict: The dictionary to be unserialized.
        :type dict: dict
        :returns: A Gramps object.
        :rtype: object
        """
        if data is not None and "_object" in data:
            return data["_object"]
        else:
            return cls.string_to_object(json.dumps(data))

    # def to_json(obj):
    @classmethod
    def object_to_string(cls, obj: object) -> str | bytes:
        """
        Encode a Gramps object in JSON format.

        :param obj: The object to be serialized.
        :type obj: object
        :returns: A JSON string.
        :rtype: str
        """
        return json.dumps(obj, default=convert_object_to_state, ensure_ascii=False)

    # def from_json(data):
    @classmethod
    def string_to_object(cls, string: str | bytes):
        """
        Decode JSON data into a Gramps object hierarchy.

        :param data: The JSON string to be unserialized.
        :type data: str
        :returns: A Gramps object.
        :rtype: object
        """
        return json.loads(string, object_hook=convert_state_to_object)


class OrJSONConverter:

    # def to_dict(obj):
    @classmethod
    def object_to_data(cls, obj):
        """
        Convert any Gramps object into its dict representation.
        """
        if isinstance(obj, (float, int, str, NoneType)):
            return obj

        elif isinstance(obj, (list, tuple)):
            return [cls.object_to_data(item) for item in obj]

        state = convert_object_to_state(obj)
        return {k: cls.object_to_data(v) for k, v in state.items()}

    # def from_dict(dict):
    @classmethod
    def data_to_object(cls, data):
        if isinstance(data, dict):
            data = {k: cls.data_to_object(v) for k, v in data.items()}
            return convert_state_to_object(data)

        elif isinstance(data, (list, tuple)):
            return [cls.data_to_object(item) for item in data]

        return data

    # def to_json(obj):
    @classmethod
    def object_to_string(cls, obj: object) -> str | bytes:
        return orjson.dumps(cls.object_to_data(obj))

    # def from_json(data):
    @classmethod
    def string_to_object(cls, string: str | bytes):
        return cls.data_to_object(orjson.loads(string))


if orjson is None:
    from_json = JSONConverter.string_to_object
    to_json = JSONConverter.object_to_string
    from_dict = JSONConverter.data_to_object
    to_dict = JSONConverter.object_to_data
    json_loads = json.loads
    json_dumps = json.dumps
else:
    from_json = OrJSONConverter.string_to_object
    to_json = OrJSONConverter.object_to_string
    from_dict = OrJSONConverter.data_to_object
    to_dict = OrJSONConverter.object_to_data
    json_loads = orjson.loads
    json_dumps = orjson.dumps
