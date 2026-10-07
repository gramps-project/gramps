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
"""Check AIO startup and packaging without launching the installed application."""

# -------------------------------------------------------------------------
# Python modules
# -------------------------------------------------------------------------
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import ssl
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import uuid

# -------------------------------------------------------------------------
# Gramps specific
# -------------------------------------------------------------------------
from aio import check_pip, grampsaio


# -------------------------------------------------------------------------
# StartupTest
# -------------------------------------------------------------------------
class StartupTest(unittest.TestCase):
    """Check resources, native mutex lifetime and failure reporting."""

    def test_source_environment_is_unchanged(self) -> None:
        """Unfrozen source runs retain their interpreter's environment."""
        original_path = sys.path[:]
        with (
            patch.object(sys, "frozen", False, create=True),
            patch.dict(os.environ, {"SSL_CERT_FILE": "custom.pem"}, clear=True),
        ):
            grampsaio.configure_environment()
            self.assertEqual(os.environ["SSL_CERT_FILE"], "custom.pem")
            self.assertEqual(sys.path, original_path)

    def test_frozen_resources_and_certificates(self) -> None:
        """A frozen launcher uses the certificate path packaged by setup.py."""
        with tempfile.TemporaryDirectory(prefix="gramps-aio-") as temporary:
            directory = Path(temporary)
            with (
                patch.object(sys, "frozen", True, create=True),
                patch.object(sys, "executable", str(directory / "grampsw.exe")),
                patch.object(sys, "path", sys.path[:]),
                patch.dict(os.environ, {}, clear=True),
            ):
                grampsaio.configure_environment()
                self.assertEqual(
                    os.environ["SSL_CERT_FILE"],
                    str(directory / "etc" / "ssl" / "cert.pem"),
                )
                self.assertEqual(
                    ssl.get_default_verify_paths().openssl_cafile_env, "SSL_CERT_FILE"
                )
                self.assertEqual(
                    os.environ["GRAMPS_RESOURCES"], str(directory / "share")
                )
                self.assertEqual(
                    os.environ["PATH"].split(os.pathsep)[:2],
                    [str(directory), str(directory / "lib")],
                )

    @unittest.skipUnless(sys.platform == "win32", "Windows mutex API")
    def test_real_mutex_lifetime(self) -> None:
        """A second instance is rejected until the original handle is closed."""
        name = "gramps-aio-test-" + uuid.uuid4().hex
        with patch.object(grampsaio.atexit, "register") as register:
            self.assertTrue(grampsaio.acquire_instance_lock(name))
            close, handle = register.call_args.args
            try:
                self.assertEqual(close.argtypes, [wintypes.HANDLE])
                self.assertFalse(grampsaio.acquire_instance_lock(name))
                self.assertEqual(register.call_count, 1)
            finally:
                self.assertTrue(close(handle))
            self.assertTrue(grampsaio.acquire_instance_lock(name))
            close, handle = register.call_args.args
            self.assertTrue(close(handle))

    @unittest.skipUnless(sys.platform == "win32", "Windows mutex API")
    def test_pointer_sized_handle_is_preserved(self) -> None:
        """Handles above 32 bits reach CloseHandle without truncation."""
        handle = 0x123456789ABC
        kernel = Mock()
        kernel.CreateMutexW.return_value = handle
        with (
            patch.object(ctypes, "WinDLL", return_value=kernel),
            patch.object(ctypes, "get_last_error", return_value=183),
        ):
            self.assertFalse(grampsaio.acquire_instance_lock())
        self.assertIs(kernel.CreateMutexW.restype, wintypes.HANDLE)
        kernel.CloseHandle.assert_called_once_with(handle)

    @unittest.skipUnless(sys.platform == "win32", "Windows mutex API")
    def test_mutex_creation_error_is_reported(self) -> None:
        """Failed mutex creation must not silently permit another instance."""
        kernel = Mock()
        kernel.CreateMutexW.return_value = None
        with (
            patch.object(ctypes, "WinDLL", return_value=kernel),
            patch.object(ctypes, "get_last_error", return_value=5),
            self.assertRaises(OSError),
        ):
            grampsaio.acquire_instance_lock()


# -------------------------------------------------------------------------
# FrozenPipTest
# -------------------------------------------------------------------------
class FrozenPipTest(unittest.TestCase):
    """Check packaging failures that the old shell smoke check ignored."""

    def test_success(self) -> None:
        """Both pip version and dependency-resolution commands are required."""
        result = subprocess.CompletedProcess([], 0, "OK", "")
        with patch.object(check_pip.subprocess, "run", return_value=result) as run:
            self.assertTrue(check_pip.check_pip("pip.exe"))
            self.assertEqual(run.call_count, 2)

    def test_nonzero_exit_without_traceback(self) -> None:
        """Ordinary pip errors must stop packaging too."""
        result = subprocess.CompletedProcess([], 1, "", "ERROR: resolution failed")
        with (
            patch.object(check_pip.subprocess, "run", return_value=result),
            self.assertLogs(check_pip.LOG, level="ERROR"),
        ):
            self.assertFalse(check_pip.check_pip("pip.exe"))

    def test_traceback_despite_zero_exit(self) -> None:
        """A frozen bootstrap may emit an exception without an exit failure."""
        result = subprocess.CompletedProcess([], 0, "", "ModuleNotFoundError: missing")
        with (
            patch.object(check_pip.subprocess, "run", return_value=result),
            self.assertLogs(check_pip.LOG, level="ERROR"),
        ):
            self.assertFalse(check_pip.check_pip("pip.exe"))

    def test_process_failure(self) -> None:
        """Missing executables and hung subprocesses fail the build check."""
        for error in (
            FileNotFoundError("missing pip"),
            subprocess.TimeoutExpired([], 120),
        ):
            with (
                self.subTest(error=type(error).__name__),
                patch.object(check_pip.subprocess, "run", side_effect=error),
                self.assertLogs(check_pip.LOG, level="ERROR"),
            ):
                self.assertFalse(check_pip.check_pip("pip.exe"))
