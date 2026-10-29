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

"""Read-only structured search prefill from saved or unsaved native people."""

from __future__ import annotations

# ------------------------
# Python modules
# ------------------------
from typing import Any, Callable

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.db.base import DbReadBase
from gramps.gen.errors import HandleError
from gramps.gen.fs.search_context import LocalFact, SearchPolicy, vital_filters
from gramps.gen.fs.search import SearchQuery
from gramps.gen.lib import ChildRefType, Person
from gramps.gen.types import PersonHandle


def _read(reader: Callable[..., Any], handle: str) -> Any:
    """Ignore missing referenced objects without interpreting them as empty facts."""
    if not handle:
        return None
    try:
        return reader(handle)
    except HandleError:
        return None


def _names(person: Person | None) -> tuple[str, str]:
    """Keep native name parts, including historical spelling and surname prefixes."""
    if person is None:
        return "", ""
    name = person.get_primary_name()
    return name.get_first_name(), name.get_surname()


def person_query(
    db: DbReadBase, person: Person, policy: SearchPolicy = SearchPolicy()
) -> SearchQuery:
    """Prefill conservative hints without saving or traversing the evidence graph.

    :param db: Open native tree, read only during projection.
    :param person: Editor draft or saved Person; never reloaded over dirty edits.
    :param policy: Finite year margin shared with the background matcher.
    :returns: Editable query hints, without identity conclusions or bindings.

    Parent slots come from actual family roles and explicit birth relationships,
    never a relative's sex. Multiple or uncertain alternatives remain blank.
    Referenced events/places/families must already exist in the open tree.
    """
    facts: list[LocalFact] = []
    for reference in person.get_event_ref_list():
        event = _read(db.get_event_from_handle, reference.ref)
        if event is None:
            continue
        date = event.get_date_object()
        place = _read(db.get_place_from_handle, event.place)
        facts.append(
            LocalFact(
                event.get_type().xml_str(),
                reference.get_role().xml_str(),
                reference.ref,
                date.get_year(),
                date.get_month(),
                date.get_day(),
                date.get_modifier(),
                date.get_quality(),
                date.get_calendar(),
                str(date),
                place.get_title() if place is not None else "",
            )
        )
    birth_from, birth_to, birth_place = vital_filters(
        tuple(facts), "Birth", policy.year_margin
    )
    death_from, death_to, death_place = vital_filters(
        tuple(facts), "Death", policy.year_margin
    )
    parents: dict[str, set[PersonHandle]] = {"father": set(), "mother": set()}
    uncertain: set[str] = set()
    if person.handle:
        for family_handle in person.get_parent_family_handle_list():
            family = _read(db.get_family_from_handle, family_handle)
            if family is None:
                uncertain.update(parents)
                continue
            children = [
                child
                for child in family.get_child_ref_list()
                if child.ref == person.handle
            ]
            if not children:
                uncertain.update(parents)
            for child in children:
                for role, parent, relation in (
                    ("father", family.get_father_handle(), child.get_father_relation()),
                    ("mother", family.get_mother_handle(), child.get_mother_relation()),
                ):
                    if parent:
                        if int(relation) == ChildRefType.BIRTH:
                            parents[role].add(PersonHandle(parent))
                        else:
                            uncertain.add(role)
    parent_names: dict[str, tuple[str, str]] = {}
    for role, handles in parents.items():
        parent_names[role] = (
            _names(_read(db.get_person_from_handle, next(iter(handles))))
            if len(handles) == 1 and role not in uncertain
            else ("", "")
        )
    spouses: set[PersonHandle] = set()
    incomplete_spouses = False
    if person.handle:
        for family_handle in person.get_family_handle_list():
            family = _read(db.get_family_from_handle, family_handle)
            if family is None:
                incomplete_spouses = True
                continue
            partners = (family.get_father_handle(), family.get_mother_handle())
            if person.handle in partners:
                spouses.update(
                    PersonHandle(handle)
                    for handle in partners
                    if handle and handle != person.handle
                )
            else:
                incomplete_spouses = True
    spouse_given, spouse_surname = (
        _names(_read(db.get_person_from_handle, next(iter(spouses))))
        if len(spouses) == 1 and not incomplete_spouses
        else ("", "")
    )
    given_name, surname = _names(person)
    return SearchQuery(
        given_name=given_name,
        surname=surname,
        birth_from=birth_from,
        birth_to=birth_to,
        birth_place=birth_place,
        death_from=death_from,
        death_to=death_to,
        death_place=death_place,
        father_given=parent_names["father"][0],
        father_surname=parent_names["father"][1],
        mother_given=parent_names["mother"][0],
        mother_surname=parent_names["mother"][1],
        spouse_given=spouse_given,
        spouse_surname=spouse_surname,
    )
