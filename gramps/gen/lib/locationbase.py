#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
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
LocationBase class for Gramps.
"""

#-------------------------------------------------------------------------
#
# LocationBase class
#
#-------------------------------------------------------------------------
class LocationBase(object):
    """
    Base class for all things Address.
    """

    def __init__(self, source=None):
        """
        Create a LocationBase object, copying from the source object if it
        exists.
        """
        if source:
            self.street = source.street
            self.locality = source.locality
            self.city = source.city
            self.county = source.county
            self.state = source.state
            self.country = source.country
            self.postal = source.postal
            self.phone = source.phone
        else:
            self.street = ""
            self.locality = ""
            self.city = ""
            self.county = ""
            self.state = ""
            self.country = ""
            self.postal = ""
            self.phone = ""

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.street, self.locality, self.city, self.county, self.state,
                self.country, self.postal, self.phone)

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
        return {
            "_class": "LocationBase",
            "street": self.street,
            "locality": self.locality,
            "city": self.city,
            "county": self.county,
            "state": self.state,
            "country": self.country,
            "postal": self.postal,
            "phone": self.phone
        }

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = LocationBase()
        return (struct.get("street", default.street),
                struct.get("locality", default.locality),
                struct.get("city", default.city),
                struct.get("county", default.county),
                struct.get("state", default.state),
                struct.get("country", default.country),
                struct.get("postal", default.postal),
                struct.get("phone", default.phone))

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.street, self.locality, self.city, self.county, self.state,
         self.country, self.postal, self.phone) = data
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.street, self.locality, self.city, self.county,
                self.state, self.country, self.postal, self.phone]

    def set_street(self, val):
        """Set the street portion of the Location."""
        self.street = val

    def get_street(self):
        """Return the street portion of the Location."""
        return self.street

    def set_locality(self, val):
        """Set the locality portion of the Location."""
        self.locality = val

    def get_locality(self):
        """Return the locality portion of the Location."""
        return self.locality

    def set_city(self, data):
        """Set the city name of the LocationBase object."""
        self.city = data

    def get_city(self):
        """Return the city name of the LocationBase object."""
        return self.city

    def set_postal_code(self, data):
        """Set the postal code of the LocationBase object."""
        self.postal = data

    def get_postal_code(self):
        """Return the postal code of the LocationBase object."""
        return self.postal

    def set_phone(self, data):
        """Set the phone number of the LocationBase object."""
        self.phone = data

    def get_phone(self):
        """Return the phone number of the LocationBase object."""
        return self.phone

    def set_state(self, data):
        """Set the state name of the LocationBase object."""
        self.state = data

    def get_state(self):
        """Return the state name of the LocationBase object."""
        return self.state

    def set_country(self, data):
        """Set the country name of the LocationBase object."""
        self.country = data

    def get_country(self):
        """Return the country name of the LocationBase object."""
        return self.country

    def set_county(self, data):
        """Set the county name of the LocationBase object."""
        self.county = data

    def get_county(self):
        """Return the county name of the LocationBase object."""
        return self.county
