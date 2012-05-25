from django.conf import settings
import webapp.settings as default_settings
try:
    settings.configure(default_settings)
except RuntimeError:
    # already configured; ignore
    pass

from webapp.grampsdb.models import *
from webapp.grampsdb.forms import *
from webapp.dbdjango import DbDjango
from webapp.reports import import_file
from webapp.libdjango import DjangoInterface, totime, todate

import DateHandler

db = DbDjango()
dji = DjangoInterface()
dd = DateHandler.displayer.display
dp = DateHandler.parser.parse

#def Print(m):
#    print m
#import_file(db, "/tmp/dblank-im_ged.ged", Print)
