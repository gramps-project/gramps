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

"""Tests for ViewManager._update_familysearch_ui (issue 9 fix).

The fix restructured the method so that both the familysearchgroup visibility
calls and update_menu() are guarded under a single hasattr(self, "uimanager")
check â€” preventing an AttributeError crash and silent skip of update_menu()
when the method is called before the UI manager is fully initialised.

We load the method body directly from viewmanager.py using AST parsing,
avoiding the full GTK-heavy module import chain.
"""

# python3 -m unittest gramps.gui.test.viewmanager_fs_test -v

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import ast
import logging
import os
import types
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("LANG", "en_US.utf-8")

# -------------------------------------------------------------------------
#
# Extract _update_familysearch_ui from viewmanager.py via AST
#
# -------------------------------------------------------------------------
_VIEWMANAGER_PATH = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "viewmanager.py")
)


def _load_method_code(filepath: str, classname: str, methodname: str):
    """
    Parse a Python source file and return compiled code for one class method.

    The resulting code object can be exec'd to define the function in any
    namespace, without importing the surrounding module.
    """
    with open(filepath) as fh:
        source = fh.read()
    tree = ast.parse(source, filename=filepath)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == classname:
            for item in node.body:
                if (
                    isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name == methodname
                ):
                    mod = ast.Module(body=[item], type_ignores=[])
                    ast.fix_missing_locations(mod)
                    return compile(mod, filepath, "exec")
    raise ValueError(f"{classname}.{methodname} not found in {filepath}")


# The method's global namespace â€” just what _update_familysearch_ui references.
_LOG = logging.getLogger("gramps.gui.viewmanager")
_close_tools_window_stub = MagicMock(name="close_tools_window")
_METHOD_NS: dict = {
    "__builtins__": __builtins__,
    "LOG": _LOG,
    "close_tools_window": _close_tools_window_stub,
}

exec(
    _load_method_code(_VIEWMANAGER_PATH, "ViewManager", "_update_familysearch_ui"),
    _METHOD_NS,
)
_update_familysearch_ui = _METHOD_NS["_update_familysearch_ui"]


# -------------------------------------------------------------------------
#
# Helpers
#
# -------------------------------------------------------------------------


def _make_mock_vm(
    *,
    has_uimanager: bool = True,
    has_familysearchgroup: bool = True,
    fs_enabled: bool = True,
    file_loaded: bool = True,
):
    """
    Build a minimal stand-in for ViewManager with only the attributes that
    _update_familysearch_ui touches, so we can test the method in isolation.
    """
    vm = types.SimpleNamespace()
    vm.file_loaded = file_loaded
    vm._familysearch_enabled = lambda: fs_enabled
    vm.statusbar = types.SimpleNamespace(
        set_fs_visible=MagicMock(),
        set_fs_online=MagicMock(),
    )
    if has_uimanager:
        vm.uimanager = types.SimpleNamespace(
            set_actions_visible=MagicMock(),
            set_actions_sensitive=MagicMock(),
            update_menu=MagicMock(),
        )
    if has_familysearchgroup:
        vm.familysearchgroup = MagicMock()
    return vm


# -------------------------------------------------------------------------
#
# UpdateFamilySearchUiGuardTest
#
# -------------------------------------------------------------------------


