#!/usr/bin/env python3
from os import environ
import sys
from grampsaio import configure_environment

configure_environment()
if getattr(sys, "frozen", False):
    environ["LANG"] = "en"
    environ["PANGOCAIRO_BACKEND"] = "fontconfig"

import gramps.grampsapp as app

app.run()
