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
import gtk.glade
import gnome

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

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

class EditSource:

    def __init__(self,source,db,parent,parent_window=None,
                 func=None,readonly=False):
        if source:
            self.source = source
        else:
            self.source = RelLib.Source()
        self.db = db
        self.parent = parent
        self.name_display = NameDisplay.displayer.display
        if source:
            if self.parent.child_windows.has_key(source.get_handle()):
                self.parent.child_windows[source.get_handle()].present(None)
                return
            else:
                self.win_key = source.get_handle()
        else:
            self.win_key = self
        self.child_windows = {}
        self.callback = func
        self.path = db.get_save_path()
        self.not_loaded = 1
        self.ref_not_loaded = 1
        self.lists_changed = 0
        self.gallery_ok = 0
        mode = not self.db.readonly

        self.top_window = gtk.glade.XML(const.gladeFile,"sourceEditor","gramps")
        self.top = self.top_window.get_widget("sourceEditor")

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

        self.top_window.signal_autoconnect({
            "on_switch_page" : self.on_switch_page,
            "on_addphoto_clicked" : self.gallery.on_add_media_clicked,
            "on_selectphoto_clicked"    : self.gallery.on_select_media_clicked,
            "on_deletephoto_clicked" : self.gallery.on_delete_media_clicked,
            "on_editphoto_clicked"     : self.gallery.on_edit_media_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_sourceEditor_help_clicked" : self.on_help_clicked,
            "on_sourceEditor_ok_clicked" : self.on_source_apply_clicked,
            "on_sourceEditor_cancel_clicked" : self.close,
            "on_sourceEditor_delete_event" : self.on_delete_event,
            "on_delete_data_clicked" : self.on_delete_data_clicked,
            "on_add_data_clicked" : self.on_add_data_clicked,
            })

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

        self.display_references()
        if parent_window:
            self.top.set_transient_for(parent_window)
        self.add_itself_to_menu()
        self.top.show()
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

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')

    def close(self,obj):
        self.gallery.close()
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.top.destroy()
        
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

    def display_references(self):
        p_event_list = []
        p_attr_list = []
        p_addr_list = []
        p_name_list = []
        m_list = []
        f_event_list = []
        f_attr_list = []
        person_list = []
        p_list = []
        for key in self.db.get_place_handles():
            p = self.db.get_place_from_handle(key) 
            name = p.get_title()
            for sref in p.get_source_references():
                if sref.get_base_handle() == self.source.get_handle():
                    p_list.append(name)
        for key in self.db.get_person_handles(sort_handles=False):
            p = self.db.get_person_from_handle(key)
            name = self.name_display(p)
            for sref in p.get_source_references():
                if sref.get_base_handle() == self.source.get_handle():
                    person_list.append((name,''))
            for event_handle in p.get_event_list() + [p.get_birth_handle(), p.get_death_handle()]:
                if event_handle:
                    event = self.db.get_event_from_handle(event_handle)
                    for sref in event.get_source_references():
                        if sref.get_base_handle() == self.source.get_handle():
                            p_event_list.append((name,event.get_name()))
            for v in p.get_attribute_list():
                for sref in v.get_source_references():
                    if sref.get_base_handle() == self.source.get_handle():
                        p_attr_list.append((name,v.get_type()))
            for v in p.get_alternate_names() + [p.get_primary_name()]:
                for sref in v.get_source_references():
                    if sref.get_base_handle() == self.source.get_handle():
                        p_name_list.append((name,v.get_name()))
            for v in p.get_address_list():
                for sref in v.get_source_references():
                    if sref.get_base_handle() == self.source.get_handle():
                        p_addr_list.append((name,v.get_street()))
        for object_handle in self.db.get_media_object_handles():
            obj = self.db.get_object_from_handle(object_handle)
            name = obj.get_description()
            for sref in obj.get_source_references():
                if sref.get_base_handle() == self.source.get_handle():
                    m_list.append(name)
        for family_handle in self.db.get_family_handles():
            family = self.db.get_family_from_handle(family_handle)
            f_id = family.get_father_handle()
            m_id = family.get_mother_handle()
            if f_id:
                f = self.db.get_person_from_handle(f_id)
            if m_id:
                m = self.db.get_person_from_handle(m_id)
            if f_id and m_id:
                name = _("%(father)s and %(mother)s") % {
                    "father" : self.name_display(f),
                    "mother" : self.name_display(m)}
            elif f_id:
                name = self.name_display(f)
            else:
                name = self.name_display(m)
            for v_id in p.get_event_list():
                v = self.db.get_event_from_handle(v_id)
                if not v:
                    continue
                for sref in v.get_source_references():
                    if sref.get_base_handle() == self.source.get_handle():
                        f_event_list.append((name,v.get_name()))
            for v in p.get_attribute_list():
                for sref in v.get_source_references():
                    if sref.get_base_handle() == self.source.get_handle():
                        f_attr_list.append((name,v.get_type()))

        slist = self.top_window.get_widget('slist')

        titles = [(_('Source Type'),0,150),(_('Object'),1,150),(_('Value'),2,150)]
        
        self.model = ListModel.ListModel(slist,titles)
        any = 0

        if len(person_list) > 0:
            any = 1
            for p in person_list:
                self.model.add([_("Persons"),p[0],''])

        if len(p_event_list) > 0:
            any = 1
            for p in p_event_list:
                self.model.add([_("Individual Events"),p[0],
                                const.display_pevent(p[1])])
        if len(p_attr_list) > 0:
            any = 1
            for p in p_attr_list:
                self.model.add([_("Individual Attributes"),p[0],
                               const.display_pattr(p[1])])
        if len(p_name_list) > 0:
            any = 1
            for p in p_name_list:
                self.model.add([_("Individual Names"),p[0],p[1]])
        if len(f_event_list) > 0:
            any = 1
            for p in f_event_list:
                self.model.add([_("Family Events"),p[0],
                                const.display_fevent(p[1])])
        if len(f_attr_list) > 0:
            any = 1
            for p in f_event_list:
                self.model.add([_("Family Attributes"),p[0],
                                const.display_fattr(p[1])])
        if len(m_list) > 0:
            any = 1
            for p in m_list:
                self.model.add([_("Media Objects"),p,''])
        if len(p_list) > 0:
            any = 1
            for p in p_list:
                self.model.add([_("Places"),p,''])
        
        if len(p_addr_list) > 0:
            any = 1
            for p in p_addr_list:
                self.model.add([_("Addresses"),p[0],p[1]])

        if any:
            Utils.bold_label(self.refs_label)
        else:
            Utils.unbold_label(self.refs_label)
            
        self.ref_not_loaded = 0

    def on_source_apply_clicked(self,obj):

        title = unicode(self.title.get_text())
        author = unicode(self.author.get_text())
        pubinfo = unicode(self.pubinfo.get_text())
        abbrev = unicode(self.abbrev.get_text())
        note = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                  self.notes_buffer.get_end_iter(),False))
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
        
        if self.callback:
            self.callback(self.source)
        self.close(obj)

    def on_switch_page(self,obj,a,page):
        if page == 2 and self.not_loaded:
            self.not_loaded = 0
            self.gallery.load_images()
        elif page == 3 and self.ref_not_loaded:
            self.ref_not_loaded = 0
            self.display_references()
        text = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                self.notes_buffer.get_end_iter(),False))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)


