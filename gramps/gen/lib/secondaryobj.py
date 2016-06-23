#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
Secondary Object class for Gramps.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from abc import abstractmethod

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .baseobj import BaseObject

#-------------------------------------------------------------------------
#
# Secondary Object class
#
#-------------------------------------------------------------------------
class SecondaryObject(BaseObject):
    """
    The SecondaryObject is the base class for all secondary objects in the
    database.
    """

    @abstractmethod
    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """

    @abstractmethod
    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """

    @abstractmethod
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
        """

    @abstractmethod
    def from_struct(self, struct):
        """
        Given a struct data representation, return an object of this type.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns an object of this type.
        """

    def is_equal(self, source):
        return self.serialize() == source.serialize()

    def is_equivalent(self, other):
        """
        Return if this object is equivalent to other.

        Should be overwritten by objects that inherit from this class.
        """
        pass

    @classmethod
    def get_labels(cls, _):
        """
        Return labels.
        """
        return {}

    def get_label(self, field, _):
        """
        Get the associated label given a field name of this object.
        """
        chain = field.split(".")
        path = self
        for part in chain[:-1]:
            if hasattr(path, part):
                path = getattr(path, part)
            else:
                path = path[int(part)]
        labels = path.get_labels(_)
        if chain[-1] in labels:
            return labels[chain[-1]]
        else:
            raise Exception("%s has no such label: '%s'" % (self, field))
