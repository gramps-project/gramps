#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Researcher informaiton for GRAMPS.
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from locationbase import LocationBase

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class Researcher(LocationBase):
    """Contains the information about the owner of the database"""
    
    def __init__(self, source=None):
        """Initializes the Researcher object,
        copying from the source if provided"""

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
        Converts the object to a serialized tuple of data
        """
        return (LocationBase.serialize(self),
                self.name, self.addr, self.email)

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        (location, self.name, self.addr, self.email) = data
        LocationBase.unserialize(self, location)
        
        return self

    def set_name(self, data):
        """sets the database owner's name"""
        self.name = data
        
    def get_name(self):
        """returns the database owner's name"""
        return self.name

    def set_address(self, data):
        """sets the database owner's address"""
        self.addr = data
        
    def get_address(self):
        """returns the database owner's address"""
        return self.addr

    def set_email(self, data):
        """ sets the database owner's email"""
        self.email = data
        
    def get_email(self):
        """returns the database owner's email"""
        return self.email

    def set_from(self,other_researcher):
        """set all attributes from another instance"""
        self.street = other_researcher.street
        self.city = other_researcher.city
        self.county = other_researcher.county
        self.state = other_researcher.state
        self.country = other_researcher.country
        self.postal = other_researcher.postal
        self.phone = other_researcher.phone

        self.name = other_researcher.name
        self.addr = other_researcher.addr
        self.email =  other_researcher.email
