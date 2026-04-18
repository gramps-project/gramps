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
Tests that the plugin registration scanner logs errors rather than crashing
and leaves no partial registrations behind when a gpr.py fails.
"""

# ------------------------
# Python modules
# ------------------------
import os
import tempfile
import unittest

# ------------------------
# Gramps modules
# ------------------------
from .._pluginreg import PluginRegister


# ------------------------------------------------------------
#
# PluginRegScanErrorsTest
#
# ------------------------------------------------------------
class PluginRegScanErrorsTest(unittest.TestCase):
    """Exercise the error paths in ``PluginRegister.scan_dir``."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.directory = self._tmp.name
        self.registry = PluginRegister.get_instance()
        # name-mangled access; the registry is a singleton and other tests
        # may have populated it, so we measure deltas against a snapshot.
        self._before_pdata = list(self.registry._PluginRegister__plugindata)
        self._before_ids = dict(self.registry._PluginRegister__id_to_pdata)

    def tearDown(self) -> None:
        self.registry._PluginRegister__plugindata = self._before_pdata
        self.registry._PluginRegister__id_to_pdata = self._before_ids

    def _write_gpr(self, name: str, body: str, *, encoding: str = "utf-8") -> str:
        path = os.path.join(self.directory, name)
        with open(path, "w", encoding=encoding) as file_descriptor:
            file_descriptor.write(body)
        return name

    def test_runtime_error_in_gpr_is_caught_and_logged(self) -> None:
        """A non-ValueError raised by a gpr.py must be logged, not propagated."""
        self._write_gpr("broken.gpr.py", "raise RuntimeError('kaboom')\n")
        with self.assertLogs("._manager", level="ERROR") as captured:
            self.registry.scan_dir(self.directory, ["broken.gpr.py"])
        joined = "\n".join(captured.output)
        self.assertIn("Failed reading plugin registration", joined)
        self.assertIn("broken.gpr.py", joined)
        added = self.registry._PluginRegister__plugindata[len(self._before_pdata) :]
        self.assertEqual(added, [], "No plugin data should be registered on failure")

    def test_value_error_in_gpr_is_caught_and_logged(self) -> None:
        """ValueError has its own except arm; ensure it still logs."""
        self._write_gpr("bad_value.gpr.py", "raise ValueError('bad value')\n")
        with self.assertLogs("._manager", level="ERROR") as captured:
            self.registry.scan_dir(self.directory, ["bad_value.gpr.py"])
        self.assertIn("bad_value.gpr.py", "\n".join(captured.output))

    def test_non_utf8_gpr_is_caught_and_logged(self) -> None:
        """A gpr.py with non-UTF-8 bytes must not crash the scan."""
        path = os.path.join(self.directory, "bad_bytes.gpr.py")
        with open(path, "wb") as file_descriptor:
            file_descriptor.write(b"\xff\xfe not utf-8 bytes")
        with self.assertLogs("._manager", level="ERROR") as captured:
            self.registry.scan_dir(self.directory, ["bad_bytes.gpr.py"])
        self.assertIn("bad_bytes.gpr.py", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
