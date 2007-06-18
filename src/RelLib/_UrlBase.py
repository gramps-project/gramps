#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"""
UrlBase class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _Url import Url

#-------------------------------------------------------------------------
#
# UrlBase classes
#
#-------------------------------------------------------------------------
class UrlBase:
    """
    Base class for url-aware objects.
    """

    def __init__(self, source=None):
        """
        Initialize an UrlBase. If the source is not None, then object
        is initialized from values of the source object.

        @param source: Object used to initialize the new object
        @type source: UrlBase
        """
        
        if source:
            self.urls = [ Url(url) for url in source.urls ]
        else:
            self.urls = []

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return [url.serialize() for url in self.urls]

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        self.urls = [Url().unserialize(item) for item in data]

    def get_url_list(self):
        """
        Returns the list of L{Url} instances associated with the object.

        @returns: List of L{Url} instances
        @rtype: list
        """
        return self.urls

    def set_url_list(self, url_list):
        """
        Sets the list of L{Url} instances to passed the list.

        @param url_list: List of L{Url} instances
        @type url_list: list
        """
        self.urls = url_list

    def add_url(self, url):
        """
        Adds a L{Url} instance to the object's list of L{Url} instances

        @param url: L{Url} instance to be added to the Person's list of
            related web sites.
        @type url: L{Url}
        """
        self.urls.append(url)
    
    def remove_url(self, url):
        """
        Removes the specified L{Url} instance from the url list
        If the instance does not exist in the list, the operation has
        no effect.

        @param url: L{Url} instance to remove from the list
        @type url: L{Url}

        @return: True if the url was removed, False if it was not in the list.
        @rtype: bool
        """
        if url in self.urls:
            self.urls.remove(url)
            return True
        else:
            return False
