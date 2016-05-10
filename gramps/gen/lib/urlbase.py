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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
UrlBase class for Gramps.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .url import Url
from .const import IDENTICAL, EQUAL

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
        Initialize an UrlBase.

        If the source is not None, then object is initialized from values of
        the source object.

        :param source: Object used to initialize the new object
        :type source: UrlBase
        """
        self.urls = list(map(Url, source.urls)) if source else []

    def serialize(self):
        """
        Convert the object to a serialized tuple of data
        """
        return [url.serialize() for url in self.urls]

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.

        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: list
        """
        return [url.to_struct() for url in self.urls]

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        return [Url.from_struct(url) for url in struct]

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.urls = [Url().unserialize(item) for item in data]

    def get_url_list(self):
        """
        Return the list of :class:`~.url.Url` instances associated with the
        object.

        :returns: List of :class:`~.url.Url` instances
        :rtype: list
        """
        return self.urls

    def set_url_list(self, url_list):
        """
        Set the list of :class:`~.url.Url` instances to passed the list.

        :param url_list: List of :class:`~.url.Url` instances
        :type url_list: list
        """
        self.urls = url_list

    def _merge_url_list(self, acquisition):
        """
        Merge the list of urls from acquisition with our own.

        :param acquisition: The url list of this object will be merged with
                            the current url list.
        :type acquisition: UrlBase
        """
        url_list = self.urls[:]
        for addendum in acquisition.get_url_list():
            for url in url_list:
                equi = url.is_equivalent(addendum)
                if equi == IDENTICAL:
                    break
                elif equi == EQUAL:
                    url.merge(addendum)
                    break
            else:
                self.urls.append(addendum)

    def add_url(self, url):
        """
        Add a :class:`~.url.Url` instance to the object's list of
        :class:`~.url.Url` instances.

        :param url: :class:`~.url.Url` instance to be added to the Person's
                    list of related web sites.
        :type url: :class:`~.url.Url`
        """
        self.urls.append(url)

    def remove_url(self, url):
        """
        Remove the specified :class:`~.url.Url` instance from the url list.

        If the instance does not exist in the list, the operation has no effect.

        :param url: :class:`~.url.Url` instance to remove from the list
        :type url: :class:`~.url.Url`

        :returns: True if the url was removed, False if it was not in the list.
        :rtype: bool
        """
        if url in self.urls:
            self.urls.remove(url)
            return True
        else:
            return False
