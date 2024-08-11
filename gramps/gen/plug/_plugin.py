#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
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
This module provides the base class for plugins.
"""


class Plugin:
    """
    This class serves as a base class for all plugins that can be registered
    with the plugin manager
    """

    def __init__(self, name, description, module_name):
        """
        :param name: A friendly name to call this plugin.
            Example: "GEDCOM Import"
        :type name: string
        :param description: A short description of the plugin.
            Example: "This plugin will import a GEDCOM file into a database"
        :type description: string
        :param module_name: The name of the module that contains this plugin.
            Example: "gedcom"
        :type module_name: string
        :return: nothing
        """
        self.__name = name
        self.__desc = description
        self.__mod_name = module_name

    def get_name(self):
        """
        Get the name of this plugin.

        :return: a string representing the name of the plugin
        """
        return self.__name

    def get_description(self):
        """
        Get the description of this plugin.

        :return: a string that describes the plugin
        """
        return self.__desc

    def get_module_name(self):
        """
        Get the name of the module that this plugin lives in.

        :return: a string representing the name of the module for this plugin
        """
        return self.__mod_name
