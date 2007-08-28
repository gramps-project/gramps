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
AttributeBase class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _Attribute import Attribute

#-------------------------------------------------------------------------
#
# AttributeBase class
#
#-------------------------------------------------------------------------
class AttributeBase:
    """
    Base class for attribute-aware objects.
    """

    def __init__(self, source=None):
        """
        Initialize a AttributeBase. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: AttributeBase
        """
        if source:
            self.attribute_list = [ Attribute(attribute) \
                                    for attribute in source.attribute_list ]
        else:
            self.attribute_list = []

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return [attr.serialize() for attr in self.attribute_list]

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        self.attribute_list = [Attribute().unserialize(item) for item in data]

    def add_attribute(self, attribute):
        """
        Adds the L{Attribute} instance to the object's list of attributes

        @param attribute: L{Attribute} instance to add.
        @type attribute: L{Attribute}
        """
        assert type(attribute) != unicode
        self.attribute_list.append(attribute)

    def remove_attribute(self, attribute):
        """
        Removes the specified L{Attribute} instance from the attribute list
        If the instance does not exist in the list, the operation has
        no effect.

        @param attribute: L{Attribute} instance to remove from the list
        @type attribute: L{Attribute}

        @return: True if the attribute was removed, False if it was not
            in the list.
        @rtype: bool
        """
        if attribute in self.attribute_list:
            self.attribute_list.remove(attribute)
            return True
        else:
            return False

    def get_attribute_list(self):
        """
        Returns the list of L{Attribute} instances associated with the object.
        
        @returns: Returns the list of L{Attribute} instances.
        @rtype: list
        """
        return self.attribute_list

    def set_attribute_list(self, attribute_list):
        """
        Assigns the passed list to the Person's list of L{Attribute} instances.

        @param attribute_list: List of L{Attribute} instances to ba associated
            with the Person
        @type attribute_list: list
        """
        self.attribute_list = attribute_list
