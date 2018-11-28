#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
#
# This program is free software; you can redistribute it and/or modiy
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

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import pickle
import os
from xml.sax.saxutils import escape
from time import strftime as strftime

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Pango
import cairo

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.lib import NoteType
from gramps.gen.datehandler import get_date
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.constfunc import mac
from .display import display_help
from .managedwindow import ManagedWindow
from .glade import Glade
from .ddtargets import DdTargets
from .makefilter import make_filter
from .utils import is_right_click, no_match_primary_mask
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Navigation' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Using_the_Clipboard')
clipdb = None  # current db to avoid different transient dbs during db change

#-------------------------------------------------------------------------
#
# icons used in the object listing
#
#-------------------------------------------------------------------------

theme = Gtk.IconTheme.get_default()
LINK_PIC = theme.load_icon('stock_link', 16, 0)
ICONS = {}
for (name, icon) in (("media", "gramps-media"),
                     ("note", "gramps-notes"),
                     ("person", "gramps-person"),
                     ("place", "gramps-place"),
                     ('address', 'gramps-address'),
                     ('attribute', 'gramps-attribute'),
                     ('event', 'gramps-event'),
                     ('family', 'gramps-family'),
                     ('location', 'geo-place-link'),
                     ('media', 'gramps-media'),
                     ('name', 'geo-show-person'),
                     ('repository', 'gramps-repository'),
                     ('source', 'gramps-source'),
                     ('citation', 'gramps-citation'),
                     ('text', 'gramps-font'),
                     ('url', 'gramps-geo')):
    ICONS[name] = theme.load_icon(icon, 16, 0)


#-------------------------------------------------------------------------
#
# Local functions
#
#-------------------------------------------------------------------------
def map2class(target):
    _d_ = {"person-link": ClipPersonLink,
           "family-link": ClipFamilyLink,
           'personref': ClipPersonRef,
           'childref': ClipChildRef,
           'source-link': ClipSourceLink,
           'citation-link': ClipCitation,
           'repo-link': ClipRepositoryLink,
           'pevent': ClipEvent,
           'eventref': ClipEventRef,
           'media': ClipMediaObj,
           'mediaref': ClipMediaRef,
           'place-link': ClipPlace,
           'placeref': ClipPlaceRef,
           'note-link': ClipNote,
           'TEXT': ClipText}
    return _d_[target] if target in _d_ else None


def obj2class(target):
    _d_ = {"Person": ClipPersonLink,
           "Family": ClipFamilyLink,
           'Source': ClipSourceLink,
           'Citation': ClipCitation,
           'Repository': ClipRepositoryLink,
           'Event': ClipEvent,
           'Media': ClipMediaObj,
           'Place': ClipPlace,
           'Note': ClipNote}
    return _d_[target] if target in _d_ else None

OBJ2TARGET = {"Person": Gdk.atom_intern('person-link', False),
              "Family": Gdk.atom_intern('family-link', False),
              'Source': Gdk.atom_intern('source-link', False),
              'Citation': Gdk.atom_intern('citation-link', False),
              'Repository': Gdk.atom_intern('repo-link', False),
              'Event': Gdk.atom_intern('pevent', False),
              'Media': Gdk.atom_intern('media', False),
              'Place': Gdk.atom_intern('place-link', False),
              'Note': Gdk.atom_intern('note-link', False)}


def obj2target(target):
    return OBJ2TARGET[target] if target in OBJ2TARGET else None


def model_contains(model, data):
    """
    Returns True if data is a row in model.
    """
    # check type and value
    # data[0] is type of drop item, data[1] is Clip object
    for row in model:
        if data[0] == 'TEXT':
            same = ((row[0] == data[0]) and
                    (row[1]._value == data[1]._value))
        else:
            # FIXME: too restrictive, birth and death won't both copy
            same = ((row[0] == data[0]) and
                    (row[1]._title == data[1]._title) and
                    (row[1]._handle == data[1]._handle) and
                    (row[3] == data[3]) and
                    (row[4] == data[4]))
        if same:
            return True
    return False


#-------------------------------------------------------------------------
#
# wrapper classes to provide object specific listing in the ListView
#
#-------------------------------------------------------------------------
class ClipWrapper:
    UNAVAILABLE_ICON = 'dialog-error'

    def __init__(self, obj):
        self._obj = obj
        self._pickle = obj
        self._type = _("Unknown")
        self._objclass = None
        self._handle = None
        self._title = _('Unavailable')
        self._value = _('Unavailable')
        self._dbid = clipdb.get_dbid()
        self._dbname = clipdb.get_dbname()

    def get_type(self):
        return self._type

    def get_title(self):
        return self._title

    def get_value(self):
        return self._value

    def get_dbname(self):
        return self._dbname

    def pack(self):
        """
        Return a byte string that can be packed in a GtkSelectionData
        structure
        """
        if not self.is_valid():
            data = list(pickle.loads(self._pickle))
            data[2] = {
                "_obj": self._obj,
                "_pickle": self._pickle,
                "_type": self._type,
                "_handle": self._handle,
                "_objclass": self._objclass,
                "_title": self._title,
                "_value": self._value,
                "_dbid": self._dbid,
                "_dbname": self._dbname}
            return pickle.dumps(data)
        if isinstance(self._obj, bytes):
            return self._obj
        # don't know if this happens in Gramps, theoretically possible
        asuni = str(self._obj)
        return asuni.encode('utf-8')

    def is_valid(self):
        if self._objclass and obj2class(self._objclass):
            # we have a primary object
            data = pickle.loads(self._obj)
            handle = data[2]
            return clipdb.method("has_%s_handle", self._objclass)(handle)
        return True


class ClipHandleWrapper(ClipWrapper):

    def __init__(self, obj):
        super(ClipHandleWrapper, self).__init__(obj)
        # unpack object
        (drag_type, idval, data, val) = pickle.loads(obj)
        if isinstance(data, dict):
            self.set_data(data)
        else:
            self._handle = data

    def set_data(self, data):
        for item in data:
            setattr(self, item, data[item])


