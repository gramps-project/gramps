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

from gtk import *

import sys

_enable   = 0
oddbg    = (0xffff,0xffff,0xffff)
evenbg   = (0xffff,0xffff,0xffff)
oddfg    = (0,0,0)
evenfg   = (0,0,0)

class ColorList:
    def __init__(self,clist,increment):
        self.index = 0
        self.modval = 2*increment
        self.increment = increment
        self.clist = clist
        self.color_ok = 1
        try:
            self.oddbg = GdkColor(oddbg[0],oddbg[1],oddbg[2])
            self.oddfg = GdkColor(oddfg[0],oddfg[1],oddfg[2])
            self.evenbg = GdkColor(evenbg[0],evenbg[1],evenbg[2])
            self.evenfg = GdkColor(evenfg[0],evenfg[1],evenfg[2])
        except OverflowError:
            self.color_ok = 0
        
    def add(self,list):
        self.clist.append(list)
        if _enable and self.color_ok:
            if self.index % self.modval < self.increment:
                self.clist.set_background(self.index,self.oddbg)
                self.clist.set_foreground(self.index,self.oddfg)
            else:
                self.clist.set_background(self.index,self.evenbg)
                self.clist.set_foreground(self.index,self.evenfg)
        self.index = self.index + 1

    def add_with_data(self,list,data):
        self.add(list)
        self.clist.set_row_data(self.index-1,data)

def set_enable(val):
    global _enable
    
    _enable = val

def get_enable():
    return _enable
