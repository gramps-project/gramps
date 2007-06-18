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
# GTK 
#
#-------------------------------------------------------------------------
import gtk
import pango
import const
gtk26 = gtk.pygtk_version >= (2,6,0)

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
TEXT    = 0
TOGGLE  = 1
COMBO   = 2
IMAGE   = 3
INTEGER = 4

NOSORT = -1    

#-------------------------------------------------------------------------
#
# ListModel
#
#-------------------------------------------------------------------------
class ListModel:

    def __init__(self,tree,dlist,select_func=None,
                 event_func=None,mode=gtk.SELECTION_SINGLE):
        self.tree = tree
        self.tree.set_fixed_height_mode(True)
        self.mylist = []
        self.data_index = 0
        for l in dlist:
            if len(l)>3:
                if l[3] == TOGGLE:
                    self.mylist.append(bool)
                elif l[3] == IMAGE:
                    self.mylist.append(gtk.gdk.Pixbuf)
                elif l[3] == INTEGER:
                    self.mylist.append(int)
            else:
                self.mylist.append(str)
            self.data_index += 1
        self.mylist.append(object)

        self.function = {}
        self.tree.set_rules_hint(True)
        self.model = None
        self.selection = None
        self.mode = mode
        self.new_model()
        self.count = 0
        self.cid = None
        self.cids = []
        self.idmap = {}

        cnum = 0
        for name in dlist:
            if not name[2]:
                continue
            
            if len(name) == 3:
                name = (name[0],name[1],name[2],TEXT,False, None)
            elif len(name) == 4:
                name = (name[0],name[1],name[2],name[3],False, None)

            if name[0] and name[3] == TOGGLE:
                renderer = gtk.CellRendererToggle()
                column = gtk.TreeViewColumn(name[0],renderer)
                column.add_attribute(renderer,'active',cnum)
            elif name[0] and name[3] == IMAGE:
                renderer = gtk.CellRendererPixbuf()
                column = gtk.TreeViewColumn(name[0],renderer)
                column.add_attribute(renderer,'pixbuf',cnum)
                renderer.set_property('height',const.thumbScale/2)
            elif gtk26 and name[3] == COMBO:
                store = gtk.ListStore(str)
                model = gtk.ListStore(str, object)
                for val in name[4]:
                    model.append((val,store))
                self.function[cnum] = name[5]
                renderer = gtk.CellRendererCombo()
                renderer.set_property('model',model)
                renderer.set_property('text_column',0)
                renderer.set_fixed_height_from_font(True)
                renderer.set_property('editable',True)
                renderer.connect('edited',self.edited_cb, cnum)
                column = gtk.TreeViewColumn(name[0],renderer,text=cnum)
                column.set_reorderable(True)
            else:
                renderer = gtk.CellRendererText()
                renderer.set_fixed_height_from_font(True)
                renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
                if name[5]:
                    renderer.set_property('editable',True)
                    renderer.connect('edited',self.edited_cb, cnum)
                    self.function[cnum] = name[5]
                else:
                    renderer.set_property('editable',False)
                column = gtk.TreeViewColumn(name[0],renderer,text=cnum)
                column.set_reorderable(True)
            column.set_min_width(name[2])

            if name[0] == '':
                column.set_visible(False)
            else:
                column.set_resizable(True)
            if name[1] == -1:
                column.set_clickable(False)
            else:
                column.set_clickable(True)
                column.set_sort_column_id(name[1])

            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_fixed_width(name[2])

            cnum += 1
            self.cids.append(name[1])
            if name[0] != '':
                self.tree.append_column(column)

        self.connect_model()
        
        if select_func:
            self.selection.connect('changed',select_func)
        if event_func:
            self.double_click = event_func
            self.tree.connect('event',self.button_press)

    def edited_cb(self, cell, path, new_text, col):
        self.model[path][col] = new_text
        if self.function.has_key(col):
            self.function[col](int(path),new_text)

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

        self.model = gtk.ListStore(*self.mylist)
        self.selection = self.tree.get_selection()
        self.selection.set_mode(self.mode)
        self.sel_iter = None
        
    def connect_model(self):
        self.tree.set_model(self.model)
        if self.sel_iter:
            self.selection.select_iter(self.sel_iter)

        # if the sort column has not been defined (val[0] == -2), set
        # the sort column to the first column
        
        val = self.model.get_sort_column_id()
        if val[0] == -2 and self.cid:
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
        store, node = self.selection.get_selected()
        if node:
            rows = store.get_path(node)
            return rows[0]
        else:
            return -1

    def get_selected_objects(self):
        if self.count == 0:
            return []
        elif self.mode == gtk.SELECTION_SINGLE:
            store,node = self.selection.get_selected()
            if node:
                return [self.model.get_value(node,self.data_index)]
            else:
                return []
        else:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            return mlist

    def get_icon(self):
        if self.mode == gtk.SELECTION_SINGLE:
            store,node = self.selection.get_selected()
            path = self.model.get_path(node)
        else:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            path = self.model.get_path(mlist[0])
        return self.tree.create_row_drag_icon(path)

    def blist(self,store,path,node,list):
        list.append(self.model.get_value(node,self.data_index))

    def clear(self):
        self.count = 0
        self.model.clear()

    def remove(self,node):
        self.model.remove(node)
        self.count -= 1
        
    def get_row(self,node):
        row = self.model.get_path(node)
        return row[0]

    def select_row(self,row):
        self.selection.select_path((row))

    def select_iter(self,node):
        self.selection.select_iter(node)
    
    def get_object(self,node):
        return self.model.get_value(node,self.data_index)
        
    def insert(self,position,data,info=None,select=0):
        self.count += 1
        node = self.model.insert(position)
        col = 0
        for obj in data:
            self.model.set_value(node,col,obj)
            col += 1
        self.model.set_value(node,col,info)
        if info:
            self.idmap[str(info)] = node
        if select:
            self.selection.select_iter(node)
        return node
    
    def get_data(self,node,cols):
        return [ self.model.get_value(node,c) for c in cols ]
    
    def add(self,data,info=None,select=0):
        self.count += 1
        node = self.model.append()
        col = 0
        for obj in data:
            self.model.set_value(node,col,obj)
            col += 1
        self.model.set_value(node,col,info)
        if info:
            self.idmap[str(info)] = node
        if select:
            self.sel_iter = node
            self.selection.select_iter(self.sel_iter)
        return node

    def set(self,node,data,info=None,select=0):
        col = 0
        for obj in data:
            self.model.set_value(node,col,obj)
            col += 1
        self.model.set_value(node,col,info)
        if info:
            self.idmap[str(info)] = node
        if select:
            self.sel_iter = node
        return node

    def add_and_select(self,data,info=None):
        self.count += 1
        node = self.model.append()
        col = 0
        for obj in data:
            self.model.set_value(node,col,obj)
            col += 1
        if info:
            self.idmap[str(info)] = node
        self.model.set_value(node,col,info)
        self.selection.select_iter(node)

    def center_selected(self):
        model,node = self.selection.get_selected()
        if node:
            path = model.get_path(node)
            self.tree.scroll_to_cell(path,None,True,0.5,0.5)
        
    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.double_click(obj)
            return True
        return False

    def find(self,info):
        if info in self.idmap.keys():
            node = self.idmap[str(info)]
            self.selection.select_iter(node)

