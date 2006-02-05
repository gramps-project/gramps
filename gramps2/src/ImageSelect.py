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
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import gc
import urlparse
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
import GrampsKeys
import NameDisplay
import PluginMgr
import RelLib
import RelImage
import ListModel
import SelectObject
import GrampsMime
import Sources
import DateEdit
import DateHandler
import ImgManip
import Spell
import DisplayState
import GrampsDisplay

from QuestionDialog import ErrorDialog
from DdTargets import DdTargets
from WindowUtils import GladeIf

_IMAGEX = 140
_IMAGEY = 150
_PAD = 5

_last_path = ""
_iconlist_refs = []

_drag_targets = [
    ('STRING', 0, 0),
    ('text/plain',0,0),
    ('text/uri-list',0,2),
    ('application/x-rootwin-drop',0,1)]

#-------------------------------------------------------------------------
#
# LocalMediaProperties
#
#-------------------------------------------------------------------------
class LocalMediaProperties:

    def __init__(self,photo,path,parent,parent_window=None):
        self.parent = parent
        if photo:
            if self.parent.parent.child_windows.has_key(photo):
                self.parent.parent.child_windows[photo].present(None)
                return
            else:
                self.win_key = photo
        else:
            self.win_key = self
        self.child_windows = {}
        self.photo = photo
        self.db = parent.db
        self.obj = self.db.get_object_from_handle(photo.get_reference_handle())
        self.alist = photo.get_attribute_list()[:]
        self.lists_changed = 0
        
        fname = self.obj.get_path()
        self.change_dialog = gtk.glade.XML(const.gladeFile,
                                           "change_description","gramps")

        title = _('Media Reference Editor')
        self.window = self.change_dialog.get_widget('change_description')
        Utils.set_titles(self.window,
                         self.change_dialog.get_widget('title'), title)
        
        descr_window = self.change_dialog.get_widget("description")
        self.pixmap = self.change_dialog.get_widget("pixmap")
        self.attr_type = self.change_dialog.get_widget("attr_type")
        self.attr_value = self.change_dialog.get_widget("attr_value")
        self.attr_details = self.change_dialog.get_widget("attr_details")

        self.attr_list = self.change_dialog.get_widget("attr_list")
        titles = [(_('Attribute'),0,150),(_('Value'),0,100)]

        self.attr_label = self.change_dialog.get_widget("attr_local")
        self.notes_label = self.change_dialog.get_widget("notes_local")
        self.flowed = self.change_dialog.get_widget("flowed")
        self.preform = self.change_dialog.get_widget("preform")

        self.atree = ListModel.ListModel(self.attr_list,titles,
                                         self.on_attr_list_select_row,
                                         self.on_update_attr_clicked)
        
        self.slist  = self.change_dialog.get_widget("src_list")
        self.sources_label = self.change_dialog.get_widget("source_label")
        if self.obj:
            self.srcreflist = [RelLib.SourceRef(ref)
                               for ref in self.photo.get_source_references()]
        else:
            self.srcreflist = []
    
