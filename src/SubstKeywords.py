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
    
    def __init__(self,person):
        """Creates a new object and associates a person with it."""

        self.n = person.getPrimaryName().getRegularName()
        self.N = person.getPrimaryName().getName()
        self.b = person.getBirth().getDate()
        self.d = person.getDeath().getDate()
        self.B = person.getBirth().getPlaceName()
        self.D = person.getDeath().getPlaceName()
        self.i = str(person.getId())

        if len(person.getFamilyList()) > 0:
            f = person.getFamilyList()[0]
            if f.getFather() == person:
                if f.getMother():
                    self.s = f.getMother().getPrimaryName().getRegularName()
                    self.S = f.getMother().getPrimaryName().getName()
                else:
                    self.s = ""
                    self.S = ""
            else:
                if f.getFather():
                    self.s = f.getFather().getPrimaryName().getRegularName()
                    self.S = f.getFather().getPrimaryName().getName()
                else:
                    self.s = ""
                    self.S = ""
                
            self.m = ''
            self.M = ''
            for e in f.getEventList():
                if e.getName == 'Marriage':
                    self.m = e.getDate()
                    self.M = e.getPlaceName()
        else:
            self.s = ""
            self.S = ""
            self.m = ""
            self.M = ""

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