class ClipObjWrapper(ClipWrapper):

    def __init__(self, obj):
        super(ClipObjWrapper, self).__init__(obj)
        #unpack object
        (drag_type, idval, self._obj, val) = pickle.loads(obj)
        self._pickle = obj

    def pack(self):
        if not self.is_valid():
            data = list(pickle.loads(self._pickle))
            data[2] = {
                "_obj": self._obj,
                "_pickle": self._pickle,
                "_type": self._type,
                "_handle": self._handle,
                "_objclass": self._objclass,
                "_title": self._title,
                "_value": self._value,
                "_dbid": self._dbid,
                "_dbname": self._dbname}
            return pickle.dumps(data)
        return self._pickle

    def is_valid(self):
        if self._obj is None:
            return False

        for (clname, handle) in self._obj.get_referenced_handles_recursively():
            if obj2class(clname):  # a class we care about (not tag)
                if not clipdb.method("has_%s_handle", clname)(handle):
                    return False

        return True


class ClipAddress(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.ADDRESS]
    DRAG_TARGET = DdTargets.ADDRESS
    ICON = ICONS['address']

    def __init__(self, obj):
        super(ClipAddress, self).__init__(obj)
        self._type = _("Address")
        self.refresh()

    def refresh(self):
        if self._obj:
            self._title = get_date(self._obj)
            self._value = "%s %s %s %s" % (self._obj.get_street(),
                                           self._obj.get_city(),
                                           self._obj.get_state(),
                                           self._obj.get_country())


class ClipLocation(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.LOCATION]
    DRAG_TARGET = DdTargets.LOCATION
    ICON = ICONS['location']

    def __init__(self, obj):
        super(ClipLocation, self).__init__(obj)
        self._type = _("Location")
        self.refresh()

    def refresh(self):
        self._value = "%s %s %s" % (self._obj.get_city(),
                                    self._obj.get_state(),
                                    self._obj.get_country())


class ClipEvent(ClipHandleWrapper):

    DROP_TARGETS = [DdTargets.EVENT]
    DRAG_TARGET = DdTargets.EVENT
    ICON = ICONS["event"]

    def __init__(self, obj):
        super(ClipEvent, self).__init__(obj)
        self._type = _("Event")
        self._objclass = 'Event'
        self.refresh()

    def refresh(self):
        if self._handle:
            value = clipdb.get_event_from_handle(self._handle)
            if value:
                self._title = str(value.get_type())
                self._value = value.get_description()


class ClipPlace(ClipHandleWrapper):

    DROP_TARGETS = [DdTargets.PLACE_LINK]
    DRAG_TARGET = DdTargets.PLACE_LINK
    ICON = ICONS["place"]

    def __init__(self, obj):
        super(ClipPlace, self).__init__(obj)
        self._type = _("Place")
        self._objclass = 'Place'
        self.refresh()

    def refresh(self):
        if self._handle:
            value = clipdb.get_place_from_handle(self._handle)
            if value:
                self._title = value.gramps_id
                self._value = place_displayer.display(clipdb, value)


class ClipNote(ClipHandleWrapper):

    DROP_TARGETS = [DdTargets.NOTE_LINK]
    DRAG_TARGET = DdTargets.NOTE_LINK
    ICON = ICONS["note"]

    def __init__(self, obj):
        super(ClipNote, self).__init__(obj)
        self._type = _("Note")
        self._objclass = 'Note'
        self.refresh()

    def refresh(self):
        value = clipdb.get_note_from_handle(self._handle)
        if value:
            self._title = value.get_gramps_id()
            note = value.get().replace('\n', ' ')
            # String must be unicode for truncation to work for non
            # ascii characters
            note = str(note)
            if len(note) > 80:
                self._value = note[:80] + "..."
            else:
                self._value = note


class ClipFamilyEvent(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.FAMILY_EVENT]
    DRAG_TARGET = DdTargets.FAMILY_EVENT
    ICON = ICONS['family']

    def __init__(self, obj):
        super(ClipFamilyEvent, self).__init__(obj)
        self._type = _("Family Event")
        self.refresh()

    def refresh(self):
        if self._obj:
            self._title = str(self._obj.get_type())
            self._value = self._obj.get_description()


class ClipUrl(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.URL]
    DRAG_TARGET = DdTargets.URL
    ICON = ICONS['url']

    def __init__(self, obj):
        super(ClipUrl, self).__init__(obj)
        self._type = _("Url")
        self.refresh()

    def refresh(self):
        if self._obj:
            self._title = self._obj.get_path()
            self._value = self._obj.get_description()


class ClipAttribute(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.ATTRIBUTE]
    DRAG_TARGET = DdTargets.ATTRIBUTE
    ICON = ICONS['attribute']

    def __init__(self, obj):
        super(ClipAttribute, self).__init__(obj)
        self._type = _("Attribute")
        self.refresh()

    def refresh(self):
        self._title = str(self._obj.get_type())
        self._value = self._obj.get_value()


class ClipFamilyAttribute(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.FAMILY_ATTRIBUTE]
    DRAG_TARGET = DdTargets.FAMILY_ATTRIBUTE
    ICON = ICONS['attribute']

    def __init__(self, obj):
        super(ClipFamilyAttribute, self).__init__(obj)
        self._type = _("Family Attribute")
        self.refresh()

    def refresh(self):
        if self._obj:
            self._title = str(self._obj.get_type())
            self._value = self._obj.get_value()


class ClipCitation(ClipHandleWrapper):

    DROP_TARGETS = [DdTargets.CITATION_LINK]
    DRAG_TARGET = DdTargets.CITATION_LINK
    ICON = ICONS["citation"]

    def __init__(self, obj):
        super(ClipCitation, self).__init__(obj)
        self._type = _("Citation")
        self._objclass = 'Citation'
        self.refresh()

    def refresh(self):
        if self._handle:
            citation = clipdb.get_citation_from_handle(self._handle)
            if citation:
                self._title = citation.get_gramps_id()
                notelist = list(map(clipdb.get_note_from_handle,
                                    citation.get_note_list()))
                srctxtlist = [note for note in notelist
                              if note.get_type() == NoteType.SOURCE_TEXT]
                page = citation.get_page()
                if not page:
                    page = _('not available|NA')
                text = ""
                if srctxtlist:
                    text = " ".join(srctxtlist[0].get().split())
                #String must be unicode for truncation to work for non
                #ascii characters
                    text = str(text)
                    if len(text) > 60:
                        text = text[:60] + "..."
                self._value = _("Volume/Page: %(pag)s -- %(sourcetext)s") % {
                    'pag' : page,
                    'sourcetext' : text}


