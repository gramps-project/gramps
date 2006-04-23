#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

"""
Gender statistics kept in GRAMPS database.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _Person import Person

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class GenderStats:
    """
    Class for keeping track of statistics related to Given Name vs.
    Gender. This allows the tracking of the liklihood of a person's
    given name indicating the gender of the person.
    """
    def __init__ (self,stats={}):
        if stats == None:
            self.stats = {}
        else:
            self.stats = stats

    def save_stats(self):
        return self.stats

    def _get_key (self, person):
        name = person.get_primary_name().get_first_name()
        return self._get_key_from_name (name)

    def _get_key_from_name (self, name):
        return name.split (' ')[0].replace ('?', '')

    def name_stats (self, name):
        if self.stats.has_key (name):
            return self.stats[name]
        return (0, 0, 0)

    def count_person (self, person, undo = 0):
        if not person:
            return
        # Let the Person do their own counting later

        name = self._get_key (person)
        if not name:
            return

        gender = person.get_gender()
        (male, female, unknown) = self.name_stats (name)
        if not undo:
            increment = 1
        else:
            increment = -1

        if gender == Person.MALE:
            male += increment
        elif gender == Person.FEMALE:
            female += increment
        elif gender == Person.UNKNOWN:
            unknown += increment

        self.stats[name] = (male, female, unknown)
        return

    def uncount_person (self, person):
        return self.count_person (person, undo = 1)

    def guess_gender (self, name):
        name = self._get_key_from_name (name)
        if not name or not self.stats.has_key (name):
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

