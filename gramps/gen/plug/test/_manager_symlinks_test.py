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

"""Tests that plugin scanning follows symlinks and survives symlink loops."""

# ------------------------
# Python modules
# ------------------------
import os
import tempfile
import unittest
from unittest.mock import patch

# ------------------------
# Gramps modules
# ------------------------
from .._manager import BasePluginManager
from gramps.gen.constfunc import win


# ------------------------------------------------------------
#
# RegPluginsSymlinkTest
#
# ------------------------------------------------------------
@unittest.skipIf(win(), "Symlinks not supported or tested by default on Windows")
class RegPluginsSymlinkTest(unittest.TestCase):
    """Exercise the os.walk(followlinks=True) behavior in reg_plugins."""

    def setUp(self) -> None:
        self.mgr = BasePluginManager.get_instance()
        self.pgr = self.mgr._BasePluginManager__pgr  # type: ignore[attr-defined]

    def test_symlinked_subdir_is_scanned(self) -> None:
        """A directory reached only via a symlink must be scanned."""
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "target_plugin")
            os.makedirs(target)
            # A marker filename so we can confirm scan_dir saw target's contents.
            open(os.path.join(target, "marker.gpr.py"), "w").close()

            plugin_root = os.path.join(tmp, "plugins")
            os.makedirs(plugin_root)
            link = os.path.join(plugin_root, "linked_plugin")
            os.symlink(target, link, target_is_directory=True)

            with patch.object(self.pgr, "scan_dir") as mock_scan:
                self.mgr.reg_plugins(plugin_root)

            visited = [call.args[0] for call in mock_scan.call_args_list]
            self.assertIn(link, visited)
            # scan_dir must have received the marker filename for the link.
            link_call = next(
                call for call in mock_scan.call_args_list if call.args[0] == link
            )
            self.assertIn("marker.gpr.py", link_call.args[1])

    def test_self_referential_symlink_loop_terminates(self) -> None:
        """A symlink pointing at an ancestor must not cause infinite recursion."""
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, "plugin_root")
            os.makedirs(root)
            # Absolute symlink pointing back at root creates an infinite tree
            # under os.walk(..., followlinks=True) unless guarded.
            os.symlink(root, os.path.join(root, "loop"), target_is_directory=True)

            with patch.object(self.pgr, "scan_dir") as mock_scan:
                self.mgr.reg_plugins(root)

            # Either scan_dir is called a bounded number of times, or our
            # realpath dedup prunes the recursion before reaching scan_dir
            # a second time.  The absolute bound here is generous on purpose
            # to leave room for platform quirks.
            self.assertLess(mock_scan.call_count, 10)


if __name__ == "__main__":
    unittest.main()
