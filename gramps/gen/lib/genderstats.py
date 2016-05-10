#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
# Copyright (C) 2012       Benny Malengier
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

"""
Gender statistics kept in Gramps database.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .person import Person

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class GenderStats:
    """
    Class for keeping track of statistics related to Given Name vs. Gender.

    This allows the tracking of the liklihood of a person's given name
    indicating the gender of the person.
    """
    def __init__(self, stats=None):
        if stats is None:
            self.stats = {}
        else:
            # Current use of GenderStats is such that a shallow copy suffices.
            self.stats = stats

    def save_stats(self):
        return self.stats

    def clear_stats(self):
        self.stats = {}
        return self.stats

    def name_stats(self, name):
        if name in self.stats:
            return self.stats[name]
        return (0, 0, 0)

    def count_name(self, name, gender):
        """
        Count a given name under gender in the gender stats.
        """
        keyname = _get_key_from_name(name)
        if not keyname:
            return

        self._set_stats(keyname, gender)

    def count_person(self, person, undo=0):
        if not person:
            return
        # Let the Person do their own counting later

        keyname = _get_key(person)
        if not keyname:
            return

        gender = person.get_gender()
        self._set_stats(keyname, gender, undo)

    def _set_stats(self, keyname, gender, undo=0):
        (male, female, unknown) = self.name_stats(keyname)
        if not undo:
            increment = 1
        else:
            increment = -1

        if gender == Person.MALE:
            male += increment
            if male < 0:
                male = 0
        elif gender == Person.FEMALE:
            female += increment
            if female < 0:
                female = 0
        elif gender == Person.UNKNOWN:
            unknown += increment
            if unknown < 0:
                unknown = 0

        self.stats[keyname] = (male, female, unknown)

    def uncount_person(self, person):
        return self.count_person(person, undo=1)

    def guess_gender(self, name):
        name = _get_key_from_name(name)
        if not name or name not in self.stats:
            return Person.UNKNOWN

        (male, female, unknown) = self.stats[name]
        if unknown == 0:
            if male and not female:
                return Person.MALE
            if female and not male:
                return Person.FEMALE

        if male > (2 * female):
            return Person.MALE

        if female > (2 * male):
            return Person.FEMALE

        return Person.UNKNOWN

def _get_key(person):
    name = person.get_primary_name().get_first_name()
    return _get_key_from_name(name)

def _get_key_from_name(name):
    return name.split(' ')[0].replace('?', '')
