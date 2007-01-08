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
from _LocationBase import LocationBase

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class Researcher(LocationBase):
    """Contains the information about the owner of the database"""
    
    def __init__(self):
        """Initializes the Researcher object"""

        LocationBase.__init__(self )
        self.name = ""
        self.addr = ""
        self.email = ""

    def get_name(self):
        """returns the database owner's name"""
        return self.name

    def get_address(self):
        """returns the database owner's address"""
        return self.addr

    def get_email(self):
        """returns the database owner's email"""
        return self.email

    def set(self, name, addr, city, state, country, postal, phone, email):
        """sets the information about the database owner"""
        if name:
            self.name = name.strip()
        if addr:
            self.addr = addr.strip()
        if city:
            self.city = city.strip()
        if state:
            self.state = state.strip()
        if country:
            self.country = country.strip()
        if postal:
            self.postal = postal.strip()
        if phone:
            self.phone = phone.strip()
        if email:
            self.email = email.strip()

