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
Display a person's siblings in a report window
"""

from Simple import SimpleAccess, SimpleDoc
from gettext import gettext as _

# define the formatting string once as a constant. Since this is reused

__FMT = "%-30s\t%-10s\t%s"

def run(database, document, person):
    """
    Loops through the families that the person is a child in, and display
    the information about the other children.
    """
    
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)

    # display the title
    sdoc.title(_("Siblings of %s") % sdb.name(person))
    sdoc.paragraph("")

    # display the header of a table
    sdoc.header1(__FMT % (_("Sibling"), _("Gender"), _("Birth Date")))

    # grab our current id, so we can filter the active person out
    # of the data

    gid = sdb.gid(person)

    # loop through each family in which the person is a child
    for family in sdb.child_in(person):

        # loop through each child in the family
        for child in sdb.children(family):

            # only display if this child is not the active person
            if sdb.gid(child) != gid:
                sdoc.paragraph(__FMT % (
                        sdb.name(child),
                        sdb.gender(child),
                        sdb.birth_date(child)))
                    
