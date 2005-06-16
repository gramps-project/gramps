#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gnome

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
import Date
from DateHandler import parser as _dp, displayer as _dd
import ImageSelect
import DateEdit
from QuestionDialog import WarningDialog, ErrorDialog

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
class EventEditor:

    def __init__(self,event,db,parent,parent_window):
        self.parent = parent
        self.db = db
        read_only = self.db.readonly
        noedit = self.db.readonly
        if event:
            if self.parent.child_windows.has_key(event.get_handle()):
                self.parent.child_windows[event.get_handle()].present(None)
                return
            else:
                self.win_key = event.get_handle()
        else:
            self.win_key = self
        self.event = event
        self.child_windows = {}
        self.path = self.db.get_save_path()
        self.plist = []
        self.pmap = {}

        for key in self.parent.db.get_place_handles():
            title = self.parent.db.get_place_from_handle(key).get_title()
            self.pmap[title] = key

        if event:
            self.srcreflist = self.event.get_source_references()
            self.date = Date.Date(self.event.get_date_object())
        else:
            self.srcreflist = []
            self.date = Date.Date(None)

        self.top = gtk.glade.XML(const.dialogFile, "event_edit","gramps")

        self.window = self.top.get_widget("event_edit")
        title_label = self.top.get_widget('title')

        etitle = _('Event Editor')
        Utils.set_titles(self.window,title_label, etitle,
                         _('Event Editor'))
        
        self.place_field = self.top.get_widget("eventPlace")
        self.place_field.set_editable(not noedit)
        self.cause_field = self.top.get_widget("eventCause")
        self.cause_field.set_editable(not noedit)
        self.slist = self.top.get_widget("slist")
        self.wlist = self.top.get_widget("wlist")
        self.date_field  = self.top.get_widget("eventDate")
        self.date_field.set_editable(not noedit)
        self.descr_field = self.top.get_widget("event_description")
        self.descr_field.set_editable(not noedit)
        self.note_field = self.top.get_widget("eventNote")
        self.note_field.set_editable(not noedit)
        self.event_menu = self.top.get_widget("personal_events")
        self.priv = self.top.get_widget("priv")
        self.priv.set_sensitive(not noedit)
        self.sources_label = self.top.get_widget("sources_tab")
        self.notes_label = self.top.get_widget("note_tab")
        self.general_label = self.top.get_widget("general_tab")
        self.gallery_label = self.top.get_widget("gallery_tab")
        self.witnesses_label = self.top.get_widget("witness_tab")
        self.flowed = self.top.get_widget("eventflowed")
        self.flowed.set_sensitive(not noedit)
        self.preform = self.top.get_widget("eventpreform")
        self.preform.set_sensitive(not noedit)
        self.ok = self.top.get_widget('ok')
        
        self.ok.set_sensitive(not noedit)
            
        if read_only or noedit:
            self.event_menu.set_sensitive(False)
            self.date_field.grab_focus()

        add_src = self.top.get_widget('add_src')
        add_src.set_sensitive(not noedit)
        del_src = self.top.get_widget('del_src')
        del_src.set_sensitive(not noedit)

        self.sourcetab = Sources.SourceTab(
            self.srcreflist, self, self.top, self.window, self.slist,
            add_src, self.top.get_widget('edit_src'), del_src,
            self.db.readonly)

        add_witness = self.top.get_widget('add_witness')
        add_witness.set_sensitive(not noedit)
        edit_witness = self.top.get_widget('edit_witness')
        del_witness = self.top.get_widget('del_witness')
        del_witness.set_sensitive(not noedit)
        
