#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Craig Anderson
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

# $Id:

""" Recursive base classes for reports
"""

from gramps.gen.plug.report import utils as ReportUtils


#------------------------------------------------------------------------
#
# Class DescendPerson
#
#------------------------------------------------------------------------
class DescendPerson(object):
    """ Recursive (down) base class

    The following methods need to be sub-classed as needed:
    . add_person
    . add_person_again (called when a person is seen a second more more times)
    if you don't want to see marriages don't subclass the following two
    . add_marriage
    . add_marriage_again (when a marriage is seen a second more more times)

    Public variables:
    . families_seen a set of all famalies seen.
    . people_seen, a set of all people seen.
    . . useful for knowing if a recursion (kid marring a grandparent)
    . . has happened.
    These can be edited if needed
    . appending can be useful for excluding parts of the tree

    Methods (tools):
    is_direct_descendant - is this person a direct descendant
    . in the example 'kid 1 of mom and other spouse' is NOT
    stop_descending - tells the recursion to stop going down
    . mostly used in add_person_again and add_marriage_again
    has_children - checks to see if the person:
    . is NOT already seen and has hildren.

    Methods (informative)
    . These are the methods that need to be subclassed
    . all methods are given the:
    . . level in (Generagion, Spousal level) tuple
    . . person_handle of the person
    . . family_handle of the family
    add_person - The recursion found a new person in the tree
    add_person_again - found a person again
    . a prolific person or recursion
    add_marriage
    add_marriage_again

    Methods (recursive)
    recurse - The main recursive routine. needs:
    . person_handle
    . g_level - Generation level of this person
    . . if max_gen is 2 and g_level is 1, only this generation
    . . will be displayed.
    . s_level - spousal level - most always 0
    recurse_parents - Thes same as above except:
    . mom (the spouse) is still shown even if s_level == 0
    . . father will have a level of (g_level,0), mother (g_level, 1)
    """
    def __init__(self, dbase, maxgen, maxspouse):
        """ initalized with the
            . database
            . maxgen is the max generations (down) of people to return
            . maxspouse is the level of spouses to recruse through
            . . 0 = no spouses, 1 = spouses of a direct descendant
            . . 2 = spouses of 1, 3 = spouses of 2, etc.  See example below

        """
        # example:  maxgen = 2, maxspouses = 2
        # (1,0) father
        #   (1,1) Mother
        #     (1,2) Mothers other spouse
        #       (2,0) kid 1 of mom and other spouse
        #     (2,0) Kid 1 of father and mother
        #   (1,1) fathers other spouse
        #     (2,0) Kid 1 of father and fathers other spouse
        #       (2,1) Spouse of Kid 1 of father and fathers other spouse

        self.database = dbase

        self.families_seen = set()
        self.people_seen = set()

        self.max_generations = maxgen
        self.max_spouses = maxspouse

        #can we bold direct descendants?
        #bold_now will have only three values
        #0 - no bolding
        #1 - Only bold the first person
        #2 - Bold all direct descendants
        self.__bold_now = 1
        self.__this_slevel = -1
        self.__stop_descending = False

    def is_direct_descendant(self):
        return self.__bold_now != 0 and self.__this_slevel == 0

    def stop_descending(self):
        self.__stop_descending = True

    def has_children(self, person_handle):
        """
        Quickly check to see if this person has children
        still we want to respect the people_seen list
        """

        if not person_handle or person_handle in self.people_seen:
            return False

        person = self.database.get_person_from_handle(person_handle)

        for family_handle in person.get_family_handle_list():
            if family_handle not in self.families_seen:

                family = self.database.get_family_from_handle(family_handle)

                if family.get_child_ref_list():
                    return True
        return False

    def add_person(self, level, person_handle, family_handle):
        """ Makes a person box """
        pass

    def add_person_again(self, level, person_handle, family_handle):
        pass

    def __add_person(self, level, person_handle, family_handle):
        if person_handle is not None and person_handle in self.people_seen:
            self.add_person_again(level, person_handle, family_handle)
        else:
            self.add_person(level, person_handle, family_handle)
        if person_handle is not None:
            self.people_seen.add(person_handle)

    def add_marriage(self, level, person_handle, family_handle):
        """ Makes a marriage box """
        pass

    def add_marriage_again(self, level, person_handle, family_handle):
        """ Makes a marriage box """
        pass

    def __add_marriage(self, level, person_handle, family_handle):
        """ Makes a marriage box """
        if family_handle in self.families_seen:
            self.add_marriage_again(level, person_handle, family_handle)
        else:
            self.add_marriage(level, person_handle, family_handle)
        self.families_seen.add(family_handle)

    def recurse(self, person_handle, g_level, s_level):
        """traverse the descendants recursively
        until either the end of a line is found,
        or until we reach the maximum number of generations
        or we reach the max number of spouses
        that we want to deal with"""

        if not person_handle:
            return
        if g_level > self.max_generations:
            return
        if s_level > 0 and s_level == self.max_spouses:
            return
        #if person_handle in self.people_seen: return

        person = self.database.get_person_from_handle(person_handle)
        family_handles = person.get_family_handle_list()
        if s_level == 0:
            val = family_handles[0] if family_handles else None
            self.__this_slevel = s_level
            self.__add_person((g_level, s_level), person_handle, val)

            if self.__bold_now == 1:
                self.__bold_now = 0

            if self.__stop_descending:
                self.__stop_descending = False
                return

        if s_level == 1:
            tmp_bold = self.__bold_now
            self.__bold_now = 0

        for family_handle in family_handles:
            #Marriage box if the option is there.
            self.__add_marriage((g_level, s_level + 1),
                                person_handle, family_handle)

            if self.__stop_descending:
                self.__stop_descending = False
                continue

            family = self.database.get_family_from_handle(family_handle)

            spouse_handle = ReportUtils.find_spouse(person, family)
            if self.max_spouses > s_level:
                self.__this_slevel = s_level + 1
                self.__add_person((g_level, s_level + 1),
                                  spouse_handle, family_handle)

                if self.__stop_descending:
                    self.__stop_descending = False
                    continue

            mykids = [kid.ref for kid in family.get_child_ref_list()]

            if not self.__stop_descending:
                for child_ref in mykids:
                    self.recurse(child_ref, g_level + 1, 0)
            else:
                self.__stop_descending = False

            if self.max_spouses > s_level:
                #spouse_handle = ReportUtils.find_spouse(person,family)
                self.recurse(spouse_handle, g_level, s_level + 1)

        if s_level == 1:
            self.__bold_now = tmp_bold

    def recurse_parents(self, family_handle, g_level):
        """
        Adds a family.
        ignoring maxspouse, s_level assumed 0 and 1
        father is (g_level,0) and mother is (g_level,1)
        children are (g_level+1,0) and respects maxgen
        """

        if family_handle is None:
            return

        family = self.database.get_family_from_handle(family_handle)
        father_h = family.get_father_handle()
        mother_h = family.get_mother_handle()

        self.__bold_now = 2
        self.__this_slevel = 0
        #if father_h:
        father_b = self.__add_person((g_level, 0), father_h, family_handle)
        #else:
        #    #TODO - should send family_h instead of None?
        #    father_b = self.__add_person((g_level, 0), None, family_h)
        #self.people_seen.add(father_h)

        family_b = self.__add_marriage((g_level, 1), father_h, family_handle)

        self.__bold_now = 0
        self.__this_slevel = 1
        mother_b = self.__add_person((g_level, 1), mother_h, family_handle)

        self.__bold_now = 2
        for child_ref in family.get_child_ref_list():
            self.recurse(child_ref.ref, g_level + 1, 0)

        self.__bold_now = 0

        return (father_b, family_b, mother_b)

    def recurse_if(self, person_handle, g_level):
        """
        Quickly check to see if we want to continue recursion
        we still we want to respect the FamiliesSeen list
        """

        person = self.database.get_person_from_handle(person_handle)

        show = False
        myfams = person.get_family_handle_list()
        if len(myfams) > 1:  # and self.max_spouses > 0
            show = True

        #if self.max_spouses == 0 and not self.has_children(person_handle):
        #    self.people_seen.add(person_handle)
        #    show = False

        if show:
            self.__bold_now = 1
            self.recurse(person_handle, g_level, 0)

#------------
# Jer 29:11: "For I know the plans I have for you," declares the LORD,
# "plans to prosper you and not to harm you, plans to give you hope
# and a future."
