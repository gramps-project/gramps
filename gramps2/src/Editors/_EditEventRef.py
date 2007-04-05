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

from DisplayTabs import SourceEmbedList,NoteTab,GalleryTab,EventBackRefList,AttrEmbedList
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

    WIDTH_KEY = Config.EVENT_REF_WIDTH
    HEIGHT_KEY = Config.EVENT_REF_HEIGHT

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
        self.share_btn = self.top.get_widget('share_place')
        self.add_del_btn = self.top.get_widget('add_del_place')
                              
    def _init_event(self):
        self.commit_event = self.db.commit_personal_event
        self.add_event = self.db.add_person_event

    def get_custom_events(self):
        return self.db.get_person_event_types()

    def _connect_signals(self):
        self.define_ok_button(self.top.get_widget('ok'),self.ok_clicked)
        self.define_cancel_button(self.top.get_widget('cancel'))
	# FIXME: activate when help page is available
	#self.define_help_button(self.top.get_widget('help'), 'tag')

    def _setup_fields(self):
        
        self.ref_privacy = PrivacyButton(
            self.top.get_widget('eer_ref_priv'),
            self.source_ref, self.db.readonly)

        self.descr_field = MonitoredEntry(
            self.top.get_widget("eer_description"),
            self.source.set_description,
            self.source.get_description,
            self.db.readonly)

        self.gid = MonitoredEntry(
            self.top.get_widget("gid"),
            self.source.set_gramps_id,
            self.source.get_gramps_id,
            self.db.readonly)

        self.place_field = PlaceEntry(
            self.dbstate,
            self.uistate,
            self.track,
            self.top.get_widget("eer_place"),
            self.source.set_place_handle,
            self.source.get_place_handle,
            self.add_del_btn,
            self.share_btn)

        self.ev_privacy = PrivacyButton(
            self.top.get_widget("eer_ev_priv"),
            self.source, self.db.readonly)
                
        self.role_selector = MonitoredDataType(
            self.top.get_widget('eer_role_combo'),
            self.source_ref.set_role,
            self.source_ref.get_role,
            self.db.readonly,
            self.db.get_event_roles()
            )

        self.event_menu = MonitoredDataType(
            self.top.get_widget("eer_type_combo"),
            self.source.set_type,
            self.source.get_type,
            self.db.readonly,
            custom_values=self.get_custom_events())

        table = self.top.get_widget('table62')
	date_entry = ValidatableMaskedEntry(str)
        date_entry.show()
        table.attach(date_entry, 1, 2, 1, 2)

        self.date_check = MonitoredDate(
            date_entry,
            self.top.get_widget("eer_date_stat"),
            self.source.get_date_object(),
            self.uistate,
            self.track,
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
            SourceEmbedList(self.dbstate,self.uistate,self.track,self.source))

        try:
            self.attr_list = self._add_tab(
                notebook,
                AttrEmbedList(self.dbstate, self.uistate, self.track,
                              self.source.get_attribute_list()))
        except AttributeError:
            print "Attribute list not available yet"
        
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

        try:
            self.attr_ref_list = self._add_tab(
                notebook_ref,
                AttrEmbedList(self.dbstate, self.uistate, self.track,
                              self.source_ref.get_attribute_list()))
        except AttributeError:
            print "Attribute list not available yet"

        self._setup_notebook_tabs( notebook)
        self._setup_notebook_tabs( notebook_ref)

    def build_menu_names(self,eventref):
        if self.source:
            event_name = str(self.source.get_type())
            submenu_label = _('Event: %s')  % event_name
        else:
            submenu_label = _('New Event')
        return (_('Event Reference Editor'),submenu_label)
        
    def ok_clicked(self,obj):

        trans = self.db.transaction_begin()
        if self.source.handle:
            self.commit_event(self.source,trans)
            self.db.transaction_commit(trans,_("Modify Event"))
        else:
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