#        self.witnesstab = Witness.WitnessTab(
#            self.witnesslist, self, self.top, self.window, self.wlist,
#            add_witness, edit_witness, del_witness)

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
            
            self.note_field.get_buffer().set_text(event.get_note())
            if event.get_note():
                self.note_field.get_buffer().set_text(event.get_note())
                Utils.bold_label(self.notes_label)
                if event.get_note_format() == 1:
                    self.preform.set_active(1)
                else:
                    self.flowed.set_active(1)
            if event.get_media_list():
                Utils.bold_label(self.gallery_label)
        else:
            event = RelLib.Event()

        self.date_check = DateEdit.DateEdit(self.date,
                                        self.date_field,
                                        self.top.get_widget("date_stat"),
                                        self.window)

        self.icon_list = self.top.get_widget("iconlist")
        self.gallery = ImageSelect.Gallery(event, self.db.commit_event,
                                           self.path, self.icon_list,
                                           self.db,self,self.window)

        self.top.signal_autoconnect({
            "on_switch_page"            : self.on_switch_page,
            "on_help_event_clicked"     : self.on_help_clicked,
            "on_ok_event_clicked"       : self.on_event_edit_ok_clicked,
            "on_cancel_event_clicked"   : self.close,
            "on_event_edit_delete_event": self.on_delete_event,
            "on_addphoto_clicked"       : self.gallery.on_add_media_clicked,
            "on_selectphoto_clicked"    : self.gallery.on_select_media_clicked,
            "on_deletephoto_clicked"    : self.gallery.on_delete_media_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_editphoto_clicked"      : self.gallery.on_edit_media_clicked,
            })

        self.top.get_widget('del_obj').set_sensitive(not noedit)
        self.top.get_widget('sel_obj').set_sensitive(not noedit)
        self.top.get_widget('add_obj').set_sensitive(not noedit)

        Utils.bold_label(self.general_label)

        try:
            self.window.set_transient_for(self.parent.window)
        except AttributeError:
            pass
        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.gallery.close()
        self.close_child_windows()
        self.remove_itself_from_menu()

    def close(self,obj):
        self.gallery.close()
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.window.destroy()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        if not self.event:
            label = _("New Event")
        else:
            (val,strval) = self.event.get_type()
            if val == RelLib.Event.CUSTOM:
                label = strval
            else:
                label = total_events[val]
        if not label.strip():
            label = _("New Event")
        label = "%s: %s" % (_('Event'),label)
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Event Editor'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        if self.window:
            del self.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','adv-ev')

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

        self.close(obj)

    def update_event(self,the_type,date,place,desc,note,format,priv,cause):
        self.parent.lists_changed = 0
        if place:
            if self.event.get_place_handle() != place.get_handle():
                self.event.set_place_handle(place.get_handle())
                self.parent.lists_changed = 1
        else:
            if self.event.get_place_handle():
                self.event.set_place_handle("")
                self.parent.lists_changed = 1
        
        if self.event.get_type() != the_type:
            self.event.set_type(the_type)
            self.parent.lists_changed = 1
        
        if self.event.get_description() != desc:
            self.event.set_description(desc)
            self.parent.lists_changed = 1

        if self.event.get_note() != note:
            self.event.set_note(note)
            self.parent.lists_changed = 1

        if self.event.get_note_format() != format:
            self.event.set_note_format(format)
            self.parent.lists_changed = 1

        dobj = self.event.get_date_object()

        self.event.set_source_reference_list(self.srcreflist)
        
        if not dobj.is_equal(date):
            self.event.set_date_object(date)
            self.parent.lists_changed = 1

        if self.event.get_cause() != cause:
            self.event.set_cause(cause)
            self.parent.lists_changed = 1

        if self.event.get_privacy() != priv:
            self.event.set_privacy(priv)
            self.parent.lists_changed = 1

    def on_switch_page(self,obj,a,page):
        buf = self.note_field.get_buffer()
        start = buf.get_start_iter()
        stop = buf.get_end_iter()
        text = unicode(buf.get_text(start,stop,False))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)

