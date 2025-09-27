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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
"""Types for static type checking."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    NewType,
    Protocol,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)

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

if TYPE_CHECKING:
    from .lib.address import Address
    from .lib.attribute import Attribute
    from .lib.attrtype import AttributeType
    from .lib.date import Date
    from .lib.eventref import EventRef
    from .lib.eventroletype import EventRoleType
    from .lib.grampstype import GrampsType
    from .lib.ldsord import LdsOrd
    from .lib.mediaref import MediaRef
    from .lib.name import Name
    from .lib.nameorigintype import NameOriginType
    from .lib.nametype import NameType
    from .lib.personref import PersonRef
    from .lib.surname import Surname
    from .lib.url import Url
    from .lib.urltype import UrlType

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


@runtime_checkable
class GrampsTypeLike(Protocol):
    """Protocol for GrampsType-like objects (NameType, AttributeType, etc.)."""

    string: str  # Custom type string
    value: int  # Type code


@runtime_checkable
class DateLike(Protocol):
    """Protocol for Date-like objects."""

    calendar: int
    modifier: int
    quality: int
    dateval: tuple[int | bool, ...]  # Array of date values
    text: str
    sortval: int
    newyear: int  # New year begins


@runtime_checkable
class SurnameLike(Protocol):
    """Protocol for Surname-like objects."""

    surname: str
    prefix: str
    primary: bool
    origintype: GrampsTypeLike  # NameOriginType
    connector: str


@runtime_checkable
class NameLike(Protocol):
    """Protocol for Name-like objects."""

    private: bool
    citation_list: list[str]
    note_list: list[str]
    date: DateLike
    first_name: str
    surname_list: list[SurnameLike]
    suffix: str
    title: str
    type: GrampsTypeLike  # NameType
    group_as: str
    sort_as: int
    display_as: int
    call: str
    nick: str
    famnick: str


@runtime_checkable
class EventRefLike(Protocol):
    """Protocol for EventRef-like objects."""

    private: bool
    citation_list: list[str]
    note_list: list[str]
    attribute_list: list[AttributeLike]
    ref: str  # Event handle
    role: GrampsTypeLike  # EventRoleType


@runtime_checkable
class MediaRefLike(Protocol):
    """Protocol for MediaRef-like objects."""

    private: bool
    citation_list: list[str]
    note_list: list[str]
    attribute_list: list[AttributeLike]
    ref: str  # Media handle
    rect: list[int] | None  # Region coordinates [x, y, width, height]


@runtime_checkable
class AddressLike(Protocol):
    """Protocol for Address-like objects."""

    private: bool
    citation_list: list[str]
    note_list: list[str]
    date: DateLike
    street: str
    locality: str
    city: str
    county: str
    state: str
    country: str
    postal: str  # Postal Code
    phone: str


@runtime_checkable
class AttributeLike(Protocol):
    """Protocol for Attribute-like objects."""

    private: bool
    citation_list: list[str]
    note_list: list[str]
    type: GrampsTypeLike  # AttributeType
    value: str


@runtime_checkable
class UrlLike(Protocol):
    """Protocol for Url-like objects."""

    private: bool
    path: str
    desc: str  # Description
    type: GrampsTypeLike  # UrlType


@runtime_checkable
class LdsOrdLike(Protocol):
    """Protocol for LdsOrd-like objects."""

    citation_list: list[str]
    note_list: list[str]
    date: DateLike
    type: int  # LDS ordinance type
    place: str
    famc: str | None  # Family
    temple: str
    status: int
    private: bool


@runtime_checkable
class PersonRefLike(Protocol):
    """Protocol for PersonRef-like objects."""

    private: bool
    citation_list: list[str]
    note_list: list[str]
    ref: str  # Person handle
    rel: str  # Association/relationship


@runtime_checkable
class PersonLike(Protocol):
    """Protocol for Person-like objects."""

    handle: str
    gramps_id: str
    gender: int
    primary_name: NameLike
    alternate_names: list[NameLike]
    death_ref_index: int
    birth_ref_index: int
    event_ref_list: list[EventRefLike]
    family_list: list[str]
    parent_family_list: list[str]
    media_list: list[MediaRefLike]
    address_list: list[AddressLike]
    attribute_list: list[AttributeLike]
    urls: list[UrlLike]
    lds_ord_list: list[LdsOrdLike]
    citation_list: list[str]
    note_list: list[str]
    change: int
    tag_list: list[str]
    private: bool
    person_ref_list: list[PersonRefLike]


if TYPE_CHECKING:
    # Verify that actual classes implement their corresponding protocols
    _gramps_type: type[GrampsTypeLike] = GrampsType
    _name_type: type[GrampsTypeLike] = NameType
    _attribute_type: type[GrampsTypeLike] = AttributeType
    _url_type: type[GrampsTypeLike] = UrlType
    _event_role_type: type[GrampsTypeLike] = EventRoleType
    _name_origin_type: type[GrampsTypeLike] = NameOriginType

    _date: type[DateLike] = Date
    _surname: type[SurnameLike] = Surname
    _name: type[NameLike] = Name
    _event_ref: type[EventRefLike] = EventRef
    _media_ref: type[MediaRefLike] = MediaRef
    _address: type[AddressLike] = Address
    _attribute: type[AttributeLike] = Attribute
    _url: type[UrlLike] = Url
    _lds_ord: type[LdsOrdLike] = LdsOrd
    _person_ref: type[PersonRefLike] = PersonRef
    _person: type[PersonLike] = Person
