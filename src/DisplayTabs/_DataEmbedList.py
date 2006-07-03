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
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
from _DataModel import DataModel
from _EmbeddedList import EmbeddedList

#-------------------------------------------------------------------------
#
# DataEmbedList
#
#-------------------------------------------------------------------------
class DataEmbedList(EmbeddedList):

    _HANDLE_COL = 0
    _DND_TYPE   = None
    
    _column_names = [
        (_('Key'), 0, 150), 
        (_('Value'), 1, 250), 
        ]
    
    def __init__(self, dbstate, uistate, track, obj):
        self.obj = obj
        
        EmbeddedList.__init__(self, dbstate, uistate, track, 
                              _('Data'), DataModel)

    def build_columns(self):
        EmbeddedList.build_columns(self)

        # Need to add attributes to renderers
        # and connect renderers to the 'edited' signal
        for colno in range(len(self.columns)):
            for renderer in self.columns[colno].get_cell_renderers():
                renderer.set_property('editable',True)
                renderer.connect('edited',self.edit_inline,colno)

    def get_data(self):
        return self.obj.get_data_map()

    def is_empty(self):
        return len(self.model)==0

    def _get_map_from_model(self):
        new_map = {}
        for idx in range(len(self.model)):
            node = self.model.get_iter(idx)
            key = unicode(self.model.get_value(node,0))
            value = unicode(self.model.get_value(node,1))
            if key.strip():
                new_map[key] = value
        return new_map
        
    def update(self):
        new_map = self._get_map_from_model()
        self.obj.set_data_map(new_map)
        self._set_label()

    def column_order(self):
        return ((1, 0), (1, 1))

    def add_button_clicked(self, obj):
        node = self.model.append(row=['',''])
        self.selection.select_iter(node)
        path = self.model.get_path(node)
        self.tree.set_cursor_on_cell(path,
                                     focus_column=self.columns[0],
                                     focus_cell=None,
                                     start_editing=True)

    def del_button_clicked(self, obj):
        (model,node) = self.selection.get_selected()
        if node:
            self.model.remove(node)
            self.update()

    def edit_inline(self, cell, path, new_text, data):
        node = self.model.get_iter(path)
        self.model.set_value(node,data,new_text)
        self.update()
            
    def edit_button_clicked(self, obj):
        (model,node) = self.selection.get_selected()
        if node:
            path = self.model.get_path(node)
            self.tree.set_cursor_on_cell(path,
                                         focus_column=self.columns[0],
                                         focus_cell=None,
                                         start_editing=True)
