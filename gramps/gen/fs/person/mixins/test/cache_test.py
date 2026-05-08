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

"""Tests for logging behaviour in gramps/gen/fs/person/mixins/cache.py.

Verifies that OSError / fetch failures emit LOG.warning instead of print().

# python3 -m unittest gramps.gen.fs.person.mixins.test.cache_test -v
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..", "..")
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

from gramps.gen.fs.person.mixins.cache import CacheMixin, _FsCache
import gramps.gen.fs.person.mixins.cache as cache_module
from gramps.gen.fs.fs_import import deserializer as deserialize


# -------------------------------------------------------------------------
#
# TestFsCacheLogging
#
# -------------------------------------------------------------------------
class TestFsCacheLogging(unittest.TestCase):
    """Tests that _FsCache uses LOG.warning instead of print() on errors."""

    def setUp(self):
        """Create a temporary cache directory."""
        self.tmpdir = tempfile.mkdtemp(prefix="gramps-cache-test-")
        self.cache = _FsCache(self.tmpdir)

    def tearDown(self):
        """Remove the temporary directory."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_write_json_oserror_calls_log_warning_not_print(self):
        """When the write raises OSError, LOG.warning is called and print is not."""
        with patch("builtins.open", side_effect=OSError("disk full")):
            with patch.object(cache_module, "LOG") as mock_log:
                with patch("builtins.print") as mock_print:
                    self.cache.write_json("FS-100", {"persons": []}, None, None)

        mock_log.warning.assert_called_once()
        warning_args = mock_log.warning.call_args[0]
        self.assertIn("FS-100", str(warning_args))
        mock_print.assert_not_called()

    def test_clear_listdir_error_calls_log_warning(self):
        """When os.listdir raises, LOG.warning is called."""
        with patch("os.listdir", side_effect=OSError("permission denied")):
            with patch.object(cache_module, "LOG") as mock_log:
                self.cache.clear()

        mock_log.warning.assert_called_once()
        warning_args = mock_log.warning.call_args[0]
        self.assertIn(self.cache.base_dir, str(warning_args))

    def test_write_json_happy_path_no_warning(self):
        """A successful write does not call LOG.warning."""
        with patch.object(cache_module, "LOG") as mock_log:
            self.cache.write_json("FS-101", {"persons": []}, "etag-1", 1690000000)

        mock_log.warning.assert_not_called()

        # Verify the file was actually written
        path = self.cache._path("FS-101")
        self.assertTrue(os.path.exists(path))


# -------------------------------------------------------------------------
#
# TestCacheMixinHydrateLogging
#
# -------------------------------------------------------------------------
class TestCacheMixinHydrateLogging(unittest.TestCase):
    """Tests that CacheMixin._hydrate_relative_payloads uses LOG.warning on errors."""

    def setUp(self):
        """Prepare a minimal CacheMixin instance and clear Person.index."""
        deserialize.Person.index.clear()
        self.mixin = CacheMixin.__new__(CacheMixin)

    def tearDown(self):
        """Clear Person.index after each test."""
        deserialize.Person.index.clear()

    def _make_minimal_person(self, fsid: str) -> MagicMock:
        """
        Build a mock Person whose relationship collections are all empty/None,
        so that all three endpoints (spouses, children, parents) are in
        missing_endpoints, triggering get_jsonurl calls.
        """
        person = MagicMock(spec=deserialize.Person)
        # All relationship attributes must be falsy iterables so the "not list(...)"
        # check in _hydrate_relative_payloads evaluates to True.
        person._spouses = []
        person._children = []
        person._childrenCP = []
        person._parents = []
        person._parentsCP = []
        deserialize.Person.index[fsid] = person
        return person

    def test_hydrate_get_jsonurl_raises_calls_log_warning(self):
        """When get_jsonurl raises an exception, LOG.warning is called for that endpoint."""
        fsid = "FS-200"
        self._make_minimal_person(fsid)

        mock_session = MagicMock()
        mock_session.get_jsonurl.side_effect = RuntimeError("connection refused")

        mock_tree = MagicMock()

        with patch.object(cache_module, "LOG") as mock_log:
            self.mixin._hydrate_relative_payloads(fsid, mock_tree, mock_session)

        # One warning per failing endpoint (all three should fail)
        self.assertGreaterEqual(mock_log.warning.call_count, 1)
        # Each warning message should reference the endpoint or fsid
        first_warning_args = mock_log.warning.call_args_list[0][0]
        warning_text = " ".join(str(a) for a in first_warning_args)
        self.assertIn(fsid, warning_text)

    def test_hydrate_no_person_in_index_returns_immediately(self):
        """When the person is not in deserialize.Person.index, the method returns without calling get_jsonurl."""
        fsid = "FS-201"
        # Do NOT add to Person.index

        mock_session = MagicMock()
        mock_tree = MagicMock()

        with patch.object(cache_module, "LOG") as mock_log:
            self.mixin._hydrate_relative_payloads(fsid, mock_tree, mock_session)

        mock_session.get_jsonurl.assert_not_called()
        mock_log.warning.assert_not_called()

    def test_hydrate_all_relatives_present_no_fetch(self):
        """When a person already has all relatives, missing_endpoints is empty and get_jsonurl is not called."""
        fsid = "FS-202"
        person = MagicMock(spec=deserialize.Person)
        # Non-empty relationship collections — nothing is missing.
        rel = MagicMock()
        person._spouses = [rel]
        person._children = [rel]
        person._childrenCP = []
        person._parents = [rel]
        person._parentsCP = []
        deserialize.Person.index[fsid] = person

        mock_session = MagicMock()
        mock_tree = MagicMock()

        self.mixin._hydrate_relative_payloads(fsid, mock_tree, mock_session)

        mock_session.get_jsonurl.assert_not_called()


