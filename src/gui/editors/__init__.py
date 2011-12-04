#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# gui/editors/__init__.py
# $Id$
#

from editaddress import EditAddress
from editattribute import EditAttribute, EditFamilyAttribute
from editchildref import EditChildRef
from editcitation import EditCitation, DeleteCitationQuery
from editevent import EditEvent, DeleteEventQuery
from editeventref import EditEventRef, EditFamilyEventRef
from editfamily import EditFamily
from editldsord import EditLdsOrd, EditFamilyLdsOrd
from editlocation import EditLocation
from editmedia import EditMedia, DeleteMediaQuery
from editmediaref import EditMediaRef
from editname import EditName
from editnote import EditNote, DeleteNoteQuery
from editperson import EditPerson
from editpersonref import EditPersonRef
from editplace import EditPlace, DeletePlaceQuery
from editrepository import EditRepository, DeleteRepositoryQuery
from editreporef import EditRepoRef
from editsource import EditSource, DeleteSrcQuery
from editurl import EditUrl
from editlink import EditLink

# Map from gen.lib name to Editor:
EDITORS = {
    'Person': EditPerson,
    'Event': EditEvent,
    'Family': EditFamily,
    'Media': EditMedia,
    'Source': EditSource,
    'Citation': EditCitation,
    'Place': EditPlace,
    'Repository': EditRepository,
    'Note': EditNote,
    }

def EditObject(dbstate, uistate, track, obj_class, prop, value):
    """
    Generic Object Editor. 
    obj_class is Person, Source, Repository, etc.
    prop is 'handle' or 'gramps_id'
    value is string handle or string gramps_id
    """
    import logging
    LOG = logging.getLogger(".Edit")
    if obj_class in dbstate.db.get_table_names():
        if prop in ("gramps_id", "handle"):
            obj = dbstate.db.get_table_metadata(obj_class)[prop + "_func"](value)
            if obj:
                try:
                    EDITORS[obj_class](dbstate, uistate, track, obj)
                except Exception as msg:
                    LOG.warn(str(msg)) 
            else:
                LOG.warn("gramps://%s/%s/%s not found" % 
                         (obj_class, prop, value))
        else:
            LOG.warn("unknown property to edit '%s'; "
                     "should be 'gramps_id' or 'handle'" % prop)
    else:
        LOG.warn("unknown object to edit '%s'; "
                 "should be one of %s" % (obj_class, EDITORS.keys()))

