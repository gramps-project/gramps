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
Tests for ``plugin_version_status`` classification and the deprecation
warning emitted by ``PluginRegister.scan_dir`` for one-minor-behind
plugins.
"""

# ------------------------
# Python modules
# ------------------------
import os
import tempfile
import unittest
from unittest import mock

# ------------------------
# Gramps modules
# ------------------------
from .. import _pluginreg
from .._pluginreg import (
    PluginRegister,
    PluginVersionStatus,
    plugin_version_status,
    valid_plugin_version,
)


# ------------------------------------------------------------
#
# PluginVersionStatusTest
#
# ------------------------------------------------------------
class PluginVersionStatusTest(unittest.TestCase):
    """Unit tests for :func:`plugin_version_status`."""

    def test_exact_major_minor_is_current(self) -> None:
        self.assertEqual(
            plugin_version_status("6.1", current_version=(6, 1, 0)),
            PluginVersionStatus.CURRENT,
        )

    def test_exact_major_minor_patch_is_current(self) -> None:
        self.assertEqual(
            plugin_version_status("6.1.0", current_version=(6, 1, 0)),
            PluginVersionStatus.CURRENT,
        )

    def test_older_patch_of_current_minor_is_current(self) -> None:
        self.assertEqual(
            plugin_version_status("6.1.0", current_version=(6, 1, 5)),
            PluginVersionStatus.CURRENT,
        )

    def test_future_patch_of_current_minor_is_invalid(self) -> None:
        self.assertEqual(
            plugin_version_status("6.1.5", current_version=(6, 1, 0)),
            PluginVersionStatus.INVALID,
        )

    def test_previous_minor_is_deprecated(self) -> None:
        self.assertEqual(
            plugin_version_status("6.0", current_version=(6, 1, 0)),
            PluginVersionStatus.DEPRECATED,
        )

    def test_previous_minor_with_any_patch_is_deprecated(self) -> None:
        self.assertEqual(
            plugin_version_status("6.0.99", current_version=(6, 1, 0)),
            PluginVersionStatus.DEPRECATED,
        )

    def test_two_minors_behind_is_invalid(self) -> None:
        self.assertEqual(
            plugin_version_status("6.0", current_version=(6, 2, 0)),
            PluginVersionStatus.INVALID,
        )

    def test_different_major_is_invalid(self) -> None:
        self.assertEqual(
            plugin_version_status("5.9", current_version=(6, 1, 0)),
            PluginVersionStatus.INVALID,
        )

    def test_future_major_is_invalid(self) -> None:
        self.assertEqual(
            plugin_version_status("7.0", current_version=(6, 1, 0)),
            PluginVersionStatus.INVALID,
        )

    def test_future_minor_is_invalid(self) -> None:
        self.assertEqual(
            plugin_version_status("6.2", current_version=(6, 1, 0)),
            PluginVersionStatus.INVALID,
        )

    def test_zero_minor_has_no_deprecation_window(self) -> None:
        """On Gramps X.0.0 there is no previous minor to be deprecated."""
        self.assertEqual(
            plugin_version_status("6.0", current_version=(6, 0, 0)),
            PluginVersionStatus.CURRENT,
        )
        self.assertEqual(
            plugin_version_status("5.9", current_version=(6, 0, 0)),
            PluginVersionStatus.INVALID,
        )

    def test_non_string_is_invalid(self) -> None:
        self.assertEqual(
            plugin_version_status(None, current_version=(6, 1, 0)),
            PluginVersionStatus.INVALID,
        )
        self.assertEqual(
            plugin_version_status(61, current_version=(6, 1, 0)),
            PluginVersionStatus.INVALID,
        )

    def test_malformed_string_is_invalid(self) -> None:
        for bad in ("", "not-a-version", "6", "6.1.2.3", "6.x", "..", "6.1."):
            with self.subTest(value=bad):
                self.assertEqual(
                    plugin_version_status(bad, current_version=(6, 1, 0)),
                    PluginVersionStatus.INVALID,
                )


# ------------------------------------------------------------
#
# ValidPluginVersionCompatTest
#
# ------------------------------------------------------------
class ValidPluginVersionCompatTest(unittest.TestCase):
    """``valid_plugin_version`` is kept as a bool compat wrapper; verify it
    now also accepts one-minor-behind (deprecated) targets."""

    def test_current_is_valid(self) -> None:
        with mock.patch.object(_pluginreg, "VERSION_TUPLE", new=(6, 1, 0)):
            self.assertTrue(valid_plugin_version("6.1"))

    def test_deprecated_is_valid(self) -> None:
        with mock.patch.object(_pluginreg, "VERSION_TUPLE", new=(6, 1, 0)):
            self.assertTrue(valid_plugin_version("6.0"))

    def test_invalid_is_rejected(self) -> None:
        with mock.patch.object(_pluginreg, "VERSION_TUPLE", new=(6, 1, 0)):
            self.assertFalse(valid_plugin_version("5.9"))
            self.assertFalse(valid_plugin_version("6.2"))
            self.assertFalse(valid_plugin_version("garbage"))


# ------------------------------------------------------------
#
# ScanDirDeprecationWarningTest
#
# ------------------------------------------------------------
class ScanDirDeprecationWarningTest(unittest.TestCase):
    """A ``.gpr.py`` targeting the previous minor must be registered but
    must also trigger a deprecation warning through the module logger."""

    def setUp(self) -> None:
        """
        Create a temporary plugin directory and snapshot the shared
        ``PluginRegister`` state so it can be restored in ``tearDown``.
        """
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.directory = self._tmp.name
        self.registry = PluginRegister.get_instance()
        self._before_pdata = list(self.registry._PluginRegister__plugindata)
        self._before_ids = dict(self.registry._PluginRegister__id_to_pdata)

    def tearDown(self) -> None:
        """
        Restore the ``PluginRegister`` state captured in ``setUp`` so the
        scan performed by a test does not leak into other tests.
        """
        self.registry._PluginRegister__plugindata = self._before_pdata
        self.registry._PluginRegister__id_to_pdata = self._before_ids

    def _write_gpr(self, name: str, body: str) -> None:
        """
        Write *body* to a file named *name* in the temporary directory.

        :param name: The file name to create within the temporary
                     plugin directory.
        :type name: str
        :param body: The text content to write into the file.
        :type body: str
        :returns: Nothing.
        :rtype: None
        """
        path = os.path.join(self.directory, name)
        with open(path, "w", encoding="utf-8") as file_descriptor:
            file_descriptor.write(body)

    def test_deprecated_plugin_is_registered_with_warning(self) -> None:
        gpr_body = (
            "register(TOOL,\n"
            "    id='version_skew_test', name='Skewed Plugin',\n"
            "    description='targets previous minor version',\n"
            "    version='1.0', status=STABLE,\n"
            "    fname='version_skew_plugin.py',\n"
            "    authors=['Test'], authors_email=['t@example.com'],\n"
            "    category=TOOL_UTILS,\n"
            "    gramps_target_version='6.0')\n"
        )
        self._write_gpr("version_skew_test.gpr.py", gpr_body)
        with open(
            os.path.join(self.directory, "version_skew_plugin.py"),
            "w",
            encoding="utf-8",
        ) as file_descriptor:
            file_descriptor.write("")
        with mock.patch.object(_pluginreg, "VERSION_TUPLE", new=(6, 1, 0)):
            with mock.patch.object(_pluginreg, "GRAMPSVERSION", new="6.1.0"):
                with self.assertLogs("._manager", level="WARNING") as captured:
                    self.registry.scan_dir(self.directory, ["version_skew_test.gpr.py"])
        self.assertIn("version_skew_test", self.registry._PluginRegister__id_to_pdata)
        joined = "\n".join(captured.output)
        self.assertIn("6.0", joined)
        self.assertIn("deprecated", joined.lower())


if __name__ == "__main__":
    unittest.main()
