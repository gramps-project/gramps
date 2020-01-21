#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020       Paul Culley
# Copyright (C) 2020       Nick Hall
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

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .uid import Uid


#-------------------------------------------------------------------------
#
# UidBase class
#
#-------------------------------------------------------------------------
class UidBase:
    """
    Base class for uid-aware objects.
    """

    def __init__(self):
        """
        Initialize a UidBase.
        """
        self.uid_list = [Uid()]

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return [uid.serialize() for uid in self.uid_list]

    def unserialize(self, uid_list):
        """
        Convert a serialized tuple of data to an object.
        """
        self.uid_list = [Uid().unserialize(uid) for uid in uid_list]

    def add_uid(self, uid):
        """
        Add the Uid to the person or family, only if different

        :param uid:
        :type Uid
        """
        if uid not in self.uid_list:
            self.uid_list.append(uid)

    def get_uid_list(self):
        """
        Return the list of Uid.

        :returns: Returns the list of uid strings.
        :rtype: list
        """
        return self.uid_list

    def set_uid_list(self, uid_list):
        """
        Set a Person or Family instance's uid list to the passed list.

        :param uid_list: List of Uid
        :type uid_list: list
        """
        self.uid_list = uid_list

    def _merge_uid_list(self, acquisition):
        """
        Merge the list of uids from acquisition with our own.

        :param acquisition: the list of Uids.
        :rtype acquisition: list
        """
        for uid in acquisition.get_uid_list():
            self.add_uid(uid)
