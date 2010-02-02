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
AddressBase class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.address import Address

#-------------------------------------------------------------------------
#
# AddressBase classes
#
#-------------------------------------------------------------------------
class AddressBase(object):
    """
    Base class for address-aware objects.
    """

    def __init__(self, source=None):
        """
        Initialize a AddressBase. 
        
        If the source is not None, then object is initialized from values of 
        the source object.

        :param source: Object used to initialize the new object
        :type source: AddressBase
        """
        self.address_list = map(Address, source.address_list) if source else []

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return [addr.serialize() for addr in self.address_list]

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.address_list = [Address().unserialize(item) for item in data]

    def add_address(self, address):
        """
        Add the :class:`~gen.lib.address.Address` instance to the object's list of addresses.

        :param address: :class:`~gen.lib.address.Address` instance to add to the object's address list
        :type address: list
        """
        self.address_list.append(address)

    def remove_address(self, address):
        """
        Remove the specified :class:`~gen.lib.address.Address` instance from the address list.
        
        If the instance does not exist in the list, the operation has
        no effect.

        :param address: :class:`~gen.lib.address.Address` instance to remove from the list
        :type address: :class:`~gen.lib.address.Address`

        :returns: True if the address was removed, False if it was not in the list.
        :rtype: bool
        """
        if address in self.address_list:
            self.address_list.remove(address)
            return True
        else:
            return False

    def get_address_list(self):
        """
        Return the list of :class:`~gen.lib.address.Address` instances associated with the object.

        :returns: Returns the list of :class:`~gen.lib.address.Address` instances
        :rtype: list
        """
        return self.address_list

    def set_address_list(self, address_list):
        """
        Assign the passed list to the object's list of :class:`~gen.lib.address.Address` instances.
        
        :param address_list: List of :class:`~gen.lib.address.Address` instances to be associated
            with the object
        :type address_list: list
        """
        self.address_list = address_list
