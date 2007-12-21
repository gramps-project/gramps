#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Donald N. Allingham
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

"""
Provides a simplified table creation interface
"""

import copy

class SimpleTable:
    """
    Provides a simplified table creation interface.
    """

    def __init__(self, access, doc, title=None):
        """
        Initializes the class with the real document
        """
        self.access = access
        self.doc = doc # simpledoc; doc.doc = actual document
        self.title = title
        self.__columns = []
        self.__rows = []
        self.__sort_col = None
        self.__sort_reverse = False

    def columns(self, *columns):
        self.__columns = list(copy.copy(columns))

    def row(self, *data):
        self.__rows.append(copy.copy(data))

    def sort(self, column_name, reverse=False):
        self.__sort_col = column_name
        self.__sort_reverse = reverse

    def __sort(self):
        idx = self.__columns.index(self.__sort_col)
        if self.__sort_reverse:
            self.__rows.sort(lambda a, b: -cmp(a[idx],b[idx]))
        else:
            self.__rows.sort(lambda a, b: cmp(a[idx],b[idx]))

    def write(self):
        if self.doc.doc.type == "standard":
            self.doc.start_table('simple','Table')
            columns = len(self.__columns)
            if self.title:
                self.doc.start_row()
                self.doc.start_cell('TableHead',columns)
                self.doc.start_paragraph('TableTitle')
                self.doc.write_text(_(self.title))
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()
            if self.__sort_col:
                self.__sort()
            self.doc.start_row()
            for col in self.__columns:
                self.doc.start_cell('TableNormalCell',1)
                self.doc.write_text(col,'TableTitle')
                self.doc.end_cell()
            self.doc.end_row()
            for row in self.__rows:
                self.doc.start_row()
                for col in row:
                    self.doc.start_cell('TableNormalCell',1)
                    self.doc.write_text(col,'Normal')
                    self.doc.end_cell()
                self.doc.end_row()
            self.doc.end_table()
            self.doc.start_paragraph("Normal")
            self.doc.end_paragraph()
        elif self.doc.doc.type == "gtk":
            import gtk
            buffer = self.doc.doc.buffer
            text_view = self.doc.doc.text_view
            model_index = 0
            if self.__sort_col:
                sort_index = self.__columns.index(self.__sort_col)
            else:
                sort_index = 0
            treeview = gtk.TreeView()
            treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
            renderer = gtk.CellRendererText()
            types = []
            for col in self.__columns:
                types.append(type(col))
                column = gtk.TreeViewColumn(col,renderer,text=model_index)
                column.set_sort_column_id(model_index)
                treeview.append_column(column)
                #if model_index == sort_index:
                # FIXME: what to set here?    
                model_index += 1
            frame = gtk.Frame()
            frame.add(treeview)
            model = gtk.ListStore(*types)
            treeview.set_model(model)
            iter = buffer.get_end_iter()
            anchor = buffer.create_child_anchor(iter)
            text_view.add_child_at_anchor(frame, anchor)
            for data in self.__rows:
                model.append(row=list(data))
            frame.show_all()
            self.doc.paragraph("")
