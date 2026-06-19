#!/usr/bin/env python3
"""
gramps.exe  —  console entry point.
"""

import os
from os import environ
from os.path import join
import sys

if getattr(sys, "frozen", False):
    _meipass = sys._MEIPASS

    _cert_path = join(_meipass, "etc", "ssl", "cert.pem")
    environ["SSL_CERT_FILE"] = _cert_path
    environ["REQUESTS_CA_BUNDLE"] = _cert_path
    environ["CURL_CA_BUNDLE"] = _cert_path
    import ssl as _ssl_module

    if os.path.exists(_cert_path):
        _orig_cdc = _ssl_module.create_default_context

        def _patched_cdc(purpose=_ssl_module.Purpose.SERVER_AUTH, *, cafile=None, **kw):
            if cafile is None:
                cafile = _cert_path
            return _orig_cdc(purpose, cafile=cafile, **kw)

        _ssl_module.create_default_context = _patched_cdc

    environ["PANGOCAIRO_BACKEND"] = "fontconfig"
    environ["G_ENABLE_DIAGNOSTIC"] = "0"
    environ["G_PARAM_DEPRECATED"] = "0"
    environ["GRAMPS_RESOURCES"] = join(_meipass, "share")


def close():
    sys.exit()


import atexit
import ctypes

HANDLE = ctypes.windll.kernel32.CreateMutexW(None, 1, "org.gramps-project.gramps")
ERROR = ctypes.GetLastError()
if ERROR == 183:  # ERROR_ALREADY_EXISTS
    print("Gramps is already running!", file=sys.stderr)
    close()

atexit.register(ctypes.windll.kernel32.CloseHandle, HANDLE)
atexit.register(ctypes.windll.kernel32.ReleaseMutex, HANDLE)

import warnings

warnings.simplefilter("ignore")

import gramps.grampsapp as app

app.run()
