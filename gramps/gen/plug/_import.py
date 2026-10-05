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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
This module provides the :class:`.Plugin` class for import plugins.
"""

# ------------------------
# Python modules
# ------------------------
from collections.abc import Callable

# ------------------------
# Gramps modules
# ------------------------
from . import Plugin


# ------------------------------------------------------------
#
# ImportPlugin
#
# ------------------------------------------------------------
class ImportPlugin(Plugin):
    """
    This class represents a plugin for importing data into Gramps.
    """

    def __init__(
        self,
        name: str,
        description: str,
        import_function: Callable,
        extension: str,
        sniff_function: Callable | None = None,
    ) -> None:
        """
        Initialise the ImportPlugin.

        :param name: A friendly name to call this plugin.
            Example: "GEDCOM Import"
        :type name: str
        :param description: A short description of the plugin.
            Example: "This plugin will import a GEDCOM file into a database"
        :type description: str
        :param import_function: A function to call to perform the import.
            The function must take the form ``import_function(db, filename,
            user)`` where *db* is a Gramps database, *filename* is the file
            to import, and *user* is a :class:`gramps.gen.user.User` instance.
        :type import_function: callable
        :param extension: The file extension handled by this plugin (without
            the leading dot). Example: ``"ged"``
        :type extension: str
        :param sniff_function: Optional callable that accepts a filename and
            returns ``True`` when this plugin should handle that file. Used to
            disambiguate between importers that share the same extension (e.g.
            GEDCOM 5.5 vs GEDCOM 7.0). When ``None`` (the default) the plugin
            acts as a fallback for its extension.
        :type sniff_function: callable | None
        """
        Plugin.__init__(self, name, description, import_function.__module__)
        self.__import_func = import_function
        self.__extension = extension
        self.__sniff_func = sniff_function

    def get_import_function(self) -> Callable:
        """
        Return the import function for this plugin.

        :returns: the callable import_function passed into :meth:`__init__`
        :rtype: callable
        """
        return self.__import_func

    def get_extension(self) -> str:
        """
        Return the file extension handled by this plugin.

        :returns: file extension string (without leading dot)
        :rtype: str
        """
        return self.__extension

    def get_sniff_function(self) -> Callable | None:
        """
        Return the sniff function for this plugin, or ``None`` if not set.

        The sniff function accepts a filename and returns ``True`` when this
        plugin is the correct handler for the file. It is called when multiple
        importers are registered for the same extension so that the right one
        can be selected based on file content rather than extension alone.

        :returns: the sniff callable, or ``None``
        :rtype: callable | None
        """
        return self.__sniff_func
