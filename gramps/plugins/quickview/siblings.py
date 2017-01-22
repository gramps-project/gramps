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

"""
Display a person's siblings in a report window
"""

from gramps.gen.simple import SimpleAccess, SimpleDoc
from gramps.gui.plug.quick import QuickTable
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

def run(database, document, person):
    """
    Loops through the families that the person is a child in, and display
    the information about the other children.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = QuickTable(sdb)
    rel_class = get_relationship_calculator(glocale)

    # display the title
    # feature request 2356: avoid genitive form
    sdoc.title(_("Siblings of %s") % sdb.name(person))
    sdoc.paragraph("")
    stab.columns(_("Sibling"), _("Gender"), _("Birth Date"), _("Type"))
    # grab our current id (self):
    gid = sdb.gid(person)
    # loop through each family in which the person is a child
    document.has_data = False
    for family in sdb.child_in(person):
        # loop through each child in the family
        for child in sdb.children(family):
            # only display if this child is not the active person
            if sdb.gid(child) != gid:
                rel_str = rel_class.get_sibling_relationship_string(
                    rel_class.get_sibling_type(database, person, child),
                    person.get_gender(), child.get_gender())
            else:
                rel_str = _('self')
            # pass row the child object to make link:
            stab.row(child,
                     sdb.gender(child),
                     sdb.birth_or_fallback(child),
                     rel_str)
            document.has_data = True
    if document.has_data:
        stab.write(sdoc)
    else:
        sdoc.header1(_("Not found") + "\n")
