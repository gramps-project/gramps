#!/usr/bin/env python3
"""
    grampsw.exe
"""
import os
from os import environ
from os.path import join
import sys
import site

if getattr(sys, "frozen", False):
    aio = os.path.dirname(sys.executable)
    sys.path.insert(1, aio)
    sys.path.insert(1, os.path.join(aio, "lib"))
    sys.path.insert(1, site.getusersitepackages())
    environ["SSL_CERT_FILE"] = join(aio, "ssl/certs/ca-bundle.trust.crt")
    environ["GI_TYPELIB_PATH"] = join(aio, "lib/girepository-1.0")
    environ["G_ENABLE_DIAGNOSTIC"] = "0"
    environ["G_PARAM_DEPRECATED"] = "0"
    environ["GRAMPS_RESOURCES"] = join(aio, "share")
    environ["PATH"] = aio + ";" + aio + "\\lib;" + environ["PATH"]

import atexit
import ctypes


def close():
    """Show warning dialog if Gramps is already running"""
    sys.exit("Gramps is already running!")


HANDLE = ctypes.windll.kernel32.CreateMutexW(None, 1, "org.gramps-project.gramps")
ERROR = ctypes.GetLastError()
if ERROR == 183:  # ERROR_ALREADY_EXISTS:
    close()

atexit.register(ctypes.windll.kernel32.CloseHandle, HANDLE)
atexit.register(ctypes.windll.kernel32.ReleaseMutex, HANDLE)

import gramps.grampsapp as app

app.main()
