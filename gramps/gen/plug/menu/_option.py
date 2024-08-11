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
The base option class for all other option classes.
"""

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from ...utils.callback import Callback


# -------------------------------------------------------------------------
#
# Option class
#
# -------------------------------------------------------------------------
class Option(Callback):
    """
    This class serves as a base class for all options. All Options must
    minimally provide the services provided by this class. Options are allowed
    to add additional functionality.
    """

    __signals__ = {"value-changed": None, "avail-changed": None}

    def __init__(self, label, value):
        """
        :param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        :type label: string
        :param value: An initial value for this option.
            Example: True
        :type value: The type will depend on the type of option.
        :return: nothing
        """
        Callback.__init__(self)
        self.__value = value
        self.__label = label
        self.__help_str = ""
        self.__available = True

    def get_label(self):
        """
        Get the friendly label for this option.

        :return: string
        """
        return self.__label

    def set_label(self, label):
        """
        Set the friendly label for this option.

        :param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        :type label: string
        :return: nothing
        """
        self.__label = label

    def get_value(self):
        """
        Get the value of this option.

        :return: The option value.
        """
        return self.__value

    def set_value(self, value):
        """
        Set the value of this option.

        :param value: A value for this option.
            Example: True
        :type value: The type will depend on the type of option.
        :return: nothing
        """
        self.__value = value
        self.emit("value-changed")

    def get_help(self):
        """
        Get the help information for this option.

        :return: A string that provides additional help beyond the label.
        """
        return self.__help_str

    def set_help(self, help_text):
        """
        Set the help information for this option.

        :param help: A string that provides additional help beyond the label.
            Example: "Whether to include or exclude people who are calculated
            to be alive at the time of the generation of this report"
        :type value: string
        :return: nothing
        """
        self.__help_str = help_text

    def set_available(self, avail):
        """
        Set the availability of this option.

        :param avail: An indicator of whether this option is currently
                      available. True indicates that the option is available.
                      False indicates that the option is not available.
        :type avail: Bool
        :return: nothing
        """
        if avail != self.__available:
            self.__available = avail
            self.emit("avail-changed")

    def get_available(self):
        """
        Get the availability of this option.

        :return: A Bool indicating the availablity of this option. True
                 indicates that the option is available. False indicates that
                 the option is not available.
        """
        return self.__available
