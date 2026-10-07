#!/usr/bin/env python3
from os import environ
import sys
from grampsaio import acquire_instance_lock, configure_environment

configure_environment()
if getattr(sys, "frozen", False):
    environ["PANGOCAIRO_BACKEND"] = "fontconfig"

if not acquire_instance_lock():
    print("Gramps is already running!", file=sys.stderr)
    sys.exit()

import warnings

warnings.simplefilter("ignore")

import gramps.grampsapp as app

app.run()
