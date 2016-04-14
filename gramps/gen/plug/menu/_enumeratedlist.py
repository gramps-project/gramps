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
from gramps.gen.const import GRAMPS_LOCALE as glocale
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
        Option.__init__(self, label, value)
        self.__items = []

    def add_item(self, value, description):
        """
        Add an item to the list of possible values.

        :param value: The value that corresponds to this item.
            Example: 5
        :type value: int
        :param description: A description of this value.
            Example: "8.5 x 11"
        :type description: string
        :return: nothing
        """
        self.__items.append((value, description))
        self.emit('options-changed')

    def set_items(self, items):
        """
        Add a list of items to the list of possible values.

        :param items: A list of tuples containing value, description pairs.
            Example: [ (5,"8.5 x 11"), (6,"11 x 17")]
        :type items: array
        :return: nothing
        """
        self.__items = items
        self.emit('options-changed')

    def get_items(self):
        """
        Get all the possible values for this option.

        :return: an array of tuples containing (value,description) pairs.
        """
        return self.__items

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
        else:
            logging.warning(_("Value '%(val)s' not found for option '%(opt)s'") %
                             {'val' : str(value), 'opt' : self.get_label()})
            logging.warning(_("Valid values: ") + str(self.__items))
