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
import gtk
import gtk.glade
from gtk.gdk import ACTION_COPY, BUTTON1_MASK, INTERP_BILINEAR, pixbuf_new_from_file
from gobject import TYPE_PYOBJECT
import cPickle as pickle

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib
import Date
import DateEdit
import DateHandler
import GrampsDBCallback
import GrampsDisplay
import Spell

from DdTargets import DdTargets
from WindowUtils import GladeIf

#-------------------------------------------------------------------------
#
# SourceSelector
#
#-------------------------------------------------------------------------

class SourceSelector:
    def __init__(self,srclist,parent,update=None):
        self.db = parent.db
        self.parent = parent
        if srclist:
            if self.parent.child_windows.has_key(id(srclist)):
                self.parent.child_windows[id(srclist)].present(None)
                return
            else:
                self.win_key = id(srclist)
        else:
            self.win_key = self
        self.orig = srclist
        self.list = []
        self.child_windows = {}
        for s in self.orig:
            self.list.append(RelLib.SourceRef(s))
        self.update=update
        self.top = gtk.glade.XML(const.srcselFile,"sourcesel","gramps")
        self.gladeif = GladeIf(self.top)
        
        self.window = self.top.get_widget("sourcesel")

        Utils.set_titles(self.window, self.top.get_widget('title'),
                         _('Source Reference Selection'))

        self.gladeif.connect('sourcesel', 'delete_event', self.on_delete_event)
        self.gladeif.connect('button138','clicked', self.close)
        self.gladeif.connect('ok', 'clicked', self.src_ok_clicked)
        self.gladeif.connect('button145', 'clicked', self.on_help_clicked)
        self.gladeif.connect('add', 'clicked', self.add_src_clicked)
        self.gladeif.clicked('edit', 'clicked', self.edit_src_clicked)
        self.gladeif.clicked('delete', 'clicked', self.del_src_clicked)
        
        self.slist = self.top.get_widget("slist")
        self.edit = self.top.get_widget('edit')
        self.delete = self.top.get_widget('delete')
        self.delete.set_sensitive(not self.db.readonly)
        self.selection = self.slist.get_selection()
        self.model = gtk.ListStore(str,str)
        self.slist.set_model(self.model)
        self.top.get_widget('add').set_sensitive(not self.db.readonly)
        self.top.get_widget('ok').set_sensitive(not self.db.readonly)

        colno = 0
        for title in [ (_('ID'),0,100), (_('Title'),1,150)]:
            renderer = gtk.CellRendererText ()
            renderer.set_fixed_height_from_font(1)
            column = gtk.TreeViewColumn (title[0], renderer, text=colno)
            colno += 1
            column.set_clickable (True)
            column.set_resizable(True)
            column.set_sort_column_id(title[1])
            column.set_min_width(title[2])
            self.slist.append_column (column)

        self.selection.connect('changed',self.selection_changed)

        self.delete.set_sensitive(False)
        self.edit.set_sensitive(False)
        self.redraw()
        if self.parent:
            self.window.set_transient_for(self.parent.window)
        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.gladeif.close()
        self.close_child_windows()
        self.remove_itself_from_menu()
        gc.collect()

    def close(self,obj):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.gladeif.close()
        self.window.destroy()
        gc.collect()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        label = _('Source Reference')
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Reference Selector'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-edit-complete')

    def selection_changed(self,obj):
        (store,node) = self.selection.get_selected()
        if node:
            self.delete.set_sensitive(True)
            self.edit.set_sensitive(True)
        else:
            self.delete.set_sensitive(False)
            self.edit.set_sensitive(False)

    def redraw(self):
        self.model.clear()
        for s in self.list:
            base_handle = s.get_base_handle()
            base = self.db.get_source_from_handle(base_handle)
            node = self.model.append()
            self.model.set(node,0,base.get_gramps_id(),1,base.get_title())

    def src_ok_clicked(self,obj):
        del self.orig[:]
        for s in self.list:
            self.orig.append(s)
        if self.update:
            self.update(self.orig)
        self.close(obj)
    
    def edit_src_clicked(self,obj):
        store,node = self.selection.get_selected()
        if node:
            col = store.get_path(node)
            src = self.list[col[0]]
            SourceEditor(src,self.db,self.update_clist,self)

    def update_clist(self,inst,ref):
        inst.redraw()

    def add_src_clicked(self,obj):
        src = RelLib.SourceRef()
        SourceEditor(src,self.db,self.add_ref,self)

    def del_src_clicked(self,obj):
        (store,node) = self.selection.get_selected()
        if node:
            path = store.get_path(node)
            del self.list[path[0]]
            self.redraw()

    def add_ref(self,inst,ref):
        self.parent.lists_changed = 1
        inst.list.append(ref)
        inst.redraw()