class ClipRepoRef(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.REPOREF]
    DRAG_TARGET = DdTargets.REPOREF
    ICON = LINK_PIC

    def __init__(self, obj):
        super(ClipRepoRef, self).__init__(obj)
        self._type = _("Repository ref")
        self.refresh()

    def refresh(self):
        if self._obj:
            base = clipdb.get_repository_from_handle(self._obj.ref)
            if base:
                self._title = str(base.get_type())
                self._value = base.get_name()


class ClipEventRef(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.EVENTREF]
    DRAG_TARGET = DdTargets.EVENTREF
    ICON = LINK_PIC

    def __init__(self, obj):
        super(ClipEventRef, self).__init__(obj)
        self._type = _("Event ref")
        self.refresh()

    def refresh(self):
        if self._obj:
            base = clipdb.get_event_from_handle(self._obj.ref)
            if base:
                self._title = base.gramps_id
                self._value = str(base.get_type())


class ClipPlaceRef(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.PLACEREF]
    DRAG_TARGET = DdTargets.PLACEREF
    ICON = LINK_PIC

    def __init__(self, obj):
        super(ClipPlaceRef, self).__init__(obj)
        self._type = _("Place ref")
        self.refresh()

    def refresh(self):
        if self._obj:
            base = clipdb.get_place_from_handle(self._obj.ref)
            if base:
                self._title = base.gramps_id
                self._value = place_displayer.display(clipdb, base)


class ClipName(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.NAME]
    DRAG_TARGET = DdTargets.NAME
    ICON = ICONS['name']

    def __init__(self, obj):
        super(ClipName, self).__init__(obj)
        self._type = _("Name")
        self.refresh()

    def refresh(self):
        if self._obj:
            self._title = str(self._obj.get_type())
            self._value = self._obj.get_name()


class ClipPlaceName(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.PLACENAME]
    DRAG_TARGET = DdTargets.PLACENAME
    ICON = ICONS['name']

    def __init__(self, obj):
        super(ClipPlaceName, self).__init__(obj)
        self._type = _("Place Name")
        self.refresh()

    def refresh(self):
        if self._obj:
            self._title = get_date(self._obj)
            self._value = self._obj.get_value()


class ClipSurname(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.SURNAME]
    DRAG_TARGET = DdTargets.SURNAME
    ICON = ICONS['name']

    def __init__(self, obj):
        super(ClipSurname, self).__init__(obj)
        self._type = _("Surname")
        self.refresh()

    def refresh(self):
        if self._obj:
            self._title = self._obj.get_surname()
            self._value = self._obj.get_surname()


class ClipText(ClipWrapper):

    DROP_TARGETS = DdTargets.all_text()
    DRAG_TARGET = DdTargets.TEXT
    ICON = ICONS['text']

    def __init__(self, obj):
        super(ClipText, self).__init__(obj)
        self._type = _("Text")
        if isinstance(self._obj, bytes):
            self._pickle = str(self._obj, "utf-8")
        else:
            self._pickle = self._obj
        self.refresh()

    def refresh(self):
        self._title = _("Text")
        if isinstance(self._obj, bytes):
            self._value = str(self._obj, "utf-8")
        else:
            self._value = self._obj


class ClipMediaObj(ClipHandleWrapper):

    DROP_TARGETS = [DdTargets.MEDIAOBJ]
    DRAG_TARGET = DdTargets.MEDIAOBJ
    ICON = ICONS["media"]

    def __init__(self, obj):
        super(ClipMediaObj, self).__init__(obj)
        self._type = _("Media")
        self._objclass = 'Media'
        self.refresh()

    def refresh(self):
        if self._handle:
            obj = clipdb.get_media_from_handle(self._handle)
            if obj:
                self._title = obj.get_description()
                self._value = obj.get_path()


class ClipMediaRef(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.MEDIAREF]
    DRAG_TARGET = DdTargets.MEDIAREF
    ICON = LINK_PIC

    def __init__(self, obj):
        super(ClipMediaRef, self).__init__(obj)
        self._type = _("Media ref")
        self.refresh()

    def refresh(self):
        if self._obj:
            base = clipdb.get_media_from_handle(
                self._obj.get_reference_handle())
            if base:
                self._title = base.get_description()
                self._value = base.get_path()


class ClipPersonRef(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.PERSONREF]
    DRAG_TARGET = DdTargets.PERSONREF
    ICON = LINK_PIC

    def __init__(self, obj):
        super(ClipPersonRef, self).__init__(obj)
        self._type = _("Person ref")
        self.refresh()

    def refresh(self):
        if self._obj:
            person = clipdb.get_person_from_handle(
                self._obj.get_reference_handle())
            if person:
                self._title = self._obj.get_relation()
                self._value = person.get_primary_name().get_name()


class ClipChildRef(ClipObjWrapper):

    DROP_TARGETS = [DdTargets.CHILDREF]
    DRAG_TARGET = DdTargets.CHILDREF
    ICON = LINK_PIC

    def __init__(self, obj):
        super(ClipChildRef, self).__init__(obj)
        self._type = _("Child ref")
        self.refresh()

    def refresh(self):
        if self._obj:
            person = clipdb.get_person_from_handle(
                self._obj.get_reference_handle())
            if person:
                frel = str(self._obj.get_father_relation())
                mrel = str(self._obj.get_mother_relation())
                self._title = _('%(frel)s %(mrel)s') % {'frel': frel,
                                                        'mrel': mrel}
                self._value = person.get_primary_name().get_name()


class ClipPersonLink(ClipHandleWrapper):

    DROP_TARGETS = [DdTargets.PERSON_LINK]
    DRAG_TARGET = DdTargets.PERSON_LINK
    ICON = ICONS["person"]

    def __init__(self, obj):
        super(ClipPersonLink, self).__init__(obj)
        self._type = _("Person")
        self._objclass = 'Person'
        self.refresh()

    def refresh(self):
        if self._handle:
            person = clipdb.get_person_from_handle(self._handle)
            if person:
                self._title = person.gramps_id
                self._value = person.get_primary_name().get_name()


