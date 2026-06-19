#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Eduard Ralph
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
Tests that ``gramps.gen.plug.utils.get_addons`` validates addon listing
JSON and fails gracefully rather than crashing the plugin manager UI.

See Gramps bugtracker issue #12974.
"""

# ------------------------
# Python modules
# ------------------------
import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock

# ------------------------
# Gramps modules
# ------------------------
from ...const import GRAMPS_LOCALE as glocale
from ..utils import get_addons


def _valid_entry(plugin_id: str, version: str = "1.0") -> dict:
    """Build a minimal addon listing record that passes validation."""
    return {
        "i": plugin_id,
        "n": f"Plugin {plugin_id}",
        "v": version,
        "d": "description",
        "t": 2,
        "z": f"{plugin_id}.zip",
    }


# ------------------------------------------------------------
#
# AddonListingValidationTest
#
# ------------------------------------------------------------
class AddonListingValidationTest(unittest.TestCase):
    """Exercise the validation paths of ``get_addons``."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.directory = self._tmp.name
        self.listings = os.path.join(self.directory, "listings")
        os.makedirs(self.listings)
        self.url = pathlib.Path(self.directory).as_uri()
        # Short-circuit the locale fallback so only the "en" listing is tried.
        langs_patch = mock.patch.object(glocale, "get_language_list", return_value=[])
        langs_patch.start()
        self.addCleanup(langs_patch.stop)

    def _write_listing(self, body: str, lang: str = "en") -> None:
        path = os.path.join(self.listings, f"addons-{lang}.json")
        with open(path, "w", encoding="utf-8") as file_descriptor:
            file_descriptor.write(body)

    def test_valid_listing_returns_all_entries(self) -> None:
        """A well-formed listing passes through and gains the project/url
        metadata keys plus the default optional fields."""
        self._write_listing(
            json.dumps([_valid_entry("plug1"), _valid_entry("plug2", "1.1")])
        )
        result = get_addons("proj", self.url)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["i"], "plug1")
        self.assertEqual(result[0]["_p"], "proj")
        self.assertEqual(result[0]["_u"], self.url)
        self.assertEqual(result[0]["a"], 0)
        self.assertEqual(result[0]["s"], 0)
        self.assertEqual(result[0]["h"], "")

    def test_malformed_json_returns_empty(self) -> None:
        """A non-JSON body must be logged as an error, not propagated."""
        self._write_listing("{not valid json at all")
        with self.assertLogs(".gen.plug", level="ERROR") as captured:
            result = get_addons("proj", self.url)
        self.assertEqual(result, [])
        self.assertIn("not valid JSON", "\n".join(captured.output))

    def test_non_array_top_level_returns_empty(self) -> None:
        """A JSON object at the top level is not a valid listing."""
        self._write_listing(json.dumps({"not": "an array"}))
        with self.assertLogs(".gen.plug", level="ERROR") as captured:
            result = get_addons("proj", self.url)
        self.assertEqual(result, [])
        self.assertIn("not a JSON array", "\n".join(captured.output))

    def test_non_dict_entry_is_skipped(self) -> None:
        """A non-object element must be skipped; valid siblings survive."""
        self._write_listing(json.dumps(["not a dict", _valid_entry("plug1")]))
        with self.assertLogs(".gen.plug", level="WARNING") as captured:
            result = get_addons("proj", self.url)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["i"], "plug1")
        self.assertIn("expected object", "\n".join(captured.output))

    def test_entry_missing_required_field_is_skipped(self) -> None:
        """Entries missing any of i/n/v/d/t/z are skipped with a warning."""
        incomplete = _valid_entry("incomplete")
        del incomplete["z"]
        self._write_listing(json.dumps([incomplete, _valid_entry("plug1")]))
        with self.assertLogs(".gen.plug", level="WARNING") as captured:
            result = get_addons("proj", self.url)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["i"], "plug1")
        joined = "\n".join(captured.output)
        self.assertIn("incomplete", joined)
        self.assertIn("z", joined)

    def test_unsupported_url_scheme_returns_empty(self) -> None:
        """Anything other than http(s)/file is short-circuited."""
        self.assertEqual(get_addons("proj", "ftp://example.invalid/"), [])

    def test_missing_listing_file_returns_empty(self) -> None:
        """No listing file present ⇒ empty list, not an exception."""
        with self.assertLogs(".gen.plug", level="WARNING"):
            result = get_addons("proj", self.url)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
