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
Tests for ``normalize_project_url`` and ``classify_project_fetch``
(bug #13069 — Addon Manager "project" path validity indicator).
"""

# ------------------------
# Python modules
# ------------------------
import io
import json
import unittest
from email.message import Message
from unittest import mock
from urllib.error import HTTPError, URLError

# ------------------------
# Gramps modules
# ------------------------
from .. import utils as plug_utils
from ..utils import (
    ProjectFetchResult,
    ProjectFetchStatus,
    classify_project_fetch,
    normalize_project_url,
)


# ------------------------------------------------------------
#
# _FakeResponse
#
# ------------------------------------------------------------
class _FakeResponse:
    """Minimal stand-in for the object returned by :func:`urlopen`."""

    def __init__(self, payload: bytes, code: int = 200, is_file: bool = False) -> None:
        self._buffer = io.BytesIO(payload)
        self._code = code
        self.file = self if is_file else None

    def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)

    def getcode(self) -> int:
        return self._code

    def close(self) -> None:
        self._buffer.close()


def _json_response(records: object, code: int = 200) -> _FakeResponse:
    return _FakeResponse(json.dumps(records).encode("utf-8"), code=code)


# ------------------------------------------------------------
#
# NormalizeProjectUrlTest
#
# ------------------------------------------------------------
class NormalizeProjectUrlTest(unittest.TestCase):
    """Unit tests for :func:`normalize_project_url`."""

    def test_strips_surrounding_whitespace(self) -> None:
        self.assertEqual(
            normalize_project_url("  https://example.com/path  "),
            "https://example.com/path",
        )

    def test_strips_trailing_slashes(self) -> None:
        self.assertEqual(
            normalize_project_url("https://example.com/path///"),
            "https://example.com/path",
        )

    def test_keeps_scheme_double_slash(self) -> None:
        self.assertEqual(normalize_project_url("file://"), "file://")

    def test_http_scheme_accepted(self) -> None:
        self.assertEqual(
            normalize_project_url("http://example.com"), "http://example.com"
        )

    def test_file_scheme_accepted(self) -> None:
        self.assertEqual(
            normalize_project_url("file:///tmp/addons/"), "file:///tmp/addons"
        )

    def test_empty_string_rejected(self) -> None:
        self.assertIsNone(normalize_project_url(""))
        self.assertIsNone(normalize_project_url("   "))

    def test_unsupported_scheme_rejected(self) -> None:
        self.assertIsNone(normalize_project_url("ftp://example.com"))
        self.assertIsNone(normalize_project_url("gopher://example.com"))
        self.assertIsNone(normalize_project_url("example.com"))

    def test_non_string_rejected(self) -> None:
        self.assertIsNone(normalize_project_url(None))
        self.assertIsNone(normalize_project_url(42))
        self.assertIsNone(normalize_project_url(b"https://example.com"))


# ------------------------------------------------------------
#
# ClassifyProjectFetchTest
#
# ------------------------------------------------------------
class ClassifyProjectFetchTest(unittest.TestCase):
    """Unit tests for :func:`classify_project_fetch`."""

    def _patch_urlopen(self, side_effect: object) -> mock._patch:
        return mock.patch.object(
            plug_utils, "urlopen_maybe_no_check_cert", side_effect=side_effect
        )

    def test_invalid_url_for_none(self) -> None:
        result = classify_project_fetch(None)
        self.assertIsInstance(result, ProjectFetchResult)
        self.assertEqual(result.status, ProjectFetchStatus.INVALID_URL)
        self.assertIsNone(result.normalized_url)

    def test_invalid_url_for_wrong_scheme(self) -> None:
        result = classify_project_fetch("ftp://example.com/addons")
        self.assertEqual(result.status, ProjectFetchStatus.INVALID_URL)

    def test_invalid_url_for_empty_string(self) -> None:
        self.assertEqual(
            classify_project_fetch("   ").status, ProjectFetchStatus.INVALID_URL
        )

    def test_ok_when_compatible_entry_present(self) -> None:
        records = [
            {"i": "one", "n": "One", "v": "1.0", "d": "d", "t": "6.1", "z": "z"},
            {"i": "two", "n": "Two", "v": "0.9", "d": "d", "t": "5.2", "z": "z"},
        ]
        with self._patch_urlopen(lambda u, *a, **k: _json_response(records)):
            result = classify_project_fetch(
                "https://example.com/addons",
                current_version=(6, 1, 0),
                languages=["en"],
            )
        self.assertEqual(result.status, ProjectFetchStatus.OK)
        self.assertEqual(result.addon_count, 2)
        self.assertEqual(result.compatible_count, 1)
        self.assertEqual(result.fetched_language, "en")

    def test_empty_listing(self) -> None:
        with self._patch_urlopen(lambda u, *a, **k: _json_response([])):
            result = classify_project_fetch(
                "https://example.com/addons",
                current_version=(6, 1, 0),
                languages=["en"],
            )
        self.assertEqual(result.status, ProjectFetchStatus.EMPTY_LISTING)
        self.assertEqual(result.addon_count, 0)

    def test_no_compatible_addons(self) -> None:
        records = [
            {"i": "x", "n": "X", "v": "1.0", "d": "d", "t": "5.2", "z": "z"},
            {"i": "y", "n": "Y", "v": "1.0", "d": "d", "t": "5.1", "z": "z"},
        ]
        with self._patch_urlopen(lambda u, *a, **k: _json_response(records)):
            result = classify_project_fetch(
                "https://example.com/addons",
                current_version=(6, 1, 0),
                languages=["en"],
            )
        self.assertEqual(result.status, ProjectFetchStatus.NO_COMPATIBLE_ADDONS)
        self.assertEqual(result.addon_count, 2)
        self.assertEqual(result.compatible_count, 0)

    def test_lang_fallback_to_en(self) -> None:
        calls: list[str] = []
        records = [
            {"i": "a", "n": "A", "v": "1.0", "d": "d", "t": "6.1", "z": "z"},
        ]

        def fake_urlopen(addon_url: str, *a: object, **k: object) -> _FakeResponse:
            calls.append(addon_url)
            if "addons-en.json" in addon_url:
                return _json_response(records)
            raise HTTPError(addon_url, 404, "Not Found", hdrs=Message(), fp=None)

        with self._patch_urlopen(fake_urlopen):
            result = classify_project_fetch(
                "https://example.com/addons",
                current_version=(6, 1, 0),
                languages=["de", "en"],
            )
        self.assertEqual(result.status, ProjectFetchStatus.LANG_FALLBACK_EN)
        self.assertEqual(result.fetched_language, "en")
        self.assertIn("de", result.tried_languages)
        self.assertIn("en", result.tried_languages)
        self.assertTrue(any("addons-en.json" in u for u in calls))

    def test_json_error_on_invalid_body(self) -> None:
        with self._patch_urlopen(
            lambda u, *a, **k: _FakeResponse(b"not json at all", code=200)
        ):
            result = classify_project_fetch(
                "https://example.com/addons",
                current_version=(6, 1, 0),
                languages=["en"],
            )
        self.assertEqual(result.status, ProjectFetchStatus.JSON_ERROR)

    def test_json_error_on_non_array_payload(self) -> None:
        with self._patch_urlopen(
            lambda u, *a, **k: _FakeResponse(b'{"an": "object"}', code=200)
        ):
            result = classify_project_fetch(
                "https://example.com/addons",
                current_version=(6, 1, 0),
                languages=["en"],
            )
        self.assertEqual(result.status, ProjectFetchStatus.JSON_ERROR)

    def test_http_error(self) -> None:
        def raise_404(addon_url: str, *a: object, **k: object) -> _FakeResponse:
            raise HTTPError(addon_url, 404, "Not Found", hdrs=Message(), fp=None)

        with self._patch_urlopen(raise_404):
            result = classify_project_fetch(
                "https://example.com/addons",
                current_version=(6, 1, 0),
                languages=["en"],
            )
        self.assertEqual(result.status, ProjectFetchStatus.HTTP_ERROR)
        self.assertEqual(result.http_code, 404)

    def test_network_error(self) -> None:
        def raise_url_error(addon_url: str, *a: object, **k: object) -> _FakeResponse:
            raise URLError("getaddrinfo failed")

        with self._patch_urlopen(raise_url_error):
            result = classify_project_fetch(
                "https://example.com/addons",
                current_version=(6, 1, 0),
                languages=["en"],
            )
        self.assertEqual(result.status, ProjectFetchStatus.NETWORK_ERROR)
        self.assertIn("getaddrinfo failed", result.detail or "")

    def test_trailing_slashes_normalized_before_fetch(self) -> None:
        seen: list[str] = []

        def fake_urlopen(addon_url: str, *a: object, **k: object) -> _FakeResponse:
            seen.append(addon_url)
            return _json_response(
                [{"i": "a", "n": "A", "v": "1.0", "d": "d", "t": "6.1", "z": "z"}]
            )

        with self._patch_urlopen(fake_urlopen):
            classify_project_fetch(
                "https://example.com/addons///",
                current_version=(6, 1, 0),
                languages=["en"],
            )
        self.assertEqual(seen[0], "https://example.com/addons/listings/addons-en.json")


if __name__ == "__main__":
    unittest.main()
