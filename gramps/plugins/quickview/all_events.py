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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#
#
"""
Display a person's events, both personal and family
"""

from gramps.gen.simple import SimpleAccess, SimpleDoc
from gramps.gui.plug.quick import QuickTable
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

def run(database, document, person):
    """
    Loops through the person events and the family events of any family
    in which the person is a parent (to catch Marriage events), displaying
    the basic details of the event
    """

    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = QuickTable(sdb)

    # get the personal events
    event_list = sdb.events(person)

    # get the events of each family in which the person is
    # a parent
    for family in sdb.parent_in(person):
        event_list += sdb.events(family)

    # Sort the events by their date
    event_list.sort(key=lambda x: x.get_date_object())

    # display the results

    # feature request 2356: avoid genitive form
    sdoc.title(_("Sorted events of %s") % sdb.name(person))
    sdoc.paragraph("")

    stab.columns(_("Event Type"), _("Event Date"), _("Event Place"))
    document.has_data = False
    for event in event_list:
        stab.row(event,
                 sdb.event_date_obj(event),
                 sdb.event_place(event))
        document.has_data = True
    if document.has_data:
        stab.write(sdoc)
    else:
        sdoc.header1(_("Not found"))

def run_fam(database, document, family):
    """
    Loops through the family events and the events of all parents, displaying
    the basic details of the event
    """

    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = QuickTable(sdb)

    # get the family events
    event_list = [(_('Family'), x) for x in sdb.events(family)]

    # get the events of father and mother
    #fathername = sdb.first_name(sdb.father(family))
    event_list += [(sdb.father(family), x) for x in sdb.events(sdb.father(family))]
    #mothername = sdb.first_name(sdb.mother(family))
    event_list += [(sdb.mother(family), x) for x in sdb.events(sdb.mother(family))]

    # children events
    event_list_children = []
    for child in sdb.children(family):
        #name = sdb.first_name(child)
        event_list_children += [(child, x) for x in sdb.events(child)]

    # Sort the events by their date
    event_list.sort(key=lambda x: x[1].get_date_object())
    event_list_children.sort(key=lambda x: x[1].get_date_object())

    # display the results

    sdoc.title(_("Sorted events of family\n %(father)s - %(mother)s") % {
        'father': sdb.name(sdb.father(family)),
        'mother': sdb.name(sdb.mother(family))})
    sdoc.paragraph("")

    document.has_data = False
    stab.columns(_("Family Member"), _("Event Type"),
                 _("Event Date"), _("Event Place"))

    for (person, event) in event_list:
        stab.row(person, sdb.event_type(event),
                 sdb.event_date_obj(event),
                 sdb.event_place(event))
        document.has_data = True
    if document.has_data:
        stab.write(sdoc)
    else:
        sdoc.header1(_("Not found") + "\n")

    stab = QuickTable(sdb)
    sdoc.header1(_("Personal events of the children"))
    stab.columns(_("Family Member"), _("Event Type"),
                 _("Event Date"), _("Event Place"))
    for (person, event) in event_list_children:
        stab.row(person, sdb.event_type(event),
                 sdb.event_date_obj(event),
                 sdb.event_place(event))
        document.has_data = True
    if document.has_data:
        stab.write(sdoc)
    else:
        sdoc.header1(_("Not found") + "\n")
