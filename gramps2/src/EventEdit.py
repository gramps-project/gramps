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
import sets
import gc
from cgi import escape

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
import Sources
import Witness
import const
import Utils
import AutoComp
import RelLib
from DateHandler import parser as _dp, displayer as _dd
import DateEdit
import GrampsDisplay
import DisplayState

from QuestionDialog import WarningDialog, ErrorDialog
from WindowUtils import GladeIf
from DisplayTabs import *

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
        
        read_only = self.db.readonly
        noedit = self.db.readonly
        self.event = event
        self.path = self.db.get_save_path()
        self.plist = []
        self.pmap = {}

        self.dp = _dp
        self.dd = _dd

        DisplayState.ManagedWindow.__init__(self, uistate, self.track, event)
        if self.already_exist:
            return

        for key in self.db.get_place_handles():
            title = self.db.get_place_from_handle(key).get_title()
            self.pmap[title] = key

        if event:
            self.srcreflist = self.event.get_source_references()
            self.date = RelLib.Date(self.event.get_date_object())
        else:
            self.srcreflist = []
            self.date = RelLib.Date(None)

        self.top = gtk.glade.XML(const.gladeFile, "event_edit","gramps")
        self.gladeif = GladeIf(self.top)

        self.window = self.top.get_widget("event_edit")
        title_label = self.top.get_widget('title')

        etitle = _('Event Editor')
        Utils.set_titles(self.window,title_label, etitle,
                         _('Event Editor'))
        
        self.place_field = self.top.get_widget("eventPlace")
        self.place_field.set_editable(not noedit)
        self.cause_field = self.top.get_widget("eventCause")
        self.cause_field.set_editable(not noedit)
        self.date_field  = self.top.get_widget("eventDate")
        self.date_field.set_editable(not noedit)
        self.descr_field = self.top.get_widget("event_description")
        self.descr_field.set_editable(not noedit)
        self.event_menu = self.top.get_widget("personal_events")
        self.priv = self.top.get_widget("priv")
        self.priv.set_sensitive(not noedit)
        self.ok = self.top.get_widget('ok')
        
        self.ok.set_sensitive(not noedit)
            
        if read_only or noedit:
            self.event_menu.set_sensitive(False)
            self.date_field.grab_focus()

        if event:
            defval = event.get_type()[0]
        else:
            defval = None

        self.type_selector = AutoComp.StandardCustomSelector(
            total_events, self.event_menu,
            RelLib.Event.CUSTOM, defval)

        AutoComp.fill_entry(self.place_field,self.pmap.keys())

        if event != None:
            place_handle = event.get_place_handle()
            if not place_handle:
                place_name = u""
            else:
                place_name = self.db.get_place_from_handle(place_handle).get_title()
            self.place_field.set_text(place_name)

            self.date_field.set_text(_dd.display(self.date))
            self.cause_field.set_text(event.get_cause())
            self.descr_field.set_text(event.get_description())
            self.priv.set_active(event.get_privacy())
            
        else:
            event = RelLib.Event()
        date_stat = self.top.get_widget("date_stat")
        date_stat.set_sensitive(not self.db.readonly)
        self.date_check = DateEdit.DateEdit(self.date,
                                        self.date_field,
                                        date_stat,
                                        self.window)

        self.gladeif.connect('button111','clicked',self.close)
        self.gladeif.connect('ok','clicked',self.on_event_edit_ok_clicked)
        self.gladeif.connect('button126','clicked',self.on_help_clicked)

        self._create_tabbed_pages()

        self.show()

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
            win_key = obj.get_handle()
        else:
            win_key = id(self)

    def on_delete_event(self,obj,b):
        self.gladeif.close()

    def close(self,obj):
        self.gladeif.close()
        self.window.destroy()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-ev')

    def on_event_edit_ok_clicked(self,obj):

        event_data = self.type_selector.get_values()
        ecause = unicode(self.cause_field.get_text())
        eplace_obj = get_place(self.place_field,self.pmap,self.db)
        buf = self.note_field.get_buffer()

        start = buf.get_start_iter()
        stop = buf.get_end_iter()
        enote = unicode(buf.get_text(start,stop,False))
        eformat = self.preform.get_active()
        edesc = unicode(self.descr_field.get_text())
        epriv = self.priv.get_active()

