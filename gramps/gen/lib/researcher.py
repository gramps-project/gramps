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

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .locationbase import LocationBase

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Researcher(LocationBase):
    """Contains the information about the owner of the database."""

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
        return (LocationBase.serialize(self),
                self.name, self.addr, self.email)

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
        """ Set the database owner's email."""
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
        return [getattr(self, value) for value in
                ['name', 'addr', 'locality', 'city', 'state',
                 'country', 'postal', 'phone', 'email']
               ]

    def is_empty(self):
        for attr in ['name', 'addr', 'locality', 'city', 'state',
                     'country', 'postal', 'phone', 'email']:
            if getattr(self, attr) != "":
                return False
        return True