class ClipFamilyLink(ClipHandleWrapper):

    DROP_TARGETS = [DdTargets.FAMILY_LINK]
    DRAG_TARGET = DdTargets.FAMILY_LINK
    ICON = ICONS["family"]

    def __init__(self, obj):
        super(ClipFamilyLink, self).__init__(obj)
        self._type = _("Family")
        self._objclass = 'Family'
        self.refresh()

    def refresh(self):
        from gramps.gen.simple import SimpleAccess
        if self._handle:
            family = clipdb.get_family_from_handle(self._handle)
            if family:
                _sa = SimpleAccess(clipdb)
                self._title = family.gramps_id
                self._value = _sa.describe(family)


class ClipSourceLink(ClipHandleWrapper):

    DROP_TARGETS = [DdTargets.SOURCE_LINK]
    DRAG_TARGET = DdTargets.SOURCE_LINK
    ICON = ICONS["source"]

    def __init__(self, obj):
        super(ClipSourceLink, self).__init__(obj)
        self._type = _("Source")
        self._objclass = 'Source'
        self.refresh()

    def refresh(self):
        if self._handle:
            source = clipdb.get_source_from_handle(self._handle)
            if source:
                self._title = source.get_gramps_id()
                self._value = source.get_title()


class ClipRepositoryLink(ClipHandleWrapper):

    DROP_TARGETS = [DdTargets.REPO_LINK]
    DRAG_TARGET = DdTargets.REPO_LINK
    ICON = ICONS["repository"]

    def __init__(self, obj):
        super(ClipRepositoryLink, self).__init__(obj)
        self._type = _("Repository")
        self._objclass = 'Repository'
        self.refresh()

    def refresh(self):
        if self._handle:
            source = clipdb.get_repository_from_handle(self._handle)
            if source:
                self._title = str(source.get_type())
                self._value = source.get_name()

#-------------------------------------------------------------------------
#
# Wrapper classes to deal with lists of objects
#
#-------------------------------------------------------------------------


class ClipDropList:
    DROP_TARGETS = [DdTargets.LINK_LIST]
    DRAG_TARGET = None

    def __init__(self, obj_list):
        # ('link-list', id, (('person-link', handle),
        #                    ('person-link', handle), ...), 0)
        self._obj_list = pickle.loads(obj_list)

    def get_objects(self):
        list_type, _id, handles, timestamp = self._obj_list
        retval = []
        for (target, handle) in handles:
            _class = map2class(target)
            if _class:
                obj = _class(pickle.dumps((target, _id, handle, timestamp)))
                if obj:
                    retval.append(obj)
        return retval


class ClipDropRawList(ClipDropList):
    DROP_TARGETS = [DdTargets.RAW_LIST]
    DRAG_TARGET = None

    def __init__(self, obj_list):
        # ('raw-list', id, (ClipObject, ClipObject, ...), 0)
        self._obj_list = pickle.loads(obj_list)

    def get_objects(self):
        retval = []
        for item in self._obj_list:
            if item is None:
                continue
            target = pickle.loads(item)[0]
            _class = map2class(target)
            if _class:
                obj = _class(item)
                if obj:
                    retval.append(obj)
        return retval


class ClipDropHandleList(ClipDropList):
    DROP_TARGETS = [DdTargets.HANDLE_LIST]
    DRAG_TARGET = None

    def __init__(self, obj_list):
        # incoming:
        # ('handle-list', id, (('Person', '2763526751235'),
        #                      ('Source', '3786234743978'), ...), 0)
        self._obj_list = pickle.loads(obj_list)

    def get_objects(self):
        retval = []
        for (objclass, handle) in self._obj_list:
            _class = obj2class(objclass)
            target = obj2target(objclass).name()
            # outgoing:
            # (drag_type, idval, self._handle, val) = pickle.loads(self._obj)
            data = (target, id(self), handle, 0)
            obj = _class(pickle.dumps(data))
            retval.append(obj)
        return retval

# FIXME: add family


#-------------------------------------------------------------------------
#
# ClipboardListModel class
#
#-------------------------------------------------------------------------
class ClipboardListModel(Gtk.ListStore):

    def __init__(self):
        Gtk.ListStore.__init__(self,
                               str,     # 0: object type
                               object,  # 1: object
                               object,  # 2: tooltip callback
                               str,     # 3: type
                               str,     # 4: value
                               str,     # 5: unique database id (dbid)
                               str)     # 6: db name (may be old)


