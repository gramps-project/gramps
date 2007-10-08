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
PrivacyBase Object class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# PrivacyBase Object
#
#-------------------------------------------------------------------------
class PrivacyBase:
    """
    Base class for privacy-aware objects.
    """

    def __init__(self, source=None):
        """
        Initialize a PrivacyBase. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: PrivacyBase
        """
        
        if source:
            self.private = source.private
        else:
            self.private = False

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return self.private

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        self.private = data
        return self

    def set_privacy(self, val):
        """
        Sets or clears the privacy flag of the data

        @param val: value to assign to the privacy flag. True indicates that the
           record is private, False indicates that it is public.
        @type val: bool
        """
        self.private = val

    def get_privacy(self):
        """
        Returns the privacy level of the data. 

        @returns: True indicates that the record is private
        @rtype: bool
        """
        return self.private
