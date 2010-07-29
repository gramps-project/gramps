#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import cPickle as pickle
import os
from xml.sax.saxutils import escape
from time import strftime as strftime

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
from gtk.gdk import ACTION_COPY, BUTTON1_MASK, ACTION_MOVE

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import config
import gen.lib
import TreeTips
import DateHandler
import GrampsDisplay
import ManagedWindow
from gen.ggettext import sgettext as _
from constfunc import mac
from glade import Glade
from DdTargets import DdTargets

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Navigation' % const.URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Using_the_Clipboard')

#-------------------------------------------------------------------------
#
# icons used in the object listing
#
#-------------------------------------------------------------------------

_stock_image = os.path.join(const.IMAGE_DIR,'stock_link.png')
LINK_PIC = gtk.gdk.pixbuf_new_from_file(_stock_image)
ICONS = {}
for (name, file) in (
    ("media", "gramps-media.png"),
    ("note", "gramps-notes.png"),
    ("person", "gramps-person.png"),
    ("place", "gramps-place.png"),
    ('address', 'gramps-address.png'),
    ('attribute', 'gramps-attribute.png'),
    ('event', 'gramps-event.png'),
    ('family', 'gramps-family.png'),
    ('location', 'geo-place-link.png'),
    ('media', 'gramps-media.png'),
    ('name', 'geo-show-person.png'),
    ('repository', 'gramps-repository.png'),
    ('source', 'gramps-source.png'),
    ('text', 'gramps-font.png'),
    ('url', 'gramps-geo.png'),
    ):
    _image = os.path.join(const.IMAGE_DIR, '16x16', file)
    ICONS[name] = gtk.gdk.pixbuf_new_from_file(_image) 

#-------------------------------------------------------------------------
#
# wrapper classes to provide object specific listing in the ListView
#
#-------------------------------------------------------------------------

class ScratchPadWrapper(object):

    def __init__(self,dbstate, obj):
        dbstate.connect('database-changed', self.database_changed)
        self.database_changed(dbstate.db)
        self._obj = obj
        self._pickle = obj
        self._type  = _("Unknown")
        self._objclass = None
        self._handle = None
        self._title = _('Unavailable')
        self._value = _('Unavailable')

    def database_changed(self,db):
        self._db = db

    def get_type(self):
        return self._type

    def get_title(self):
        return self._title

    def get_value(self):
        return self._value

    def pack(self):
        return str(self._obj)

    def is_valid(self):
        return True

class ScratchPadGrampsTypeWrapper(ScratchPadWrapper):
        
    def __init__(self,dbstate, obj):
        ScratchPadWrapper.__init__(self,dbstate, obj)
        #unpack object
        (drag_type, idval, self._obj, val) = pickle.loads(obj)
        self._pickle = obj

    def pack(self):
        return self._pickle

    def is_valid(self):
        valid_func_map = {'Person': self._db.get_person_from_handle,
                          'Family': self._db.get_family_from_handle,
                          'Event':  self._db.get_event_from_handle,
                          'Place': self._db.get_place_from_handle,
                          'MediaObject': self._db.get_object_from_handle,
                          'Source': self._db.get_source_from_handle}

        for (classname, handle) in self._obj.get_referenced_handles_recursively():
            if classname in valid_func_map:
                if not valid_func_map[classname](handle):
                    return False
            
        return True


class ScratchPadAddress(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.ADDRESS]
    DRAG_TARGET  = DdTargets.ADDRESS
    ICON         = ICONS['address']
    
    def __init__(self,dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate, obj)
        self._type  = _("Address")
        self.reset()

    def reset(self):
        self._title = DateHandler.get_date(self._obj)
        self._value = "%s %s %s %s" % (self._obj.get_street(),self._obj.get_city(),
                                       self._obj.get_state(),self._obj.get_country())

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Address"),
            _("Date"), escape(DateHandler.get_date(self._obj)),
            _("Location"),
            escape(self._obj.get_street()),
            escape(self._obj.get_city()),
            escape(self._obj.get_state()),
            escape(self._obj.get_country()),
            escape(self._obj.get_postal_code()),
            _("Telephone"), escape(self._obj.get_phone()))
    
        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_reference_handle()
            psrc = self._db.get_source_from_handle(psrc_id)
            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Sources"),
                _("Name"),escape(short(psrc.get_title())))
            
        return s

class ScratchPadLocation(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.LOCATION]
    DRAG_TARGET  = DdTargets.LOCATION
    ICON         = ICONS['location']
    
    def __init__(self,dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate, obj)
        self._type  = _("Location")
        self._value = "%s %s %s" % (self._obj.get_city(),
                                    self._obj.get_state(),self._obj.get_country())

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\n"\
            "\t\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Location"),
            escape(self._obj.get_city()),
            escape(self._obj.get_state()),
            escape(self._obj.get_country()),
            escape(self._obj.get_postal_code()),
            _("Telephone"), escape(self._obj.get_phone()))

        return s