#-------------------------------------------------------------------------
#
# ClipboardListView class
#
#-------------------------------------------------------------------------
class ClipboardListView:

    LOCAL_DRAG_TYPE = 'MY_TREE_MODEL_ROW'
    LOCAL_DRAG_ATOM_TYPE = Gdk.atom_intern(LOCAL_DRAG_TYPE, False)
    LOCAL_DRAG_TARGET = (LOCAL_DRAG_ATOM_TYPE, Gtk.TargetFlags.SAME_WIDGET, 0)

    def __init__(self, dbstate, widget):

        self._widget = widget
        self.dbstate = dbstate
        self.dbstate.connect('database-changed', self.database_changed)
        self.database_changed(dbstate.db)

        self._target_type_to_wrapper_class_map = {}
        self._previous_drop_time = 0

        # Create the tree columns
        self._col1 = Gtk.TreeViewColumn(_("Type"))
        self._col1.set_property("resizable", True)
        self._col1.set_sort_column_id(0)
        self._col2 = Gtk.TreeViewColumn(_("Title"))
        self._col2.set_property("resizable", True)
        self._col2.set_sort_column_id(3)
        self._col3 = Gtk.TreeViewColumn(_("Value"))
        self._col3.set_property("resizable", True)
        self._col3.set_sort_column_id(4)
        self._col4 = Gtk.TreeViewColumn(_("Family Tree"))
        self._col4.set_property("resizable", True)
        self._col4.set_sort_column_id(6)

        # Add columns
        self._widget.append_column(self._col1)
        self._widget.append_column(self._col2)
        self._widget.append_column(self._col3)
        self._widget.append_column(self._col4)

        # Create cell renders
        self._col1_cellpb = Gtk.CellRendererPixbuf()
        self._col1_cell = Gtk.CellRendererText()
        self._col2_cell = Gtk.CellRendererText()
        self._col3_cell = Gtk.CellRendererText()
        self._col4_cell = Gtk.CellRendererText()

        # Add cells to view
        self._col1.pack_start(self._col1_cellpb, False)
        self._col1.pack_start(self._col1_cell, True)
        self._col2.pack_start(self._col2_cell, True)
        self._col3.pack_start(self._col3_cell, True)
        self._col4.pack_start(self._col4_cell, True)

        # Setup the cell data callback funcs
        self._col1.set_cell_data_func(self._col1_cellpb, self.object_pixbuf)
        self._col1.set_cell_data_func(self._col1_cell, self.object_type)
        self._col2.set_cell_data_func(self._col2_cell, self.object_title)
        self._col3.set_cell_data_func(self._col3_cell, self.object_value)
        self._col4.set_cell_data_func(self._col4_cell, self.get_dbname)

        # Set the column that inline searching will use.
        self._widget.set_enable_search(True)
        #self._widget.set_search_column(3)

        targ_data = DdTargets.all_dtype()
        tglist = Gtk.TargetList.new([])
        tglist.add(ClipboardListView.LOCAL_DRAG_TARGET[0],
                   ClipboardListView.LOCAL_DRAG_TARGET[1],
                   ClipboardListView.LOCAL_DRAG_TARGET[2])
        for _tg in targ_data:
            tglist.add(_tg.atom_drag_type, _tg.target_flags, _tg.app_id)
        self._widget.enable_model_drag_dest([], Gdk.DragAction.COPY)
        #TODO GTK3: workaround here for bug
        # https://bugzilla.gnome.org/show_bug.cgi?id=680638
        self._widget.drag_dest_set_target_list(tglist)
        #self._widget.drag_dest_set(Gtk.DestDefaults.ALL, targ_data,
        #                            Gdk.DragAction.COPY)

        self._widget.connect('drag-data-get', self.object_drag_data_get)
        self._widget.connect('drag-begin', self.object_drag_begin)
        self._widget.connect_after('drag-begin', self.object_after_drag_begin)
        self._widget.connect('drag-data-received',
                             self.object_drag_data_received)
        self._widget.connect('drag-end', self.object_drag_end)

        self.register_wrapper_classes()

    def database_changed(self, db):
        if not db.is_open():
            return
        global clipdb
        clipdb = db
        # Note: delete event is emitted before the delete, so checking
        #        if valid on this is useless !
        db_signals = (
            'person-update',
            'person-rebuild',
            'family-update',
            'family-rebuild',
            'source-update',
            'source-rebuild',
            'place-update',
            'place-rebuild',
            'media-update',
            'media-rebuild',
            'event-update',
            'event-rebuild',
            'repository-update',
            'repository-rebuild',
            'note-rebuild')

        for signal in db_signals:
            clipdb.connect(signal, self.refresh_objects)

        clipdb.connect('person-delete',
                       gen_del_obj(self.delete_object, 'person-link'))
        clipdb.connect('person-delete',
                       gen_del_obj(self.delete_object_ref, 'personref'))
        clipdb.connect('person-delete',
                       gen_del_obj(self.delete_object_ref, 'childref'))
        clipdb.connect('source-delete',
                       gen_del_obj(self.delete_object, 'source-link'))
        clipdb.connect('source-delete',
                       gen_del_obj(self.delete_object_ref, 'srcref'))
        clipdb.connect('repository-delete',
                       gen_del_obj(self.delete_object, 'repo-link'))
        clipdb.connect('event-delete',
                       gen_del_obj(self.delete_object, 'pevent'))
        clipdb.connect('event-delete',
                       gen_del_obj(self.delete_object_ref, 'eventref'))
        clipdb.connect('media-delete',
                       gen_del_obj(self.delete_object, 'media'))
        clipdb.connect('media-delete',
                       gen_del_obj(self.delete_object_ref, 'mediaref'))
        clipdb.connect('place-delete',
                       gen_del_obj(self.delete_object, 'place-link'))
        clipdb.connect('note-delete',
                       gen_del_obj(self.delete_object, 'note-link'))
        # family-delete not needed, cannot be dragged!

        self.refresh_objects()

    def refresh_objects(self, dummy=None):
        model = self._widget.get_model()

        if model:
            for _ob in model:
                if not _ob[1].is_valid():
                    model.remove(_ob.iter)
                else:
                    _ob[1].refresh()
                    _ob[4] = _ob[1].get_value()  # Force listview to update

    def delete_object(self, handle_list, link_type):
        model = self._widget.get_model()

        if model:
            for _ob in model:
                if _ob[0] == link_type:
                    data = pickle.loads(_ob[1]._obj)
                    if data[2] in handle_list:
                        model.remove(_ob.iter)

    def delete_object_ref(self, handle_list, link_type):
        model = self._widget.get_model()

        if model:
            for _ob in model:
                if _ob[0] == link_type:
                    data = _ob[1]._obj.get_reference_handle()
                    if data in handle_list:
                        model.remove(_ob.iter)

    # Method to manage the wrapper classes.

    def register_wrapper_classes(self):
        self.register_wrapper_class(ClipAddress)
        self.register_wrapper_class(ClipLocation)
        self.register_wrapper_class(ClipEvent)
        self.register_wrapper_class(ClipPlace)
        self.register_wrapper_class(ClipEventRef)
        self.register_wrapper_class(ClipPlaceRef)
        self.register_wrapper_class(ClipRepoRef)
        self.register_wrapper_class(ClipFamilyEvent)
        self.register_wrapper_class(ClipUrl)
        self.register_wrapper_class(ClipAttribute)
        self.register_wrapper_class(ClipFamilyAttribute)
        self.register_wrapper_class(ClipName)
        self.register_wrapper_class(ClipPlaceName)
        self.register_wrapper_class(ClipRepositoryLink)
        self.register_wrapper_class(ClipMediaObj)
        self.register_wrapper_class(ClipMediaRef)
        self.register_wrapper_class(ClipSourceLink)
        self.register_wrapper_class(ClipCitation)
        self.register_wrapper_class(ClipPersonLink)
        self.register_wrapper_class(ClipFamilyLink)
        self.register_wrapper_class(ClipDropList)
        self.register_wrapper_class(ClipDropRawList)
        self.register_wrapper_class(ClipDropHandleList)
        self.register_wrapper_class(ClipPersonRef)
        self.register_wrapper_class(ClipChildRef)
        self.register_wrapper_class(ClipText)
        self.register_wrapper_class(ClipNote)

    def register_wrapper_class(self, wrapper_class):
        for drop_target in wrapper_class.DROP_TARGETS:
            self._target_type_to_wrapper_class_map[
                drop_target.drag_type] = wrapper_class

    # Methods for rendering the cells.

    def object_pixbuf(self, column, cell, model, node, user_data=None):
        _ob = model.get_value(node, 1)
        if _ob._dbid is not None and _ob._dbid != self.dbstate.db.get_dbid():
            if isinstance(_ob.__class__.UNAVAILABLE_ICON, str):
                cell.set_property('icon-name',
                                  _ob.__class__.UNAVAILABLE_ICON)
            else:
                cell.set_property('pixbuf',
                                  _ob.__class__.UNAVAILABLE_ICON)
        else:
            cell.set_property('pixbuf', _ob.__class__.ICON)

    def object_type(self, column, cell, model, node, user_data=None):
        _ob = model.get_value(node, 1)
        cell.set_property('text', _ob.get_type())

    def object_title(self, column, cell, model, node, user_data=None):
        _ob = model.get_value(node, 1)
        cell.set_property('text', _ob.get_title())

    def object_value(self, column, cell, model, node, user_data=None):
        _ob = model.get_value(node, 1)
        cell.set_property('text', _ob.get_value())

    def get_dbname(self, column, cell, model, node, user_data=None):
        _ob = model.get_value(node, 1)
        cell.set_property('text', _ob.get_dbname())

    # handlers for the drag and drop events.

    def on_object_select_row(self, obj):
        tree_selection = self._widget.get_selection()
        model, paths = tree_selection.get_selected_rows()
        if len(paths) > 1:
            targets = [(DdTargets.RAW_LIST.atom_drag_type,
                        Gtk.TargetFlags.SAME_WIDGET, 0),
                       ClipboardListView.LOCAL_DRAG_TARGET]
        else:
            targets = [ClipboardListView.LOCAL_DRAG_TARGET]
        for path in paths:
            node = model.get_iter(path)
            if node is not None:
                _ob = model.get_value(node, 1)
                targets += [target.target_data_atom()
                            for target in _ob.__class__.DROP_TARGETS]

        #TODO GTK3: workaround here for bug
        # https://bugzilla.gnome.org/show_bug.cgi?id=680638
        self._widget.enable_model_drag_source(
            Gdk.ModifierType.BUTTON1_MASK, [],
            Gdk.DragAction.COPY | Gdk.DragAction.MOVE)
        tglist = Gtk.TargetList.new([])
        for _tg in targets:
            tglist.add(_tg[0], _tg[1], _tg[2])
        self._widget.drag_source_set_target_list(tglist)

    def object_drag_begin(self, widget, drag_context):
        """ Handle the beginning of a drag operation. """
        pass

    def object_after_drag_begin(self, widget, drag_context):
        tree_selection = widget.get_selection()
        model, paths = tree_selection.get_selected_rows()
        if len(paths) == 1:
            path = paths[0]
            node = model.get_iter(path)
            target = model.get_value(node, 0)
            if target == "TEXT":
                layout = widget.create_pango_layout(model.get_value(node, 4))
                layout.set_alignment(Pango.Alignment.CENTER)
                width, height = layout.get_pixel_size()
                surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
                                             width, height)
                ctx = cairo.Context(surface)
                style_ctx = self._widget.get_style_context()
                Gtk.render_background(style_ctx, ctx, 0, 0, width, height)
                ctx.save()
                Gtk.render_layout(style_ctx, ctx, 0, 0 , layout)
                ctx.restore()
                Gtk.drag_set_icon_surface(drag_context, surface)
            else:
                try:
                    if map2class(target):
                        Gtk.drag_set_icon_pixbuf(drag_context,
                                                 map2class(target).ICON, 0, 0)
                except:
                    Gtk.drag_set_icon_default(drag_context)

    def object_drag_end(self, widget, drag_context):
        """ Handle the end of a drag operation. """
        pass

    def object_drag_data_get(self, widget, context, sel_data, info, time):
        tree_selection = widget.get_selection()
        model, paths = tree_selection.get_selected_rows()
        if hasattr(context, "targets"):
            tgs = context.targets
        else:
            tgs = context.list_targets()
        if len(paths) == 1:
            path = paths[0]
            node = model.get_iter(path)
            _ob = model.get_value(node, 1)
            if model.get_value(node, 0) == 'TEXT':
                sel_data.set_text(_ob._value, -1)
            else:
                sel_data.set(tgs[0], 8, _ob.pack())
        elif len(paths) > 1:
            raw_list = []
            for path in paths:
                node = model.get_iter(path)
                _ob = model.get_value(node, 1)
                raw_list.append(_ob.pack())
            sel_data.set(tgs[0], 8, pickle.dumps(raw_list))

    def object_drag_data_received(self, widget, context, x, y, selection, info,
                                  time, title=None, value=None, dbid=None,
                                  dbname=None):
        model = widget.get_model()
        if hasattr(selection, "data"):
            sel_data = selection.data
        else:
            sel_data = selection.get_data()  # GtkSelectionData
        # In Windows time is always zero. Until that is fixed, use the seconds
        # of the local time to filter out double drops.
        real_time = strftime("%S")

        # There is a strange bug that means that if there is a selection
        # in the list we get multiple drops of the same object. Luckily
        # the time values are the same so we can drop all but the first.
        if (real_time == self._previous_drop_time) and (time != -1):
            return None

        # Find a wrapper class
        possible_wrappers = []
        if mac():
            # context is empty on mac due to a bug, work around this
            # Note that this workaround code works fine in linux too as
            # we know very well inside of Gramps what sel_data can be, so
            # we can anticipate on it, instead of letting the wrapper handle
            # it. This is less clean however !
            # See http://www.gramps-project.org/bugs/view.php?id=3089 for
            # an explaination of why this is required.
            dragtype = None
            try:
                dragtype = pickle.loads(sel_data)[0]
            except pickle.UnpicklingError as msg :
                # not a pickled object, probably text
                if isinstance(sel_data, str):
                    dragtype = DdTargets.TEXT.drag_type
            if dragtype in self._target_type_to_wrapper_class_map:
                possible_wrappers = [dragtype]
        else:
            if hasattr(context, "targets"):
                tgs = context.targets
            else:
                tgs = [atm.name() for atm in context.list_targets()]
            possible_wrappers = [
                target for target in tgs
                if target in self._target_type_to_wrapper_class_map]

        if not possible_wrappers:
            # No wrapper for this class
            return None

        # Just select the first match.
        wrapper_class = self._target_type_to_wrapper_class_map[
            str(possible_wrappers[0])]
        try:
            _ob = wrapper_class(sel_data)
            if title:
                _ob._title = title
            if value:
                _ob._value = value
            if dbid:
                _ob._dbid = dbid
            if dbname:
                _ob._dbname = dbname

            # If this was a ClipPersonLink with a list for a handle, we don't
            # want it.  Can happen in People Treeview with attemp to drag last
            # name group.
            if (isinstance(_ob, ClipHandleWrapper) and
                    isinstance(_ob._handle, list)):
                return None
            # If the wrapper object is a subclass of ClipDropList then
            # the drag data was a list of objects and we need to decode
            # all of them.
            if isinstance(_ob, ClipDropList):
                o_list = _ob.get_objects()
            else:
                o_list = [_ob]
            for _ob in o_list:
                if _ob.__class__.DRAG_TARGET is None:
                    continue
                data = [_ob.__class__.DRAG_TARGET.drag_type, _ob, None,
                        _ob._type, _ob._value, _ob._dbid, _ob._dbname]
                contains = model_contains(model, data)
                if (contains and not
                        ((context.action if hasattr(context, "action") else
                          context.get_actions()) & Gdk.DragAction.MOVE)):
                    continue
                drop_info = widget.get_dest_row_at_pos(x, y)
                if drop_info:
                    path, position = drop_info
                    node = model.get_iter(path)
                    if position == Gtk.TreeViewDropPosition.BEFORE or \
                       position == Gtk.TreeViewDropPosition.INTO_OR_BEFORE:

                        model.insert_before(node, data)
                    else:
                        model.insert_after(node, data)
                else:
                    model.append(data)

            # FIXME: there is one bug here: if you multi-select and drop
            # on self, then it moves the first, and copies the rest.

            if ((context.action if hasattr(context, "action") else
                 context.get_actions()) & Gdk.DragAction.MOVE):
                context.finish(True, True, time)

            # remember time for double drop workaround.
            self._previous_drop_time = real_time
            return o_list
        except EOFError:
            return None

    # proxy methods to provide access to the real widget functions.

    def set_model(self, model=None):
        self._widget.set_model(model)
        self._widget.get_selection().connect('changed',
                                             self.on_object_select_row)
        self._widget.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

    def get_model(self):
        return self._widget.get_model()

    def get_selection(self):
        return self._widget.get_selection()

    def set_search_column(self, col):
        return self._widget.set_search_column(col)


