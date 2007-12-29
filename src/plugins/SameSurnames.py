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
Display a people who have a person's same surname
"""

from Simple import SimpleAccess, SimpleDoc, SimpleTable
from gen.lib import Person
from gettext import gettext as _
from PluginUtils import register_quick_report, relationship_class
from ReportBase import CATEGORY_QR_PERSON
from Filters.Rules.Person import SearchName
from Filters import GenericFilterFactory, Rules

def run(database, document, person):
    """
    Loops through the families that the person is a child in, and display
    the information about the other children.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = SimpleTable(sdb, sdoc)
    rel_class = relationship_class()
    # display the title
    sdoc.title(_("People with same surname as %s") % sdb.name(person))
    sdoc.paragraph("")
    stab.columns(_("Person"), _("Birth Date"), _("Name type"))
    # grab our current id (self):
    gid = sdb.gid(person)
    filter = GenericFilterFactory('Person')()
    rule = SearchName([person.get_primary_name().get_surname()])
    filter.add_rule(rule)
    people = filter.apply(database, 
                          database.get_person_handles(sort_handles=False))
    matches = 0
    for person_handle in people:
        person = database.get_person_from_handle(person_handle)
        stab.row(person, sdb.birth_date(person), str(person.get_primary_name().get_type()))
        matches += 1
    sdoc.paragraph(_("There are %d people with a matching name, or alternate name.\n") % matches)
    stab.write()
                    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_quick_report(
    name = 'surnames',
    category = CATEGORY_QR_PERSON,
    run_func = run,
    translated_name = _("Same Surnames"),
    status = _("Stable"),
    description= _("Display people with the same surname as a person."),
    author_name="Douglas S. Blank",
    author_email="dblank@cs.brynmawr.edu"
    )
