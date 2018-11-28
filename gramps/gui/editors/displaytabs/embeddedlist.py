#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2009       Benny Malengier
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

#-------------------------------------------------------------------------
#
# python
#
#-------------------------------------------------------------------------
import pickle

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from ...widgets.cellrenderertextedit import CellRendererTextEdit
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from ...utils import is_right_click
from .buttontab import ButtonTab


#----------------------------------------------------------------
#
# Constants
#
#----------------------------------------------------------------
TEXT_COL = 0
MARKUP_COL = 1
ICON_COL = 2
TEXT_EDIT_COL = 3

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------
class EmbeddedList(ButtonTab):
    """
    This class provides the base class for all the list tabs.

    It maintains a Gtk.TreeView, including the selection and button sensitivity.
    """

    _HANDLE_COL = -1
    _DND_TYPE   = None
    _DND_EXTRA  = None

    def __init__(self, dbstate, uistate, track, name, build_model,
                 share_button=False, move_buttons=False, jump_button=False,
                 top_label=None):
        """
        Create a new list, using the passed build_model to populate the list.
        """
        ButtonTab.__init__(self, dbstate, uistate, track, name, share_button,
                           move_buttons, jump_button, top_label)

        self.changed = False
        self.model = None
        self.build_model = build_model
        #renderer for pixbuf
        self.pb_renderer = None

        # handle the selection
        self.selection = self.tree.get_selection()
        self.selection.connect('changed', self._selection_changed)
        self.track_ref_for_deletion("selection")

        # build the columns
        self.col_icons = {}
        self.columns = []
        self.build_columns()

        if self._DND_TYPE:
            self._set_dnd()

        # set up right click option
        self.tree.connect('button-press-event', self._on_button_press)

        # build the initial data
        self.rebuild()
        self.show_all()

    def _select_row_at_coords(self, x, y):
        """
        Select the row at the current cursor position.
        """
        wx, wy = self.tree.convert_bin_window_to_widget_coords(x, y)
        row = self.tree.get_dest_row_at_pos(wx, wy)
        if row:
            self.tree.get_selection().select_path(row[0])

    def _on_button_press(self, obj, event):
        """
        Handle button press, not double-click, that is done in init_interface
        """
        self._select_row_at_coords(event.x, event.y)
        if is_right_click(event):
            #ref = self.get_selected()
            #if ref:
            self.right_click(obj, event)
            return True
        elif event.type == Gdk.EventType.BUTTON_PRESS and event.button == 2:
            fun = self.get_middle_click()
            if fun:
                fun()
                return True
        return False

    def get_popup_menu_items(self):
        """
        Create the list needed to populate the right popup action
        An entry is
            ( needs_write_access, title, function)
        """
        if self.share_btn:
            itemlist = [
                (True, _('_Add'), self.add_button_clicked),
                (True,  _('Share'), self.share_button_clicked),
                (False, _('_Edit'), self.edit_button_clicked),
                (True, _('_Remove'), self.del_button_clicked),
                ]
        else:
            itemlist = [
                (True, _('_Add'), self.add_button_clicked),
                (False, _('_Edit'), self.edit_button_clicked),
                (True, _('_Remove'), self.del_button_clicked),
            ]
        return itemlist

    def get_middle_click(self):
        return None

    def right_click(self, obj, event):
        """
        On right click show a popup menu.
        This is populated with get_popup_menu_items
        """
        self.__store_menu = Gtk.Menu() #need to keep reference or menu disappears
        menu = self.__store_menu
        menu.set_reserve_toggle_size(False)
        for (need_write, title, func) in self.get_popup_menu_items():
            item = Gtk.MenuItem.new_with_mnemonic(title)
            item.connect('activate', func)
            if need_write and self.dbstate.db.readonly:
                item.set_sensitive(False)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, None, event.button, event.time)
        return True

    def find_index(self, obj):
        """
        returns the index of the object within the associated data
        """
        return self.get_data().index(obj)

    def _set_dnd(self):
        """
        Set up drag-n-drop. The source and destination are set by calling .target()
        on the _DND_TYPE. Obviously, this means that there must be a _DND_TYPE
        variable defined that points to an entry in DdTargets.
        """

        if self._DND_EXTRA:
            dnd_types = [self._DND_TYPE,
                         self._DND_EXTRA]
        else:
            dnd_types = [self._DND_TYPE]

        #TODO GTK3: wourkaround here for bug https://bugzilla.gnome.org/show_bug.cgi?id=680638
        self.tree.enable_model_drag_dest([], Gdk.DragAction.COPY)
        self.tree.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [],
                                           Gdk.DragAction.COPY)
        tglist = Gtk.TargetList.new([])
        for tg in dnd_types:
            tglist.add(tg.atom_drag_type, tg.target_flags, tg.app_id)
        self.tree.drag_dest_set_target_list(tglist)
        tglist = Gtk.TargetList.new([])
        tglist.add(self._DND_TYPE.atom_drag_type, self._DND_TYPE.target_flags,
                   self._DND_TYPE.app_id)
        self.tree.drag_source_set_target_list(tglist)

        self.tree.connect('drag_data_get', self.drag_data_get)
        self.tree.connect_after('drag-begin', self.after_drag_begin)
        if not self.dbstate.db.readonly:
            self.tree.connect('drag_data_received', self.drag_data_received)
            self.tree.connect('drag_motion', self.tree_drag_motion)

    def drag_data_get(self, widget, context, sel_data, info, time):
        """
        Provide the drag_data_get function, which passes a tuple consisting of:

           1) Drag type defined by the .drag_type field specified by the value
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
        sel_data.set(self._DND_TYPE.atom_drag_type, 8, data)

    def drag_data_received(self, widget, context, x, y, sel_data, info, time):
        """
        Handle the standard gtk interface for drag_data_received.

        If the selection data is defined, extract the value from sel_data.data,
        and decide if this is a move or a reorder.
        """
        if sel_data and sel_data.get_data():
            data = pickle.loads(sel_data.get_data())
            if isinstance(data, list):
                data = [pickle.loads(x) for x in data]
            else:
                data = [data]
            for value in data:
                (mytype, selfid, obj, row_from) = value

                # make sure this is the correct DND type for this object
                if mytype == self._DND_TYPE.drag_type:

                    # determine the destination row
                    row = self._find_row(x, y)

                    # if the is same object, we have a move, otherwise,
                    # it is a standard drag-n-drop

                    if id(self) == selfid and self.get_selected() is not None:
                        self._move(row_from, row, obj)
                    else:
                        self._handle_drag(row, obj)
                elif self._DND_EXTRA and mytype == self._DND_EXTRA.drag_type:
                    self.handle_extra_type(mytype, obj)
            self.rebuild()

    def tree_drag_motion(self, *args):
        """
        On drag motion one wants the list to show as the database
        representation so it is clear how save will change the data.
        """
        pass

    def after_drag_begin(self, widget, drag_context):
        """
        We want to show the icon during drag instead of the long row entry
        """
        Gtk.drag_set_icon_name(drag_context, self.get_icon_name(), 0, 0)

    def handle_extra_type(self, objtype, obj):
        pass

    def _find_row(self, x, y):
        row = self.tree.get_dest_row_at_pos(x, y)
        if row is None:
            return len(self.get_data())
        else:
            path = row[0].get_indices()
            if row[1] in (Gtk.TreeViewDropPosition.BEFORE,
                          Gtk.TreeViewDropPosition.INTO_OR_BEFORE):
                return path[0]
            else:
                return path[0]+1

    def _handle_drag(self, row, obj):
        self.get_data().insert(row, obj)
        self.changed = True

    def _move(self, row_from, row_to, obj):
        dlist = self.get_data()
        if row_from < row_to:
            dlist.insert(row_to, obj)
            del dlist[row_from]
        else:
            del dlist[row_from]
            dlist.insert(row_to, obj)
        self.changed = True

    def _move_up(self, row_from, obj, selmethod=None):
        """
        Move the item a position up in the EmbeddedList.
        Eg: 0,1,2,3 needs to become 0,2,1,3, here row_from = 2
        """
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
        # The height/location of Gtk.treecells is calculated in an idle handler
        # so use idle_add to scroll cell into view.
        GLib.idle_add(self.tree.scroll_to_cell, path)

    def _move_down(self, row_from, obj, selmethod=None):
        """
        Move the item a position down in the EmbeddedList.
        Eg: 0,1,2,3 needs to become 0,2,1,3, here row_from = 1
        """
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
        GLib.idle_add(self.tree.scroll_to_cell, path)

    def get_icon_name(self):
        """
        Specifies the basic icon used for a generic list. Typically,
        a derived class will override this. The icon chosen is the
        STOCK_JUSTIFY_FILL icon, which in the default GTK style
        looks kind of like a list.
        """
        return 'format-justify-fill'

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
                self._move_up(pos, ref)

    def down_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            pos = self.find_index(ref)
            if pos >= 0 and pos < len(self.get_data())-1:
                self._move_down(pos, ref)

    def build_interface(self):
        """
        Builds the interface, instantiating a Gtk.TreeView in a
        Gtk.ScrolledWindow.
        """

        # create the tree, turn on rule hinting and connect the
        # button press to the double click function.

        self.tree = Gtk.TreeView()
        self.tree.set_reorderable(True)
        self.tree.connect('button_press_event', self.double_click)
        self.tree.connect('key_press_event', self.key_pressed)
        self.track_ref_for_deletion("tree")

        # create the scrolled window, and attach the treeview
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.tree)
        self.pack_end(scroll, True, True,0)

    def get_selected(self):
        """
        Return the value associated with selected row in the model,
        based of the _HANDLE_COL value. Each model must define this
        to indicate what the returned value should be. If no selection
        has been made, None is returned.
        """
        (model, node) = self.selection.get_selected()
        if node:
            return model.get_value(node, self._HANDLE_COL)
        return None

    def is_empty(self):
        """
        Return True if the get_data returns a length greater than
        0. Typically, get_data returns the list of associated data.
        """
        return len(self.get_data()) == 0

    def get_data(self):
        """
        Return the data associated with the list. This is typically
        a list of objects.

        This should be overridden in the derived classes.
        """
        raise NotImplementedError

    def column_order(self):
        """
        Specifies the column order for the columns. This should be
        in the format of a list of tuples, in the format of (int,int),
        where the first in indicates if the column is visible, and the
        second column indicates the index into the model.

        This should be overridden in the derived classes.
        """
        raise NotImplementedError

    def setup_editable_col(self):
        """
        inherit this and set the variables needed for editable columns
        Variable edit_col_funcs needs to be a dictionary from model col_nr to
        function to call for
        Example:
        self.edit_col_funcs ={1: {'edit_start': self.on_edit_start,
                                  'edited': self.on_edited
                              }}
        """
        self.edit_col_funcs ={}

    def build_columns(self):
        """
        Builds the columns and inserts them into the TreeView. Any
        previous columns exist, they will be in the self.columns array,
        and removed.
        """

        # remove any existing columns, which would be stored in
        # self.columns

        list(map(self.tree.remove_column, self.columns))
        self.columns = []
        self.setup_editable_col()

        # loop through the values returned by column_order
        for pair in self.column_order():

            # if the first value isn't 1, then we skip the values
            if not pair[0]:
                continue

            # extract the name from the _column_names variable, and
            # assign it to the column name. The text value is extracted
            # from the model column specified in pair[1]
            name = self._column_names[pair[1]][0]
            col_icon = self._column_names[pair[1]][5]
            model_col = self._column_names[pair[1]][1]
            type_col = self._column_names[pair[1]][3]

            if (type_col in [TEXT_COL, MARKUP_COL, TEXT_EDIT_COL]):
                if type_col == TEXT_EDIT_COL:
                    renderer = CellRendererTextEdit()
                else:
                    renderer = Gtk.CellRendererText()
                renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
                if type_col == TEXT_COL or type_col == TEXT_EDIT_COL:
                    column = Gtk.TreeViewColumn(name, renderer, text=pair[1])
                else:
                    column = Gtk.TreeViewColumn(name, renderer, markup=pair[1])
                if not self._column_names[pair[1]][4] == -1:
                    #apply weight attribute
                    column.add_attribute(renderer, "weight",
                                         self._column_names[pair[1]][4])
                #set up editable
                if type_col == TEXT_EDIT_COL:
                    #model col must have functions defined
                    callbacks = self.edit_col_funcs[model_col]
                    for renderer in column.get_cells():
                        renderer.set_property('editable', not self.dbstate.db.readonly)
                        renderer.connect('editing_started',
                                            callbacks['edit_start'], model_col)
                        renderer.connect('edited', callbacks['edited'], model_col)
            elif self._column_names[pair[1]][3] == ICON_COL:
                self.col_icons[pair[1]] = col_icon
                self.pb_renderer = Gtk.CellRendererPixbuf()
                column = Gtk.TreeViewColumn(name, self.pb_renderer)
                column.set_cell_data_func(self.pb_renderer, self.icon_func, pair[1])
            else:
                raise NotImplementedError('Unknown column type: %s, with column name %s' % (type_col, self._column_names[pair[1]][3]))
            if col_icon is not None:
                image = Gtk.Image()
                image.set_from_icon_name(col_icon, Gtk.IconSize.MENU)
                image.set_tooltip_text(name)
                image.show()
                column.set_widget(image)
                column.set_resizable(False)
            else:
                # insert the colum into the tree
                column.set_resizable(True)
            column.set_clickable(True)
            if self._column_names[pair[1]][2] != -1:
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
                #column.set_min_width(self._column_names[pair[1]][2])
                column.set_fixed_width(self._column_names[pair[1]][2])
            else:
                column.set_expand(True)

            column.set_sort_column_id(self._column_names[pair[1]][1])
            self.columns.append(column)
            self.tree.append_column(column)
        self.track_ref_for_deletion("columns")

    def icon_func(self, column, renderer, model, iter_, col_num):
        '''
        Set the stock icon property of the cell renderer.  We use a cell data
        function because there is a problem returning None from a model.
        '''
        icon_name = model.get_value(iter_, col_num)
        if icon_name == '' or icon_name == False:
            icon_name = None
        elif icon_name == True:
            icon_name = self.col_icons[col_num]
        renderer.set_property('icon-name', icon_name)

    def construct_model(self):
        """
        Method that creates the model using the passed build_model parameter
        """
        return self.build_model(self.get_data(), self.dbstate.db)

    def rebuild(self):
        """
        Rebuilds the data in the database by creating a new model,
        using the build_model function passed at creation time.
        """
        offset = self.tree.get_visible_rect()
        #during rebuild, don't do _selection_changed
        self.dirty_selection = True
        (model, node) = self.selection.get_selected()
        selectedpath = None
        if node:
            selectedpath = model.get_path(node)
        if self.model and hasattr(self.model, 'destroy'):
            self.tree.set_model(None)
            self.model.destroy()
        try:
            self.model = self.construct_model()
        except AttributeError as msg:
            from ...dialog import RunDatabaseRepair
            import traceback
            traceback.print_exc()
            RunDatabaseRepair(str(msg), parent=self.uistate.window)
            return

        self.tree.set_model(self.model)
        #reset previous select
        if selectedpath is not None:
            self.selection.select_path(selectedpath)
        #self.selection.select_path(node)
        self._set_label()
        #model and tree are reset, allow _selection_changed again, and force it
        self.dirty_selection = False
        self._selection_changed()
        if self.tree.get_realized():
            GLib.idle_add(self.tree.scroll_to_point, offset.x, offset.y)
        self.post_rebuild(selectedpath)

    def post_rebuild(self, prebuildpath):
        """
        Allow post rebuild embeddedlist specific handling.
        @param prebuildpath: path selected before rebuild, None if none
        @type prebuildpath: tree path
        """
        pass

    def rebuild_callback(self):
        """
        The view must be remade when data changes outside this tab.
        Use this method to connect to after a db change. It makes sure the
        data is obtained again from the present object and the db what is not
        present in the obj, and the view rebuild
        """
        self.changed = True
        self.rebuild()
