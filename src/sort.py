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

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_last_name2(first, second) :

    name1 = first[0]
    name2 = second[0]

    if name1.getSurname() == name2.getSurname() :
        if name1.getFirstName() == name2.getFirstName() :
            return cmp(name1.getSuffix(), name2.getSuffix())
        else :
            return cmp(name1.getFirstName(), name2.getFirstName())
    else :
        return cmp(name1.getSurname(), name2.getSurname())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_last_name(first, second) :

    name1 = first.getPrimaryName()
    name2 = second.getPrimaryName()

    if name1.getSurname() == name2.getSurname() :
        if name1.getFirstName() == name2.getFirstName() :
            return cmp(name1.getSuffix(), name2.getSuffix())
        else :
            return cmp(name1.getFirstName(), name2.getFirstName())
    else :
        return cmp(name1.getSurname(), name2.getSurname())

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
def by_last_name_backwards2(first, second) :
    return by_last_name2(second,first)

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

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_deathdate(first, second) :

    date1 = first.getDeath().getDateObj()
    date2 = second.getDeath().getDateObj()
    val = compare_dates(date1,date2)
    if val == 0:
        return by_last_name(first,second)
    return val

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_birthdate_backwards(first, second) :
    return by_birthdate(second,first)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_deathdate_backwards(first, second) :
    return by_deathdate(second,first)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_birthdate2(first, second) :

    date1 = first[1].getBirth().getDateObj()
    date2 = second[1].getBirth().getDateObj()
    val = compare_dates(date1,date2)
    if val == 0:
        return by_last_name2(first,second)
    return val

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_deathdate2(first, second) :

    date1 = first[1].getDeath().getDateObj()
    date2 = second[1].getDeath().getDateObj()
    val = compare_dates(date1,date2)
    if val == 0:
        return by_last_name2(first,second)
    return val

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_birthdate_backwards2(first, second) :
    return by_birthdate2(second,first)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_deathdate_backwards2(first, second) :
    return by_deathdate2(second,first)

    
