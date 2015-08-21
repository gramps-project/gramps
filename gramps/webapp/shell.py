# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012      Douglas S. Blank <doug.blank@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#### This sets up Django so you can interact with it via the Python
#### command line.
#### Start with something like:
####    $ PYTHONPATH=..:../plugins/lib python -i shell.py
####    >>> Person.objects.all()

import os
os.environ['GRAMPS_RESOURCES'] = os.path.dirname(os.path.abspath(".."))
pystartup = os.path.expanduser("~/.pystartup")
if not os.path.exists(pystartup):
    fp = file(pystartup, "w")
    fp.write("""
import atexit
import os
import readline
import rlcompleter
import sys

# change autocomplete to tab
readline.parse_and_bind("tab: complete")

historyPath = os.path.expanduser("~/.pyhistory")

def save_history(historyPath=historyPath):
    import readline
    readline.write_history_file(historyPath)

if os.path.exists(historyPath):
    readline.read_history_file(historyPath)

atexit.register(save_history)

# anything not deleted (sys and os) will remain in the interpreter session
del atexit, readline, rlcompleter, save_history, historyPath""")
    fp.close()

with open(pystartup) as f:
    code = compile(f.read(), pystartup, 'exec')
    exec(code, globals(), locals())

from django.conf import settings
from gramps.webapp import default_settings
try:
    settings.configure(default_settings)
except RuntimeError:
    # already configured; ignore
    pass

# For Django 1.6:
import django
django.setup()

from gramps.webapp.grampsdb.models import *
from gramps.webapp.grampsdb.forms import *
from gramps.webapp.djangodb import DbDjango
from gramps.webapp.reports import import_file, export_file
from gramps.webapp.libdjango import DjangoInterface, totime, todate
from gramps.gen.datehandler import displayer, parser
from gramps.webapp.utils import StyledNoteFormatter, parse_styled_text
from gramps.gen.lib import StyledText
from gramps.cli.user import User as GUser # gramps user

from django.db.models import Q

db = DbDjango()

db.load(os.path.abspath(os.path.dirname(__file__)))
dd = displayer.display
dp = parser.parse

#import_file(db,
#            "/home/dblank/gramps/trunk/example/gramps/data.gramps",
#            GUser())

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
