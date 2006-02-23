#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# $Id$

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

try:
    set()
except:
    from sets import Set as set

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import AutoComp
import RelLib
import DateEdit
import GrampsDisplay
import DisplayState

from QuestionDialog import WarningDialog, ErrorDialog
from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
total_events = dict(Utils.personal_events)
for event_type in Utils.family_events.keys():
    if not total_events.has_key(event_type):
        total_events[event_type] = Utils.family_events[event_type]

#-------------------------------------------------------------------------
#
# helper function
#
#-------------------------------------------------------------------------
def get_place(field,pmap,db):
    text = unicode(field.get_text().strip())
    if text:
        if pmap.has_key(text):
            return db.get_place_from_handle(pmap[text])
        else:
            place = RelLib.Place()
            place.set_title(text)
            trans = db.transaction_begin()
            db.add_place(place,trans)
            db.transaction_commit(trans,_("Add Place"))
            return place
    else:
        return None

#-------------------------------------------------------------------------
#
# EventEditor class
#
#-------------------------------------------------------------------------
class EventEditor(DisplayState.ManagedWindow):

    def __init__(self,event,dbstate,uistate,track=[],callback=None):
        self.db = dbstate.db
        self.uistate = uistate
        self.dbstate = dbstate
        self.track = track
        self.callback = callback
        
        self.event = event
        self.path = self.db.get_save_path()
        self.plist = []
        self.pmap = {}

        DisplayState.ManagedWindow.__init__(self, uistate, self.track, event)
        if self.already_exist:
            return

        if not event:
            self.event = RelLib.Event()

        self.top = gtk.glade.XML(const.gladeFile, "event_edit","gramps")

        self.window = self.top.get_widget("event_edit")
        title_label = self.top.get_widget('title')

        etitle = _('Event Editor')
        Utils.set_titles(self.window,title_label, etitle,
                         _('Event Editor'))

        self.place_field = self.top.get_widget("eventPlace")
        self.place_field.set_editable(not self.db.readonly)

        place_handle = event.get_place_handle()
        if not place_handle:
            place_name = u""
        else:
            place_name = self.db.get_place_from_handle(place_handle).get_title()
        self.place_field.set_text(place_name)
        self.place_field.set_completion(self.dbstate.get_place_completion())

        self._create_tabbed_pages()
        self._setup_fields()
        self._connect_signals()
        self.show()

    def _connect_signals(self):
        self.top.get_widget('button111').connect('clicked',self.close_window)
        self.top.get_widget('button126').connect('clicked',self.on_help_clicked)

        ok = self.top.get_widget('ok')
        ok.set_sensitive(not self.db.readonly)
        ok.connect('clicked',self.on_event_edit_ok_clicked)

    def _setup_fields(self):
        self.cause_monitor = MonitoredEntry(
            self.top.get_widget("eventCause"),
            self.event.set_cause,
            self.event.get_cause, self.db.readonly)

        self.descr_field = MonitoredEntry(
            self.top.get_widget("event_description"),
            self.event.set_description,
            self.event.get_description, self.db.readonly)


        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.event, self.db.readonly)

        self.event_menu = MonitoredType(
            self.top.get_widget("personal_events"),
            self.event.set_type,
            self.event.get_type,
            dict(total_events),
            RelLib.Event.CUSTOM)

        self.date_field = MonitoredDate(
            self.top.get_widget("eventDate"),
            self.top.get_widget("date_stat"),
            self.event.get_date_object(),
            self.window, self.db.readonly)

    def _add_page(self,page):
        self.notebook.insert_page(page)
        self.notebook.set_tab_label(page,page.get_tab_widget())
        return page

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        """
        vbox = self.top.get_widget('vbox')
        self.notebook = gtk.Notebook()

        self.srcref_list = self._add_page(SourceEmbedList(
            self.dbstate,self.uistate, self.track,
            self.event.source_list))
        self.note_tab = self._add_page(NoteTab(
            self.dbstate, self.uistate, self.track,
            self.event.get_note_object()))
        self.gallery_tab = self._add_page(GalleryTab(
            self.dbstate, self.uistate, self.track,
            self.event.get_media_list()))

        self.notebook.show_all()
        vbox.pack_start(self.notebook,True)

    def build_menu_names(self,event):
        if event:
            if event.get_type()[0] == RelLib.Event.CUSTOM:
                event_name = event.get_type()[1]
            else:
                try:
                    event_name = Utils.personal_events[event.get_type()[0]]
                except:
                    event_name = Utils.family_events[event.get_type()[0]]
            submenu_label = _('Event: %s')  % event_name
        else:
            submenu_label = _('New Event')
        return (_('Event Editor'),submenu_label)

    def build_window_key(self,obj):
        if obj:
            return obj.get_handle()
        else:
            return id(self)

    def on_delete_event(self,obj,b):
        self.close()

    def close_window(self,obj):
        self.close()
        self.window.destroy()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-ev')

    def on_event_edit_ok_clicked(self,obj):

        eplace_obj = get_place(self.place_field,self.pmap,self.db)

        self.update_event(eplace_obj)

        if self.event.handle == None:
            trans = self.db.transaction_begin()
            self.db.add_event(self.event,trans)
            self.db.transaction_commit(trans,_("Add Event"))
        else:
            orig = self.dbstate.db.get_event_from_handle(self.event.handle)
            if cmp(self.event.serialize(),orig.serialize()):
                trans = self.db.transaction_begin()
                self.db.commit_event(self.event,trans)
                self.db.transaction_commit(trans,_("Edit Event"))

        if self.callback:
            self.callback(self.event)
        self.close(obj)

    def update_event(self,place):
        # FIXME: commented because we no longer have parent
        if place:
            if self.event.get_place_handle() != place.get_handle():
                self.event.set_place_handle(place.get_handle())
        else:
            if self.event.get_place_handle():
                self.event.set_place_handle("")
        
    def commit(self,event,trans):
        self.db.commit_event(event,trans)

    def get_event_names(self):
        data = set(self.db.get_family_event_types())
        data.union(self.db.get_person_event_types())
        return list(data)

#-------------------------------------------------------------------------
#
# Delete Query class
#
#-------------------------------------------------------------------------
class DelEventQuery:
    def __init__(self,event,db,person_list,family_list):
        self.event = event
        self.db = db
        self.person_list = person_list
        self.family_list = family_list

    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        ev_handle_list = [self.event.get_handle()]

        for handle in self.person_list:
            person = self.db.get_person_from_handle(handle)
            person.remove_handle_references('Event',ev_handle_list)
            self.db.commit_person(person,trans)

        for handle in self.family_list:
            family = self.db.get_family_from_handle(handle)
            family.remove_handle_references('Event',ev_handle_list)
            self.db.commit_family(family,trans)

        self.db.enable_signals()
        self.db.remove_event(self.event.get_handle(),trans)
        self.db.transaction_commit(
            trans,_("Delete Event (%s)") % self.event.get_gramps_id())
