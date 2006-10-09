#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
LocationBase class for GRAMPS
"""

#-------------------------------------------------------------------------
#
# LocationBase class
#
#-------------------------------------------------------------------------
class LocationBase:
    """
    Base class for all things Address.
    """
    
    def __init__(self,source=None):
        """
        Creates a LocationBase object,
        copying from the source object if it exists.
        """
        if source:
            self.street = source.street
            self.city = source.city
            self.county = source.county
            self.state = source.state
            self.country = source.country
            self.postal = source.postal
            self.phone = source.phone
        else:
            self.street = ""
            self.city = ""
            self.county = ""
            self.state = ""
            self.country = ""
            self.postal = ""
            self.phone = ""

    def serialize(self):
        return (self.street, self.city, self.county, self.state,
                self.country, self.postal, self.phone)

    def unserialize(self,data):
        (self.street, self.city, self.county, self.state, self.country,
         self.postal, self.phone) = data
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.city,self.state,self.country,self.postal,self.phone]

    def set_street(self,val):
        """sets the street portion of the Location"""
        self.street = val

    def get_street(self):
        """returns the street portion of the Location"""
        return self.street

    def set_city(self,data):
        """sets the city name of the LocationBase object"""
        self.city = data

    def get_city(self):
        """returns the city name of the LocationBase object"""
        return self.city

    def set_postal_code(self,data):
        """sets the postal code of the LocationBase object"""
        self.postal = data

    def get_postal_code(self):
        """returns the postal code of the LocationBase object"""
        return self.postal

    def set_phone(self,data):
        """sets the phone number of the LocationBase object"""
        self.phone = data

    def get_phone(self):
        """returns the phone number of the LocationBase object"""
        return self.phone

    def set_state(self,data):
        """sets the state name of the LocationBase object"""
        self.state = data

    def get_state(self):
        """returns the state name of the LocationBase object"""
        return self.state

    def set_country(self,data):
        """sets the country name of the LocationBase object"""
        self.country = data

    def get_country(self):
        """returns the country name of the LocationBase object"""
        return self.country

    def set_county(self,data):
        """sets the county name of the LocationBase object"""
        self.county = data

    def get_county(self):
        """returns the county name of the LocationBase object"""
        return self.county
