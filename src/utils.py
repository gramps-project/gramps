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

import gtk

_modifiedFlag  = 0

#-------------------------------------------------------------------------
#
# Sets the modified flag, which is used to determine if the database
# needs to be saved.  Anytime a routine modifies data, it should call
# this routine.
#
#-------------------------------------------------------------------------
def modified():
    global _modifiedFlag
    _modifiedFlag = 1

#-------------------------------------------------------------------------
#
# Clears the modified flag.  Should be called after data is saved.
#
#-------------------------------------------------------------------------
def clearModified():
    global _modifiedFlag
    _modifiedFlag = 0

#-------------------------------------------------------------------------
#
# Returns the modified flag
#
#-------------------------------------------------------------------------
def wasModified():
    return _modifiedFlag

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's name, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------
def phonebook_name(person):
    if person:
        return person.getPrimaryName().getName()
    else:
        return ""

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's name, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------
def phonebook_from_name(name,alt):
    if alt:
        return "%s *" % name.getName()
    else:
        return name.getName()

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's name, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------
def normal_name(person):
    if person:
        return person.getPrimaryName().getRegularName()
    else:
        return ""

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def destroy_passed_object(obj):
    obj.destroy()
    while gtk.events_pending():
        gtk.mainiteration()

#-------------------------------------------------------------------------
#
# Get around python's interpretation of commas/periods in floating
# point numbers
#
#-------------------------------------------------------------------------
import string

if string.find("%.3f" % 1.2, ",") == -1:
    _use_comma = 0
else:
    _use_comma = 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def txt2fl(st):
    if _use_comma:
        return string.atof(string.replace(st,'.',','))
    else:
        return string.atof(string.replace(st,',','.'))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def fl2txt(fmt,val):
    return string.replace(fmt % val, ',', '.')
