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
from PluginUtils import register_quick_report
from ReportBase import CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY

# define the formatting string once as a constant. Since this is reused

__FMT     = "%-15s\t%-15s\t%s"
__FMT_fam = "%-15s\t%-15s\t%-15s\t%s"

    
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

def run_fam(database, document, family):
    """
    Loops through the family events and the events of all parents, displaying 
    the basic details of the event
    """
    
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    
    # get the family events
    event_list = [(_('Family'), x) for x in sdb.events(family)]
    
    # get the events of father and mother
    fathername = sdb.first_name(sdb.father(family))
    event_list += [(fathername, x) for x in sdb.events(sdb.father(family))]
    mothername = sdb.first_name(sdb.mother(family))
    event_list += [(mothername, x) for x in sdb.events(sdb.mother(family))]
    
    # children events
    event_list_children = []
    for child in sdb.children(family) :
        name = sdb.first_name(child)
        event_list_children += [(name, x) for x in sdb.events(child)]
        
    # Sort the events by their date
    event_list.sort(fam_sort)
    event_list_children.sort(fam_sort)
    
    # display the results

    sdoc.title(_("Sorted events of family\n %s - %s") % 
                            (sdb.name(sdb.father(family)), 
                            sdb.name(sdb.mother(family))))
    sdoc.paragraph("")

    sdoc.header2(__FMT_fam % (_("Family Member"), _("Event Type"), 
                                _("Event Date"), _("Event Place")))

    for (name, event) in event_list:
        sdoc.paragraph(__FMT_fam % (name, sdb.event_type(event), 
                                sdb.event_date(event), 
                                sdb.event_place(event)))
    sdoc.paragraph("")
    sdoc.header1(_("Personal events of the children"))
    sdoc.header2(__FMT_fam % (_("Family Member"), _("Event Type"), 
                                _("Event Date"), _("Event Place")))
    for (name, event) in event_list_children:
        sdoc.paragraph(__FMT_fam % (name, sdb.event_type(event), 
                                sdb.event_date(event), 
                                sdb.event_place(event)))
                                
def fam_sort(event1, event2):
    """
    Sort function that will compare two events by their dates.

    @param event1: first event
    @type event1: L{Event}
    @param event2: second event
    @type event2: L{Event}
    @return: Returns -1 if event1 < event2, 0 if they are equal, and
       1 if they are the same.
    @rtype: int
    """
    return by_date(event1[1],event2[1])
                                
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_quick_report(
    name = 'all_events',
    category = CATEGORY_QR_PERSON,
    run_func = run,
    translated_name = _("All Events"),
    status = _("Stable"),
    description= _("Display a person's events, both personal and family."),
    author_name="Donald N. Allingham",
    author_email="don@gramps-project.org"
    )
    
register_quick_report(
    name = 'all_events_fam',
    category = CATEGORY_QR_FAMILY,
    run_func = run_fam,
    translated_name = _("All Events"),
    status = _("Stable"),
    description= _("Display the family and family members events."),
    author_name="B. Malengier",
    author_email="benny.malengier@gramps-project.org"
    )
