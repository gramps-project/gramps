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
import gc

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import ImageSelect
import ListModel
import RelLib
import NameDisplay
import Spell
import GrampsDisplay
from WindowUtils import GladeIf

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

class EditSource:

    def __init__(self,source,db,parent,parent_window=None,readonly=False):
        if source:
            self.source = source
        else:
            self.source = RelLib.Source()
        if self.source.get_handle():
            self.ref_not_loaded = 1
        else:
            self.ref_not_loaded = 0
        self.idle = None
        self.db = db
        self.parent = parent
        self.name_display = NameDisplay.displayer.display
        if source:
            if parent and self.parent.child_windows.has_key(source.get_handle()):
                self.parent.child_windows[source.get_handle()].present(None)
                return
            else:
                self.win_key = source.get_handle()
        else:
            self.win_key = self
        self.child_windows = {}
        self.path = db.get_save_path()
        self.not_loaded = 1
        self.lists_changed = 0
        self.gallery_ok = 0
        mode = not self.db.readonly

        self.top_window = gtk.glade.XML(const.gladeFile,"sourceEditor","gramps")
        self.top = self.top_window.get_widget("sourceEditor")
        self.gladeif = GladeIf(self.top_window)

        Utils.set_titles(self.top,self.top_window.get_widget('title'),
                         _('Source Editor'))
        
        plwidget = self.top_window.get_widget("iconlist")
        self.gallery = ImageSelect.Gallery(source, db.commit_place, self.path,
                                           plwidget, db, self, self.top)
        self.author = self.top_window.get_widget("author")
        self.pubinfo = self.top_window.get_widget("pubinfo")
        self.abbrev = self.top_window.get_widget("abbrev")
        self.note = self.top_window.get_widget("source_note")
        self.note.set_editable(mode)
        self.spell = Spell.Spell(self.note)
        self.notes_buffer = self.note.get_buffer()
        self.gallery_label = self.top_window.get_widget("gallerySourceEditor")
        self.refs_label = self.top_window.get_widget("refsSourceEditor")
        self.notes_label = self.top_window.get_widget("notesSourceEditor")
        self.flowed = self.top_window.get_widget("source_flowed")
        self.flowed.set_sensitive(mode)
        self.preform = self.top_window.get_widget("source_preform")
        self.preform.set_sensitive(mode)
        
        self.refinfo = self.top_window.get_widget("refinfo")
        
        self.title = self.top_window.get_widget("source_title")
        self.title.set_text(source.get_title())
        self.title.set_editable(mode)
        self.author.set_text(source.get_author())
        self.author.set_editable(mode)
        self.pubinfo.set_text(source.get_publication_info())
        self.pubinfo.set_editable(mode)
        self.abbrev.set_text(source.get_abbreviation())
        self.abbrev.set_editable(mode)

        self.top_window.get_widget('del_data').set_sensitive(mode)
        self.top_window.get_widget('add_data').set_sensitive(mode)
        self.top_window.get_widget('add_photo').set_sensitive(mode)
        self.top_window.get_widget('sel_photo').set_sensitive(mode)
        self.top_window.get_widget('delete_photo').set_sensitive(mode)

        if source.get_note():
            self.notes_buffer.set_text(source.get_note())
            Utils.bold_label(self.notes_label)
            if source.get_note_format() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)

        if self.source.get_media_list():
            Utils.bold_label(self.gallery_label)

        self.gladeif.connect('sourceEditor','delete_event',self.on_delete_event)
        self.gladeif.connect('button90','clicked',self.close)
        self.gladeif.connect('ok','clicked',self.on_source_apply_clicked)
        self.gladeif.connect('button166','clicked',self.on_help_clicked)
        self.gladeif.connect('notebook2','switch_page',self.on_switch_page)
        self.gladeif.connect('add_data','clicked',self.on_add_data_clicked)
        self.gladeif.connect('del_data','clicked',self.on_delete_data_clicked)
        self.gladeif.connect('add_photo','clicked',self.gallery.on_add_media_clicked)
        self.gladeif.connect('sel_photo','clicked',self.gallery.on_select_media_clicked)
        self.gladeif.connect('edit_photo','clicked',self.gallery.on_edit_media_clicked)
        self.gladeif.connect('delete_photo','clicked',self.gallery.on_delete_media_clicked)

        if self.source.get_handle() == None or self.db.readonly:
            self.top_window.get_widget("edit_photo").set_sensitive(False)
            self.top_window.get_widget("delete_photo").set_sensitive(False)

        self.datalist = self.top_window.get_widget('datalist')
        colno = 0
        first = True
        for title in [ (_('Key'),0,175), (_('Value'),1,150)]:
            renderer = gtk.CellRendererText()
            renderer.set_property('editable',True)
            renderer.connect('edited',self.edit_cb, colno)
            column = gtk.TreeViewColumn(title[0], renderer, text=colno)
            colno += 1
            column.set_clickable(True)
            column.set_resizable(True)
            column.set_min_width(title[2])
            column.set_sort_column_id(title[1])
            self.datalist.append_column(column)
            if first:
                first = False
                self.key_cell = renderer
                self.key_col = column

        self.data_model = gtk.ListStore(str,str)
        self.datalist.set_model(self.data_model)
        dmap = self.source.get_data_map()
        for item in dmap.keys():
            self.data_model.append(row=[item,dmap[item]])

        if parent_window:
            self.top.set_transient_for(parent_window)

        self.top_window.get_widget('ok').set_sensitive(not self.db.readonly)

        if parent_window:
            self.top.set_transient_for(parent_window)
        self.add_itself_to_menu()
        self.top.show()
        if self.ref_not_loaded:
            self.ref_not_loaded = 0
            Utils.temp_label(self.refs_label,self.top)
            self.cursor_type = None
            self.idle = gobject.idle_add(self.display_references)
        self.data_sel = self.datalist.get_selection()

    def on_add_data_clicked(self,widget):
        node = self.data_model.append(row=['',''])
        self.data_sel.select_iter(node)
        path = self.data_model.get_path(node)
        self.datalist.set_cursor_on_cell(path,
                                         focus_column=self.key_col,
                                         focus_cell=None,
                                         start_editing=True)


    def on_delete_data_clicked(self,widget):
        (model,node) = self.data_sel.get_selected()
        if node:
            model.remove(node)

    def edit_cb(self, cell, path, new_text, data):
        node = self.data_model.get_iter(path)
        self.data_model.set_value(node,data,new_text)

    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.gladeif.close()
        gc.collect()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-src')

    def close(self,obj=None):
        self.gallery.close()
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.gladeif.close()
        self.top.destroy()
        if self.idle != None:
            gobject.source_remove(self.idle)
        gc.collect()
        
    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        if not self.source:
            label = _("New Source")
        else:
            label = self.source.get_title()
        if not label.strip():
            label = _("New Source")
        label = "%s: %s" % (_('Source'),label)
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Source Editor'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.top.present()

    def button_press(self,obj):
        data = self.model.get_selected_objects()
        if not data:
            return
        (data_type,handle) = data[0]
        if data_type == 0:
            import EditPerson
            person = self.db.get_person_from_handle(handle)
            EditPerson.EditPerson(self.parent,person,self.db)
        elif data_type == 1:
            import Marriage
            family = self.db.get_family_from_handle(handle)
            Marriage.Marriage(self.parent,family,self.db)
        elif data_type == 2:
            import EventEdit
            event = self.db.get_event_from_handle(handle)
            event_name = event.get_name()
            if const.family_events.has_key(event_name):
                EventEdit.FamilyEventEditor(
                    self,", ", event, None, 0, None, None, self.db.readonly)
            elif const.personal_events.has_key(event_name):
                EventEdit.PersonEventEditor(
                    self,", ", event, None, 0, None, None, self.db.readonly)
            elif event_name in ["Birth","Death"]:
                EventEdit.PersonEventEditor(
                    self,", ", event, None, 1, None, None, self.db.readonly)
        elif data_type == 3:
            import EditPlace
            place = self.db.get_place_from_handle(handle)
            EditPlace.EditPlace(self.parent,place)
        elif data_type == 4:
            source = self.db.get_source_from_handle(handle)
            EditSource(source,self.db,self.parent,None,self.db.readonly)
        elif data_type == 5:
            media = self.db.get_object_from_handle(handle)
            ImageSelect.GlobalMediaProperties(self.db,media,self)

    def display_references(self):
        source_handle = self.source.get_handle()

        # Initialize things if we're entering this functioin
        # for the first time
        if not self.cursor_type:
            self.cursor_type = 'Person'
            self.cursor = self.db.get_person_cursor()
            self.data = self.cursor.first()

            self.any_refs = False
            slist = self.top_window.get_widget('slist')
            titles = [(_('Type'),0,150),(_('ID'),1,75),(_('Name'),2,150)]
            self.model = ListModel.ListModel(slist,
                                             titles,
                                             event_func=self.button_press)

        if self.cursor_type == 'Person':
            while self.data:
                handle,val = self.data
                person = RelLib.Person()
                person.unserialize(val)
                if person.has_source_reference(source_handle):
                    name = self.name_display(person)
                    gramps_id = person.get_gramps_id()
                    self.model.add([_("Person"),gramps_id,name],(0,handle))
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
                if family.has_source_reference(source_handle):
                    name = Utils.family_name(family,self.db)
                    gramps_id = family.get_gramps_id()
                    self.model.add([_("Family"),gramps_id,name],(1,handle))
                    self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()
            
            self.cursor_type = 'Event'
            self.cursor = self.db.get_event_cursor()
            self.data = self.cursor.first()

        if self.cursor_type == 'Event':
            while self.data:
                handle,val = self.data
                event = RelLib.Event()
                event.unserialize(val)
                if event.has_source_reference(source_handle):
                    name = event.get_name()
                    gramps_id = event.get_gramps_id()
                    self.model.add([_("Event"),gramps_id,name],(2,handle))
                    self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()
            
            self.cursor_type = 'Place'
            self.cursor = self.db.get_place_cursor()
            self.data = self.cursor.first()

        if self.cursor_type == 'Place':
            while self.data:
                handle,val = self.data
                place = RelLib.Place()
                place.unserialize(val)
                if place.has_source_reference(source_handle):
                    name = place.get_title()
                    gramps_id = place.get_gramps_id()
                    self.model.add([_("Place"),gramps_id,name],(3,handle))
                    self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()
            
            self.cursor_type = 'Source'
            self.cursor = self.db.get_source_cursor()
            self.data = self.cursor.first()

        if self.cursor_type == 'Source':
            while self.data:
                handle,val = self.data
                source = RelLib.Source()
                source.unserialize(val)
                if source.has_source_reference(source_handle):
                    name = source.get_title()
                    gramps_id = source.get_gramps_id()
                    self.model.add([_("Source"),gramps_id,name],(4,handle))
                    self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()
            
            self.cursor_type = 'Media'
            self.cursor = self.db.get_media_cursor()
            self.data = self.cursor.first()

        if self.cursor_type == 'Media':
            while self.data:
                handle,val = self.data
                obj = RelLib.MediaObject()
                obj.unserialize(val)
                if obj.has_source_reference(source_handle):
                    name = obj.get_description()
                    gramps_id = obj.get_gramps_id()
                    self.model.add([_("Media"),gramps_id,name],(5,handle))
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

    def on_source_apply_clicked(self,obj):

        title = unicode(self.title.get_text())
        author = unicode(self.author.get_text())
        pubinfo = unicode(self.pubinfo.get_text())
        abbrev = unicode(self.abbrev.get_text())
        note = unicode(
            self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                       self.notes_buffer.get_end_iter(),
                                       False))
        format = self.preform.get_active()

        if author != self.source.get_author():
            self.source.set_author(author)
        
        if title != self.source.get_title():
            self.source.set_title(title)
        
        if pubinfo != self.source.get_publication_info():
            self.source.set_publication_info(pubinfo)
        
        if abbrev != self.source.get_abbreviation():
            self.source.set_abbreviation(abbrev)
        
        if note != self.source.get_note():
            self.source.set_note(note)

        if format != self.source.get_note_format():
            self.source.set_note_format(format)

        new_map = {}
        for val in range(0,len(self.data_model)):
            node = self.data_model.get_iter(val)
            key = self.data_model.get_value(node,0)
            value = self.data_model.get_value(node,1)
            if key:
                new_map[unicode(key)] = unicode(value)
        if new_map != self.source.get_data_map():
            self.source.set_data_map(new_map)
        
        self.gallery_ok = 1

        trans = self.db.transaction_begin()
        if self.source.get_handle() == None:
            self.db.add_source(self.source,trans)
        else:
            self.db.commit_source(self.source,trans)
        self.db.transaction_commit(trans,_("Edit Source (%s)") % title)
        self.close(obj)

    def on_switch_page(self,obj,a,page):
        if page == 2 and self.not_loaded:
            self.not_loaded = 0
            self.gallery.load_images()
        elif page == 3 and self.ref_not_loaded:
            self.ref_not_loaded = 0
            Utils.temp_label(self.refs_label,self.top)
            self.idle = gobject.idle_add(self.display_references)
        text = unicode(
            self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                       self.notes_buffer.get_end_iter(),
                                       False)
            )
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)


