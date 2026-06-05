#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026            Gabriel Rios
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
Base class for primary objects that carry FamilySearch sync state.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .familysearchsync import FamilySearchSync


class FamilySearchSyncBase:
    """
    Mixin that adds a single FamilySearch sync secondary object.
    """

    def __init__(self, source=None):
        self.familysearch_sync = FamilySearchSync()

        if source:
            getter = getattr(source, "get_familysearch_sync", None)
            if callable(getter):
                self.familysearch_sync = FamilySearchSync(getter().serialize())

    def serialize(self):
        """
        Serialize the FamilySearch sync child object.
        """
        return self.familysearch_sync.serialize()

    def unserialize(self, data):
        """
        Unserialize the FamilySearch sync child object.
        """
        self.familysearch_sync = FamilySearchSync()
        if data:
            self.familysearch_sync.unserialize(data)
        return self

    def get_familysearch_sync(self):
        """
        Return the FamilySearch sync child object.
        """
        return self.familysearch_sync

    def set_familysearch_sync(self, familysearch_sync):
        """
        Assign the FamilySearch sync child object.
        """
        if familysearch_sync is None:
            self.familysearch_sync = FamilySearchSync()
        elif isinstance(familysearch_sync, FamilySearchSync):
            self.familysearch_sync = familysearch_sync
        else:
            self.familysearch_sync = FamilySearchSync(familysearch_sync)

    def clear_familysearch_sync(self):
        """
        Clear all FamilySearch sync state.
        """
        self.familysearch_sync = FamilySearchSync()

    def has_familysearch_sync_data(self):
        """
        Return True if any FamilySearch sync state is stored.
        """
        return not self.familysearch_sync.is_empty()
