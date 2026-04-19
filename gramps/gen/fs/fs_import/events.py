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

from urllib.parse import unquote

from gramps.gen.lib import Event, Attribute

from . import _
from .places import get_place_by_id, add_place
from .notes import add_note
from gramps.gen.fs.utils import fs_date_to_gramps_date, get_fsftid
from gramps.gen.fs.constants import GEDCOMX_TO_GRAMPS_FACTS


def update_event(db, txn, fs_fact, gr_event):
    # Update a Gramps Event from a FS fact (place/date/description). Commits event
    if fs_fact.place:
        if not hasattr(fs_fact.place, "normalized"):
            print("place not normalized: " + fs_fact.place.original)
        gr_place = get_place_by_id(db, fs_fact.place)
        if gr_place:
            gr_handle = gr_place.handle
        else:
            add_place(db, txn, fs_fact.place)
            gr_handle = fs_fact.place._handle
        gr_event.set_place_handle(gr_handle)

    gr_date = fs_date_to_gramps_date(fs_fact.date)
    if gr_date:
        gr_event.set_date_object(gr_date)
    gr_event.set_description(fs_fact.value or "")
    db.commit_event(gr_event, txn)


def add_event(db, txn, fs_fact, obj):
    evt_type = GEDCOMX_TO_GRAMPS_FACTS.get(unquote(fs_fact.type))
    if not evt_type:
        if fs_fact.type[:6] == "data:,":
            evt_type = unquote(fs_fact.type[6:])
        else:
            evt_type = fs_fact.type

    place_handle = None
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

    # match by FSFTID first
    for er in obj.event_ref_list:
        e = db.get_event_from_handle(er.ref)
        if get_fsftid(e) == fs_fact.id:
            return e

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