class DelSrcQuery:
    def __init__(self,source,db,the_lists):
        self.source = source
        self.db = db
        self.the_lists = the_lists

    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        (person_list,family_list,event_list,
            place_list,source_list,media_list) = self.the_lists

        src_handle_list = [self.source.get_handle()]

        for handle in person_list:
            person = self.db.get_person_from_handle(handle)
            person.remove_source_references(src_handle_list)
            self.db.commit_person(person,trans)

        for handle in family_list:
            family = self.db.get_family_from_handle(handle)
            family.remove_source_references(src_handle_list)
            self.db.commit_family(family,trans)

        for handle in event_list:
            event = self.db.get_event_from_handle(handle)
            event.remove_source_references(src_handle_list)
            self.db.commit_event(event,trans)

        for handle in place_list:
            place = self.db.get_place_from_handle(handle)
            place.remove_source_references(src_handle_list)
            self.db.commit_place(place,trans)

        for handle in source_list:
            source = self.db.get_source_from_handle(handle)
            source.remove_source_references(src_handle_list)
            self.db.commit_source(source,trans)

        for handle in media_list:
            media = self.db.get_object_from_handle(handle)
            media.remove_source_references(src_handle_list)
            self.db.commit_media_object(media,trans)

        self.db.enable_signals()
        self.db.remove_source(self.source.get_handle(),trans)
        self.db.transaction_commit(
            trans,_("Delete Source (%s)") % self.source.get_title())