class UpdateFamilySearchUiGuardTest(unittest.TestCase):
    """Tests for the hasattr(self, 'uimanager') guard in _update_familysearch_ui.

    Before the fix the familysearchgroup block and update_menu() had separate
    guards. The fix unified them so neither is attempted without uimanager.
    """

    def _call(self, vm):
        """Call the real method body on the mock vm object."""
        with patch.dict(_METHOD_NS, {"close_tools_window": MagicMock()}):
            _update_familysearch_ui(vm)

    def test_no_crash_without_uimanager(self):
        """Calling the method before uimanager is ready must not raise."""
        vm = _make_mock_vm(has_uimanager=False, has_familysearchgroup=False)
        try:
            self._call(vm)
        except AttributeError as exc:
            self.fail(f"_update_familysearch_ui raised AttributeError: {exc}")

    def test_no_crash_without_familysearchgroup(self):
        """uimanager present but familysearchgroup not yet created â€” must not raise."""
        vm = _make_mock_vm(has_uimanager=True, has_familysearchgroup=False)
        try:
            self._call(vm)
        except AttributeError as exc:
            self.fail(f"_update_familysearch_ui raised AttributeError: {exc}")

    def test_update_menu_called_when_uimanager_present(self):
        """update_menu() must be called when uimanager exists."""
        vm = _make_mock_vm(has_uimanager=True, has_familysearchgroup=True)
        self._call(vm)
        vm.uimanager.update_menu.assert_called_once()

    def test_familysearchgroup_visibility_set_when_both_present(self):
        """set_actions_visible and set_actions_sensitive called when both exist."""
        vm = _make_mock_vm(
            has_uimanager=True,
            has_familysearchgroup=True,
            fs_enabled=True,
            file_loaded=True,
        )
        self._call(vm)
        vm.uimanager.set_actions_visible.assert_called_once_with(
            vm.familysearchgroup, True
        )
        vm.uimanager.set_actions_sensitive.assert_called_once_with(
            vm.familysearchgroup, True
        )

    def test_update_menu_not_called_without_uimanager(self):
        """update_menu() must not be attempted when uimanager is absent."""
        vm = _make_mock_vm(has_uimanager=False, has_familysearchgroup=False)
        self._call(vm)
        self.assertFalse(hasattr(vm, "uimanager"))

    def test_familysearchgroup_not_called_without_uimanager(self):
        """set_actions_visible must not be called when uimanager is missing."""
        vm = _make_mock_vm(has_uimanager=False, has_familysearchgroup=True)
        self._call(vm)
        self.assertFalse(hasattr(vm, "uimanager"))
        vm.familysearchgroup.assert_not_called()

    def test_disabled_integration_hides_group(self):
        """When FS is disabled the group should be hidden/insensitive."""
        vm = _make_mock_vm(
            has_uimanager=True,
            has_familysearchgroup=True,
            fs_enabled=False,
            file_loaded=True,
        )
        self._call(vm)
        vm.uimanager.set_actions_visible.assert_called_once_with(
            vm.familysearchgroup, False
        )
        vm.uimanager.set_actions_sensitive.assert_called_once_with(
            vm.familysearchgroup, False
        )


