#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008       Brian G. Matherly
# Copyright (C) 2008            Gary Burton
# Copyright (C) 2008            Robert Cheramy <robert@cheramy.net>
# Copyright (C) 2011       Tim G L Lyons
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
Proxy class for the Gramps databases. Apply filter
"""
# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations

# -------------------------------------------------------------------------
#
# Gramps libraries
#
# -------------------------------------------------------------------------
from .proxybase import ProxyDbBase
from ..lib import (
    Date,
    Person,
    Name,
    Surname,
    NameOriginType,
    Family,
    Source,
    Citation,
    Event,
    Media,
    Place,
    Repository,
    Note,
    Tag,
)
from ..const import GRAMPS_LOCALE as glocale
from ..types import (
    AnyHandle,
    PersonHandle,
    EventHandle,
    FamilyHandle,
    PlaceHandle,
    PrimaryObject,
    SourceHandle,
    RepositoryHandle,
    CitationHandle,
    MediaHandle,
    NoteHandle,
    TagHandle,
    TableObjectType,
    PersonGrampsID,
    EventGrampsID,
    FamilyGrampsID,
    PlaceGrampsID,
    SourceGrampsID,
    RepositoryGrampsID,
    CitationGrampsID,
    MediaGrampsID,
    NoteGrampsID,
)


class FilterProxyDb(ProxyDbBase):
    def __init__(
        self, db, person_filter=None, event_filter=None, note_filter=None, user=None
    ):
        self.person_filter = person_filter
        self.event_filter = event_filter
        self.note_filter = note_filter
        self.user = user

        super().__init__(db)

    def get_person_map(self):
        # Get a map from map[handle] = {"surname": "Name"}
        if self.person_filter:
            return self.person_filter.apply(
                self.db, self.db.iter_person_handles(), user=self.user
            )
        else:
            return super().get_person_map()

    def get_event_map(self):
        if self.event_filter:
            return self.event_filter.apply(
                self.db, self.db.iter_event_handles(), user=self.user
            )
        else:
            return super().get_event_map()

    def get_note_map(self):
        if self.note_filter:
            return self.note_filter.apply(
                self.db, self.db.iter_note_handles(), user=self.user
            )
        else:
            return super().get_note_map()