#-------------------------------------------------------------------------
#
# ClipboardWindow class
#
#-------------------------------------------------------------------------
class ClipboardWindow(ManagedWindow):
    """
        The Clipboard provides a temporary area to hold objects that can
        be reused accross multiple Person records. The pad provides a window
        onto which objects can be dropped and then dragged into new Person
        dialogs. The objects are stored as the pickles that are built by the
        origininating widget. The objects are only unpickled in order to
        provide the text in the display.

        No attempt is made to ensure that any references contained within
        the pickles are valid. Because the pad extends the life time of drag
        and drop objects, it is possible that references that were valid
        when an object is copied to the pad are invalid by the time they
        are dragged to a new Person. For this reason, using the pad places
        a responsibility on all '_drag_data_received' methods to check the
        references of objects before attempting to use them.
        """

    # Class attribute used to hold the content of the Clipboard.
    # A class attribute is used so that the content
    # it preserved even when the Clipboard window is closed.
    # As there is only ever one Clipboard we do not need to
    # maintain a list of these.
    otree = None

    def __init__(self, dbstate, uistate):
        """Initialize the ClipboardWindow class, and display the window"""

        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.dbstate = dbstate

        self.database_changed(self.dbstate.db)
        self.dbstate.connect('database-changed', self.database_changed)

        self.top = Glade()
        self.set_window(self.top.toplevel, None, None, msg=_("Clipboard"))
        self.setup_configs('interface.clipboard', 500, 300)

        self.clear_all_btn = self.top.get_object("btn_clear_all")
        self.clear_btn = self.top.get_object("btn_clear")
        objectlist = self.top.get_object('objectlist')
        mtv = MultiTreeView(self.dbstate, self.uistate, _("Clipboard"))
        scrolledwindow = self.top.get_object('scrolledwindow86')
        scrolledwindow.remove(objectlist)
        scrolledwindow.add(mtv)
        self.object_list = ClipboardListView(self.dbstate, mtv)
        self.object_list.get_selection().connect(
            'changed', self.set_clear_btn_sensitivity)
        self.object_list.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.set_clear_btn_sensitivity(sel=self.object_list.get_selection())

        if not ClipboardWindow.otree:
            ClipboardWindow.otree = ClipboardListModel()

        self.set_clear_all_btn_sensitivity(treemodel=ClipboardWindow.otree)
        ClipboardWindow.otree.connect('row-deleted',
                                      self.set_clear_all_btn_sensitivity)
        ClipboardWindow.otree.connect('row-inserted',
                                      self.set_clear_all_btn_sensitivity)

        self.object_list.set_model(ClipboardWindow.otree)

        #Database might have changed, objects might have been removed,
        #we need to reevaluate if all data is valid
        self.object_list.refresh_objects()

        self.top.connect_signals({
            "on_close_clipboard" : self.close,
            "on_clear_clicked": self.on_clear_clicked,
            "on_help_clicked": self.on_help_clicked})

        self.clear_all_btn.connect_object('clicked', Gtk.ListStore.clear,
                                          ClipboardWindow.otree)
        self.db.connect('database-changed',
                        lambda x: ClipboardWindow.otree.clear())

        self.show()

    def build_menu_names(self, obj):
        return (_('Clipboard'), None)

    def database_changed(self, database):
        self.db = database

    def set_clear_all_btn_sensitivity(self, treemodel=None,
                                      path=None, node=None, user_param1=None):
        if treemodel:
            self.clear_all_btn.set_sensitive(True)
        else:
            self.clear_all_btn.set_sensitive(False)

    def set_clear_btn_sensitivity(self, sel=None, user_param1=None):
        if sel.count_selected_rows() == 0:
            self.clear_btn.set_sensitive(False)
        else:
            self.clear_btn.set_sensitive(True)

    def on_help_clicked(self, obj):
        """Display the relevant portion of Gramps manual"""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def on_clear_clicked(self, obj):
        """Deletes the selected object from the object list"""
        selection = self.object_list.get_selection()
        model, paths = selection.get_selected_rows()
        paths.reverse()
        for path in paths:
            node = model.get_iter(path)
            if node:
                model.remove(node)


