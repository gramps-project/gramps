#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017       Nick Hall
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

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
import gramps.gen.lib as lib


def __default(obj):
    obj_dict = {"_class": obj.__class__.__name__}
    if isinstance(obj, lib.GrampsType):
        obj_dict["string"] = getattr(obj, "string")
    if isinstance(obj, lib.Date):
        if obj.is_empty() and not obj.text:
            return None
    for key, value in obj.__dict__.items():
        if not key.startswith("_"):
            obj_dict[key] = value
    for key, value in obj.__class__.__dict__.items():
        if isinstance(value, property):
            if key != "year":
                obj_dict[key] = getattr(obj, key)
    return obj_dict


def __object_hook(obj_dict):
    obj = getattr(lib, obj_dict["_class"])()
    for key, value in obj_dict.items():
        if key != "_class":
            if key in ("dateval", "rect") and value is not None:
                value = tuple(value)
            if key == "ranges":
                value = [tuple(item) for item in value]
            setattr(obj, key, value)
    if obj_dict["_class"] == "Date":
        if obj.is_empty() and not obj.text:
            return None
    return obj


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
