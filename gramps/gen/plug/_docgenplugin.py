#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2012       Paul Franklin
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
This module provides the Plugin class for document generator plugins.
"""

from . import Plugin
from .docgen import TextDoc, DrawDoc


class DocGenPlugin(Plugin):
    """
    This class represents a plugin for generating documents from Gramps
    """

    def __init__(
        self,
        name,
        description,
        basedoc,
        paper,
        style,
        extension,
        docoptclass,
        basedocname,
    ):
        """
        :param name: A friendly name to call this plugin.
            Example: "Plain Text"
        :type name: string
        :param description: A short description of the plugin.
            Example: "This plugin will generate text documents in plain text."
        :type description: string
        :param basedoc: A class that implements the BaseDoc
            interface.
        :type basedoc: BaseDoc
        :param paper: Indicates whether the plugin uses paper or not.
            True = use paper; False = do not use paper
        :type paper: bool
        :param style: Indicates whether the plugin uses styles or not.
            True = use styles; False = do not use styles
        :type style: bool
        :param extension: The extension for the output file.
            Example: "txt"
        :type extension: str
        :param docoptclass: either None or a subclass of DocOptions
        :type docoptclass: either None or a DocOptions subclass
        :param basedocname: The BaseDoc name of this plugin.
            Example: "AsciiDoc"
        :type basedocname: string
        :return: nothing
        """
        Plugin.__init__(self, name, description, basedoc.__module__)
        self.__basedoc = basedoc
        self.__paper = paper
        self.__style = style
        self.__extension = extension
        self.__docoptclass = docoptclass
        self.__basedocname = basedocname

    def get_basedoc(self):
        """
        Get the :class:`.BaseDoc` class for this plugin.

        :return: the :class:`.BaseDoc` class passed into :meth:`__init__`
        """
        return self.__basedoc

    def get_paper_used(self):
        """
        Get the paper flag for this plugin.

        :return: bool - True = use paper; False = do not use paper
        """
        return self.__paper

    def get_style_support(self):
        """
        Get the style flag for this plugin.

        :return: bool - True = use styles; False = do not use styles
        """
        return self.__style

    def get_extension(self):
        """
        Get the file extension for the output file.

        :return: str
        """
        return self.__extension

    def get_doc_option_class(self):
        """
        Get the :class:`.DocOptions` subclass for this plugin, if any

        :return: the :class:`.DocOptions` subclass passed into :meth:`__init__`
        """
        return self.__docoptclass

    def get_basedocname(self):
        """
        Get the :class:`.BaseDoc` name for this plugin.

        :return: the :class:`.BaseDoc` name passed into :meth:`__init__`
        """
        return self.__basedocname

    def get_text_support(self):
        """
        Check if the plugin supports the :class:`.TextDoc` interface.

        :return: bool: True if :class:`.TextDoc` is supported; False if
                       :class:`.TextDoc` is not supported.
        """
        return bool(issubclass(self.__basedoc, TextDoc))

    def get_draw_support(self):
        """
        Check if the plugin supports the :class:`.DrawDoc` interface.

        :return: bool: True if :class:`.DrawDoc` is supported; False if
                       :class:`.DrawDoc` is not supported.
        """
        return bool(issubclass(self.__basedoc, DrawDoc))
