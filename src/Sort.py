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

"""
Provides sorting routines for use in GRAMPS. Since these functions are
intended to provide fast sorting, they tend to bypass access methods,
and directly use class members. For this reason, care needs to be taken
to make sure these remain in sync with the rest of the design.
"""

#-------------------------------------------------------------------------
#
# Imported Modules
#
#-------------------------------------------------------------------------
import Date

#-------------------------------------------------------------------------
#
# Functions
#
#-------------------------------------------------------------------------

_plist = [ 'de', 'van', 'von', 'la', 'di', 'le', 'du' ]

_prefix = {}
for i in _plist:
    _prefix[i] = 1

def build_sort_name(n):
    """Builds a name from a RelLib.Name instance that is suitable for
    use as a sort key in a GtkCList. The name is converted to upper case
    to provide for case-insenstive sorting"""
    if n.Surname:
        return "%-25s%-30s%s" % (n.Surname.upper(),n.FirstName.upper(),n.Suffix.upper())
    else:
        return "@"

def build_sort_date(n):
    """Builds a date from a Date.Date instance that is suitable for
    use as a sort key in a GtkCList. The resultant string is in the format
    of YYYYMMDD. Unknown values are given as all nines, so that the
    appear at the end"""
    y = n.start.year
    if y < 0:
        y = 9999
    m = n.start.month
    if m < 0:
        m = 99
    d = n.start.day
    if d < 0:
        d = 99
    return "%04d%02d%02d" % (y,m,d)

class Sort:
    def __init__(self,database):
        self.database = database


    def by_last_name(self,first_id,second_id):
        """Sort routine for comparing two last names. If last names are equal,
        uses the given name and suffix"""
        first = self.database.find_person_from_id(first_id)
        second = self.database.find_person_from_id(second_id)
        
        name1 = first.get_primary_name()
        name2 = second.get_primary_name()

        fsn = name1.get_surname().upper()
        ssn = name2.get_surname().upper()

        if fsn == ssn :
            ffn = name1.get_first_name().upper()
            sfn = name2.get_first_name().upper()
            if ffn == sfn:
                return cmp(name1.get_suffix().upper(), name2.get_suffix().upper())
            else:
                return cmp(ffn, sfn)
        else:
            return cmp(fsn, ssn)

    def by_birthdate(self,first_id,second_id):
        """Sort routine for comparing two people by birth dates. If the birth dates
        are equal, sorts by name"""
        first = self.database.find_person_from_id(first_id)
        second = self.database.find_person_from_id(second_id)

        birth_id1 = first.get_birth_id()
        if birth_id1:
            date1 = self.database.find_event_from_id(birth_id1).get_date_object()
        else:
            date1 = Date.Date()

        birth_id2 = second.get_birth_id()
        if birth_id2:
            date2 = self.database.find_event_from_id(birth_id2).get_date_object()
        else:
            date2 = Date.Date()

        val = Date.compare_dates(date1,date2)
        if val == 0:
            return self.by_last_name(first_id,second_id)
        return val

    def by_date(self,a_id,b_id):
        """Sort routine for comparing two events by their dates. """
        if not (a_id and b_id):
            return 0
        a = self.database.find_event_from_id(a_id)
        b = self.database.find_event_from_id(b_id)
        return Date.compare_dates(a.get_date_object(),b.get_date_object())