class ScratchPadEvent(ScratchPadWrapper):

    DROP_TARGETS = [DdTargets.EVENT]
    DRAG_TARGET  = DdTargets.EVENT
    ICON         = ICONS["event"]

    def __init__(self,dbstate, obj):
        ScratchPadWrapper.__init__(self,dbstate, obj)
        self._type  = _("Event")
        self._objclass = 'Event'
        self.reset()

    def reset(self):
        (drag_type, idval, self._handle, val) = pickle.loads(self._obj)
        value = self._db.get_event_from_handle(self._handle)
        if value:
            self._title = str(value.get_type())
            self._value = value.get_description()

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        # there  are several errors in the below which all cause gramps to 
        # crash
        
#        s = "<big><b>%s</b></big>\n\n"\
#            "\t<b>%s:</b>\t%s\n"\
#            "\t<b>%s:</b>\t%s\n"\
#            "\t<b>%s:</b>\t%s\n"\
#            "\t<b>%s:</b>\t%s\n"\
#            "\t<b>%s:</b>\t%s\n" % (
#            _("Event"),
#            _("Type"),escape(Utils.format_personal_event(self._obj.get_name())),
#            _("Date"),escape(DateHander.get_date(self._obj)),
#            _("Place"),escape(place_title(self._db,self._obj)),
#            _("Cause"),escape(self._obj.get_cause()),
#            _("Description"), escape(self._obj.get_description()))
#        if len(self._obj.get_source_references()) > 0:
#            psrc_ref = self._obj.get_source_references()[0]
#            psrc_id = psrc_ref.get_reference_handle()
#            psrc = self._db.get_source_from_handle(psrc_id)
#            s += "\n<big><b>%s</b></big>\n\n"\
#                "\t<b>%s:</b>\t%s\n" % (
#                _("Primary source"),
#                _("Name"),
#                escape(short(psrc.get_title())))
        s = ""
        return s

    def is_valid(self):
        data = pickle.loads(self._obj)
        handle = data[2]
        obj = self._db.get_event_from_handle(handle)
        if obj:
            return True
        return False

class ScratchPadPlace(ScratchPadWrapper):

    DROP_TARGETS = [DdTargets.PLACE_LINK]
    DRAG_TARGET  = DdTargets.PLACE_LINK
    ICON         = ICONS["place"]

    def __init__(self,dbstate, obj):
        ScratchPadWrapper.__init__(self,dbstate, obj)
        self._type  = _("Place")
        self._objclass = 'Place'
        self.reset()

    def reset(self):
        (drag_type, idval, self._handle, val) = pickle.loads(self._obj)
        value = self._db.get_place_from_handle(self._handle)
        if value:
            self._title = value.get_title()
            self._value = "" #value.get_description()

    def tooltip(self):
        return ""

    def is_valid(self):
        data = pickle.loads(self._obj)
        handle = data[2]
        obj = self._db.get_place_from_handle(handle)
        if obj:
            return True
        return False

class ScratchPadNote(ScratchPadWrapper):

    DROP_TARGETS = [DdTargets.NOTE_LINK]
    DRAG_TARGET  = DdTargets.NOTE_LINK
    ICON         = ICONS["note"]

    def __init__(self,dbstate, obj):
        ScratchPadWrapper.__init__(self,dbstate, obj)
        self._type  = _("Note")
        self._objclass = 'Note'
        self.reset()

    def reset(self):
        (drag_type, idval, self._handle, val) = pickle.loads(self._obj)
        value = self._db.get_note_from_handle(self._handle)
        if value:
            self._title = value.get_gramps_id()
            note = value.get().replace('\n', ' ')
            #String must be unicode for truncation to work for non ascii characters 
            note = unicode(note)
            if len(note) > 80:
                self._value = note[:80]+"..."
            else:
                self._value = note

    def tooltip(self):
        return ""

    def is_valid(self):
        data = pickle.loads(self._obj)
        handle = data[2]
        obj = self._db.get_note_from_handle(handle)
        if obj:
            return True
        return False

class ScratchPadFamilyEvent(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.FAMILY_EVENT]
    DRAG_TARGET  = DdTargets.FAMILY_EVENT
    ICON         = ICONS['family']
    
    def __init__(self, dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self, dbstate, obj)
        self._type  = _("Family Event")
        self.reset()

    def reset(self):
        self._title = str(self._obj.get_type())
        self._value = self._obj.get_description()

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Family Event"),
            _("Type"),escape(str(self._obj.get_type())),
            _("Date"),escape(DateHandler.get_date(self._obj)),
            _("Place"),escape(place_title(self._db, self._obj)),
            _("Cause"),escape(self._obj.get_cause()),
            _("Description"), escape(self._obj.get_description()))

        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_reference_handle()
            psrc = self._db.get_source_from_handle(psrc_id)

            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Primary source"),
                _("Name"),
                escape(short(psrc.get_title())))

        return s

class ScratchPadUrl(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.URL]
    DRAG_TARGET  = DdTargets.URL
    ICON         = ICONS['url']

    def __init__(self,dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self,dbstate, obj)
        self._type  = _("Url")
        self.reset()

    def reset(self):
        self._title = self._obj.get_path()
        self._value = self._obj.get_description()

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        return "<big><b>%s</b></big>\n\n"\
               "\t<b>%s:</b>\t%s\n"\
               "\t<b>%s:</b>\t%s" % (_("Url"),
                                     _("Path"),
                                     escape(self._obj.get_path()),
                                     _("Description"),
                                     escape(self._obj.get_description()))

