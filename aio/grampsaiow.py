#!/usr/bin/env python3
"""
grampsw.exe  —  GUI entry point (no console window).
"""

import os
from os import environ
from os.path import join
import sys

if getattr(sys, "frozen", False):
    # sys._MEIPASS is the PyInstaller bundle directory.
    # With contents_directory='.' it equals os.path.dirname(sys.executable).
    _meipass = sys._MEIPASS

    # SSL certificates.
    # Python 3.13 no longer reads SSL_CERT_FILE inside create_default_context(),
    # so we patch it directly in addition to setting the environment variable
    # for older Python versions and third-party libraries.
    _cert_path = join(_meipass, "etc", "ssl", "cert.pem")
    environ["SSL_CERT_FILE"] = _cert_path       # Python < 3.13
    environ["REQUESTS_CA_BUNDLE"] = _cert_path  # requests library
    environ["CURL_CA_BUNDLE"] = _cert_path      # curl-based libs
    import ssl as _ssl_module
    if os.path.exists(_cert_path):
        _orig_cdc = _ssl_module.create_default_context
        def _patched_cdc(purpose=_ssl_module.Purpose.SERVER_AUTH, *,
                         cafile=None, **kw):
            if cafile is None:
                cafile = _cert_path
            return _orig_cdc(purpose, cafile=cafile, **kw)
        _ssl_module.create_default_context = _patched_cdc

    # PyInstaller's gi runtime hook sets GI_TYPELIB_PATH automatically.
    environ["G_ENABLE_DIAGNOSTIC"] = "0"
    environ["G_PARAM_DEPRECATED"] = "0"
    environ["GRAMPS_RESOURCES"] = join(_meipass, "share")

import atexit
import ctypes


def close():
    """Show warning dialog if Gramps is already running."""
    sys.exit("Gramps is already running!")


HANDLE = ctypes.windll.kernel32.CreateMutexW(None, 1, "org.gramps-project.gramps")
ERROR = ctypes.GetLastError()
if ERROR == 183:  # ERROR_ALREADY_EXISTS
    close()

atexit.register(ctypes.windll.kernel32.CloseHandle, HANDLE)
atexit.register(ctypes.windll.kernel32.ReleaseMutex, HANDLE)

import gramps.grampsapp as app

app.main()
