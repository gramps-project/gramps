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

"""Tests for backfill_last_modified in gramps/gen/fs/compare/aggregate.py.

# python3 -m unittest gramps.gen.fs.compare.test.aggregate_test -v
"""

import os
import shutil
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..")
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

import gramps.gen.fs.tree as tree_mod
from gramps.gen.fs.compare import aggregate


def _fs_person(fsid, last_modified=0):
    person = types.SimpleNamespace()
    person.id = fsid
    if last_modified:
        person._last_modified = last_modified
    return person


def _response(status_code=200, headers=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {}
    return resp


# -------------------------------------------------------------------------
#
# TestBackfillLastModified
#
# -------------------------------------------------------------------------
class TestBackfillLastModified(unittest.TestCase):
    """Tests for aggregate.backfill_last_modified."""

    def setUp(self):
        tree_mod._fs_session = None

    def tearDown(self):
        tree_mod._fs_session = None

    def test_no_session_returns_zero_without_error(self):
        """When _fs_session is None, returns 0 and touches nothing."""
        pairs = [(_fs_person("FS-001"), MagicMock())]
        result = aggregate.backfill_last_modified(MagicMock(), pairs)
        self.assertEqual(result, 0)

    def test_already_has_last_modified_is_skipped(self):
        """Pairs whose fs_person already has _last_modified are never fetched."""
        session = MagicMock()
        tree_mod._fs_session = session
        pairs = [(_fs_person("FS-010", last_modified=123), MagicMock())]

        result = aggregate.backfill_last_modified(MagicMock(), pairs)

        session.head_url.assert_not_called()
        self.assertEqual(result, 0)

    def test_resolves_last_modified_and_etag_concurrently(self):
        """Two persons needing backfill are both resolved and updated."""
        session = MagicMock()
        session.head_url.return_value = _response(
            headers={"Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT", "Etag": "abc"}
        )
        tree_mod._fs_session = session

        fs_a = _fs_person("FS-020")
        fs_b = _fs_person("FS-021")
        pairs = [(fs_a, MagicMock()), (fs_b, MagicMock())]

        result = aggregate.backfill_last_modified(MagicMock(), pairs)

        self.assertEqual(result, 2)
        self.assertTrue(getattr(fs_a, "_last_modified", 0))
        self.assertTrue(getattr(fs_b, "_last_modified", 0))
        self.assertEqual(fs_a._etag, "abc")
        self.assertEqual(fs_b._etag, "abc")

    def test_progress_callback_called_once_per_pair(self):
        """progress_callback fires once per resolved pair, not per HTTP call."""
        session = MagicMock()
        session.head_url.return_value = _response(headers={})
        tree_mod._fs_session = session

        pairs = [
            (_fs_person("FS-030"), MagicMock()),
            (_fs_person("FS-031"), MagicMock()),
        ]
        callback = MagicMock()

        aggregate.backfill_last_modified(MagicMock(), pairs, progress_callback=callback)

        self.assertEqual(callback.call_count, 2)

    def test_redirect_chain_relinks_fsid_and_updates_person(self):
        """A 301 redirect follows to the new FSID and calls link_gramps_fs_id."""
        session = MagicMock()
        redirect_resp = _response(
            status_code=301, headers={"X-Entity-Forwarded-Id": "FS-NEW"}
        )
        final_resp = _response(
            headers={"Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT"}
        )
        session.head_url.side_effect = [redirect_resp, final_resp]
        tree_mod._fs_session = session

        fs_person = _fs_person("FS-040")
        gr_person = MagicMock()
        pairs = [(fs_person, gr_person)]

        with patch.object(aggregate.fs_utilities, "link_gramps_fs_id") as mock_link:
            db = MagicMock()
            aggregate.backfill_last_modified(db, pairs)

        mock_link.assert_called_once_with(db, gr_person, "FS-NEW")
        self.assertEqual(fs_person.id, "FS-NEW")
        self.assertTrue(getattr(fs_person, "_last_modified", 0))

    def test_resolve_exception_is_logged_and_does_not_raise(self):
        """A failure resolving one person is logged and does not abort the batch."""
        session = MagicMock()
        session.head_url.side_effect = RuntimeError("network failure")
        tree_mod._fs_session = session

        pairs = [(_fs_person("FS-050"), MagicMock())]

        with patch.object(aggregate, "logger"):
            result = aggregate.backfill_last_modified(MagicMock(), pairs)

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
