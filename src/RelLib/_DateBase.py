#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
DateBase class for GRAMPS
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _Date import Date

#-------------------------------------------------------------------------
#
# Base classes
#
#-------------------------------------------------------------------------
class DateBase:
    """
    Base class for storing date information.
    """

    def __init__(self,source=None):
        """
        Create a new DateBase, copying from source if not None
        
        @param source: Object used to initialize the new object
        @type source: DateBase
        """
        if source:
            self.date = Date(source.date)
        else:
            self.date = Date()

    def serialize(self):
        if self.date == None or self.date.is_empty():
            date = None
        else:
            date = self.date.serialize()
        return date

    def unserialize(self,data):
        if data == None:
            self.date = Date()
        else:
            self.date = Date().unserialize(data)

    def get_date_object(self):
        """
        Returns the L{Date} object associated with the DateBase.

        @return: Returns a DateBase L{Date} instance.
        @rtype: L{Date}
        """
        if not self.date:
            self.date = Date()
        return self.date

    def set_date_object(self,date):
        """
        Sets the L{Date} object associated with the DateBase.

        @param date: L{Date} instance to be assigned to the DateBase
        @type date: L{Date}
        """
        self.date = date
