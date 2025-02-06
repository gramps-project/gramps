#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       David Straub
# Copyright (C) 2025       Steve Youngs
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
"""Types for static type checking."""

from __future__ import annotations

from typing import NewType, Type, TypeVar, Union

from .lib import (
    Citation,
    Event,
    Family,
    Media,
    Note,
    Person,
    Place,
    PrimaryObject,
    Repository,
    Source,
    Tag,
)
from .lib.tableobj import TableObject

PersonHandle = NewType("PersonHandle", str)
FamilyHandle = NewType("FamilyHandle", str)
EventHandle = NewType("EventHandle", str)
PlaceHandle = NewType("PlaceHandle", str)
SourceHandle = NewType("SourceHandle", str)
RepositoryHandle = NewType("RepositoryHandle", str)
CitationHandle = NewType("CitationHandle", str)
MediaHandle = NewType("MediaHandle", str)
NoteHandle = NewType("NoteHandle", str)
TagHandle = NewType("TagHandle", str)
PrimaryObjectHandle = Union[
    PersonHandle,
    FamilyHandle,
    EventHandle,
    PlaceHandle,
    SourceHandle,
    RepositoryHandle,
    CitationHandle,
    MediaHandle,
    NoteHandle,
]
AnyHandle = Union[PrimaryObjectHandle, TagHandle]
TableObjectType = TypeVar("TableObjectType", bound=TableObject)

PersonGrampsID = NewType("PersonGrampsID", str)
FamilyGrampsID = NewType("FamilyGrampsID", str)
EventGrampsID = NewType("EventGrampsID", str)
PlaceGrampsID = NewType("PlaceGrampsID", str)
SourceGrampsID = NewType("SourceGrampsID", str)
RepositoryGrampsID = NewType("RepositoryGrampsID", str)
CitationGrampsID = NewType("CitationGrampsID", str)
MediaGrampsID = NewType("MediaGrampsID", str)
NoteGrampsID = NewType("NoteGrampsID", str)
# No Tag IDs
PrimaryObjectGrampsID = Union[
    PersonGrampsID,
    FamilyGrampsID,
    EventGrampsID,
    PlaceGrampsID,
    SourceGrampsID,
    RepositoryGrampsID,
    CitationGrampsID,
    MediaGrampsID,
    NoteGrampsID,
]
AnyGrampsID = PrimaryObjectGrampsID  # No Tag IDs
