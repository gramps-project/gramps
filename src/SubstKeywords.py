#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
Provides the SubstKeywords class that will replace keywords in a passed
string with informatin about the person. For sample:

foo = SubstKeywords(person)
print foo.replace('$n was born on $b.')

Will return a value such as:

Mary Smith was born on 3/28/1923.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#------------------------------------------------------------------------
#
# python classes
#
#------------------------------------------------------------------------
import string

#------------------------------------------------------------------------
#
# SubstKeywords
#
#------------------------------------------------------------------------
class SubstKeywords:
    """
    Produces an object that will substitute information about a person
    into a passed string.

    $n -> Name - FirstName LastName
    $N -> Name - LastName, FirstName
    $i -> GRAMPS ID
    $b -> Date of birth
    $B -> Place of birth
    $d -> Date of death
    $D -> Place of death
    $s -> Preferred spouse's name - FirstName LastName
    $S -> Preferred spouse's name - LastName, FirstName
    $m -> Date of preferred marriage
    $M -> Place of preferred marriage
    """
    
    def __init__(self,database,person_id):
        """Creates a new object and associates a person with it."""

        person = database.find_person_from_id(person_id)
        self.n = person.get_primary_name().get_regular_name()
        self.N = person.get_primary_name().get_name()
        self.b = ""
        self.B = ""
        self.d = ""
        self.D = ""
        self.s = ""
        self.S = ""
        self.m = ""
        self.M = ""
        
        birth_id = person.get_birth_id()
        if birth_id:
            birth = database.find_event_from_id(birth_id)
            self.b = birth.get_date()
            bplace_id = birth.get_place_id()
            if bplace_id:
                self.B = database.find_place_from_id(bplace_id).get_title()
        death_id = person.get_death_id()
        if death_id:
            death = database.find_event_from_id(death_id)
            self.d = death.get_date()
            dplace_id = death.get_place_id()
            if dplace_id:
                self.D = database.find_place_from_id(dplace_id).get_title()
        self.i = str(person_id)

        if person.get_family_id_list():
            f_id = person.get_family_id_list()[0]
            f = database.find_family_from_id(f_id)
            father_id = f.get_father_id()
            mother_id = f.get_mother_id
            if father_id == person_id:
                if mother_id:
                    mother = database.find_person_from_id(mother_id)
                    self.s = mother.get_primary_name().get_regular_name()
                    self.S = mother.get_primary_name().get_name()
            else:
                if father_id:
                    father = database.find_person_from_id(father_id)
                    self.s = father.get_primary_name().get_regular_name()
                    self.S = father.get_primary_name().get_name()
            for e_id in f.get_event_list():
                if not e_id:
                    continue
                e = database.find_event_from_id(e_id)
                if e.get_name() == 'Marriage':
                    self.m = e.get_date()
                    mplace_id = e.get_place_id()
                    if mplace_id:
                        self.M = database.find_place_from_id(mplace_id).get_title()

    def replace(self,line):
        """Returns a new line of text with the substitutions performed."""
        
        line = string.replace(line,"$n",self.n)
        line = string.replace(line,"$N",self.N)
        line = string.replace(line,"$b",self.b)
        line = string.replace(line,"$B",self.B)
        line = string.replace(line,"$d",self.d)
        line = string.replace(line,"$D",self.D)
        line = string.replace(line,"$i",self.i)
        line = string.replace(line,"$S",self.S)
        line = string.replace(line,"$s",self.s)
        line = string.replace(line,"$m",self.m)
        line = string.replace(line,"$M",self.M)
        return string.replace(line,"$$",'$')
