# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2023-2024  Jean Michault
# Copyright (C) 2023-2026  Gabriel Rios
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

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from collections import ChainMap
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from typing import Any, ClassVar, Optional, get_args, get_origin
import logging

logger = logging.getLogger(__name__)


# =====================================
# Annotation utilities
# ====================================


@lru_cache(maxsize=None)
def _merged_annotations(type_obj: type) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for base in reversed(type_obj.__mro__):
        merged.update(getattr(base, "__annotations__", {}) or {})
    return merged


def all_annotations(type_obj: type) -> ChainMap:
    return ChainMap(_merged_annotations(type_obj))


def init_class(obj: Any) -> None:
    """
    initialize attributes declared in annotations to predictable empty containers
    (set/dict/list) or None
    """
    ann = _merged_annotations(obj.__class__)
    for name, declared in ann.items():
        origin = get_origin(declared)
        if declared is set or origin is set:
            setattr(obj, name, set())
        elif declared is dict or origin is dict:
            setattr(obj, name, {})
        elif declared is list or origin is list:
            setattr(obj, name, [])
        else:
            setattr(obj, name, None)


# =============================================================================
# Type resolution helpers (forward refs like "Link" inside dict[str, "Link"])
# =============================================================================


def _resolve_type_ref(type_ref: Any) -> Any:
    if isinstance(type_ref, str):
        return globals().get(type_ref, type_ref)

    forward_arg = getattr(type_ref, "__forward_arg__", None)
    if isinstance(forward_arg, str):
        return globals().get(forward_arg, type_ref)

    return type_ref


def _unwrap_optional(type_ref: Any) -> Any:
    origin = get_origin(type_ref)
    if origin is None:
        return type_ref

    if getattr(origin, "__name__", "") == "Union":
        args = get_args(type_ref) or ()
        non_none = [a for a in args if a is not type(None)]  # noqa: E721
        if len(non_none) == 1:
            return non_none[0]
    return type_ref


# ======================
# Formal date parsing
# ======================


def _tz_from_suffix(suffix: str):
    """
    should accept 'Z', '+HH', '+HH:MM', '-HH', '-HH:MM'.
    uses UTC on weird input
    """
    if not suffix or suffix == "Z":
        return timezone.utc

    raw = suffix.strip()
    sign = 1
    if raw.startswith("-"):
        sign = -1
        raw = raw[1:]
    elif raw.startswith("+"):
        raw = raw[1:]

    hh = 0
    mm = 0
    parts = raw.split(":", 1)
    try:
        if parts[0]:
            hh = int(parts[0])
        if len(parts) == 2 and parts[1]:
            mm = int(parts[1])
    except ValueError:
        return timezone.utc

    return timezone(timedelta(hours=sign * hh, minutes=sign * mm))