# ------------------------------------------------------------
#
# IntegrationPreferencesTest
#
# ------------------------------------------------------------
class IntegrationPreferencesTest(unittest.TestCase):
    """Check integration setup without sending keys or starting authentication."""

    def test_access_setup_and_reachability(self) -> None:
        """Keep access requests separate and never authenticate connection tests."""
        import os
        from types import SimpleNamespace
        from unittest.mock import patch
        from gramps.gui.fs import integration_panel as panel

        values = {
            "familysearch.enable": True,
            "familysearch.server": 0,
            "familysearch.auth-provider": "foundation",
            "familysearch.middleware.base-url": "https://middleware.example.invalid",
        }
        configuration = MagicMock()
        configuration.get.side_effect = lambda key: values.get(key, "")
        configuration.set.side_effect = values.__setitem__
        for name, value in (("_SESSION", None), ("_SESSION_INVALIDATED", False)):
            patcher = patch.object(panel.manager, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        if not panel.Gtk.init_check()[0]:
            self.skipTest("GTK display unavailable")
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(panel, "config", configuration),
            patch.object(panel.manager, "current_session", return_value=None),
        ):
            section = panel.FamilySearchIntegrationPanel(
                SimpleNamespace(viewmanager=None)
            )
            self.addCleanup(section.widget.destroy)
            label = section._grid.get_child_at(0, 0)
            self.assertIs(label.get_mnemonic_widget(), section._server)
            menu = panel.Gtk.Menu()
            self.addCleanup(menu.destroy)
            section.cb_address_menu(section._address, menu)
            self.assertTrue(menu.get_children()[-1].get_sensitive())
            values["familysearch.enable"] = False
            section.cb_refresh()
            self.assertFalse(section._address.get_sensitive())
            section.cb_address_menu(section._address, menu)
            self.assertFalse(menu.get_children()[-1].get_sensitive())
            values["familysearch.enable"] = True
            section.cb_refresh()
            section._key.set_text("private-key")
            self.assertFalse(section._key.get_visibility())
            with patch.object(panel, "display_url") as opened:
                request_menu = panel.Gtk.Menu()
                self.addCleanup(request_menu.destroy)
                section.cb_key_menu(section._key, request_menu)
                self.assertTrue(request_menu.get_children()[-1].get_sensitive())
                request_menu.get_children()[-1].activate()
                opened.assert_called_once_with(
                    values["familysearch.middleware.base-url"]
                )
            response = MagicMock(status_code=200)
            response.__enter__.return_value = response
            with (
                patch.object(panel.requests, "get", return_value=response) as get,
                patch.object(panel.requests, "post") as post,
            ):
                self.assertIn(
                    "200",
                    panel.check_middleware(
                        str(values["familysearch.middleware.base-url"])
                    ),
                )
                self.assertNotIn("headers", get.call_args.kwargs)
                self.assertFalse(get.call_args.kwargs["allow_redirects"])
                self.assertEqual(get.call_args.kwargs["timeout"], (3, 5))
                post.assert_not_called()
            for address in (
                "",
                "invalid",
                "file:///private",
                "https://user:key@example.invalid",
            ):
                with (
                    self.subTest(address=address),
                    patch.object(panel.requests, "get") as get,
                ):
                    self.assertTrue(panel.check_middleware(address))
                    get.assert_not_called()
            with patch.object(
                panel.requests, "get", side_effect=panel.requests.ConnectionError
            ):
                self.assertTrue(
                    panel.check_middleware("https://middleware.example.invalid")
                )

    def test_session_settings_and_stale_results(self) -> None:
        """Show the real session state and discard results for old settings."""
        import os
        from types import SimpleNamespace
        from unittest.mock import patch
        from gramps.gui.fs import integration_panel as panel

        values = {"familysearch.enable": True, "familysearch.server": 0}
        configuration = MagicMock()
        configuration.get.side_effect = lambda key: values.get(key, "")
        configuration.set.side_effect = values.__setitem__
        session = SimpleNamespace(
            access_token="private-token",
            connected=True,
            _profile=SimpleNamespace(env="beta"),
            logout=MagicMock(),
        )
        if not panel.Gtk.init_check()[0]:
            self.skipTest("GTK display unavailable")
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(panel, "config", configuration),
            patch.object(panel.manager, "current_session", return_value=session),
        ):
            section = panel.FamilySearchIntegrationPanel(
                SimpleNamespace(viewmanager=None)
            )
            self.addCleanup(section.widget.destroy)
            self.assertEqual(
                section._status.get_text(), panel._("Signed in to FamilySearch.")
            )
            self.assertFalse(section._server.get_sensitive())
            self.assertFalse(section._sign_in.get_sensitive())
            self.assertTrue(section._sign_out.get_sensitive())
            values["familysearch.server"] = 1
            section.cb_refresh()
            self.assertEqual(
                section._status.get_text(),
                panel._("Sign out before using the selected server."),
            )
            self.assertEqual(
                section._account_note.get_text(),
                panel._("Production requires your regular FamilySearch account."),
            )
            with (
                patch.object(panel.manager, "invalidate_session") as invalidate,
                patch.object(panel.threading, "Thread") as worker,
                patch.object(
                    panel.GLib, "idle_add", side_effect=lambda callback: callback()
                ),
            ):
                section.cb_sign_out(None)
                worker.call_args.kwargs["target"]()
                session.logout.assert_called_once()
                invalidate.assert_called_once()
            section._status.set_text("current result")
            section.cb_test_finished(section._generation - 1, "outdated result")
            self.assertEqual(section._status.get_text(), "current result")
        with (
            patch.object(panel.manager, "_SESSION", session),
            patch.object(panel.manager, "_SESSION_INVALIDATED", False),
            patch.object(panel.manager, "get_active_session", return_value=session),
        ):
            panel.manager.invalidate_session()
            self.assertIsNone(panel.manager.current_session())


if __name__ == "__main__":
    unittest.main()
