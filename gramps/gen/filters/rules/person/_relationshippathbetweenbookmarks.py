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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
try:
    set()
except NameError:
    from sets import Set as set
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .. import Rule

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

    name = _("Relationship path between bookmarked persons")
    category = _('Relationship filters')
    description = _("Matches the ancestors of bookmarked individuals "
                    "back to common ancestors, producing the relationship "
                    "path(s) between bookmarked persons.")

    def prepare(self, db, user):
        self.db = db
        self.map = set()
        bookmarks = db.get_bookmarks().get()
        if len(bookmarks) == 0:
            self.apply = lambda db,p : False
        else:
            self.bookmarks = set(bookmarks)
        try:
            self.init_list()
        except:
            pass

    def reset(self):
        self.map.clear()

    #
    # Returns a name, given a handle.
    def hnm(self, handle):
        try:
            person = self.db.get_person_from_handle(handle)
        except:
            return None
        if person is None:
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
    def parents(self, generation):
        if len(generation) < 1: return None
        prev_generation = {}
        for handle in generation:
            try:
                person = self.db.get_person_from_handle(handle)
                if person is None:
                    continue
                fam_id = person.get_main_parents_family_handle()
                family = self.db.get_family_from_handle(fam_id)
                if family is None:
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
    def rel_path_for_two(self, handle1, handle2):
        #print "rel_path_for_two (", handle1, self.hnm(handle1), ",", handle2, self.hnm(handle2), ")"
        rel_path = {}                       # Result map
        gmap1 = { handle1 : [ handle1 ] }   # Key is ancestor, value is the path
        gmap2 = { handle2 : [ handle2 ] }
        map1 = {}
        map2 = {}
        overlap = set( {} )
        for rank in range(1, 50):       # Limit depth of search
            try:
                gmap1 = self.parents(gmap1)     # Get previous generation into map
                gmap2 = self.parents(gmap2)     # Get previous generation into map
                map1.update(gmap1)              # Merge previous generation into map
                map2.update(gmap2)              # Merge previous generation into map
                overlap = set(map1).intersection(set(map2)) # Any common ancestors?
                if len(overlap) > 0: break      # If so, stop walking through generations
            except: pass
        if len(overlap) < 1:                # No common ancestor found
            rel_path[handle1] = handle1     # Results for degenerate case
            rel_path[handle2] = handle2
            #print "  In rel_path_for_two, returning rel_path = ", rel_path
            return rel_path
        for handle in overlap:          # Handle of common ancestor(s)
            for phandle in map1[handle] + map2[handle]:
                rel_path[phandle] = phandle
        #print "  In rel_path_for_two, returning rel_path = ", rel_path
        return rel_path

    def init_list(self):
        self.map.update(self.bookmarks)
        if len(self.bookmarks) < 2:
            return
        bmarks = list(self.bookmarks)

        # Go through all bookmarked individuals, and mark all
        # of the people in each of the paths betweent them.
        lb = len(bmarks)
        for i in range(lb-1):
            for j in range(i+1, lb):
                try:
                    pathmap = self.rel_path_for_two(bmarks[i], bmarks[j])
                    self.map.update(pathmap)
                except:
                    pass

    def apply(self,db,person):
        return person.handle in self.map


