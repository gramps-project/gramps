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
import logging

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
import gramps.gen.lib as lib

LOG = logging.getLogger(".serialize")


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

    :param dict: The dictionary to be unserialized.
    :type dict: dict
    :returns: A Gramps object.
    :rtype: object
    """
    return from_json(json.dumps(dict))


class BlobSerializer:
    """
    Serializer for blob data

    In this serializer, data is a nested array,
    and string is pickled bytes.
    """

    data_field = "blob_data"
    metadata_field = "value"

    @staticmethod
    def data_to_object(obj_class, data):
        LOG.debug("blob, data_to_object: %s(%r)", obj_class, data[0] if data else data)
        return obj_class.create(data)

    @staticmethod
    def string_to_object(obj_class, bytes):
        LOG.debug("blob, string_to_object: %r...", bytes[:35])
        return obj_class.create(pickle.loads(bytes))

    @staticmethod
    def string_to_data(bytes):
        LOG.debug("blob, string_to_object: %r...", bytes[:35])
        return pickle.loads(bytes)

    @staticmethod
    def object_to_string(obj):
        LOG.debug("blob, object_to_string: %s...", obj)
        return pickle.dumps(obj.serialize())

    @staticmethod
    def data_to_string(data):
        LOG.debug("blob, data_to_string: %s...", data[0] if data else data)
        return pickle.dumps(data)

    @staticmethod
    def metadata_to_object(blob):
        return pickle.loads(blob)

    @staticmethod
    def object_to_metadata(value):
        return pickle.dumps(value)


class JSONSerializer:
    """
    Serializer for JSON data.

    In this serializer, data is a dict,
    and string is a JSON string.
    """

    data_field = "json_data"
    metadata_field = "json_data"

    @staticmethod
    def data_to_object(obj_class, data):
        LOG.debug(
            "json, data_to_object: {'_class': %r, ...}",
            data["_class"] if (data and "_class" in data) else data,
        )
        return from_dict(data)

    @staticmethod
    def string_to_object(obj_class, string):
        LOG.debug("json, string_to_object: %r...", string[:65])
        return from_json(string)

    @staticmethod
    def string_to_data(string):
        LOG.debug("json, string_to_data: %r...", string[:65])
        return json.loads(string)

    @staticmethod
    def object_to_string(obj):
        LOG.debug("json, object_to_string: %s...", obj)
        return to_json(obj)

    @staticmethod
    def data_to_string(data):
        LOG.debug(
            "json, data_to_string: {'_class': %r, ...}",
            data["_class"] if (data and "_class" in data) else data,
        )
        return json.dumps(data)

    @staticmethod
    def metadata_to_object(string):
        doc = json.loads(string)
        type_name = doc["type"]
        if type_name in ("int", "str", "list"):
            return doc["value"]
        elif type_name == "set":
            return set(doc["value"])
        elif type_name == "tuple":
            return tuple(doc["value"])
        elif type_name == "dict":
            return doc["value"]
        elif type_name == "Researcher":
            return from_dict(doc["value"])
        else:
            return doc["value"]

    @staticmethod
    def object_to_metadata(value):
        type_name = type(value).__name__
        if type_name in ("set", "tuple"):
            value = list(value)
        elif type_name == "Researcher":
            value = to_dict(value)
        elif type_name not in ("int", "str", "list"):
            value = json.loads(to_json(value))
        data = {
            "type": type_name,
            "value": value,
        }
        return json.dumps(data)