class ScratchPadAttribute(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.ATTRIBUTE]
    DRAG_TARGET  = DdTargets.ATTRIBUTE
    ICON         = ICONS['attribute']

    def __init__(self, dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self, dbstate, obj)
        self._type  = _("Attribute")
        self.reset()

    def reset(self):
        self._title = str(self._obj.get_type())
        self._value = self._obj.get_value()

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % (_("Attribute"),
                                  _("Type"),
                                  escape(str(self._obj.get_type())),
                                  _("Value"),
                                  escape(self._obj.get_value()))
        
        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_reference_handle()
            psrc = self._db.get_source_from_handle(psrc_id)
            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Sources"),
                _("Name"),escape(short(psrc.get_title())))

        return s

class ScratchPadFamilyAttribute(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.FAMILY_ATTRIBUTE]
    DRAG_TARGET  = DdTargets.FAMILY_ATTRIBUTE
    ICON         = ICONS['attribute']

    def __init__(self, dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self, dbstate, obj)
        self._type  = _("Family Attribute")
        self.reset()

    def reset(self):
        self._title = str(self._obj.get_type())
        self._value = self._obj.get_value()

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % (_("Family Attribute"),
                                  _("Type"),
                                  escape(str(self._obj.get_type())),
                                  _("Value"),
                                  escape(self._obj.get_value()))
        
        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_reference_handle()
            psrc = self._db.get_source_from_handle(psrc_id)
            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Sources"),
                _("Name"),escape(short(psrc.get_title())))

        return s

class ScratchPadSourceRef(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.SOURCEREF]
    DRAG_TARGET  = DdTargets.SOURCEREF
    ICON         = LINK_PIC

    def __init__(self, dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self, dbstate, obj)
        self._type  = _("Source Reference")
        self.reset()

    def reset(self):
        base = self._db.get_source_from_handle(self._obj.get_reference_handle())
        if base:
            self._title = base.get_title()
            notelist = map(self._db.get_note_from_handle, self._obj.get_note_list())
            srctxtlist = [ note for note in notelist 
                           if note.get_type() == gen.lib.NoteType.SOURCE_TEXT]
            page = self._obj.get_page()
            if not page:
                page = _('not available|NA')
            text = ""
            if len(srctxtlist) > 0:
                text = " ".join(srctxtlist[0].get().split())
            #String must be unicode for truncation to work for non ascii characters 
                text = unicode(text)
                if len(text) > 60:
                    text =  text[:60]+"..."
            self._value = _("Volume/Page: %(pag)s -- %(sourcetext)s") % {
                                'pag'        : page,
                                'sourcetext' : text,
                                }

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        base = self._db.get_source_from_handle(self._obj.get_reference_handle())
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % \
            (_("Source Reference"),
             _("Title"),escape(base.get_title()),
             _("Page"), escape(self._obj.get_page()))

        return s

class ScratchPadRepoRef(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.REPOREF]
    DRAG_TARGET  = DdTargets.REPOREF
    ICON         = LINK_PIC

    def __init__(self, dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self, dbstate, obj)
        self._type  = _("Repository Reference")
        self.reset()

    def reset(self):
        base = self._db.get_repository_from_handle(self._obj.ref)
        if base:
            self._title = base.get_name()
            self._value = str(base.get_type())

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        base = self._db.get_repository_from_handle(self._obj.get_reference_handle())
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % (
            _("Repository Reference"),
            _("Name"),escape(base.get_name()),
            _("Call Number"), escape(self._obj.get_call_number()),
            _("Media Type"), escape(self._obj.get_media_type().__str__()))

        return s

class ScratchPadEventRef(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.EVENTREF]
    DRAG_TARGET  = DdTargets.EVENTREF
    ICON         = LINK_PIC

    def __init__(self, dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self, dbstate, obj)
        self._type  = _("Event Reference")
        self.reset()

    def reset(self):
        base = self._db.get_event_from_handle(self._obj.ref)
        if base:
            self._title = base.get_description()
            self._value = str(base.get_type())

    def tooltip(self):
        return ""

class ScratchPadName(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.NAME]
    DRAG_TARGET  = DdTargets.NAME
    ICON         = ICONS['name']

    def __init__(self, dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self, dbstate, obj)
        self._type  = _("Name")
        self.reset()

    def reset(self):
        self._title = self._obj.get_name()
        self._value = str(self._obj.get_type())

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Name"),
            _("Name"),escape(self._obj.get_name()),
            _("Call Name"),escape(self._obj.get_call_name()),
            _("Given"),escape(self._obj.get_first_name()),
            _("Family"),escape(self._obj.get_surname()),
            _("Patronymic"),escape(self._obj.get_patronymic()),
            _("Prefix"),escape(self._obj.get_surname_prefix()),
            _("Person|Title"),escape(self._obj.get_title()),
            _("Suffix"),escape(self._obj.get_suffix()),
            _("Type"),escape(self._obj.get_type().__str__()),
            )

        if len(self._obj.get_source_references()) > 0:
            psrc_ref = self._obj.get_source_references()[0]
            psrc_id = psrc_ref.get_reference_handle()
            psrc = self._db.get_source_from_handle(psrc_id)

            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Primary source"),
                _("Name"),
                escape(short(psrc.get_title())))

        return s

