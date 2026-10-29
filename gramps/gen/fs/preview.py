#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gabriel Rios
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""Fresh canonical person and family previews, without global deserializer state."""

from __future__ import annotations

# ------------------------
# Python modules
# ------------------------
from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any

import requests

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.fs.search import person_id_from_text
from gramps.gen.fs.session import FSException

_ = glocale.translation.gettext


# ------------------------------------------------------------
# FactPreview
# ------------------------------------------------------------
@dataclass(frozen=True)
class FactPreview:
    """Source-stated values; no normalization into a genealogical conclusion."""

    kind: str
    date: str = ""
    formal_date: str = ""
    place: str = ""
    place_id: str = ""


# ------------------------------------------------------------
# PersonPreview
# ------------------------------------------------------------
@dataclass(frozen=True)
class PersonPreview:
    """Minimal immutable person details for comparison and review."""

    person_id: str
    names: tuple[str, ...] = ()
    gender: str = ""
    living: bool | None = None
    facts: tuple[FactPreview, ...] = ()


# ------------------------------------------------------------
# RelationshipPreview
# ------------------------------------------------------------
@dataclass(frozen=True)
class RelationshipPreview:
    """Actual API relationship to the subject, not a display-name suggestion.

    Relationship facts remain attached to the relationship. A parent role alone
    does not establish biological or documentary parentage.
    """

    role: str
    person: PersonPreview
    relationship_id: str
    facts: tuple[FactPreview, ...] = ()


# ------------------------------------------------------------
# FamilyPreview
# ------------------------------------------------------------
@dataclass(frozen=True)
class FamilyPreview:
    """A fresh subject and its recorded relationships, with merge provenance."""

    requested_id: str
    person: PersonPreview
    relatives: tuple[RelationshipPreview, ...]
    redirected_ids: tuple[str, ...] = ()


def _objects(value: Any, field: str) -> list[dict[str, Any]]:
    """Read an optional object array, rejecting partial or malformed evidence."""
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise FSException(_("FamilySearch returned invalid %s data.") % field)
    return value


def _facts(value: Any) -> tuple[FactPreview, ...]:
    """Keep original date/place text and machine values separately."""
    result = []
    for fact in _objects(value, "fact"):
        date = fact.get("date") or {}
        place = fact.get("place") or {}
        if not isinstance(date, dict) or not isinstance(place, dict):
            raise FSException(_("FamilySearch returned invalid fact data."))
        result.append(
            FactPreview(
                str(fact.get("type") or ""),
                str(date.get("original") or ""),
                str(date.get("formal") or ""),
                str(place.get("original") or ""),
                str(place.get("description") or ""),
            )
        )
    return tuple(result)


def parse_person(data: dict[str, Any]) -> PersonPreview:
    """Read a tree person without inferring names, sex or vital dates."""
    pid = person_id_from_text(str(data.get("id") or ""))
    if not pid:
        raise FSException(_("FamilySearch returned an invalid person ID."))
    names: list[str] = []
    for name in _objects(data.get("names"), "name"):
        for form in _objects(name.get("nameForms"), "name form"):
            text = str(form.get("fullText") or "").strip()
            if text and text not in names:
                names.append(text)
    display = data.get("display") or {}
    gender = data.get("gender") or {}
    if not isinstance(display, dict) or not isinstance(gender, dict):
        raise FSException(_("FamilySearch returned invalid person data."))
    if not names and display.get("name"):
        names.append(str(display["name"]))
    living = data.get("living")
    return PersonPreview(
        pid,
        tuple(names),
        str(gender.get("type") or ""),
        living if isinstance(living, bool) else None,
        _facts(data.get("facts")),
    )


def _reference(value: Any) -> str:
    """Resolve only a PID reference; never follow arbitrary relationship URLs."""
    if value is None:
        return ""
    if not isinstance(value, dict):
        raise FSException(_("FamilySearch returned invalid relationship data."))
    rid = str(value.get("resourceId") or "")
    resource = str(value.get("resource") or "")
    pid = person_id_from_text(rid or resource.removeprefix("#"))
    if not pid:
        raise FSException(_("FamilySearch returned an invalid relative ID."))
    if rid and resource and pid != person_id_from_text(resource.removeprefix("#")):
        raise FSException(_("FamilySearch returned inconsistent relative IDs."))
    return pid


def parse_family(
    subject: PersonPreview, data: dict[str, Any]
) -> tuple[RelationshipPreview, ...]:
    """Select relationships touching the subject, preserving relationship roles.

    :param subject: The independently fetched canonical subject.
    :param data: The families response for that subject.
    :returns: Direct relatives only; embedded unrelated people are not candidates.
    """
    people: dict[str, PersonPreview] = {}
    for item in _objects(data.get("persons"), "person"):
        person = parse_person(item)
        if person.person_id in people:
            raise FSException(_("FamilySearch returned duplicate person data."))
        people[person.person_id] = person
    if subject.person_id not in people:
        raise FSException(
            _("FamilySearch did not return the requested family subject.")
        )
    result: dict[tuple[str, str, str], RelationshipPreview] = {}

    def add(role: str, pid: str, relationship: dict[str, Any], facts: Any) -> None:
        """Keep one observation per actual relationship, not per display label."""
        if not pid or pid == subject.person_id:
            return
        rel_id = str(relationship.get("id") or "")
        result[role, pid, rel_id] = RelationshipPreview(
            role, people.get(pid, PersonPreview(pid)), rel_id, _facts(facts)
        )

    for relation in _objects(data.get("relationships"), "relationship"):
        first = _reference(relation.get("person1"))
        second = _reference(relation.get("person2"))
        kind = str(relation.get("type") or "")
        if kind == "http://gedcomx.org/ParentChild":
            if first == subject.person_id:
                add("child", second, relation, relation.get("facts"))
            if second == subject.person_id:
                add("parent", first, relation, relation.get("facts"))
        else:
            links = relation.get("links") or {}
            link = links.get("relationship") or {} if isinstance(links, dict) else {}
            href = str(link.get("href") or "") if isinstance(link, dict) else ""
            is_couple = kind == "http://gedcomx.org/Couple" or (
                not kind and "/couple-relationships/" in href
            )
            if is_couple and subject.person_id in (first, second):
                add(
                    "spouse",
                    second if first == subject.person_id else first,
                    relation,
                    relation.get("facts"),
                )
    for relation in _objects(data.get("childAndParentsRelationships"), "family"):
        child = _reference(relation.get("child"))
        for position in ("parent1", "parent2"):
            parent = _reference(relation.get(position))
            facts = relation.get(position + "Facts")
            if child == subject.person_id:
                add("parent", parent, relation, facts)
            if parent == subject.person_id:
                add("child", child, relation, facts)
    return tuple(result.values())


# ------------------------------------------------------------
# PreviewService
# ------------------------------------------------------------
class PreviewService:
    """Fetch fresh read-only previews through the caller's authorized session."""

    def __init__(self, session: Any) -> None:
        """Pin the transport rather than changing a global deserializer session."""
        self.session = session

    def _read(
        self, pid: str, suffix: str = ""
    ) -> tuple[str, dict[str, Any], tuple[str, ...]]:
        """Follow explicit merged-PID headers only, bounded against cycles."""
        visited: list[str] = []
        while pid not in visited and len(visited) < 20:
            visited.append(pid)
            try:
                response = self.session.get_url(
                    f"/platform/tree/persons/{pid}{suffix}",
                    allow_redirects=False,
                    headers={"Accept": "application/x-fs-v1+json"},
                )
            except requests.RequestException as error:
                raise FSException(
                    _("FamilySearch preview could not connect. Try again later.")
                ) from error
            status = getattr(response, "status_code", None)
            if status == 301:
                forwarded = str(response.headers.get("X-Entity-Forwarded-Id", ""))
                # A forwarded header is a PID, never a URL to follow with auth.
                if (
                    person_id_from_text(forwarded) != forwarded.strip().upper()
                    or not forwarded.strip()
                ):
                    raise FSException(
                        _("FamilySearch returned an invalid merged person ID.")
                    )
                pid = forwarded.strip().upper()
                continue
            if status != 200:
                raise FSException(_("FamilySearch preview failed (HTTP %s).") % status)
            try:
                data = response.json()
            except (ValueError, TypeError) as error:
                raise FSException(
                    _("FamilySearch returned invalid preview data.")
                ) from error
            payload = data.get("person", data) if isinstance(data, dict) else None
            if not isinstance(payload, dict):
                raise FSException(_("FamilySearch returned invalid preview data."))
            return pid, payload, tuple(visited[:-1])
        raise FSException(_("FamilySearch returned a circular merged person redirect."))

    def preview(self, value: str) -> FamilyPreview:
        """Read a current person and actual family graph without assigning an ID.

        :param value: A PID or recognized tree-person URL.
        :returns: A canonical preview, with the requested alias retained.
        :raises FSException: For access, malformed data or an unstable merged ID.
        """
        requested = person_id_from_text(value)
        if not requested:
            raise FSException(_("Enter a FamilySearch person ID or person link."))
        current = requested
        aliases: list[str] = []
        for attempt in range(3):
            current, data, redirected = self._read(current)
            aliases.extend(pid for pid in redirected if pid not in aliases)
            people = [
                parse_person(item) for item in _objects(data.get("persons"), "person")
            ]
            subjects = [person for person in people if person.person_id == current]
            if len(subjects) != 1:
                raise FSException(
                    _("FamilySearch did not return the requested person.")
                )
            family_id, family, redirected = self._read(current, "/families")
            aliases.extend(pid for pid in redirected if pid not in aliases)
            if family_id != current:
                if attempt == 2:
                    break
                current = family_id
                continue
            return FamilyPreview(
                requested,
                subjects[0],
                parse_family(subjects[0], family),
                tuple(aliases),
            )
        raise FSException(
            _("This FamilySearch person changed while loading. Try again.")
        )


def person_fingerprint(person: PersonPreview) -> str:
    """Hash identity facts without timestamp churn or unrelated family additions."""
    data = asdict(person)
    data["names"] = sorted(data["names"])
    data["facts"] = sorted(
        data["facts"], key=lambda value: json.dumps(value, sort_keys=True)
    )
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def preview_from_data(value: dict[str, Any]) -> FamilyPreview:
    """Decode a saved matching comparison, never a native serialized Person."""

    def person(data: dict[str, Any]) -> PersonPreview:
        """Restore immutable person facts from private operational state."""
        return PersonPreview(
            data["person_id"],
            tuple(data["names"]),
            data["gender"],
            data["living"],
            tuple(FactPreview(**fact) for fact in data["facts"]),
        )

    return FamilyPreview(
        value["requested_id"],
        person(value["person"]),
        tuple(
            RelationshipPreview(
                item["role"],
                person(item["person"]),
                item["relationship_id"],
                tuple(FactPreview(**fact) for fact in item["facts"]),
            )
            for item in value["relatives"]
        ),
        tuple(value["redirected_ids"]),
    )
