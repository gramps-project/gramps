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
Display references for any object
"""
from ReportBase import (CATEGORY_QR_SOURCE, CATEGORY_QR_PERSON, 
                        CATEGORY_QR_FAMILY, CATEGORY_QR_EVENT, 
                        CATEGORY_QR_PLACE, CATEGORY_QR_REPOSITORY)

from Simple import SimpleAccess, SimpleDoc, SimpleTable
from gettext import gettext as _
from PluginUtils import register_quick_report

def get_ref(db, objclass, handle):
    """
    Looks up object in database
    """
    if objclass == 'Person':
        ref = db.get_person_from_handle(handle)
    elif objclass == 'Family':
        ref = db.get_family_from_handle(handle)
    elif objclass == 'Event':
        ref = db.get_event_from_handle(handle)
    elif objclass == 'Source':
        ref = db.get_source_from_handle(handle)
    elif objclass == 'Place':
        ref = db.get_place_from_handle(handle)
    elif objclass == 'Repository':
        ref = db.get_repository_from_handle(handle)
    else:
        ref = objclass
    return ref

def run(database, document, object, item, trans):
    """
    Display back-references for this object.
    """

    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = SimpleTable(sdb, sdoc)

    # display the title
    sdoc.title(_("References for this %s") % trans)
    sdoc.paragraph("\n")
    stab.columns(_("Type"), _("Reference"))
    
    for (objclass, handle) in database.find_backlink_handles(object.handle):
        ref = get_ref(database, objclass, handle)
        stab.row(objclass, ref)

    if stab.get_row_count() > 0:
        stab.write()
    else:
        sdoc.paragraph(_("No references for this %s") % trans)
        sdoc.paragraph("")
    sdoc.paragraph("")

#------------------------------------------------------------------------
#
# Register the report
#
#------------------------------------------------------------------------

refitems = [(CATEGORY_QR_PERSON, 'person', _("Person")), 
            (CATEGORY_QR_FAMILY,'family', _("Family")), 
            (CATEGORY_QR_EVENT, 'event', _("Event")), 
            (CATEGORY_QR_SOURCE, 'source', _("Source")), 
            (CATEGORY_QR_PLACE, 'place', _("Place")), 
            (CATEGORY_QR_REPOSITORY, 'repository', _("Repository")), 
            ]
for (category,item,trans) in refitems:
    register_quick_report(
        name = item + 'refereneces',
        category = category,
        run_func = lambda db, doc, obj, item=item, trans=trans: \
            run(db, doc, obj, item, trans),
        translated_name = _("%s References") % trans,
        status = _("Stable"),
        description= _("Display references for a %s") % trans,
        author_name="Douglas Blank",
        author_email="dblank@cs.brynmawr.edu"
        )
