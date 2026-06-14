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

"""Tests for quickplaceparser — no GTK required.

Input convention: most-general first, most-specific last.
Example: "USA, Illinois, Springfield"
"""

import unittest

from gramps.gen.lib import Place, PlaceName, PlaceRef, PlaceType
from gramps.gui.selectors.quickplaceparser import (
    _find_place_child,
    commit_place_hierarchy,
    parse_place_hierarchy,
)

# ---------------------------------------------------------------------------
# Minimal fake database
# ---------------------------------------------------------------------------


class _FakeDb:
    """Minimal stand-in for DbGeneric sufficient to test the parser."""

    def __init__(self):
        self._places: dict[str, Place] = {}
        self._next_id = 1

    # --- place iteration / lookup ---

    def iter_places(self):
        yield from self._places.values()

    def get_place_from_handle(self, handle: str) -> Place:
        return self._places[handle]

    # --- write ---

    def add_place(self, place: Place, transaction) -> str:
        handle = f"handle{self._next_id:04d}"
        self._next_id += 1
        place.set_handle(handle)
        self._places[handle] = place
        return handle

    # --- helpers for test setup ---

    def _add(self, name: str, parent_handle: str | None = None) -> str:
        """Create and store a Place; return its handle."""
        p = Place()
        pn = PlaceName()
        pn.set_value(name)
        p.set_name(pn)
        if parent_handle is not None:
            ref = PlaceRef()
            ref.ref = parent_handle
            p.add_placeref(ref)
        return self.add_place(p, None)


# ---------------------------------------------------------------------------
# Tests for _find_place_child
# ---------------------------------------------------------------------------


class TestFindPlaceChild(unittest.TestCase):
    def setUp(self):
        self.db = _FakeDb()
        self.usa_h = self.db._add("USA")
        self.il_h = self.db._add("Illinois", parent_handle=self.usa_h)
        self.spring_h = self.db._add("Springfield", parent_handle=self.il_h)

    def test_find_root_place(self):
        self.assertEqual(_find_place_child(self.db, "USA", None), self.usa_h)

    def test_find_child(self):
        self.assertEqual(_find_place_child(self.db, "Illinois", self.usa_h), self.il_h)

    def test_find_grandchild(self):
        self.assertEqual(
            _find_place_child(self.db, "Springfield", self.il_h), self.spring_h
        )

    def test_no_match_wrong_parent(self):
        self.assertIsNone(_find_place_child(self.db, "Springfield", self.usa_h))

    def test_no_match_missing(self):
        self.assertIsNone(_find_place_child(self.db, "Chicago", self.il_h))

    def test_case_insensitive(self):
        self.assertEqual(_find_place_child(self.db, "usa", None), self.usa_h)
        self.assertEqual(_find_place_child(self.db, "USA", None), self.usa_h)


# ---------------------------------------------------------------------------
# Tests for parse_place_hierarchy  (most-general first)
# ---------------------------------------------------------------------------


class TestParsePlaceHierarchy(unittest.TestCase):
    def setUp(self):
        self.db = _FakeDb()
        self.usa_h = self.db._add("USA")
        self.il_h = self.db._add("Illinois", parent_handle=self.usa_h)

    def test_empty_string(self):
        self.assertEqual(parse_place_hierarchy(self.db, ""), [])

    def test_whitespace_only(self):
        self.assertEqual(parse_place_hierarchy(self.db, "   ,  , "), [])

    def test_all_existing(self):
        result = parse_place_hierarchy(self.db, "USA, Illinois")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "USA")
        self.assertEqual(result[0]["handle"], self.usa_h)
        self.assertEqual(result[0]["status"], "existing")
        self.assertEqual(result[1]["name"], "Illinois")
        self.assertEqual(result[1]["handle"], self.il_h)
        self.assertEqual(result[1]["status"], "existing")

    def test_new_innermost(self):
        # Springfield is new; USA and Illinois already exist
        result = parse_place_hierarchy(self.db, "USA, Illinois, Springfield")
        self.assertEqual(result[0]["name"], "USA")
        self.assertEqual(result[0]["status"], "existing")
        self.assertEqual(result[1]["name"], "Illinois")
        self.assertEqual(result[1]["status"], "existing")
        self.assertEqual(result[2]["name"], "Springfield")
        self.assertIsNone(result[2]["handle"])
        self.assertEqual(result[2]["status"], "new")

    def test_all_new(self):
        result = parse_place_hierarchy(self.db, "France, Paris")
        for entry in result:
            self.assertEqual(entry["status"], "new")
            self.assertIsNone(entry["handle"])

    def test_single_token_existing(self):
        result = parse_place_hierarchy(self.db, "USA")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["handle"], self.usa_h)

    def test_single_token_new(self):
        result = parse_place_hierarchy(self.db, "Atlantis")
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["handle"])

    def test_strips_whitespace(self):
        result = parse_place_hierarchy(self.db, "  USA  ,  Illinois  ")
        self.assertEqual(result[0]["name"], "USA")
        self.assertEqual(result[1]["name"], "Illinois")

    def test_wrong_parent_not_matched(self):
        # "Illinois" exists as child of USA, not as root — should be "new"
        result = parse_place_hierarchy(self.db, "Illinois")
        self.assertEqual(result[0]["status"], "new")


