#### This sets up Django so you can interact with it via the Python
#### command line.
#### Start with something like:
####    $ PYTHONPATH=.. python -i shell.py 
####    >>> Person.objects.all()

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
from gen.datehandler import displayer, parser
import gen.lib
import cli.user

db = DbDjango()
dji = DjangoInterface()
dd = displayer.display
dp = parser.parse

#import_file(db, 
#            "/home/dblank/gramps/trunk/example/gramps/data.gramps", 
#            cli.user.User())