class SimpleDate:
    """
    Parses a practical subset of GedcomX "formal" timestamps:
      +-YYYY[-MM[-DD[Thh[:mm[:ss]][+-hh[:mm]|Z]]]]
    """

    def __init__(self, value: Optional[str] = None):
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0.0
        self.zone = "Z"

        if not value:
            return

        s = value.strip()
        if len(s) < 2:
            print("invalid formal date: " + value)
            return

        if "Z" in s:
            s = s.replace("Z", "")
            self.zone = "Z"

        # split date / time
        date_part, _, time_part = s.partition("T")
        if not date_part or len(date_part) < 2:
            print("invalid formal date: " + value)
            return

        # drop explicit leading '+'
        if date_part.startswith("+"):
            date_part = date_part[1:]

        # handle sign for negative years
        sign = 1
        if date_part.startswith("-"):
            sign = -1
            date_part = date_part[1:]

        ymd = date_part.split("-")
        try:
            if ymd and ymd[0]:
                self.year = sign * int(ymd[0])
            if len(ymd) > 1 and ymd[1]:
                self.month = int(ymd[1])
            if len(ymd) > 2 and ymd[2]:
                self.day = int(ymd[2])
        except ValueError:
            print("invalid formal date: " + value)
            return

        if time_part:
            zone_pos = -1
            plus = time_part.find("+")
            minus = time_part.find("-")
            if plus >= 0 and minus >= 0:
                zone_pos = min(plus, minus)
            else:
                zone_pos = max(plus, minus)

            if zone_pos >= 0:
                self.zone = time_part[zone_pos:]
                time_part = time_part[:zone_pos]

            t = time_part.split(":")
            try:
                if t and t[0]:
                    self.hour = int(t[0])
                if len(t) > 1 and t[1]:
                    self.minute = int(t[1])
                if len(t) > 2 and t[2]:
                    self.second = float(t[2])
            except ValueError:
                print("invalid formal date: " + value)
                return

    def __str__(self) -> str:
        if self.year == 0:
            return ""

        out = ("+" if self.year >= 0 else "") + f"{self.year:04d}"

        if self.month:
            out += f"-{self.month:02d}"
            if self.day:
                out += f"-{self.day:02d}"

        if self.hour:
            out += f"T{self.hour:02d}"
            if self.minute:
                out += f":{self.minute:02d}"
                if self.second:
                    if abs(self.second - int(self.second)) < 1e-9:
                        out += f":{int(self.second):02d}"
                    else:
                        out += (f":{self.second:02f}").rstrip("0").rstrip(".")
            out += self.zone

        return out

    def datetime(self) -> datetime:
        # datetime() can't accept 0 month/day
        month = self.month or 1
        day = self.day or 1

        tz = _tz_from_suffix(self.zone)
        micro = round((self.second % 1) * 1_000_000)
        return datetime(
            self.year,
            month,
            day,
            self.hour,
            self.minute,
            int(self.second),
            microsecond=micro,
            tzinfo=tz,
        )

    def int(self) -> int:
        return round(self.datetime().timestamp() * 1000)


class DateFormal:
    def __init__(self, src: Optional[str] = None):
        self.approximate = False
        self.is_range = False
        self.occurrences = 0
        self.start_date = SimpleDate()
        self.end_date = SimpleDate()
        self.duration: Optional[str] = None
        self.parse(src)

    def parse(self, src: Optional[str]) -> None:
        if not src or len(src) < 5:
            return

        s = src.strip()

        if s.startswith("A"):
            self.approximate = True
            s = s[1:]

        if s.startswith("R"):
            s = s[1:]
            head, _, tail = s.partition("/")
            try:
                self.occurrences = int(head) or 1
            except ValueError:
                self.occurrences = 1
            s = tail

        left, sep, right = s.partition("/")
        self.start_date = SimpleDate(left)
        self.is_range = bool(sep)

        if self.is_range and right and len(right) > 1:
            if right.startswith("P"):
                self.duration = right
            else:
                self.end_date = SimpleDate(right)

    def to_string(self) -> str:
        return str(self)

    def __str__(self) -> str:
        out = "A" if self.approximate else ""
        if self.occurrences > 0:
            out += f"R{self.occurrences}/"
        out += str(self.start_date)

        if self.is_range:
            out += "/"
            if self.duration:
                out += self.duration
            else:
                out += str(self.end_date)

        return out


# =================================
# JSON serializer/deserializer
# =================================


def serialize_json(obj: Any):
    """
    convert an object graph to JSON-serializable Python types
    empty containers become None
    """
    if hasattr(obj, "serialize_json"):
        return obj.serialize_json()
    if hasattr(obj, "to_string"):
        return obj.to_string()

    if isinstance(obj, (bool, str, int, float)):
        return obj

    if isinstance(obj, (set, list, tuple)):
        if not obj:
            return
        return [serialize_json(x) for x in obj]

    if isinstance(obj, dict):
        if not obj:
            return
        out_dict: dict[Any, Any] = {}
        for k, v in obj.items():
            sk = serialize_json(k)
            sv = serialize_json(v)
            if sv:
                out_dict[sk] = sv
        return out_dict

    out_obj: dict[str, Any] = {}
    for name in dir(obj):
        if name.startswith("_"):
            continue
        value = getattr(obj, name)
        if callable(value):
            continue

        if value is None:
            continue
        if isinstance(value, (set, list, dict, str)) and len(value) == 0:
            continue

        key = name.replace("_", "-")
        out_obj[key] = serialize_json(value)
    return out_obj


