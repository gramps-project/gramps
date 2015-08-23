#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Doug Blank <doug.blank@gmail.com>
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
Display link references for a note
"""

from gramps.gen.simple import SimpleAccess, SimpleDoc
from gramps.gui.plug.quick import QuickTable
from gramps.gen.lib import StyledTextTagType
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

def run(database, document, obj):
    """
    Display link references for this note.
    """

    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = QuickTable(sdb)

    # display the title
    sdoc.title(_("Link References for this note"))
    sdoc.paragraph("\n")
    stab.columns(_("Type"), _("Reference"), _("Link check"))

    for (ldomain, ltype, lprop, lvalue) in obj.get_links():
            if ldomain == "gramps":
                tagtype = _(ltype)
                ref_obj = sdb.get_link(ltype, lprop, lvalue)
                if ref_obj:
                    tagvalue = ref_obj
                    tagcheck = _("Ok")
                else:
                    tagvalue = lvalue
                    tagcheck = _("Failed: missing object")
            else:
                tagtype = _("Internet")
                tagvalue = lvalue
                tagcheck = ""
            stab.row(tagtype, tagvalue, tagcheck)

    if stab.get_row_count() > 0:
        stab.write(sdoc)
        document.has_data = True
    else:
        sdoc.paragraph(_("No link references for this note"))
        sdoc.paragraph("")
        document.has_data = False
    sdoc.paragraph("")