#-------------------------------------------------------------------------
#
# EventRefEditor class
#
#-------------------------------------------------------------------------
class EventRefEditor:
    def __init__(self, event, event_ref, referent, database, update, parent):
        self.db = database
        self.parent = parent
        self.referent = referent
        if self.parent.__dict__.has_key('child_windows'):
            self.win_parent = self.parent
        else:
            self.win_parent = self.parent.parent
        if event_ref:
            if self.win_parent.child_windows.has_key(event_ref):
                self.win_parent.child_windows[event_ref].present(None)
                return
            else:
                self.win_key = event_ref
        else:
            self.win_key = self
        self.update = update
        self.event_ref = event_ref
        self.event = event
        self.child_windows = {}

        self.pmap = {}
        for key in self.parent.db.get_place_handles():
            title = self.parent.db.get_place_from_handle(key).get_title()
            self.pmap[title] = key

        self.title = _('Event Reference Editor')

        self.top = gtk.glade.XML(const.dialogFile, "event_eref_edit","gramps")
        self.window = self.top.get_widget('event_eref_edit')
        self.ref_note_field = self.top.get_widget('eer_ref_note')
        self.role_combo = self.top.get_widget('eer_role_combo')
        self.ref_privacy = self.top.get_widget('eer_ref_priv')

        self.place_field = self.top.get_widget("eer_place")
        self.cause_field = self.top.get_widget("eer_cause")
        self.slist = self.top.get_widget("eer_slist")
        self.wlist = self.top.get_widget("eer_wlist")
        self.date_field  = self.top.get_widget("eer_date")
        self.descr_field = self.top.get_widget("eer_description")
        self.ev_note_field = self.top.get_widget("eer_ev_note")
        self.type_combo = self.top.get_widget("eer_type_combo")
        self.ev_privacy = self.top.get_widget("eer_ev_priv")
        self.sources_label = self.top.get_widget("eer_sources_tab")
        self.notes_label = self.top.get_widget("eer_note_tab")
        self.general_label = self.top.get_widget("eer_general_tab")
        self.gallery_label = self.top.get_widget("eer_gallery_tab")
        self.witnesses_label = self.top.get_widget("eer_witness_tab")
        self.flowed = self.top.get_widget("eer_ev_flowed")
        self.preform = self.top.get_widget("eer_ev_preform")
        self.ok = self.top.get_widget('ok')
        self.expander = self.top.get_widget("eer_expander")
        
        add_src = self.top.get_widget('eer_add_src')
        del_src = self.top.get_widget('eer_del_src')

        add_witness = self.top.get_widget('eer_add_wit')
        edit_witness = self.top.get_widget('eer_edit_wit')
        del_witness = self.top.get_widget('eer_del_wit')

        Utils.set_titles(self.window,
                         self.top.get_widget('eer_title'),
                         self.title)
        
        self.top.signal_autoconnect({
            "on_eer_help_clicked"   : self.on_help_clicked,
            "on_eer_ok_clicked"     : self.on_ok_clicked,
            "on_eer_cancel_clicked" : self.close,
            "on_eer_delete_event"   : self.on_delete_event,
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
            self.date = Date.Date(self.event.get_date_object())
            self.expander.set_expanded(False)
        else:
            trans = self.db.transaction_begin()
            self.event = RelLib.Event()
            self.event.set_type((default_type,ev_dict[default_type]))
            self.db.add_event(self.event,trans)
            self.db.transaction_commit(trans,_("Add Event"))
            self.date = Date.Date(None)
            self.expander.set_expanded(True)

        if not self.event_ref:
            self.event_ref = RelLib.EventRef()
            self.event_ref.set_role((default_role,role_dict[default_role]))
            self.event_ref.set_reference_handle(self.event.get_handle())

        self.srcreflist = self.event.get_source_references()
        self.sourcetab = Sources.SourceTab(
            self.srcreflist, self, self.top, self.window, self.slist,
            add_src, self.top.get_widget('eer_edit_src'), del_src,
            self.db.readonly)

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
        if self.event.get_note():
            self.ev_note_field.get_buffer().set_text(event.get_note())
            Utils.bold_label(self.notes_label)
            if event.get_note_format() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)
        if self.event.get_media_list():
            Utils.bold_label(self.gallery_label)

        self.add_itself_to_menu()
        try:
            self.window.set_transient_for(self.parent.window)
        except AttributeError:
            pass
        self.window.show()

    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()

    def close(self,obj):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.window.destroy()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.win_parent.child_windows[self.win_key] = self
        label = _('Event Reference')
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.win_parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(self.title)
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.win_parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

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
        self.update_event(etype,self.date,eplace_obj,edesc,enote,eformat,
                          epriv,ecause)
        # event is a primary object, so its change has to be committed now
        if self.parent.lists_changed:
            trans = self.db.transaction_begin()
            self.db.commit_event(self.event,trans)
            self.db.transaction_commit(trans,_("Modify Event"))
        
        # then, set properties of the event_ref
        self.event_ref.set_role(self.role_selector.get_values())
        self.event_ref.set_privacy(self.ref_privacy.get_active())
        buf = self.ref_note_field.get_buffer()
        start = buf.get_start_iter()
        stop = buf.get_end_iter()
        note = unicode(buf.get_text(start,stop,False))
        self.event_ref.set_note(note)
        #self.referent.add_event_ref(self.event_ref)
        self.close(None)

        if self.update:
            self.update((self.event_ref,self.event))

    def update_event(self,the_type,date,place,desc,note,format,priv,cause):
        if place:
            if self.event.get_place_handle() != place.get_handle():
                self.event.set_place_handle(place.get_handle())
                self.parent.lists_changed = 1
        else:
            if self.event.get_place_handle():
                self.event.set_place_handle("")
                self.parent.lists_changed = 1
        
        if self.event.get_type() != the_type:
            self.event.set_type(the_type)
            self.parent.lists_changed = 1
        
        if self.event.get_description() != desc:
            self.event.set_description(desc)
            self.parent.lists_changed = 1

        if self.event.get_note() != note:
            self.event.set_note(note)
            self.parent.lists_changed = 1

        if self.event.get_note_format() != format:
            self.event.set_note_format(format)
            self.parent.lists_changed = 1

        dobj = self.event.get_date_object()

        self.event.set_source_reference_list(self.srcreflist)
        
        if not dobj.is_equal(date):
            self.event.set_date_object(date)
            self.parent.lists_changed = 1

        if self.event.get_cause() != cause:
            self.event.set_cause(cause)
            self.parent.lists_changed = 1

        if self.event.get_privacy() != priv:
            self.event.set_privacy(priv)
            self.parent.lists_changed = 1

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
