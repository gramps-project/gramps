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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Provide the basic functionality for a list view
"""

#-------------------------------------------------------------------------
#
# GTK
#
#-------------------------------------------------------------------------
from gi.repository import Pango, Gdk, Gtk, GdkPixbuf
from gramps.gen.const import THUMBSCALE

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
TEXT = 0
TOGGLE = 1
COMBO = 2
IMAGE = 3
INTEGER = 4
COLOR = 5

NOSORT = -1

#-------------------------------------------------------------------------
#
# ListModel
#
#-------------------------------------------------------------------------
class ListModel:
    """
    Simple model for lists in smaller dialogs (not views).

    tree:       A Gtk TreeView object.
    dlist:      A list of column definitions.  Each column definition is a tuple
                consisting of the following elements:
                (name, sort_id, width, type, editable, callback)
        name:       The column name.  If the name is an empty string then the
                    column is hidden.  Use a single space for the column to be
                    displayed but have no heading.
        sort_id:    The column id to used to sort the column.  Use the NOSORT
                    constant to disable sorting on the column.
        width:      The column width.
        type:       An optional column type.  One of the constants TEXT, TOGGLE,
                    COMBO, IMAGE, INTEGER or COLOR.  Default = TEXT.
        editable:   An optional boolean.  True if the column is editable.
                    Used with TEXT, INTEGER, COMBO and TOGGLE columns.
                    Default = False.
        callback:   An optional callback to be executed when the column is
                    edited. Used with TEXT, INTEGER, COMBO and TOGGLE columns.
                    Default = None.
    select_func:    Function called when the TreeView selection changes.
    event_func:     Function called when the user double-clicks on a row.
    mode:           Selection mode for TreeView.  See Gtk documentation.
    list_mode:      "list" or "tree"
    right_click:    Function called when the user right-clicks on a row.
    """

    def __init__(self, tree, dlist, select_func=None, event_func=None,
                 mode=Gtk.SelectionMode.SINGLE, list_mode="list",
                 right_click=None):

        self.tree = tree
        self.tree.set_fixed_height_mode(True)
        self.mylist = []
        self.data_index = 0
        self.sel_iter = None
        self.list_mode = list_mode # "list", or "tree"
        self.double_click = None
        self.right_click = None

        for info in dlist:
            col_type = TEXT
            if isinstance(info, (list, tuple)):
                if len(info) > 3:
                    col_type = info[3]
            elif isinstance(info, dict):
                col_type = info.get("type", TEXT)
            # Now, add columns:
            if col_type == TOGGLE:
                self.mylist.append(bool)
            elif col_type == IMAGE:
                self.mylist.append(GdkPixbuf.Pixbuf)
            elif col_type == INTEGER:
                self.mylist.append(int)
            elif col_type == COLOR:
                self.mylist.append(str)
            else:
                self.mylist.append(str)
            self.data_index += 1
        self.mylist.append(object)

        self.function = {}
        self.model = None
        self.selection = None
        self.mode = mode
        self.new_model()
        self.count = 0
        self.cid = None
        self.cids = []
        self.idmap = {}

        self.__build_columns(dlist)
        self.connect_model()

        if select_func:
            self.selection.connect('changed', select_func)
        if event_func or right_click:
            if event_func:
                self.double_click = event_func
            if right_click:
                self.right_click = right_click
            self.tree.connect('button-press-event', self.__button_press)

    def __build_image_column(self, cnum, name, renderer, column):
        renderer = Gtk.CellRendererPixbuf()
        column = Gtk.TreeViewColumn(name[0], renderer)
        column.add_attribute(renderer, 'pixbuf', cnum)
        renderer.set_property('height', THUMBSCALE / 2)
        return renderer, column

    def __build_columns(self, dlist):
        """
        Builds the columns based of the data in dlist
        """
        cnum = 0

        for item in dlist:
            visible_col = None
            if isinstance(item, (list, tuple)):
                if not item[2]:
                    continue
                else:
                    # [name, sort_id, width, [type, [editable, [callback]]]
                    name = item
            elif isinstance(item, dict):
                # valid fields: name, sort_id, width, type, editable, callback, visible_col
                name = [item.get("name", " "), item.get("sort_id", NOSORT), item.get("width", 10),
                        item.get("type", TEXT), item.get("editable", False), item.get("callback", None)]
                visible_col = item.get("visible_col", None)
            if len(name) == 3:
                name = (name[0], name[1], name[2], TEXT, False, None)
            elif len(name) == 4:
                name = (name[0], name[1], name[2], name[3], False, None)
            elif len(name) == 5:
                name = (name[0], name[1], name[2], name[3], name[4], None)

            if name[0] and name[3] == TOGGLE:
                renderer = Gtk.CellRendererToggle()
                if visible_col is not None:
                    column = Gtk.TreeViewColumn(name[0], renderer, visible=visible_col)
                else:
                    column = Gtk.TreeViewColumn(name[0], renderer)
                column.add_attribute(renderer, 'active', cnum)
                if name[4]:
                    renderer.set_property('activatable', True)
                    renderer.connect('toggled', self.__toggled_cb, cnum)
                    if name[5]:
                        self.function[cnum] = name[5]
                else:
                    renderer.set_property('activatable', False)
            elif name[0] and name[3] == IMAGE:
                renderer, column = self.__build_image_column(cnum, name, renderer, column)
            elif name[0] and name[3] == COLOR:
                renderer = Gtk.CellRendererText()
                if visible_col is not None:
                    column = Gtk.TreeViewColumn(name[0], renderer, background=cnum,
                                                visible=visible_col)
                else:
                    column = Gtk.TreeViewColumn(name[0], renderer, background=cnum)
            else:
                renderer = Gtk.CellRendererText()
                renderer.set_fixed_height_from_font(True)
                renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
                if name[4]:
                    renderer.set_property('editable', True)
                    renderer.connect('edited', self.__edited_cb, cnum)
                    if name[5]:
                        self.function[cnum] = name[5]
                else:
                    renderer.set_property('editable', False)
                if visible_col is not None:
                    column = Gtk.TreeViewColumn(name[0], renderer, text=cnum, visible=visible_col)
                else:
                    column = Gtk.TreeViewColumn(name[0], renderer, text=cnum)
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

            column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            column.set_fixed_width(name[2])

            cnum += 1
            self.cids.append(name[1])
            if name[0] != '':
                self.tree.append_column(column)

    def __toggled_cb(self, obj, path, col):
        """
        Callback executed when the checkbox of the cell renderer is clicked
        """
        new_value = not self.model[path][col]
        self.model[path][col] = new_value
        if col in self.function:
            self.function[col](int(path), new_value)

    def __edited_cb(self, cell, path, new_text, col):
        """
        Callback executed when the text of the cell renderer has changed
        """
        self.model[path][col] = new_text
        if col in self.function:
            self.function[col](int(path), new_text)

    def unselect(self):
        """
        Remove the selection from the view
        """
        self.selection.unselect_all()

    def set_reorderable(self, order):
        """
        Enables or disables reordering of data
        """
        self.tree.set_reorderable(order)

    def new_model(self):
        """
        Create a new model instance
        """
        if self.model:
            self.cid = self.model.get_sort_column_id()
            del self.model
            del self.selection
        self.count = 0
        if self.list_mode == "list":
            self.model = Gtk.ListStore(*self.mylist)
        elif self.list_mode == "tree":
            self.model = Gtk.TreeStore(*self.mylist)
        self.selection = self.tree.get_selection()
        self.selection.set_mode(self.mode)
        self.sel_iter = None

    def connect_model(self):
        """
        Connects the model to the associated tree
        """
        self.tree.set_model(self.model)
        if self.sel_iter:
            self.selection.select_iter(self.sel_iter)

        # if the sort column has not been defined (val[0] == -2), set
        # the sort column to the first column

        val = self.model.get_sort_column_id()
        if val[0] == -2 and self.cid:
            self.model.set_sort_column_id(self.cid[0], self.cid[1])
        self.sort()

    def sort(self):
        """
        Sorts the current view
        """
        val = self.model.get_sort_column_id()
        col = val[0]
        if col is None or col < 0:
            return
        if col > 0:
            self.model.set_sort_column_id(col, val[1])
        else:
            self.model.set_sort_column_id(self.cids[0], val[1])
        self.model.sort_column_changed()

    def get_selected(self):
        """
        Return the selected items
        """
        return self.selection.get_selected()

    def get_row_at(self, xpos, ypos):
        """
        Return the row at the specified (x,y) coordinates
        """
        path = self.tree.get_path_at_pos(xpos, ypos)
        if path is None:
            return self.count -1
        else:
            return path[0][0]-1

    def get_selected_row(self):
        """
        Get the selected row number
        """
        store, node = self.selection.get_selected()
        if node:
            rows = store.get_path(node).get_indices()
            return rows[0]
        else:
            return -1

    def get_selected_objects(self):
        """
        Return the list of selected objects in the list
        """
        if self.count == 0:
            return []
        elif self.mode == Gtk.SelectionMode.SINGLE:
            store, node = self.selection.get_selected()
            if node:
                return [self.model.get_value(node, self.data_index)]
            else:
                return []
        else:
            mlist = []
            self.selection.selected_foreach(self.__build_select_list, mlist)
            return mlist

    def get_icon(self):
        """
        Return an icon to be used for Drag and drop.
        """
        if self.mode == Gtk.SelectionMode.SINGLE:
            store, node = self.selection.get_selected()
            path = self.model.get_path(node)
        else:
            mlist = []
            self.selection.selected_foreach(self.__build_select_list, mlist)
            path = self.model.get_path(mlist[0])
        return self.tree.create_row_drag_icon(path)

    def __build_select_list(self, store, path, node, dlist):
        """
        GTK callback function for walking a select list
        """
        dlist.append(self.model.get_value(node, self.data_index))

    def clear(self):
        """
        Clears all data in the list
        """
        self.count = 0
        self.model.clear()

    def remove(self, node):
        """
        Remove the item from the model
        """
        self.model.remove(node)
        self.count -= 1

    def get_row(self, node):
        """
        Return the row associated with the selected node
        """
        row = self.model.get_path(node)
        return row[0]

    def select_row(self, row):
        """
        Selects the item based on path
        """
        self.selection.select_path(row)

    def select_iter(self, node):
        """
        Selects the item based on iter
        """
        self.selection.select_iter(node)

    def get_object(self, node):
        """
        Return the object associated with the node. This is controlled
        by extracting the data from the associated data index
        """
        return self.model.get_value(node, self.data_index)

    def insert(self, position, data, info=None, select=0):
        """
        Inserts the item at the specified position in the model.
        """
        self.count += 1
        node = self.model.insert(position)
        col = 0
        for obj in data:
            self.model.set_value(node, col, obj)
            col += 1
        if info:
            self.model.set_value(node, col, info)
            self.idmap[str(info)] = node
        if select:
            self.selection.select_iter(node)
        return node

    def get_data(self, node, cols):
        """
        Return a list of data from the model associated with the node
        """
        return [ self.model.get_value(node, c) for c in cols ]

    def add(self, data, info=None, select=0, node=None):
        """
        Add the data to the model at the end of the model
        """
        info = info or ''
        self.count += 1
        need_to_set = True
        # Create the node:
        if self.list_mode == "list":
            node = self.model.append()
        elif self.list_mode == "tree":
            if node is None: # new node
                node = self.model.append(None, data + [info])
                need_to_set = False
            else: # use a previous node, passed in
                node = self.model.append(node)
        # Add data:
        if need_to_set:
            col = 0
            for obj in data:
                self.model.set_value(node, col, obj)
                col += 1
            self.model.set_value(node, col, info)
        # Set info and select:
        if info is not None:
            self.idmap[str(info)] = node
        if select:
            self.sel_iter = node
            self.selection.select_iter(self.sel_iter)
        # Return created node
        return node

    def set(self, node, data, info=None, select=0):
        """
        Change the data associated with the specific node. It does not
        add any data, just alters an existing row.
        """
        col = 0
        for obj in data:
            self.model.set_value(node, col, obj)
            col += 1
        self.model.set_value(node, col, info)
        if info:
            self.idmap[str(info)] = node
        if select:
            self.sel_iter = node
        return node

    def __button_press(self, obj, event):
        """
        Called when a button press is executed
        """
        from .utils import is_right_click
        if (event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS
                and event.button == 1):
            if self.double_click:
                self.double_click(obj)
                return True
        elif is_right_click(event):
            if self.right_click:
                self.right_click(obj, event)
                return True
        return False

    def find(self, info):
        """
        Selects the item associated with the pass information.
        """
        if info in self.idmap:
            node = self.idmap[str(info)]
            self.selection.select_iter(node)

    def move_up(self, row):
        """
        Move the given row up one position.
        """
        if row < 1 or row == -1:
            return False
        this_row = self.model.get_iter((row, ))
        prev_row = self.model.get_iter((row - 1, ))
        self.model.move_before(this_row, prev_row)
        return True

    def move_down(self, row):
        """
        Move the given row down one position.
        """
        if row >= self.count - 1 or row == -1:
            return False
        this_row = self.model.get_iter((row, ))
        next_row = self.model.get_iter((row + 1, ))
        self.model.move_after(this_row, next_row)
        return True
