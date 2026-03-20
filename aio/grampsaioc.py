#!/usr/bin/env python3
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
    environ["PANGOCAIRO_BACKEND"] = "fontconfig"
    environ["SSL_CERT_FILE"] = join(aio, "ssl/certs/ca-bundle.trust.crt")
    environ["GI_TYPELIB_PATH"] = join(aio, "lib/girepository-1.0")
    environ["G_ENABLE_DIAGNOSTIC"] = "0"
    environ["G_PARAM_DEPRECATED"] = "0"
    environ["GRAMPS_RESOURCES"] = join(aio, "share")
    environ["PATH"] = aio + ";" + aio + "\\lib;" + environ["PATH"]


def close():
    sys.exit()


import atexit
import ctypes

HANDLE = ctypes.windll.kernel32.CreateMutexW(None, 1, "org.gramps-project.gramps")
ERROR = ctypes.GetLastError()
if ERROR == 183:  # ERROR_ALREADY_EXISTS:
    print("Gramps is already running!", file=sys.stderr)
    close()

atexit.register(ctypes.windll.kernel32.CloseHandle, HANDLE)
atexit.register(ctypes.windll.kernel32.ReleaseMutex, HANDLE)

import warnings

warnings.simplefilter("ignore")

import gramps.grampsapp as app

app.run()
