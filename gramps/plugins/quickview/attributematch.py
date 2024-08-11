#
# Gramps - a GTK+/GNOME based genealogy program
#
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
#

from gramps.gen.simple import SimpleAccess, SimpleDoc
from gramps.gui.plug.quick import QuickTable
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


def run(database, document, attribute, value=None):
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = QuickTable(sdb)
    sdoc.title(_("People who have the '%s' Attribute") % attribute)
    sdoc.paragraph("")
    stab.columns(_("Person"), str(attribute))
    matches = 0
    for person_handle in database.iter_person_handles():
        person = database.get_person_from_handle(person_handle)
        matched = False
        for attr in person.attribute_list:
            if str(attr.type) == attribute:
                stab.row(person, str(attr.get_value()))
                matched = True
        if matched:
            matches += 1
    document.has_data = matches > 0
    sdoc.paragraph(_("There are %d people with a matching attribute name.\n") % matches)
    if document.has_data:
        stab.write(sdoc)
    else:
        sdoc.header1(_("Not found"))
