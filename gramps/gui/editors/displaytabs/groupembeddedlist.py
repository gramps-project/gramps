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

# -------------------------------------------------------------------------
#
# python
#
# -------------------------------------------------------------------------
import pickle

# -------------------------------------------------------------------------
#
# GTK libraries
#
# -------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import GLib

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from ...utils import is_right_click
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL


# -------------------------------------------------------------------------
#
# Classes
#
# -------------------------------------------------------------------------
class GroupEmbeddedList(EmbeddedList):
    """
    This class provides the base class for all the list tabs that show
    grouped data.

    It maintains a Gtk.TreeView, including the selection and button sensitivity.
    """

    _WORKGROUP = 0

    def __init__(
        self,
        dbstate,
        uistate,
        track,
        name,
        build_model,
        config_key,
        share_button=False,
        move_buttons=False,
        jump_button=False,
        **kwargs,
    ):
        """
        Create a new list, using the passed build_model to populate the list.
        """
        self.kwargs = kwargs
        EmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            name,
            build_model,
            config_key,
            share_button,
            move_buttons,
            jump_button,
        )
        # connect click on the first column
        self.columns[0].connect("clicked", self.groupcol_click)
        for col in self.columns[1:]:
            col.connect("clicked", self.col_click)
        self.dbsort = True

    def construct_model(self):
        """
        Method that creates the model using the passed build_model parameter
        Overwrites the EmbeddedList calling sequence by adding the different
        groups
        """
        return self.build_model(
            self.get_data(), self.dbstate.db, self.groups(), **self.kwargs
        )

    def groups(self):
        """
        Return the (group key, group name)s in the order as given by get_data()
        """
        raise NotImplementedError

    def groupcol_click(self, obj):
        """
        The group column is clicked, sort it as it was
        """
        self.columns[0].set_sort_order(Gtk.SortType.ASCENDING)
        self.rebuild()
        self.dbsort = True

    def col_click(self, obj):
        self.dbsort = False

    def _on_button_press(self, obj, event):
        """
        Handle button press, not double-click, that is done in init_interface
        """
        self._select_row_at_coords(event.x, event.y)
        if is_right_click(event):
            obj = self.get_selected()
            if obj and obj[1]:
                self._tmpgroup = obj[0]
                self.right_click(obj[1], event)
                return True
        elif event.type == Gdk.EventType.BUTTON_PRESS and event.button == 2:
            fun = self.get_middle_click()
            if fun:
                fun()
                return True
        return False

    def is_empty(self):
        """
        Return True if the get_data returns a length greater than
        0. Typically, get_data returns the list of associated data.
        """
        return len(self.get_data()[self._WORKGROUP]) == 0

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
        if not obj or obj[1] is None:
            # nothing selected or a grouping selected
            return

        # pickle the data, and build the tuple to be passed
        value = (self._DND_TYPE.drag_type, id(self), obj[1], self.find_index(obj))
        data = pickle.dumps(value)

        # pass as a string (8 bits)
        sel_data.set(self._DND_TYPE.atom_drag_type, 8, data)

    def drag_data_received(self, widget, context, x, y, sel_data, info, time):
        """
        Handle the standard gtk interface for drag_data_received.

        If the selection data is define, extract the value from sel_data.data,
        and decide if this is a move or a reorder.
        """
        if sel_data and sel_data.get_data():
            # make sure data = 1 row
            # pickle.loads(sel_data.data)[3] = 0
            try:
                (mytype, selfid, obj, row_from) = pickle.loads(sel_data.get_data())
            except ValueError:
                return

            # make sure this is the correct DND type for this object
            if mytype == self._DND_TYPE.drag_type:
                # determine the destination row
                row = self._find_row(x, y)

                # if this is same object, we have a move, otherwise,
                # it is a standard drag-n-drop

                if id(self) == selfid and self.get_selected() is not None:
                    self._move(row_from, row, obj)
                else:
                    self._handle_drag(row, obj)
                self.rebuild()
            elif self._DND_EXTRA and mytype == self._DND_EXTRA.drag_type:
                self.handle_extra_type(mytype, obj)

    def tree_drag_motion(self, *args):
        """
        On drag motion one wants the list to show as the database
        representation so it is clear how save will change the data
        """
        if not self.dbsort:
            self.columns[0].clicked()

    def find_index(self, obj):
        """
        Returns the index of the object within the associated data.
        This will be a path (groupindex, index)
        """
        data = self.get_data()
        groupindex = None
        index = None
        for groupindex, group in enumerate(data):
            try:
                index = group.index(obj[1])
                break
            except ValueError:
                pass
        return (groupindex, index)

    def _find_row(self, x, y):
        """
        Return a path as [groupindex, index] of the row on x,y.
        If no row, then a new line in the working group is returned
        """
        dest = self.tree.get_dest_row_at_pos(x, y)
        if dest is None:
            # Below last item in list
            if self.is_empty():
                return [self._WORKGROUP, 0]
            else:
                return [self._WORKGROUP, len(self.get_data()[self._WORKGROUP])]
        else:
            path = dest[0].get_indices()
            wgroup = path[0]
            if len(path) == 1:
                # On a heading
                if dest[1] == Gtk.TreeViewDropPosition.BEFORE:
                    if wgroup != 0:
                        # If before then put at end of previous group
                        return (wgroup - 1, len(self.get_data()[wgroup - 1]))
                    else:
                        # unless it is the first group
                        return (wgroup, 0)
                else:
                    return (wgroup, 0)
            else:
                if dest[1] in (
                    Gtk.TreeViewDropPosition.BEFORE,
                    Gtk.TreeViewDropPosition.INTO_OR_BEFORE,
                ):
                    return (wgroup, path[1])
                else:
                    return (wgroup, path[1] + 1)

    def _handle_drag(self, row, obj):
        """
        drag from external place to row of obj
        """
        if row[0] == self._WORKGROUP:
            self.get_data()[self._WORKGROUP].insert(row[1], obj)
            self.changed = True
        else:
            self.dropnotworkgroup(row, obj)

    def dropnotworkgroup(self, row, obj):
        """
        Drop of obj on row that is not WORKGROUP
        """
        pass

    def _move(self, row_from, row_to, obj):
        """
        Drag and drop move of the order. Allow in workgroup
        """
        if row_from[0] == row_to[0] and row_from[0] == self._WORKGROUP:
            dlist = self.get_data()[self._WORKGROUP]
            if row_from[1] < row_to[1]:
                dlist.insert(row_to[1], obj)
                del dlist[row_from[1]]
            else:
                del dlist[row_from[1]]
                dlist.insert(row_to[1], obj)
            self.changed = True
        elif row_from[0] == self._WORKGROUP:
            self.move_away_work(row_from, row_to, obj)
        elif row_to[0] == self._WORKGROUP:
            self.move_to_work(row_from, row_to, obj)

    def move_away_work(self, row_from, row_to, obj):
        """
        move from the workgroup to a not workgroup
        handle in inherited class, default is nothing changes
        """
        pass

    def move_to_work(self, row_from, row_to, obj):
        """
        move from a non workgroup to the workgroup
        handle in inherited class, default is nothing changes
        """
        pass

    def _move_up(self, row_from, obj, selmethod=None):
        """
        Move the item a position up in the EmbeddedList.
        Eg: 0,1,2,3 needs to become 0,2,1,3, here row_from = 2
        """
        if row_from[0] == self._WORKGROUP:
            if selmethod:
                dlist = selmethod()
            else:
                dlist = self.get_data()[self._WORKGROUP]
            del dlist[row_from[1]]
            dlist.insert(row_from[1] - 1, obj)
            self.changed = True
            self.rebuild()
            # select the row
            path = (self._WORKGROUP, row_from[1] - 1)
            self.tree.get_selection().select_path(path)
            GLib.idle_add(self.tree.scroll_to_cell, path)
        else:
            self._move_up_notwork(row_from, obj, selmethod)

    def _move_up_notwork(self, row_from, obj, selmethod=None):
        """
        move up outside of workgroup
        """
        pass

    def _move_up_group(self, groupindex):
        """
        move up pressed on the group
        """
        pass

    def _move_down(self, row_from, obj, selmethod=None):
        """
        Move the item a position down in the EmbeddedList.
        Eg: 0,1,2,3 needs to become 0,2,1,3, here row_from = 1
        """
        if row_from[0] == self._WORKGROUP:
            if selmethod:
                dlist = selmethod()
            else:
                dlist = self.get_data()[self._WORKGROUP]
            del dlist[row_from[1]]
            dlist.insert(row_from[1] + 1, obj)
            self.changed = True
            self.rebuild()
            # select the row
            path = (self._WORKGROUP, row_from[1] + 1)
            self.tree.get_selection().select_path(path)
            GLib.idle_add(self.tree.scroll_to_cell, path)
        else:
            self._move_down_notwork(row_from, obj, selmethod)

    def _move_down_notwork(self, row_from, obj, selmethod=None):
        """
        move down outside of workgroup
        """
        pass

    def _move_down_group(self, groupindex):
        """
        move down pressed on the group
        """
        pass

    def get_icon_name(self):
        """
        Specifies the basic icon used for a generic list. Typically,
        a derived class will override this. The icon chosen is the
        STOCK_JUSTIFY_FILL icon, which in the default GTK style
        looks kind of like a list.
        """
        return "format-justify-fill"

    def del_button_clicked(self, obj):
        ref = self.get_selected()
        if ref and ref[1] is not None:
            if ref[0] == self._WORKGROUP:
                ref_list = self.get_data()[self._WORKGROUP]
                ref_list.remove(ref[1])
                self.changed = True
                self.rebuild()
            else:
                self.del_notwork(ref)

    def del_notwork(self, ref):
        """
        delete of ref asked that is not part of workgroup
        """
        pass

    def up_button_clicked(self, obj):
        ref = self.get_selected()
        if ref and ref[1] is not None:
            pos = self.find_index(ref)
            if pos[1] > 0:
                self._move_up(pos, ref[1])
        elif ref and ref[1] is None:
            self._move_up_group(ref[0])

    def down_button_clicked(self, obj):
        ref = self.get_selected()
        if ref and ref[1] is not None:
            pos = self.find_index(ref)
            if pos[1] >= 0 and pos[1] < len(self.get_data()[pos[0]]) - 1:
                self._move_down(pos, ref[1])
        elif ref and ref[1] is None:
            self._move_down_group(ref[0])
