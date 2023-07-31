#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2022       Nick Hall
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
This module provides the base class for thumbnailer plugins.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


# -------------------------------------------------------------------------
#
# Thumbnailer class
#
# -------------------------------------------------------------------------
class Thumbnailer(metaclass=ABCMeta):
    @abstractmethod
    def is_supported(self, mime_type):
        """
        Indicates if a mime type is supported by this thumbnailer.

        :param mime_type: mime type of the source file
        :type mime_type: unicode
        :rtype: bool
        :returns: True if the mime type is supported by this thumbnailer
        """

    @abstractmethod
    def run(self, mime_type, src_file, dest_file, size, rectangle):
        """
        Generates a thumbnail image for the specified file.

        :param mime_type: mime type of the source file
        :type mime_type: unicode
        :param src_file: filename of the source file
        :type src_file: unicode
        :param dest_file: filename of the destination file
        :type dest_file: unicode
        :param size: required size of the thumbnail in pixels
        :type size: int
        :param rectangle: subsection rectangle
        :type rectangle: tuple
        :rtype: bool
        :returns: True if the thumbnail was successfully generated
        """