class DelSrcQuery:
    def __init__(self,source,db,update):
        self.source = source
        self.db = db
        self.update = update

    def delete_source(self,obj):
        m = 0
        l = []
        for sref in obj.get_source_references():
            if sref.get_base_handle() != self.source.get_handle():
                l.append(sref)
            else:
                m = 1
        if m:
            obj.set_source_reference_list(l)
        return m

    def query_response(self):
        trans = self.db.transaction_begin()
        
        for key in self.db.get_person_handles(sort_handles=False):
            commit = 0
            p = self.db.get_person_from_handle(key)
            for v_id in p.get_event_list() + [p.get_birth_handle(), p.get_death_handle()]:
                v = self.db.get_event_from_handle(v_id)
                if v:
                    commit += self.delete_source(v)

            for v in p.get_attribute_list():
                commit += self.delete_source(v)

            for v in p.get_alternate_names() + [p.get_primary_name()]:
                commit += self.delete_source(v)

            for v in p.get_address_list():
                commit += self.delete_source(v)
            if commit > 0:
                self.db.commit_person(p,trans)

        for p_id in self.db.get_family_handles():
            commit = 0
            p = self.db.get_family_from_handle(p_id)
            for v_id in p.get_event_list():
                v = self.db.get_event_from_handle(v_id)
                if v:
                    commit += self.delete_source(v)
                    self.db.commit_event(v,trans)

            for v in p.get_attribute_list():
                commit += self.delete_source(v)
                self.db.commit_event(v,trans)
            if commit > 0:
                self.db.commit_family(p,trans)

        for p_id in self.db.get_media_object_handles():
            p = self.db.get_object_from_handle(p_id)
            if self.delete_source(p):
                self.db.commit_media_object(p,trans)

        for key in self.db.get_place_handles():
            p = self.db.get_place_from_handle(key)
            if self.delete_source(self.db.get_place_from_handle(key)):
                self.db.commit_place(p,trans)

        self.db.remove_source(self.source.get_handle(),trans)
        self.db.transaction_commit(trans,_("Delete Source (%s)") % self.source.get_title())
        self.update(self.source.get_handle())