#         self.sourcetab = Sources.SourceTab(self.srcreflist,self,
#                                  self.change_dialog,
#                                  self.window, self.slist,
#                                  self.change_dialog.get_widget('add_src'),
#                                  self.change_dialog.get_widget('edit_src'),
#                                  self.change_dialog.get_widget('del_src'))

        descr_window.set_text(self.obj.get_description())
        mtype = self.obj.get_mime_type()

        self.pix = ImgManip.get_thumbnail_image(self.obj.get_path(),mtype)
        self.pixmap.set_from_pixbuf(self.pix)

        self.change_dialog.get_widget("private").set_active(photo.get_privacy())
        coord = photo.get_rectangle()
        if coord and type(coord) == tuple:
            self.change_dialog.get_widget("upperx").set_value(coord[0])
            self.change_dialog.get_widget("uppery").set_value(coord[1])
            self.change_dialog.get_widget("lowerx").set_value(coord[2])
            self.change_dialog.get_widget("lowery").set_value(coord[3])
        
        self.change_dialog.get_widget("gid").set_text(self.obj.get_gramps_id())

        self.change_dialog.get_widget("path").set_text(fname)

        mt = GrampsMime.get_description(mtype)
        if mt:
            self.change_dialog.get_widget("type").set_text(mt)
        else:
            self.change_dialog.get_widget("type").set_text("")
        self.notes = self.change_dialog.get_widget("notes")
        self.spell = Spell.Spell(self.notes)
        if self.photo.get_note():
            self.notes.get_buffer().set_text(self.photo.get_note())
            Utils.bold_label(self.notes_label)
            if self.photo.get_note_format() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)

        self.gladeif = GladeIf(self.change_dialog)
        self.gladeif.connect('change_description','delete_event',self.on_delete_event)
        self.gladeif.connect('button84','clicked',self.close)
        self.gladeif.connect('button82','clicked',self.on_ok_clicked)
        self.gladeif.connect('button104','clicked',self.on_help_clicked)
        self.gladeif.connect('notebook1','switch_page',self.on_notebook_switch_page)
        self.gladeif.connect('button86','clicked',self.on_add_attr_clicked)
        self.gladeif.connect('button100','clicked',self.on_update_attr_clicked)
        self.gladeif.connect('button88','clicked',self.on_delete_attr_clicked)
            
        media_obj = self.db.get_object_from_handle(self.photo.get_reference_handle())
        gnote = self.change_dialog.get_widget('global_notes')
        spell = Spell.Spell(gnote)
        global_note = gnote.get_buffer()
        global_note.insert_at_cursor(media_obj.get_note())
        
        self.redraw_attr_list()
        if parent_window:
            self.window.set_transient_for(parent_window)
        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.gladeif.close()
        self.close_child_windows()
        self.remove_itself_from_menu()
        gc.collect()

    def close(self,obj):
        self.gladeif.close()
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.window.destroy()
        gc.collect()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.parent.child_windows[self.win_key] = self
        label = _('Media Reference')
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Reference Editor'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.parent.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def redraw_attr_list(self):
        self.atree.clear()
        self.amap = {}
        for attr in self.alist:
            d = [attr.get_type(),attr.get_value()]
            node = self.atree.add(d,attr)
            self.amap[str(attr)] = node
        if self.alist:
            Utils.bold_label(self.attr_label)
        else:
            Utils.unbold_label(self.attr_label)
        
    def on_notebook_switch_page(self,obj,junk,page):
        t = self.notes.get_buffer()
        text = unicode(t.get_text(t.get_start_iter(),t.get_end_iter(),False))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)
            
    def on_apply_clicked(self):
        priv = self.change_dialog.get_widget("private").get_active()

        coord = (
            self.change_dialog.get_widget("upperx").get_value_as_int(),
            self.change_dialog.get_widget("uppery").get_value_as_int(),
            self.change_dialog.get_widget("lowerx").get_value_as_int(),
            self.change_dialog.get_widget("lowery").get_value_as_int(),
            )
        if (coord[0] == None and coord[1] == None
            and coord[2] == None and coord[3] == None):
            coord = None

        t = self.notes.get_buffer()
        text = unicode(t.get_text(t.get_start_iter(),t.get_end_iter(),False))
        note = self.photo.get_note()
        format = self.preform.get_active()
        if text != note or priv != self.photo.get_privacy() \
               or coord != self.photo.get_rectangle() \
               or format != self.photo.get_note_format():
            self.photo.set_rectangle(coord)
            self.photo.set_note(text)
            self.photo.set_privacy(priv)
            self.photo.set_note_format(format)
            self.parent.lists_changed = 1
            self.parent.parent.lists_changed = 1
        if self.lists_changed:
            self.photo.set_attribute_list(self.alist)
            self.photo.set_source_reference_list(self.srcreflist)
            self.parent.lists_changed = 1
            self.parent.parent.lists_changed = 1

        trans = self.db.transaction_begin()
        self.db.commit_media_object(self.obj,trans)
        self.db.transaction_commit(trans,_("Edit Media Object"))

    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-edit-complete')
        
    def on_ok_clicked(self,obj):
        self.on_apply_clicked()
        self.close(obj)
        
    def on_attr_list_select_row(self,obj):
        store,node = self.atree.get_selected()
        if node:
            attr = self.atree.get_object(node)

            self.attr_type.set_label(attr.get_type())
            self.attr_value.set_text(attr.get_value())
        else:
            self.attr_type.set_label('')
            self.attr_value.set_text('')

    def attr_callback(self,attr):
        self.redraw_attr_list()
        self.atree.select_iter(self.amap[str(attr)])
        
    def on_update_attr_clicked(self,obj):
        import AttrEdit

        store,node = self.atree.get_selected()
        if node:
            attr = self.atree.get_object(node)
            AttrEdit.AttributeEditor(self,attr,"Media Object",
                                     PluginMgr.get_image_attributes(),
                                     self.attr_callback)

    def on_delete_attr_clicked(self,obj):
        if Utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        AttrEdit.AttributeEditor(self,None,"Media Object",
                                 PluginMgr.get_image_attributes(),
                                 self.attr_callback)

def build_dropdown(entry,strings):
    store = gtk.ListStore(str)
    for value in strings:
        node = store.append()
        store.set(node,0,value)
    completion = gtk.EntryCompletion()
    completion.set_text_column(0)
    completion.set_model(store)
    entry.set_completion(completion)
