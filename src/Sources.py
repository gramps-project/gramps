#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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
from intl import gettext as _

#-------------------------------------------------------------------------
#
# SourceSelector
#
#-------------------------------------------------------------------------

class SourceSelector:
    def __init__(self,srclist,parent,update=None):
        self.db = parent.db
        self.parent = parent
        self.orig = srclist
        self.list = []
        for s in self.orig:
            self.list.append(RelLib.SourceRef(s))
        self.update=update
        self.top = gtk.glade.XML(const.srcselFile,"sourcesel")
        self.top.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_add_src_clicked"    : self.add_src_clicked,
            "on_del_src_clicked"    : self.del_src_clicked,
            "on_src_ok_clicked"     : self.src_ok_clicked,
            })

        self.sourcesel = self.top.get_widget("sourcesel")
        self.slist = self.top.get_widget("slist")
        self.selection = self.slist.get_selection()
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.slist.set_model(self.model)

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

        self.redraw()
        self.sourcesel.show()

    def redraw(self):
        self.model.clear()
        for s in self.list:
            base = s.getBase()
            iter = self.model.append()
            self.model.set(iter,0,base.getId(),1,base.getTitle())

    def src_ok_clicked(self,obj):
        del self.orig[:]
        for s in self.list:
            self.orig.append(s)
        if self.update:
            self.update(self.orig)
        Utils.destroy_passed_object(self.sourcesel)
    
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
    def __init__(self,srclist,parent,top,clist,add_btn,del_btn):
        self.db = parent.db
        self.parent = parent
        self.list = srclist
        self.top = top
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
        del_btn.connect('clicked', self.del_src_clicked)
        self.slist.connect('button-press-event',self.double_click)
        self.redraw()

    def double_click(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.edit_src_clicked(obj)

    def redraw(self):
        self.model.clear()
        for s in self.list:
            base = s.getBase()
            iter = self.model.append()
            self.model.set(iter,0,base.getId(),1,base.getTitle())

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
        self.update = update
        self.source_ref = srcref
        self.showSource = gtk.glade.XML(const.srcselFile, "sourceDisplay")
        self.showSource.signal_autoconnect({
            "on_combo_insert_text"  : Utils.combo_insert_text,
            "on_sourceok_clicked"   : self.on_sourceok_clicked,
            "on_source_changed"     : self.on_source_changed,
            "destroy_passed_object" : Utils.destroy_passed_object
            })
        self.sourceDisplay = self.get_widget("sourceDisplay")
        self.source_field = self.get_widget("sourceList")
        self.title_menu = self.get_widget("source_title")
        self.title_menu.set_data("o",self)
        self.conf_menu = self.get_widget("conf")
        Utils.build_confidence_menu(self.conf_menu)
        self.conf_menu.set_history(srcref.getConfidence())

        self.author_field = self.get_widget("sauthor")
        self.pub_field = self.get_widget("spubinfo")

        if self.source_ref:
            self.active_source = self.source_ref.getBase()
        else:
            self.active_source = None
        self.draw()
        self.sourceDisplay.show()

    def get_widget(self,name):
        """returns the widget associated with the specified name"""
        return self.showSource.get_widget(name)

    def draw(self):
        if self.source_ref:
            self.get_widget("spage").set_text(self.source_ref.getPage())
            date = self.source_ref.getDate()
            if date:
                self.get_widget("sdate").set_text(date.getDate())

            text = self.get_widget("stext")
            text.get_buffer().set_text(self.source_ref.getText())

            scom = self.get_widget("scomment")
            scom.get_buffer().set_text(self.source_ref.getComments())
            src = self.source_ref.getBase()
            self.active_source = src
            if src:
                self.author_field.set_text(src.getAuthor())
                self.pub_field.set_text(src.getPubInfo())
        else:
            self.author_field.set_text("")
            self.pub_field.set_text("")

        values = self.db.getSourceMap().values()
#        values.sort(by_title)

        sel_child = None
        list = []
        for src in values:
            l = gtk.Label("%s [%s]" % (src.getTitle(),src.getId()))
            l.show()
            l.set_alignment(0,0.5)
            c = gtk.ListItem()
            c.add(l)
            c.set_data("s",src)
            c.show()
            list.append(c)
            if self.active_source == src:
                sel_child = c

        self.title_menu.list.append_items(list)
        
        if sel_child:
            self.title_menu.list.select_child(sel_child)

    def on_sourceok_clicked(self,obj):
        if self.active_source != self.source_ref.getBase():
            self.source_ref.setBase(self.active_source)
        
        page = self.get_widget("spage").get_text()
        date = self.get_widget("sdate").get_text()
        conf = self.get_widget("conf").get_menu().get_active().get_data('a')

        buffer = self.get_widget("scomment").get_buffer()
        comments = buffer.get_text(buffer.get_start_iter(),
                               buffer.get_end_iter(),gtk.FALSE)

        buffer = self.get_widget("stext").get_buffer()
        text = buffer.get_text(buffer.get_start_iter(),
                               buffer.get_end_iter(),gtk.FALSE)

        self.source_ref.setPage(page)
        self.source_ref.getDate().set(date)
        self.source_ref.setText(text)
        self.source_ref.setComments(comments)
        self.source_ref.setConfidence(conf)

        if self.update:
            self.update(self.parent,self.source_ref)
        
        Utils.modified()
        Utils.destroy_passed_object(obj)

    def on_source_changed(self,obj):
        self.active_source = obj.list.get_selection()[0].get_data("s")

        if self.active_source:
            self.author_field.set_text(self.active_source.getAuthor())
            self.pub_field.set_text(self.active_source.getPubInfo())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_title(a,b):
    return cmp(a.getTitle(),b.getTitle())
               

        
