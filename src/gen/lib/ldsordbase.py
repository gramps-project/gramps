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
LdsOrdBase class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.ldsord import LdsOrd

#-------------------------------------------------------------------------
#
# LdsOrdBase classes
#
#-------------------------------------------------------------------------
class LdsOrdBase(object):
    """
    Base class for lds_ord-aware objects.
    """

    def __init__(self, source=None):
        """
        Initialize a LdsOrdBase. 
        
        If the source is not None, then object is initialized from values of 
        the source object.

        :param source: Object used to initialize the new object
        :type source: LdsOrdBase
        """
        
        if source:
            self.lds_ord_list = [ LdsOrd(lds_ord) \
                                    for lds_ord in source.lds_ord_list ]
        else:
            self.lds_ord_list = []

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return [lds_ord.serialize() for lds_ord in self.lds_ord_list]

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object
        """
        self.lds_ord_list = [LdsOrd().unserialize(item) for item in data]

    def add_lds_ord(self, lds_ord):
        """
        Add the :class:`~gen.lib.ldsord.LdsOrd` instance to the object's list of lds_ordes.

        :param lds_ord: :class:`~gen.lib.ldsord.LdsOrd` instance to add to the object's lds_ord list
        :type lds_ord: list
        """
        self.lds_ord_list.append(lds_ord)

    def remove_lds_ord(self, lds_ord):
        """
        Remove the specified :class:`~gen.lib.ldsord.LdsOrd` instance from the lds_ord list.
        
        If the instance does not exist in the list, the operation has no effect.

        :param lds_ord: :class:`~gen.lib.ldsord.LdsOrd` instance to remove from the list
        :type lds_ord: :class:`~gen.lib.ldsord.LdsOrd`

        :returns: True if the lds_ord was removed, False if it was not in the list.
        :rtype: bool
        """
        if lds_ord in self.lds_ord_list:
            self.lds_ord_list.remove(lds_ord)
            return True
        else:
            return False

    def get_lds_ord_list(self):
        """
        Return the list of :class:`~gen.lib.ldsord.LdsOrd` instances associated with the object.

        :returns: Returns the list of :class:`~gen.lib.ldsord.LdsOrd` instances
        :rtype: list
        """
        return self.lds_ord_list

    def set_lds_ord_list(self, lds_ord_list):
        """
        Assign the passed list to the object's list of :class:`~gen.lib.ldsord.LdsOrd` instances.
        
        :param lds_ord_list: List of :class:`~gen.lib.ldsord.LdsOrd` instances to be associated
            with the object
        :type lds_ord_list: list
        """
        self.lds_ord_list = lds_ord_list
