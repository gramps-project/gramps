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
# python
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import cPickle as pickle

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
import pango

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
from _ButtonTab import ButtonTab

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------
class EmbeddedList(ButtonTab):
    """
    This class provides the base class for all the list tabs. It
    maintains a gtk.TreeView, including the selection and button
    sensitivity.
    """
    
    _HANDLE_COL = -1
    _DND_TYPE   = None
    _DND_EXTRA  = None
    
    def __init__(self, dbstate, uistate, track, name, build_model,
                 share=False, move=False):
        """
        Creates a new list, using the passed build_model to
        populate the list.
        """
        ButtonTab.__init__(self, dbstate, uistate, track, name, share, move)

        
        self.changed = False
        self.build_model = build_model

        # handle the selection
        self.selection = self.tree.get_selection()
        self.selection.connect('changed', self._selection_changed)

        # build the columns
        self.columns = []
        self.build_columns()

        if self._DND_TYPE:
            self._set_dnd()

        # set up right click option
        self.tree.connect('button-press-event', self._on_button_press)

        # build the initial data
        self.rebuild()
        self.show_all()

    def _on_button_press(self, obj, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            ref = self.get_selected()
            if ref:
                self.right_click(obj, event)

    def get_popup_menu_items(self):
        if self.share_btn:
            itemlist = [
                (True, True, gtk.STOCK_ADD, self.add_button_clicked),
                (True, False, _('Share'), self.edit_button_clicked),
                (False,True, gtk.STOCK_EDIT, self.edit_button_clicked),
                (True, True, gtk.STOCK_REMOVE, self.del_button_clicked),
                ]
        else:
            itemlist = [
                (True, True, gtk.STOCK_ADD, self.add_button_clicked),
                (False,True, gtk.STOCK_EDIT, self.edit_button_clicked),
                (True, True, gtk.STOCK_REMOVE, self.del_button_clicked),
            ]
        return itemlist

    def right_click(self, obj, event):

        menu = gtk.Menu()
        for (needs_write_access, image, title, func) in self.get_popup_menu_items():
            if image:
                item = gtk.ImageMenuItem(stock_id=title)
            else:
                item = gtk.MenuItem(title)
            item.connect('activate', func)
            if needs_write_access and self.dbstate.db.readonly:
                item.set_sensitive(False)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, event.button, event.time)

    def find_index(self, obj):
        """
        returns the index of the object within the associated data
        """
        return self.get_data().index(obj)

    def _set_dnd(self):
        """
        Sets up drag-n-drop. The source and destionation are set by calling .target()
        on the _DND_TYPE. Obviously, this means that there must be a _DND_TYPE
        variable defined that points to an entry in DdTargets.
        """

        if self._DND_EXTRA:
            dnd_types = [ self._DND_TYPE.target(), self._DND_EXTRA.target() ]
        else:
            dnd_types = [ self._DND_TYPE.target() ]
        
        self.tree.drag_dest_set(gtk.DEST_DEFAULT_ALL, dnd_types,
                                gtk.gdk.ACTION_COPY)
        self.tree.drag_source_set(gtk.gdk.BUTTON1_MASK,
                                  [self._DND_TYPE.target()],
                                  gtk.gdk.ACTION_COPY)
        self.tree.connect('drag_data_get', self.drag_data_get)
        if not self.dbstate.db.readonly:
            self.tree.connect('drag_data_received', self.drag_data_received)
        
    def drag_data_get(self, widget, context, sel_data, info, time):
        """
        Provide the drag_data_get function, which passes a tuple consisting of:

           1) Drag type defined by the .drag_type field specfied by the value
              assigned to _DND_TYPE
           2) The id value of this object, used for the purpose of determining
              the source of the object. If the source of the object is the same
              as the object, we are doing a reorder instead of a normal drag
              and drop
           3) Pickled data. The pickled version of the selected object
           4) Source row. Used for a reorder to determine the original position
              of the object
        """

        # get the selected object, returning if not is defined
        obj = self.get_selected()
        if not obj:
            return

        # pickle the data, and build the tuple to be passed
        value = (self._DND_TYPE.drag_type, id(self), obj, self.find_index(obj))
        data = pickle.dumps(value)

        # pass as a string (8 bits)
        sel_data.set(sel_data.target, 8, data)

    def drag_data_received(self, widget, context, x, y, sel_data, info, time):
        """
        Handle the standard gtk interface for drag_data_received.

        If the selection data is define, extract the value from sel_data.data,
        and decide if this is a move or a reorder.
        """
        if sel_data and sel_data.data:
            (mytype, selfid, obj, row_from) = pickle.loads(sel_data.data)

            # make sure this is the correct DND type for this object
            if mytype == self._DND_TYPE.drag_type:
                
                # determine the destination row
                row = self._find_row(x, y)

                # if the is same object, we have a move, otherwise,
                # it is a standard drag-n-drop
                
                if id(self) == selfid:
                    self._move(row_from, row, obj)
                else:
                    self._handle_drag(row, obj)
                self.rebuild()
            elif self._DND_EXTRA and mytype == self._DND_EXTRA.drag_type:
                self.handle_extra_type(mytype, obj)

    def handle_extra_type(self, objtype, obj):
        pass

    def _find_row(self, x, y):
        row = self.tree.get_path_at_pos(x, y)
        if row == None:
            return len(self.get_data())
        else:
            return row[0][0]

    def _handle_drag(self, row, obj):
        self.get_data().insert(row, obj)
        self.changed = True
        self.rebuild()

    def _move(self, row_from, row_to, obj):
        dlist = self.get_data()
        if row_from < row_to:
            dlist.insert(row_to, obj)
            del dlist[row_from]
        else:
            del dlist[row_from]
            dlist.insert(row_to-1, obj)
        self.changed = True
        self.rebuild()
    
    def _move_up(self, row_from, obj,selmethod=None):
        ''' 
        Move the item a position up in the EmbeddedList.
        Eg: 0,1,2,3 needs to become 0,2,1,3, here row_from = 2
        '''
        if selmethod :
            dlist = selmethod()
        else :
            dlist = self.get_data()
        del dlist[row_from]
        dlist.insert(row_from-1, obj)
        self.changed = True
        self.rebuild()
        #select the row
        path = '%d' % (row_from-1) 
        self.tree.get_selection().select_path(path)
        
    def _move_down(self, row_from, obj,selmethod=None):
        ''' 
        Move the item a position down in the EmbeddedList.
        Eg: 0,1,2,3 needs to become 0,2,1,3, here row_from = 1
        '''
        if selmethod :
            dlist = selmethod()
        else :
            dlist = self.get_data()
        del dlist[row_from]
        dlist.insert(row_from+1, obj)
        self.changed = True
        self.rebuild()
        #select the row
        path = '%d' % (row_from+1) 
        self.tree.get_selection().select_path(path)

    def get_icon_name(self):
        """
        Specifies the basic icon used for a generic list. Typically,
        a derived class will override this. The icon chosen is the
        STOCK_JUSTIFY_FILL icon, which in the default GTK style
        looks kind of like a list.
        """
        return gtk.STOCK_JUSTIFY_FILL

    def del_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            ref_list = self.get_data()
            ref_list.remove(ref)
            self.changed = True
            self.rebuild()
            
    def up_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            pos = self.find_index(ref)
            if pos > 0 :
                self._move_up(pos,ref)
                
    def down_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            pos = self.find_index(ref)
            if pos >=0 and pos < len(self.get_data())-1:
                self._move_down(pos,ref)

    def build_interface(self):
        """
        Builds the interface, instantiating a gtk.TreeView in a
        gtk.ScrolledWindow.
        """

        # create the tree, turn on rule hinting and connect the
        # button press to the double click function.
        
        self.tree = gtk.TreeView()
        self.tree.set_reorderable(True)
        self.tree.set_rules_hint(True)
        self.tree.connect('button_press_event', self.double_click)

        # create the scrolled window, and attach the treeview
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.tree)
        self.pack_start(scroll, True)

    def get_selected(self):
        """
        returns the value associated with selected row in the model,
        based of the _HANDLE_COL value. Each model must define this
        to indicate what the returned value should be. If no selection
        has been made, None is returned.
        """
        (model, node) = self.selection.get_selected()
        if node:
            obj = self.model.get_value(node, self._HANDLE_COL)
            return model.get_value(node, self._HANDLE_COL)
        return None

    def is_empty(self):
        """
        Returns True if the get_data returns a length greater than
        0. Typically, get_data returns the list of associated data.
        """
        return len(self.get_data()) == 0
    
    def get_data(self):
        """
        Returns the data associated with the list. This is typically
        a list of objects.

        This should be overridden in the derrived classes.
        """
        return []

    def column_order(self):
        """
        Specifies the column order for the columns. This should be
        in the format of a list of tuples, in the format of (int,int),
        where the first in indicates if the column is visible, and the
        second column indicates the index into the model.

        This should be overridden in the derrived classes.
        """
        return []

    def build_columns(self):
        """
        Builds the columns and inserts them into the TreeView. Any
        previous columns exist, they will be in the self.columns array,
        and removed. 
        """

        # remove any existing columns, which would be stored in
        # self.columns
        
        for column in self.columns:
            self.tree.remove_column(column)
        self.columns = []

        # loop through the values returned by column_order
        
        for pair in self.column_order():

            # if the first value isn't 1, then we skip the values
            if not pair[0]:
                continue

            # extract the name from the _column_names variable, and
            # assign it to the column name. The text value is extracted
            # from the model column specified in pair[1]
            name = self._column_names[pair[1]][0]
            renderer = gtk.CellRendererText()
            renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
            column = gtk.TreeViewColumn(name, renderer, text=pair[1])

            # insert the colum into the tree
            column.set_resizable(True)
            column.set_min_width(self._column_names[pair[1]][2])
            column.set_sort_column_id(self._column_names[pair[1]][1])
            self.columns.append(column)
            self.tree.append_column(column)

    def rebuild(self):
        """
        Rebuilds the data in the database by creating a new model,
        using the build_model function passed at creation time.
        """
        self.model = self.build_model(self.get_data(), self.dbstate.db)
        self.tree.set_model(self.model)
        self._set_label()
        self._selection_changed()