class ScratchPadText(ScratchPadWrapper):

    DROP_TARGETS = DdTargets.all_text()
    DRAG_TARGET  = DdTargets.TEXT
    ICON         = ICONS['text']

    def __init__(self, dbstate, obj):
        ScratchPadWrapper.__init__(self, dbstate, obj)
        self._type  = _("Text")
        self._title = ""
        self._value = self._obj
        self._pickle = self._obj

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        return "<big><b>%s</b></big>\n"\
               "%s" % (_("Text"),
                       escape(self._obj))

class ScratchMediaObj(ScratchPadWrapper):

    DROP_TARGETS = [DdTargets.MEDIAOBJ]
    DRAG_TARGET  = DdTargets.MEDIAOBJ
    ICON         = ICONS["media"]

    def __init__(self, dbstate, obj):
        ScratchPadWrapper.__init__(self, dbstate, obj)
        self._type  = _("Media")
        self._objclass = 'Media'
        self.reset()

    def reset(self):
        (drag_type, idval, self._handle, val) = pickle.loads(self._obj)
        obj = self._db.get_object_from_handle(self._handle)
        if obj:
            self._title = obj.get_description()
            self._value = obj.get_path()

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        (drag_type, idval, handle, val) = pickle.loads(self._obj)
        obj = self._db.get_object_from_handle(handle)
        return "<big><b>%s</b></big>\n\n"\
                "\t<b>%s:</b>\t%s\n"\
                "\t<b>%s:</b>\t%s\n"\
                "\t<b>%s:</b>\t%s\n" % (_("Media"),
                _("Title"),escape(obj.get_description()),
                _("Type"),escape(obj.get_mime_type()),
                _("Name"),escape(obj.get_path()))

    def is_valid(self):
        data = pickle.loads(self._obj)
        handle = data[2]
        obj = self._db.get_object_from_handle(handle)
        if obj:
            return True
        return False

class ScratchPadMediaRef(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.MEDIAREF]
    DRAG_TARGET  = DdTargets.MEDIAREF
    ICON         = LINK_PIC

    def __init__(self, dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self, dbstate, obj)
        self._type  = _("Media Reference")
        self.reset()

    def reset(self):
        base = self._db.get_object_from_handle(self._obj.get_reference_handle())
        if base:
            self._title = base.get_description()
            self._value = base.get_path()

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        base = self._db.get_object_from_handle(self._obj.get_reference_handle())
        return "<big><b>%s</b></big>\n\n"\
                "\t<b>%s:</b>\t%s\n"\
                "\t<b>%s:</b>\t%s\n"\
                "\t<b>%s:</b>\t%s\n" % (_("Media Reference"),
                _("Title"),escape(base.get_description()),
                _("Type"),escape(base.get_mime_type()),
                _("Name"),escape(base.get_path()))


class ScratchPadPersonRef(ScratchPadGrampsTypeWrapper):

    DROP_TARGETS = [DdTargets.PERSONREF]
    DRAG_TARGET  = DdTargets.PERSONREF
    ICON         = LINK_PIC

    def __init__(self, dbstate, obj):
        ScratchPadGrampsTypeWrapper.__init__(self, dbstate, obj)
        self._type  = _("Person Reference")
        self.reset()

    def reset(self):
        person = self._db.get_person_from_handle(self._obj.get_reference_handle())
        if person:
            self._title = self._obj.get_relation()
            self._value = person.get_primary_name().get_name()

    def tooltip(self):
        return ""

class ScratchPersonLink(ScratchPadWrapper):

    DROP_TARGETS = [DdTargets.PERSON_LINK]
    DRAG_TARGET  = DdTargets.PERSON_LINK
    ICON         = ICONS["person"]

    def __init__(self, dbstate, obj):
        ScratchPadWrapper.__init__(self, dbstate, obj)
        self._type  = _("Person")
        self._objclass = 'Person'
        self.reset()

    def reset(self):
        (drag_type, idval, self._handle, val) = pickle.loads(self._obj)
        person = self._db.get_person_from_handle(self._handle)
        if person:
            self._title = person.get_primary_name().get_name()
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth_handle = birth_ref.ref
                birth = self._db.get_event_from_handle(birth_handle)
                date_str = DateHandler.get_date(birth)
                if date_str != "":
                    self._value = escape(date_str)

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        data = pickle.loads(self._obj)
        handle = data[2]
        person = self._db.get_person_from_handle(handle)

        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Person"),
            _("Name"),escape(self._title),
            _("Birth"),escape(self._value))

        if person and len(person.get_source_references()) > 0:
            psrc_ref = person.get_source_references()[0]
            psrc_id = psrc_ref.get_reference_handle()
            psrc = self._db.get_source_from_handle(psrc_id)

            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Primary source"),
                _("Name"),
                escape(short(psrc.get_title())))

        return s

    def is_valid(self):
        data = pickle.loads(self._obj)
        handle = data[2]
        obj = self._db.get_person_from_handle(handle)
        if obj:
            return True
        return False
        

