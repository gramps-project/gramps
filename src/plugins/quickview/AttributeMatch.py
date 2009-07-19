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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# $Id: $
#
#

from ReportBase import CATEGORY_QR_MISC
from Simple import SimpleAccess, SimpleDoc, SimpleTable
from gen.plug import PluginManager
from gettext import gettext as _

def run(database, document, attribute, value=None):
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = SimpleTable(sdb)
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
    sdoc.paragraph(_("There are %d people with a matching attribute name.\n") % matches)
    stab.write(sdoc)

pmgr = PluginManager.get_instance()
pmgr.register_quick_report(
    name = 'attribute_match',
    category = CATEGORY_QR_MISC, # to run with attribute/value
    run_func = run,
    translated_name = _("Attribute Match"),
    status = _("Stable"),
    description= _("Display people with same attribute."),
    author_name="Douglas S. Blank",
    author_email="dblank@cs.brynmawr.edu"
    )
