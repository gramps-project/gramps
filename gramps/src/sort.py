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
import string
import Date

#-------------------------------------------------------------------------
#
# Functions
#
#-------------------------------------------------------------------------

def build_sort_name(n):
    """Builds a name from a RelLib.Name instance that is suitable for
    use as a sort key in a GtkCList. The name is converted to upper case
    to provide for case-insenstive sorting"""
    return "%-25s%-30s%s" % \
           (string.upper(n.Surname),string.upper(n.FirstName),string.upper(n.Suffix))

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

def by_last_name(first, second):
    """Sort routine for comparing two last names. If last names are equal,
    uses the given name and suffix"""
    u = string.upper
    name1 = first.PrimaryName
    name2 = second.PrimaryName

    fsn = u(name1.Surname)
    ssn = u(name2.Surname)

    if fsn == ssn :
        ffn = u(name1.FirstName)
        sfn = u(name2.FirstName)
        if ffn == sfn :
            return cmp(u(name1.Suffix), u(name2.Suffix))
        else :
            return cmp(ffn, sfn)
    else :
        return cmp(fsn, ssn)

def by_birthdate(first, second) :
    """Sort routine for comparing two people by birth dates. If the birth dates
    are equal, sorts by name"""
    date1 = first.getBirth().getDateObj()
    date2 = second.getBirth().getDateObj()
    val = Date.compare_dates(date1,date2)
    if val == 0:
        return by_last_name(first,second)
    return val