def _json_key_to_attr(key: str) -> str:
    """
    normalize JSON keys
    """
    ns = "{http://www.w3.org/XML/1998/namespace}"
    if key.startswith(ns):
        key = key[len(ns) :]
    return key.replace("-", "_")


def _reuse_by_id_if_nonindexed(type_obj: type, data: Any, parent: Any):
    if not isinstance(data, dict):
        return None

    obj_id = data.get("id")
    if not obj_id:
        return None

    if type_obj.__name__ == "SourceReference":
        container_name = "sources"
    else:
        container_name = type_obj.__name__.lower() + "s"

    container = getattr(parent, container_name, None)
    if not container:
        return None

    try:
        for existing in container:
            if getattr(existing, "id", None) == obj_id:
                return existing
    except TypeError:
        return None

    return None


def _construct_object(target_type_obj: Any, data: Any, parent: Any):
    """
    build or reuse a child object instance, preserving the original rules:
    - primitive str: return str(data)
    - id + _index => global cache
    - id without _index => try to reuse within parent collection

    also resolves forward refs like "Link".
    """
    target_type_obj = _resolve_type_ref(target_type_obj)
    target_type_obj = _unwrap_optional(target_type_obj)
    target_type_obj = _resolve_type_ref(target_type_obj)

    if target_type_obj is str:
        return str(data)

    if isinstance(target_type_obj, str):
        return data

    ann = _merged_annotations(target_type_obj)
    has_id = "id" in ann
    has_index = "_index" in ann

    if isinstance(data, dict) and has_id and not has_index:
        reused = _reuse_by_id_if_nonindexed(target_type_obj, data, parent)
        if reused is not None:
            deserialize_json(reused, data)
            return reused

    obj_id = data.get("id") if isinstance(data, dict) else None

    if has_id and has_index and obj_id:
        index = getattr(target_type_obj, "_index", None)
        if isinstance(index, dict) and obj_id in index:
            obj = index[obj_id]
            deserialize_json(obj, data)
            return obj
        try:
            obj = target_type_obj(id=obj_id)
        except TypeError:
            obj = target_type_obj()
        deserialize_json(obj, data)
        if isinstance(getattr(target_type_obj, "_index", None), dict):
            target_type_obj._index[obj_id] = obj
        return obj

    obj = target_type_obj()
    deserialize_json(obj, data)
    if (
        has_id
        and has_index
        and obj_id
        and isinstance(getattr(target_type_obj, "_index", None), dict)
    ):
        target_type_obj._index[obj_id] = obj
    return obj


