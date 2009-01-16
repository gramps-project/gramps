#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
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

"""
Display all events on a particular day.
"""

from Simple import SimpleAccess, SimpleDoc, SimpleTable
from gettext import gettext as _
from gen.plug import PluginManager
from ReportBase import CATEGORY_QR_EVENT
import gen.lib

def get_ref(db, objclass, handle):
    """
    Looks up object in database
    """
    if objclass == 'Person':
        ref = db.get_person_from_handle(handle)
    elif objclass == 'Family':
        ref = db.get_family_from_handle(handle)
    elif objclass == 'Event':
        ref = db.get_event_from_handle(handle)
    elif objclass == 'Source':
        ref = db.get_source_from_handle(handle)
    elif objclass == 'Place':
        ref = db.get_place_from_handle(handle)
    elif objclass == 'Repository':
        ref = db.get_repository_from_handle(handle)
    else:
        ref = objclass
    return ref

def run(database, document, main_event):
    """
    Displays events on a specific date of an event (or date)
    
    Takes an Event or Date object
    """
    if isinstance(main_event, gen.lib.Date):
        main_date = main_event
    else:
        main_date = main_event.get_date_object()

    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = SimpleTable(sdb)
    stab.set_link_col(3)
    yeartab = SimpleTable(sdb)
    yeartab.set_link_col(3)
    histab = SimpleTable(sdb)
    histab.set_link_col(3)

    # display the title
    sdoc.title(_("Events of %(date)s") % 
               {"date": sdb.date_string(main_date)})
    sdoc.paragraph("")
    stab.columns(_("Date"), _("Type"), _("Place"), _("Reference"))
    yeartab.columns(_("Date"), _("Type"), _("Place"), _("Reference"))
    histab.columns(_("Date"), _("Type"), _("Place"), _("Reference"))
    
    for event_handle in database.get_event_handles():
        event = database.get_event_from_handle(event_handle)
        date = event.get_date_object()
        if date.get_year() == 0:
            continue
        if (date.get_year() == main_date.get_year() and 
            date.get_month() == main_date.get_month() and
            date.get_day() == main_date.get_day()):
            for (objclass, handle) in database.find_backlink_handles(event_handle):
                ref = get_ref(database, objclass, handle)
                stab.row(date, 
                         sdb.event_type(event), 
                         sdb.event_place(event), ref)
        elif (date.get_month() == main_date.get_month() and
              date.get_day() == main_date.get_day() and
              date.get_month() != 0):
            for (objclass, handle) in database.find_backlink_handles(event_handle):
                ref = get_ref(database, objclass, handle)
                histab.row(date, 
                           sdb.event_type(event), 
                           sdb.event_place(event), ref)
        elif (date.get_year() == main_date.get_year()):
            for (objclass, handle) in database.find_backlink_handles(event_handle):
                ref = get_ref(database, objclass, handle)
                yeartab.row(date, 
                            sdb.event_type(event), 
                            sdb.event_place(event), ref)

    if stab.get_row_count() > 0:
        sdoc.paragraph(_("Events on this exact date"))
        stab.write(sdoc)
    else:
        sdoc.paragraph(_("No events on this exact date"))
        sdoc.paragraph("")
    sdoc.paragraph("")

    if histab.get_row_count() > 0:
        sdoc.paragraph(_("Other events on this month/day in history"))
        histab.write(sdoc)
    else:
        sdoc.paragraph(_("No other events on this month/day in history"))
        sdoc.paragraph("")
    sdoc.paragraph("")

    if yeartab.get_row_count() > 0:
        sdoc.paragraph(_("Other events in %(year)d") % 
                       {"year":main_date.get_year()})
        yeartab.write(sdoc)
    else:
        sdoc.paragraph(_("No other events in %(year)d") % 
                       {"year":main_date.get_year()})
        sdoc.paragraph("")
    sdoc.paragraph("")
                    
#------------------------------------------------------------------------
#
# Register the report
#
#------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_quick_report(
    name = 'onthisday',
    category = CATEGORY_QR_EVENT,
    run_func = run,
    translated_name = _("On This Day"),
    status = _("Stable"),
    description= _("Display events on a particular day"),
    author_name="Douglas Blank",
    author_email="dblank@cs.brynmawr.edu"
    )
