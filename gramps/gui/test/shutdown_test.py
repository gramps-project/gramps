#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Dmitry Marin
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

"""Session shutdown tests without requiring a GTK display.

Application methods are loaded via AST, as in viewmanager_fs_test.py.
The native message delivery test additionally runs on Windows.
"""

# These tests deliberately exercise internal callbacks without importing GTK.
# pylint: disable=protected-access,invalid-name,exec-used

# ------------------------
# Python modules
# ------------------------
import ast
from enum import Enum, auto
import ctypes
from pathlib import Path
import logging
import sys
import unittest
from typing import cast
from unittest.mock import Mock

# ------------------------
# Gramps modules
# ------------------------
from gramps.gui.windowsshutdown import (
    WindowsShutdown,
    WM_QUERYENDSESSION,
    WM_ENDSESSION,
)


def load_application() -> type:
    """Load shutdown methods with a stand-in GTK base for headless testing."""
    path = Path(__file__).parents[1] / "grampsgui.py"
    tree = ast.parse(path.read_text())
    original = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "GrampsApplication"
    )
    names = {
        "cb_query_end_session",
        "cb_end_session",
        "cb_session_quit",
        "cb_on_sigterm",
        "cb_finish_sigterm",
        "do_shutdown",
    }
    klass = ast.parse("class Application: pass").body[0]
    assert isinstance(klass, ast.ClassDef)
    klass.body = [
        n for n in original.body if isinstance(n, ast.FunctionDef) and n.name in names
    ]
    state = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "ShutdownState"
    )
    namespace = {
        "LOG": logging.getLogger(__name__),
        "GLib": Mock(),
        "Gtk": Mock(),
        "Enum": Enum,
        "auto": auto,
    }
    exec(
        compile(
            ast.fix_missing_locations(ast.Module(body=[state, klass], type_ignores=[])),
            str(path),
            "exec",
        ),
        namespace,
    )
    return cast(type, namespace["Application"])


