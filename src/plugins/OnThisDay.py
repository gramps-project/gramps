#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Brian G. Matherly
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
from PluginUtils import register_quick_report
from ReportBase import CATEGORY_QR_EVENT

def run(database, document, main_event):
    """
    Loops through the families that the person is a child in, and display
    the information about the other children.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = SimpleTable(sdb, sdoc)
    yeartab = SimpleTable(sdb, sdoc)
    histab = SimpleTable(sdb, sdoc)

    main_date = main_event.get_date_object()

    # display the title
    sdoc.title(_("Events of %s") % sdb.event_date(main_event))
    sdoc.paragraph("")
    stab.columns(_("Date"), _("Type"), _("Place"))
    yeartab.columns(_("Date"), _("Type"), _("Place"))
    histab.columns(_("Date"), _("Type"), _("Place"))
    
    for event_handle in database.get_event_handles():
        event = database.get_event_from_handle(event_handle)
        date = event.get_date_object()
        if date.get_year() == 0:
            continue
        if (date.get_year() == main_date.get_year() and 
            date.get_month() == main_date.get_month() and
            date.get_day() == main_date.get_day()):
            stab.row(date, 
                     sdb.event_type(event), 
                     sdb.event_place(event))
        elif (date.get_month() == main_date.get_month() and
              date.get_day() == main_date.get_day()):
            histab.row(date, 
                        sdb.event_type(event), 
                        sdb.event_place(event))
        elif (date.get_year() == main_date.get_year()):
            yeartab.row(date, 
                        sdb.event_type(event), 
                        sdb.event_place(event))

    stab.write()

    sdoc.paragraph("")
    if histab.get_row_count() > 0:
        sdoc.paragraph("Other events on this day in history")
        histab.write()

    sdoc.paragraph("")
    if yeartab.get_row_count() > 0:
        sdoc.paragraph("Other events in %d" % main_date.get_year())
        yeartab.write()
                    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_quick_report(
    name = 'onthisday',
    category = CATEGORY_QR_EVENT,
    run_func = run,
    translated_name = _("On This Day"),
    status = _("Stable"),
    description= _("Display events on a particular day"),
    author_name="Douglas Blank",
    author_email="dblank@cs.brynmawr.edu"
    )
