#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015       Craig Anderson
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

""" Recursive base classes for reports
"""

from gramps.gen.plug.report import utils


# ------------------------------------------------------------------------
#
# Livrecurse base objects only
#
# ------------------------------------------------------------------------
class _PersonSeen:
    """librecurse base boject only
    Keep track of people that have been seen so we can call the correct
    virtual method.
    """

    def __init__(self):
        self.people_seen = set()

    def add_person(self, level, person_handle, family_handle):
        """a person is seen for the first time"""
        pass

    def add_person_again(self, level, person_handle, family_handle):
        """a person is seen again"""
        pass

    def _add_person(self, level, person_handle, family_handle):
        """Which virtual method to call?"""
        if person_handle is not None and person_handle in self.people_seen:
            self.add_person_again(level, person_handle, family_handle)
        else:
            self.add_person(level, person_handle, family_handle)
        if person_handle is not None:
            self.people_seen.add(person_handle)


class _FamilySeen:
    """librecurse base boject only
    Keep track of the famalies that have been seen so we can call the correct
    virtual method.
    """

    def __init__(self):
        self.families_seen = set()

    def add_marriage(self, level, person_handle, family_handle):
        """Makes a marriage"""
        pass

    def add_marriage_again(self, level, person_handle, family_handle):
        """Makes a marriage"""
        pass

    def _add_marriage(self, level, person_handle, family_handle):
        """Makes a marriage"""
        if family_handle in self.families_seen:
            self.add_marriage_again(level, person_handle, family_handle)
        else:
            self.add_marriage(level, person_handle, family_handle)
        self.families_seen.add(family_handle)


class _StopRecurse:
    """A simple class to break out the
    . stop_recursion
    . can_recurse
    . continue_recursion
    methods
    """

    def __init__(self):
        # The default value.  Lets recurse.
        self.__stop_recursion = False

    def stop_recursion(self):
        """Stop Recursion at theis person/family"""
        self.__stop_recursion = True

    def continue_recursion(self):
        """Used to allow recursion again"""
        self.__stop_recursion = False

    def can_recurse(self):
        """Has the upper class told up to stop or can we continue?"""
        return not self.__stop_recursion


