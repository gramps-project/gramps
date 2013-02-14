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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# $Id$
#

"""
Display link references for a note
"""

from gramps.gen.simple import SimpleAccess, SimpleDoc
from gramps.gui.plug.quick import QuickTable
from gramps.gen.lib import StyledTextTagType
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.get_translation().gettext

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

    tags = obj.text.get_tags()

    for styledtext_tag in tags:
        if int(styledtext_tag.name) == StyledTextTagType.LINK:
            if styledtext_tag.value.startswith("gramps://"):
                object_class, prop, value = styledtext_tag.value[9:].split("/", 2)
                tagtype = _(object_class)
                ref_obj = sdb.get_link(object_class, prop, value)
                if ref_obj:
                    tagvalue = ref_obj
                    tagcheck = _("Ok")
                else:
                    tagvalue = styledtext_tag.value
                    tagcheck = _("Failed: missing object")
            else:
                tagtype = _("Internet")
                tagvalue = styledtext_tag.value
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

