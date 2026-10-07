#!/usr/bin/env python3
"""
grampsw.exe
"""

import sys
from grampsaio import acquire_instance_lock, configure_environment

configure_environment()

if not acquire_instance_lock():
    sys.exit("Gramps is already running!")

import gramps.grampsapp as app

app.main()