# ---------------------------------------------------------------------------
# Tests for commit_place_hierarchy  (most-general first)
# ---------------------------------------------------------------------------


class TestCommitPlaceHierarchy(unittest.TestCase):
    def setUp(self):
        self.db = _FakeDb()
        self.usa_h = self.db._add("USA")

    def test_commit_all_new(self):
        # France → Lyon
        parsed = [
            {"name": "France", "handle": None, "status": "new"},
            {"name": "Lyon", "handle": None, "status": "new"},
        ]
        handle = commit_place_hierarchy(self.db, parsed, None)
        # Returns the leaf (last entry)
        self.assertIsNotNone(handle)
        self.assertEqual(handle, parsed[-1]["handle"])
        # France was created
        france_h = parsed[0]["handle"]
        self.assertIsNotNone(france_h)
        france = self.db.get_place_from_handle(france_h)
        self.assertEqual(france.get_name().get_value(), "France")
        # Lyon is a child of France
        lyon = self.db.get_place_from_handle(handle)
        self.assertEqual(lyon.get_name().get_value(), "Lyon")
        parent_refs = [ref.ref for ref in lyon.get_placeref_list()]
        self.assertIn(france_h, parent_refs)

    def test_commit_with_existing_parent(self):
        # USA (existing) → California (new)
        parsed = [
            {"name": "USA", "handle": self.usa_h, "status": "existing"},
            {"name": "California", "handle": None, "status": "new"},
        ]
        handle = commit_place_hierarchy(self.db, parsed, None)
        # Returns the leaf
        self.assertEqual(handle, parsed[-1]["handle"])
        cal = self.db.get_place_from_handle(handle)
        parent_refs = [ref.ref for ref in cal.get_placeref_list()]
        self.assertIn(self.usa_h, parent_refs)

    def test_commit_all_existing_no_writes(self):
        count_before = self.db._next_id
        parsed = [{"name": "USA", "handle": self.usa_h, "status": "existing"}]
        handle = commit_place_hierarchy(self.db, parsed, None)
        self.assertEqual(handle, self.usa_h)
        self.assertEqual(self.db._next_id, count_before)

    def test_empty_returns_none(self):
        self.assertIsNone(commit_place_hierarchy(self.db, [], None))

    def test_place_type_applied(self):
        pt = PlaceType(PlaceType.CITY)
        parsed = [
            {
                "name": "Berlin",
                "handle": None,
                "status": "new",
                "place_type": pt,
            }
        ]
        handle = commit_place_hierarchy(self.db, parsed, None)
        place = self.db.get_place_from_handle(handle)
        self.assertEqual(place.get_type(), pt)

    def test_default_type_used_when_no_type_key(self):
        default_pt = PlaceType(PlaceType.COUNTRY)
        parsed = [{"name": "Japan", "handle": None, "status": "new"}]
        handle = commit_place_hierarchy(self.db, parsed, None, default_type=default_pt)
        place = self.db.get_place_from_handle(handle)
        self.assertEqual(place.get_type(), default_pt)


if __name__ == "__main__":
    unittest.main()
