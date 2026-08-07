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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Utility functions for parsing a comma-separated place hierarchy string and
committing any new Place objects to the database.

No GTK dependency — fully testable without a display.

Input is ordered from most-general to most-specific, matching the natural
way people refer to places and the way Gramps displays them::

    parsed = parse_place_hierarchy(db, "USA, Illinois, Springfield")
    # show confirmation UI using parsed list
    handle = commit_place_hierarchy(db, parsed, transaction)
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations

from typing import TYPE_CHECKING

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Place, PlaceName, PlaceRef, PlaceType
from gramps.gen.types import PlaceHandle

if TYPE_CHECKING:
    from gramps.gen.db import DbGeneric, DbTxn


# -------------------------------------------------------------------------
#
# Public API
#
# -------------------------------------------------------------------------


def parse_place_hierarchy(db: "DbGeneric", text: str) -> list[dict]:
    """
    Parse *text* as a comma-separated place hierarchy (most-general first).

    Returns a list of dicts, one per token, ordered from most-general to
    most-specific.  Each dict contains:

    - ``name`` (:class:`str`) — stripped token
    - ``handle`` (:class:`PlaceHandle` | ``None``) — existing handle, or
      ``None`` if not found
    - ``status`` (:class:`str`) — ``"existing"`` or ``"new"``

    Parent context is taken into account when matching: "Springfield" is
    only considered a match when it is a child of whatever resolves as
    "Illinois". Resolution proceeds from left (outermost) to right
    (innermost) so parent handles are known before searching for children.

    :param db: The Gramps database to search.
    :type db: DbGeneric
    :param text: Comma-separated place names, most-general first.
    :type text: str
    :returns: List of dicts describing each token, most-general first.
    :rtype: list[dict]
    """
    tokens = [t.strip() for t in text.split(",") if t.strip()]
    if not tokens:
        return []

    entries: list[dict] = [{"name": t, "handle": None, "status": "new"} for t in tokens]

    # Resolve from the outermost (first token) inward so parent handles are
    # known before we search for children.
    for i in range(len(entries)):
        parent_handle: PlaceHandle | None = entries[i - 1]["handle"] if i > 0 else None
        handle = _find_place_child(db, entries[i]["name"], parent_handle)
        if handle is not None:
            entries[i]["handle"] = handle
            entries[i]["status"] = "existing"

    return entries


def commit_place_hierarchy(
    db: "DbGeneric",
    parsed: list[dict],
    with_transaction: "DbTxn | None",
    default_type: PlaceType | None = None,
) -> PlaceHandle | None:
    """
    Commit any ``"new"`` places in *parsed* to the database and wire PlaceRefs.

    *parsed* is the list returned by :func:`parse_place_hierarchy`, possibly
    modified by the user (e.g. with ``place_type`` keys added for new
    entries).  If a ``"new"`` entry is missing a ``place_type`` key,
    *default_type* is used (falls back to an empty :class:`PlaceType`).

    *with_transaction* must be an active :class:`DbTxn` (the caller owns the
    transaction so that multiple operations can be batched).

    Returns the handle of the most-specific place (``parsed[-1]``), whether
    it was pre-existing or newly created, or ``None`` if *parsed* is empty.

    :param db: The Gramps database.
    :type db: DbGeneric
    :param parsed: List of entry dicts from :func:`parse_place_hierarchy`.
    :type parsed: list[dict]
    :param with_transaction: Active database transaction.
    :type with_transaction: DbTxn | None
    :param default_type: PlaceType used for new entries that carry no
        ``place_type`` key.
    :type default_type: PlaceType | None
    :returns: Handle of the most-specific (leaf) place, or ``None``.
    :rtype: PlaceHandle | None
    """
    if not parsed:
        return None

    if default_type is None:
        default_type = PlaceType()

    # Build from outermost → innermost (left to right) so parent handles
    # exist when we need to attach a PlaceRef to a child.
    for i in range(len(parsed)):
        entry = parsed[i]
        if entry["status"] == "existing":
            continue

        place = Place()
        name = PlaceName()
        name.set_value(entry["name"])
        place.set_name(name)
        place.set_type(entry.get("place_type", default_type))

        parent_handle: PlaceHandle | None = parsed[i - 1]["handle"] if i > 0 else None
        if parent_handle is not None:
            ref = PlaceRef()
            ref.ref = parent_handle
            place.add_placeref(ref)

        db.add_place(place, with_transaction)
        entry["handle"] = place.get_handle()

    return parsed[-1]["handle"]


# -------------------------------------------------------------------------
#
# Internal helpers
#
# -------------------------------------------------------------------------


def _find_place_child(
    db: "DbGeneric", name: str, parent_handle: PlaceHandle | None
) -> PlaceHandle | None:
    """
    Search *db* for a Place whose primary name matches *name*.

    The match is case-insensitive.  If *parent_handle* is given the place
    must have it in its ``placeref_list``; if *parent_handle* is ``None``
    the place must have no parents (i.e. it is a root-level place).

    :param db: The Gramps database to search.
    :type db: DbGeneric
    :param name: Primary name to match (case-insensitive).
    :type name: str
    :param parent_handle: Required parent handle, or ``None`` for root places.
    :type parent_handle: PlaceHandle | None
    :returns: The matching place's handle, or ``None`` if not found.
    :rtype: PlaceHandle | None
    """
    name_lower = name.strip().lower()
    for place in db.iter_places():
        if place.get_name().get_value().lower() != name_lower:
            continue
        place_parents = [ref.ref for ref in place.get_placeref_list()]
        if parent_handle is None:
            if not place_parents:
                return PlaceHandle(place.get_handle())
        else:
            if parent_handle in place_parents:
                return PlaceHandle(place.get_handle())
    return None
