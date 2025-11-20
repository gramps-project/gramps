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
    Sequence,
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
    from .lib.childref import ChildRef
    from .lib.childreftype import ChildRefType
    from .lib.date import Date
    from .lib.eventref import EventRef
    from .lib.eventroletype import EventRoleType
    from .lib.eventtype import EventType
    from .lib.familyreltype import FamilyRelType
    from .lib.grampstype import GrampsType
    from .lib.ldsord import LdsOrd
    from .lib.location import Location
    from .lib.mediaref import MediaRef
    from .lib.name import Name
    from .lib.nameorigintype import NameOriginType
    from .lib.nametype import NameType
    from .lib.notetype import NoteType
    from .lib.personref import PersonRef
    from .lib.placename import PlaceName
    from .lib.placeref import PlaceRef
    from .lib.placetype import PlaceType
    from .lib.reporef import RepoRef
    from .lib.repotype import RepositoryType
    from .lib.srcattribute import SrcAttribute
    from .lib.srcattrtype import SrcAttributeType
    from .lib.srcmediatype import SourceMediaType
    from .lib.styledtext import StyledText
    from .lib.styledtexttag import StyledTextTag
    from .lib.styledtexttagtype import StyledTextTagType
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
    citation_list: Sequence[str]
    note_list: Sequence[str]
    date: DateLike
    first_name: str
    surname_list: Sequence[SurnameLike]
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
    citation_list: Sequence[str]
    note_list: Sequence[str]
    attribute_list: Sequence[AttributeLike]
    ref: str  # Event handle
    role: GrampsTypeLike  # EventRoleType


@runtime_checkable
class MediaRefLike(Protocol):
    """Protocol for MediaRef-like objects."""

    private: bool
    citation_list: Sequence[str]
    note_list: Sequence[str]
    attribute_list: Sequence[AttributeLike]
    ref: str  # Media handle
    rect: Sequence[int] | None  # Region coordinates [x, y, width, height]


@runtime_checkable
class AddressLike(Protocol):
    """Protocol for Address-like objects."""

    private: bool
    citation_list: Sequence[str]
    note_list: Sequence[str]
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
    citation_list: Sequence[str]
    note_list: Sequence[str]
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

    citation_list: Sequence[str]
    note_list: Sequence[str]
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
    citation_list: Sequence[str]
    note_list: Sequence[str]
    ref: str  # Person handle
    rel: str  # Association/relationship


@runtime_checkable
class ChildRefLike(Protocol):
    """Protocol for ChildRef-like objects."""

    private: bool
    citation_list: Sequence[str]
    note_list: Sequence[str]
    ref: str  # Child handle
    frel: GrampsTypeLike  # ChildRefType - Father relationship
    mrel: GrampsTypeLike  # ChildRefType - Mother relationship


@runtime_checkable
class PlaceRefLike(Protocol):
    """Protocol for PlaceRef-like objects."""

    ref: str  # Place handle
    date: DateLike


@runtime_checkable
class RepoRefLike(Protocol):
    """Protocol for RepoRef-like objects."""

    private: bool
    note_list: Sequence[str]
    ref: str  # Repository handle
    call_number: str
    media_type: GrampsTypeLike  # SourceMediaType


@runtime_checkable
class SrcAttributeLike(Protocol):
    """Protocol for SrcAttribute-like objects."""

    private: bool
    type: GrampsTypeLike  # SrcAttributeType
    value: str


@runtime_checkable
class StyledTextTagLike(Protocol):
    """Protocol for StyledTextTag-like objects."""

    name: GrampsTypeLike  # StyledTextTagType
    value: str | int | None
    ranges: Sequence[tuple[int, int]]


@runtime_checkable
class StyledTextLike(Protocol):
    """Protocol for StyledText-like objects."""

    string: str
    tags: Sequence[StyledTextTagLike]


@runtime_checkable
class PlaceNameLike(Protocol):
    """Protocol for PlaceName-like objects."""

    value: str
    date: DateLike
    lang: str


@runtime_checkable
class LocationLike(Protocol):
    """Protocol for Location-like objects."""

    street: str
    locality: str
    city: str
    county: str
    state: str
    country: str
    postal: str
    phone: str
    parish: str


@runtime_checkable
class PersonLike(Protocol):
    """Protocol for Person-like objects."""

    handle: str
    gramps_id: str
    gender: int
    primary_name: NameLike
    alternate_names: Sequence[NameLike]
    death_ref_index: int
    birth_ref_index: int
    event_ref_list: Sequence[EventRefLike]
    family_list: Sequence[str]
    parent_family_list: Sequence[str]
    media_list: Sequence[MediaRefLike]
    address_list: Sequence[AddressLike]
    attribute_list: Sequence[AttributeLike]
    urls: Sequence[UrlLike]
    lds_ord_list: Sequence[LdsOrdLike]
    citation_list: Sequence[str]
    note_list: Sequence[str]
    change: int
    tag_list: Sequence[str]
    private: bool
    person_ref_list: Sequence[PersonRefLike]


@runtime_checkable
class FamilyLike(Protocol):
    """Protocol for Family-like objects."""

    handle: str
    gramps_id: str
    father_handle: str | None
    mother_handle: str | None
    child_ref_list: Sequence[ChildRefLike]
    type: GrampsTypeLike  # FamilyRelType
    event_ref_list: Sequence[EventRefLike]
    media_list: Sequence[MediaRefLike]
    attribute_list: Sequence[AttributeLike]
    lds_ord_list: Sequence[LdsOrdLike]
    citation_list: Sequence[str]
    note_list: Sequence[str]
    change: int
    tag_list: Sequence[str]
    private: bool


