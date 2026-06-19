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
Tests that ``BasePluginManager.import_plugin`` does not leak ``sys.path``
entries, even when the imported plugin module raises an unexpected
exception.
"""

# ------------------------
# Python modules
# ------------------------
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace

# ------------------------
# Gramps modules
# ------------------------
from .._manager import BasePluginManager, _prepended_sys_path


# ------------------------------------------------------------
#
# PluginImportSysPathTest
#
# ------------------------------------------------------------
class PluginImportSysPathTest(unittest.TestCase):
    """Exercise the ``sys.path`` invariants of ``import_plugin``."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.directory = self._tmp.name
        self.manager = BasePluginManager.get_instance()
        self._sys_path_before = list(sys.path)
        self._sys_modules_before = set(sys.modules)

    def tearDown(self) -> None:
        sys.path[:] = self._sys_path_before
        for modname in list(sys.modules):
            if modname not in self._sys_modules_before:
                del sys.modules[modname]

    def _pdata(self, mod_name: str, plugin_id: str = "tpl") -> SimpleNamespace:
        return SimpleNamespace(fpath=self.directory, mod_name=mod_name, id=plugin_id)

    def _write_module(self, name: str, body: str) -> None:
        path = os.path.join(self.directory, name + ".py")
        with open(path, "w", encoding="utf-8") as file_descriptor:
            file_descriptor.write(body)

    def test_successful_import_does_not_leak_sys_path(self) -> None:
        """sys.path must be pristine after a successful import."""
        self._write_module("gramps_test_ok_mod", "VALUE = 42\n")
        pdata = self._pdata("gramps_test_ok_mod")
        module = self.manager.import_plugin(pdata)
        self.assertIsNotNone(module)
        self.assertEqual(sys.path, self._sys_path_before)
        self.assertNotIn(self.directory, sys.path)

    def test_import_error_does_not_leak_sys_path(self) -> None:
        """ImportError is caught and sys.path is still restored."""
        self._write_module(
            "gramps_test_bad_mod",
            "import this_module_does_not_exist_xyzzy\n",
        )
        pdata = self._pdata("gramps_test_bad_mod")
        result = self.manager.import_plugin(pdata)
        self.assertIsNone(result)
        self.assertEqual(sys.path, self._sys_path_before)

    def test_unexpected_exception_does_not_leak_sys_path(self) -> None:
        """An uncaught exception from the plugin module must still restore
        sys.path via the context manager's finally clause."""
        self._write_module(
            "gramps_test_raises_mod",
            "raise RuntimeError('oops at import time')\n",
        )
        pdata = self._pdata("gramps_test_raises_mod")
        with self.assertRaises(RuntimeError):
            self.manager.import_plugin(pdata)
        self.assertEqual(sys.path, self._sys_path_before)


# ------------------------------------------------------------
#
# PrependedSysPathTest
#
# ------------------------------------------------------------
class PrependedSysPathTest(unittest.TestCase):
    """Direct unit tests for the ``_prepended_sys_path`` context manager."""

    def test_inserts_and_removes_new_entry(self) -> None:
        marker = "/definitely/not/a/real/path/gramps_test_marker"
        self.assertNotIn(marker, sys.path)
        with _prepended_sys_path(marker):
            self.assertEqual(sys.path[0], marker)
        self.assertNotIn(marker, sys.path)

    def test_preserves_existing_entry(self) -> None:
        """If the path is already present we must not remove it on exit."""
        existing = sys.path[0] if sys.path else os.getcwd()
        with _prepended_sys_path(existing):
            pass
        self.assertIn(existing, sys.path)

    def test_removes_entry_even_on_exception(self) -> None:
        marker = "/definitely/not/a/real/path/gramps_test_marker_exc"
        self.assertNotIn(marker, sys.path)
        with self.assertRaises(RuntimeError):
            with _prepended_sys_path(marker):
                raise RuntimeError("boom")
        self.assertNotIn(marker, sys.path)

    def test_empty_path_is_noop(self) -> None:
        before = list(sys.path)
        with _prepended_sys_path(""):
            self.assertEqual(sys.path, before)
        self.assertEqual(sys.path, before)


if __name__ == "__main__":
    unittest.main()
