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

"""Tests for the user-customizable keyboard shortcut API on UIManager."""

# python3 -m unittest gramps.gui.test.uimanager_test -v

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import ast
import os
import tempfile
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("GDK_BACKEND", "-")
os.environ.setdefault("LANG", "en_US.utf-8")

import gi

gi.require_version("Gtk", "3.0")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gui.uimanager import ActionGroup, UIManager, _normalize_accel, check_accel

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="menubar">
    <section>
      <item>
        <attribute name="action">win.Clipboard</attribute>
        <attribute name="label" translatable="yes">Clip_board</attribute>
      </item>
    </section>
  </menu>
</interface>
"""


def make_manager():
    """Build a UIManager with a mock Gtk.Application-like accel backend."""
    bindings = {}

    app = MagicMock()
    app.set_accels_for_action.side_effect = lambda action_id, accels: bindings.update(
        {action_id: list(accels)}
    )
    app.get_accels_for_action.side_effect = lambda action_id: bindings.get(
        action_id, []
    )
    app.get_actions_for_accel.side_effect = lambda accel: [
        action_id for action_id, accels in bindings.items() if accel in accels
    ]

    manager = UIManager(app, SAMPLE_XML)
    group = ActionGroup(
        "Main",
        [
            ("Clipboard", None, "<Primary>b"),
            ("Undo", None, "<Primary>z"),
        ],
    )
    manager.insert_action_group(group, MagicMock())
    return manager


class NormalizeAccelTest(unittest.TestCase):
    """
    _normalize_accel() must be a safe no-op when running headless (as
    this test suite always does, per GDK_BACKEND=-): Gtk.accelerator_parse
    silently drops modifiers like <Primary> without a real display, so
    normalizing under test would corrupt values rather than canonicalize
    them.
    """

    def test_empty_string_stays_empty(self):
        self.assertEqual(_normalize_accel(""), "")

    def test_headless_passthrough_leaves_value_unchanged(self):
        self.assertEqual(os.environ.get("GDK_BACKEND"), "-")
        self.assertEqual(_normalize_accel("<PRIMARY>b"), "<PRIMARY>b")
        self.assertEqual(_normalize_accel("<shift><PRIMARY>R"), "<shift><PRIMARY>R")


class DefaultAccelsTest(unittest.TestCase):
    """default_accels must capture the hard-coded accel for each action."""

    def test_defaults_recorded_on_insert(self):
        manager = make_manager()
        self.assertEqual(manager.default_accels["win.Clipboard"], "<Primary>b")
        self.assertEqual(manager.default_accels["win.Undo"], "<Primary>z")


class ActionLabelTest(unittest.TestCase):
    """get_action_label pulls from the menu XML, falling back to the name."""

    def test_label_from_menu_strips_mnemonic(self):
        manager = make_manager()
        self.assertEqual(manager.get_action_label("win.Clipboard"), "Clipboard")

    def test_label_falls_back_to_action_name(self):
        manager = make_manager()
        self.assertEqual(manager.get_action_label("win.Undo"), "Undo")


class ListActionsTest(unittest.TestCase):
    def test_list_actions_reports_current_and_default(self):
        manager = make_manager()
        actions = {a["action_id"]: a for a in manager.list_actions()}
        self.assertEqual(actions["win.Clipboard"]["current_accel"], "<Primary>b")
        self.assertEqual(actions["win.Clipboard"]["default_accel"], "<Primary>b")
        self.assertEqual(actions["win.Clipboard"]["group_name"], "Main")

    def test_window_manager_group_is_excluded(self):
        """The WindowManager group holds per-open-window switcher actions
        (generate_id() in managedwindow.py keys them off the window's
        instance id), so they are not stable, listable commands and must
        not clutter the shortcut editor."""
        manager = make_manager()
        group = ActionGroup("WindowManager", [("wm-12345", None, "")])
        manager.insert_action_group(group, MagicMock())
        actions = {a["action_id"] for a in manager.list_actions()}
        self.assertNotIn("win.wm-12345", actions)


class MenuActionIdsTest(unittest.TestCase):
    """menu_action_ids reports actions reachable by clicking a menu item,
    as opposed to toolbar-only or keyboard-only actions."""

    def test_action_present_in_menu_xml_is_reported(self):
        manager = make_manager()
        self.assertIn("win.Clipboard", manager.menu_action_ids())

    def test_action_absent_from_menu_xml_is_not_reported(self):
        manager = make_manager()
        self.assertNotIn("win.Undo", manager.menu_action_ids())


class SetClearResetAccelTest(unittest.TestCase):
    def test_set_accel_rebinds_and_records_override(self):
        manager = make_manager()
        conflicts = manager.set_accel("win.Undo", "<Primary>y")
        self.assertEqual(conflicts, [])
        self.assertEqual(manager.get_accel("win.Undo"), "<Primary>y")
        self.assertEqual(manager.accel_dict["win.Undo"], "<Primary>y")

    def test_set_accel_reports_conflicting_actions(self):
        manager = make_manager()
        conflicts = manager.set_accel("win.Undo", "<Primary>b")
        self.assertEqual(conflicts, ["win.Clipboard"])
        # both are left bound; the caller decides whether to clear one
        self.assertEqual(manager.get_accel("win.Clipboard"), "<Primary>b")
        self.assertEqual(manager.get_accel("win.Undo"), "<Primary>b")

    def test_clear_accel_empties_binding(self):
        manager = make_manager()
        manager.clear_accel("win.Clipboard")
        self.assertEqual(manager.get_accel("win.Clipboard"), "")
        self.assertEqual(manager.accel_dict["win.Clipboard"], "")

    def test_reset_accel_restores_default_and_drops_override(self):
        manager = make_manager()
        manager.set_accel("win.Clipboard", "<Primary>k")
        manager.reset_accel("win.Clipboard")
        self.assertEqual(manager.get_accel("win.Clipboard"), "<Primary>b")
        self.assertNotIn("win.Clipboard", manager.accel_dict)

    def test_reset_accel_with_no_default_clears(self):
        manager = make_manager()
        manager.set_accel("win.Clipboard", "<Primary>k")
        manager.default_accels.pop("win.Clipboard")
        manager.reset_accel("win.Clipboard")
        self.assertEqual(manager.get_accel("win.Clipboard"), "")


class CheckAccelTest(unittest.TestCase):
    def test_empty_string_is_allowed(self):
        self.assertEqual(check_accel(""), "")

    def test_modified_letter_is_allowed(self):
        # Gtk.accelerator_name() -- what the shortcut editor actually
        # feeds check_accel() -- always emits a concrete modifier name
        # like '<Control>', never the virtual '<Primary>'.
        self.assertEqual(check_accel("<Control>a"), "")

    def test_bare_letter_is_reserved(self):
        self.assertNotEqual(check_accel("a"), "")

    def test_bare_space_is_reserved(self):
        self.assertNotEqual(check_accel("space"), "")

    def test_bare_escape_is_reserved(self):
        self.assertNotEqual(check_accel("Escape"), "")

    def test_bare_return_is_reserved(self):
        self.assertNotEqual(check_accel("Return"), "")

    def test_bare_delete_is_reserved(self):
        self.assertNotEqual(check_accel("Delete"), "")

    def test_bare_tab_is_reserved(self):
        self.assertNotEqual(check_accel("Tab"), "")

    def test_bare_arrow_is_reserved(self):
        self.assertNotEqual(check_accel("Up"), "")

    def test_bare_function_key_is_allowed(self):
        self.assertEqual(check_accel("F1"), "")

    def test_bare_menu_key_is_allowed(self):
        self.assertEqual(check_accel("Menu"), "")

    def test_uimanager_method_delegates(self):
        manager = make_manager()
        self.assertEqual(manager.check_accel("<Control>a"), "")
        self.assertNotEqual(manager.check_accel("a"), "")


class SaveLoadAccelsTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

    def _path(self, name):
        return os.path.join(self.tmpdir.name, name)

    def test_save_only_changed_omits_untouched_defaults(self):
        manager = make_manager()
        manager.set_accel("win.Clipboard", "<Primary>k")
        path = self._path("gramps.accel")
        manager.save_accels(path, only_changed=True)
        with open(path) as hndl:
            data = ast.literal_eval(hndl.read())
        self.assertEqual(data, {"win.Clipboard": "<Primary>k"})

    def test_save_full_dump_includes_every_action(self):
        manager = make_manager()
        path = self._path("gramps.accel")
        manager.save_accels(path, only_changed=False)
        with open(path) as hndl:
            data = ast.literal_eval(hndl.read())
        self.assertEqual(
            data, {"win.Clipboard": "<Primary>b", "win.Undo": "<Primary>z"}
        )

    def test_load_accels_replaces_by_default(self):
        manager = make_manager()
        manager.accel_dict = {"win.Undo": "<Primary>y"}
        path = self._path("gramps.accel")
        with open(path, "w") as hndl:
            hndl.write(repr({"win.Clipboard": "<Primary>x"}))
        manager.load_accels(path)
        self.assertEqual(manager.accel_dict, {"win.Clipboard": "<Primary>x"})
        self.assertEqual(manager.get_accel("win.Clipboard"), "<Primary>x")

    def test_load_accels_merge_layers_on_top(self):
        manager = make_manager()
        manager.accel_dict = {"win.Undo": "<Primary>y"}
        path = self._path("gramps.accel")
        with open(path, "w") as hndl:
            hndl.write(repr({"win.Clipboard": "<Primary>x"}))
        manager.load_accels(path, merge=True)
        self.assertEqual(
            manager.accel_dict,
            {"win.Undo": "<Primary>y", "win.Clipboard": "<Primary>x"},
        )

    def test_save_then_load_round_trip(self):
        manager = make_manager()
        manager.set_accel("win.Clipboard", "<Primary>k")
        path = self._path("gramps.accel")
        manager.save_accels(path, only_changed=True)

        reloaded = make_manager()
        reloaded.load_accels(path)
        self.assertEqual(reloaded.get_accel("win.Clipboard"), "<Primary>k")


class StaticRegistrationTest(unittest.TestCase):
    """
    register_static_shortcuts() lets an action be known -- listed, bound,
    reset, exported -- without its action group ever having been inserted
    into the UIManager. This is what makes the shortcuts editor complete
    for a view that hasn't been visited yet this session, instead of only
    showing whatever view happens to be active right now.
    """

    def _manager_with_static_action(self):
        manager = make_manager()
        manager.register_static_shortcuts(
            [("Sidebar", "<shift><PRIMARY>R", "_Sidebar")],
            "List Views",
            prefix="win",
        )
        return manager

    def test_never_live_action_appears_in_list_actions(self):
        manager = self._manager_with_static_action()
        actions = {a["action_id"]: a for a in manager.list_actions()}
        self.assertIn("win.Sidebar", actions)
        self.assertEqual(actions["win.Sidebar"]["current_accel"], "<shift><PRIMARY>R")
        self.assertEqual(actions["win.Sidebar"]["default_accel"], "<shift><PRIMARY>R")
        self.assertEqual(actions["win.Sidebar"]["group_name"], "List Views")

    def test_never_live_action_label_is_mnemonic_stripped(self):
        manager = self._manager_with_static_action()
        self.assertEqual(manager.get_action_label("win.Sidebar"), "Sidebar")

    def test_never_live_action_get_accel_returns_default(self):
        manager = self._manager_with_static_action()
        self.assertEqual(manager.get_accel("win.Sidebar"), "<shift><PRIMARY>R")

    def test_never_live_action_can_be_bound(self):
        manager = self._manager_with_static_action()
        conflicts = manager.set_accel("win.Sidebar", "<PRIMARY>k")
        self.assertEqual(conflicts, [])
        self.assertEqual(manager.get_accel("win.Sidebar"), "<PRIMARY>k")

    def test_conflict_detected_against_never_live_action(self):
        manager = self._manager_with_static_action()
        # "win.Clipboard" is a real, currently-live action from make_manager();
        # binding it to the still-never-instantiated Sidebar's default accel
        # must be flagged even though Sidebar's action group was never
        # inserted into the UIManager.
        conflicts = manager.set_accel("win.Clipboard", "<shift><PRIMARY>R")
        self.assertEqual(conflicts, ["win.Sidebar"])

    def test_reset_never_live_action_after_override(self):
        manager = self._manager_with_static_action()
        manager.set_accel("win.Sidebar", "<PRIMARY>k")
        manager.reset_accel("win.Sidebar")
        self.assertEqual(manager.get_accel("win.Sidebar"), "<shift><PRIMARY>R")

    def test_save_full_dump_includes_never_live_action(self):
        manager = self._manager_with_static_action()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "gramps.accel")
            manager.save_accels(path, only_changed=False)
            with open(path) as hndl:
                data = ast.literal_eval(hndl.read())
        self.assertEqual(data["win.Sidebar"], "<shift><PRIMARY>R")

    def test_action_with_no_default_accel_is_listed_but_unbound(self):
        manager = make_manager()
        manager.register_static_shortcuts(
            [("Merge", "", "Merge")], "List Views", prefix="win"
        )
        actions = {a["action_id"]: a for a in manager.list_actions()}
        self.assertIn("win.Merge", actions)
        self.assertEqual(actions["win.Merge"]["current_accel"], "")
        self.assertEqual(actions["win.Merge"]["default_accel"], "")


class PluginMenuAccelTest(unittest.TestCase):
    """
    Tools and Reports menu entries are built dynamically per installed
    plugin by viewmanager.build_plugin_menu(), one action per plugin, with
    no hard-coded default accelerator. Confirm they are still fully
    bindable through the shortcuts editor, conflict-checked against other
    actions, and that a saved binding survives the menu being torn down
    and rebuilt (as happens on a 'plugins-reloaded' event).
    """

    def _insert_tool_group(self, manager, action_name="VerifyTheData"):
        group = ActionGroup(name="Tools")
        group.add_actions([(action_name, None, "")])
        manager.insert_action_group(group)
        return group

    def test_plugin_action_is_listed_with_no_default(self):
        manager = make_manager()
        self._insert_tool_group(manager)
        actions = {a["action_id"]: a for a in manager.list_actions()}
        self.assertIn("win.VerifyTheData", actions)
        self.assertEqual(actions["win.VerifyTheData"]["default_accel"], "")
        self.assertEqual(actions["win.VerifyTheData"]["current_accel"], "")
        self.assertEqual(actions["win.VerifyTheData"]["group_name"], "Tools")

    def test_plugin_action_can_be_bound(self):
        manager = make_manager()
        self._insert_tool_group(manager)
        conflicts = manager.set_accel("win.VerifyTheData", "<PRIMARY><shift>V")
        self.assertEqual(conflicts, [])
        self.assertEqual(manager.get_accel("win.VerifyTheData"), "<PRIMARY><shift>V")

    def test_plugin_action_conflict_detected(self):
        manager = make_manager()
        self._insert_tool_group(manager)
        # "<Primary>z" is make_manager()'s default binding for "win.Undo"
        conflicts = manager.set_accel("win.VerifyTheData", "<Primary>z")
        self.assertEqual(conflicts, ["win.Undo"])

    def test_plugin_action_binding_survives_menu_rebuild(self):
        manager = make_manager()
        group = self._insert_tool_group(manager)
        manager.set_accel("win.VerifyTheData", "<PRIMARY><shift>V")

        # Simulate __build_tools_menu() rebuilding the menu, e.g. after a
        # 'plugins-reloaded' event: the old group is removed and a fresh
        # one, from re-scanning installed plugins, takes its place.
        manager.remove_action_group(group)
        self._insert_tool_group(manager)

        self.assertEqual(manager.get_accel("win.VerifyTheData"), "<PRIMARY><shift>V")


class GladeAccelConflictScopeTest(unittest.TestCase):
    """
    Each .glade file's <accelerator> tags are scoped to that dialog's own
    implicit Gtk.AccelGroup -- editor dialogs are never open at the same
    time, so the same key reused across two different dialogs is not a
    real conflict, unlike within the same dialog.
    """

    def _manager_with_two_dialogs(self):
        manager = make_manager()
        manager.register_static_shortcuts(
            [
                ("select", "<Primary>s", "Person"),
                ("add_del", "<Primary>s", "Person"),
            ],
            "Person Reference Editor",
            prefix="glade.editpersonref",
        )
        manager.register_static_shortcuts(
            [("select_place", "<Primary>d", "Place")],
            "Event Editor",
            prefix="glade.editevent",
        )
        return manager

    def test_same_dialog_conflict_is_flagged(self):
        manager = self._manager_with_two_dialogs()
        conflicts = manager.set_accel("glade.editpersonref.select", "<Primary>s")
        self.assertEqual(conflicts, ["glade.editpersonref.add_del"])

    def test_cross_dialog_same_key_is_not_flagged(self):
        manager = self._manager_with_two_dialogs()
        conflicts = manager.set_accel("glade.editevent.select_place", "<Primary>s")
        self.assertEqual(conflicts, [])

    def test_non_glade_actions_still_use_global_conflict_scope(self):
        manager = self._manager_with_two_dialogs()
        # "win.Clipboard" defaults to "<Primary>b" in make_manager(); a
        # glade-scoped accel must not be able to silently collide with it
        # since win.* actions are unaffected by the glade-only scoping.
        conflicts = manager.set_accel("win.Undo", "<Primary>b")
        self.assertEqual(conflicts, ["win.Clipboard"])


class StaticAppActionConflictScopeTest(unittest.TestCase):
    """
    Static-only "app." entries such as "app.dialog-ok"/"app.dialog-cancel"
    have no live Gio.SimpleAction: ManagedWindow wires them into a
    per-dialog Gtk.AccelGroup that only fires while that dialog holds
    keyboard focus. A background view's "win." actions can never receive
    that same keypress while a dialog is focused, so they must not be
    reported as conflicting -- only other "app." actions (dispatched
    regardless of window focus) or a dialog's own "glade." shortcuts
    (live in that same focused window) can genuinely collide.
    """

    def _manager_with_static_dialog_action(self):
        manager = make_manager()
        manager.register_static_shortcuts(
            [("dialog-ok", "<Alt>o", "Accept Dialog (OK)")],
            "Dialogs",
            prefix="app",
        )
        manager.register_static_shortcuts(
            [("select", "<Primary>d", "Select")],
            "Note Editor",
            prefix="glade.editnote",
        )
        live_app_group = ActionGroup(
            "App", [("quit", None, "<Primary>q")], prefix="app"
        )
        manager.insert_action_group(live_app_group, MagicMock())
        return manager

    def test_no_conflict_with_win_action(self):
        manager = self._manager_with_static_dialog_action()
        # "win.Clipboard" defaults to "<Primary>b" in make_manager(); a
        # dialog can never be open and focused at the same moment as the
        # main window's own view actions are live, so this must not flag.
        conflicts = manager.set_accel("app.dialog-ok", "<Primary>b")
        self.assertEqual(conflicts, [])

    def test_conflict_with_live_app_action(self):
        manager = self._manager_with_static_dialog_action()
        conflicts = manager.set_accel("app.dialog-ok", "<Primary>q")
        self.assertEqual(conflicts, ["app.quit"])

    def test_conflict_with_glade_action(self):
        manager = self._manager_with_static_dialog_action()
        conflicts = manager.set_accel("app.dialog-ok", "<Primary>d")
        self.assertEqual(conflicts, ["glade.editnote.select"])


if __name__ == "__main__":
    unittest.main()
