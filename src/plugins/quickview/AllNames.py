#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  Douglas S. Blank
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
#
# $Id$
#
#

"""
Display all names of all people
"""

from Simple import SimpleAccess, SimpleDoc, SimpleTable
from BasicUtils import name_displayer as nd
from gen.lib import Person

from gettext import gettext as _
from gettext import ngettext

def run(database, document, *args, **kwargs):
    """
    Loops through the families that the person is a child in, and display
    the information about the other children.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = SimpleTable(sdb)
    # display the title
    sdoc.title(_("All Names of All People"))
    sdoc.paragraph("")
    matches = 0
    stab.columns(_("Name"), _("Primary Name"), _("Name Type"))
    names = [] # name, person
    for person in database.iter_people():
        primary_name = person.get_primary_name()
        if primary_name:
            names += [(nd.display_name(primary_name), 
                       person, 
                       str(primary_name.get_type()))]
        names += [(nd.display_name(name), 
                   person, 
                   str(name.get_type())) for name in  
                  person.get_alternate_names()]
    names.sort()
    matches = 0
    for (name, person, name_type) in names:
        stab.row(name, person, name_type)
        matches += 1
    sdoc.paragraph(_("Total names %d") % matches)
    sdoc.paragraph("")
    stab.write(sdoc)