#         if ename not in self.elist:
#             WarningDialog(
#                 _('New event type created'),
#                 _('The "%s" event type has been added to this database.\n'
#                   'It will now appear in the event menus for this database') % ename)
#             self.elist.append(ename)
#             self.elist.sort()

        just_added = self.event.handle == None

        self.update_event(event_data,self.date,eplace_obj,edesc,enote,eformat,
                          epriv,ecause)

        if just_added:
            trans = self.db.transaction_begin()
            self.db.add_event(self.event,trans)
            self.db.transaction_commit(trans,_("Add Event"))
        elif self.parent.lists_changed:
            trans = self.db.transaction_begin()
            self.db.commit_event(self.event,trans)
            self.db.transaction_commit(trans,_("Edit Event"))
        if self.callback:
            self.callback(self.event)

        self.close(obj)

    def update_event(self,the_type,date,place,desc,note,format,priv,cause):
        # FIXME: commented because we no longer have parent
        #self.parent.lists_changed = 0
        if place:
            if self.event.get_place_handle() != place.get_handle():
                self.event.set_place_handle(place.get_handle())
                #self.parent.lists_changed = 1
        else:
            if self.event.get_place_handle():
                self.event.set_place_handle("")
                #self.parent.lists_changed = 1
        
        if self.event.get_type() != the_type:
            self.event.set_type(the_type)
            #self.parent.lists_changed = 1
        
        if self.event.get_description() != desc:
            self.event.set_description(desc)
            #self.parent.lists_changed = 1

        if self.event.get_note() != note:
            self.event.set_note(note)
            #self.parent.lists_changed = 1

        if self.event.get_note_format() != format:
            self.event.set_note_format(format)
            #self.parent.lists_changed = 1

        dobj = self.event.get_date_object()

        self.event.set_source_reference_list(self.srcreflist)
        
        if not dobj.is_equal(date):
            self.event.set_date_object(date)
            #self.parent.lists_changed = 1

        if self.event.get_cause() != cause:
            self.event.set_cause(cause)
            #self.parent.lists_changed = 1

        if self.event.get_privacy() != priv:
            self.event.set_privacy(priv)
            #self.parent.lists_changed = 1

    def on_switch_page(self,obj,a,page):
        buf = self.note_field.get_buffer()
        start = buf.get_start_iter()
        stop = buf.get_end_iter()
        text = unicode(buf.get_text(start,stop,False))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)

    def commit(self,event,trans):
        self.db.commit_event(event,trans)

    def get_event_names(self):
        data = sets.Set(self.db.get_family_event_types())
        data.union(self.db.get_person_event_types())
        return list(data)

