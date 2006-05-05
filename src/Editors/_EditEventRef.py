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
import RelLib

from DisplayTabs import SourceEmbedList,NoteTab,GalleryTab,EventBackRefList
from GrampsWidgets import *
from _EditReference import EditReference

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# EditEventRef class
#
#-------------------------------------------------------------------------
class EditEventRef(EditReference):
    def __init__(self, state, uistate, track, event, event_ref, update):
        EditReference.__init__(self, state, uistate, track, event, event_ref,
                               update)
        self._init_event()

    def _local_init(self):

        self.top = gtk.glade.XML(const.gladeFile, "event_eref_edit","gramps")
        self.set_window(self.top.get_widget('event_eref_edit'),
                        self.top.get_widget('eer_title'),
                        _('Event Reference Editor'))
        self.define_warn_box(self.top.get_widget("eer_warning"))
        self.define_expander(self.top.get_widget("eer_expander"))
                              
    def _init_event(self):
        self.commit_event = self.db.commit_personal_event
        self.add_event = self.db.add_person_event

    def get_custom_events(self):
        return self.db.get_person_event_type_list()

    def _connect_signals(self):
        self.define_ok_button(self.top.get_widget('ok'),self.ok_clicked)
        self.define_cancel_button(self.top.get_widget('cancel'))

    def _setup_fields(self):
        
        self.cause_monitor = MonitoredEntry(
            self.top.get_widget("eer_cause"),
            self.source.set_cause,
            self.source.get_cause,
            self.db.readonly)
        
        self.ref_privacy = PrivacyButton(
            self.top.get_widget('eer_ref_priv'),
            self.source_ref)

        self.descr_field = MonitoredEntry(
            self.top.get_widget("eer_description"),
            self.source.set_description,
            self.source.get_description,
            self.db.readonly)

        self.place_field = PlaceEntry(
            self.top.get_widget("eer_place"),
            self.source.get_place_handle(),
            self.dbstate.get_place_completion(),
            self.db.readonly)

        self.ev_privacy = PrivacyButton(
            self.top.get_widget("eer_ev_priv"),
            self.source)
                
        self.role_selector = MonitoredDataType(
            self.top.get_widget('eer_role_combo'),
            self.source_ref.set_role,
            self.source_ref.get_role,
            )

        self.event_menu = MonitoredDataType(
            self.top.get_widget("eer_type_combo"),
            self.source.set_type,
            self.source.get_type,
            custom_values=self.get_custom_events())

        self.date_check = MonitoredDate(
            self.top.get_widget("eer_date"),
            self.top.get_widget("eer_date_stat"),
            self.source.get_date_object(),
            self.window,
            self.db.readonly)

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        """

        notebook = self.top.get_widget('notebook')
        notebook_ref = self.top.get_widget('notebook_ref')

        self.srcref_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate, self.track,
                            self.source.source_list))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.source.get_note_object()))
        
        self.note_ref_tab = self._add_tab(
            notebook_ref,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.source_ref.get_note_object()))
        
        self.gallery_tab = self._add_tab(
            notebook,
            GalleryTab(self.dbstate, self.uistate, self.track,
                       self.source.get_media_list()))

        self.backref_tab = self._add_tab(
            notebook,
            EventBackRefList(self.dbstate, self.uistate, self.track,
                             self.db.find_backlink_handles(self.source.handle),
                             self.enable_warnbox))

    def build_menu_names(self,eventref):
        if self.source:
            event_name = str(self.source.get_type())
            submenu_label = _('Event: %s')  % event_name
        else:
            submenu_label = _('New Event')
        return (_('Event Reference Editor'),submenu_label)
        
    def ok_clicked(self,obj):

        (need_new, handle) = self.place_field.get_place_info()
        if need_new:
            place_obj = RelLib.Place()
            place_obj.set_handle(Utils.create_id())
            place_obj.set_title(handle)
            self.source.set_place_handle(place_obj.get_handle())
        else:
            self.source.set_place_handle(handle)

        trans = self.db.transaction_begin()
        if self.source.handle:
            if need_new:
                self.db.add_place(place_obj,trans)
            self.commit_event(self.source,trans)
            self.db.transaction_commit(trans,_("Modify Event"))
        else:
            if need_new:
                self.db.add_place(place_obj,trans)
            self.add_event(self.source,trans)
            self.db.transaction_commit(trans,_("Add Event"))
            self.source_ref.ref = self.source.handle
        
        if self.update:
            self.update(self.source_ref,self.source)

        self.close()

class EditFamilyEventRef(EditEventRef):

    def __init__(self, state, uistate, track, event, event_ref, update):
        
        EditEventRef.__init__(self, state, uistate, track, event,
                              event_ref, update)
        
    def _init_event(self):
        self.commit_event = self.db.commit_family_event
        self.add_event = self.db.add_family_event

    def get_custom_events(self):
        return [ RelLib.EventType((RelLib.EventType.CUSTOM,val)) \
                 for val in self.dbstate.db.get_family_event_types()]
        

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
