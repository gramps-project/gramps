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
# GNOME
#
#-------------------------------------------------------------------------
from gobject import TYPE_STRING, TYPE_INT
import gtk
import pango

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
_BCOL = 8
_IDCOL = 1

_TOP_FONT=pango.WEIGHT_ULTRABOLD
_TEXT_FONT=pango.WEIGHT_NORMAL

#-------------------------------------------------------------------------
#
# PeopleStore
#
#-------------------------------------------------------------------------
class PeopleStore:
    def __init__(self,tree,parent,select_func=None,event_func=None,
                 mode=gtk.SELECTION_SINGLE):

        self.titles  = [
            (_('Name'),5,250), (_('ID'),1,50),(_('Gender'),2,70),
            (_('Birth date'),6,150),(_('Death date'),7,150)
            ]

        ncols = len(self.titles) + 3
        self.tree = tree
        self.parent = parent
        self.tree.connect('row-expanded',self.on_row_expanded)
        self.mylist = [TYPE_STRING]*ncols + [TYPE_INT]

        self.tree.set_rules_hint(gtk.TRUE)
        self.model = None
        self.tree_roots = {}
        self.tree_open = {}
        self.tree_list = {}
        self.selection = None
        self.mode = mode
        self.new_model()
        self.count = 0
        self.cid = None
        self.cids = []
        
        cnum = 0
        for name in self.titles:
            renderer = gtk.CellRendererText()
            renderer.set_fixed_height_from_font(1)
            if name[0] != '':
                column = gtk.TreeViewColumn(name[0],renderer,text=cnum)
                column.set_min_width(name[2])
                column.set_resizable(gtk.TRUE)
                column.set_clickable(gtk.TRUE)
                column.set_sort_column_id(name[1])

                cnum +=  1
                self.cids.append(name[1])
                self.tree.append_column(column)
                
        self.connect_model()
        
        if select_func:
            self.selection.connect('changed',select_func)
        if event_func:
            self.double_click = event_func
            self.tree.connect('row_activated', self.row_activated)

    def row_activated (self, treeview, path, column):
        self.double_click (treeview)

    def enable_sort(self):
        if self.cids[0] != -1:
            self.model.set_sort_column_id(self.cids[0],gtk.SORT_ASCENDING)

    def unselect(self):
        self.selection.unselect_all()

    def set_reorderable(self,order):
        self.tree.set_reorderable(order)
        
    def new_model(self):
        if self.model:
            self.cid = self.model.get_sort_column_id()
            del self.model
            del self.selection
        self.count = 0

        self.model = gtk.TreeStore(*self.mylist)
        self.selection = self.tree.get_selection()
        self.selection.set_mode(self.mode)
        self.sel_iter = None
        
    def connect_model(self):
        self.tree.set_model(self.model)
        if self.sel_iter:
            self.selection.select_iter(self.sel_iter)
        if self.cid:
            self.model.set_sort_column_id(self.cid[0],self.cid[1])
        self.sort()

    def sort(self):
        val = self.model.get_sort_column_id()
        col = val[0]
        if col < 0:
            return
        if col > 0:
            self.model.set_sort_column_id(col,val[1])
        else:
            self.model.set_sort_column_id(self.cids[0],val[1])
        self.model.sort_column_changed()
        
    def get_selected(self):
        return self.selection.get_selected()

    def get_row_at(self,x,y):
        path = self.tree.get_path_at_pos(x,y)
        if path == None:
            return self.count -1
        else:
            return path[0][0]-1

    def get_selected_row(self):
        store, iter = self.selection.get_selected()
        if iter:
            rows = store.get_path(iter)
            return rows[0]
        else:
            return -1

    def get_selected_objects(self):
        if self.count == 0:
            return []
        elif self.mode == gtk.SELECTION_SINGLE:
            store,iter = self.selection.get_selected()
            if iter:
                return [self.model.get_value(iter,_IDCOL)]
            else:
                return []
        else:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            return mlist

    def get_icon(self):
        if self.mode == gtk.SELECTION_SINGLE:
            store,iter = self.selection.get_selected()
            path = self.model.get_path(iter)
        else:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            path = self.model.get_path(mlist[0])
        return self.tree.create_row_drag_icon(path)

    def blist(self,store,path,iter,id_list):
        id_list.append(self.model.get_value(iter,_IDCOL))

    def clear(self):
        self.count = 0
        self.tree_roots = {}
        self.tree_open = {}
        self.model.clear()

    def remove(self,iter):
        try:
            iter_parent = self.model.iter_parent (iter)
            self.model.remove(iter)
            if iter_parent and not self.model.iter_has_child (iter_parent):
                name = unicode(self.model.get_value(iter_parent,0))
                self.model.remove (iter_parent)
                if self.tree_roots.has_key(name):
                    del self.tree_roots[name]
                if self.tree_open.has_key(name):
                    del self.tree_open[name]
                if self.tree_list.has_key(name):
                    del self.tree_list[name]
            self.count = self.count - 1
        except:
            pass
        
    def get_row(self,iter):
        row = self.model.get_path(iter)
        return row[0]

    def select_row(self,row):
        self.selection.select_path((row))

    def select_iter(self,iter):
        self.selection.select_iter(iter)
    
    def get_object(self,iter):
        return self.model.get_value(iter,_IDCOL)
        
    def insert(self,position,data,info=None,select=0):
        self.count = self.count + 1
        iter = self.model.insert(position)
        col = 0
        for object in data:
            self.model.set_value(iter,col,object)
            col = col + 1
        self.model.set_value(iter,_IDCOL,info)
        self.model.set_value(iter,_BCOL,_TOP_FONT)
        if select:
            self.selection.select_iter(iter)
        return iter
    
    def get_data(self,iter,cols):
        return [ self.model.get_value(iter,c) for c in cols ]

    def on_row_expanded(self, view, iter, path):
        name = self.model.get_value(iter,0)
        self.fill_row(name,iter)

    def expand_row(self,name,iter=None):
        path = self.model.get_path(self.tree_roots[name])
        self.parent.parent.status_text(_('Updating display...'))
        self.tree.expand_row(path,1)
        self.parent.parent.modify_statusbar()

    def fill_row(self,name,iter=None):
        name = unicode(name)
        
        if not iter:
            iter = self.tree_roots[name]
        child = self.model.iter_children(iter)

        if self.model.get_value(child,0) is None:
            self.model.remove(child)
            for d in self.tree_list[name]:
                new_iter = self.model.append(iter)
                self.model.set(new_iter,0,d[0],1,d[1],2,d[2],3,d[3],4,d[4],
                               5,d[5],6,d[6],7,d[7])
                self.parent.id2col[d[1]] = (self,new_iter)
	self.expand_row (name, iter)

    def add(self,data,select=0):
        self.count = self.count + 1

        name = data[-1]
        if self.tree_roots.has_key(name):
            top = self.tree_roots[name]
        else:
            top = self.model.append(None)
            self.model.append(top)
            self.tree_open[name] = 0
            self.tree_list[name] = []
            self.model.set_value(top,0,name)
            self.model.set_value(top,5,name.upper())
            self.model.set_value(top,_BCOL,_TOP_FONT)
            self.tree_roots[name] = top

        if self.tree_open[name] or select:
            iter = self.model.append(top)
            col = 0
            for object in data[:-1]:
                self.model.set_value(iter,col,object)
                col = col + 1
            self.model.set_value(iter,_BCOL,_TEXT_FONT)
            if select:
                self.sel_iter = iter
                self.selection.select_iter(self.sel_iter)
            return iter
        else:
            self.tree_list[name].append(data)
            return None

    def set(self,iter,data,select=0):
        col = 0
        for object in data:
            self.model.set_value(iter,col,object)
            col = col + 1
        self.model.set_value(iter,_BCOL,_TEXT_FONT)
        if select:
            self.sel_iter = iter
        return iter

    def add_and_select(self,data):
        self.count = self.count + 1
        iter = self.model.append()
        col = 0
        for object in data:
            self.model.set_value(iter,col,object)
            col = col + 1
        self.model.set_value(iter,_BCOL,_TEXT_FONT)
        self.selection.select_iter(iter)

    def center_selected(self):
        model,iter = self.selection.get_selected()
        if iter:
            path = model.get_path(iter)
            self.tree.scroll_to_cell(path,None,gtk.TRUE,0.5,0.5)