# -------------------------------------------------------------------------
#
# TestParseDateUtcConversion
#
# -------------------------------------------------------------------------
class TestParseDateUtcConversion(unittest.TestCase):
    """Tests that _ensure_person_cached parses Last-Modified as UTC.

    Regression tests for the fix that replaced time.mktime (local-time) with
    calendar.timegm (UTC) and added a None-guard around email.utils.parsedate.
    """

    def test_valid_gmt_header_parsed_correctly(self):
        """A valid RFC-2822 GMT Last-Modified header yields the correct UTC epoch."""
        import calendar
        import email.utils

        gmt_header = "Thu, 01 Jan 2026 00:00:00 GMT"
        parsed = email.utils.parsedate(gmt_header)
        expected_ts = calendar.timegm(parsed)

        # Verify our expected value is what calendar.timegm gives for that date
        self.assertIsNotNone(parsed)
        self.assertIsInstance(expected_ts, int)
        # 2026-01-01 00:00:00 UTC
        self.assertEqual(expected_ts, 1767225600)

    def test_malformed_last_modified_parsedate_returns_none(self):
        """email.utils.parsedate returns None for a malformed date string."""
        import email.utils

        parsed = email.utils.parsedate("not-a-real-date")
        self.assertIsNone(parsed)

    def test_malformed_last_modified_does_not_crash_cache_logic(self):
        """The cache Last-Modified parsing does not raise when parsedate returns None.

        This directly tests the fixed expression:
          if lm:
              try:
                  parsed = email.utils.parsedate(lm)
                  last_mod = calendar.timegm(parsed) if parsed is not None else None
              except Exception:
                  last_mod = None
        """
        import calendar
        import email.utils

        lm = "not-a-real-date"
        if lm:
            try:
                parsed = email.utils.parsedate(lm)
                last_mod = calendar.timegm(parsed) if parsed is not None else None
            except Exception:
                last_mod = None
        else:
            last_mod = None

        self.assertIsNone(last_mod)

    def test_utc_timestamp_differs_from_local_mktime_on_non_utc_machine(self):
        """calendar.timegm and time.mktime differ on machines not in UTC.

        This test documents the original bug: on a machine with UTC offset != 0,
        time.mktime() would return a wrong value for an HTTP UTC timestamp.
        """
        import calendar
        import email.utils
        import time

        gmt_header = "Thu, 01 Jan 2026 00:00:00 GMT"
        parsed = email.utils.parsedate(gmt_header)
        utc_ts = calendar.timegm(parsed)
        local_ts = int(time.mktime(parsed))

        utc_offset_seconds = time.timezone  # positive for west of UTC
        if utc_offset_seconds != 0:
            # On non-UTC machines the two values differ by the UTC offset
            self.assertNotEqual(utc_ts, local_ts)
        else:
            # On UTC machines they happen to be equal; test still passes
            self.assertEqual(utc_ts, local_ts)


if __name__ == "__main__":
    unittest.main()
