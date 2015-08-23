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
Option class representing a list of filters.
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from . import EnumeratedListOption

#-------------------------------------------------------------------------
#
# FilterOption class
#
#-------------------------------------------------------------------------
class FilterOption(EnumeratedListOption):
    """
    This class describes an option that provides a list of person filters.
    Each possible value represents one of the possible filters.
    """
    def __init__(self, label, value):
        """
        :param label: A friendly label to be applied to this option.
            Example: "Filter"
        :type label: string
        :param value: A default value for the option.
            Example: 1
        :type label: int
        :return: nothing
        """
        EnumeratedListOption.__init__(self, label, value)
        self.__filters = []

    def set_filters(self, filter_list):
        """
        Set the list of filters available to be chosen from.

        :param filter_list: An array of person filters.
        :type filter_list: array
        :return: nothing
        """
        curval = self.get_value()
        items = [(value, filt.get_name())
                    for value, filt in enumerate(filter_list)]

        self.__filters = filter_list
        self.clear()
        self.set_items( items )

        self.set_value(curval)

    def get_filter(self):
        """
        Return the currently selected filter object.

        :return: A filter object.
        """
        return self.__filters[self.get_value()]