#-------------------------------------------------------------------------
#
# EventRefEditor class
#
#-------------------------------------------------------------------------
class EventRefEditor(DisplayState.ManagedWindow):
    def __init__(self, state, uistate, track, 
                 event, event_ref, referent, update):
        self.db = state.db
        self.state = state
        self.uistate = uistate
        self.referent = referent
        self.event_ref = event_ref
        self.event = event

        DisplayState.ManagedWindow.__init__(self, uistate, track, event_ref)
        if self.already_exist:
            return

        self.update = update

        self.pmap = {}
        for key in self.db.get_place_handles():
            title = self.db.get_place_from_handle(key).get_title()
            self.pmap[title] = key

        self.title = _('Event Reference Editor')

        self.top = gtk.glade.XML(const.gladeFile, "event_eref_edit","gramps")
        self.window = self.top.get_widget('event_eref_edit')
        self.ref_note_field = self.top.get_widget('eer_ref_note')
        self.role_combo = self.top.get_widget('eer_role_combo')
        self.ref_privacy = self.top.get_widget('eer_ref_priv')

        self.place_field = self.top.get_widget("eer_place")
        self.cause_field = self.top.get_widget("eer_cause")
        self.date_field  = self.top.get_widget("eer_date")
        self.descr_field = self.top.get_widget("eer_description")
        self.ev_note_field = self.top.get_widget("eer_ev_note")
        self.type_combo = self.top.get_widget("eer_type_combo")
        self.ev_privacy = self.top.get_widget("eer_ev_priv")
        self.general_label = self.top.get_widget("eer_general_tab")
        self.ok = self.top.get_widget('ok')
        self.expander = self.top.get_widget("eer_expander")
        self.warning = self.top.get_widget("eer_warning")
        self.notebook = self.top.get_widget('notebook')
        
        Utils.set_titles(self.window,
                         self.top.get_widget('eer_title'),
                         self.title)
        
        self.top.signal_autoconnect({
            "on_eer_help_clicked"   : self.on_help_clicked,
            "on_eer_ok_clicked"     : self.on_ok_clicked,
            "on_eer_cancel_clicked" : self.close,
            "on_eer_delete_event"   : self.close,
            })

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

        self.role_selector = AutoComp.StandardCustomSelector(
            role_dict,self.role_combo,
            RelLib.EventRef.CUSTOM,default_role)

        AutoComp.fill_entry(self.place_field,self.pmap.keys())

        self.type_selector = AutoComp.StandardCustomSelector(
            ev_dict,self.type_combo,
            RelLib.Event.CUSTOM,default_type)

        if self.event:
            self.event_added = False
            self.date = RelLib.Date(self.event.get_date_object())
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
            self.date = RelLib.Date(None)
            self.expander.set_expanded(True)
            self.warning.hide()

        if not self.event_ref:
            self.event_ref = RelLib.EventRef()
            self.event_ref.set_role((default_role,role_dict[default_role]))
            self.event_ref.set_reference_handle(self.event.get_handle())

        self.date_check = DateEdit.DateEdit(self.date,
                                        self.date_field,
                                        self.top.get_widget("eer_date_stat"),
                                        self.window)

        # set event_ref values
        self.role_selector.set_values(self.event_ref.get_role())
        self.ref_note_field.get_buffer().set_text(self.event_ref.get_note())
        self.ref_privacy.set_active(self.event_ref.get_privacy())

        # set event values
        self.type_selector.set_values(self.event.get_type())
        place_handle = self.event.get_place_handle()
        if not place_handle:
            place_name = u""
        else:
            place_name = self.db.get_place_from_handle(place_handle).get_title()
        self.place_field.set_text(place_name)
        self.date_field.set_text(_dd.display(self.date))
        self.cause_field.set_text(self.event.get_cause())
        self.descr_field.set_text(self.event.get_description())
        self.ev_privacy.set_active(self.event.get_privacy())

        self._create_tabbed_pages()

        self.show()

    def _add_page(self,page):
        self.notebook.insert_page(page)
        self.notebook.set_tab_label(page,page.get_tab_widget())
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
        self.gallery_tab = self._add_page(GalleryTab(
            self.state, self.uistate, self.track,
            self.event.get_media_list()))

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

    def on_help_clicked(self,obj):
        pass

    def on_ok_clicked(self,obj):

        # first, save event if changed
        etype = self.type_selector.get_values()
        ecause = unicode(self.cause_field.get_text())
        eplace_obj = get_place(self.place_field,self.pmap,self.db)
        buf = self.ev_note_field.get_buffer()
        start = buf.get_start_iter()
        stop = buf.get_end_iter()
        enote = unicode(buf.get_text(start,stop,False))
        eformat = self.preform.get_active()
        edesc = unicode(self.descr_field.get_text())
        epriv = self.ev_privacy.get_active()
        self.lists_changed = 0
        self.update_event(etype,self.date,eplace_obj,edesc,enote,eformat,
                          epriv,ecause)
        
        trans = self.db.transaction_begin()
        self.db.commit_event(self.event,trans)
        if self.event_added:
            self.db.transaction_commit(trans,_("Add Event"))
        else:
            self.db.transaction_commit(trans,_("Modify Event"))
        
        # then, set properties of the event_ref
        self.event_ref.set_role(self.role_selector.get_values())
        self.event_ref.set_privacy(self.ref_privacy.get_active())
        buf = self.ref_note_field.get_buffer()
        start = buf.get_start_iter()
        stop = buf.get_end_iter()
        note = unicode(buf.get_text(start,stop,False))
        self.event_ref.set_note(note)
        self.close(None)

        if self.update:
            self.update((self.event_ref,self.event))

    def update_event(self,the_type,date,place,desc,note,format,priv,cause):
        if place:
            if self.event.get_place_handle() != place.get_handle():
                self.event.set_place_handle(place.get_handle())
                self.lists_changed = 1
        else:
            if self.event.get_place_handle():
                self.event.set_place_handle("")
                self.lists_changed = 1
        
        if self.event.get_type() != the_type:
            self.event.set_type(the_type)
            self.lists_changed = 1
        
        if self.event.get_description() != desc:
            self.event.set_description(desc)
            self.lists_changed = 1

        if self.event.get_note() != note:
            self.event.set_note(note)
            self.lists_changed = 1

        if self.event.get_note_format() != format:
            self.event.set_note_format(format)
            self.lists_changed = 1

        dobj = self.event.get_date_object()

        self.event.set_source_reference_list(self.srcreflist)
        
        if not dobj.is_equal(date):
            self.event.set_date_object(date)
            self.lists_changed = 1

        if self.event.get_cause() != cause:
            self.event.set_cause(cause)
            self.lists_changed = 1

        if self.event.get_privacy() != priv:
            self.event.set_privacy(priv)
            self.lists_changed = 1

    def on_switch_page(self,obj,a,page):
        buf = self.ev_note_field.get_buffer()
        start = buf.get_start_iter()
        stop = buf.get_end_iter()
        text = unicode(buf.get_text(start,stop,False))
        if text:
            Utils.bold_label(self.eer_notes_label)
        else:
            Utils.unbold_label(self.eer_notes_label)

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
