#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017,2024       Nick Hall
# Copyright (C) 2024            Doug Blank
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
Serialization utilities for Gramps.
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import json
import pickle

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
import gramps.gen.lib as lib


def __object_hook(obj_dict):
    _class = obj_dict.pop("_class")
    cls = lib.__dict__[_class]
    obj = cls.__new__(cls)
    obj.set_object_state(obj_dict)
    return obj


def __default(obj):
    return obj.get_object_state()


def to_json(obj):
    """
    Encode a Gramps object in JSON format.

    :param obj: The object to be serialized.
    :type obj: object
    :returns: A JSON string.
    :rtype: str
    """
    return json.dumps(obj, default=__default, ensure_ascii=False)


def from_json(data):
    """
    Decode JSON data into a Gramps object hierarchy.

    :param data: The JSON string to be unserialized.
    :type data: str
    :returns: A Gramps object.
    :rtype: object
    """
    return json.loads(data, object_hook=__object_hook)


def to_dict(obj):
    """
    Convert a Gramps object into a struct.

    :param obj: The object to be serialized.
    :type obj: object
    :returns: A dictionary.
    :rtype: dict
    """
    return json.loads(to_json(obj))


def from_dict(dict):
    """
    Convert a dictionary into a Gramps object.

    :param struct: The dictionary to be unserialized.
    :type struct: dict
    :returns: A Gramps object.
    :rtype: object
    """
    return from_json(json.dumps(struct))


class BlobSerializer:
    """
    Serializer for blob data
    """

    data_field = "blob_data"

    @staticmethod
    def data_to_object(obj_class, data):
        return obj_class.create(data)

    @staticmethod
    def string_to_object(obj_class, string):
        return obj_class.create(pickle.loads(string))

    @staticmethod
    def string_to_data(string):
        return pickle.loads(string)

    @staticmethod
    def object_to_string(obj):
        return pickle.dumps(obj.serialize())

    @staticmethod
    def data_to_string(data):
        return pickle.dumps(data)

    @staticmethod
    def get_item(data, position):
        return data[position]


class JSONSerializer:
    """
    Serializer for JSON data
    """

    data_field = "json_data"

    @staticmethod
    def data_to_object(obj_class, data):
        return from_dict(data)

    @staticmethod
    def string_to_object(obj_class, string):
        return from_json(string)

    @staticmethod
    def string_to_data(string):
        return json.loads(string)

    @staticmethod
    def object_to_string(obj):
        return to_json(obj)

    @staticmethod
    def data_to_string(data):
        return json.dumps(data)

    @staticmethod
    def get_item(data, key):
        return data[key]
