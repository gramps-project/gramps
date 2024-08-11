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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# gui/editors/__init__.py

from .editaddress import EditAddress
from .editattribute import EditAttribute, EditSrcAttribute
from .editchildref import EditChildRef
from .editcitation import EditCitation
from .editdate import EditDate
from .editevent import EditEvent
from .editeventref import EditEventRef
from .editfamily import EditFamily
from .editldsord import EditLdsOrd, EditFamilyLdsOrd
from .editlocation import EditLocation
from .editmedia import EditMedia
from .editmediaref import EditMediaRef
from .editname import EditName
from .editnote import EditNote
from .editperson import EditPerson
from .editpersonref import EditPersonRef
from .editplace import EditPlace
from .editplacename import EditPlaceName
from .editplaceref import EditPlaceRef
from .editrepository import EditRepository
from .editreporef import EditRepoRef
from .editsource import EditSource
from .edittaglist import EditTagList
from .editurl import EditUrl
from .editlink import EditLink
from .filtereditor import FilterEditor, EditFilter
from gramps.gen.lib import (
    Person,
    Family,
    Event,
    Place,
    Repository,
    Source,
    Citation,
    Media,
    Note,
)

# Map from gramps.gen.lib name to Editor:
EDITORS = {
    "Person": EditPerson,
    "Event": EditEvent,
    "Family": EditFamily,
    "Media": EditMedia,
    "Source": EditSource,
    "Citation": EditCitation,
    "Place": EditPlace,
    "Repository": EditRepository,
    "Note": EditNote,
}

CLASSES = {
    "Person": Person,
    "Event": Event,
    "Family": Family,
    "Media": Media,
    "Source": Source,
    "Citation": Citation,
    "Place": Place,
    "Repository": Repository,
    "Note": Note,
}


def EditObject(
    dbstate, uistate, track, obj_class, prop=None, value=None, callback=None
):
    """
    Generic Object Editor.
    obj_class is Person, Source, Repository, etc.
    prop is 'handle', 'gramps_id', or None (for new object)
    value is string handle, string gramps_id, or None (for new object)
    """
    import logging

    LOG = logging.getLogger(".Edit")
    if obj_class in EDITORS.keys():
        if value is None:
            obj = CLASSES[obj_class]()
            try:
                EDITORS[obj_class](dbstate, uistate, track, obj, callback=callback)
            except Exception as msg:
                LOG.warning(str(msg))
        elif prop in ("gramps_id", "handle"):
            obj = dbstate.db.method("get_%s_from_%s", obj_class, prop)(value)
            if obj:
                try:
                    EDITORS[obj_class](dbstate, uistate, track, obj, callback=callback)
                except Exception as msg:
                    LOG.warning(str(msg))
            else:
                LOG.warning("gramps://%s/%s/%s not found" % (obj_class, prop, value))
        else:
            LOG.warning(
                "unknown property to edit '%s'; "
                "should be 'gramps_id' or 'handle'" % prop
            )
    else:
        LOG.warning(
            "unknown object to edit '%s'; "
            "should be one of %s" % (obj_class, list(EDITORS.keys()))
        )
