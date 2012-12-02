#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Location class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .tableobj import TableObject

#-------------------------------------------------------------------------
#
# Location class for Places
#
#-------------------------------------------------------------------------
class Location(TableObject):
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
        TableObject.__init__(self, source)
        if source:
            self.parent = source.parent
            self.name = source.name
            self.location_type = source.location_type
            self.lat = source.lat
            self.long = source.long
        else:
            self.parent = None
            self.name = ''
            self.location_type = 1 # Country
            self.lat = ''
            self.long = ''

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.handle,
                self.parent,
                self.name,
                self.location_type,
                self.lat,
                self.long,
                self.change)

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
        return {"street": self.street, 
                "locality": self.locality, 
                "city": self.city, 
                "country": self.county, 
                "state": self.state,
                "country": self.country, 
                "postal": self.postal, 
                "phone": self.phone,
                "parish": self.parish}

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.handle,
         self.parent,
         self.name,
         self.location_type,
         self.lat,
         self.long,
         self.change) = data

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.name, self.lat, self.long]

    def is_empty(self):
        """
        Return True if the Location is an empty object (no values set).

        :returns: True if the Location is empty
        :rtype: bool
        """
        return self.name == ''

    def are_equal(self, other):
        """
        Return True if the passed Tag is equivalent to the current Location.

        :param other: Location to compare against
        :type other: Location
        :returns: True if the Locations are equal
        :rtype: bool
        """
        if other is None:
            other = Location()

        if self.name != other.name or \
           self.parent != other.parent:
            return False
        return True

    def set_parent(self, parent):
        """
        Set the parent of the Location to the passed string.
        """
        self.parent = parent

    def get_parent(self):
        """
        Return the parent of the Location.
        """
        return self.parent

    def set_name(self, name):
        """
        Set the name of the Location to the passed string.
        """
        self.name = name

    def get_name(self):
        """
        Return the name of the Location.
        """
        return self.name

    def set_type(self, location_type):
        """
        Set the type of the Location to the passed integer.
        """
        self.location_type = location_type

    def get_type(self):
        """
        Return the type of the Location.
        """
        return self.location_type

    def set_latitude(self, latitude):
        """
        Set the latitude of the Location object.

        :param latitude: latitude to assign to the Location
        :type latitude: str
        """
        self.lat = latitude

    def get_latitude(self):
        """
        Return the latitude of the Location object.

        :returns: Returns the latitude of the Location
        :rtype: str
        """
        return self.lat

    def set_longitude(self, longitude):
        """
        Set the longitude of the Location object.

        :param longitude: longitude to assign to the Location
        :type longitude: str
        """
        self.long = longitude

    def get_longitude(self):
        """
        Return the longitude of the Location object.

        :returns: Returns the longitude of the Location
        :rtype: str
        """
        return self.long
