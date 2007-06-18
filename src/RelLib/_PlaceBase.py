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
PlaceBase class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# PlaceBase class
#
#-------------------------------------------------------------------------
class PlaceBase:
    """
    Base class for place-aware objects.
    """
    def __init__(self, source=None):
        """
        Initialize a PlaceBase. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: PlaceBase
        """
        if source:
            self.place = source.place
        else:
            self.place = ""

    def set_place_handle(self, place_handle):
        """
        Sets the database handle for L{Place} associated with the object.

        @param place_handle: L{Place} database handle
        @type place_handle: str
        """
        self.place = place_handle

    def get_place_handle(self):
        """
        Returns the database handle of the L{Place} assocated with
        the Event.

        @returns: L{Place} database handle
        @rtype: str
        """
        return self.place 