# ------------------------------------------------------------
# SessionShutdownTest
# ------------------------------------------------------------
class SessionShutdownTest(unittest.TestCase):
    """Check confirmed/cancelled shutdowns, busy work and duplicate messages."""

    def setUp(self) -> None:
        """Provide an idle application and an unregistered native receiver."""
        self.app = load_application()()
        self.state = self.app.cb_on_sigterm.__globals__["ShutdownState"]
        self.app._shutdown_state = self.state.RUNNING
        self.app._gramps = Mock()
        self.app._gramps._vm.uistate.busy = False
        self.app.quit = Mock()
        self.receiver = WindowsShutdown.__new__(WindowsShutdown)
        self.receiver._can_close = self.app.cb_query_end_session
        self.receiver._end_session = self.app.cb_end_session
        self.receiver._ended = False
        self.receiver._user32 = Mock()

    def test_query_does_not_close_database(self) -> None:
        """Approval must not close a tree if shutdown is subsequently cancelled."""
        self.assertEqual(
            self.receiver.cb_window_message(1, WM_QUERYENDSESSION, 0, 0), 1
        )
        self.receiver.cb_window_message(1, WM_ENDSESSION, 0, 0)
        self.app._gramps._vm.quit.assert_not_called()
        self.assertFalse(self.receiver._ended)

    def test_confirmed_shutdown_closes_synchronously_once(self) -> None:
        """Close before returning to Windows, omitting the optional backup."""
        for _ in range(2):
            self.receiver.cb_window_message(1, WM_ENDSESSION, 1, 0)
        self.app._gramps._vm.quit.assert_called_once_with(make_backup=False)
        self.assertFalse(self.app.cb_finish_sigterm())

    def test_busy_operation_refuses_shutdown(self) -> None:
        """A nested GTK loop must not close a database during an operation."""
        self.app._gramps._vm.uistate.busy = True
        self.assertEqual(
            self.receiver.cb_window_message(1, WM_QUERYENDSESSION, 0, 0), 0
        )
        self.assertTrue(self.app.cb_finish_sigterm())
        self.app._gramps._vm.quit.assert_not_called()

    def test_busy_after_query_does_not_close_database(self) -> None:
        """Forced termination must not reenter a newly started operation."""
        self.app._gramps._vm.uistate.busy = True
        with self.assertLogs(__name__, level="WARNING"):
            self.app.cb_end_session()
        self.app._gramps._vm.quit.assert_not_called()

    def test_shutdown_before_activation(self) -> None:
        """There is no database to close before the GUI has been constructed."""
        self.app._gramps = None
        self.assertTrue(self.app.cb_query_end_session())
        self.app.cb_end_session()
        self.app.cb_end_session()
        self.assertIs(self.app._shutdown_state, self.state.CLOSING)
        self.assertFalse(self.app.cb_query_end_session())
        self.app.quit.assert_called_once()

    def test_macos_quit_waits_for_operation_then_closes_once(self) -> None:
        """Native macOS Quit uses the same safe deferred path as SIGTERM."""
        self.app._gramps._vm.uistate.busy = True
        self.app.cb_session_quit(None, None)
        self.app.cb_session_quit(None, None)
        self.assertIs(self.app._shutdown_state, self.state.PENDING)
        self.assertTrue(self.app.cb_finish_sigterm())
        self.app._gramps._vm.uistate.busy = False
        self.assertFalse(self.app.cb_finish_sigterm())
        self.assertFalse(self.app.cb_finish_sigterm())
        self.app._gramps._vm.quit.assert_called_once_with()

    def test_callback_exception_is_contained(self) -> None:
        """An exception cannot propagate across the native callback boundary."""
        self.receiver._can_close = Mock(side_effect=RuntimeError("failure"))
        with self.assertLogs("gramps.gui.windowsshutdown", level="ERROR"):
            self.assertEqual(
                self.receiver.cb_window_message(1, WM_QUERYENDSESSION, 0, 0), 0
            )

    def test_unrelated_message_uses_default_procedure(self) -> None:
        """Other native messages keep their normal window behavior."""
        cast(Mock, self.receiver._user32).DefWindowProcW.return_value = 7
        self.assertEqual(self.receiver.cb_window_message(1, 123, 2, 3), 7)
        cast(Mock, self.receiver._user32).DefWindowProcW.assert_called_once_with(
            1, 123, 2, 3
        )

    def test_close_releases_native_resources_once(self) -> None:
        """Repeated application shutdown cannot destroy the window twice."""
        self.receiver._hwnd = 123
        self.receiver._class_name = "test"
        self.receiver._instance = 456
        self.receiver.close()
        self.receiver.close()
        cast(Mock, self.receiver._user32).DestroyWindow.assert_called_once_with(123)
        cast(Mock, self.receiver._user32).UnregisterClassW.assert_called_once_with(
            "test", 456
        )

    def test_pending_requests_schedule_one_timer(self) -> None:
        """Repeated requests keep one pending timer until work completes."""
        self.app._gramps._vm.uistate.busy = True
        self.app.cb_on_sigterm()
        self.app.cb_on_sigterm()
        glib = self.app.cb_on_sigterm.__globals__["GLib"]
        glib.timeout_add.assert_called_once_with(100, self.app.cb_finish_sigterm)
        self.assertIs(self.app._shutdown_state, self.state.PENDING)
        self.assertTrue(self.app.cb_finish_sigterm())
        self.assertIs(self.app._shutdown_state, self.state.PENDING)
        self.app._gramps._vm.uistate.busy = False
        self.assertFalse(self.app.cb_finish_sigterm())
        self.assertIs(self.app._shutdown_state, self.state.CLOSING)

    def test_closing_ignores_new_requests(self) -> None:
        """Once cleanup starts, new requests cannot schedule another timer."""
        self.app.cb_end_session()
        self.assertIs(self.app._shutdown_state, self.state.CLOSING)
        self.app.cb_on_sigterm()
        self.app.cb_on_sigterm.__globals__["GLib"].timeout_add.assert_not_called()
        self.assertFalse(self.app.cb_finish_sigterm())
        self.assertFalse(self.app.cb_query_end_session())
        self.app._gramps._vm.quit.assert_called_once_with(make_backup=False)

    def test_exit_backup_is_optional_but_database_close_is_required(self) -> None:
        """Windows skips backup; ordinary Quit retains it and both close the DB."""
        path = Path(__file__).parents[1] / "viewmanager.py"
        tree = ast.parse(path.read_text())
        klass = next(
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "ViewManager"
        )
        klass.bases = []
        klass.body = [
            n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == "quit"
        ]
        config = Mock()
        config.get.return_value = True
        namespace = {"config": config}
        exec(
            compile(
                ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])),
                str(path),
                "exec",
            ),
            namespace,
        )
        manager_class = cast(type, namespace["ViewManager"])
        for make_backup in (False, True):
            with self.subTest(make_backup=make_backup):
                manager = manager_class()
                manager.uistate = Mock()
                manager.window = Mock()
                manager.window.get_size.return_value = (800, 600)
                manager.window.get_position.return_value = (0, 0)
                manager.del_event = 1
                manager.no_del_event = Mock()
                manager.autobackup = Mock()
                manager.dbstate = Mock()
                manager.user = Mock()
                manager.app = Mock()
                manager._ViewManager__delete_pages = Mock()
                manager.quit(make_backup=make_backup)
                self.assertEqual(manager.autobackup.call_count, int(make_backup))
                manager.dbstate.db.close.assert_called_once_with(user=manager.user)
                manager.app.quit.assert_called_once_with()

    @unittest.skipUnless(sys.platform == "win32", "requires Windows native APIs")
    def test_native_window_messages(self) -> None:
        """Exercise real pointer-sized ctypes declarations without logging out."""
        end = Mock()
        receiver = WindowsShutdown(lambda: True, end)
        user32 = getattr(ctypes, "WinDLL")("user32", use_last_error=True)
        user32.SendMessageW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_size_t,
            ctypes.c_ssize_t,
        ]
        user32.SendMessageW.restype = ctypes.c_ssize_t
        try:
            self.assertEqual(
                user32.SendMessageW(receiver._hwnd, WM_QUERYENDSESSION, 0, 0), 1
            )
            user32.SendMessageW(receiver._hwnd, WM_ENDSESSION, 0, 0)
            end.assert_not_called()
            user32.SendMessageW(receiver._hwnd, WM_ENDSESSION, 1, 0)
            end.assert_called_once_with()
        finally:
            receiver.close()
