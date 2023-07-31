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
Option class representing a document style.
"""

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from . import EnumeratedListOption
from ..docgen import StyleSheetList


# -------------------------------------------------------------------------
#
# StyleOption class
#
# -------------------------------------------------------------------------
class StyleOption(EnumeratedListOption):  # TODO this is likely dead code
    """
    This class describes an option that allows the use to select a style sheet.
    """

    def __init__(self, label, default_style, module_name):
        """
        :param label: A friendly label to be applied to this option.
            Example: "Style"
        :type label: string
        :param default_style: A docgen StyleSheet instance which provides the
        default styles.
        :type default_style: docgen StyleSheet
        :param module_name: The name of the module the style sheets belong to.
            Example: "web_cal"
        :type module_name: string
        :return: nothing
        """
        EnumeratedListOption.__init__(self, label, "default")

        self.__default_style = default_style
        self.__default_style.set_name("default")
        self.__style_file = "%s_style.xml" % module_name
        style_list = StyleSheetList(self.__style_file, self.__default_style)
        for style_name in style_list.get_style_names():
            self.add_item(style_name, style_name)

    def get_default_style(self):
        """Get the default style"""
        return self.__default_style

    def get_style_file(self):
        """Get the name of the style file"""
        return self.__style_file

    def get_style(self):
        """Get the selected style"""
        style_list = StyleSheetList(self.__style_file, self.__default_style)
        return style_list.get_style_sheet(self.get_value())