def deserialize_json(obj: Any, data: Any, required: bool = False):
    """
    Populate obj from decoded JSON data.
    """
    if not required:
        if hasattr(obj, "deserialize_json"):
            obj.deserialize_json(data)
            return
        if hasattr(obj, "parse"):
            obj.parse(data)
            return

    if not data:
        return

    if isinstance(obj, set):
        try:
            obj.update(data)
        except TypeError:
            obj.add(data)
        return

    if not isinstance(data, dict):
        return

    ann = _merged_annotations(obj.__class__)

    for raw_key, raw_value in data.items():
        attr_name = _json_key_to_attr(raw_key)
        declared = ann.get(attr_name)

        if declared is None:
            print(
                "Unknown JSON Value: Error: " + obj.__class__.__name__ + ":" + raw_key
            )
            continue

        declared = _unwrap_optional(declared)
        declared = _resolve_type_ref(declared)

        origin = get_origin(declared)
        args = get_args(declared)

        if declared is bool:
            if raw_value == "true":
                setattr(obj, attr_name, True)
            elif raw_value == "false":
                setattr(obj, attr_name, False)
            else:
                setattr(obj, attr_name, raw_value)
            continue

        if declared in (str, int, float) or declared is None:
            setattr(obj, attr_name, raw_value)
            continue

        # dict[str, T] special handling (including dict[str, set[...]])
        if origin is dict and args and len(args) == 2 and args[0] is str:
            value_type_obj = _unwrap_optional(args[1])
            value_type_obj = _resolve_type_ref(value_type_obj)
            value_origin = get_origin(value_type_obj)

            current_any = getattr(obj, attr_name, None)
            current_dict: dict[str, Any] = (
                dict(current_any) if isinstance(current_any, dict) else {}
            )

            if isinstance(raw_value, dict):
                for k2, v2 in raw_value.items():
                    if value_type_obj is set or value_origin is set:
                        if isinstance(v2, (list, tuple, set)):
                            current_dict[k2] = set(v2)
                        else:
                            current_dict[k2] = {v2}
                    else:
                        current_dict[k2] = _construct_object(value_type_obj, v2, obj)

            setattr(obj, attr_name, current_dict)
            continue

        # containers: set
        if declared is set or origin is set:
            current_any_set = getattr(obj, attr_name, None)
            current_set: set[Any] = (
                set(current_any_set) if isinstance(current_any_set, set) else set()
            )

            elem_type_obj = _unwrap_optional(args[0]) if args else None
            elem_type_obj = _resolve_type_ref(elem_type_obj)

            if (
                elem_type_obj in (bool, str, int, float, type(None))
                or elem_type_obj is None
            ):
                try:
                    current_set.update(raw_value)
                except TypeError:
                    current_set.add(raw_value)
                setattr(obj, attr_name, current_set)
                continue

            for item in raw_value or []:
                child = _construct_object(elem_type_obj, item, obj)
                if child is None:
                    logger.debug(
                        "deserialize_json: child construction failed k=%s; x=%r",
                        raw_key,
                        item,
                    )
                    continue

                if hasattr(elem_type_obj, "iseq"):
                    dup = False
                    for existing in current_set:
                        try:
                            if existing.iseq(child):
                                dup = True
                                break
                        except Exception:
                            pass
                    if not dup:
                        current_set.add(child)
                else:
                    current_set.add(child)

            setattr(obj, attr_name, current_set)
            continue

        # containers: list
        if declared is list or origin is list:
            current_any_list = getattr(obj, attr_name, None)
            current_list: list[Any] = (
                list(current_any_list) if isinstance(current_any_list, list) else []
            )

            if isinstance(raw_value, list):
                current_list.extend(raw_value)
            else:
                current_list.append(raw_value)

            setattr(obj, attr_name, current_list)
            continue

        # containers: dict (untyped)
        if declared is dict or origin is dict:
            current_any_map = getattr(obj, attr_name, None)
            current_map: dict[Any, Any] = (
                dict(current_any_map) if isinstance(current_any_map, dict) else {}
            )

            if isinstance(raw_value, dict):
                current_map.update(raw_value)

            setattr(obj, attr_name, current_map)
            continue

        # nested object
        if isinstance(declared, type) or (
            declared is not None and not isinstance(declared, str)
        ):
            try:
                child = _construct_object(declared, raw_value, obj)
                setattr(obj, attr_name, child)
            except Exception:
                print(
                    "deserialize_json:error : k=" + raw_key + "; d[k]=" + str(raw_value)
                )
            continue

        setattr(obj, attr_name, raw_value)

    if not required:
        if hasattr(obj, "post_deserialize"):
            obj.post_deserialize(data)
        elif hasattr(obj, "postjson"):
            obj.postjson(data)


def to_string(obj: Any):
    return serialize_json(obj)


def parse(obj: Any, d: Any, nepre: bool = False):
    return deserialize_json(obj, d, required=nepre)


# =========
# Gedcom
# =========


class ExtensibleData:
    """
    Base for Gedcom objects. Some classes index instances by id (global cache),
    others do not because their ids are only unique within a parent.
    """

    _index: ClassVar[Optional[dict[str, Any]]] = None
    id: str

    def __new__(cls, id: Optional[str] = None, tree: Any = None):
        if id:
            index = getattr(cls, "_index", None)
            if isinstance(index, dict):
                existing = index.get(id)
                if existing is not None:
                    return existing
        return super().__new__(cls)

    def __init__(self, id: Optional[str] = None, tree: Any = None):
        init_class(self)
        if id:
            self.id = id
            index = getattr(self.__class__, "_index", None)
            if isinstance(index, dict):
                index[id] = self


class HypermediaEnabledData(ExtensibleData):
    links: dict[str, "Link"]


class HasText:
    text: str

    def __init__(self):
        init_class(self)


