#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2025  Gabriel Rios
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

from __future__ import annotations

# ------------------------
# Python modules
# ------------------------
from typing import Any
from urllib.parse import unquote

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.db import DbTxn
from gramps.gen.db.base import DbWriteBase
from gramps.gen.lib import Event, Attribute, Date, Family, Person
from gramps.gen.types import PlaceHandle

from gramps.gen.fs.utils import fs_date_to_gramps_date, get_fsftid
from gramps.gen.fs.constants import GEDCOMX_TO_GRAMPS_FACTS

# ------------------------
# Gramps specific
# ------------------------
from .places import get_place_by_id, add_place
from .notes import add_note


def update_event(db: DbWriteBase, txn: DbTxn, fs_fact: Any, gr_event: Event) -> None:
    """
    Apply the imported date, place and description to an existing event.

    :param db: The destination database.
    :param txn: The active import transaction.
    :param fs_fact: The downloaded FamilySearch fact.
    :param gr_event: The native event to update.
    """
    place_handle: PlaceHandle | None = None
    if fs_fact.place:
        gr_place = get_place_by_id(db, fs_fact.place)
        if gr_place is None:
            gr_place = add_place(db, txn, fs_fact.place)
        if gr_place is not None:
            place_handle = gr_place.handle

    gr_date = fs_date_to_gramps_date(fs_fact.date)
    before = gr_event.serialize()
    if gr_date is not None:
        gr_event.set_date_object(gr_date)
    elif fs_fact.date is None or not (
        fs_fact.date.original or fs_fact.date.formal or fs_fact.date.normalized
    ):
        gr_event.set_date_object(Date())
    if (
        place_handle is not None
        or fs_fact.place is None
        or not (
            fs_fact.place.original
            or fs_fact.place.description
            or fs_fact.place.normalized
            or getattr(fs_fact.place, "id", None)
        )
    ):
        gr_event.set_place_handle(place_handle or PlaceHandle(""))
    gr_event.set_description(fs_fact.value or "")
    if gr_event.serialize() != before:
        db.commit_event(gr_event, txn)


def add_event(db: DbWriteBase, txn: DbTxn, fs_fact: Any, obj: Person | Family) -> Event:
    """
    Import a fact, updating date, place and description on its linked event.

    :param db: The destination database.
    :param txn: The active import transaction.
    :param fs_fact: The downloaded FamilySearch fact.
    :param obj: The person or family receiving the event.
    :returns: The existing or newly imported event.
    """
    evt_type = GEDCOMX_TO_GRAMPS_FACTS.get(unquote(fs_fact.type))
    if not evt_type:
        if fs_fact.type[:6] == "data:,":
            evt_type = unquote(fs_fact.type[6:])
        else:
            evt_type = fs_fact.type

    # Match by FSFTID before creating another event.
    for er in obj.event_ref_list:
        event = db.get_event_from_handle(er.ref)
        if fs_fact.id and get_fsftid(event) == fs_fact.id:
            update_event(db, txn, fs_fact, event)
            return event

    place_handle: PlaceHandle | None = None
    if fs_fact.place:
        if not hasattr(fs_fact.place, "normalized"):
            print("place not normalized: " + fs_fact.place.original)
        gr_place = get_place_by_id(db, fs_fact.place)
        if gr_place:
            place_handle = gr_place.handle
        else:
            gr_place = add_place(db, txn, fs_fact.place)
            if gr_place:
                place_handle = gr_place.handle

    fs_desc = fs_fact.value or ""
    gr_date = fs_date_to_gramps_date(fs_fact.date)

    for er in obj.event_ref_list:
        e = db.get_event_from_handle(er.ref)
        gr_type = (
            int(e.type)
            if isinstance(e.type, int) or hasattr(e.type, "__int__")
            else e.type
        )
        if gr_type == evt_type:
            same_place = (e.get_place_handle() == place_handle) or (
                not e.get_place_handle() and not place_handle
            )
            same_desc = (e.description == fs_desc) or (
                not e.description and not fs_desc
            )
            if e.get_date_object() == gr_date and same_place and same_desc:
                return e
            if (
                e.get_date_object().is_empty()
                and not gr_date
                and same_place
                and same_desc
            ):
                return e

    event = Event()
    event.set_type(evt_type)
    if place_handle:
        event.set_place_handle(place_handle)
    if gr_date:
        event.set_date_object(gr_date)
    event.set_description(fs_desc)
    if fs_fact.id:
        a = Attribute()
        a.set_type("_FSFTID")
        a.set_value(fs_fact.id)
        event.add_attribute(a)

    # notes on the event
    for fs_note in fs_fact.notes:
        note = add_note(db, txn, fs_note, event.note_list)
        event.add_note(note.handle)

    db.add_event(event, txn)
    db.commit_event(event, txn)
    return event
