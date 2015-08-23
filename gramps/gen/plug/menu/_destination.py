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
Option class representing a file destination.
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from . import StringOption

#-------------------------------------------------------------------------
#
# DestinationOption class
#
#-------------------------------------------------------------------------
class DestinationOption(StringOption):
    """
    This class describes an option that specifies a destination file or path.
    The destination can be a directory or a file. If the destination is a file,
    the extension can be specified.
    """

    __signals__ = { 'options-changed' : None }

    def __init__(self, label, value):
        """
        :param label: A friendly label to be applied to this option.
            Example: "File Name"
        :type label: string
        :param value: A default destination for this option.
            Example: "/home/username/Desktop/"
            Example: "/home/username/Desktop/report.pdf"
        :type value: string
        :param is_directory: Specifies whether the destination is a directory
                             or a file.
        :type is_directory: bool
        :return: nothing
        """
        StringOption.__init__(self, label, value)
        self.__is_directory = False
        self.__extension = ""

    def set_directory_entry(self, is_directory):
        """
        :param is_directory: Specifies whether the destination is a directory
                             or a file.
        :type is_directory: bool
        :return: nothing
        """
        self.__is_directory = is_directory
        self.emit('options-changed')

    def get_directory_entry(self):
        """
        :return: True if the destination is a directory. False if the
                 destination is a file.
        :rtype: bool
        """
        return self.__is_directory

    def set_extension(self, extension):
        """
        :param extension: Specifies the extension for the destination file.
        :type extension: str
        :return: nothing
        """
        self.__extension = extension

    def get_extension(self):
        """
        :return: The extension for the destination file.
        """
        return self.__extension
