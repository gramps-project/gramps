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


import sets
import Errors
import NameDisplay

class GraphLayout:

    def __init__(self,database,plist,person_handle):
        self.database = database
        self.plist = plist
        self.person_handle = person_handle
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
        try:
            self.space_for(self.person_handle)
        except RuntimeError,msg:
            person = self.database.get_person_from_handle(self.person_handle)
            raise Errors.DatabaseError(
                _("Database error: %s is defined as his or her own ancestor") %
                NameDisplay.displayer.display(person))
        
        return (self.v,self.e[1:])
    
    def space_for(self,person_handle,level=1.0,pos=1.0):

        person = self.database.get_person_from_handle(person_handle)
            
        last = self.elist[-1]
        self.elist.append((level,pos))
        self.e.append((last[0],last[1],level,pos))
        self.v.append((person_handle,level,pos))
        if level > self.maxx:
            self.maxx = level
        if pos > self.maxy:
            self.maxy = pos
            
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            for child_handle in family.get_child_handle_list():
                self.space_for(child_handle,level+1.0,pos)
                pos = pos + max(self.depth(child_handle),1)
                if pos > self.maxy:
                    self.maxy = pos
        self.elist.pop()
        
    def depth(self,person_handle,val=0):
        person = self.database.get_person_from_handle(person_handle)
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            clist = family.get_child_handle_list()
            val = val + len(clist)
            for child_handle in clist:
                d = self.depth(child_handle)
                if d > 0:
                   val = val + d - 1 #first child is always on the same
        return val                   #row as the parent, so subtract 1