class Link:
    href: str
    template: str
    title: str
    type: str
    accept: str
    allow: str
    hreflang: str
    count: int
    offset: int
    results: int

    def __init__(self):
        init_class(self)


class Qualifier:
    name: str
    value: str

    def __init__(self):
        init_class(self)


class ResourceReference:
    resourceId: str
    resource: str

    def __init__(self):
        init_class(self)


class Attribution(ExtensibleData):
    contributor: ResourceReference
    modified: int
    changeMessage: str
    changeMessageResource: str
    creator: ResourceReference
    created: int


class Tag:
    resource: str
    conclusionId: str

    def __init__(self):
        init_class(self)


class OnlineAccount(ExtensibleData):
    serviceHomepage: ResourceReference
    accountName: str


class TextValue:
    lang: str
    value: str

    def __init__(self):
        init_class(self)

    def iseq(self, other: Any) -> bool:
        return (
            isinstance(other, TextValue)
            and self.lang == other.lang
            and self.value == other.value
        )


class Agent(HypermediaEnabledData):
    identifiers: dict[str, set[Any]]
    names: set["TextValue"]
    homepage: ResourceReference
    openid: ResourceReference
    accounts: set["OnlineAccount"]
    emails: set[ResourceReference]
    phones: set[ResourceReference]
    addresses: set[ResourceReference]
    person: ResourceReference


class DiscussionReference(HypermediaEnabledData):
    resourceId: str
    resource: str
    attribution: Attribution


class SourceReference(HypermediaEnabledData):
    description: str
    descriptionId: str
    attribution: Attribution
    qualifiers: set[Qualifier]
    tags: set[Tag]


class ReferencesSources:
    sources: set[SourceReference]

    def __init__(self):
        init_class(self)


class VocabElement:
    id: str
    uri: str
    subclass: str
    type: str
    sortName: str
    labels: set[TextValue]
    descriptions: set[TextValue]
    sublist: str
    position: int

    def __init__(self):
        init_class(self)


class VocabElementList:
    id: str
    title: str
    description: str
    uri: str
    elements: set[VocabElement]

    def __init__(self):
        init_class(self)


class FamilyView(HypermediaEnabledData):
    parent1: ResourceReference
    parent2: ResourceReference
    children: set[ResourceReference]


class Date(ExtensibleData):
    original: str
    formal: DateFormal
    normalized: set[TextValue]
    confidence: str

    def __str__(self) -> str:
        if self.formal:
            return str(self.formal)
        if self.original:
            return self.original
        return ""


class DisplayProperties(ExtensibleData):
    name: str
    gender: str
    lifespan: str
    birthDate: str
    birthPlace: str
    deathDate: str
    deathPlace: str
    marriageDate: str
    marriagePlace: str
    ascendancyNumber: str
    descendancyNumber: str
    relationshipDescription: str
    familiesAsParent: set[FamilyView]
    familiesAsChild: set[FamilyView]
    role: str


class Note(HypermediaEnabledData):
    subject: str
    text: str
    attribution: Attribution
    lang: str


class HasNotes:
    notes: set[Note]

    def __init__(self):
        init_class(self)


class Conclusion(HypermediaEnabledData):
    attribution: Attribution
    sources: set[SourceReference]
    analysis: ResourceReference
    notes: set[Note]
    lang: str
    confidence: str
    sortKey: str


class CitationField:
    def __init__(self):
        init_class(self)


class SourceCitation(TextValue, HypermediaEnabledData):
    citationTemplate: ResourceReference
    fields: set[CitationField]


class PlaceReference(ExtensibleData):
    original: str
    normalized: set[TextValue]
    description: str
    confidence: str
    latitude: float
    longitude: float
    names: set[TextValue]


class HasDateAndPlace:
    date: Date
    place: PlaceReference

    def __init__(self):
        init_class(self)


class Fact(Conclusion):
    date: Date
    place: PlaceReference
    value: str
    qualifiers: set[Qualifier]
    type: str
    id: str


class HasFacts:
    facts: set[Fact]

    def __init__(self):
        init_class(self)


class NamePart(ExtensibleData):
    type: str
    value: str
    qualifiers: set[Qualifier]


