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
    def __init__(self,person):
        self.n = person.getPrimaryName().getRegularName()
        self.N = person.getPrimaryName().getName()
        self.b = person.getBirth().getDate()
        self.d = person.getDeath().getDate()
        self.B = person.getBirth().getPlaceName()
        self.D = person.getDeath().getPlaceName()
        self.i = "%s" % person.getId()

        if len(person.getFamilyList()) > 0:
            f = person.getFamilyList()[0]
            if f.getFather() == person:
                self.s = f.getMother().getPrimaryName().getRegularName()
                self.S = f.getMother().getPrimaryName().getName()
            else:
                self.s = ""
                self.S = ""
            self.m = ''
            self.M = ''
            for e in f.getEventList():
                if e.getName == 'Marriage':
                    self.m = e.getDate()
                    self.M = e.getPlace()
        else:
            self.s = ""
            self.S = ""
            self.m = ""
            self.M = ""

    def replace(self,line):
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
