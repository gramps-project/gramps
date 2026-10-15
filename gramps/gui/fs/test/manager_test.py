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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Tests for get_session() session-caching fix in gramps/gui/fs/manager.py.

Issue 5: the old code used ``get_active_session() or _SESSION``, which
discarded an already-authenticated ``_SESSION`` whenever
``get_active_session()`` returned a fresh (unauthenticated) session.  The
fix swaps the operands so the cached ``_SESSION`` is always preferred.

python3 -m unittest gramps.gui.fs.test.manager_test -v
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import copy
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Protect headless / standalone CI runs from missing display.
os.environ.setdefault("GDK_BACKEND", "-")

# -------------------------------------------------------------------------
#
# Test-resource bootstrap  (mirrors familysearch_status_test.py)
#
# -------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)


def _ensure_test_resources():
    """Return a valid GRAMPS_RESOURCES path, creating a minimal one if needed."""
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

# -------------------------------------------------------------------------
#
# Gramps modules  (imported AFTER resource path is set)
#
# -------------------------------------------------------------------------

# We need to stub out the GTK-heavy session module before importing manager
# so that the import itself does not fail in headless environments.
_fake_session_mod = MagicMock()
_fake_session_class = MagicMock()
_fake_get_active_session = MagicMock(return_value=None)
_fake_session_mod.Session = _fake_session_class
_fake_session_mod.get_active_session = _fake_get_active_session

sys.modules.setdefault("gramps.gui.fs.session", _fake_session_mod)

import gramps.gui.fs.manager as manager  # noqa: E402  (must follow the stub above)
from gramps.gui.fs.manager import get_session  # noqa: E402


# -------------------------------------------------------------------------
#
# GetSessionCachingTest
#
# -------------------------------------------------------------------------
class GetSessionCachingTest(unittest.TestCase):
    """Unit tests for the ``get_session`` session-priority fix."""

    def setUp(self):
        """Reset module-level _SESSION before each test."""
        manager._SESSION = None

    def tearDown(self):
        """Clean up module-level _SESSION after each test."""
        manager._SESSION = None

    # ------------------------------------------------------------------
    # Helper: patch the minimum set of collaborators so get_session()
    # exercises the caching logic without touching real config / GTK.
    # ------------------------------------------------------------------
    def _run_get_session(self, *, cached_session, active_session, enabled=True):
        """
        Run get_session() with controlled collaborators and return its result.

        :param cached_session: value to pre-load into manager._SESSION
        :param active_session: value returned by get_active_session()
        :param enabled: value returned by _cfg_get for familysearch.enable
        :returns: whatever get_session() returns
        """
        manager._SESSION = cached_session

        with (
            patch.object(
                manager, "get_active_session", return_value=active_session
            ) as mock_active,
            patch.object(manager, "_bind_session_context") as mock_bind,
            patch.object(manager, "_cfg_get", return_value=enabled),
        ):
            result = get_session()

        return result, mock_active, mock_bind

    # ------------------------------------------------------------------
    # Issue 5 regression test: cached _SESSION must win over get_active_session()
    # ------------------------------------------------------------------
    def test_cached_session_preferred_over_active_session(self):
        """_SESSION is returned when both _SESSION and get_active_session() exist."""
        cached = MagicMock(name="cached_session")
        active = MagicMock(name="active_session")

        result, mock_active, mock_bind = self._run_get_session(
            cached_session=cached,
            active_session=active,
        )

        # The cached session must win.
        self.assertIs(result, cached)
        # get_active_session() should NOT have been called because _SESSION
        # short-circuited the ``or``.
        mock_active.assert_not_called()
        # The winner must be re-cached and context-bound.
        self.assertIs(manager._SESSION, cached)
        mock_bind.assert_called_once()

    def test_active_session_used_when_no_cached_session(self):
        """get_active_session() result is used when _SESSION is None."""
        active = MagicMock(name="active_session")

        result, mock_active, mock_bind = self._run_get_session(
            cached_session=None,
            active_session=active,
        )

        self.assertIs(result, active)
        mock_active.assert_called_once()
        self.assertIs(manager._SESSION, active)
        mock_bind.assert_called_once()

    def test_returns_none_when_both_sessions_absent(self):
        """None is returned when _SESSION is None and get_active_session() returns None.

        In this case the function falls through to the config-based Session
        construction path, which also returns None when credentials are not
        configured (the default in tests).
        """
        # Patch _cfg_get so every key lookup returns a falsy value, which
        # causes the foundation-auth branch to return None.
        manager._SESSION = None

        with (
            patch.object(manager, "get_active_session", return_value=None),
            patch.object(manager, "_bind_session_context"),
            patch.object(manager, "_cfg_get", return_value=""),
        ):
            result = get_session()

        self.assertIsNone(result)

    def test_integration_disabled_returns_none(self):
        """get_session() returns None when familysearch.enable is False."""
        cached = MagicMock(name="cached_session")
        manager._SESSION = cached

        with (
            patch.object(manager, "_cfg_get", return_value=False),
            patch.object(manager, "get_active_session") as mock_active,
            patch.object(manager, "_bind_session_context"),
        ):
            result = get_session()

        self.assertIsNone(result)
        mock_active.assert_not_called()

    def test_cached_session_stored_back(self):
        """After returning an active session, _SESSION is updated to that session."""
        active = MagicMock(name="active_session")

        self._run_get_session(cached_session=None, active_session=active)

        self.assertIs(manager._SESSION, active)

    def test_cached_session_unchanged_when_already_set(self):
        """_SESSION remains the same object after a successful return."""
        cached = MagicMock(name="cached_session")
        active = MagicMock(name="other_session")

        self._run_get_session(cached_session=cached, active_session=active)

        self.assertIs(manager._SESSION, cached)


if __name__ == "__main__":
    unittest.main()
