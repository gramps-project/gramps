#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013    Doug Blank <doug.blank@gmail.com>
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

from gramps.gen.constfunc import UNITYPE

class Handle:
    def __init__(self, classname, handle):
        """ Class to hold type and handle of referenced item """
        self.classname = classname
        if handle and not isinstance(handle, UNITYPE):
            handle = handle.decode('utf-8')
        if handle:
            self.handle = handle
        else:
            self.handle = None

    def __repr__(self):
        return "Handle(%s, %s)" % (self.classname, self.handle)

    def __str__(self):
        if self.handle:
            return self.handle
        else:
            return "None"

