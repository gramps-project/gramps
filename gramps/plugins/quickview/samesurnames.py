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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#

"""
Display a people who have a person's same surname or given name.
"""

from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
ngettext = glocale.translation.ngettext # else "nearby" comments are ignored
from gramps.gen.simple import SimpleAccess, SimpleDoc
from gramps.gui.plug.quick import QuickTable
from gramps.gen.lib import Person
from gramps.gen.filters.rules import Rule
from gramps.gen.filters import GenericFilterFactory

class IncompleteSurname(Rule):
    """People with incomplete surnames"""
    name = _('People with incomplete surnames')
    description = _("Matches people with lastname missing")
    category = _('General filters')
    def apply(self, db, person):
        for name in [person.get_primary_name()] + person.get_alternate_names():
            if name.get_group_name() == "":
                return True
        return False

class SameSurname(Rule):
    """People with same surname"""
    labels = [_('Substring:')]
    name = _('People matching the <surname>')
    description = _("Matches people with same lastname")
    category = _('General filters')
    def apply(self, db, person):
        src = self.list[0].upper()
        for name in [person.get_primary_name()] + person.get_alternate_names():
            if name.get_surname() and name.get_surname().upper() == src.upper():
                return True
        return False

class SameGiven(Rule):
    """People with same given name"""
    labels = [_('Substring:')]
    name = _('People matching the <given>')
    description = _("Matches people with same given name")
    category = _('General filters')
    def apply(self, db, person):
        src = self.list[0].upper()
        for name in [person.get_primary_name()] + person.get_alternate_names():
            if name.first_name:
                anyNBSP = name.first_name.split('\u00A0')
                if len(anyNBSP) > 1: # there was an NBSP, a non-breaking space
                    first_two = anyNBSP[0] + '\u00A0' + anyNBSP[1].split()[0]
                    if first_two.upper() == src:
                        return True
                    else:
                        name.first_name = ' '.join(anyNBSP[1].split()[1:])
                if " " in name.first_name.strip():
                    for name in name.first_name.upper().strip().split():
                        if name == src.upper():
                            return True
                elif name.first_name.upper() == src.upper():
                    return True
        return False

class IncompleteGiven(Rule):
    """People with incomplete given names"""
    name = _('People with incomplete given names')
    description = _("Matches people with firstname missing")
    category = _('General filters')
    def apply(self, db, person):
        for name in [person.get_primary_name()] + person.get_alternate_names():
            if name.get_first_name() == "":
                return True
        return False

def run(database, document, person):
    """
    Loops through the families that the person is a child in, and displays
    the information about the other children.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = QuickTable(sdb)
    if isinstance(person, Person):
        surname = sdb.surname(person)
        rsurname = person.get_primary_name().get_group_name()
    else:
        surname = person
        rsurname = person
    # display the title
    sdoc.title(_("People sharing the surname '%s'") % surname)
    sdoc.paragraph("")
    stab.columns(_("Person"), _("Birth Date"), _("Name type"))
    filter = GenericFilterFactory('Person')()
    if rsurname != '':
        rule = SameSurname([rsurname])
    else:
        rule = IncompleteSurname([])
    filter.add_rule(rule)
    people = filter.apply(database,
                          database.iter_person_handles())

    matches = 0
    for person_handle in people:
        person = database.get_person_from_handle(person_handle)
        stab.row(person, sdb.birth_or_fallback(person),
                 str(person.get_primary_name().get_type()))
        matches += 1

    document.has_data = matches > 0
    sdoc.paragraph(
        # translators: leave all/any {...} untranslated
        ngettext("There is {number_of} person "
                     "with a matching name, or alternate name.\n",
                 "There are {number_of} people "
                     "with a matching name, or alternate name.\n", matches
                ).format(number_of=matches) )
    stab.write(sdoc)

def run_given(database, document, person):
    """
    Loops through the families that the person is a child in, and displays
    the information about the other children.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = QuickTable(sdb)
    if isinstance(person, Person):
        rgivenname = person.get_primary_name().get_first_name()
    else:
        rgivenname = person
    if " " in rgivenname.strip():
        rgivenname, second = rgivenname.strip().split(" ", 1)
    # display the title
    sdoc.title(_("People with the given name '%s'") % rgivenname)
    sdoc.paragraph("")
    stab.columns(_("Person"), _("Birth Date"), _("Name type"))
    filter = GenericFilterFactory('Person')()
    if rgivenname != '':
        rule = SameGiven([rgivenname])
    else:
        rule = IncompleteGiven([])
    filter.add_rule(rule)
    people = filter.apply(database,
                          database.iter_person_handles())

    matches = 0
    for person_handle in people:
        person = database.get_person_from_handle(person_handle)
        stab.row(person, sdb.birth_or_fallback(person),
                 str(person.get_primary_name().get_type()))
        matches += 1

    document.has_data = matches > 0
    sdoc.paragraph(
        # translators: leave all/any {...} untranslated
        ngettext("There is {number_of} person "
                     "with a matching name, or alternate name.\n",
                 "There are {number_of} people "
                     "with a matching name, or alternate name.\n", matches
                ).format(number_of=matches) )
    stab.write(sdoc)