class ScratchSourceLink(ScratchPadWrapper):

    DROP_TARGETS = [DdTargets.SOURCE_LINK]
    DRAG_TARGET  = DdTargets.SOURCE_LINK
    ICON         = ICONS["source"]

    def __init__(self, dbstate, obj):
        ScratchPadWrapper.__init__(self, dbstate, obj)
        self._type  = _("Source")
        self._objclass = 'Source'
        self.reset()

    def reset(self):
        (drag_type, idval, self._handle, val) = pickle.loads(self._obj)
        source = self._db.get_source_from_handle(self._handle)
        if source:
            self._title = source.get_title()
            self._value = source.get_gramps_id()

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        (drag_type, idval, handle, val) = pickle.loads(self._obj)
        base = self._db.get_source_from_handle(handle)
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % (
            _("Source"),
            _("Title"),escape(base.get_title()),
            _("Abbreviation"), escape(base.get_abbreviation()),
            _("Author"), escape(base.get_author()),
            _("Publication Information"), escape(base.get_publication_info()))
        return s

    def is_valid(self):
        data = pickle.loads(self._obj)
        handle = data[2]
        obj = self._db.get_source_from_handle(handle)
        if obj:
            return True
        return False

class ScratchRepositoryLink(ScratchPadWrapper):

    DROP_TARGETS = [DdTargets.REPO_LINK]
    DRAG_TARGET  = DdTargets.REPO_LINK
    ICON         = ICONS["repository"]

    def __init__(self, dbstate, obj):
        ScratchPadWrapper.__init__(self, dbstate, obj)
        self._type  = _("Repository")
        self._objclass = 'Repository'
        self.reset()

    def reset(self):
        (drag_type, idval, self._handle, val) = pickle.loads(self._obj)
        source = self._db.get_repository_from_handle(self._handle)
        if source:
            self._title = source.get_name()
            self._value = str(source.get_type())

    def tooltip(self):
        if not self.is_valid(): return _("Unavailable")
        (drag_type, idval, handle, val) = pickle.loads(self._obj)
        base = self._db.get_repository_from_handle(handle)
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % (
            _("Repository"),
            _("Name"),escape(base.get_name()),
            _("Type"), escape(base.get_type().__str__()))
        return s

    def is_valid(self):
        data = pickle.loads(self._obj)
        handle = data[2]
        obj = self._db.get_repository_from_handle(handle)
        if obj:
            return True
        return False

#-------------------------------------------------------------------------
#
# Wrapper classes to deal with lists of objects
#
#-------------------------------------------------------------------------

class ScratchDropList(object):
    DROP_TARGETS = [DdTargets.LINK_LIST]
    DRAG_TARGET  = None

    def __init__(self, dbstate, obj_list):
        self._dbstate = dbstate
        # ('link-list', id, (('person-link', handle), 
        #                    ('person-link', handle), ...), 0)
        self._obj_list = pickle.loads(obj_list)

    def map2class(self, target):
        return {"person-link": ScratchPersonLink,
                'personref': ScratchPadPersonRef,
                'source-link': ScratchSourceLink,
                'srcref': ScratchPadSourceRef,
                'repo-link': ScratchRepositoryLink,
                'pevent': ScratchPadEvent,
                'eventref': ScratchPadEventRef,
                'mediaobj': ScratchMediaObj,
                'mediaref': ScratchPadMediaRef,
                'place-link': ScratchPadPlace,
                'note-link': ScratchPadNote,
                }[target]

    def get_objects(self):
        list_type, id, handles, timestamp = self._obj_list
        retval = []
        for (target, handle) in handles:
            _class = self.map2class(target)
            obj = _class(self._dbstate, pickle.dumps((target, id, handle, timestamp)))
            retval.append(obj)
        return retval

class ScratchDropRawList(ScratchDropList):
    DROP_TARGETS = [DdTargets.RAW_LIST]
    DRAG_TARGET  = None

    def __init__(self, dbstate, obj_list):
        self._dbstate = dbstate
        # ('raw-list', id, (ScratchObject, ScratchObject, ...), 0)
        self._obj_list = pickle.loads(obj_list)

    def get_objects(self):
        retval = []
        for item in self._obj_list:
            target = pickle.loads(item)[0]
            _class = self.map2class(target)
            obj = _class(self._dbstate, item)
            retval.append(obj)
        return retval

# FIXME: add family, and all other object lists

#-------------------------------------------------------------------------
#
# ScratchPadListModel class
# Now shown as 'Clipboard'
#-------------------------------------------------------------------------
class ScratchPadListModel(gtk.ListStore):

    def __init__(self):
        gtk.ListStore.__init__(self,
                               str,    # object type
                               object, # object
                               object,  # tooltip callback
                               str, # type
                               str, # value
                               )


