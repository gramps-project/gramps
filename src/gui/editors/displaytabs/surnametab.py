#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2010       Benny Malengier
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
# Python classes
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK classes
#
#-------------------------------------------------------------------------
import gtk
_TAB = gtk.gdk.keyval_from_name("Tab")
_ENTER = gtk.gdk.keyval_from_name("Enter")

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
from surnamemodel import SurnameModel
from embeddedlist import EmbeddedList
from DdTargets import DdTargets
from gen.lib import Surname, NameOriginType

#-------------------------------------------------------------------------
#
# SurnameTab
#
#-------------------------------------------------------------------------
class SurnameTab(EmbeddedList):

    _HANDLE_COL = 5
    _DND_TYPE   = DdTargets.SURNAME
    
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
        (_('Prefix'), 0, 150, 0, -1),
        (_('Surname'), 1, 250, 0, -1),
        (_('Connector'), 2, 100, 0, -1),
        ]
    
    def __init__(self, dbstate, uistate, track, name):
        self.obj = name
        self.curr_col = -1
        self.curr_cellr = None
        self.curr_celle = None
        
        EmbeddedList.__init__(self, dbstate, uistate, track, _('Family Surnames'), 
                              SurnameModel, move_buttons=True)

    def build_columns(self):
        #first the standard text columns with normal method
        EmbeddedList.build_columns(self)

        # Need to add attributes to renderers
        # and connect renderers to the 'edited' signal
        for colno in range(len(self.columns)):
            for renderer in self.columns[colno].get_cell_renderers():
                renderer.set_property('editable', not self.dbstate.db.readonly)
                renderer.connect('editing_started', self.edit_start, colno)
                renderer.connect('edited', self.edit_inline, colno)
        
        # now we add the two special columns
        # TODO 

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
            surn.set_prefix(unicode(self.model.get_value(node, 0)))
            surn.set_surname(unicode(self.model.get_value(node, 1)))
            surn.set_connector(unicode(self.model.get_value(node, 2)))
            surn.set_primary(self.model.get_value(node, 4))
            new_list += [surn]
        return new_list
        
    def update(self):
        new_map = self._get_surn_from_model()
        self.obj.set_surname_list(new_map)
        # update name in title name editor
        # TODO

    def column_order(self):
        # order of columns for EmbeddedList. Only the text columns here
        return ((1, 0), (1, 1), (1, 2))

    def add_button_clicked(self, obj):
        prim = False
        if len(self.obj.get_surname_list()) == 0:
            prim = true
        node = self.model.append(row=['', '', '', NameOriginType(), prim, 
                                      Surname()])
        self.selection.select_iter(node)
        path = self.model.get_path(node)
        self.tree.set_cursor_on_cell(path,
                                     focus_column=self.columns[0],
                                     focus_cell=None,
                                     start_editing=True)

    def del_button_clicked(self, obj):
        (model, node) = self.selection.get_selected()
        if node:
            self.model.remove(node)
            self.update()

    def edit_start(self, cellr, celle, path, colnr):
        self.curr_col = colnr
        self.curr_cellr = cellr
        self.curr_celle = celle
        
    def edit_inline(self, cell, path, new_text, colnr):
        node = self.model.get_iter(path)
        self.model.set_value(node, colnr, new_text)
        self.update()
            
    def edit_button_clicked(self, obj):
        (model, node) = self.selection.get_selected()
        if node:
            path = self.model.get_path(node)
            self.tree.set_cursor_on_cell(path,
                                         focus_column=self.columns[0],
                                         focus_cell=None,
                                         start_editing=True)

    def key_pressed(self, obj, event):
        """
        Handles the key being pressed. 
        Here we make sure tab moves to next value in row
        """
        if not EmbeddedList.key_pressed(self, obj, event):
            if event.type == gtk.gdk.KEY_PRESS and event.keyval in (_TAB,):
                if event.state not in (gtk.gdk.SHIFT_MASK, gtk.gdk.CONTROL_MASK):
                    self.next_cell()
                elif event.state in (gtk.gdk.SHIFT_MASK, gtk.gdk.CONTROL_MASK):
                    self.prev_cell()
                else:
                    return
            else:
                return
            return True

    def next_cell(self):
        """
        Move to the next cell to edit it
        """           
        (model, node) = self.selection.get_selected()
        if node:
            path = self.model.get_path(node)
            if  self.curr_col+1 < len(self.columns):
                self.tree.set_cursor_on_cell(path,
                                         focus_column=self.columns[self.curr_col+1],
                                         focus_cell=None,
                                         start_editing=True)
            elif self.curr_col+1 == len(self.columns):
                #go to next line if there is one
                if path[0]+1 < len(self.obj.get_surname_list()):
                    newpath = (path[0]+1,)
                    self.selection.select_path(newpath)
                    self.tree.set_cursor_on_cell(newpath,
                                     focus_column=self.columns[0],
                                     focus_cell=None,
                                     start_editing=True)
                else:
                    #stop editing
                    self.curr_celle.editing_done()
        
    def prev_cell(self):
        """
        Move to the next cell to edit it
        """     
        (model, node) = self.selection.get_selected()
        if node:
            path = self.model.get_path(node)
            if  self.curr_col > 0:
                self.tree.set_cursor_on_cell(path,
                                         focus_column=self.columns[self.curr_col-1],
                                         focus_cell=None,
                                         start_editing=True)
            elif self.curr_col == 0:
                #go to prev line if there is one
                if path[0] > 0:
                    newpath = (path[0]-1,)
                    self.selection.select_path(newpath)
                    self.tree.set_cursor_on_cell(newpath,
                                     focus_column=self.columns[-1],
                                     focus_cell=None,
                                     start_editing=True)
                else:
                    #stop editing
                    self.curr_celle.editing_done()
