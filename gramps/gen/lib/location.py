#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
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
Location class for Gramps.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .locationbase import LocationBase
from .const import IDENTICAL, DIFFERENT

#-------------------------------------------------------------------------
#
# Location class for Places
#
#-------------------------------------------------------------------------
class Location(SecondaryObject, LocationBase):
    """
    Provide information about a place.

    The data including street, locality, city, county, state, and country.
    Multiple Location objects can represent the same place, since names
    of cities, counties, states, and even countries can change with time.
    """
    
    def __init__(self, source=None):
        """
        Create a Location object, copying from the source object if it exists.
        """
        LocationBase.__init__(self, source)
        if source:
            self.parish = source.parish
        else:
            self.parish = ""

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (LocationBase.serialize(self), self.parish)

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
        return {"_class": "Location",
                "street": self.street, 
                "locality": self.locality, 
                "city": self.city, 
                "county": self.county, 
                "state": self.state,
                "country": self.country, 
                "postal": self.postal, 
                "phone": self.phone,
                "parish": self.parish}

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = Location()
        return ((struct.get("street", default.street),
                 struct.get("locality", default.locality),
                 struct.get("city", default.city),
                 struct.get("country", default.country),
                 struct.get("state", default.state),
                 struct.get("country", default.country),
                 struct.get("postal", default.postal),
                 struct.get("phone", default.phone)), 
                struct.get("parish", default.parish))
        
    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (lbase, self.parish) = data
        LocationBase.unserialize(self, lbase)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.parish] + LocationBase.get_text_data_list(self)

    def is_equivalent(self, other):
        """
        Return if this location is equivalent to other.

        :param other: The location to compare this one to.
        :type other: Location
        :returns: Constant inidicating degree of equivalence.
        :rtype: int
        """
        if self.is_equal(other):
            return IDENTICAL
        else:
            return DIFFERENT

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this location.

        Lost: everything of acquisition.

        :param acquisition: The location to merge with the present location.
        :type acquisition: Location
        """
        pass

    def is_empty(self):
        return not self.street and not self.locality and not self.city and \
               not self.county and not self.state and not self.country and \
               not self.postal and not self.phone
        
    def set_parish(self, data):
        """Set the religious parish name."""
        self.parish = data

    def get_parish(self):
        """Get the religious parish name."""
        return self.parish
