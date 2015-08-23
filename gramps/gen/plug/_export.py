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
This module provides the :class:`.Plugin` class for export plugins.
"""

from . import Plugin

class ExportPlugin(Plugin):
    """
    This class represents a plugin for exporting data from Gramps
    """
    def __init__(self, name, description, export_function,
                 extension, config=None):
        """
        :param name: A friendly name to call this plugin.
            Example: "GEDCOM Export"
        :type name: string
        :param description: A short description of the plugin.
            Example: "This plugin will export a GEDCOM file from database"
        :type description: string
        :param export_function: A function to call to perform the export.
            The function must take the form:
                def export_function(database, filename, user, option_box):
            where:
                "db" is a Gramps database to import the data into
                "filename" is the file that the data will be exported to
                "user" provides UI output (callback, errors, etc)
        :type export_function: callable
        :param extension: The extension for the output file.
            Example: "ged"
        :type extension: str
        :param config: Options for the exporter
        :type config: tuple (??,??)
        :return: nothing
        """
        Plugin.__init__(self, name, description, export_function.__module__)
        self.__export_func = export_function
        self.__extension = extension
        self.__config = config

    def get_export_function(self):
        """
        Get the export function for this plugin.

        :return: the callable export_function passed into :meth:`__init__`
        """
        return self.__export_func

    def get_extension(self):
        """
        Get the file extension for the export file.

        :return: str
        """
        return self.__extension

    def get_config(self):
        """
        Get the config.

        :return: (??,??)
        """
        return self.__config
