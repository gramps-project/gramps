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
Option class representing a number.
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from . import Option

#-------------------------------------------------------------------------
#
# NumberOption class
#
#-------------------------------------------------------------------------
class NumberOption(Option):
    """
    This class describes an option that is a simple number with defined maximum
    and minimum values.
    """
    def __init__(self, label, value, min_val, max_val, step = 1):
        """
        :param label: A friendly label to be applied to this option.
            Example: "Number of generations to include"
        :type label: string
        :param value: An initial value for this option.
            Example: 5
        :type value: int
        :param min: The minimum value for this option.
            Example: 1
        :type min: int
        :param max: The maximum value for this option.
            Example: 10
        :type value: int
        :param step: The step size for this option.
            Example: 0.01
        :type value: int or float
        :return: nothing
        """
        Option.__init__(self, label, value)
        self.__min = min_val
        self.__max = max_val
        self.__step = step

    def get_min(self):
        """
        Get the minimum value for this option.

        :return: an int that represents the minimum value for this option.
        """
        return self.__min

    def get_max(self):
        """
        Get the maximum value for this option.

        :return: an int that represents the maximum value for this option.
        """
        return self.__max

    def get_step(self):
        """
        Get the step size for this option.

        :return: an int that represents the step size for this option.
        """
        return self.__step
