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
from gramps.gen.datehandler import displayer, parser
from webapp.utils import StyledNoteFormatter, parse_styled_text
from gramps.gen.lib import StyledText
from gramps.cli.user import User

db = DbDjango()
dji = DjangoInterface()
dd = displayer.display
dp = parser.parse

#import_file(db, 
#            "/home/dblank/gramps/trunk/example/gramps/data.gramps", 
#            User())

#snf = StyledNoteFormatter(db)
#for n in Note.objects.all():
#    note = db.get_note_from_handle(n.handle)
#    print snf.format(note)

#note = Note.objects.get(handle="aef30789d3d2090abe2")
#genlibnote = db.get_note_from_handle(note.handle)
#html_text = snf.format(genlibnote)
## FIXME: this looks wrong:
#print html_text
#print parse_styled_text(html_text)

##st = StyledText(note.text, dji.get_note_markup(note))
