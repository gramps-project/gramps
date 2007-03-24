#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Config
import RelLib
import GrampsDisplay
from _EditPrimary import EditPrimary

from QuestionDialog import ErrorDialog
from DisplayTabs import SourceEmbedList, NoteTab, GalleryTab, EventBackRefList, AttrEmbedList
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# EditEvent class
#
#-------------------------------------------------------------------------
class EditEvent(EditPrimary):

    def __init__(self,dbstate,uistate,track,event,callback=None):

        EditPrimary.__init__(self, dbstate, uistate, track,
                             event, dbstate.db.get_event_from_handle)

        self._init_event()

    def _init_event(self):
        self.commit_event = self.db.commit_event

    def empty_object(self):
        return RelLib.Event()

    def get_menu_title(self):
        if self.obj.get_handle():
            event_name = self.obj.get_description()
            if not event_name:
                event_name = str(self.obj.get_type())
            dialog_title = _('Event: %s')  % event_name
        else:
            dialog_title = _('New Event')
        return dialog_title

    def get_custom_events(self):
        return self.dbstate.db.get_person_event_types() + \
               self.dbstate.db.get_family_event_types()

    def _local_init(self):
        self.top = gtk.glade.XML(const.gladeFile, "event_edit","gramps")
        self.set_window(self.top.get_widget("event_edit"), None, 
                        self.get_menu_title())

        self.place = self.top.get_widget('place')
        self.share_btn = self.top.get_widget('select_place')
        self.add_del_btn = self.top.get_widget('add_del_place')

        width = Config.get(Config.EVENT_WIDTH)
        height = Config.get(Config.EVENT_HEIGHT)
        self.window.resize(width, height)

    def _connect_signals(self):
        self.top.get_widget('button111').connect('clicked',self.close)
        self.top.get_widget('button126').connect('clicked',self.help_clicked)

        ok = self.top.get_widget('ok')
        ok.set_sensitive(not self.db.readonly)
        ok.connect('clicked',self.save)

    def _setup_fields(self):

        # place, select_place, add_del_place
        
        self.place_field = PlaceEntry(
            self.dbstate,
            self.uistate,
            self.track,
            self.top.get_widget("place"),
            self.obj.set_place_handle,
            self.obj.get_place_handle,
            self.add_del_btn,
            self.share_btn)
        
        self.descr_field = MonitoredEntry(
            self.top.get_widget("event_description"),
            self.obj.set_description,
            self.obj.get_description, self.db.readonly)

        self.gid = MonitoredEntry(
            self.top.get_widget("gid"),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.obj, self.db.readonly)

        self.event_menu = MonitoredDataType(
            self.top.get_widget("personal_events"),
            self.obj.set_type,
            self.obj.get_type,
            custom_values=self.get_custom_events())

        self.date_field = MonitoredDate(
            self.top.get_widget("date_entry"),
            self.top.get_widget("date_stat"),
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        """
        notebook = gtk.Notebook()
        
        self.srcref_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate,self.track,self.obj))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_list()))
        
        self.gallery_tab = self._add_tab(
            notebook,
            GalleryTab(self.dbstate, self.uistate, self.track,
                       self.obj.get_media_list()))

        self.backref_tab = self._add_tab(
            notebook,
            EventBackRefList(self.dbstate, self.uistate, self.track,
                             self.dbstate.db.find_backlink_handles(self.obj.handle)))

        try:
            self.attr_ref_list = self._add_tab(
                notebook,
                AttrEmbedList(self.dbstate, self.uistate, self.track,
                              self.obj.get_attribute_list()))
        except AttributeError:
            print "Attribute list not available yet"
        

        self._setup_notebook_tabs( notebook)
        
        notebook.show_all()
        self.top.get_widget('vbox').pack_start(notebook,True)

    def _cleanup_on_exit(self):
        self.backref_tab.close()
        (width, height) = self.window.get_size()
        Config.set(Config.EVENT_WIDTH, width)
        Config.set(Config.EVENT_HEIGHT, height)
        Config.sync()

    def build_menu_names(self,event):
        return (_('Edit Event'), self.get_menu_title())

    def help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-ev')

    def save(self,*obj):
        if self.object_is_empty():
            ErrorDialog(_("Cannot save event"),
                        _("No data exists for this event. Please "
                          "enter data or cancel the edit."))
            return

        t = self.obj.get_type()
        if t.is_custom() and str(t) == '':
            ErrorDialog(
                _("Cannot save event"),
                _("The event type cannot be empty"))
            return

        if self.obj.handle == None:
            trans = self.db.transaction_begin()
            self.db.add_event(self.obj,trans)
            self.db.transaction_commit(trans,_("Add Event"))
        else:
            orig = self.dbstate.db.get_event_from_handle(self.obj.handle)
            if cmp(self.obj.serialize(),orig.serialize()):
                trans = self.db.transaction_begin()
                self.commit_event(self.obj,trans)
                self.db.transaction_commit(trans,_("Edit Event"))

        if self.callback:
            self.callback(self.obj)
        self.close()

    def data_has_changed(self):
        """
        A date comparison can fail incorrectly because we have made the
        decision to store entered text in the date. However, there is no
        entered date when importing from a XML file, so we can get an
        incorrect fail.
        """
        
        if self.db.readonly:
            return False
        elif self.obj.handle:
            orig = self.get_from_handle(self.obj.handle)
            if orig:
                cmp_obj = orig
            else:
                cmp_obj = self.empty_object()
            return cmp(cmp_obj.serialize(True)[1:],
                       self.obj.serialize(True)[1:]) != 0
        else:
            cmp_obj = self.empty_object()
            return cmp(cmp_obj.serialize(True)[1:],
                       self.obj.serialize()[1:]) != 0


class EditPersonEvent(EditEvent):

    def __init__(self, dbstate, uistate, track, event, callback=None):
        EditEvent.__init__(self, dbstate, uistate, track, event, callback)

    def _init_event(self):
        self.commit_event = self.db.commit_personal_event

    def get_custom_events(self):
        return self.dbstate.db.get_person_event_types()

class EditFamilyEvent(EditEvent):

    def __init__(self, dbstate, uistate, track, event, callback=None):
        EditEvent.__init__(self, dbstate, uistate, track, event, callback)

    def _init_event(self):
        self.commit_event = self.db.commit_family_event

    def get_custom_events(self):
        return self.dbstate.db.get_family_event_types()

#-------------------------------------------------------------------------
#
# Delete Query class
#
#-------------------------------------------------------------------------
class DelEventQuery:
    def __init__(self,dbstate,uistate,event,person_list,family_list):
        self.event = event
        self.db = dbstate.db
        self.uistate = uistate
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
