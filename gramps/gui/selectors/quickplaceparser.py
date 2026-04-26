#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Doug Blank <doug.blank@gmail.com>
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

"""
Utility functions for parsing a comma-separated place hierarchy string and
committing any new Place objects to the database.

No GTK dependency — fully testable without a display.

Typical call sequence:
    parsed = parse_place_hierarchy(db, "Springfield, Illinois, USA")
    # show confirmation UI using parsed list
    handle = commit_place_hierarchy(db, parsed, with_transaction)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from gramps.gen.lib import Place, PlaceName, PlaceRef, PlaceType

if TYPE_CHECKING:
    from gramps.gen.db import DbGeneric


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_place_hierarchy(db: "DbGeneric", text: str) -> list[dict]:
    """
    Parse *text* as a comma-separated place hierarchy (most-specific first).

    Returns a list of dicts, one per token, ordered from most-specific to
    most-general.  Each dict has:
        name   (str)  — stripped token
        handle (str | None) — existing Place handle, or None if not found
        status (str)  — "existing" | "new"

    Example:
        parse_place_hierarchy(db, "Springfield, Illinois, USA")
        → [
            {"name": "Springfield", "handle": "abc123", "status": "existing"},
            {"name": "Illinois",    "handle": None,     "status": "new"},
            {"name": "USA",         "handle": "def456", "status": "existing"},
          ]

    Parent context is taken into account: "Springfield" is only considered
    a match if it is a child of whatever place resolves as "Illinois".
    Resolution is done outer-to-inner so that parent handles are known before
    searching children.
    """
    tokens = [t.strip() for t in text.split(",") if t.strip()]
    if not tokens:
        return []

    entries: list[dict] = [{"name": t, "handle": None, "status": "new"} for t in tokens]

    # Resolve from the outermost (last token) inward.
    # entries[-1] has no required parent; entries[0] must be a child of entries[1].
    for i in range(len(entries) - 1, -1, -1):
        parent_handle = entries[i + 1]["handle"] if i + 1 < len(entries) else None
        handle = _find_place_child(db, entries[i]["name"], parent_handle)
        if handle is not None:
            entries[i]["handle"] = handle
            entries[i]["status"] = "existing"

    return entries


def commit_place_hierarchy(
    db: "DbGeneric",
    parsed: list[dict],
    with_transaction,
    default_type: PlaceType | None = None,
) -> str | None:
    """
    Commit any "new" places in *parsed* to the database and wire PlaceRefs.

    *parsed* is the list returned by :func:`parse_place_hierarchy`, possibly
    modified by the user (e.g. PlaceType overrides).  Each "new" entry must
    additionally carry a ``place_type`` key (a :class:`PlaceType` instance);
    if missing, *default_type* is used (falls back to ``PlaceType()``).

    *with_transaction* must be an active ``DbTxn`` context (the caller owns
    the transaction so that multiple operations can be batched).

    Returns the handle of the most-specific place (entries[0]), whether it
    was pre-existing or newly created.  Returns None if *parsed* is empty.
    """
    if not parsed:
        return None

    if default_type is None:
        default_type = PlaceType()

    # Build from outermost → innermost so that parent handles exist when
    # we need to attach a PlaceRef to a child.
    for i in range(len(parsed) - 1, -1, -1):
        entry = parsed[i]
        if entry["status"] == "existing":
            continue

        place = Place()
        name = PlaceName()
        name.set_value(entry["name"])
        place.set_name(name)
        place.set_type(entry.get("place_type", default_type))

        parent_handle = parsed[i + 1]["handle"] if i + 1 < len(parsed) else None
        if parent_handle is not None:
            ref = PlaceRef()
            ref.ref = parent_handle
            place.add_placeref(ref)

        db.add_place(place, with_transaction)
        entry["handle"] = place.get_handle()

    return parsed[0]["handle"]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _find_place_child(
    db: "DbGeneric", name: str, parent_handle: str | None
) -> str | None:
    """
    Search *db* for a Place whose primary name matches *name* (case-insensitive)
    and whose placeref_list contains *parent_handle* (or has no parents when
    *parent_handle* is None).

    Returns the matching Place's handle, or None.
    """
    name_lower = name.strip().lower()
    for place in db.iter_places():
        if place.get_name().get_value().lower() != name_lower:
            continue
        place_parents = [ref.ref for ref in place.get_placeref_list()]
        if parent_handle is None:
            if not place_parents:
                return place.get_handle()
        else:
            if parent_handle in place_parents:
                return place.get_handle()
    return None