#-------------------------------------------------------------------------
#
# SourceTab
#
#-------------------------------------------------------------------------
class SourceTab:
    def __init__(self, srclist, parent, top, window, clist, add_btn,
                 edit_btn, del_btn, readonly=False):

        self.db = parent.db
        self.parent = parent
        self.list = srclist
        self.top = top
        self.window = window
        self.slist = clist
        self.selection = clist.get_selection()
        self.model = gtk.ListStore(str,str,TYPE_PYOBJECT)

        add_btn.set_sensitive(not readonly)
        del_btn.set_sensitive(not readonly)

        colno = 0
        for title in [ (_('ID'),0,100), (_('Title'),1,150)]:
            renderer = gtk.CellRendererText ()
            column = gtk.TreeViewColumn (title[0], renderer, text=colno)
            colno = colno + 1
            column.set_clickable (True)
            column.set_resizable(True)
            column.set_sort_column_id(title[1])
            column.set_min_width(title[2])
            self.slist.append_column (column)
        
        self.slist.set_model(self.model)

        add_btn.connect('clicked', self.add_src_clicked)
        edit_btn.connect('clicked', self.edit_src_clicked)
        del_btn.connect('clicked', self.del_src_clicked)
        self.slist.connect('button-press-event',self.double_click)
        self.setup_drag_n_drop()
        self.redraw()

    def setup_drag_n_drop(self):
        self.slist.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                 [DdTargets.SOURCEREF.target()],
                                 ACTION_COPY)
        self.slist.drag_source_set(BUTTON1_MASK,
                                   [DdTargets.SOURCEREF.target()],
                                   ACTION_COPY)
        self.slist.connect('drag_data_get', self.drag_data_get)
        self.slist.connect('drag_begin', self.drag_begin)
        self.slist.connect('drag_data_received',self.drag_data_received)

    def drag_data_received(self,widget,context,x,y,sel_data,info,time):
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if mytype != DdTargets.SOURCEREF.drag_type:
                return
            else:
                foo = pickle.loads(data[2]);
                self.list.append(foo)

            self.lists_changed = True
            self.redraw()

    def drag_data_get(self,widget, context, sel_data, info, time):

        store,node = self.selection.get_selected()
        if not node:
            return
        ev = store.get_value(node,2)

        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev);
        data = str((DdTargets.SOURCEREF.drag_type,None,pickled));
        sel_data.set(sel_data.target, bits_per, data)

    def drag_begin(self, context, a):
        return

    def double_click(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.edit_src_clicked(obj)

    def redraw(self):
        self.model.clear()
        for s in self.list:
            base_handle = s.get_base_handle()
            node = self.model.append()
            base = self.db.get_source_from_handle(base_handle)
            self.model.set(node,0,base.get_gramps_id(),1,base.get_title(),
                           2,s)
        if self.list:
            Utils.bold_label(self.parent.sources_label)
        else:
            Utils.unbold_label(self.parent.sources_label)

    def update_clist(self,inst,ref):
        inst.redraw()
        self.parent.lists_changed = 1
            
    def add_ref(self,inst,ref):
        self.parent.lists_changed = 1
        inst.list.append(ref)
        inst.redraw()

    def edit_src_clicked(self,obj):
        store,node = self.selection.get_selected()
        if node:
            col = store.get_path(node)
            src = self.list[col[0]]
            SourceEditor(src,self.db,self.update_clist,self)

    def add_src_clicked(self,obj):
        src = RelLib.SourceRef()
        SourceEditor(src,self.db,self.add_ref,self)

    def del_src_clicked(self,obj):
        (store,node) = self.selection.get_selected()
        if node:
            path = store.get_path(node)
            del self.list[path[0]]
            self.parent.lists_changed = 1
            self.redraw()

#-------------------------------------------------------------------------
#
# SourceEditor
#
#-------------------------------------------------------------------------
class SourceEditor:

    def __init__(self, srcref, database, update, parent):

        self.db = database
        self.parent = parent
        if self.parent.__dict__.has_key('child_windows'):
            self.win_parent = self.parent
        else:
            self.win_parent = self.parent.parent
        if srcref:
            if self.win_parent.child_windows.has_key(srcref):
                self.win_parent.child_windows[srcref].present(None)
                return
            else:
                self.win_key = srcref
        else:
            self.win_key = self
        self.update = update
        self.source_ref = srcref
        self.child_windows = {}
        self.showSource = gtk.glade.XML(const.srcselFile,
                                        "sourceDisplay","gramps")
        self.sourceDisplay = self.get_widget("sourceDisplay")

        Utils.set_titles(self.sourceDisplay,
                         self.showSource.get_widget('title'),
                         _('Source Information'))
        
        self.showSource.signal_autoconnect({
            "on_add_src_clicked"            : self.add_src_clicked,
            "on_help_srcDisplay_clicked"    : self.on_help_clicked,
            "on_ok_srcDisplay_clicked"      : self.on_sourceok_clicked,
            "on_cancel_srcDisplay_clicked"  : self.close,
            "on_sourceDisplay_delete_event" : self.on_delete_event,
            })
        self.source_field = self.get_widget("sourceList")

        # setup menu
        self.title_menu = self.get_widget("source_title")
        cell = gtk.CellRendererText()
        self.title_menu.pack_start(cell,True)
        self.title_menu.add_attribute(cell,'text',0)
        self.title_menu.connect('changed',self.on_source_changed)
        self.conf_menu = self.get_widget("conf")
        self.private = self.get_widget("priv")
        self.ok = self.get_widget("ok")
        self.conf_menu.set_active(srcref.get_confidence_level())

        self.author_field = self.get_widget("sauthor")
        self.pub_field = self.get_widget("spubinfo")

        self.date_entry_field = self.get_widget("sdate")

        if self.source_ref:
            handle = self.source_ref.get_base_handle()
            self.active_source = self.db.get_source_from_handle(handle)
            self.date_obj = self.source_ref.get_date_object()
            date_str = DateHandler.displayer.display(self.date_obj)
            self.date_entry_field.set_text(date_str)
            self.private.set_active(self.source_ref.get_privacy())
        else:
            self.date_obj = Date.Date()
            self.active_source = None

        date_stat = self.get_widget("date_stat")
        self.date_check = DateEdit.DateEdit(
            self.date_obj, self.date_entry_field,
            date_stat, self.sourceDisplay)

        self.spage = self.get_widget("spage")
        self.scom = self.get_widget("scomment")
        self.spell1 = Spell.Spell(self.scom)
        self.stext = self.get_widget("stext")
        self.spell2 = Spell.Spell(self.stext)

        self.draw(self.active_source,fresh=True)
        self.set_button()
        if self.parent:
            self.sourceDisplay.set_transient_for(self.parent.window)
        self.add_itself_to_menu()
        self.db.connect('source-add', self.rebuild_menu)
        self.sourceDisplay.show()

    def rebuild_menu(self,handle_list):
        self.build_source_menu(handle_list[0])

    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()
        gc.collect()

    def close(self,obj):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.sourceDisplay.destroy()
        gc.collect()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.win_parent.child_windows[self.win_key] = self
        if self.active_source:
            label = self.active_source.get_title()
        else:
            label = _("New Source")
        if not label.strip():
            label = _("New Source")
        label = "%s: %s" % (_('Source Reference'),label)
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.win_parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Source Information'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.win_parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.sourceDisplay.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-si')

    def set_button(self):
        if self.active_source:
            self.ok.set_sensitive(True)
        else:
            self.ok.set_sensitive(False)

    def get_widget(self,name):
        """returns the widget associated with the specified name"""
        return self.showSource.get_widget(name)

    def draw(self,sel=None,fresh=False):
        if self.source_ref and fresh:
            self.spage.get_buffer().set_text(self.source_ref.get_page())

            self.stext.get_buffer().set_text(self.source_ref.get_text())
            self.scom.get_buffer().set_text(self.source_ref.get_note())
            idval = self.source_ref.get_base_handle()
            src = self.db.get_source_from_handle(idval)
            self.active_source = src
            if src:
                self.author_field.set_text(src.get_author())
                self.pub_field.set_text(src.get_publication_info())
        else:
            self.author_field.set_text("")
            self.pub_field.set_text("")
        self.active_source = sel
        if sel:
            self.build_source_menu(sel.get_handle())
        else:
            self.build_source_menu(None)

    def build_source_menu(self,selected_handle):
        keys = self.db.get_source_handles()
        keys.sort(self.db._sortbysource)

        store = gtk.ListStore(str)

        sel_child = None
        index = 0
        sel_index = 0
        self.handle_list = []
        for src_id in keys:
            src = self.db.get_source_from_handle(src_id)
            title = src.get_title()
            gid = src.get_gramps_id()

            if len(title) > 40:
                title = title[0:37] + "..."
            
            store.append(row=["%s [%s]" % (title,gid)])
            self.handle_list.append(src_id)
            if selected_handle == src_id:
                sel_index = index
            index += 1
        self.title_menu.set_model(store)

        if index > 0:
            self.title_menu.set_sensitive(1)
            self.title_menu.set_active(sel_index)
        else:
            self.title_menu.set_sensitive(0)

    def on_sourceok_clicked(self,obj):

        shandle = self.source_ref.get_base_handle()
        if self.active_source != self.db.get_source_from_handle(shandle):
            self.source_ref.set_base_handle(self.active_source.get_handle())
        
        conf = self.get_widget("conf").get_active()

        buf = self.scom.get_buffer()
        comments = unicode(buf.get_text(buf.get_start_iter(),
                                        buf.get_end_iter(),False))

        buf = self.stext.get_buffer()
        text = unicode(buf.get_text(buf.get_start_iter(),
                                    buf.get_end_iter(),False))

        buf = self.spage.get_buffer()
        page = unicode(buf.get_text(buf.get_start_iter(),
                                    buf.get_end_iter(),False))

        self.source_ref.set_page(page)
        self.source_ref.set_date_object(self.date_obj)
        self.source_ref.set_text(text)
        self.source_ref.set_note(comments)
        self.source_ref.set_confidence_level(conf)
        self.source_ref.set_privacy(self.private.get_active())

        self.update(self.parent,self.source_ref)
        self.close(obj)

    def on_source_changed(self,obj):
        handle = self.handle_list[obj.get_active()]
        self.active_source = self.db.get_source_from_handle(handle)
        self.author_field.set_text(self.active_source.get_author())
        self.pub_field.set_text(self.active_source.get_publication_info())
        self.set_button()

    def update_display(self,source):
        self.draw(source,fresh=False)

    def add_src_clicked(self,obj):
        import EditSource
        EditSource.EditSource(RelLib.Source(),self.db, self)

