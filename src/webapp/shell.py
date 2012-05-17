from django.conf import settings
import webapp.settings as default_settings
try:
    settings.configure(default_settings)
except RuntimeError:
    # already configured; ignore
    pass

from webapp.grampsdb.models import *
from webapp.dbdjango import DbDjango
from webapp.reports import import_file

db = DbDjango()

def Print(m):
    print m

import_file(db, "/tmp/dblank-im_ged.ged", Print)
