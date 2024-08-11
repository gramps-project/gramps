#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008       Brian G. Matherly
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
This module provides the :class:`.Plugin` class for import plugins.
"""

from . import Plugin


class ImportPlugin(Plugin):
    """
    This class represents a plugin for importing data into Gramps
    """

    def __init__(self, name, description, import_function, extension):
        """
        :param name: A friendly name to call this plugin.
            Example: "GEDCOM Import"
        :type name: string
        :param description: A short description of the plugin.
            Example: "This plugin will import a GEDCOM file into a database"
        :type description: string
        :param import_function: A function to call to perform the import.
            The function must take the form:
                def import_function(db, filename, user):
            where:
                "db" is a Gramps database to import the data into
                "filename" is the file that contains data to be imported
                "user" is an instance of the User class implementing
                       GUI functions (callbacks, errors, warnings, etc)
        :type import_function: callable
        :param extension: The extension for the files imported by this plugin.
            Example: "ged"
        :type extension: str
        :return: nothing
        """
        Plugin.__init__(self, name, description, import_function.__module__)
        self.__import_func = import_function
        self.__extension = extension

    def get_import_function(self):
        """
        Get the import function for this plugins.

        :return: the callable import_function passed into :meth:`__init__`
        """
        return self.__import_func

    def get_extension(self):
        """
        Get the extension for the files imported by this plugin.

        :return: str
        """
        return self.__extension
