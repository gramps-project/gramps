#### This sets up Django so you can interact with it via the Python
#### command line.
#### Start with something like:
####    $ PYTHONPATH=..:../plugins/lib python -i shell.py 
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

from webapp.utils import StyledNoteFormatter
snf = StyledNoteFormatter(db)
for n in Note.objects.all():
    note = db.get_note_from_handle(n.handle)
    print snf.get_note_format(note)

#note = Note.objects.get(handle="aef30789d3d2090abe2")
#st = gen.lib.StyledText(note.text, dji.get_note_markup(note))
