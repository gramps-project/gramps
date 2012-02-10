#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012        Nick Hall
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$

#------------------------------------------------------------------------
#
# IndexOptions
#
#------------------------------------------------------------------------
class IndexOptions(object):
    """
    Define the options for the alphabetical index and table of contents.
    """
    def __init__(self, include_toc, include_index):
        self.__include_toc = include_toc
        self.__include_index = include_index
        
    def get_include_toc(self):
        """
        Return a boolean indicating if a table of contents should be included.
        """
        return self.__include_toc
        
    def get_include_index(self):
        """
        Return a boolean indicating if an alphabetical index should be included.
        """
        return self.__include_index