@runtime_checkable
class EventLike(Protocol):
    """Protocol for Event-like objects."""

    handle: str
    gramps_id: str
    type: GrampsTypeLike  # EventType
    date: DateLike
    description: str
    place: str | None
    citation_list: Sequence[str]
    note_list: Sequence[str]
    media_list: Sequence[MediaRefLike]
    attribute_list: Sequence[AttributeLike]
    change: int
    tag_list: Sequence[str]
    private: bool


@runtime_checkable
class MediaLike(Protocol):
    """Protocol for Media-like objects."""

    handle: str
    gramps_id: str
    path: str
    mime: str
    desc: str
    checksum: str
    attribute_list: Sequence[AttributeLike]
    citation_list: Sequence[str]
    note_list: Sequence[str]
    change: int
    date: DateLike
    tag_list: Sequence[str]
    private: bool


@runtime_checkable
class PlaceLike(Protocol):
    """Protocol for Place-like objects."""

    handle: str
    gramps_id: str
    title: str
    long: str
    lat: str
    placeref_list: Sequence[PlaceRefLike]
    name: PlaceNameLike
    alt_names: Sequence[PlaceNameLike]
    place_type: GrampsTypeLike  # PlaceType
    code: str
    alt_loc: Sequence[LocationLike]
    urls: Sequence[UrlLike]
    media_list: Sequence[MediaRefLike]
    citation_list: Sequence[str]
    note_list: Sequence[str]
    change: int
    tag_list: Sequence[str]
    private: bool


@runtime_checkable
class SourceLike(Protocol):
    """Protocol for Source-like objects."""

    handle: str
    gramps_id: str
    title: str
    author: str
    pubinfo: str
    note_list: Sequence[str]
    media_list: Sequence[MediaRefLike]
    abbrev: str
    change: int
    attribute_list: Sequence[SrcAttributeLike]
    reporef_list: Sequence[RepoRefLike]
    tag_list: Sequence[str]
    private: bool


@runtime_checkable
class CitationLike(Protocol):
    """Protocol for Citation-like objects."""

    handle: str
    gramps_id: str
    date: DateLike
    page: str
    confidence: int
    source_handle: str
    note_list: Sequence[str]
    media_list: Sequence[MediaRefLike]
    attribute_list: Sequence[SrcAttributeLike]
    change: int
    tag_list: Sequence[str]
    private: bool


@runtime_checkable
class RepositoryLike(Protocol):
    """Protocol for Repository-like objects."""

    handle: str
    gramps_id: str
    type: GrampsTypeLike  # RepositoryType
    name: str
    note_list: Sequence[str]
    address_list: Sequence[AddressLike]
    urls: Sequence[UrlLike]
    change: int
    tag_list: Sequence[str]
    private: bool


@runtime_checkable
class NoteLike(Protocol):
    """Protocol for Note-like objects."""

    handle: str
    gramps_id: str
    text: StyledTextLike
    format: int
    type: GrampsTypeLike  # NoteType
    change: int
    tag_list: Sequence[str]
    private: bool


@runtime_checkable
class TagLike(Protocol):
    """Protocol for Tag-like objects."""

    handle: str
    name: str
    color: str
    priority: int
    change: int


if TYPE_CHECKING:
    # Verify that actual classes implement their corresponding protocols
    _gramps_type: Type[GrampsTypeLike] = GrampsType
    _name_type: Type[GrampsTypeLike] = NameType
    _attribute_type: Type[GrampsTypeLike] = AttributeType
    _url_type: Type[GrampsTypeLike] = UrlType
    _event_role_type: Type[GrampsTypeLike] = EventRoleType
    _name_origin_type: Type[GrampsTypeLike] = NameOriginType
    _event_type: Type[GrampsTypeLike] = EventType
    _family_rel_type: Type[GrampsTypeLike] = FamilyRelType
    _child_ref_type: Type[GrampsTypeLike] = ChildRefType
    _place_type: Type[GrampsTypeLike] = PlaceType
    _repository_type: Type[GrampsTypeLike] = RepositoryType
    _src_attribute_type: Type[GrampsTypeLike] = SrcAttributeType
    _source_media_type: Type[GrampsTypeLike] = SourceMediaType
    _styled_text_tag_type: Type[GrampsTypeLike] = StyledTextTagType
    _note_type: Type[GrampsTypeLike] = NoteType

    _date: Type[DateLike] = Date
    _surname: Type[SurnameLike] = Surname
    _name: Type[NameLike] = Name
    _event_ref: Type[EventRefLike] = EventRef
    _media_ref: Type[MediaRefLike] = MediaRef
    _address: Type[AddressLike] = Address
    _attribute: Type[AttributeLike] = Attribute
    _url: Type[UrlLike] = Url
    _lds_ord: Type[LdsOrdLike] = LdsOrd
    _person_ref: Type[PersonRefLike] = PersonRef
    _child_ref: Type[ChildRefLike] = ChildRef
    _place_ref: Type[PlaceRefLike] = PlaceRef
    _repo_ref: Type[RepoRefLike] = RepoRef
    _src_attribute: Type[SrcAttributeLike] = SrcAttribute
    _styled_text_tag: Type[StyledTextTagLike] = StyledTextTag
    _styled_text: Type[StyledTextLike] = StyledText
    _place_name: Type[PlaceNameLike] = PlaceName
    _location: Type[LocationLike] = Location

    _person: Type[PersonLike] = Person
    _family: Type[FamilyLike] = Family
    _event: Type[EventLike] = Event
    _media: Type[MediaLike] = Media
    _place: Type[PlaceLike] = Place
    _source: Type[SourceLike] = Source
    _citation: Type[CitationLike] = Citation
    _repository: Type[RepositoryLike] = Repository
    _note: Type[NoteLike] = Note
    _tag: Type[TagLike] = Tag
