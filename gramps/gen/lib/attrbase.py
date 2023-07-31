#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
AttributeRootBase class for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .attribute import Attribute, AttributeRoot
from .srcattribute import SrcAttribute
from .const import IDENTICAL, EQUAL


# -------------------------------------------------------------------------
#
# AttributeRootBase class
#
# -------------------------------------------------------------------------
class AttributeRootBase:
    """
    Base class for attribute-aware objects.
    """

    _CLASS = AttributeRoot

    def __init__(self, source=None):
        """
        Initialize a AttributeBase.

        If the source is not None, then object is initialized from values of
        the source object.

        :param source: Object used to initialize the new object
        :type source: AttributeBase
        """
        if source:
            self.attribute_list = [
                self._CLASS(attribute) for attribute in source.attribute_list
            ]
        else:
            self.attribute_list = []

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return [attr.serialize() for attr in self.attribute_list]

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.attribute_list = [self._CLASS().unserialize(item) for item in data]

    def add_attribute(self, attribute):
        """
        Add the :class:`~.attribute.Attribute` instance to the object's list of
        attributes.

        :param attribute: :class:`~.attribute.Attribute` instance to add.
        :type attribute: :class:`~.attribute.Attribute`
        """
        assert not isinstance(attribute, str)
        self.attribute_list.append(attribute)

    def remove_attribute(self, attribute):
        """
        Remove the specified :class:`~.attribute.Attribute` instance from the
        attribute list.

        If the instance does not exist in the list, the operation has
        no effect.

        :param attribute: :class:`~.attribute.Attribute` instance to remove
                          from the list
        :type attribute: :class:`~.attribute.Attribute`

        :returns: True if the attribute was removed, False if it was not in the
                  list.
        :rtype: bool
        """
        if attribute in self.attribute_list:
            self.attribute_list.remove(attribute)
            return True
        else:
            return False

    def get_attribute_list(self):
        """
        Return the list of :class:`~.attribute.Attribute` instances associated
        with the object.

        :returns: Returns the list of :class:`~.attribute.Attribute` instances.
        :rtype: list
        """
        return self.attribute_list

    def set_attribute_list(self, attribute_list):
        """
        Assign the passed list to the Person's list of
        :class:`~.attribute.Attribute` instances.

        :param attribute_list: List of :class:`~.attribute.Attribute` instances
                               to ba associated with the Person
        :type attribute_list: list
        """
        self.attribute_list = attribute_list

    def _merge_attribute_list(self, acquisition):
        """
        Merge the list of attributes from acquisition with our own.

        :param acquisition: the attribute list of this object will be merged
                            with the current attribute list.
        :type acquisition: AttributeBase
        """
        attr_list = self.attribute_list[:]
        for addendum in acquisition.get_attribute_list():
            for attr in attr_list:
                equi = attr.is_equivalent(addendum)
                if equi == IDENTICAL:
                    break
                elif equi == EQUAL:
                    attr.merge(addendum)
                    break
            else:
                self.attribute_list.append(addendum)


class AttributeBase(AttributeRootBase):
    _CLASS = Attribute


class SrcAttributeBase(AttributeRootBase):
    _CLASS = SrcAttribute
