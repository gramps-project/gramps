#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import string

#-------------------------------------------------------------------------
#
# constants 
#
#-------------------------------------------------------------------------
IGNORE = "HW~!@#$%^&*()_+=-`[]\|;:'/?.,<>\" \t\f\v"
TABLE  = string.maketrans('ABCDEFGIJKLMNOPQRSTUVXYZ', 
                          '012301202245501262301202')

#-------------------------------------------------------------------------
#
# soundex - returns the soundex value for the specified string
#
#-------------------------------------------------------------------------
def soundex(strval):
    "Return the soundex value to a string argument."

    strval = strval.upper().strip()
    if not strval:
	return "Z000"
    strval = strval.encode('iso-8859-1')
    str2 = strval[0]
    strval = strval.translate(TABLE, IGNORE)
    if not strval:
        return "Z000"
    prev = strval[0]
    for x in strval[1:]:
	if x != prev and x != "0":
	    	str2 = str2 + x
	prev = x
    # pad with zeros
    str2 = str2+"0000"
    return str2[:4]

#-------------------------------------------------------------------------
#
# compare - compares the soundex values of two strings
#
#-------------------------------------------------------------------------
def compare(str1, str2):
    "1 if strings are close. 0 otherwise."
    return soundex(str1) == soundex(str2)
