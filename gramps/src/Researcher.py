#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

import string

class Researcher:
    def __init__(self):
        self.name = ""
        self.addr = ""
        self.city = ""
        self.state = ""
        self.country = ""
        self.postal = ""
        self.phone = ""
        self.email = ""

    def getName(self):
        return self.name

    def getAddress(self):
        return self.addr

    def getCity(self):
        return self.city

    def getState(self):
        return self.state

    def getCountry(self):
        return self.country

    def getPostalCode(self):
        return self.postal

    def getPhone(self):
        return self.phone

    def getEmail(self):
        return self.email

    def set(self,name,addr,city,state,country,postal,phone,email):
        self.name = string.strip(name)
        self.addr = string.strip(addr)
        self.city = string.strip(city)
        self.state = string.strip(state)
        self.country = string.strip(country)
        self.postal = string.strip(postal)
        self.phone = string.strip(phone)
        self.email = string.strip(email)
    
    

