#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2008       Gary Burton
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
Option class representing a list of people.
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gen.plug.menu import Option


#-------------------------------------------------------------------------
#
# PersonListOption class
#
#-------------------------------------------------------------------------
class PersonListOption(Option):
    """
    This class describes a widget that allows multiple people from the 
    database to be selected.
    """
    def __init__(self, label):
        """
        @param label: A friendly label to be applied to this option.
            Example: "People of interest"
        @type label: string
        @param value: A set of GIDs as initial values for this option.
            Example: "111 222 333 444"
        @type value: string
        @return: nothing
        """
        Option.__init__(self, label, "")
