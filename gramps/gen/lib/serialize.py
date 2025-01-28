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

LOG = logging.getLogger(".serialize")

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from .json_utils import (
    from_dict,
    to_dict,
    to_json,
    from_json,
    dict_to_string,
    data_to_object,
    string_to_object,
    string_to_data,
    string_to_dict,
    object_to_string,
    data_to_string,
)


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
        LOG.debug("blob, string_to_data: %r...", bytes[:35])
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
        return data_to_object(data)

    @staticmethod
    def string_to_object(obj_class, string):
        LOG.debug("json, string_to_object: %r...", string[:65])
        return string_to_object(string)

    @staticmethod
    def string_to_data(string):
        LOG.debug("json, string_to_data: %r...", string[:65])
        return string_to_data(string)

    @staticmethod
    def object_to_string(obj):
        LOG.debug("json, object_to_string: %s...", obj)
        return object_to_string(obj)

    @staticmethod
    def data_to_string(data):
        LOG.debug(
            "json, data_to_string: {'_class': %r, ...}",
            data["_class"] if (data and "_class" in data) else data,
        )
        return data_to_string(data)

    @staticmethod
    def metadata_to_object(string):
        doc = string_to_dict(string)
        type_name = doc["type"]
        if type_name == "set":
            return set(doc["value"])
        elif type_name == "tuple":
            return tuple(doc["value"])
        elif type_name == "Researcher":
            return data_to_object(doc["value"])
        else:
            return doc["value"]

    @staticmethod
    def object_to_metadata(value):
        type_name = type(value).__name__
        if type_name in ("set", "tuple"):
            value = list(value)
        elif type_name == "Researcher":
            value = object_to_data(value)

        data = {
            "type": type_name,
            "value": value,
        }
        return dict_to_string(data)
