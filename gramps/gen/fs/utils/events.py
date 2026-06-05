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

# -------------------------------------------------------------------------
#
# Future imports
#
# -------------------------------------------------------------------------
from __future__ import annotations

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from typing import Optional

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Event, Person
from gramps.gen.lib import EventRoleType


def get_fs_fact(person, fact_type):
    # Return the first FamilySearch fact on person matching fact_type
    if not person:
        return None
    for fact in getattr(person, "facts", []) or []:
        if getattr(fact, "type", None) == fact_type:
            return fact
    return None


def get_gramps_event(db, person: Optional[Person], event_type) -> Optional[Event]:
    # return the first Gramps Event of event_type where role is PRIMARY
    if not person:
        return None
    for event_ref in person.get_event_ref_list():
        try:
            if int(event_ref.get_role()) != EventRoleType.PRIMARY:
                continue
        except Exception:
            continue
        event = db.get_event_from_handle(event_ref.ref)
        if event and event.get_type() == event_type:
            return event
    return None
