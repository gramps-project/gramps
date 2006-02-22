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
from WindowUtils import GladeIf
from DisplayTabs import *

#-------------------------------------------------------------------------
#
# EditPlace
#
#-------------------------------------------------------------------------
class EditPlace(DisplayState.ManagedWindow):

    def __init__(self,dbstate,uistate,track,place):
        self.dbstate = dbstate
        self.uistate = uistate

        self.ref_not_loaded = place and place.get_handle()
        self.idle = None
        self.name_display = NameDisplay.displayer.display
        self.place = place
        self.db = dbstate.db
        self.path = dbstate.db.get_save_path()
        self.not_loaded = True
        self.model = None # becomes the model for back references.
        self.lists_changed = 0

        self.top = gtk.glade.XML(const.gladeFile,"placeEditor","gramps")
        self.gladeif = GladeIf(self.top)

        self.window = self.top.get_widget("placeEditor")
        title_label = self.top.get_widget('title')

        Utils.set_titles(self.window,title_label,_('Place Editor'))

        mode = not self.dbstate.db.readonly
        self.title = self.top.get_widget("place_title")
        self.title.set_editable(mode)
        self.city = self.top.get_widget("city")
        self.city.set_editable(mode)
        self.parish = self.top.get_widget("parish")
        self.parish.set_editable(mode)
        self.county = self.top.get_widget("county")
        self.county.set_editable(mode)
        self.state = self.top.get_widget("state")
        self.state.set_editable(mode)
        self.phone = self.top.get_widget("phone")
        self.phone.set_editable(mode)
        self.postal = self.top.get_widget("postal")
        self.postal.set_editable(mode)
        self.country = self.top.get_widget("country")
        self.country.set_editable(mode)
        self.longitude = self.top.get_widget("longitude")
        self.longitude.set_editable(mode)
        self.latitude = self.top.get_widget("latitude")
        self.latitude.set_editable(mode)

        self.top.get_widget('changed').set_text(place.get_change_display())

        self.title.set_text(place.get_title())
        mloc = place.get_main_location()
        self.city.set_text(mloc.get_city())
        self.county.set_text(mloc.get_county())
        self.state.set_text(mloc.get_state())
        self.phone.set_text(mloc.get_phone())
        self.postal.set_text(mloc.get_postal_code())
        self.parish.set_text(mloc.get_parish())
        self.country.set_text(mloc.get_country())
        self.longitude.set_text(place.get_longitude())
        self.latitude.set_text(place.get_latitude())
        self.plist = self.top.get_widget("refinfo")

        self.notebook = self.top.get_widget('notebook3')

        self.gladeif.connect('placeEditor', 'delete_event', self.on_delete_event)
        self.gladeif.connect('button127', 'clicked', self.close)
        self.gladeif.connect('ok', 'clicked', self.on_place_apply_clicked)
        self.gladeif.connect('button135', 'clicked', self.on_help_clicked)

        DisplayState.ManagedWindow.__init__(self, uistate, track, place)
        
        if self.place.get_handle() == None or self.dbstate.db.readonly:
            self.top.get_widget("add_photo").set_sensitive(0)
            self.top.get_widget("delete_photo").set_sensitive(0)

        self.top.get_widget('ok').set_sensitive(not self.db.readonly)

        self._create_tabbed_pages()
        self.show()

        self.pdmap = {}
        self.build_pdmap()
        

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
        self.backref_list = self._add_page(SourceBackRefList(
            self.dbstate,self.uistate,self.track,
            self.db.find_backlink_handles(self.place.handle)))

    def on_delete_event(self,obj,b):
        self.gladeif.close()
        self.close()

    def close_window(self,obj):
        self.gladeif.close()
        self.close()
        self.window.destroy()
        if self.idle != None:
            gobject.source_remove(self.idle)

    def on_help_clicked(self,obj):
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

    def set(self,field,getf,setf):
        text = unicode(field.get_text())
        if text != getf():
            setf(text)
    
    def on_place_apply_clicked(self,obj):

        mloc = self.place.get_main_location()
        title = self.title.get_text()
        if self.pdmap.has_key(title) and self.pdmap[title] != self.place.handle:
            import QuestionDialog
            QuestionDialog.ErrorDialog(
                _("Place title is already in use"),
                _("Each place must have a unique title, and "
                  "title you have selected is already used by "
                  "another place"))
            return

        self.set(self.city,mloc.get_city,mloc.set_city)
        self.set(self.parish,mloc.get_parish,mloc.set_parish)
        self.set(self.state,mloc.get_state,mloc.set_state)
        self.set(self.phone,mloc.get_phone,mloc.set_phone)
        self.set(self.postal,mloc.get_postal_code,mloc.set_postal_code)
        self.set(self.county,mloc.get_county,mloc.set_county)
        self.set(self.country,mloc.get_country,mloc.set_country)
        self.set(self.title,self.place.get_title,self.place.set_title)
        self.set(self.longitude,self.place.get_longitude,
                 self.place.set_longitude)
        self.set(self.latitude,self.place.get_latitude,
                 self.place.set_latitude)

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