class NameFormInfo:
    order: str

    def __init__(self):
        init_class(self)


class NameForm(ExtensibleData):
    lang: str
    parts: set[NamePart]
    fullText: str
    nameFormInfo: set[NameFormInfo]

    def iseq(self, other: Any) -> bool:
        return (
            isinstance(other, NameForm)
            and self.lang == other.lang
            and self.fullText == other.fullText
        )


class Name(Conclusion):
    preferred: bool
    date: Date
    nameForms: set[NameForm]
    type: str

    def akSurname(self) -> str:
        for nf in self.nameForms or []:
            for p in nf.parts or []:
                if p.type == "http://gedcomx.org/Surname":
                    return p.value or ""
        return ""

    def akGiven(self) -> str:
        for nf in self.nameForms or []:
            for p in nf.parts or []:
                if p.type == "http://gedcomx.org/Given":
                    return p.value or ""
        return ""


class EvidenceReference(HypermediaEnabledData):
    resource: str
    resourceId: str
    attribution: Attribution


class Subject(Conclusion):
    evidence: set[EvidenceReference]
    media: set[SourceReference]
    identifiers: dict[str, set[Any]]
    extracted: bool


class Gender(Conclusion):
    type: str


class PersonInfo:
    canUserEdit: bool
    privateSpaceRestricted: bool
    readOnly: bool
    visibleToAll: bool
    visibleToAllWhenUsingFamilySearchApps: bool

    def __init__(self):
        init_class(self)


class Relationship(Subject):
    _index: ClassVar[dict[str, "Relationship"]] = {}
    identifiers: dict[str, set[Any]]
    person1: ResourceReference
    person2: ResourceReference
    facts: set[Fact]
    type: str

    def postjson(self, d: Any) -> None:
        facts = list(self.facts or [])
        if facts:
            has_id = any(getattr(f, "id", None) for f in facts)
            has_missing = any(not getattr(f, "id", None) for f in facts)
            if has_id and has_missing:
                self.facts = {f for f in facts if getattr(f, "id", None)}

        if self.type == "http://gedcomx.org/ParentChild":
            if self.person2 and self.person2.resourceId in Person.index:
                Person.index[self.person2.resourceId]._parents.add(self)
            if self.person1 and self.person1.resourceId in Person.index:
                Person.index[self.person1.resourceId]._children.add(self)

        if self.type == "http://gedcomx.org/Couple":
            if self.person1 and self.person1.resourceId in Person.index:
                Person.index[self.person1.resourceId]._spouses.add(self)
            if self.person2 and self.person2.resourceId in Person.index:
                Person.index[self.person2.resourceId]._spouses.add(self)


class ChildAndParentsRelationship(Subject):
    _index: ClassVar[dict[str, "ChildAndParentsRelationship"]] = {}
    parent1: ResourceReference
    parent2: ResourceReference
    child: ResourceReference
    parent1Facts: set[Fact]
    parent2Facts: set[Fact]

    def postjson(self, d: Any) -> None:
        if self.child and self.child.resourceId in Person.index:
            Person.index[self.child.resourceId]._parentsCP.add(self)
        if self.parent1 and self.parent1.resourceId in Person.index:
            Person.index[self.parent1.resourceId]._childrenCP.add(self)
        if self.parent2 and self.parent2.resourceId in Person.index:
            Person.index[self.parent2.resourceId]._childrenCP.add(self)


class Value:
    lang: str
    type: str
    text: str

    def __init__(self):
        init_class(self)


class Field:
    type: str
    values: set[Value]

    def __init__(self):
        init_class(self)


class Person(Subject):
    _index: ClassVar[dict[str, "Person"]] = {}
    index: ClassVar[dict[str, "Person"]] = _index
    private: bool
    living: bool
    gender: Gender
    names: set[Name]
    facts: set[Fact]
    display: DisplayProperties
    personInfo: set[PersonInfo]
    discussion_references: set[DiscussionReference]
    fields: set[Field]
    sortKey: str

    _parents: set[Relationship]
    _children: set[Relationship]
    _spouses: set[Relationship]
    _childrenCP: set[ChildAndParentsRelationship]
    _parentsCP: set[ChildAndParentsRelationship]

    def preferred_name(self):
        for n in self.names or []:
            if n.preferred:
                return n
        if self.names:
            return next(iter(self.names))
        return Name()


