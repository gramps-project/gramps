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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Option class representing an enumerated list of possible values.
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from . import Option
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging

#-------------------------------------------------------------------------
#
# EnumeratedListOption class
#
#-------------------------------------------------------------------------
class EnumeratedListOption(Option):
    """
    This class describes an option that provides a finite number of values.
    Each possible value is assigned a value and a description.
    """

    __signals__ = { 'options-changed' : None }

    def __init__(self, label, value):
        """
        :param label: A friendly label to be applied to this option.
            Example: "Paper Size"
        :type label: string
        :param value: An initial value for this option.
            Example: 5
        :type value: int
        :return: nothing
        """
        self.ini_value = value
        Option.__init__(self, label, value)
        self.__items = []
        self.__xml_items = []

    def add_item(self, value, description, xml_item=False):
        """
        Add an item to the list of possible values.

        :param value: The value that corresponds to this item.
            Example: 5
        :type value: int
        :param description: A description of this value.
            Example: "8.5 x 11"
        :type description: string
        :param xml_item: allow deferred translation of item description
        :type _xml_item: Boolean
        :return: nothing
        """
        if not xml_item: # localized item description is being passed in
            self.__items.append((value, description))
        else: # English item description is being passed in
            self.__xml_items.append((value, description))
            self.__items.append((value, _(description)))
        self.emit('options-changed')

    def set_items(self, items, xml_items=False):
        """
        Add a list of items to the list of possible values.

        :param items: A list of tuples containing value, description pairs.
            Example: [ (5,"8.5 x 11"), (6,"11 x 17")]
        :type items: array
        :param xml_items: allow deferred translation of item descriptions
        :type _xml_items: Boolean
        :return: nothing
        """
        if not xml_items: # localized item descriptions are being passed in
            self.__items = items
        else: # English item descriptions are being passed in
            self.__xml_items = items
            for (value, description) in items:
                self.__items.append((value, _(description)))
        self.emit('options-changed')

    def get_items(self, xml_items=False):
        """
        Get all the possible values for this option.

        :param xml_items: allow deferred translation of item descriptions
        :type _xml_items: Boolean
        :return: an array of tuples containing (value,description) pairs.
        """
        if not xml_items: # localized item descriptions are wanted
            return self.__items
        return self.__xml_items # English item descriptions are wanted

    def clear(self):
        """
        Clear all possible values from this option.

        :return: nothing.
        """
        self.__items = []
        self.emit('options-changed')

    def set_value(self, value):
        """
        Set the value of this option.

        :param value: A value for this option.
            Example: True
        :type value: The type will depend on the type of option.
        :return: nothing
        """
        if value in (v for v, d in self.__items):
            Option.set_value(self, value)
        elif value == self.ini_value:
            return
        else:
            logging.warning(_("Value '%(val)s' not found for option '%(opt)s'") %
                             {'val' : str(value), 'opt' : self.get_label()})
            logging.warning(_("Valid values: ") + str(self.__items))
