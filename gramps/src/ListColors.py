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

_enable   = 0
oddbg    = (0xffff,0xffff,0xffff)
evenbg   = (0xffff,0xffff,0xffff)
oddfg    = (0,0,0)
evenfg   = (0,0,0)
ancestorfg = (0,0,0)

def to_signed(a):
    if a & 0x8000:
        return a - 0x10000
    else:
        return a
    
class ColorList:
    def __init__(self,clist,increment):
        self.index = 0
        self.modval = 2*increment
        self.increment = increment
        self.clist = clist
        self.color_ok = 1
        try:
            cmap = clist.get_colormap()
            self.oddbg = cmap.alloc(to_signed(oddbg[0]),to_signed(oddbg[1]),to_signed(oddbg[2]))
            self.oddfg = cmap.alloc(to_signed(oddfg[0]),to_signed(oddfg[1]),to_signed(oddfg[2]))
            self.evenbg = cmap.alloc(to_signed(evenbg[0]),to_signed(evenbg[1]),to_signed(evenbg[2]))
            self.evenfg = cmap.alloc(to_signed(evenfg[0]),to_signed(evenfg[1]),to_signed(evenfg[2]))
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
