#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2011       Tim G L Lyons
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
Display references for any object
"""

from gramps.gen.simple import SimpleAccess, SimpleDoc
from gramps.gui.plug.quick import QuickTable
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

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
    elif objclass == 'Citation':
        ref = db.get_citation_from_handle(handle)
    elif objclass == 'Place':
        ref = db.get_place_from_handle(handle)
    elif objclass == 'Note':
        ref = db.get_note_from_handle(handle)
    elif objclass == 'Media':
        ref = db.get_media_from_handle(handle)
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
    stab = QuickTable(sdb)

    # display the title
    sdoc.title(_("References for this %s") % trans)
    sdoc.paragraph("\n")
    stab.columns(_("Type"), _("Reference"))
    for (objclass, handle) in database.find_backlink_handles(object.handle):
        ref = get_ref(database, objclass, handle)
        stab.row(_(objclass), ref) # translation are explicit (above)

    if stab.get_row_count() > 0:
        document.has_data = True
        stab.write(sdoc)
    else:
        document.has_data = False
        sdoc.paragraph(_("No references for this %s") % trans)
        sdoc.paragraph("")
    sdoc.paragraph("")

#functions for the actual quickreports
run_person = lambda db, doc, obj: run(db, doc, obj, 'person', _("Person"))
run_family = lambda db, doc, obj: run(db, doc, obj, 'family', _("Family"))
run_event = lambda db, doc, obj: run(db, doc, obj, 'event', _("Event"))
run_source = lambda db, doc, obj: run(db, doc, obj, 'source', _("Source"))
run_citation = lambda db, doc, obj: run(db, doc, obj, 'citation', _("Citation"))
run_source_or_citation = lambda db, doc, obj: run(db, doc, obj,
                                'source or citation', _("Source or Citation"))
run_place = lambda db, doc, obj: run(db, doc, obj, 'place', _("Place"))
run_media = lambda db, doc, obj: run(db, doc, obj, 'media', _("Media"))
run_note = lambda db, doc, obj: run(db, doc, obj, 'note', _("Note"))
