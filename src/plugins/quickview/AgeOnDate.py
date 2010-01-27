#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2009       Douglas S. Blank
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
#
# $Id$
#
#
"""
Display references for any object
"""

from Simple import SimpleAccess, SimpleDoc, SimpleTable
from Utils import probably_alive
from gen.ggettext import gettext as _
import DateHandler
import gen.lib
import config

def run(database, document, date):
    """
    Display people probably alive and their ages on a particular date.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = SimpleTable(sdb)
    if not date.get_valid():
        sdoc.paragraph("Date is not a valid date.")
        return
    # display the title
    if date.get_day_valid():
        sdoc.title(_("People probably alive and their ages the %s") % 
               DateHandler.displayer.display(date))
    else:
        sdoc.title(_("People probably alive and their ages on %s") % 
               DateHandler.displayer.display(date))
    stab.columns(_("Person"), _("Age")) # Actual Date makes column unicode
    matches = 0
    for person in sdb.all_people():
        alive, birth, death, explain, relative = \
            probably_alive(person, database, date, return_range=True)
        # Doesn't show people probably alive but no way of figuring an age:
        if alive and birth:
            diff_span = (date - birth)
            stab.row(person, str(diff_span))
            stab.row_sort_val(1, int(diff_span))
            matches += 1

    sdoc.paragraph(_("\n%d matches.\n") % matches)
    stab.write(sdoc)
    sdoc.paragraph("")

def get_event_date_from_ref(database, ref):
    date = None
    if ref:
        handle = ref.get_reference_handle()
        if handle:
            event = database.get_event_from_handle(handle)
            if event:
                date = event.get_date_object()
    return date
