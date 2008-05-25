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
Display a people who have a person's same surname
"""

from Simple import SimpleAccess, SimpleDoc, SimpleTable
from gettext import gettext as _
from PluginUtils import PluginManager
from ReportBase import CATEGORY_QR_PERSON
from Filters.Rules import Rule
from Filters import GenericFilterFactory

class IncompleteSurname(Rule):
    """People with incomplete surnames"""
    name        = _('People with incomplete surnames')
    description = _("Matches people with lastname missing")
    category    = _('General filters')
    def apply(self,db,person):
        for name in [person.get_primary_name()] + person.get_alternate_names():
            if name.get_group_name() == "":
                return True
        return False

class SameSurname(Rule):
    """People with same surname"""
    labels      = [_('Substring:')]
    name        = _('People matching the <name>')
    description = _("Matches people with same lastname")
    category    = _('General filters')
    def apply(self,db,person):
        src = self.list[0].upper()
        for name in [person.get_primary_name()] + person.get_alternate_names():
            if name.surname and name.surname.upper() == src.upper():
                return True
        return False

def run(database, document, person):
    """
    Loops through the families that the person is a child in, and display
    the information about the other children.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = SimpleTable(sdb)
    if isinstance(person, str):
        surname = person
        rsurname = person
    else:
        surname = sdb.surname(person)
        rsurname = person.get_primary_name().get_group_name()
    # display the title
    sdoc.title(_("People with the surname '%s'") % surname)
    sdoc.paragraph("")
    stab.columns(_("Person"), _("Birth Date"), _("Name type"))
    filter = GenericFilterFactory('Person')()
    if rsurname != '':
        rule = SameSurname([rsurname])
    else:
        rule = IncompleteSurname([])
    filter.add_rule(rule)
    people = filter.apply(database, 
                          database.get_person_handles(sort_handles=False))
    matches = 0
    for person_handle in people:
        person = database.get_person_from_handle(person_handle)
        stab.row(person, sdb.birth_date_obj(person),
                 str(person.get_primary_name().get_type()))
        matches += 1
    sdoc.paragraph(_("There are %d people with a matching name, or alternate name.\n") % matches)
    stab.write(sdoc)
                    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_quick_report(
    name = 'samesurnames',
    category = CATEGORY_QR_PERSON,
    run_func = run,
    translated_name = _("Same Surnames"),
    status = _("Stable"),
    description= _("Display people with the same surname as a person."),
    author_name="Douglas S. Blank",
    author_email="dblank@cs.brynmawr.edu"
    )
