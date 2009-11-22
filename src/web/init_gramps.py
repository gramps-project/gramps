"""
Clears gramps data
"""

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
import settings

import grampsdb.models as dj

dj.clear_tables("primary", "secondary", "ref")
