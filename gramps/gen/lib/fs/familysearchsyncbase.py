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

from __future__ import annotations

from typing import Any

from .familysearchsync import FamilySearchSync


class FamilySearchSyncBase:
    """
    Mixin that adds a single FamilySearch sync secondary object.
    """

    def __init__(self, source: Any = None) -> None:
        self.familysearch_sync: FamilySearchSync | None = None

        if source:
            getter = getattr(source, "get_familysearch_sync", None)
            if callable(getter) and getter() is not None:
                self.familysearch_sync = FamilySearchSync(getter().serialize())

    def serialize(self) -> dict | None:
        """
        Serialize the FamilySearch sync child object, or return None.
        """
        if self.familysearch_sync is None:
            return None
        return self.familysearch_sync.serialize()

    def unserialize(self, data: dict | None) -> FamilySearchSyncBase:
        """
        Unserialize the FamilySearch sync child object.
        """
        self.set_familysearch_sync(data)
        return self

    def get_familysearch_sync(self):
        """
        Return the FamilySearch sync child object.
        """
        return self.familysearch_sync

    def set_familysearch_sync(
        self, familysearch_sync: FamilySearchSync | dict | None
    ) -> None:
        """
        Assign the FamilySearch sync child object.
        """
        if familysearch_sync is None:
            self.familysearch_sync = None
        elif isinstance(familysearch_sync, FamilySearchSync):
            self.familysearch_sync = familysearch_sync
        else:
            self.familysearch_sync = FamilySearchSync(familysearch_sync)

    def clear_familysearch_sync(self) -> None:
        """
        Clear all FamilySearch sync state.
        """
        self.familysearch_sync = None

    def has_familysearch_sync_data(self) -> bool:
        """
        Return True if any FamilySearch sync state is stored.
        """
        return (
            self.familysearch_sync is not None and not self.familysearch_sync.is_empty()
        )
