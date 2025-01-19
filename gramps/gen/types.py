"""Types for static type checking."""

from __future__ import annotations

from typing import NewType, Type, TypeVar

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
PrimaryObjectHandle = (
    PersonHandle
    | FamilyHandle
    | EventHandle
    | PlaceHandle
    | SourceHandle
    | RepositoryHandle
    | CitationHandle
    | MediaHandle
    | NoteHandle
)
AnyHandle = PrimaryObjectHandle | TagHandle
TableObjectType = TypeVar("TableObjectType", bound=TableObject)
