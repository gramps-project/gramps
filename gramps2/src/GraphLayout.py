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

class GraphLayout:

    def __init__(self,database,plist,person_id):
        self.database = database
        self.plist = plist
        self.person_id = person_id
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
        self.space_for(self.person_id)
        return (self.v,self.e[1:])
    
    def space_for(self,person_id,level=1.0,pos=1.0):
        last = self.elist[-1]
        self.elist.append((level,pos))
        self.e.append((last[0],last[1],level,pos))
        self.v.append((person_id,level,pos))
        if level > self.maxx:
            self.maxx = level
        if pos > self.maxy:
            self.maxy = pos
            
        person = self.database.try_to_find_person_from_id(person_id)
        for family_id in person.get_family_id_list():
            family = self.database.find_family_from_id(family_id)
            for child_id in family.get_child_id_list():
                self.space_for(child_id,level+1.0,pos)
                pos = pos + max(self.depth(child_id),1)
                if pos > self.maxy:
                    self.maxy = pos
        self.elist.pop()
        
    def depth(self,person_id,val=0):
        person = self.database.try_to_find_person_from_id(person_id)
        for family_id in person.get_family_id_list():
            family = self.database.find_family_from_id(family_id)
            clist = family.get_child_id_list()
            val = val + len(clist)
            for child_id in clist:
                d = self.depth(child_id)
                if d > 0:
                   val = val + d - 1 #first child is always on the same
        return val                   #row as the parent, so subtract 1
