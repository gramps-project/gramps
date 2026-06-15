#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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

"""Tests for Tree._fetch_raw and Tree.add_persons in gramps/gen/fs/tree.py.

# python3 -m unittest gramps.gen.fs.test.tree_test -v
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)


def _ensure_test_resources():
    resource_path = os.environ.get("GRAMPS_RESOURCES")
    if resource_path and os.path.exists(
        os.path.join(resource_path, "gramps", "authors.xml")
    ):
        return resource_path

    build_share = os.path.join(ROOT_DIR, "build", "share")
    if os.path.exists(os.path.join(build_share, "gramps", "authors.xml")):
        return build_share

    resource_path = tempfile.mkdtemp(prefix="gramps-resources-")
    os.makedirs(os.path.join(resource_path, "gramps", "images"), exist_ok=True)
    os.makedirs(os.path.join(resource_path, "doc", "gramps"), exist_ok=True)
    os.makedirs(os.path.join(resource_path, "locale"), exist_ok=True)

    shutil.copyfile(
        os.path.join(ROOT_DIR, "data", "authors.xml"),
        os.path.join(resource_path, "gramps", "authors.xml"),
    )
    shutil.copyfile(
        os.path.join(ROOT_DIR, "images", "gramps.png"),
        os.path.join(resource_path, "gramps", "images", "gramps.png"),
    )
    shutil.copyfile(
        os.path.join(ROOT_DIR, "COPYING"),
        os.path.join(resource_path, "doc", "gramps", "COPYING"),
    )
    return resource_path


os.environ["GRAMPS_RESOURCES"] = _ensure_test_resources()
os.environ["HOME"] = os.environ.get("HOME") or tempfile.mkdtemp(prefix="gramps-home-")

from gramps.gen.fs.tree import Tree
import gramps.gen.fs.tree as tree_mod
from gramps.gen.fs.fs_import import deserializer as deserialize


# -------------------------------------------------------------------------
#
# TestFetchRaw
#
# -------------------------------------------------------------------------
class TestFetchRaw(unittest.TestCase):
    """Tests for Tree._fetch_raw."""

    def setUp(self):
        """Create a fresh Tree and clear global session before each test."""
        self.tree = Tree()
        # Ensure module-level session is None
        tree_mod._fs_session = None
        # Clean up any lingering Person index entries
        deserialize.Person.index.clear()

    def tearDown(self):
        """Restore module-level session to None and clear Person index."""
        tree_mod._fs_session = None
        deserialize.Person.index.clear()

    def test_fetch_raw_no_session_returns_triple_none(self):
        """When _fs_session is None, _fetch_raw returns (fsid, None, None)."""
        tree_mod._fs_session = None
        result = self.tree._fetch_raw("FS-001")
        self.assertEqual(result, ("FS-001", None, None))

    def test_fetch_raw_session_returns_no_response(self):
        """When get_url returns None, _fetch_raw returns (fsid, None, None)."""
        mock_session = MagicMock()
        mock_session.get_url.return_value = None
        tree_mod._fs_session = mock_session

        result = self.tree._fetch_raw("FS-002")
        self.assertEqual(result, ("FS-002", None, None))
        mock_session.get_url.assert_called_once_with("/platform/tree/persons/FS-002")

    def test_fetch_raw_bad_json_returns_response_and_none_data(self):
        """When r.json() raises, _fetch_raw returns (fsid, response, None) and logs warning."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("bad JSON")
        mock_session.get_url.return_value = mock_response
        tree_mod._fs_session = mock_session

        with patch("gramps.gen.fs.tree.LOG") as mock_log:
            result = self.tree._fetch_raw("FS-003")

        self.assertEqual(result[0], "FS-003")
        self.assertIs(result[1], mock_response)
        self.assertIsNone(result[2])
        mock_log.warning.assert_called_once()

    def test_fetch_raw_valid_json_returns_full_triple(self):
        """When the response has valid JSON, _fetch_raw returns (fsid, response, data)."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        expected_data = {"persons": [{"id": "FS-004"}]}
        mock_response.json.return_value = expected_data
        mock_session.get_url.return_value = mock_response
        tree_mod._fs_session = mock_session

        result = self.tree._fetch_raw("FS-004")

        self.assertEqual(result[0], "FS-004")
        self.assertIs(result[1], mock_response)
        self.assertEqual(result[2], expected_data)


# -------------------------------------------------------------------------
#
# TestAddPersons
#
# -------------------------------------------------------------------------
class TestAddPersons(unittest.TestCase):
    """Tests for Tree.add_persons."""

    def setUp(self):
        """Create a fresh Tree and clear global session before each test."""
        self.tree = Tree()
        tree_mod._fs_session = None
        deserialize.Person.index.clear()

    def tearDown(self):
        """Restore module-level session to None and clear Person index."""
        tree_mod._fs_session = None
        deserialize.Person.index.clear()

    def test_add_persons_empty_list_never_calls_fetch_raw(self):
        """Passing an empty fids list never calls _fetch_raw."""
        with patch.object(self.tree, "_fetch_raw") as mock_fetch:
            self.tree.add_persons([])
        mock_fetch.assert_not_called()

    def test_add_persons_already_in_persons_skips_fetch(self):
        """fids already present in _persons are not re-fetched."""
        mock_person = MagicMock(spec=deserialize.Person)
        self.tree._persons["FS-010"] = mock_person
        self.tree._persons["FS-011"] = mock_person

        with patch.object(self.tree, "_fetch_raw") as mock_fetch:
            self.tree.add_persons(["FS-010", "FS-011"])

        mock_fetch.assert_not_called()

    def test_add_persons_two_new_fids_calls_fetch_twice_and_updates_persons(self):
        """Two new fids cause two _fetch_raw calls; _persons is updated from deserialize.Person.index."""
        mock_person_a = MagicMock(spec=deserialize.Person)
        mock_person_b = MagicMock(spec=deserialize.Person)
        mock_response = MagicMock()
        mock_response.headers = {}

        # Populate Person.index so add_persons can find the results
        deserialize.Person.index["FS-020"] = mock_person_a
        deserialize.Person.index["FS-021"] = mock_person_b

        def fake_fetch_raw(fsid):
            return (fsid, mock_response, {"persons": [{"id": fsid}]})

        with patch.object(
            self.tree, "_fetch_raw", side_effect=fake_fetch_raw
        ) as mock_fetch:
            with patch("gramps.gen.fs.tree.deserialize.deserialize_json"):
                self.tree.add_persons(["FS-020", "FS-021"])

        self.assertEqual(mock_fetch.call_count, 2)
        called_fids = {call.args[0] for call in mock_fetch.call_args_list}
        self.assertEqual(called_fids, {"FS-020", "FS-021"})
        self.assertIn("FS-020", self.tree._persons)
        self.assertIn("FS-021", self.tree._persons)

    def test_add_persons_one_fetch_raises_other_still_imported(self):
        """If one _fetch_raw future raises an exception, the successful fid is still imported."""
        mock_person_ok = MagicMock(spec=deserialize.Person)
        mock_response = MagicMock()
        mock_response.headers = {}

        deserialize.Person.index["FS-030"] = mock_person_ok

        call_count = {"n": 0}

        def fake_fetch_raw(fsid):
            call_count["n"] += 1
            if fsid == "FS-031":
                raise RuntimeError("network failure")
            return (fsid, mock_response, {"persons": [{"id": fsid}]})

        with patch("gramps.gen.fs.tree.LOG"):
            with patch.object(self.tree, "_fetch_raw", side_effect=fake_fetch_raw):
                with patch("gramps.gen.fs.tree.deserialize.deserialize_json"):
                    self.tree.add_persons(["FS-030", "FS-031"])

        # FS-030 succeeded and should be in _persons
        self.assertIn("FS-030", self.tree._persons)
        # FS-031 failed — it may or may not be in _persons, but no exception should propagate
        # (the important guarantee is that the call didn't raise)


# -------------------------------------------------------------------------
#
# TestLastModifiedTimezone
#
# -------------------------------------------------------------------------
class TestLastModifiedTimezone(unittest.TestCase):
    """Tests that Last-Modified timestamps are parsed as UTC (not local time).

    HTTP Last-Modified is always UTC; using time.mktime() instead of
    calendar.timegm() would produce a wrong timestamp on non-UTC machines.
    """

    def setUp(self):
        self.tree = Tree()
        tree_mod._fs_session = None
        deserialize.Person.index.clear()

    def tearDown(self):
        tree_mod._fs_session = None
        deserialize.Person.index.clear()

    def test_add_person_last_modified_parsed_as_utc(self):
        """Last-Modified header is converted to a UTC Unix timestamp."""
        import calendar
        import email.utils

        # Thu, 01 Jan 2026 00:00:00 GMT == 1767225600 UTC
        gmt_header = "Thu, 01 Jan 2026 00:00:00 GMT"
        expected_ts = calendar.timegm(email.utils.parsedate(gmt_header))

        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {"Last-Modified": gmt_header}
        mock_response.json.return_value = {"persons": [{"id": "FS-UTC-001"}]}
        mock_session.get_url.return_value = mock_response

        mock_person = MagicMock(spec=deserialize.Person)
        deserialize.Person.index["FS-UTC-001"] = mock_person
        tree_mod._fs_session = mock_session

        with patch("gramps.gen.fs.tree.deserialize.deserialize_json"):
            self.tree.add_person("FS-UTC-001")

        self.assertEqual(mock_person._last_modified, expected_ts)

    def test_add_person_malformed_last_modified_does_not_raise(self):
        """A malformed Last-Modified header is silently ignored."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {"Last-Modified": "not-a-date"}
        mock_response.json.return_value = {"persons": [{"id": "FS-UTC-002"}]}
        mock_session.get_url.return_value = mock_response

        mock_person = MagicMock(spec=deserialize.Person)
        deserialize.Person.index["FS-UTC-002"] = mock_person
        tree_mod._fs_session = mock_session

        with patch("gramps.gen.fs.tree.deserialize.deserialize_json"):
            # Must not raise
            self.tree.add_person("FS-UTC-002")

    def test_add_persons_does_not_overwrite_existing_etag(self):
        """add_persons does not clobber _etag/_last_modified for already-present persons."""
        # Pre-populate _persons with a fresh person object
        existing_person = MagicMock(spec=deserialize.Person)
        existing_person._etag = "v2-fresh"
        self.tree._persons["FS-NOOVER-001"] = existing_person

        # Put a stale person in the global index (simulating a prior deserialization)
        stale_person = MagicMock(spec=deserialize.Person)
        stale_person._etag = "v1-stale"
        deserialize.Person.index["FS-NOOVER-001"] = stale_person

        # Call add_persons with the same fid — it should skip fetching but also
        # must not overwrite the existing _persons entry from the index loop.
        with patch.object(self.tree, "_fetch_raw") as mock_fetch:
            self.tree.add_persons(["FS-NOOVER-001"])

        mock_fetch.assert_not_called()
        # The fresh person must not have been replaced by the stale one
        self.assertIs(self.tree._persons["FS-NOOVER-001"], existing_person)
        self.assertEqual(self.tree._persons["FS-NOOVER-001"]._etag, "v2-fresh")

    def test_add_persons_fetch_exception_is_logged_not_raised(self):
        """An exception in a concurrent fetch is logged via LOG.warning, not raised."""
        with patch("gramps.gen.fs.tree.LOG") as mock_log:
            with patch.object(
                self.tree, "_fetch_raw", side_effect=RuntimeError("auth expired")
            ):
                # Must not raise
                self.tree.add_persons(["FS-LOG-001"])

        mock_log.warning.assert_called()


if __name__ == "__main__":
    unittest.main()
