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
from gettext import gettext as _
from gen.plug import PluginManager
from ReportBase import CATEGORY_QR_DATE
import DateHandler
import gen.lib
import Config

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
        birth_date = None
        birth_str = ""
        birth_sort = 0
        birth_ref = gen.lib.Person.get_birth_ref(person)
        birth_date = get_event_date_from_ref(database, birth_ref)
        death_ref = gen.lib.Person.get_death_ref(person)
        death_date = get_event_date_from_ref(database, death_ref)
        if birth_date:
            if (birth_date.get_valid() and birth_date < date and
                birth_date.get_year() != 0 and
                ((death_date is None) or (death_date > date))):
                diff_span = (date - birth_date)
                if ((death_date is not None) or
                    (death_date is None and 
                     int(diff_span) <= Config.get(Config.MAX_AGE_PROB_ALIVE) * 365)):
                    birth_str = str(diff_span)
                    birth_sort = int(diff_span)
        if birth_str != "":
            stab.row(person, birth_str)
            stab.row_sort_val(1, diff_span)
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


#------------------------------------------------------------------------
#
# Register the report
#
#------------------------------------------------------------------------

pmgr = PluginManager.get_instance()
pmgr.register_quick_report(
    name = 'ageondate',
    category = CATEGORY_QR_DATE,
    run_func = run,
    translated_name = _("Age on Date"),
    status = _("Stable"),
    description= _("Display people and ages on a particular date"),
    author_name="Douglas Blank",
    author_email="dblank@cs.brynmawr.edu"
    )
