#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2013       Doug Blank <doug.blank@gmail.com>
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
Researcher information for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .locationbase import LocationBase


# -------------------------------------------------------------------------
#
# Researcher
#
# -------------------------------------------------------------------------
class Researcher(LocationBase):
    """
    Contains the information about the owner of the database.
    """

    def __init__(self, source=None):
        """
        Initialize the Researcher object, copying from the source if provided.
        """

        LocationBase.__init__(self, source)
        if source:
            self.name = source.name
            self.addr = source.addr
            self.email = source.email
        else:
            self.name = ""
            self.addr = ""
            self.email = ""

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (LocationBase.serialize(self), self.name, self.addr, self.email)

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (location, self.name, self.addr, self.email) = data
        LocationBase.unserialize(self, location)

        return self

    def set_name(self, data):
        """Set the database owner's name."""
        self.name = data

    def get_name(self):
        """Return the database owner's name."""
        return self.name

    def set_address(self, data):
        """Set the database owner's address."""
        self.addr = data

    def get_address(self):
        """Return the database owner's address."""
        return self.addr

    def set_email(self, data):
        """Set the database owner's email."""
        self.email = data

    def get_email(self):
        """Return the database owner's email."""
        return self.email

    def set_from(self, other_researcher):
        """Set all attributes from another instance."""
        self.street = other_researcher.street
        self.locality = other_researcher.locality
        self.city = other_researcher.city
        self.county = other_researcher.county
        self.state = other_researcher.state
        self.country = other_researcher.country
        self.postal = other_researcher.postal
        self.phone = other_researcher.phone

        self.name = other_researcher.name
        self.addr = other_researcher.addr
        self.email = other_researcher.email

    def get(self):
        """
        Return attributes about the researcher.
        """
        return [
            getattr(self, value)
            for value in [
                "name",
                "addr",
                "locality",
                "city",
                "state",
                "country",
                "postal",
                "phone",
                "email",
            ]
        ]

    def is_empty(self):
        """
        Check and return true if object empty.
        """
        for attr in [
            "name",
            "addr",
            "locality",
            "city",
            "state",
            "country",
            "postal",
            "phone",
            "email",
        ]:
            if getattr(self, attr) != "":
                return False
        return True

    def get_object_state(self):
        """
        Get the current object state as a dictionary.

        By default this returns the public attributes of the instance.  This
        method can be overridden if the class requires other attributes or
        properties to be saved.

        This method is called to provide the information required to serialize
        the object.

        :returns: Returns a dictionary of attributes that represent the state
                  of the object.
        :rtype: dict
        """
        attr_dict = dict(
            (key, value)
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        attr_dict["_class"] = self.__class__.__name__
        return attr_dict

    def set_object_state(self, attr_dict):
        """
        Set the current object state using information provided in the given
        dictionary.

        By default this sets the state of the object assuming that all items in
        the dictionary map to public attributes.  This method can be overridden
        to set the state using custom functionality.  For performance reasons
        it is useful to set a property without calling its setter function.  As
        JSON provides no distinction between tuples and lists, this method can
        also be use to convert lists into tuples where required.

        :param attr_dict: A dictionary of attributes that represent the state of
                          the object.
        :type attr_dict: dict
        """
        self.__dict__.update(attr_dict)