#-------------------------------------------------------------------------
#
# ScratchPadListView class
# Now shown as 'Clipboard'
#-------------------------------------------------------------------------
class ScratchPadListView(object):

    LOCAL_DRAG_TARGET = ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0)
    LOCAL_DRAG_TYPE   = 'MY_TREE_MODEL_ROW'
    
    def __init__(self, dbstate, widget):
        
        self._widget = widget
        self.dbstate = dbstate
        self.dbstate.connect('database-changed', self.database_changed)
        self.database_changed(dbstate.db)
            
        self._target_type_to_wrapper_class_map = {}
        self._previous_drop_time = 0

        self.otitles = [(_('Type'),-1,150),
                        (_('Title'),-1,150),
                        (_('Value'),-1,150),
                        ('',-1,0)] # To hold the tooltip text

        # Create the tree columns
        self._col1 = gtk.TreeViewColumn(_("Type"))
        self._col1.set_sort_column_id(0)
        self._col2 = gtk.TreeViewColumn(_("Title"))
        self._col2.set_sort_column_id(3)
        self._col3 = gtk.TreeViewColumn(_("Value"))
        self._col3.set_sort_column_id(4)

        # Add columns
        self._widget.append_column(self._col1)
        self._widget.append_column(self._col2)
        self._widget.append_column(self._col3)

        # Create cell renders
        self._col1_cellpb = gtk.CellRendererPixbuf()
        self._col1_cell = gtk.CellRendererText()
        self._col2_cell = gtk.CellRendererText()
        self._col3_cell = gtk.CellRendererText()

        # Add cells to view
        self._col1.pack_start(self._col1_cellpb, False)
        self._col1.pack_start(self._col1_cell, True)
        self._col2.pack_start(self._col2_cell, True)
        self._col3.pack_start(self._col3_cell, True)

        # Setup the cell data callback funcs
        self._col1.set_cell_data_func(self._col1_cellpb, self.object_pixbuf)
        self._col1.set_cell_data_func(self._col1_cell, self.object_type)
        self._col2.set_cell_data_func(self._col2_cell, self.object_title)
        self._col3.set_cell_data_func(self._col3_cell, self.object_value)                        
        
        self.treetips = TreeTips.TreeTips(self._widget,2,True)

        # Set the column that inline searching will use.
        # The search does not appear to work properly so I am disabling it for now.
        self._widget.set_enable_search(False)
        #self._widget.set_search_column(1)

        self._widget.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                   (ScratchPadListView.LOCAL_DRAG_TARGET,) + \
                                   DdTargets.all_targets(),
                                   ACTION_COPY)

        self._widget.connect('drag_data_get', self.object_drag_data_get)
        self._widget.connect('drag_begin', self.object_drag_begin)
        self._widget.connect('drag_data_received',
                             self.object_drag_data_received)
        self._widget.connect('drag_end', self.object_drag_end)

        self.register_wrapper_classes()

    def database_changed(self,db):
        self._db = db
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
            'note-rebuild'
            )

        for signal in db_signals:
            self._db.connect(signal,self.remove_invalid_objects)

        self._db.connect('person-delete', 
                         gen_del_obj(self.delete_object, 'person-link'))
        self._db.connect('person-delete', 
                         gen_del_obj(self.delete_object_ref, 'personref'))
        self._db.connect('source-delete',
                         gen_del_obj(self.delete_object, 'source-link'))
        self._db.connect('source-delete',
                         gen_del_obj(self.delete_object_ref, 'srcref'))
        self._db.connect('repository-delete',
                         gen_del_obj(self.delete_object, 'repo-link'))
        self._db.connect('event-delete',
                         gen_del_obj(self.delete_object, 'pevent'))
        self._db.connect('event-delete',
                         gen_del_obj(self.delete_object_ref, 'eventref'))
        self._db.connect('media-delete',
                         gen_del_obj(self.delete_object, 'mediaobj'))
        self._db.connect('media-delete',
                         gen_del_obj(self.delete_object_ref, 'mediaref'))
        self._db.connect('place-delete',
                         gen_del_obj(self.delete_object, 'place-link'))
        self._db.connect('note-delete',
                         gen_del_obj(self.delete_object, 'note-link'))
        # family-delete not needed, cannot be dragged!

        self.remove_invalid_objects()

    def remove_invalid_objects(self,dummy=None):
        model = self._widget.get_model()

        if model:
            for o in model:
                if not o[1].is_valid():
                    model.remove(o.iter)

    def delete_object(self, handle_list, link_type):
        model = self._widget.get_model()

        if model:
            for o in model:
                if o[0] == link_type:
                    data = pickle.loads(o[1]._obj)
                    if data[2] in handle_list:
                        model.remove(o.iter)
    
    def delete_object_ref(self, handle_list, link_type):
        model = self._widget.get_model()

        if model:
            for o in model:
                if o[0] == link_type:
                    data = o[1]._obj.get_reference_handle()
                    if data in handle_list:
                        model.remove(o.iter)
                        
    # Method to manage the wrapper classes.
    
    def register_wrapper_classes(self):
        self.register_wrapper_class(ScratchPadAddress)
        self.register_wrapper_class(ScratchPadLocation)
        self.register_wrapper_class(ScratchPadEvent)
        self.register_wrapper_class(ScratchPadPlace)
        self.register_wrapper_class(ScratchPadEventRef)
        self.register_wrapper_class(ScratchPadSourceRef)
        self.register_wrapper_class(ScratchPadRepoRef)
        self.register_wrapper_class(ScratchPadFamilyEvent)
        self.register_wrapper_class(ScratchPadUrl)
        self.register_wrapper_class(ScratchPadAttribute)
        self.register_wrapper_class(ScratchPadFamilyAttribute)
        self.register_wrapper_class(ScratchPadName)
        self.register_wrapper_class(ScratchRepositoryLink)
        self.register_wrapper_class(ScratchMediaObj)
        self.register_wrapper_class(ScratchPadMediaRef)
        self.register_wrapper_class(ScratchSourceLink)
        self.register_wrapper_class(ScratchPersonLink)
        self.register_wrapper_class(ScratchDropList)
        self.register_wrapper_class(ScratchDropRawList)
        self.register_wrapper_class(ScratchPadPersonRef)
        self.register_wrapper_class(ScratchPadText)
        self.register_wrapper_class(ScratchPadNote)
        
    def register_wrapper_class(self,wrapper_class):
        for drop_target in wrapper_class.DROP_TARGETS:            
            self._target_type_to_wrapper_class_map[drop_target.drag_type] = wrapper_class

    # Methods for rendering the cells.
    
    def object_pixbuf(self, column, cell, model, node, user_data=None):
        o = model.get_value(node, 1)
        cell.set_property('pixbuf', o.__class__.ICON)
        
    def object_type(self, column, cell, model, node, user_data=None):
        o = model.get_value(node, 1)
        cell.set_property('text', o.get_type())
        
    def object_title(self, column, cell, model, node, user_data=None):
        o = model.get_value(node, 1)
        cell.set_property('text', o.get_title())
    
    def object_value(self, column, cell, model, node, user_data=None):
        o = model.get_value(node, 1)
        cell.set_property('text', o.get_value())


    # handlers for the drag and drop events.
    
    def on_object_select_row(self, obj):        
        tree_selection = self._widget.get_selection()
        model, paths = tree_selection.get_selected_rows()
        if len(paths) > 1:
            targets = [(DdTargets.RAW_LIST.drag_type, gtk.TARGET_SAME_WIDGET, 0), 
                       ScratchPadListView.LOCAL_DRAG_TARGET] 
        else:
            targets = [ScratchPadListView.LOCAL_DRAG_TARGET] 
        for path in paths:
            node = model.get_iter(path)
            if node is not None:
                o = model.get_value(node,1)
                targets += [target.target() for target in o.__class__.DROP_TARGETS]

        self._widget.enable_model_drag_source(BUTTON1_MASK, targets, ACTION_COPY | ACTION_MOVE)

    def object_drag_begin(self, context, a):
        """ Handle the beginning of a drag operation. """
        self.treetips.disable()
    
    def object_drag_end(self, widget, drag_context):
        """ Handle the end of a drag operation. """
        self.treetips.enable()

    def object_drag_data_get(self, widget, context, sel_data, info, time):
        tree_selection = widget.get_selection()
        model, paths = tree_selection.get_selected_rows()
        if len(paths) == 1:
            path = paths[0]
            node = model.get_iter(path)
            o = model.get_value(node,1)
            sel_data.set(sel_data.target, 8, o.pack())
        elif len(paths) > 1:
            raw_list = []
            for path in paths:
                node = model.get_iter(path)
                o = model.get_value(node,1)
                raw_list.append(o._pickle)
            sel_data.set(sel_data.target, 8, pickle.dumps(raw_list))
        return True

    def object_drag_data_received(self,widget,context,x,y,selection,info,time,
                                  title=None, value=None):
        model = widget.get_model()
        sel_data = selection.data
        # In Windows time is always zero. Until that is fixed, use the seconds
        # of the local time to filter out double drops.
        realTime = strftime("%S")

        # There is a strange bug that means that if there is a selection
        # in the list we get multiple drops of the same object. Luckily
        # the time values are the same so we can drop all but the first.
        if (realTime == self._previous_drop_time) and (time != -1):
            return None

        # Find a wrapper class
        possible_wrappers = []
        if mac():
            # context is empty on mac due to a bug, work around this
            # Note that this workaround code works fine in linux too as 
            # we know very well inside of GRAMPS what sel_data can be, so 
            # we can anticipate on it, instead of letting the wrapper handle
            # it. This is less clean however !
            # See http://www.gramps-project.org/bugs/view.php?id=3089 for 
            # an explaination of why this is required.
            dragtype = None
            try:
                dragtype = pickle.loads(sel_data)[0]
            except pickle.UnpicklingError, msg :
                # not a pickled object, probably text
                if isinstance(sel_data, basestring):
                    dragtype = DdTargets.TEXT.drag_type
            if dragtype in self._target_type_to_wrapper_class_map:
                possible_wrappers = [dragtype]
        else:
            possible_wrappers = [target for target in context.targets \
                        if target in self._target_type_to_wrapper_class_map]

        if len(possible_wrappers) == 0:
            # No wrapper for this class
            return None

        # Just select the first match.
        wrapper_class = self._target_type_to_wrapper_class_map[
                                                    str(possible_wrappers[0])]
        o = wrapper_class(self.dbstate, sel_data)
        if title:
            o._title = title
        if value:
            o._value = value

        # If the wrapper object is a subclass of ScratchDropList then
        # the drag data was a list of objects and we need to decode
        # all of them.
        if isinstance(o,ScratchDropList):
            o_list = o.get_objects()
        else:
            o_list = [o]
        for o in o_list:
            drop_info = widget.get_dest_row_at_pos(x, y)
            if drop_info:
                path, position = drop_info
                node = model.get_iter(path)
                if (position == gtk.TREE_VIEW_DROP_BEFORE
                    or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                    model.insert_before(node,[o.__class__.DRAG_TARGET.drag_type, 
                                              o, o.tooltip, o._type, o._value])
                else:
                    model.insert_after(node,[o.__class__.DRAG_TARGET.drag_type, 
                                             o, o.tooltip, o._type, o._value])
            else:
                model.append([o.__class__.DRAG_TARGET.drag_type, o, o.tooltip, 
                              o._type, o._value])

            if context.action == ACTION_MOVE:
                context.finish(True, True, time)

        # remember time for double drop workaround.
        self._previous_drop_time = realTime
        return o_list

    # proxy methods to provide access to the real widget functions.
    
    def set_model(self,model=None):
        self._widget.set_model(model)
        self._widget.get_selection().connect('changed',self.on_object_select_row)
        self._widget.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

    def get_model(self):
        return self._widget.get_model()

    def get_selection(self):
        return self._widget.get_selection()

    def set_search_column(self,col):
        return self._widget.set_search_column(col)

#-------------------------------------------------------------------------
#
# ScatchPadWindow class
#
#-------------------------------------------------------------------------
class ScratchPadWindow(ManagedWindow.ManagedWindow):
    """
        The Clipboard (was ScratchPad) provides a temporary area to hold objects
        that can
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
    
    # Class attribute used to hold the content of the
    # Clipboard (was ScratchPad). A class attribute is used so that the content
    # it preserved even when the Clipboard window is closed.
    # As there is only ever one Clipboard we do not need to
    # maintain a list of these.
    otree = None
    
    def __init__(self, dbstate, uistate):
        """Initialize the ScratchPad class, and displays the window"""

        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)
        self.dbstate = dbstate

        self.database_changed(self.dbstate.db)
        self.dbstate.connect('database-changed', self.database_changed)

        self.width_key = 'interface.clipboard-width'
        self.height_key = 'interface.clipboard-height'
        
        self.top = Glade()
        self.set_window(self.top.toplevel, None, None, msg=_("Clipboard"))
        self._set_size()

        self.clear_all_btn = self.top.get_object("btn_clear_all")
        self.clear_btn = self.top.get_object("btn_clear")
        
        self.object_list = ScratchPadListView(self.dbstate, 
                                              self.top.get_object('objectlist'))
        self.object_list.get_selection().connect('changed',
                                                 self.set_clear_btn_sensitivity)
        self.object_list.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.set_clear_btn_sensitivity(sel=self.object_list.get_selection())
        
        if not ScratchPadWindow.otree:
            ScratchPadWindow.otree = ScratchPadListModel()

        self.set_clear_all_btn_sensitivity(treemodel=ScratchPadWindow.otree)
        ScratchPadWindow.otree.connect('row-deleted',
                                       self.set_clear_all_btn_sensitivity)
        ScratchPadWindow.otree.connect('row-inserted',
                                       self.set_clear_all_btn_sensitivity)
        
        
        self.object_list.set_model(ScratchPadWindow.otree)
        
        #Database might have changed, objects might have been removed,
        #we need to reevaluate if all data is valid
        self.object_list.remove_invalid_objects()
        
        self.top.connect_signals({
            "on_close_scratchpad" : self.close,
            "on_clear_clicked": self.on_clear_clicked,
            "on_help_clicked": self.on_help_clicked,
            })

        self.clear_all_btn.connect_object('clicked', gtk.ListStore.clear,
                                          ScratchPadWindow.otree)
        self.db.connect('database-changed', lambda x: ScratchPadWindow.otree.clear())
        
        self.show()

    def build_menu_names(self, obj):
        return (_('Clipboard'),None)

    def database_changed(self,database):
        self.db = database
        
    def set_clear_all_btn_sensitivity(self, treemodel=None,
                                      path=None, node=None, user_param1=None):
        if len(treemodel) == 0:
            self.clear_all_btn.set_sensitive(False)
        else:
            self.clear_all_btn.set_sensitive(True)

    def set_clear_btn_sensitivity(self, sel=None, user_param1=None):
        if sel.count_selected_rows() == 0:
            self.clear_btn.set_sensitive(False)
        else:
            self.clear_btn.set_sensitive(True)
        
    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def on_clear_clicked(self, obj):
        """Deletes the selected object from the object list"""
        selection = self.object_list.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            node = model.get_iter(path)
            if node:
                model.remove(node)

def short(val,size=60):
    if len(val) > size:
        return "%s..." % val[0:size]
    else:
        return val

def place_title(db,event):
    pid = event.get_place_handle()
    if pid:
        return db.get_place_from_handle(pid).get_title()
    else:
        return u''

def gen_del_obj(func, t):
    return lambda l : func(l, t)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def ScratchPad(database,person,callback,parent=None):
    ScratchPadWindow(database,parent)
