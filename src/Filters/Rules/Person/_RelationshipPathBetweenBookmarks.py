#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

# $Id: _RelationshipPathBetween.py 6529 2006-05-03 06:29:07Z rshura $

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
try:
    set()
except NameError:
    from sets import Set as set
#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
#
# RelationshipPathBetween
#
#-------------------------------------------------------------------------
class RelationshipPathBetweenBookmarks(Rule):
    """
    Rule that matches the ancestors of bookmarked individuals back to 
    common ancestors, producing the relationship path(s) between the
    bookmarked individuals.
    """

    name        = _("Relationship path between <persons>")
    category    = _('Relationship filters')
    description = _("Matches the ancestors of bookmarked individuals "
                    "back to common ancestors, producing the relationship "
                    "path(s) between bookmarked persons.")

    def prepare(self,db):
        self.db = db
        self.map = {}
        bookmarks = self.db.get_bookmarks()
        if len(bookmarks) == 0:
            self.apply = lambda db,p : False
        else:
            self.bookmarks = set(bookmarks)
        try:
            self.init_list()
        except:
            pass

    def reset(self):
        self.map = {}

    #
    # Returns a name, given a handle.
    def hnm(self,handle):
        try:
            person = self.db.get_person_from_handle(handle)
        except:
            return None
        if person == None:
            return None
        try:
            name = person.get_primary_name().get_name()
        except:
            return None
        return name

    #
    # Given a group of individuals, returns all of their parents.
    # The value keyed by the individual handles is the path from
    # the original person up, like generation[gfather]= [son,father,gfather]
    def parents(self,generation):
        if len(generation) < 1: return None
        prev_generation = {}
        for handle in generation:
            try:
                 person = self.db.get_person_from_handle(handle)
                 if person == None:
                     continue
                 fam_id = person.get_main_parents_family_handle()
                 family = self.db.get_family_from_handle(fam_id)
                 if family == None:
                     continue
                 fhandle = family.get_father_handle()
                 mhandle = family.get_mother_handle()
                 if fhandle:
                     prev_generation[fhandle] = generation[handle] + [fhandle]
                 if mhandle:
                     prev_generation[mhandle] = generation[handle] + [mhandle]
            except:
                pass
        return prev_generation

    #
    # Given two handles for individuals, a list of all individuals
    # in the relationship path between the two.
    def rel_path_for_two(self,handle1,handle2):
        #print "rel_path_for_two (", handle1, self.hnm(handle1), ",", handle2, self.hnm(handle2), ")"
        rel_path = {}				# Result map
        gmap1 = { handle1 : [ handle1 ] }	# Key is ancestor, value is the path
        gmap2 = { handle2 : [ handle2 ] }
        map1 = {}
        map2 = {}
        overlap = set( {} )
	for rank in range(1, 50):		# Limit depth of search
            try:
                 gmap1 = self.parents(gmap1)		# Get previous generation into map
                 gmap2 = self.parents(gmap2)		# Get previous generation into map
                 map1.update(gmap1)			# Merge previous generation into map
                 map2.update(gmap2)			# Merge previous generation into map
                 overlap = set(map1).intersection(set(map2))	# Any common ancestors?
                 if len(overlap) > 0: break		# If so, stop walking through generations
            except: pass
	if len(overlap) < 1:			# No common ancestor found
           rel_path[handle1] = handle1		# Results for degenerate case
           rel_path[handle2] = handle2
           #print "  In rel_path_for_two, returning rel_path = ", rel_path
           return rel_path
        for handle in overlap:			# Handle of common ancestor(s)
            for phandle in map1[handle] + map2[handle]:
                rel_path[phandle] = phandle
        #print "  In rel_path_for_two, returning rel_path = ", rel_path
        return rel_path
    
    def init_list(self):
        Map = {}
        pathmap = {}
        bmarks = {}
	#
        # Handle having fewer than 2 bookmarks, or unrelated people.
        nb = 0
        for handle in self.bookmarks:
            nb = nb + 1
            self.map[handle] = 1
            bmarks[nb] = handle
            #print "bmarks[", nb, "] = ", handle, self.hnm(handle)
        if nb <= 1: return
        #print "bmarks = ", bmarks
	#
        # Go through all bookmarked individuals, and mark all
        # of the people in each of the paths betweent them.
        for i in range(1, nb):
            handle1 = bmarks[i]
            for j in range(i+1, nb+1):
                handle2 = bmarks[j]
                try:
                     pathmap = self.rel_path_for_two(handle1,handle2)	
                     for handle in pathmap:
                         self.map[handle] = 1
                except:
                    pass

    def apply(self,db,person):
        return self.map.has_key(person.handle)

