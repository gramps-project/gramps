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

"""Guarded local public-PID changes using current native Person objects."""

from __future__ import annotations

# ------------------------
# Python modules
# ------------------------
import json
from dataclasses import dataclass
from typing import Any

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.fs.search import person_id_from_text
from gramps.gen.fs.session import FSException
from gramps.gen.fs.utils.index import FS_INDEX_PEOPLE
from gramps.gen.lib import Attribute, Person
from gramps.gen.types import PersonHandle

_ = glocale.translation.gettext
PUBLIC_TYPES = frozenset({"_FSFTID", "_FSTID", "FamilySearch ID"})


def public_bindings(person: Person) -> tuple[tuple[str, str], ...]:
    """Read every public binding, including malformed values, for preconditions."""
    return tuple(
        (str(attr.get_type()), attr.get_value())
        for attr in person.get_attribute_list()
        if str(attr.get_type()) in PUBLIC_TYPES
    )


def binding_payload(person: Person) -> tuple[str, ...]:
    """Capture complete public attributes, including privacy, notes and citations."""
    return tuple(
        json.dumps(attribute.serialize(), ensure_ascii=False, sort_keys=True)
        for attribute in person.get_attribute_list()
        if str(attribute.get_type()) in PUBLIC_TYPES
    )


def restore_payload(
    person: Person, expected: tuple[str, ...], target: tuple[str, ...]
) -> None:
    """Replace only public attributes, preserving subsequent unrelated edits."""
    if binding_payload(person) != expected or len(target) > 1:
        raise ValueError(
            _("The FamilySearch binding changed. Review this batch again.")
        )
    attributes = person.get_attribute_list()
    positions = [
        index
        for index, value in enumerate(attributes)
        if str(value.get_type()) in PUBLIC_TYPES
    ]
    position = positions[0] if positions else len(attributes)
    attributes = [
        value for value in attributes if str(value.get_type()) not in PUBLIC_TYPES
    ]
    for payload in target:
        attribute = Attribute()
        attribute.unserialize(json.loads(payload))
        if str(attribute.get_type()) not in PUBLIC_TYPES:
            raise ValueError(_("Invalid public binding receipt."))
        attributes.insert(min(position, len(attributes)), attribute)
    person.set_attribute_list(attributes)


def replace_binding(
    person: Person, expected: tuple[tuple[str, str], ...], pid: str
) -> None:
    """Change only binding values while preserving attribute metadata and edits.

    :param person: The current native or editor Person object.
    :param expected: The exact binding state reviewed by the user.
    :param pid: The validated canonical public Person PID, or empty for undo.
    :raises FSException: On a changed or ambiguous binding state.
    """
    if public_bindings(person) != expected or len(expected) > 1:
        raise FSException(_("The FamilySearch link changed. Review it again."))
    if pid and person_id_from_text(pid) != pid:
        raise FSException(_("A public FamilySearch link must be a plain person ID."))
    attrs = person.get_attribute_list()
    existing = next(
        (attr for attr in attrs if str(attr.get_type()) in PUBLIC_TYPES), None
    )
    if existing is not None:
        if pid:
            existing.set_value(pid)
        else:
            attrs.remove(existing)
    elif pid:
        attr = Attribute()
        attr.set_type("_FSFTID")
        attr.set_value(pid)
        attrs.append(attr)
    person.set_attribute_list(attrs)


# ------------------------------------------------------------
# LinkPlan
# ------------------------------------------------------------
@dataclass(frozen=True)
class LinkPlan:
    """A current-session binding precondition, independent of dirty editor facts."""

    database_token: int
    handle: PersonHandle
    before: tuple[tuple[str, str], ...]
    person_id: str


def plan_link(db: Any, handle: PersonHandle, canonical_id: str) -> LinkPlan:
    """Prepare a local change after a caller has reviewed fresh canonical evidence.

    :param db: The currently open native database, not a filesystem path.
    :param handle: The saved local person selected for review.
    :param canonical_id: A freshly resolved PID explicitly confirmed by the user.
    :returns: The binding precondition to revalidate when applying.
    """
    if person_id_from_text(canonical_id) != canonical_id or not canonical_id:
        raise FSException(_("A public FamilySearch link must be a plain person ID."))
    person = db.get_person_from_handle(handle)
    if person is None:
        raise FSException(_("The local person no longer exists."))
    before = public_bindings(person)
    if len(before) > 1:
        raise FSException(
            _("This person has multiple FamilySearch links. Resolve them first.")
        )
    return LinkPlan(id(db), handle, before, canonical_id)


def apply_link(db: Any, plan: LinkPlan) -> Person:
    """Revalidate identity/duplicates and commit only the current object's binding.

    The GUI must invoke this on its database thread, after network work finishes.
    No remote writes, fact imports or editor-object commits occur here.

    :param db: The same open database used to create the plan.
    :param plan: The reviewed binding change.
    :returns: The committed native Person, for binding-only editor reconciliation.
    """
    if id(db) != plan.database_token or getattr(db, "readonly", True):
        raise FSException(
            _("The tree changed or is read-only. Review this link again.")
        )
    # Native transactions are serialized by the application database thread.
    with DbTxn(_("Link FamilySearch person"), db) as transaction:
        person = db.get_person_from_handle(plan.handle)
        if person is None:
            raise FSException(_("The local person no longer exists."))
        for candidate in db.iter_people():
            if candidate.handle == plan.handle:
                continue
            if any(
                person_id_from_text(value) == plan.person_id
                for _kind, value in public_bindings(candidate)
            ):
                raise FSException(
                    _("This FamilySearch ID is already linked to another local person.")
                )
        replace_binding(person, plan.before, plan.person_id)
        db.commit_person(person, transaction)
    for _kind, old_id in plan.before:
        if FS_INDEX_PEOPLE.get(old_id) == plan.handle and old_id != plan.person_id:
            del FS_INDEX_PEOPLE[old_id]
    FS_INDEX_PEOPLE[plan.person_id] = plan.handle
    return person
