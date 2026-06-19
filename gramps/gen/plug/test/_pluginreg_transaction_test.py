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
Tests that ``PluginRegister.scan_dir`` is transactional per .gpr.py file:
a failure anywhere in the read/exec/register/validate pipeline must leave
the plugin registry exactly as it was before the file was processed.
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
# PluginRegTransactionTest
#
# ------------------------------------------------------------
class PluginRegTransactionTest(unittest.TestCase):
    """Exercise rollback semantics in ``PluginRegister.scan_dir``."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.directory = self._tmp.name
        self.registry = PluginRegister.get_instance()
        self._before_pdata = list(self.registry._PluginRegister__plugindata)
        self._before_ids = dict(self.registry._PluginRegister__id_to_pdata)

    def tearDown(self) -> None:
        self.registry._PluginRegister__plugindata = self._before_pdata
        self.registry._PluginRegister__id_to_pdata = self._before_ids

    def _write_gpr(self, name: str, body: str) -> None:
        path = os.path.join(self.directory, name)
        with open(path, "w", encoding="utf-8") as file_descriptor:
            file_descriptor.write(body)

    def test_rollback_on_exception_after_register_call(self) -> None:
        """If a gpr.py registers a plugin and then raises, the plugin must
        not remain in ``__plugindata`` or ``__id_to_pdata``."""
        body = (
            "register(TOOL,\n"
            "    id='tx_rollback_1', name='Rollback Test',\n"
            "    description='tx rollback test plugin',\n"
            "    version='1.0', status=STABLE, fname='tx_rollback.py',\n"
            "    authors=['Test'], authors_email=['t@example.com'],\n"
            "    category=TOOL_UTILS,\n"
            "    gramps_target_version=GRAMPSVERSION)\n"
            "raise RuntimeError('boom after register')\n"
        )
        self._write_gpr("tx_rollback.gpr.py", body)
        with self.assertLogs("._manager", level="ERROR"):
            self.registry.scan_dir(self.directory, ["tx_rollback.gpr.py"])
        plugindata = self.registry._PluginRegister__plugindata
        id_map = self.registry._PluginRegister__id_to_pdata
        self.assertEqual(
            plugindata,
            self._before_pdata,
            "scan_dir must roll back __plugindata on exception",
        )
        self.assertEqual(
            id_map,
            self._before_ids,
            "scan_dir must roll back __id_to_pdata on exception",
        )
        self.assertNotIn("tx_rollback_1", id_map)

    def test_rollback_on_value_error_in_gpr(self) -> None:
        """ValueError raised mid-file must also trigger a full rollback."""
        body = (
            "register(TOOL,\n"
            "    id='tx_rollback_2', name='Value Rollback',\n"
            "    description='tx rollback test plugin',\n"
            "    version='1.0', status=STABLE, fname='tx_rollback2.py',\n"
            "    authors=['Test'], authors_email=['t@example.com'],\n"
            "    category=TOOL_UTILS,\n"
            "    gramps_target_version=GRAMPSVERSION)\n"
            "raise ValueError('bad value')\n"
        )
        self._write_gpr("tx_rollback2.gpr.py", body)
        with self.assertLogs("._manager", level="ERROR"):
            self.registry.scan_dir(self.directory, ["tx_rollback2.gpr.py"])
        id_map = self.registry._PluginRegister__id_to_pdata
        self.assertEqual(self.registry._PluginRegister__plugindata, self._before_pdata)
        self.assertEqual(id_map, self._before_ids)
        self.assertNotIn("tx_rollback_2", id_map)

    def test_successful_scan_leaves_new_registrations(self) -> None:
        """Sanity check: a clean gpr.py must register normally and not be
        rolled back by the new transactional wrapper."""
        body = (
            "register(TOOL,\n"
            "    id='tx_success_1', name='Happy Plugin',\n"
            "    description='a plugin that registers cleanly',\n"
            "    version='1.0', status=STABLE, fname='tx_happy.py',\n"
            "    authors=['Test'], authors_email=['t@example.com'],\n"
            "    category=TOOL_UTILS,\n"
            "    gramps_target_version=GRAMPSVERSION)\n"
        )
        self._write_gpr("tx_happy.gpr.py", body)
        # the referenced fname must exist for the plugin to survive validation
        with open(
            os.path.join(self.directory, "tx_happy.py"), "w", encoding="utf-8"
        ) as file_descriptor:
            file_descriptor.write("")
        self.registry.scan_dir(self.directory, ["tx_happy.gpr.py"])
        self.assertIn("tx_success_1", self.registry._PluginRegister__id_to_pdata)


if __name__ == "__main__":
    unittest.main()
