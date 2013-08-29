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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#

#### This sets up Django so you can interact with it via the Python
#### command line.
#### Start with something like:
####    $ PYTHONPATH=..:../plugins/lib python -i shell.py 
####    >>> Person.objects.all()

import os
os.environ['GRAMPS_RESOURCES'] = os.path.dirname(os.path.abspath(".."))
pystartup = os.path.expanduser("~/.pystartup")
if os.path.exists(pystartup):
    execfile(pystartup)
from django.conf import settings
import gramps.webapp.settings as default_settings
try:
    settings.configure(default_settings)
except RuntimeError:
    # already configured; ignore
    pass

from gramps.webapp.grampsdb.models import *
from gramps.webapp.grampsdb.forms import *
from gramps.webapp.dbdjango import DbDjango
from gramps.webapp.reports import import_file
from gramps.webapp.libdjango import DjangoInterface, totime, todate
from gramps.gen.datehandler import displayer, parser
from gramps.webapp.utils import StyledNoteFormatter, parse_styled_text
from gramps.gen.lib import StyledText
#from gramps.cli.user import User

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
