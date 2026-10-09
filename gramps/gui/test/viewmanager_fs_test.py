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
check — preventing an AttributeError crash and silent skip of update_menu()
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

os.environ.setdefault("GDK_BACKEND", "-")
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


# The method's global namespace — just what _update_familysearch_ui references.
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
        """uimanager present but familysearchgroup not yet created — must not raise."""
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


if __name__ == "__main__":
    unittest.main()
