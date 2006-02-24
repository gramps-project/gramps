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
    print "set import failed"
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
from DateHandler import displayer as _dd
import DateEdit
import DisplayState

from QuestionDialog import WarningDialog, ErrorDialog
from WindowUtils import GladeIf
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
# EditEventRef class
#
#-------------------------------------------------------------------------
class EditEventRef(DisplayState.ManagedWindow):
    def __init__(self, state, uistate, track, 
                 event, event_ref, referent, update):
        self.db = state.db
        self.state = state
        self.referent = referent
        self.event_ref = event_ref
        self.event = event

        DisplayState.ManagedWindow.__init__(self, uistate, track, event_ref)
        if self.already_exist:
            return

        self.update = update

        self.title = _('Event Reference Editor')

        self.top = gtk.glade.XML(const.gladeFile, "event_eref_edit","gramps")
        self.window = self.top.get_widget('event_eref_edit')
        self.general_label = self.top.get_widget("eer_general_tab")
        self.ok = self.top.get_widget('ok')
        self.expander = self.top.get_widget("eer_expander")
        self.warning = self.top.get_widget("eer_warning")
        self.notebook = self.top.get_widget('notebook')
        self.notebook_ref = self.top.get_widget('notebook_ref')

        if self.referent.__class__.__name__ == 'Person':
            default_type = RelLib.Event.BIRTH
            default_role = RelLib.EventRef.PRIMARY
            ev_dict = Utils.personal_events
            role_dict = Utils.event_roles
        elif self.referent.__class__.__name__ == 'Family':
            default_type = RelLib.Event.MARRIAGE
            default_role = RelLib.EventRef.FAMILY
            ev_dict = Utils.family_events
            role_dict = Utils.family_event_roles

        Utils.set_titles(self.window,
                         self.top.get_widget('eer_title'),
                         self.title)
        
        if self.event:
            self.event_added = False
            if self.event_ref:
                if self.event_ref.get_role()[0] == default_role:
                    self.expander.set_expanded(True)
                    self.warning.hide()
                else:
                    self.expander.set_expanded(False)
                    self.warning.show_all()
        else:
            self.event = RelLib.Event()
            self.event.set_type((default_type,ev_dict[default_type]))
            self.event.set_handle(self.db.create_id())
            self.event.set_gramps_id(self.db.find_next_event_gramps_id())
            self.event_added = True
            self.expander.set_expanded(True)
            self.warning.hide()

        if not self.event_ref:
            self.event_ref = RelLib.EventRef()
            self.event_ref.set_role((default_role,role_dict[default_role]))
            self.event_ref.set_reference_handle(self.event.get_handle())

        # set event_ref values
        self._create_tabbed_pages()
        self._setup_fields(self.state.get_place_completion(),role_dict)
        self._connect_signals()
        
        self.show()

    def _setup_fields(self,place_values,role_dict):
        
        self.cause_monitor = MonitoredEntry(
            self.top.get_widget("eer_cause"),
            self.event.set_cause,
            self.event.get_cause,
            self.db.readonly)
        
        self.ref_privacy = PrivacyButton(
            self.top.get_widget('eer_ref_priv'),
            self.event_ref)

        self.descr_field = MonitoredEntry(
            self.top.get_widget("eer_description"),
            self.event.set_description,
            self.event.get_description,
            self.db.readonly)

        self.place_field = PlaceEntry(
            self.top.get_widget("eer_place"),
            self.event.get_place_handle(),
            place_values,
            self.db.readonly)

        self.ev_privacy = PrivacyButton(
            self.top.get_widget("eer_ev_priv"),
            self.event)
                
        self.role_selector = MonitoredType(
            self.top.get_widget('eer_role_combo'),
            self.event_ref.set_role,
            self.event_ref.get_role,
            role_dict,
            RelLib.EventRef.CUSTOM)

        self.event_menu = MonitoredType(
            self.top.get_widget("eer_type_combo"),
            self.event.set_type,
            self.event.get_type,
            dict(total_events),
            RelLib.Event.CUSTOM)

        self.date_check = DateEdit.DateEdit(
            self.event.get_date_object(),
            self.top.get_widget("eer_date"),
            self.top.get_widget("eer_date_stat"),
            self.window)

    def _connect_signals(self):
        self.top.get_widget('ok').connect('clicked',self.ok_clicked)
        self.top.get_widget('cancel').connect('clicked',self.close)
        self.top.get_widget('help').connect('clicked',self.help_clicked)
        self.window.connect('delete-event',self.close)

    def _add_page(self,page):
        self.notebook.insert_page(page)
        self.notebook.set_tab_label(page,page.get_tab_widget())
        return page

    def _add_ref_page(self,page):
        self.notebook_ref.insert_page(page)
        self.notebook_ref.set_tab_label(page,page.get_tab_widget())
        return page

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        """

        self.srcref_list = self._add_page(SourceEmbedList(
            self.state,self.uistate, self.track,
            self.event.source_list))
        self.note_tab = self._add_page(NoteTab(
            self.state, self.uistate, self.track,
            self.event.get_note_object()))
        self.note_ref_tab = self._add_ref_page(NoteTab(
            self.state, self.uistate, self.track,
            self.event_ref.get_note_object()))
        self.gallery_tab = self._add_page(GalleryTab(
            self.state, self.uistate, self.track,
            self.event.get_media_list()))
        self.backref_tab = self._add_page(EventBackRefList(
            self.state, self.uistate, self.track,
            self.state.db.find_backlink_handles(self.event.handle)))

    def build_menu_names(self,eventref):
        if self.event:
            if self.event.get_type()[0] == RelLib.Event.CUSTOM:
                event_name = self.event.get_type()[1]
            else:
                try:
                    event_name = Utils.personal_events[self.event.get_type()[0]]
                except:
                    event_name = Utils.family_events[self.event.get_type()[0]]
            submenu_label = _('Event: %s')  % event_name
        else:
            submenu_label = _('New Event')
        return (_('Event Reference Editor'),submenu_label)
        
    def build_window_key(self,eventref):
        if self.event:
            return self.event.get_handle()
        else:
            return id(self)

    def help_clicked(self,obj):
        pass

    def ok_clicked(self,obj):

        (need_new, handle) = self.place_field.get_place_info()
        if need_new:
            place_obj = RelLib.Place()
            place_obj.set_title(handle)
            self.event.set_place_handle(place_obj.get_handle())
        else:
            self.event.set_place_handle(handle)

        trans = self.db.transaction_begin()
        self.db.commit_event(self.event,trans)
        if self.event_added:
            if need_new:
                self.db.add_place(place_obj,trans)
            self.db.transaction_commit(trans,_("Add Event"))
        else:
            if need_new:
                self.db.add_place(place_obj,trans)
            self.db.transaction_commit(trans,_("Modify Event"))
        
        self.close(None)

        if self.update:
            self.update((self.event_ref,self.event))


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
