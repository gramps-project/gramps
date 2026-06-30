# -*- coding: utf-8 -*-
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Tests for the Mac localization helpers in :mod:`gramps.gen.utils.maclocale`.
"""

# ------------------------
# Python modules
# ------------------------
import io
import os
import subprocess
import unittest
from unittest.mock import patch

# ------------------------
# Gramps modules
# ------------------------
from .. import maclocale


# ------------------------------------------------------------
#
# _FakeProc
#
# ------------------------------------------------------------
class _FakeProc:
    """
    Minimal stand-in for the object returned by ``subprocess.Popen``.

    Supports the context-manager protocol used at
    ``maclocale.py`` and returns empty output so every ``defaults``
    lookup is treated as "no preference set".
    """

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def communicate(self):
        return (b"", b"")


# ------------------------------------------------------------
#
# _FakeGLocale
#
# ------------------------------------------------------------
class _FakeGLocale:
    """
    Stub of the GrampsLocale object ``mac_setup_localization`` mutates.

    ``check_available_translations`` always returns ``None`` so the
    function falls through to its built-in ``en_US`` default without
    needing the translation machinery.
    """

    def __init__(self):
        self.lang = None
        self.language = None
        self.calendar = None
        self.collation = None
        self.coll_qualifier = None
        self.encoding = None

    def check_available_translations(self, lang):
        return None


# ------------------------------------------------------------
#
# MacLocaleDefaultsTest
#
# ------------------------------------------------------------
class MacLocaleDefaultsTest(unittest.TestCase):
    """
    Regression coverage for the ``defaults`` subprocess call.

    The real leak path (Mantis 14243) is only *reached* on macOS, where
    ``/usr/bin/defaults`` exists; on other platforms the exec raises
    ``OSError`` before ``Popen`` returns. To exercise it everywhere we
    replace ``subprocess.Popen`` with a stub that records the ``stderr``
    argument it is handed, then drive the public entry point.
    """

    def _run_with_stub(self):
        """
        Invoke ``mac_setup_localization`` with Popen stubbed out and
        return the list of ``stderr`` arguments it was called with.
        """
        captured = []

        def fake_popen(args, **kwargs):
            captured.append(kwargs.get("stderr"))
            return _FakeProc()

        # Neutralise env vars that would short-circuit the defaults
        # lookups so the Popen path is actually taken.
        environ = dict(os.environ)
        for var in ("COLLATION", "LANGUAGE", "LANG"):
            environ.pop(var, None)

        with patch.object(maclocale.subprocess, "Popen", fake_popen):
            with patch.dict(os.environ, environ, clear=True):
                maclocale.mac_setup_localization(_FakeGLocale())

        return captured

    def test_defaults_stderr_is_not_a_leaked_file(self):
        """
        ``defaults`` must be invoked with a stderr sink that does not
        leak a Python file object.

        Mantis 14243: ``stderr=open("/dev/null")`` handed ``Popen`` a
        ``TextIOWrapper`` the context manager never closes (``Popen``
        only closes the pipes it opens itself), raising a
        ``ResourceWarning`` on garbage collection. ``subprocess.DEVNULL``
        leaves no Python-level file object to leak.
        """
        captured = self._run_with_stub()

        self.assertTrue(captured, "defaults subprocess was never invoked")
        for stderr_arg in captured:
            self.assertNotIsInstance(
                stderr_arg,
                io.IOBase,
                "defaults stderr is a caller-opened file object, which "
                "Popen's context manager does not close (Mantis 14243); "
                "use subprocess.DEVNULL instead",
            )

    def test_defaults_stderr_is_devnull(self):
        """
        Pin the specific sink to ``subprocess.DEVNULL`` so a future
        regression to ``open(os.devnull)`` is caught even if the handle
        happens to be closed elsewhere.
        """
        captured = self._run_with_stub()

        self.assertTrue(captured, "defaults subprocess was never invoked")
        for stderr_arg in captured:
            self.assertIs(stderr_arg, subprocess.DEVNULL)


if __name__ == "__main__":
    unittest.main()
