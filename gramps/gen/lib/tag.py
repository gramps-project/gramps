#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010      Nick Hall
# Copyright (C) 2013      Doug Blank <doug.blank@gmail.com>
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
Tag object for Gramps.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .tableobj import TableObject
from .handle import Handle

#-------------------------------------------------------------------------
#
# Tag class
#
#-------------------------------------------------------------------------
class Tag(TableObject):
    """
    The Tag record is used to store information about a tag that can be
    attached to a primary object.
    """

    def __init__(self, source=None):
        """
        Create a new Tag instance, copying from the source if present.

        :param source: A tag used to initialize the new tag
        :type source: Tag
        """

        TableObject.__init__(self, source)

        if source:
            self.__name = source.__name
            self.__color = source.__color
            self.__priority = source.__priority
        else:
            self.__name = ""
            self.__color = "#000000000000" # Black
            self.__priority = 0

    def serialize(self):
        """
        Convert the data held in the event to a Python tuple that
        represents all the data elements.

        This method is used to convert the object into a form that can easily
        be saved to a database.

        These elements may be primitive Python types (string, integers),
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objects or
        lists), the database is responsible for converting the data into
        a form that it can use.

        :returns: Returns a python tuple containing the data that should
                  be considered persistent.
        :rtype: tuple
        """
        return (self.handle,
                self.__name,
                self.__color,
                self.__priority,
                self.change)

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in a Tag structure.

        :param data: tuple containing the persistent data associated with the
                     object
        :type data: tuple
        """
        (self.handle,
         self.__name,
         self.__color,
         self.__priority,
         self.change) = data
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.__name]

    def is_empty(self):
        """
        Return True if the Tag is an empty object (no values set).

        :returns: True if the Tag is empty
        :rtype: bool
        """
        return self.__name != ""

    def are_equal(self, other):
        """
        Return True if the passed Tag is equivalent to the current Tag.

        :param other: Tag to compare against
        :type other: Tag
        :returns: True if the Tags are equal
        :rtype: bool
        """
        if other is None:
            other = Tag()

        if self.__name != other.__name or \
           self.__color != other.__color or \
           self.__priority != other.__priority:
            return False
        return True

    def set_name(self, name):
        """
        Set the name of the Tag to the passed string.

        :param name: Name to assign to the Tag
        :type name: str
        """
        self.__name = name

    def get_name(self):
        """
        Return the name of the Tag.

        :returns: Name of the Tag
        :rtype: str
        """
        return self.__name
    name = property(get_name, set_name, None,
                    'Returns or sets name of the tag')

    def set_color(self, color):
        """
        Set the color of the Tag to the passed string.

        The string is of the format #rrrrggggbbbb.

        :param color: Color to assign to the Tag
        :type color: str
        """
        self.__color = color

    def get_color(self) :
        """
        Return the color of the Tag.

        :returns: Returns the color of the Tag
        :rtype: str
        """
        return self.__color
    color = property(get_color, set_color, None,
                     'Returns or sets color of the tag')

    def set_priority(self, priority):
        """
        Set the priority of the Tag to the passed integer.

        The lower the value the higher the priority.

        :param priority: Priority to assign to the Tag
        :type priority: int
        """
        self.__priority = priority

    def get_priority(self) :
        """
        Return the priority of the Tag.

        :returns: Returns the priority of the Tag
        :rtype: int
        """
        return self.__priority

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.

        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {"_class": "Tag",
                "handle": Handle("Tag", self.handle),
                "name": self.__name,
                "color": self.__color,
                "priority": self.__priority,
                "change": self.change}

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = Tag()
        return (Handle.from_struct(struct.get("handle", default.handle)),
                struct.get("name", default.name),
                struct.get("color", default.color),
                struct.get("priority", default.priority),
                struct.get("change", default.change))

    priority = property(get_priority, set_priority, None,
                     'Returns or sets priority of the tag')
