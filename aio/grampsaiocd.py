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
    environ["LANG"] = "en"
    environ["PANGOCAIRO_BACKEND"] = "fontconfig"
    environ["SSL_CERT_FILE"] = join(aio, "ssl/certs/ca-bundle.trust.crt")
    environ["GI_TYPELIB_PATH"] = join(aio, "lib/girepository-1.0")
    environ["G_ENABLE_DIAGNOSTIC"] = "0"
    environ["G_PARAM_DEPRECATED"] = "0"
    environ["GRAMPS_RESOURCES"] = join(aio, "share")
    environ["PATH"] = aio + ";" + aio + "\\lib;" + environ["PATH"]

import gramps.grampsapp as app

app.run()
