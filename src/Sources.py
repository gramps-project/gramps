#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib
from gettext import gettext as _

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
        self.window = self.top.get_widget("sourcesel")

        Utils.set_titles(self.window, self.top.get_widget('title'),
                         _('Source Reference Selection'))
        
        self.top.signal_autoconnect({
            "on_add_src_clicked"    : self.add_src_clicked,
            "on_del_src_clicked"    : self.del_src_clicked,
            "on_edit_src_clicked"   : self.edit_src_clicked,
            "on_help_srcsel_clicked"   : self.on_help_clicked,
            "on_cancel_srcsel_clicked"   : self.close,
            "on_ok_srcsel_clicked"   : self.src_ok_clicked,
            "on_srcsel_delete_event"   : self.on_delete_event,
            })

        self.slist = self.top.get_widget("slist")
        self.edit = self.top.get_widget('edit')
        self.delete = self.top.get_widget('delete')
        self.selection = self.slist.get_selection()
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.slist.set_model(self.model)

        colno = 0
        for title in [ (_('ID'),0,100), (_('Title'),1,150)]:
            renderer = gtk.CellRendererText ()
            renderer.set_fixed_height_from_font(1)
            column = gtk.TreeViewColumn (title[0], renderer, text=colno)
            colno = colno + 1
            column.set_clickable (gtk.TRUE)
            column.set_resizable(gtk.TRUE)
            column.set_sort_column_id(title[1])
            column.set_min_width(title[2])
            self.slist.append_column (column)

        self.selection.connect('changed',self.selection_changed)

        self.delete.set_sensitive(gtk.FALSE)
        self.edit.set_sensitive(gtk.FALSE)
        self.redraw()
        if self.parent:
            self.window.set_transient_for(self.parent.window)
        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()

    def close(self,obj):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.window.destroy()

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
        self.parent.menu.append(self.parent_menu_item)
        self.menu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Reference Selector'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.menu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.menu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')

    def selection_changed(self,obj):
        (store,iter) = self.selection.get_selected()
        if iter:
            self.delete.set_sensitive(gtk.TRUE)
            self.edit.set_sensitive(gtk.TRUE)
        else:
            self.delete.set_sensitive(gtk.FALSE)
            self.edit.set_sensitive(gtk.FALSE)

    def redraw(self):
        self.model.clear()
        for s in self.list:
            base_id = s.get_base_id()
            base = self.db.find_source_from_id(base_id)
            iter = self.model.append()
            self.model.set(iter,0,base_id,1,base.get_title())

    def src_ok_clicked(self,obj):
        del self.orig[:]
        for s in self.list:
            self.orig.append(s)
        if self.update:
            self.update(self.orig)
        self.close(obj)
    
    def edit_src_clicked(self,obj):
        store,iter = self.selection.get_selected()
        if iter:
            col = store.get_path(iter)
            src = self.list[col[0]]
            SourceEditor(src,self.db,self.update_clist,self)

    def update_clist(self,inst,ref):
        inst.redraw()

    def add_src_clicked(self,obj):
        src = RelLib.SourceRef()
        SourceEditor(src,self.db,self.add_ref,self)

    def del_src_clicked(self,obj):
        (store,iter) = self.selection.get_selected()
        if iter:
            path = store.get_path(iter)
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
    def __init__(self,srclist,parent,top,window,clist,add_btn,edit_btn,del_btn):
        self.db = parent.db
        self.parent = parent
        self.list = srclist
        self.top = top
        self.window = window
        self.slist = clist
        self.selection = clist.get_selection()
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)

        colno = 0
        for title in [ (_('ID'),0,100), (_('Title'),1,150)]:
            renderer = gtk.CellRendererText ()
            column = gtk.TreeViewColumn (title[0], renderer, text=colno)
            colno = colno + 1
            column.set_clickable (gtk.TRUE)
            column.set_resizable(gtk.TRUE)
            column.set_sort_column_id(title[1])
            column.set_min_width(title[2])
            self.slist.append_column (column)
        
        self.slist.set_model(self.model)

        add_btn.connect('clicked', self.add_src_clicked)
        edit_btn.connect('clicked', self.edit_src_clicked)
        del_btn.connect('clicked', self.del_src_clicked)
        self.slist.connect('button-press-event',self.double_click)
        self.redraw()

    def double_click(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.edit_src_clicked(obj)

    def redraw(self):
        self.model.clear()
        for s in self.list:
            base_id = s.get_base_id()
            iter = self.model.append()
            base = self.db.find_source_from_id(base_id)
            self.model.set(iter,0,base_id,1,base.get_title())
        if self.list:
            Utils.bold_label(self.parent.sources_label)
        else:
            Utils.unbold_label(self.parent.sources_label)

    def update_clist(self,inst,ref):
        inst.redraw()
        self.parent.lists_changed = 1

    def edit_src_clicked(self,obj):
        store,iter = self.selection.get_selected()
        if iter:
            col = store.get_path(iter)
            src = self.list[col[0]]
            SourceEditor(src,self.db,self.update_clist,self)

    def add_src_clicked(self,obj):
        src = RelLib.SourceRef()
        SourceEditor(src,self.db,self.add_ref,self)

    def add_ref(self,inst,ref):
        self.parent.lists_changed = 1
        inst.list.append(ref)
        inst.redraw()

    def del_src_clicked(self,obj):
        (store,iter) = self.selection.get_selected()
        if iter:
            path = store.get_path(iter)
            del self.list[path[0]]
            self.redraw()

#-------------------------------------------------------------------------
#
# SourceEditor
#
#-------------------------------------------------------------------------
class SourceEditor:

    def __init__(self,srcref,database,update=None,parent=None):

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
        self.showSource = gtk.glade.XML(const.srcselFile, "sourceDisplay","gramps")
        self.sourceDisplay = self.get_widget("sourceDisplay")

        Utils.set_titles(self.sourceDisplay, self.showSource.get_widget('title'),
                         _('Source Information'))
        
        self.showSource.signal_autoconnect({
            "on_source_changed"     : self.on_source_changed,
            "on_add_src_clicked"    : self.add_src_clicked,
            "on_help_srcDisplay_clicked"   : self.on_help_clicked,
            "on_ok_srcDisplay_clicked"   : self.on_sourceok_clicked,
            "on_cancel_srcDisplay_clicked"   : self.close,
            "on_sourceDisplay_delete_event"  : self.on_delete_event,
            })
        self.source_field = self.get_widget("sourceList")
        self.title_menu = self.get_widget("source_title")
        self.title_menu.set_data("o",self)
        self.conf_menu = self.get_widget("conf")
        self.ok = self.get_widget("ok")
        Utils.build_confidence_menu(self.conf_menu)
        self.conf_menu.set_history(srcref.get_confidence_level())
        self.list = []

        self.title_menu.list.select_item(0)
        self.title_menu.list.remove_items(self.title_menu.list.get_selection())
        
        self.author_field = self.get_widget("sauthor")
        self.pub_field = self.get_widget("spubinfo")

        if self.source_ref:
            self.active_source = self.db.find_source_from_id(self.source_ref.get_base_id())
        else:
            self.active_source = None

        self.draw(self.active_source)
        self.set_button()
        if self.parent:
            self.sourceDisplay.set_transient_for(self.parent.window)
        self.add_itself_to_menu()
        self.sourceDisplay.show()

    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()

    def close(self,obj):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.sourceDisplay.destroy()

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
        self.win_parent.menu.append(self.parent_menu_item)
        self.menu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Source Information'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.menu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.win_parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.menu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.sourceDisplay.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','adv-si')

    def set_button(self):
        if self.active_source:
            self.ok.set_sensitive(1)
        else:
            self.ok.set_sensitive(0)

    def get_widget(self,name):
        """returns the widget associated with the specified name"""
        return self.showSource.get_widget(name)

    def draw(self,sel = None):
        self.title_menu.list.remove_items(self.list)
        if self.source_ref:
            spage = self.get_widget("spage")
            spage.get_buffer().set_text(self.source_ref.get_page())
            date = self.source_ref.get_date()
            if date:
                self.get_widget("sdate").set_text(date.get_date())

            text = self.get_widget("stext")
            text.get_buffer().set_text(self.source_ref.get_text())

            scom = self.get_widget("scomment")
            scom.get_buffer().set_text(self.source_ref.get_comments())
            src = self.db.find_source_from_id(self.source_ref.get_base_id())
            self.active_source = src
            if src:
                self.author_field.set_text(src.get_author())
                self.pub_field.set_text(src.get_publication_info())
        else:
            self.author_field.set_text("")
            self.pub_field.set_text("")

        keys = self.db.get_source_keys()
        keys.sort(self.db.sortbysource)
        
        sel_child = None
        self.list = []
        self.active_source = sel
        for src_id in keys:
            src = self.db.find_source_from_id(src_id)
            l = gtk.Label("%s [%s]" % (src.get_title(),src.get_id()))
            l.show()
            l.set_alignment(0,0.5)
            c = gtk.ListItem()
            c.add(l)
            c.set_data("s",src)
            c.show()
            self.list.append(c)
            if self.active_source == src:
                sel_child = c

        if len(self.list) > 0:
            self.title_menu.list.append_items(self.list)
            self.title_menu.set_sensitive(1)
            if sel_child:
                self.title_menu.list.select_child(sel_child)
        else:
            self.title_menu.set_sensitive(0)

    def on_sourceok_clicked(self,obj):

        if self.active_source != self.db.find_source_from_id(self.source_ref.get_base_id()):
            self.source_ref.set_base_id(self.active_source.get_id())
        
        date = unicode(self.get_widget("sdate").get_text())
        conf = self.get_widget("conf").get_menu().get_active().get_data('a')

        buffer = self.get_widget("scomment").get_buffer()
        comments = unicode(buffer.get_text(buffer.get_start_iter(),
                               buffer.get_end_iter(),gtk.FALSE))

        buffer = self.get_widget("stext").get_buffer()
        text = unicode(buffer.get_text(buffer.get_start_iter(),
                               buffer.get_end_iter(),gtk.FALSE))

        buffer = self.get_widget('spage').get_buffer()
        page = unicode(buffer.get_text(buffer.get_start_iter(),
                               buffer.get_end_iter(),gtk.FALSE))

        self.source_ref.set_page(page)
        self.source_ref.get_date().set(date)
        self.source_ref.set_text(text)
        self.source_ref.set_comments(comments)
        self.source_ref.set_confidence_level(conf)

        if self.update:
            self.update(self.parent,self.source_ref)
        
        Utils.modified()
        self.close(obj)

    def on_source_changed(self,obj):
        sel = obj.list.get_selection()
        if sel:
            self.active_source = sel[0].get_data("s")
            
            if self.active_source:
                self.author_field.set_text(self.active_source.get_author())
                self.pub_field.set_text(self.active_source.get_publication_info())
            self.set_button()

    def update_display(self,source):
        self.db.add_source(source)
        self.draw(source)
#        self.update(0)

    def add_src_clicked(self,obj):
        import EditSource
        EditSource.EditSource(RelLib.Source(),self.db, self,self.sourceDisplay, self.update_display)

