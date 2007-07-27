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

from Simple import SimpleAccess, by_date, SimpleDoc
from gettext import gettext as _

def run(database, document, person):
    
    sa = SimpleAccess(database)
    sd = SimpleDoc(document)

    sd.title(_("Siblings of %s") % sa.name(person))
    sd.paragraph("")
    sd.header1("%-30s\t%-10s\t%s" % (_("Sibling"),_("Gender"),_("Birth Date")))

    gid = sa.gid(person)

    for family in sa.child_in(person):
        for child in sa.children(family):
            if sa.gid(child) != gid:
                sd.paragraph("%-30s\t%-10s\t%s" % (
                        sa.name(child),
                        sa.gender(child),
                        sa.birth_date(child)))
                    
