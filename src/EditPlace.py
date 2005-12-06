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
import ImageSelect
import NameDisplay
import DisplayState
import Spell
import GrampsDisplay
import RelLib
import ListModel

from DdTargets import DdTargets
from WindowUtils import GladeIf

#-------------------------------------------------------------------------
#
# EditPlace
#
#-------------------------------------------------------------------------
class EditPlace(DisplayState.ManagedWindow):

<<<<<<< EditPlace.py
    def __init__(self,place,dbstate,uistate):
        self.dbstate = dbstate
        self.uistate = uistate

        self.ref_not_loaded = place and place.get_handle()
        self.idle = None
        self.name_display = NameDisplay.displayer.display
        self.place = place
        self.db = dbstate.db
        self.path = dbstate.db.get_save_path()
        self.not_loaded = True
        self.lists_changed = 0
        if place:
            self.srcreflist = place.get_source_references()
        else:
            self.srcreflist = []

        self.top_window = gtk.glade.XML(const.placesFile,"placeEditor","gramps")
        self.gladeif = GladeIf(self.top_window)

        self.top = self.top_window.get_widget("placeEditor")
        self.iconlist = self.top_window.get_widget('iconlist')
        title_label = self.top_window.get_widget('title')

        Utils.set_titles(self.top,title_label,_('Place Editor'))

        self.glry = ImageSelect.Gallery(place, self.db.commit_place, self.path,
                                        self.iconlist, self.db, self,self.top)

        mode = not self.dbstate.db.readonly
        self.title = self.top_window.get_widget("place_title")
        self.title.set_editable(mode)
        self.city = self.top_window.get_widget("city")
        self.city.set_editable(mode)
        self.parish = self.top_window.get_widget("parish")
        self.parish.set_editable(mode)
        self.county = self.top_window.get_widget("county")
        self.county.set_editable(mode)
        self.state = self.top_window.get_widget("state")
        self.state.set_editable(mode)
        self.phone = self.top_window.get_widget("phone")
        self.phone.set_editable(mode)
        self.postal = self.top_window.get_widget("postal")
        self.postal.set_editable(mode)
        self.country = self.top_window.get_widget("country")
        self.country.set_editable(mode)
        self.longitude = self.top_window.get_widget("longitude")
        self.longitude.set_editable(mode)
        self.latitude = self.top_window.get_widget("latitude")
        self.latitude.set_editable(mode)
        self.note = self.top_window.get_widget("place_note")
        self.note.set_editable(mode)
        self.spell = Spell.Spell(self.note)

        self.web_list = self.top_window.get_widget("web_list")
        self.web_url = self.top_window.get_widget("web_url")
        self.web_go = self.top_window.get_widget("web_go")
        self.web_edit = self.top_window.get_widget("web_edit")
        self.web_description = self.top_window.get_widget("url_des")

        self.top_window.get_widget('changed').set_text(place.get_change_display())

        # event display
        self.web_model = gtk.ListStore(str,str)
        self.build_columns(self.web_list, [(_('Path'),150),
                                           (_('Description'),150)])
        self.web_list.set_model(self.web_model)
        self.web_list.get_selection().connect('changed',
                                              self.on_web_list_select_row)
        
        self.loc_edit = self.top_window.get_widget("loc_edit")
        self.loc_list = self.top_window.get_widget("loc_list")
        self.loc_city = self.top_window.get_widget("loc_city")
        self.loc_county = self.top_window.get_widget("loc_county")
        self.loc_state  = self.top_window.get_widget("loc_state")
        self.loc_postal = self.top_window.get_widget("loc_postal")
        self.loc_phone  = self.top_window.get_widget("loc_phone")
        self.loc_parish  = self.top_window.get_widget("loc_parish")
        self.loc_country = self.top_window.get_widget("loc_country")

        self.ulist = place.get_url_list()[:]
        self.llist = place.get_alternate_locations()[:]

        self.loc_model = gtk.ListStore(str,str,str,str)
        self.build_columns(self.loc_list, [(_('City'),150), (_('County'),100),
                                           (_('State'),100), (_('Country'),50)])
        self.loc_list.set_model(self.loc_model)
        self.loc_sel = self.loc_list.get_selection()
        self.loc_sel.connect('changed',self.on_loc_list_select_row)

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
        self.plist = self.top_window.get_widget("plist")
        self.slist = self.top_window.get_widget("slist")
        self.sources_label = self.top_window.get_widget("sourcesPlaceEdit")
        self.names_label = self.top_window.get_widget("namesPlaceEdit")
        self.notes_label = self.top_window.get_widget("notesPlaceEdit")
        self.gallery_label = self.top_window.get_widget("galleryPlaceEdit")
        self.inet_label = self.top_window.get_widget("inetPlaceEdit")
        self.refs_label = self.top_window.get_widget("refsPlaceEdit")
        self.flowed = self.top_window.get_widget("place_flowed")
        self.preform = self.top_window.get_widget("place_preform")

        self.note_buffer = self.note.get_buffer()
        if place.get_note():
            self.note_buffer.set_text(place.get_note())
            Utils.bold_label(self.notes_label)
            if place.get_note_format() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)
        else:
            Utils.unbold_label(self.notes_label)

        self.flowed.set_sensitive(mode)
        self.preform.set_sensitive(mode)

        if self.place.get_media_list():
            Utils.bold_label(self.gallery_label)
        else:
            Utils.unbold_label(self.gallery_label)

        self.gladeif.connect('placeEditor', 'delete_event', self.on_delete_event)
        self.gladeif.connect('button127', 'clicked', self.close)
        self.gladeif.connect('ok', 'clicked', self.on_place_apply_clicked)
        self.gladeif.connect('button135', 'clicked', self.on_help_clicked)
        self.gladeif.connect('notebook3', 'switch_page', self.on_switch_page)
        self.gladeif.connect('add_name', 'clicked', self.on_add_loc_clicked)
        self.gladeif.connect('loc_edit', 'clicked', self.on_update_loc_clicked)
        self.gladeif.connect('del_name', 'clicked', self.on_delete_loc_clicked)
        self.gladeif.connect('add_photo', 'clicked', self.glry.on_add_media_clicked)
        self.gladeif.connect('sel_photo', 'clicked', self.glry.on_select_media_clicked)
        self.gladeif.connect('button134', 'clicked', self.glry.on_edit_media_clicked)
        self.gladeif.connect('delete_photo', 'clicked', self.glry.on_delete_media_clicked)
        self.gladeif.connect('add_url', 'clicked', self.on_add_url_clicked)
        self.gladeif.connect('web_edit', 'clicked', self.on_update_url_clicked)
        self.gladeif.connect('web_go', 'clicked', self.on_web_go_clicked)
        self.gladeif.connect('del_url', 'clicked', self.on_delete_url_clicked)
        
        self.sourcetab = Sources.SourceTab(
            self.srcreflist,self,
            self.top_window,self.top,self.slist,
            self.top_window.get_widget('add_src'),
            self.top_window.get_widget('edit_src'),
            self.top_window.get_widget('del_src'),
            self.dbstate.db.readonly)
        
        if self.place.get_handle() == None or self.dbstate.db.readonly:
            self.top_window.get_widget("add_photo").set_sensitive(0)
            self.top_window.get_widget("delete_photo").set_sensitive(0)

        self.web_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                    [DdTargets.URL.target()],
                                    gtk.gdk.ACTION_COPY)
        self.web_list.drag_source_set(gtk.gdk.BUTTON1_MASK,
                                      [DdTargets.URL.target()],
                                      gtk.gdk.ACTION_COPY)
        self.web_list.connect('drag_data_get',
                              self.url_source_drag_data_get)
        if not self.db.readonly:
            self.web_list.connect('drag_data_received',
                              self.url_dest_drag_data_received)

        for name in ['del_name','add_name','sel_photo','add_url','del_url']:
            self.top_window.get_widget(name).set_sensitive(mode)

        self.redraw_url_list()
        self.redraw_location_list()
        self.top_window.get_widget('ok').set_sensitive(not self.db.readonly)
        self.top.show()

        win_menu_label = place.get_title()
        if not win_menu_label.strip():
            win_menu_label = _("New Place")

        DisplayState.ManagedWindow.__init__(
            self, uistate, [], self, win_menu_label, _('Edit Place'))

        self.pdmap = {}
        self.build_pdmap()
        
        if self.ref_not_loaded:
            Utils.temp_label(self.refs_label,self.top)
            self.cursor_type = None
            self.idle = gobject.idle_add(self.display_references)
            self.ref_not_loaded = False

    def build_pdmap(self):
        self.pdmap.clear()
        cursor = self.db.get_place_cursor()
        data = cursor.next()
        while data:
            if data[1][2]:
                self.pdmap[data[1][2]] = data[0]
            data = cursor.next()
        cursor.close()

    def on_delete_event(self,obj,b):
        self.gladeif.close()
        self.glry.close()
        self.remove_itself_from_menu()
        gc.collect()

    def close(self,obj):
        self.glry.close()
        self.gladeif.close()
        self.top.destroy()
        if self.idle != None:
            gobject.source_remove(self.idle)
        gc.collect()

    def present(self,obj):
        self.top.present()

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

    def url_dest_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'place = "%s"' % data[1]
            if place == self.place.get_handle() or mytype != 'url':
                return
            foo = pickle.loads(data[2]);
            self.ulist.append(foo)
            self.lists_changed = 1
            self.redraw_url_list()

    def url_source_drag_data_get(self,widget, context, sel_data, info, time):
        store,node = self.web_list.get_selection().get_selected()
        if not node:
            return
        row = store.get_path(node)
        url = self.ulist[row[0]]
        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(url)
        data = str(('url',self.place.get_handle(),pickled))
        sel_data.set(sel_data.target, bits_per, data)

    def update_lists(self):
        self.place.set_url_list(self.ulist)
        self.place.set_alternate_locations(self.llist)
            
    def redraw_url_list(self):
        length = Utils.redraw_list(self.ulist,self.web_model,disp_url)
        if length > 0:
            self.web_go.set_sensitive(1)
            self.web_edit.set_sensitive(1)
            Utils.bold_label(self.inet_label)
        else:
            self.web_edit.set_sensitive(0)
            self.web_go.set_sensitive(0)
            self.web_url.set_text("")
            self.web_description.set_text("")
            Utils.unbold_label(self.inet_label)

    def redraw_location_list(self):
        Utils.redraw_list(self.llist,self.loc_model,disp_loc)
        if len(self.llist) > 0:
            self.loc_edit.set_sensitive(1)
            Utils.bold_label(self.names_label)
        else:
            self.loc_edit.set_sensitive(0)
            Utils.unbold_label(self.names_label)

    def on_web_go_clicked(self,obj):
        text = self.web_url.get()
        if text != "":
            GrampsDisplay.url(text)

    def set(self,field,getf,setf):
        text = unicode(field.get_text())
        if text != getf():
            setf(text)
    
    def on_place_apply_clicked(self,obj):

        note = unicode(self.note_buffer.get_text(self.note_buffer.get_start_iter(),
                                 self.note_buffer.get_end_iter(),False))
        format = self.preform.get_active()
        mloc = self.place.get_main_location()

        title = self.title.get_text()
        if self.pdmap.has_key(title) and self.pdmap[title] != self.place.handle:
            import QuestionDialog
            QuestionDialog.ErrorDialog(_("Place title is already in use"),
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

        if self.lists_changed:
            self.place.set_source_reference_list(self.srcreflist)
        
        if note != self.place.get_note():
            self.place.set_note(note)

        if format != self.place.get_note_format():
            self.place.set_note_format(format)

        self.update_lists()

        trans = self.db.transaction_begin()
        if self.place.get_handle():
            self.db.commit_place(self.place,trans)
        else:
            self.db.add_place(self.place,trans)
        self.db.transaction_commit(trans,
                                   _("Edit Place (%s)") % self.place.get_title())
        
        self.close(obj)

    def on_switch_page(self,obj,a,page):
        if page == 4 and self.not_loaded:
            self.not_loaded = False
            self.glry.load_images()
        elif page == 6 and self.ref_not_loaded:
            self.ref_not_loaded = False
            Utils.temp_label(self.refs_label,self.top)
            self.idle = gobject.idle_add(self.display_references)
        text = unicode(self.note_buffer.get_text(self.note_buffer.get_start_iter(),
                                self.note_buffer.get_end_iter(),False))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)

    def on_update_url_clicked(self,obj):
        import UrlEdit
        store,node = self.web_list.get_selection().get_selected()
        if node:
            row = store.get_path(node)
            url = self.ulist[row[0]]
            name = ""
            if self.place:
            	name = self.place.get_title()
            UrlEdit.UrlEditor(self,name,url,self.url_edit_callback)

    def on_update_loc_clicked(self,obj):
        import LocEdit

        store,node = self.loc_sel.get_selected()
        if node:
            row = store.get_path(node)
            loc = self.llist[row[0]]
            LocEdit.LocationEditor(self,loc,self.top)

    def on_delete_url_clicked(self,obj):
        if Utils.delete_selected(self.web_list,self.ulist):
            self.lists_changed = 1
            self.redraw_url_list()

    def on_delete_loc_clicked(self,obj):
        if Utils.delete_selected(self.loc_list,self.llist):
            self.lists_changed = 1
            self.redraw_location_list()

    def on_add_url_clicked(self,obj):
        import UrlEdit
        name = ""
        if self.place:
            name = self.place.get_title()
        UrlEdit.UrlEditor(self,name,None,self.url_edit_callback)

    def url_edit_callback(self,url):
        self.redraw_url_list()

    def on_add_loc_clicked(self,obj):
        import LocEdit
        LocEdit.LocationEditor(self,None,self.top)

    def on_web_list_select_row(self,obj):
        store,node = obj.get_selected()
        if not node:
            self.web_url.set_text("")
            self.web_go.set_sensitive(0)
            self.web_description.set_text("")
        else:
            row = store.get_path(node)
            url = self.ulist[row[0]]
            path = url.get_path()
            self.web_url.set_text(path)
            self.web_go.set_sensitive(1)
            self.web_description.set_text(url.get_description())

    def on_loc_list_select_row(self,obj):
        store,node = self.loc_sel.get_selected()
        if not node:
            self.loc_city.set_text('')
            self.loc_county.set_text('')
            self.loc_state.set_text('')
            self.loc_postal.set_text('')
            self.loc_phone.set_text('')
            self.loc_parish.set_text('')
            self.loc_country.set_text('')
        else:
            row = store.get_path(node)
            loc = self.llist[row[0]]

            self.loc_city.set_text(loc.get_city())
            self.loc_county.set_text(loc.get_county())
            self.loc_state.set_text(loc.get_state())
            self.loc_postal.set_text(loc.get_postal_code())
            self.loc_phone.set_text(loc.get_phone())
            self.loc_parish.set_text(loc.get_parish())
            self.loc_country.set_text(loc.get_country())

    def button_press(self,obj):
        data = self.model.get_selected_objects()
        if not data:
            return
        (data_type,handle) = data[0]
        import EventEdit
        event = self.db.get_event_from_handle(handle)
        event_name = event.get_name()
        if data_type == 0:
            if event_name in ["Birth","Death"]:
                EventEdit.PersonEventEditor(
                    self,", ", event, None, 1, None, None, self.db.readonly)
            else:
                EventEdit.PersonEventEditor(
                    self,", ", event, None, 0, None, None, self.db.readonly)
        elif data_type == 1:
            EventEdit.FamilyEventEditor(
                self,", ", event, None, 0, None, None, self.db.readonly)

    def display_references(self):
        place_handle = self.place.get_handle()
        # Initialize things if we're entering this functioin
        # for the first time
        if not self.cursor_type:
            self.cursor_type = 'Person'
            self.cursor = self.db.get_person_cursor()
            self.data = self.cursor.first()
        
            self.any_refs = False
            titles = [(_('Type'),0,150),(_('Name'),1,150),
                      (_('ID'),2,75),(_('Event Name'),3,150)]
            self.model = ListModel.ListModel(self.plist,
                                             titles,
                                             event_func=self.button_press)

        if self.cursor_type == 'Person':
            while self.data:
                handle,val = self.data
                person = RelLib.Person()
                person.unserialize(val)
                for event_handle in [person.get_birth_handle(),
                                     person.get_death_handle()] \
                                     + person.get_event_list():
                    event = self.db.get_event_from_handle(event_handle)
                    if event and event.get_place_handle() == place_handle:
                        pname = self.name_display(person)
                        gramps_id = person.get_gramps_id()
                        ename = event.get_name()
                        self.model.add(
                            [_("Personal Event"),pname,gramps_id,ename],
                            (0,event_handle))
                        self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()
            
            self.cursor_type = 'Family'
            self.cursor = self.db.get_family_cursor()
            self.data = self.cursor.first()

        if self.cursor_type == 'Family':
            while self.data:
                handle,val = self.data
                family = RelLib.Family()
                family.unserialize(val)
                for event_handle in family.get_event_list():
                    event = self.db.get_event_from_handle(event_handle)
                    if event and event.get_place_handle() == place_handle:
                        father = family.get_father_handle()
                        mother = family.get_mother_handle()
                        if father and mother:
                            fname = _("%(father)s and %(mother)s")  % {
                                "father" : self.name_display(
                                self.db.get_person_from_handle(father)),
                                "mother" : self.name_display(
                                self.db.get_person_from_handle(mother))
                                }
                        elif father:
                            fname = self.name_display(
                                self.db.get_person_from_handle(father))
                        else:
                            fname = self.name_display(
                                self.db.get_person_from_handle(mother))

                        gramps_id = family.get_gramps_id()
                        ename = event.get_name()
                        self.model.add(
                            [_("Family Event"),fname,gramps_id,ename],
                            (1,event_handle))
                        self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()

        if self.any_refs:
            Utils.bold_label(self.refs_label,self.top)
        else:
            Utils.unbold_label(self.refs_label,self.top)

        self.ref_not_loaded = 0
        self.cursor_type = None
        return False
        
#-------------------------------------------------------------------------
#
# disp_url
#
#-------------------------------------------------------------------------
def disp_url(url):
    return [url.get_path(),url.get_description()]

#-------------------------------------------------------------------------
#
# disp_loc
#
#-------------------------------------------------------------------------
def disp_loc(loc):
    return [loc.get_city(),loc.get_county(),loc.get_state(),loc.get_country()]

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
