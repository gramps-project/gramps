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

class GraphLayout:

    def __init__(self,plist,person):
        self.plist = plist
        self.person = person
        self.v = []
        self.e = []
        self.maxx = 0
        self.maxy = 0

    def max_size(self):
        return (self.maxx,self.maxy)
    
    def layout(self):
        return ([],[])

class DescendLine(GraphLayout):

    def layout(self):
        self.elist = [(0,0)]
        self.space_for(self.person)
        return (self.v,self.e[1:])
    
    def space_for(self,person,level=1.0,pos=1.0):
        last = self.elist[-1]
        self.elist.append((level,pos))
        self.e.append((last[0],last[1],level,pos))
        self.v.append((person,level,pos))
        if level > self.maxx:
            self.maxx = level
        if pos > self.maxy:
            self.maxy = pos
            
        for family in person.get_family_id_list():
            for child in family.get_child_id_list():
                self.space_for(child,level+1.0,pos)
                pos = pos + max(self.depth(child),1)
                if pos > self.maxy:
                    self.maxy = pos
        self.elist.pop()
        
    def depth(self,person,val=0):
        for family in person.get_family_id_list():
            clist = family.get_child_id_list()
            val = val + len(clist)
            for child in clist:
                d=self.depth(child)
                if d > 0:
                   val = val + d - 1 #first child is always on the same
        return val                   #row as the parent, so subtract 1
