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
AddressBase class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _Address import Address

#-------------------------------------------------------------------------
#
# AddressBase classes
#
#-------------------------------------------------------------------------
class AddressBase:
    """
    Base class for address-aware objects.
    """

    def __init__(self, source=None):
        """
        Initialize a AddressBase. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: AddressBase
        """
        
        if source:
            self.address_list = [ Address(address) \
                                    for address in source.address_list ]
        else:
            self.address_list = []

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return [addr.serialize() for addr in self.address_list]

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        self.address_list = [Address().unserialize(item) for item in data]

    def add_address(self, address):
        """
        Adds the L{Address} instance to the object's list of addresses

        @param address: L{Address} instance to add to the object's address list
        @type address: list
        """
        self.address_list.append(address)

    def remove_address(self, address):
        """
        Removes the specified L{Address} instance from the address list
        If the instance does not exist in the list, the operation has
        no effect.

        @param address: L{Address} instance to remove from the list
        @type address: L{Address}

        @return: True if the address was removed, False if it was not in the list.
        @rtype: bool
        """
        if address in self.address_list:
            self.address_list.remove(address)
            return True
        else:
            return False

    def get_address_list(self):
        """
        Returns the list of L{Address} instances associated with the object

        @return: Returns the list of L{Address} instances
        @rtype: list
        """
        return self.address_list

    def set_address_list(self, address_list):
        """
        Assigns the passed list to the object's list of L{Address} instances.
        @param address_list: List of L{Address} instances to be associated
            with the object
        @type address_list: list
        """
        self.address_list = address_list
