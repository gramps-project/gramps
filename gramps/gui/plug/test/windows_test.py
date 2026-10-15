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

"""Unit test for ``AddonManager.install_addon`` — Mantis 13736.

Mantis 0013736: when an addon's project (under
Edit → Preferences → Addon Manager → Projects) targets a different
Gramps major.minor than the running Gramps (e.g. a 5.2 project carried
over from a pre-6.0 ``gramps.ini``), ``reg_plugins`` rejects the addon
on the ``valid_plugin_version`` check and ``self.__preg.get_plugin``
returns ``None`` in ``install_addon``. The pre-fix dialog said only
"The addon will be unavailable in your current configuration" — no
addon name, no hint at the target-version mismatch as the likely cause.

This test asserts the post-fix dialog includes:

1. The actual ``addon_id`` that failed, so the user knows which one.
2. The running Gramps ``major_version`` so they can compare against
   the project URL.
3. A pointer at ``Edit → Preferences → Addon Manager → Projects`` —
   where the user actually fixes the mismatch.

The test runs headless via ``__new__``-bypass on ``AddonManager``,
patches ``OkDialog`` in the module so the dialog text is captured
instead of rendered, and stubs the plugin manager / registry so the
``pdata is None`` failure branch is forced deterministically.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

# Pin GTK 3 BEFORE any gramps.gui import; the widgets module chain
# expects Gtk 3 enums (Gtk.IconSize.MENU etc.) and otherwise hits a
# version-mismatch import error.
import gi  # noqa: E402

gi.require_version("Gtk", "3.0")  # noqa: E402

from gramps.gui.plug import _windows as plug_windows  # noqa: E402
from gramps.gui.plug._windows import AddonManager  # noqa: E402


# -----------------------------------------------------------
#
# AddonManagerInstallAddonFailureDialogTest
#
# -----------------------------------------------------------
class AddonManagerInstallAddonFailureDialogTest(unittest.TestCase):
    """Regression test for Mantis 13736 — failure-dialog content."""

    def _make_addon_manager(self) -> AddonManager:
        """Construct an ``AddonManager`` via ``__new__`` (bypass
        ``__init__`` which builds the live Gtk dialog tree). The
        ``install_addon`` method only reads a handful of attributes;
        wire those, leave the rest unset.

        The pmgr/preg attributes are name-mangled (defined inside
        ``AddonManager.__init__`` as ``self.__pmgr`` / ``self.__preg``).
        mypy can't see them as class attributes when set via __new__
        bypass, hence the targeted ``attr-defined`` ignores — the same
        pattern other gramps GUI tests use for ``__new__``-built fixtures.
        """
        am = AddonManager.__new__(AddonManager)
        am._AddonManager__pmgr = MagicMock()  # type: ignore[attr-defined]
        am._AddonManager__preg = MagicMock()  # type: ignore[attr-defined]
        # ``install_addon`` passes ``self.dbstate`` / ``self.uistate``
        # as positional args to ``pmgr.reg_plugins``; pmgr is mocked but
        # the attribute access itself still has to resolve.
        am.dbstate = MagicMock()
        am.uistate = MagicMock()
        # ``self.window`` is passed as ``parent=`` to ``OkDialog``;
        # the patched OkDialog ignores it. Any object works.
        am.window = MagicMock()
        return am

    def test_failure_dialog_names_the_addon_and_points_at_projects(self) -> None:
        """When ``reg_plugins`` rejects an addon (``get_plugin`` returns
        ``None``), the dialog must include the addon id, the running
        Gramps major.minor, and a Projects-panel pointer.
        """
        am = self._make_addon_manager()
        am._AddonManager__preg.get_plugin.return_value = None  # type: ignore[attr-defined]

        addon_id = "SomeFifty2EraAddon"
        with patch.object(plug_windows, "OkDialog") as mock_dialog:
            am.install_addon(addon_id)

        mock_dialog.assert_called_once()
        # OkDialog(title, message, parent=...) -- args are positional.
        title = mock_dialog.call_args.args[0]
        message = mock_dialog.call_args.args[1]
        self.assertEqual(title, "Addon Registration Failed")

        # 1. The addon's id appears in the message.
        self.assertIn(
            addon_id,
            message,
            f"failure dialog message should name the addon ({addon_id!r}); "
            f"got: {message!r}",
        )

        # 2. The running Gramps major.minor appears in the message.
        self.assertIn(
            plug_windows.major_version,
            message,
            f"failure dialog message should include the running Gramps "
            f"version ({plug_windows.major_version!r}); got: {message!r}",
        )

        # 3. Points the user at the Projects panel (substring match
        #    on "Projects" — the localized arrow / preferences path
        #    around it varies but the panel name doesn't).
        self.assertIn(
            "Projects",
            message,
            "failure dialog message should point the user at the "
            "Addon Manager Projects panel where the mismatch is fixed; "
            f"got: {message!r}",
        )

    def test_failure_dialog_not_shown_on_success(self) -> None:
        """Sanity check that the dialog is NOT raised when the addon
        does register (``get_plugin`` returns a non-None pdata).
        """
        am = self._make_addon_manager()
        am._AddonManager__preg.get_plugin.return_value = MagicMock()  # type: ignore[attr-defined]

        with patch.object(plug_windows, "OkDialog") as mock_dialog:
            am.install_addon("SomeWorkingAddon")

        mock_dialog.assert_not_called()
        am._AddonManager__pmgr.load_plugin.assert_called_once()  # type: ignore[attr-defined]
        am._AddonManager__pmgr.emit.assert_called_with("plugins-reloaded")  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
