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

from RelLib import *
from Date import *
import string

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def build_sort_name(n):
    return "%-25s%-30s%s" % \
           (string.upper(n.Surname),string.upper(n.FirstName),string.upper(n.Suffix))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def build_sort_birth(n):
    y = n.start.year
    if y == -1:
        y = 9999
    m = n.start.month
    if m == -1:
        m = 99
    d = n.start.day
    if d == -1:
        d = 99
    return "%04d%02d%02d" % (y,m,d)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def build_sort_death(n):
    y = n.start.year
    if y == -1:
        y = 9999
    m = n.start.month
    if m == -1:
        m = 99
    d = n.start.day
    if d == -1:
        d = 99
    return "%04d%02d%02d" % (y,m,d)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def fast_name_sort(list):
    nlist = map(build_sort_name,list)
    nlist.sort()
    return map(lambda(key,x): x, nlist)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def reverse_name_sort(list):
    nlist = map(build_sort_name,list)
    nlist.sort()
    nlist.reverse()
    return map(lambda(key,x): x, nlist)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def fast_birth_sort(list):
    nlist = map(build_sort_birth,list)
    nlist.sort()
    return map(lambda(key,x): x, nlist)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def reverse_birth_sort(list):
    nlist = map(build_sort_birth,list)
    nlist.sort()
    nlist.reverse()
    return map(lambda(key,x): x, nlist)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def fast_death_sort(list):
    nlist = map(build_sort_death,list)
    nlist.sort()
    return map(lambda(key,x): x, nlist)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def reverse_death_sort(list):
    nlist = map(build_sort_death,list)
    nlist.sort()
    nlist.reverse()
    return map(lambda(key,x): x, nlist)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_last_name(first, second) :

    name1 = first.getPrimaryName()
    name2 = second.getPrimaryName()

    fsn = string.upper(name1.getSurname())
    ssn = string.upper(name2.getSurname())

    if fsn == ssn :
        ffn = string.upper(name1.getFirstName())
        sfn = string.upper(name2.getFirstName())
        if ffn == sfn :
            return cmp(string.upper(name1.getSuffix()), string.upper(name2.getSuffix()))
        else :
            return cmp(ffn, sfn)
    else :
        return cmp(fsn, ssn)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_last_name_backwards(first, second) :
    return by_last_name(second,first)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_birthdate(first, second) :

    date1 = first.getBirth().getDateObj()
    date2 = second.getBirth().getDateObj()
    val = compare_dates(date1,date2)
    if val == 0:
        return by_last_name(first,second)
    return val