#-------------------------------------------------------------------------
#
# MultiTreeView class
#
#-------------------------------------------------------------------------
class MultiTreeView(Gtk.TreeView):
    '''
    TreeView that captures mouse events to make drag and drop work properly
    '''
    def __init__(self, dbstate, uistate, title=None):
        self.dbstate = dbstate
        self.uistate = uistate
        self.title = title if title else _("Clipboard")
        Gtk.TreeView.__init__(self)
        self.connect('button_press_event', self.on_button_press)
        self.connect('button_release_event', self.on_button_release)
        self.connect('drag-end', self.on_drag_end)
        self.connect('key_press_event', self.key_press_event)
        self.defer_select = False

    def key_press_event(self, widget, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Delete:
                model, paths = self.get_selection().get_selected_rows()
                # reverse, to delete from the end
                paths.sort(key=lambda x: -x[0])
                for path in paths:
                    try:
                        node = model.get_iter(path)
                    except:
                        node = None
                    if node:
                        model.remove(node)
                return True

    def on_button_press(self, widget, event):
        # Here we intercept mouse clicks on selected items so that we can
        # drag multiple items without the click selecting only one
        target = self.get_path_at_pos(int(event.x), int(event.y))
        if is_right_click(event):
            selection = widget.get_selection()
            store, paths = selection.get_selected_rows()
            if not paths:
                return
            tpath = paths[0] if paths else None
            node = store.get_iter(tpath) if tpath else None
            _ob = None
            if node:
                _ob = store.get_value(node, 1)
            self.newmenu = Gtk.Menu()
            popup = self.newmenu
            # ---------------------------
            if _ob:
                objclass, handle = _ob._objclass, _ob._handle
            else:
                objclass, handle = None, None
            if obj2class(objclass):
                if self.dbstate.db.method('has_%s_handle', objclass)(handle):
                    menu_item = Gtk.MenuItem(
                        label=_("the object|See %s details") %
                        glocale.trans_objclass(objclass))
                    menu_item.connect(
                        "activate",
                        lambda widget: self.edit_obj(objclass, handle))
                    popup.append(menu_item)
                    menu_item.show()
                    # ---------------------------
                    menu_item = Gtk.MenuItem(
                        label=_("the object|Make %s active") %
                        glocale.trans_objclass(objclass))
                    menu_item.connect(
                        "activate", lambda widget:
                        self.uistate.set_active(handle, objclass))
                    popup.append(menu_item)
                    menu_item.show()
                # ---------------------------
                gids = set()
                for path in paths:
                    node = store.get_iter(path)
                    if node:
                        _ob = store.get_value(node, 1)
                        if _ob._objclass == objclass:
                            my_handle = _ob._handle
                            if self.dbstate.db.method('has_%s_handle',
                                                      objclass)(my_handle):
                                obj = self.dbstate.db.method(
                                    'get_%s_from_handle', objclass)(my_handle)
                                gids.add(obj.gramps_id)
                if gids:
                    menu_item = Gtk.MenuItem(
                        label=_("the object|Create Filter from %s "
                                "selected...") %
                        glocale.trans_objclass(objclass))
                    menu_item.connect("activate", lambda widget: make_filter(
                        self.dbstate, self.uistate,
                        objclass, gids, title=self.title))
                    popup.append(menu_item)
                    menu_item.show()
            if popup.get_children():  # Show the popup menu:
                popup.popup(None, None, None, None, 3, event.time)
            return True
        elif event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            model, paths = self.get_selection().get_selected_rows()
            for path in paths:
                node = model.get_iter(path)
                if node is not None:
                    _ob = model.get_value(node, 1)
                    objclass = _ob._objclass
                    handle = _ob._handle
                    self.edit_obj(objclass, handle)
            return True
        # otherwise:
        if (target and
                event.type == Gdk.EventType.BUTTON_PRESS and
                self.get_selection().path_is_selected(target[0]) and
                no_match_primary_mask(event.get_state(),
                                      Gdk.ModifierType.SHIFT_MASK)):
            # disable selection
            self.get_selection().set_select_function(
                lambda *ignore: False, None)
            self.defer_select = target[0]

    def on_button_release(self, widget, event):
        # re-enable selection
        self.get_selection().set_select_function(lambda *ignore: True, None)

        target = self.get_path_at_pos(int(event.x), int(event.y))
        if (self.defer_select and target and
                self.defer_select == target[0] and not
                (event.x == 0 and
                 event.y == 0)):  # certain drag and drop
            self.set_cursor(target[0], target[1], False)

        self.defer_select = False

    def on_drag_end(self, widget, event):
        # re-enable selection
        self.get_selection().set_select_function(lambda *ignore: True, None)
        self.defer_select = False

    def edit_obj(self, objclass, handle):
        from .editors import (EditPerson, EditEvent, EditFamily, EditSource,
                              EditPlace, EditRepository, EditNote, EditMedia,
                              EditCitation)
        if obj2class(objclass):  # make sure it is an editable object
            if self.dbstate.db.method('has_%s_handle', objclass)(handle):
                g_object = self.dbstate.db.method(
                    'get_%s_from_handle', objclass)(handle)
                try:
                    locals()['Edit' + objclass](
                        self.dbstate, self.uistate, [], g_object)
                except WindowActiveError:
                    pass


def short(val, size=60):
    if len(val) > size:
        return "%s..." % val[0:size]
    return val


def place_title(db, event):
    return place_displayer.display_event(db, event)


def gen_del_obj(func, t):
    return lambda l : func(l, t)


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def Clipboard(database, person, callback, parent=None):
    ClipboardWindow(database, parent)
