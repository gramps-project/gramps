#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Nick Hall
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
Option class representing a list of boolean values.
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from . import Option

#-------------------------------------------------------------------------
#
# BooleanListOption class
#
#-------------------------------------------------------------------------
class BooleanListOption(Option):
    """
    This class describes an option that provides a list of check buttons.
    """
    def __init__(self, heading):
        """
        :param heading: A heading for the entire list of check buttons.
            Example: "Event groups"
        :type heading: string
        :return: nothing
        """
        Option.__init__(self, heading, '')
        self.__descriptions = []

    def add_button(self, description, default):
        """
        Add a check button to the list.

        :param description: A description for this check button.
            Example: "Census"
        :type description: string
        :param value: The default for this check button (True or False).
            Example: True
        :type value: int
        :return: nothing
        """
        self.__descriptions.append(description)
        value = self.get_value()
        if value == '':
            value = str(default)
        else:
            value = value + ',' + str(default)
        self.set_value(value)

    def get_descriptions(self):
        """
        Get a list of check button descriptions for this option.

        :return: a list of check button descriptions.
        """
        return self.__descriptions

    def get_selected(self):
        """
        Get a list of descriptions where the check button is selected.

        :return: a list of check button descriptions.
        """
        descriptions = self.__descriptions
        values = self.get_value().split(',')
        return [x[0] for x in zip(descriptions, values) if x[1] == 'True']

