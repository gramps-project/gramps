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
# python modules
#
#-------------------------------------------------------------------------
import cPickle as pickle
import gc
from gettext import gettext as _
import sys

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
import Sources
import NameDisplay
import DisplayState
import Spell
import GrampsDisplay
import RelLib
import ListModel

from DdTargets import DdTargets
from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# EditPlace
#
#-------------------------------------------------------------------------
class EditPlace(DisplayState.ManagedWindow):

    def __init__(self,dbstate,uistate,track,place):
        self.dbstate = dbstate

        DisplayState.ManagedWindow.__init__(self, uistate, track, place)

        self.name_display = NameDisplay.displayer.display
        self.place = place
        self.db = dbstate.db

        self.top = gtk.glade.XML(const.gladeFile,"placeEditor","gramps")

        self.window = self.top.get_widget("placeEditor")
        title_label = self.top.get_widget('title')

        Utils.set_titles(self.window,title_label,_('Place Editor'))

        self.top.get_widget('changed').set_text(place.get_change_display())

        self.notebook = self.top.get_widget('notebook3')

        self._create_tabbed_pages()
        self._setup_fields()
        self._connect_signals()
        self.show()

        self.pdmap = {}
        self.build_pdmap()

    def _connect_signals(self):
        self.top.get_widget('placeEditor').connect('delete_event', self.delete_event)
        self.top.get_widget('button127').connect('clicked', self.close)
        self.top.get_widget('button135').connect('clicked', self.help_clicked)
        ok = self.top.get_widget('ok')
        ok.connect('clicked', self.apply_clicked)
        ok.set_sensitive(not self.db.readonly)

    def _setup_fields(self):
        mloc = self.place.get_main_location()
        
        self.title = MonitoredEntry(
            self.top.get_widget("place_title"),
            self.place.set_title, self.place.get_title,
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
            mloc.set_country, mloc.get_county, self.db.readonly)
        
        self.longitude = MonitoredEntry(
            self.top.get_widget("longitude"),
            self.place.set_longitude, self.place.get_longitude,
            self.db.readonly)

        self.latitude = MonitoredEntry(
            self.top.get_widget("latitude"),
            self.place.set_latitude, self.place.get_latitude,
            self.db.readonly)
        

    def build_window_key(self,place):
        if place:
            return place.get_handle()
        else:
            return id(self)

    def build_menu_names(self,place):
        win_menu_label = place.get_title()
        if not win_menu_label.strip():
            win_menu_label = _("New Place")
        return (win_menu_label, _('Edit Place'))

    def build_pdmap(self):
        self.pdmap.clear()
        cursor = self.db.get_place_cursor()
        data = cursor.next()
        while data:
            if data[1][2]:
                self.pdmap[data[1][2]] = data[0]
            data = cursor.next()
        cursor.close()

    def _add_page(self,page):
        self.notebook.insert_page(page)
        self.notebook.set_tab_label(page,page.get_tab_widget())
        return page

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        
        """
        self.loc_list = self._add_page(LocationEmbedList(
            self.dbstate,self.uistate, self.track,
            self.place.alt_loc))
        self.srcref_list = self._add_page(SourceEmbedList(
            self.dbstate,self.uistate, self.track,
            self.place.source_list))
        self.note_tab = self._add_page(NoteTab(
            self.dbstate, self.uistate, self.track,
            self.place.get_note_object()))
        self.gallery_tab = self._add_page(GalleryTab(
            self.dbstate, self.uistate, self.track,
            self.place.get_media_list()))
        self.web_list = self._add_page(WebEmbedList(
            self.dbstate,self.uistate,self.track,
            self.place.get_url_list()))
        self.backref_list = self._add_page(PlaceBackRefList(
            self.dbstate,self.uistate,self.track,
            self.db.find_backlink_handles(self.place.handle)))

    def delete_event(self,obj,b):
        self.close()

    def close_window(self,obj):
        self.close()
        self.window.destroy()

    def help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-plc')

    def build_columns(self,tree,list):
        cnum = 0
        for name in list:
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(name[0],renderer,text=cnum)
            column.set_min_width(name[1])
            cnum = cnum + 1
            tree.append_column(column)

    def apply_clicked(self,obj):

        title = self.place.get_title()
        if self.pdmap.has_key(title) and self.pdmap[title] != self.place.handle:
            import QuestionDialog
            QuestionDialog.ErrorDialog(
                _("Place title is already in use"),
                _("Each place must have a unique title, and "
                  "title you have selected is already used by "
                  "another place"))
            return

        trans = self.db.transaction_begin()
        if self.place.get_handle():
            self.db.commit_place(self.place,trans)
        else:
            self.db.add_place(self.place,trans)
        self.db.transaction_commit(trans,
                                   _("Edit Place (%s)") % self.place.get_title())
        
        self.close(obj)

#-------------------------------------------------------------------------
#
# DeletePlaceQuery
#
#-------------------------------------------------------------------------
class DeletePlaceQuery:

    def __init__(self,place,db):
        self.db = db
        self.place = place
        
    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        place_handle = self.place.get_handle()

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
                                   _("Delete Place (%s)") % self.place.get_title())
