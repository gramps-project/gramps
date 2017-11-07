#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2017       Paul Culley
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
# Python classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# GTK classes
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from .surnamemodel import SurnameModel
from ..editsurname import EditSurname
from .embeddedlist import EmbeddedList, TEXT_COL
from gramps.gen.lib import Surname, NameOriginType


#-------------------------------------------------------------------------
#
# SurnameTab
#
#-------------------------------------------------------------------------
class SurnameTab(EmbeddedList):

    _HANDLE_COL = 5

    _MSG = {
        'add'   : _('Create and add a new surname'),
        'del'   : _('Remove the selected surname'),
        'edit'  : _('Edit the selected surname'),
        'up'    : _('Move the selected surname upwards'),
        'down'  : _('Move the selected surname downwards'),
    }

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text
    _column_names = [
        (_('Prefix'), -1, 150, TEXT_COL, -1, None),
        (_('Surname'), -1, -1, TEXT_COL, -1, None),
        (_('Connector'), -1, 100, TEXT_COL, -1, None),
        (_('Origin'), -1, 150, TEXT_COL, -1, None)]
    _column_toggle = (_('Name|Primary'), -1, 80, 4)

    def __init__(self, dbstate, uistate, track, name, on_change=None,
                 top_label='<b>%s</b>' % _("Multiple Surnames") ):
        self.obj = name
        self.on_change = on_change
        self.curr_col = -1
        self.curr_cellr = None
        self.curr_celle = None

        EmbeddedList.__init__(self, dbstate, uistate, track, _('Family Surnames'),
                              SurnameModel, move_buttons=True,
                              top_label=top_label)
        self.tree.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)

    def build_columns(self):
        #first the standard text columns with normal method
        EmbeddedList.build_columns(self)

        # now we add the special column
        # toggle box for primary
        name = self._column_toggle[0]
        renderer = Gtk.CellRendererToggle()
        renderer.set_property('activatable', True)
        renderer.set_property('radio', True)
        renderer.connect( 'toggled', self.on_prim_toggled, self._column_toggle[3])
        # add to treeview
        column = Gtk.TreeViewColumn(name, renderer, active=self._column_toggle[3])
        column.set_resizable(False)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.set_alignment(0.5)
        column.set_sort_column_id(self._column_toggle[1])
        column.set_max_width(self._column_toggle[2])
        self.columns.append(column)
        self.tree.append_column(column)

    def get_data(self):
        return self.obj.get_surname_list()

    def is_empty(self):
        return len(self.model)==0

    def _get_surn_from_model(self):
        """
        Return new surname_list for storing in the name based on content of
        the model
        """
        new_list = []
        for idx in range(len(self.model)):
            node = self.model.get_iter(idx)
            surn = self.model.get_value(node, 5)
            surn.set_primary(self.model.get_value(node, 4))
            new_list += [surn]
        return new_list

    def update(self):
        """
        Store the present data in the model to the name object
        """
        new_map = self._get_surn_from_model()
        self.obj.set_surname_list(new_map)
        # update name in previews
        if self.on_change:
            self.on_change()

    def post_rebuild(self, prebuildpath):
        """
        Called when data model has changed, in particular necessary when row
        order is updated.
        @param prebuildpath: path selected before rebuild, None if none
        @type prebuildpath: tree path
        """
        if self.on_change:
            self.on_change()

    def column_order(self):
        # order of columns for EmbeddedList. Only the text columns here
        return ((1, 0), (1, 1), (1, 2), (1, 3))

    def add_button_clicked(self, obj):
        """Add button is clicked, add a surname to the person"""
        prim = False
        if len(self.obj.get_surname_list()) == 0:
            prim = True
        surname = Surname()
        node = self.model.append(row=['', '', '', str(NameOriginType()), prim,
                                      surname])
        EditSurname(self.dbstate, self.uistate, self.track, surname,
                    callback=self.edited)
        self.selection.select_iter(node)
        self.update()

    def del_button_clicked(self, obj):
        """
        Delete button is clicked. Remove from the model
        """
        (model, node) = self.selection.get_selected()
        if node:
            self.model.remove(node)
            self.update()

    def edited(self, surn):
        """
        The edit is done, update model with the results
        """
        (model, node) = self.selection.get_selected()
        row = [surn.get_prefix(), surn.get_surname(), surn.get_connector(),
               str(surn.get_origintype()), surn.get_primary(), surn]
        for indx, cell in enumerate(row):
            if indx == 1 and cell == '':  # Surname missing
                cell = _("Missing surname")
            self.model.set_value(node, indx, cell)
        self.update()

    def on_prim_toggled(self, cell, path, colnr):
        """
        Primary surname on path is toggled. colnr must be the col
        in the model
        """
        #obtain current value
        node = self.model.get_iter(path)
        old_val = self.model.get_value(node, colnr)
        for nr in range(len(self.obj.get_surname_list())):
            if nr == int(path[0]):
                if old_val:
                    #True remains True
                    break
                else:
                    #This value becomes True
                    self.model.set_value(self.model.get_iter((nr,)), colnr, True)
            else:
                self.model.set_value(self.model.get_iter((nr,)), colnr, False)
        self.update()
        return

    def edit_button_clicked(self, obj):
        """ Edit button clicked
        """
        (model, node) = self.selection.get_selected()
        if node:
            surname = self.model.get_value(node, 5)
            EditSurname(self.dbstate, self.uistate, self.track, surname,
                        callback=self.edited)