class Coverage(HypermediaEnabledData):
    spatial: PlaceReference
    temporal: Date


class artifactMetadata:
    filename: str
    qualifiers: set[Qualifier]
    width: int
    height: int
    size: int
    screeningState: str
    displayState: str
    editable: bool

    def __init__(self):
        init_class(self)


class SourceDescription(Conclusion):
    _index: ClassVar[dict[str, "SourceDescription"]] = {}
    citations: set[SourceCitation]
    mediator: ResourceReference
    publisher: ResourceReference
    authors: set[str]
    componentOf: SourceReference
    titles: set[TextValue]
    identifiers: dict[str, set[Any]]
    rights: set[str]
    replacedBy: str
    replaces: set[str]
    statuses: set[str]
    about: str
    version: str
    resourceType: str
    mediaType: str
    coverage: set[Coverage]
    descriptions: set[TextValue]
    created: int
    modified: int
    published: int
    repository: Agent
    artifactMetadata: set[artifactMetadata]


class Address(ExtensibleData):
    city: str
    country: str
    postalCode: str
    stateOrProvince: str
    street: str
    street2: str
    street3: str
    street4: str
    street5: str
    street6: str
    value: str


class EventRole(Conclusion):
    person: str
    type: str


class Event(Subject):
    type: str
    date: Date
    place: PlaceReference
    roles: set[EventRole]


class Document(Conclusion):
    type: str
    extracted: bool
    textType: str
    text: str
    attribution: Attribution


class GroupRole(Conclusion):
    person: str
    type: str
    date: Date
    details: str


class Group(Subject):
    names: set[TextValue]
    date: Date
    place: PlaceReference
    roles: GroupRole


class PlaceDisplayProperties(ExtensibleData):
    name: str
    fullName: str
    type: str


class PlaceDescriptionInfo:
    zoomLevel: int
    relatedType: str
    relatedSubType: str

    def __init__(self):
        init_class(self)


class PlaceDescription(Subject):
    _index: ClassVar[dict[str, "PlaceDescription"]] = {}
    names: set[TextValue]
    temporalDescription: Date
    latitude: float
    longitude: float
    spatialDescription: ResourceReference
    place: ResourceReference
    jurisdiction: ResourceReference
    display: PlaceDisplayProperties
    type: str
    placeDescriptionInfo: set[PlaceDescriptionInfo]


def _unwrap_fs_envelope(payload: Any) -> Any:
    """
    FamilySearch sometimes wraps content like:
      {"person": {"persons": [...]}, "etag": "...", "last_modified": ...}
    We merge wrapper keys into the same dict so the raw mapper sees "persons", etc.
    """
    if not isinstance(payload, dict):
        return payload

    if "person" in payload and isinstance(payload["person"], dict):
        merged = dict(payload)
        inner = payload["person"]
        for k, v in inner.items():
            merged.setdefault(k, v)
        merged.pop("person", None)
        return merged

    return payload


class Gedcomx(HypermediaEnabledData):
    etag: str
    last_modified: int
    attribution: Attribution

    persons: set[Person]
    relationships: set[Relationship]
    sourceDescriptions: set[SourceDescription]
    agents: set[Agent]
    events: set[Event]
    places: set[PlaceDescription]
    documents: set[Document]
    groups: set[Group]

    lang: str
    description: str
    notes: Note
    childAndParentsRelationships: set[ChildAndParentsRelationship]
    sourceReferences: set[SourceReference]
    genders: set[Gender]
    names: set[Name]
    facts: set[Fact]

    def deserialize_json(self, data: Any) -> None:
        """
        FS-aware entry point:
        - keep metadata if present
        - unwrap common FS envelope(s)
        - then run the raw field-mapper (required=True) to avoid recursion loops
        """
        if isinstance(data, dict):
            if "etag" in data:
                self.etag = data["etag"]
            if "last_modified" in data:
                self.last_modified = data["last_modified"]

        data2 = _unwrap_fs_envelope(data)
        deserialize_json(self, data2, required=True)
