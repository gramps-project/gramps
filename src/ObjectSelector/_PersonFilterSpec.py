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

from _FilterSpecBase import FilterSpecBase

class PersonFilterSpec(FilterSpecBase):

    BEFORE = 1
    AFTER = 2
    
    def __init__(self):
        FilterSpecBase.__init__(self)
        
        self._name = None
        self._gender = None
        self._birth_year = None
        self._birth_criteria = self.__class__.BEFORE
        self._death_year = None
        self._death_criteria = self.__class__.BEFORE

    def set_name(self,name):
        self._name = name

    def get_name(self):
        return self._name

    def include_name(self):
        return self._name is not None

    def set_gender(self,gender):
        self._gender = gender

    def get_gender(self):
        return self._gender

    def include_gender(self):
        return self._gender is not None

    def set_birth_year(self,year):
        self._birth_year = str(year)

    def get_birth_year(self):
        return self._birth_year

    def include_birth(self):
        return self._birth_year is not None

    def set_birth_criteria(self,birth_criteria):
        self._birth_criteria = birth_criteria

    def get_birth_criteria(self):
        return self._birth_criteria

    def set_death_year(self,year):
        self._death_year = str(year)

    def get_death_year(self):
        return self._death_year

    def include_death(self):
        return self._death_year is not None

    def set_death_criteria(self,death_criteria):
        self._death_criteria = death_criteria

    def get_death_criteria(self):
        return self._death_criteria

