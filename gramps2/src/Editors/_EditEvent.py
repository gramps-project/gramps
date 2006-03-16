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
from TransUtils import sgettext as _

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
import GrampsDisplay
from _EditPrimary import EditPrimary

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
# EditEvent class
#
#-------------------------------------------------------------------------
class EditEvent(EditPrimary):

    def __init__(self,event,dbstate,uistate,track=[],callback=None):

        EditPrimary.__init__(self, dbstate, uistate, track,
                             event, dbstate.db.get_event_from_handle)

    def _local_init(self):
        self.top = gtk.glade.XML(const.gladeFile, "event_edit","gramps")
        self.window = self.top.get_widget("event_edit")

        etitle = _('Event Editor')
        Utils.set_titles(self.window, self.top.get_widget('title'),
                         etitle, etitle)

    def _connect_signals(self):
        self.top.get_widget('button111').connect('clicked',self.delete_event)
        self.top.get_widget('button126').connect('clicked',self.help_clicked)

        ok = self.top.get_widget('ok')
        ok.set_sensitive(not self.db.readonly)
        ok.connect('clicked',self.save)

    def _setup_fields(self):
        self.place_field = PlaceEntry(
            self.top.get_widget("eventPlace"),
            self.obj.get_place_handle(),
            self.dbstate.get_place_completion(),
            self.db.readonly)
        
        self.cause_monitor = MonitoredEntry(
            self.top.get_widget("eventCause"),
            self.obj.set_cause,
            self.obj.get_cause, self.db.readonly)

        self.descr_field = MonitoredEntry(
            self.top.get_widget("event_description"),
            self.obj.set_description,
            self.obj.get_description, self.db.readonly)

        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.obj, self.db.readonly)

        self.event_menu = MonitoredType(
            self.top.get_widget("personal_events"),
            self.obj.set_type,
            self.obj.get_type,
            dict(total_events),
            RelLib.Event.CUSTOM)

        self.date_field = MonitoredDate(
            self.top.get_widget("eventDate"),
            self.top.get_widget("date_stat"),
            self.obj.get_date_object(),
            self.window, self.db.readonly)

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        """
        notebook = gtk.Notebook()
        
        self.srcref_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate, self.track,
                            self.obj.source_list))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_object()))
        
        self.gallery_tab = self._add_tab(
            notebook,
            GalleryTab(self.dbstate, self.uistate, self.track,
                       self.obj.get_media_list()))
        
        self.backref_tab = self._add_tab(
            notebook,
            EventBackRefList(self.dbstate, self.uistate, self.track,
                             self.dbstate.db.find_backlink_handles(self.obj.handle)))

        notebook.show_all()
        self.top.get_widget('vbox').pack_start(notebook,True)

    def _cleanup_on_exit(self):
        self.backref_tab.close()

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

    def help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-ev')

    def save(self,*obj):

        (need_new, handle) = self.place_field.get_place_info()
        if need_new:
            place_obj = RelLib.Place()
            place_obj.set_title(handle)
            self.obj.set_place_handle(place_obj.get_handle())
        else:
            self.obj.set_place_handle(handle)
            
        if self.obj.handle == None:
            trans = self.db.transaction_begin()
            if need_new:
                self.db.add_place(place_obj,trans)
            self.db.add_event(self.obj,trans)
            self.db.transaction_commit(trans,_("Add Event"))
        else:
            orig = self.dbstate.db.get_event_from_handle(self.obj.handle)
            if cmp(self.obj.serialize(),orig.serialize()):
                trans = self.db.transaction_begin()
                if need_new:
                    self.db.add_place(place_obj,trans)
                self.db.commit_event(self.obj,trans)
                self.db.transaction_commit(trans,_("Edit Event"))

        if self.callback:
            self.callback(self.obj)
        self.close(obj)

    def get_event_names(self):
        data = set(self.db.get_family_event_types())
        data.union(self.db.get_person_event_types())
        return list(data)

    def data_has_changed(self):
        if self.db.readonly:
            return False
        elif self.obj.handle:
            orig = self.db.get_event_from_handle(self.obj.handle)
            return cmp(orig.serialize(),self.obj.serialize()) != 0
        else:
            return True

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
