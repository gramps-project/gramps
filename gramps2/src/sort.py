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

def by_last_name(first, second):
    """Sort routine for comparing two last names. If last names are equal,
    uses the given name and suffix"""
    name1 = first.PrimaryName
    name2 = second.PrimaryName

    fsn = name1.Surname.upper()
    ssn = name2.Surname.upper()

    if fsn == ssn :
        ffn = name1.FirstName.upper()
        sfn = name2.FirstName.upper()
        if ffn == sfn :
            return cmp(name1.Suffix.upper(), name2.Suffix.upper())
        else :
            return cmp(ffn, sfn)
    else :
        return cmp(fsn, ssn)

def by_birthdate(first, second) :
    """Sort routine for comparing two people by birth dates. If the birth dates
    are equal, sorts by name"""
    date1 = first.get_birth().get_date_object()
    date2 = second.get_birth().get_date_object()
    val = Date.compare_dates(date1,date2)
    if val == 0:
        return by_last_name(first,second)
    return val
