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
Display a person's events, both personal and family
"""

from Simple import SimpleAccess, by_date, SimpleDoc
from gettext import gettext as _

# define the formatting string once as a constant. Since this is reused

__FMT = "%-15s\t%-15s\t%s"

def run(database, document, person):
    """
    Loops through the person events and the family events of any family
    in which the person is a parent (to catch Marriage events), displaying 
    the basic details of the event
    """
    
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)

    # get the personal events
    event_list = sdb.events(person)

    # get the events of each family in which the person is 
    # a parent
    for family in sdb.parent_in(person):
        event_list += sdb.events(family)

    # Sort the events by their date
    event_list.sort(by_date)

    # display the results

    sdoc.title(_("Sorted events of %s") % sdb.name(person))
    sdoc.paragraph("")

    sdoc.header1(__FMT % (_("Event Type"), _("Event Date"), _("Event Place")))

    for event in event_list:
        sdoc.paragraph(__FMT % (sdb.event_type(event), 
                                sdb.event_date(event), 
                                sdb.event_place(event)))
