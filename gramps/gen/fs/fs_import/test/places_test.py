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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
"""Regression tests for FamilySearch place resolution."""

# ------------------------
# Python modules
# ------------------------
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.fs import tree, utils
from gramps.gen.fs.fs_import import deserializer, places


# ------------------------------------------------------------
#
# PlaceResolutionTest
#
# ------------------------------------------------------------
class PlaceResolutionTest(unittest.TestCase):
    """Exercise redirects, missing data, and circular place hierarchies."""

    def setUp(self) -> None:
        """Create an isolated destination and FamilySearch session."""
        self.db = MagicMock()
        self.db.get_place_handles.return_value = []
        self.db.add_place.side_effect = self.cb_add_place
        self.session = MagicMock()
        self.addCleanup(patch.stopall)
        patch.object(tree, "_fs_session", self.session).start()
        patch.object(utils, "FS_INDEX_PLACES", {}).start()
        patch.object(deserializer.PlaceDescription, "_index", {}).start()
        self.txn = MagicMock()

    @staticmethod
    def cb_add_place(place: Any, _txn: Any) -> None:
        """
        Assign a handle as the database would during insertion.

        :param place: The place being inserted.
        :param _txn: The import transaction.
        """
        place.set_handle("place-" + place.get_name().get_value())

    @staticmethod
    def payload(place_id: str, parent_id: str | None = None) -> dict[str, Any]:
        """
        Build a valid downloaded place description.

        :param place_id: The canonical FamilySearch place ID.
        :param parent_id: The enclosing place ID, if any.
        :returns: A GEDCOM X response payload.
        """
        description: dict[str, Any] = {
            "id": place_id,
            "display": {"name": place_id},
            "links": {"place": {"href": "https://example.org/" + place_id}},
            "latitude": 1.0,
            "longitude": 2.0,
        }
        if parent_id:
            description["jurisdiction"] = {"resourceId": parent_id}
        return {"places": [description]}

    def test_redirect_uses_downloaded_canonical_description(self) -> None:
        """A redirect imports without a second request that could fail."""
        response = MagicMock(status_code=200)
        response.json.return_value = self.payload("new")
        unavailable = MagicMock(status_code=404)
        unavailable.__bool__.return_value = False
        self.session.get_url.side_effect = [response, unavailable]
        reference = SimpleNamespace(id="old")
        result = places.add_place(self.db, self.txn, reference)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.get_name().get_value(), "new")
        self.assertEqual(reference._handle, result.handle)
        self.assertTrue(any(url.path.endswith("/old") for url in result.urls))
        self.assertEqual(
            utils.FS_INDEX_PLACES[
                "https://api.familysearch.org/platform/places/description/new"
            ],
            result.handle,
        )
        self.session.get_url.assert_called_once()
