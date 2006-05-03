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
# python modules
#
#-------------------------------------------------------------------------
import cPickle as pickle
from gettext import gettext as _

import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
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
from _EditPrimary import EditPrimary

from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# EditPlace
#
#-------------------------------------------------------------------------
class EditPlace(EditPrimary):

    def __init__(self,dbstate,uistate,track,place,callback=None):
        EditPrimary.__init__(self, dbstate, uistate, track, place,
                             dbstate.db.get_place_from_handle, callback)

    def empty_object(self):
        return RelLib.Place()

    def _local_init(self):
        self.top = gtk.glade.XML(const.gladeFile,"place_editor","gramps")

        self.set_window(self.top.get_widget("place_editor"),
                        self.top.get_widget('title'),
                        _('Place Editor'))

    def _connect_signals(self):
        self.define_ok_button(self.top.get_widget('ok'),self.save)
        self.define_cancel_button(self.top.get_widget('cancel'))
        self.define_help_button(self.top.get_widget('help'),'adv-plc')

    def _setup_fields(self):
        mloc = self.obj.get_main_location()
        
        self.top.get_widget('changed').set_text(self.obj.get_change_display())

        self.title = MonitoredEntry(
            self.top.get_widget("place_title"),
            self.obj.set_title, self.obj.get_title,
            self.db.readonly)
        
        self.city = MonitoredEntry(
            self.top.get_widget("city"),
            mloc.set_city, mloc.get_city, self.db.readonly)
        
        self.parish = MonitoredEntry(
            self.top.get_widget("parish"),
            mloc.set_parish, mloc.get_parish, self.db.readonly)
        
        self.county = MonitoredEntry(
            self.top.get_widget("county"),
            mloc.set_county, mloc.get_county, self.db.readonly)
        
        self.state = MonitoredEntry(
            self.top.get_widget("state"),
            mloc.set_state, mloc.get_state, self.db.readonly)

        self.phone = MonitoredEntry(
            self.top.get_widget("phone"),
            mloc.set_phone, mloc.get_phone, self.db.readonly)
        
        self.postal = MonitoredEntry(
            self.top.get_widget("postal"),
            mloc.set_postal_code, mloc.get_postal_code, self.db.readonly)

        self.country = MonitoredEntry(
            self.top.get_widget("country"),
            mloc.set_country, mloc.get_country, self.db.readonly)
        
        self.longitude = MonitoredEntry(
            self.top.get_widget("longitude"),
            self.obj.set_longitude, self.obj.get_longitude,
            self.db.readonly)

        self.latitude = MonitoredEntry(
            self.top.get_widget("latitude"),
            self.obj.set_latitude, self.obj.get_latitude,
            self.db.readonly)
        
    def build_menu_names(self,place):
        win_menu_label = place.get_title()
        if not win_menu_label.strip():
            win_menu_label = _("New Place")
        return (win_menu_label, _('Edit Place'))

    def build_pdmap(self):
        self.pdmap = {}
        cursor = self.db.get_place_cursor()
        data = cursor.next()
        while data:
            if data[1][2]:
                self.pdmap[data[1][2]] = data[0]
            data = cursor.next()
        cursor.close()

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        
        """
        notebook = self.top.get_widget('notebook3')

        self.loc_list = self._add_tab(
            notebook,
            LocationEmbedList(self.dbstate,self.uistate, self.track,
                              self.obj.alt_loc))
        
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
        
        self.web_list = self._add_tab(
            notebook,
            WebEmbedList(self.dbstate,self.uistate,self.track,
                         self.obj.get_url_list()))
        
        self.backref_list = self._add_tab(
            notebook,
            PlaceBackRefList(self.dbstate,self.uistate,self.track,
                             self.db.find_backlink_handles(self.obj.handle)))

    def _cleanup_on_exit(self):
        self.backref_list.close()

    def save(self,*obj):
        title = self.obj.get_title()
        self.build_pdmap()

        if self.pdmap.has_key(title) and self.pdmap[title] != self.obj.handle:
            import QuestionDialog
            QuestionDialog.ErrorDialog(
                _("Place title is already in use"),
                _("Each place must have a unique title, and "
                  "title you have selected is already used by "
                  "another place"))
            return

        trans = self.db.transaction_begin()
        if self.obj.get_handle():
            self.db.commit_place(self.obj,trans)
        else:
            self.db.add_place(self.obj,trans)
        self.db.transaction_commit(trans,
                                   _("Edit Place (%s)") % self.obj.get_title())
        
        self.close()

#-------------------------------------------------------------------------
#
# DeletePlaceQuery
#
#-------------------------------------------------------------------------
class DeletePlaceQuery:

    def __init__(self,place,db):
        self.db = db
        self.obj = place
        
    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        place_handle = self.obj.get_handle()

        for handle in self.db.get_person_handles(sort_handles=False):
            person = self.db.get_person_from_handle(handle)
            if person.has_handle_reference('Place',place_handle):
                person.remove_handle_references('Place',place_handle)
                self.db.commit_person(person,trans)

        for handle in self.db.get_family_handles():
            family = self.db.get_family_from_handle(handle)
            if family.has_handle_reference('Place',place_handle):
                family.remove_handle_references('Place',place_handle)
                self.db.commit_family(family,trans)

        for handle in self.db.get_event_handles():
            event = self.db.get_event_from_handle(handle)
            if event.has_handle_reference('Place',place_handle):
                event.remove_handle_references('Place',place_handle)
                self.db.commit_event(event,trans)

        self.db.enable_signals()
        self.db.remove_place(place_handle,trans)
        self.db.transaction_commit(trans,
                                   _("Delete Place (%s)") % self.obj.get_title())
