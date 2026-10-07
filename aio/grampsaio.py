#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
"""Shared startup support for the Windows AIO executables."""

# -------------------------------------------------------------------------
# Python modules
# -------------------------------------------------------------------------
import atexit
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import site
import sys


def configure_environment() -> None:
    """Locate resources and certificates shipped in a frozen AIO build."""
    if not getattr(sys, "frozen", False):
        return
    directory = Path(sys.executable).parent
    sys.path[1:1] = [
        site.getusersitepackages(),
        str(directory / "lib"),
        str(directory),
    ]
    os.environ["SSL_CERT_FILE"] = str(directory / "etc" / "ssl" / "cert.pem")
    os.environ["GI_TYPELIB_PATH"] = str(directory / "lib" / "girepository-1.0")
    os.environ["G_ENABLE_DIAGNOSTIC"] = "0"
    os.environ["G_PARAM_DEPRECATED"] = "0"
    os.environ["GRAMPS_RESOURCES"] = str(directory / "share")
    os.environ["PATH"] = os.pathsep.join(
        [str(directory), str(directory / "lib"), os.environ.get("PATH", os.defpath)]
    )


def acquire_instance_lock(name: str = "org.gramps-project.gramps") -> bool:
    """Keep a Windows mutex open until exit, using pointer-sized handles.

    :param name: Name shared by the GUI, console and uninstaller.
    :returns: False when another instance already holds the named mutex.
    :raises OSError: If Windows cannot create the mutex.
    """
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    ctypes.set_last_error(0)
    # Presence, rather than ownership, guards against another process. Keeping
    # the handle open also lets the installer detect a running Gramps instance.
    handle = kernel32.CreateMutexW(None, False, name)
    error = ctypes.get_last_error()
    if not handle:
        raise ctypes.WinError(error)
    if error == 183:  # ERROR_ALREADY_EXISTS
        kernel32.CloseHandle(handle)
        return False
    atexit.register(kernel32.CloseHandle, handle)
    return True