# ------------------------------------------------------------------------
#
# Class DescendPerson
#
# ------------------------------------------------------------------------
class DescendPerson(_StopRecurse, _PersonSeen, _FamilySeen):
    """Recursive (down) base class

    The following methods need to be sub-classed as needed:
    . add_person
    . add_person_again (called when a person is seen a second or more times)
    if you don't want to see marriages don't subclass the following two
    . add_marriage
    . add_marriage_again (when a marriage is seen a second or more times)

    returns:
    . add_person, add_person_again, add_marriage, add_marriage_again return
    . . index -> a tuple in the form
    . . . generation, which generational level >= 1
    . . . level
    . . . . 0 = A direct child
    . . . . 1 = spouse of above (0)
    . . . . 2 = spouse of 1
    . . . . 3 = spouse of 2
    . . . . 4 etc
    . . person_handle
    . . family_handle

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
    stop_recursion - tells the recursion to stop going down
    . mostly used in add_person_again and add_marriage_again
    has_children - checks to see if the person:
    . is NOT already seen and has hildren.

    Methods (informative)
    . These are the methods that need to be subclassed
    . all methods are given the:
    . . level in (Generagion, Spousal level) tuple
    . . person_handle of the person
    . . family_handle of the family
    add_marriage
    add_marriage_again

    Virtual methods in PersonSeen
    . add_person - The recursion found a new person in the tree
    . add_person_again - found a person again
    . . a prolific person or recursion

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

    def __init__(self, dbase, maxgen, maxspouse=0):
        _PersonSeen.__init__(self)
        _FamilySeen.__init__(self)
        _StopRecurse.__init__(self)

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

        assert maxgen > 0
        self.max_generations = maxgen

        assert maxspouse >= 0
        self.max_spouses = maxspouse

        # can we bold direct descendants?
        # bold_now will have only three values
        # 0 - no bolding
        # 1 - Only bold the first person
        # 2 - Bold all direct descendants
        self.__bold_now = 1
        self.__this_slevel = -1

    def is_direct_descendant(self):
        """Is this person a direct descendant?
        . Can we bold this perosn and
        . are they a direct child of the father/mother
        . . not a spouse
        """
        return self.__bold_now != 0 and self.__this_slevel == 0

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

    def recurse(self, person_handle, g_level, s_level):
        """traverse the descendants recursively
        until either the end of a line is found,
        or until we reach the maximum number of generations
        or we reach the max number of spouses
        that we want to deal with"""

        if not person_handle:
            return
        if g_level > self.max_generations:
            return  # one generation too many
        if s_level > 0 and s_level == self.max_spouses:
            return
        # if person_handle in self.people_seen: return

        person = self.database.get_person_from_handle(person_handle)
        family_handles = person.get_family_handle_list()
        if s_level == 0:
            val = family_handles[0] if family_handles else None
            self.__this_slevel = s_level
            self._add_person((g_level, s_level), person_handle, val)

            if self.__bold_now == 1:
                self.__bold_now = 0

            if not self.can_recurse():
                self.continue_recursion()
                return

        if s_level == 1:
            tmp_bold = self.__bold_now
            self.__bold_now = 0

        for family_handle in family_handles:
            # Marriage box if the option is there.
            self._add_marriage((g_level, s_level + 1), person_handle, family_handle)

            if not self.can_recurse():
                self.continue_recursion()
                return

            family = self.database.get_family_from_handle(family_handle)

            spouse_handle = utils.find_spouse(person, family)
            if self.max_spouses > s_level:
                self.__this_slevel = s_level + 1
                self._add_person((g_level, s_level + 1), spouse_handle, family_handle)

                if not self.can_recurse:
                    self.continue_recursion()
                    return

            mykids = [kid.ref for kid in family.get_child_ref_list()]

            if self.can_recurse():
                for child_ref in mykids:
                    self.recurse(child_ref, g_level + 1, 0)
            else:
                self.continue_recursion()

            if self.max_spouses > s_level:
                # spouse_handle = utils.find_spouse(person,family)
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
        # if father_h:
        father_b = self._add_person((g_level, 0), father_h, family_handle)
        # else:
        #    #TODO - should send family_h instead of None?
        #    father_b = self._add_person((g_level, 0), None, family_h)
        # self.people_seen.add(father_h)

        family_b = self._add_marriage((g_level, 1), father_h, family_handle)

        self.__bold_now = 0
        self.__this_slevel = 1
        mother_b = self._add_person((g_level, 1), mother_h, family_handle)

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

        # if self.max_spouses == 0 and not self.has_children(person_handle):
        #    self.people_seen.add(person_handle)
        #    show = False

        if show:
            self.__bold_now = 1
            self.recurse(person_handle, g_level, 0)


# ------------------------------------------------------------------------
#
# Class AscendPerson
#
# ------------------------------------------------------------------------
class AscendPerson(_StopRecurse, _PersonSeen):
    """Recursive (up) base class

    The following methods need to be sub-classed as needed:
    . add_person
    . add_person_again (called when a person is seen a second or more times)
    if you don't want to see marriages don't subclass the following
    . add_marriage
    . . index (below) will be the same as the father

    returns:
    . add_person, add_person_again, add_marriage all return
    . . index -> a tuple in the form
    . . . generation, which generational level >= 1
    . . . . Center person is 1
    . . . . Father/Mother is the generational level of the child + 1
    . . . index
    . . . . The center person is 1
    . . . . A father is the  index of the child * 2
    . . . . A mother is the (index of the child * 2) + 1
    . . person_handle  (May be None)
    . . family_handle  (May be None)

    Public variables:
    . people_seen, a set of all people seen.
    . . useful for knowing if a recursion (kid marring a grandparent)
    . . has happened.
    These can be edited if needed
    . people_seen, a set of all people seen.
    . . appending can be useful for excluding parts of the tree
    """

    def __init__(self, dbase, maxgen, maxfill=0):
        _PersonSeen.__init__(self)
        _StopRecurse.__init__(self)

        """ initalized with the
            . database
            . maxgen is the max generations (up) of people to return
            . . maxgen >= 1.  1 will only be the person.
            . maxfill is the max generations of blank (null) people to return
            . . maxfil >= 0.  0 (default) is no empty generations
        """
        self.database = dbase
        assert maxgen > 0
        self.max_generations = maxgen
        assert maxfill >= 0
        self.fill_out = maxfill

    def add_marriage(self, index, indi_handle, fams_handle):
        """Makes a marriage box and add that person into the Canvas."""
        # We are not using add_marriage only and not add_marriage_again
        # because the father will do any _again stuff if needed.
        pass

    def __fill(self, generation, index, mx_fill):
        """
        A skeleton of __iterate as person_handle == family_handle == None
        """
        if generation > self.max_generations or mx_fill == 0:
            # Gone too far.
            return

        self.add_person((generation, index), None, None)

        if not self.can_recurse():
            self.continue_recursion()
            return

        # Recursively call the function. It is okay if the handle is None,
        # since routine handles a handle of None

        self.__fill(generation + 1, index * 2, mx_fill - 1)
        if mx_fill > 1:  # marriage of parents
            self.add_marriage((generation + 1, index * 2), None, None)
            if not self.can_recurse():
                self.continue_recursion()
                return
        self.__fill(generation + 1, (index * 2) + 1, mx_fill - 1)

    def __iterate(self, generation, index, person_handle, full_family_handle):
        """
        Recursive function to walk back all parents of the current person.
        When max_generations are hit, we stop the traversal.

        Code pilfered from gramps/plugins/textreports/ancestorreport.py
        """

        # check for end of the current recursion level. This happens
        # if the person handle is None, or if the max_generations is hit

        if generation > self.max_generations:  # too many generations
            return

        if person_handle is None:  # Ran out of people
            return self.__fill(generation, index, self.fill_out)

        # retrieve the Person instance from the database from the
        # passed person_handle and find the parents from the list.
        # Since this report is for natural parents (birth parents),
        # we have to handle that parents may not
        person = self.database.get_person_from_handle(person_handle)

        # we have a valid person, add him/her
        self._add_person((generation, index), person_handle, full_family_handle)

        # has the user canceled recursion?
        if not self.can_recurse():
            self.continue_recursion()
            return

        # Now recurse on the parents
        family_handle = person.get_main_parents_family_handle()

        if family_handle is not None:
            family = self.database.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
        else:
            father_handle = None
            mother_handle = None

        # Recursively call the function. It is okay if the handle is None,
        self.__iterate(
            generation + 1, index * 2, father_handle, family_handle
        )  # recurse on dad
        if generation < self.max_generations:
            if father_handle is not None:  # Stil winin max_generations
                self.add_marriage(
                    (generation + 1, index * 2), father_handle, family_handle
                )
            elif mother_handle is not None:
                self.add_marriage(
                    (generation + 1, index * 2), mother_handle, family_handle
                )
            elif family_handle is not None:
                self.add_marriage((generation + 1, index * 2), None, family_handle)
            elif self.fill_out > 0:
                self.add_marriage((generation + 1, index * 2), None, None)

            if not self.can_recurse():
                self.continue_recursion()
                return
        self.__iterate(
            generation + 1, (index * 2) + 1, mother_handle, family_handle
        )  # recurse mom

    def recurse(self, person_handle):
        """
        A simple header to make sure we pass in the correct information
        """
        person = self.database.get_person_from_handle(person_handle)
        return self.__iterate(
            1, 1, person_handle, person.get_main_parents_family_handle()
        )


# ------------
# Jer 29:11: "For I know the plans I have for you," declares the LORD,
# "plans to prosper you and not to harm you, plans to give you hope
# and a future."
