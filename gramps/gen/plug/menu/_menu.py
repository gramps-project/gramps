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
Abstracted option handling.
"""

#-------------------------------------------------------------------------
#
# Menu class
#
#-------------------------------------------------------------------------
class Menu:
    """
    **Introduction**

    A Menu is used to maintain a collection of options that need to be
    represented to the user in a non-implementation specific way. The options
    can be described using the various option classes. A menu contains many
    options and associates them with a unique name and category.

    **Usage**

    Menus are used in the following way.

    1. Create an option object and configure all the attributes of the option.
    2. Add the option to the menu by specifying the option, name and category.
    3. Add as many options as necessary.
    4. When all the options are added, the menu can be stored and passed to
       the part of the system that will actually represent the menu to
       the user.
    """
    def __init__(self):
        # __options holds all the options by their category
        self.__options = {}
        # __categories holds the order of all categories
        self.__categories = []

    def add_option(self, category, name, option):
        """
        Add an option to the menu.

        :param category: A label that describes the category that the option
            belongs to.
            Example: "Report Options"
        :type category: string
        :param name: A name that is unique to this option.
            Example: "generations"
        :type name: string
        :param option: The option instance to be added to this menu.
        :type option: gen.plug.menu.Option
        :return: nothing
        """
        if category not in self.__options:
            self.__categories.append(category)
            self.__options[category] = []
        self.__options[category].append((name, option))

    def get_categories(self):
        """
        Get a list of categories in this menu.

        :return: a list of strings
        """
        return self.__categories

    def get_option_names(self, category):
        """
        Get a list of option names for the specified category.

        :return: a list of strings
        """
        names = []
        for (name, option) in self.__options[category]:
            names.append(name)
        return names

    def get_option(self, category, name):
        """
        Get an option with the specified category and name.

        :return: an :class:`.Option` instance or None on failure.
        """
        for (oname, option) in self.__options[category]:
            if oname == name:
                return option
        return None

    def get_all_option_names(self):
        """
        Get a list of all the option names in this menu.

        :return: a list of strings
        """
        names = []
        for category in self.__options:
            for (name, option) in self.__options[category]:
                names.append(name)
        return names

    def get_option_by_name(self, name):
        """
        Get an option with the specified name.

        :return: an :class:`.Option` instance or None on failure.
        """
        for category in self.__options:
            for (oname, option) in self.__options[category]:
                if oname == name:
                    return option
        return None
