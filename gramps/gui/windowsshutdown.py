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

"""Receive Windows session shutdown messages on the GTK main thread.

An invisible ordinary top-level window receives broadcast session messages.
A message-only window would not receive them. GTK's Windows message loop
also dispatches messages for this window, so no worker thread is needed.
"""

# ------------------------
# Python modules
# ------------------------
import ctypes
from ctypes import wintypes
import logging
from collections.abc import Callable

LOG = logging.getLogger(__name__)
WM_QUERYENDSESSION = 0x0011
WM_ENDSESSION = 0x0016


# ------------------------------------------------------------
# WindowsShutdown
# ------------------------------------------------------------
class WindowsShutdown:  # pylint: disable=too-many-instance-attributes
    """Own a native window that forwards session notifications to Gramps."""

    def __init__(
        self, can_close: Callable[[], bool], end_session: Callable[[], None]
    ) -> None:
        """Register a window on the calling GUI thread.

        :param can_close: Return false while closing the database is unsafe.
        :param end_session: Perform synchronous cleanup on confirmed shutdown.
        :raises OSError: If native window registration or creation fails.
        """
        self._can_close = can_close
        self._end_session = end_session
        self._ended = False
        self._hwnd = None
        self._user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        # LRESULT, WPARAM and LPARAM must be pointer-sized on both Win32/Win64.
        wndproc = ctypes.WINFUNCTYPE(
            ctypes.c_ssize_t,
            wintypes.HWND,
            wintypes.UINT,
            ctypes.c_size_t,
            ctypes.c_ssize_t,
        )

        class WNDCLASS(ctypes.Structure):  # pylint: disable=too-few-public-methods
            """Native WNDCLASSW layout, including pointer-sized handles."""

            _fields_ = [
                ("style", wintypes.UINT),
                ("lpfnWndProc", wndproc),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", wintypes.HINSTANCE),
                ("hIcon", wintypes.HANDLE),
                ("hCursor", wintypes.HANDLE),
                ("hbrBackground", wintypes.HANDLE),
                ("lpszMenuName", wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR),
            ]

        kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        kernel32.GetModuleHandleW.restype = wintypes.HMODULE
        self._instance = kernel32.GetModuleHandleW(None)
        self._class_name = f"GrampsShutdown_{id(self)}"
        self._user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASS)]
        self._user32.RegisterClassW.restype = wintypes.ATOM
        self._user32.UnregisterClassW.argtypes = [wintypes.LPCWSTR, wintypes.HINSTANCE]
        self._user32.UnregisterClassW.restype = wintypes.BOOL
        self._user32.CreateWindowExW.argtypes = [
            wintypes.DWORD,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.HWND,
            wintypes.HMENU,
            wintypes.HINSTANCE,
            wintypes.LPVOID,
        ]
        self._user32.CreateWindowExW.restype = wintypes.HWND
        self._user32.DestroyWindow.argtypes = [wintypes.HWND]
        self._user32.DestroyWindow.restype = wintypes.BOOL
        self._user32.DefWindowProcW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            ctypes.c_size_t,
            ctypes.c_ssize_t,
        ]
        self._user32.DefWindowProcW.restype = ctypes.c_ssize_t
        # Keep the callback alive until after DestroyWindow has returned.
        self._wndproc = wndproc(self.cb_window_message)
        window_class = WNDCLASS()
        # Native field names must match the Windows ABI.
        # pylint: disable=invalid-name
        window_class.lpfnWndProc = self._wndproc
        window_class.hInstance = self._instance
        window_class.lpszClassName = self._class_name
        if not self._user32.RegisterClassW(ctypes.byref(window_class)):
            raise ctypes.WinError(ctypes.get_last_error())
        self._hwnd = self._user32.CreateWindowExW(
            0,
            self._class_name,
            "Gramps",
            0,
            0,
            0,
            0,
            0,
            None,
            None,
            self._instance,
            None,
        )
        if not self._hwnd:
            error = ctypes.get_last_error()
            self._user32.UnregisterClassW(self._class_name, self._instance)
            raise ctypes.WinError(error)

    def cb_window_message(
        self, hwnd: int, message: int, wparam: int, lparam: int
    ) -> int:
        """Handle session messages, preserving default behavior for others.

        :returns: The native window procedure result.
        """
        try:
            if message == WM_QUERYENDSESSION:
                return int(self._can_close())
            if message == WM_ENDSESSION:
                # False means another application/user cancelled shutdown.
                if wparam and not self._ended:
                    self._ended = True
                    self._end_session()
                return 0
            return self._user32.DefWindowProcW(hwnd, message, wparam, lparam)
        except Exception:
            # Python exceptions must never escape a ctypes window callback.
            LOG.exception("Windows session shutdown handler failed")
            return 0

    def close(self) -> None:
        """Destroy the notification window and unregister its class once."""
        if self._hwnd:
            self._user32.DestroyWindow(self._hwnd)
            self._hwnd = None
            self._user32.UnregisterClassW(self._class_name, self._instance)
