#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Donald N. Allingham
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
Provide a simplified table creation interface
"""

import cgi
import copy
from gettext import gettext as _

import gen.lib
import Errors
import Config
import DateHandler

class SimpleTable:
    """
    Provide a simplified table creation interface.
    """

    def __init__(self, access, title=None):
        """
        Initialize the class with a simpledb
        """
        self.access = access
        self.title = title
        self.__columns = []
        self.__cell_markup = {} # [col][row] = "<b>data</b>"
        self.__rows = []
        self.__link = []
        self.__sort_col = None
        self.__sort_reverse = False
        self.__link_col = None
        self.__callback_leftclick = None
        self.__callback_leftdouble = None

    def get_row_count(self):
        return len(self.__rows)

    def columns(self, *columns):
        """
        Set the columns
        """
        self.__columns = list(copy.copy(columns))
        self.__sort_vals = [[] for i in range(len(self.__columns))]

    def set_callback(self, which, callback):
        """
        Override (or add) a function for click/double-click
        """
        if which == "leftclick":
            self.__callback_leftclick = callback
        elif which == "leftdouble":
            self.__callback_leftdouble = callback

    def on_table_doubleclick(self, obj, path, view_column):
        """
        Handle events on tables. obj is a treeview
        """
        from Editors import (EditPerson, EditEvent, EditFamily, EditSource,
                             EditPlace, EditRepository)
        selection = obj.get_selection()
        store, node = selection.get_selected()
        if not node:
            return
        index = store.get_value(node, 0) # index
        if self.__callback_leftdouble:
            self.__callback_leftdouble(store.get_value(node, 1))
            return True
        elif self.__link[index]:
            objclass, handle = self.__link[index]
            if objclass == 'Person':
                person = self.access.dbase.get_person_from_handle(handle)
                try:
                    EditPerson(self.simpledoc.doc.dbstate, 
                               self.simpledoc.doc.uistate, [], person)
                    return True # handled event
                except Errors.WindowActiveError:
                    pass
            elif objclass == 'Event':
                event = self.access.dbase.get_event_from_handle(handle)
                try:
                    EditEvent(self.simpledoc.doc.dbstate, 
                              self.simpledoc.doc.uistate, [], event)
                    return True # handled event
                except Errors.WindowActiveError:
                    pass
            elif objclass == 'Family':
                ref = self.access.dbase.get_family_from_handle(handle)
                try:
                    EditFamily(self.simpledoc.doc.dbstate, 
                               self.simpledoc.doc.uistate, [], ref)
                    return True # handled event
                except Errors.WindowActiveError:
                    pass
            elif objclass == 'Source':
                ref = self.access.dbase.get_source_from_handle(handle)
                try:
                    EditSource(self.simpledoc.doc.dbstate, 
                               self.simpledoc.doc.uistate, [], ref)
                    return True # handled event
                except Errors.WindowActiveError:
                    pass
            elif objclass == 'Place':
                ref = self.access.dbase.get_place_from_handle(handle)
                try:
                    EditPlace(self.simpledoc.doc.dbstate, 
                               self.simpledoc.doc.uistate, [], ref)
                    return True # handled event
                except Errors.WindowActiveError:
                    pass
            elif objclass == 'Repository':
                ref = self.access.dbase.get_repository_from_handle(handle)
                try:
                    EditRepository(self.simpledoc.doc.dbstate, 
                               self.simpledoc.doc.uistate, [], ref)
                    return True # handled event
                except Errors.WindowActiveError:
                    pass
        return False # didn't handle event

    def on_table_click(self, obj):
        """
        Handle events on tables. obj is a treeview
        """
        selection = obj.get_selection()
        store, node = selection.get_selected()
        if not node:
            return
        index = store.get_value(node, 0) # index
        if self.__callback_leftclick:
            self.__callback_leftclick(store.get_value(node, 1))
            return True
        elif self.__link[index]:
            objclass, handle = self.__link[index]
            if objclass == 'Person':
                person = self.access.dbase.get_person_from_handle(handle)
                self.simpledoc.doc.dbstate.change_active_person(person)
                return True
        return False # didn't handle event

    def row_sort_val(self, col, val):
        """
        Add a row of data to sort by.
        """
        self.__sort_vals[col].append(val) 

    def set_link_col(self, col):
        """
        Manually sets the column that defines link.
        """
        self.__link_col = col

    def row(self, *data):
        """
        Add a row of data.
        """
        retval = [] 
        link   = None
        row = len(self.__rows)
        for col in range(len(data)):
            item = data[col]
            # FIXME: add better text representations of these objects
            if isinstance(item, basestring):
                retval.append(item)
            elif isinstance(item, (int, float, long)):
                retval.append(item)
                self.row_sort_val(col, item)
            elif isinstance(item, gen.lib.Person):
                name = self.access.name(item)
                retval.append(name)
                if (self.__link_col == col or link is None):
                    link = ('Person', item.handle)
            elif isinstance(item, gen.lib.Family): 
                father = self.access.father(item)
                mother = self.access.mother(item)
                text = ""
                if father:
                    text += " " + self.access.name(father)
                else:
                    text += " " + _("Unknown father")
                text += " " + _("and")
                if mother:
                    text += " " + self.access.name(mother)
                else:
                    text += " " + _("Unknown mother")
                retval.append(text)
                if (self.__link_col == col or link is None):
                    link = ('Family', item.handle)
            elif isinstance(item, gen.lib.Source): 
                retval.append(_('Source'))
                if (self.__link_col == col or link is None):
                    link = ('Souce', item.handle)
            elif isinstance(item, gen.lib.Event):
                name = self.access.event_type(item)
                retval.append(name)
                if (self.__link_col == col or link is None):
                    link = ('Event', item.handle)
            elif isinstance(item, gen.lib.MediaObject):
                retval.append(_('Media'))
                if (self.__link_col == col or link is None):
                    link = ('Media', item.handle)
            elif isinstance(item, gen.lib.Place):
                retval.append(_('Place'))
                if (self.__link_col == col or link is None):
                    link = ('Place', item.handle)
            elif isinstance(item, gen.lib.Repository):
                retval.append(_('Repository'))
                if (self.__link_col == col or link is None):
                    link = ('Repository', item.handle)
            elif isinstance(item, gen.lib.Note):
                retval.append(_('Note'))
                if (self.__link_col == col or link is None):
                    link = ('Note', item.handle)
            elif isinstance(item, gen.lib.Date):
                text = DateHandler.displayer.display(item)
                retval.append(text)
                if item.get_valid():
                    self.row_sort_val(col, item.sortval)
                else:
                    # sort before others:
                    self.row_sort_val(col, -1)
                    # give formatted version:
                    invalid_date_format = Config.get(Config.INVALID_DATE_FORMAT)
                    self.set_cell_markup(col, row,
                                         invalid_date_format % text)
                if (self.__link_col == col or link is None):
                    link = ('Date', item)
            elif isinstance(item, gen.lib.Span):
                text = str(item)
                retval.append(text)
                self.row_sort_val(col, float(item))
            else:
                raise AttributeError, ("unknown object type: '%s': %s" % 
                                       (item, type(item)))
        self.__link.append(link)
        self.__rows.append(retval)

    def sort(self, column_name, reverse=False):
        self.__sort_col = column_name
        self.__sort_reverse = reverse

    def __sort(self):
        idx = self.__columns.index(self.__sort_col)
        if self.__sort_reverse:
            self.__rows.sort(lambda a, b: -cmp(a[idx],b[idx]))
        else:
            self.__rows.sort(lambda a, b: cmp(a[idx],b[idx]))

    def write(self, document):
        self.simpledoc = document # simpledoc; simpledoc.doc = docgen object
        if self.simpledoc.doc.type == "standard":
            doc = self.simpledoc.doc
            doc.start_table('simple','Table')
            columns = len(self.__columns)
            if self.title:
                doc.start_row()
                doc.start_cell('TableHead',columns)
                doc.start_paragraph('TableTitle')
                doc.write_text(_(self.title))
                doc.end_paragraph()
                doc.end_cell()
                doc.end_row()
            if self.__sort_col:
                self.__sort()
            doc.start_row()
            for col in self.__columns:
                doc.start_cell('TableNormalCell',1)
                doc.write_text(col,'TableTitle')
                doc.end_cell()
            doc.end_row()
            for row in self.__rows:
                doc.start_row()
                for col in row:
                    doc.start_cell('TableNormalCell',1)
                    doc.write_text(col,'Normal')
                    doc.end_cell()
                doc.end_row()
            doc.end_table()
            doc.start_paragraph("Normal")
            doc.end_paragraph()
        elif self.simpledoc.doc.type == "gtk":
            import gtk
            buffer = self.simpledoc.doc.buffer
            text_view = self.simpledoc.doc.text_view
            model_index = 1 # start after index
            if self.__sort_col:
                sort_index = self.__columns.index(self.__sort_col)
            else:
                sort_index = 0
            treeview = gtk.TreeView()
            treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
            treeview.connect('row-activated', self.on_table_doubleclick)
            treeview.connect('cursor-changed', self.on_table_click)
            renderer = gtk.CellRendererText()
            types = [int] # index
            cnt = 0
            sort_data = []
            sort_data_types = []
            for col in self.__columns:
                types.append(type(col))
                if self.get_cell_markup(cnt):
                    column = gtk.TreeViewColumn(col,renderer,markup=model_index)
                else:
                    column = gtk.TreeViewColumn(col,renderer,text=model_index)
                if self.__sort_vals[cnt] != []:
                    sort_data.append(self.__sort_vals[cnt])
                    column.set_sort_column_id(len(self.__columns) + 
                                              len(sort_data))
                    sort_data_types.append(int)
                else:
                    column.set_sort_column_id(model_index)
                treeview.append_column(column)
                #if model_index == sort_index:
                # FIXME: what to set here?    
                model_index += 1
                cnt += 1
            if self.title:
                self.simpledoc.paragraph(self.title)
            # Make a GUI to put the tree view in
            types += sort_data_types
            model = gtk.ListStore(*types)
            treeview.set_model(model)
            iter = buffer.get_end_iter()
            anchor = buffer.create_child_anchor(iter)
            text_view.add_child_at_anchor(treeview, anchor)
            count = 0
            for data in self.__rows:
                col = 0
                rowdata = []
                for cell in data:
                    rowdata.append(self.get_cell_markup(col, count, cell))
                    col += 1
                model.append(row=([count] + list(rowdata) + [col[count] for col in sort_data]))
                count += 1
            text_view.show_all()
            self.simpledoc.paragraph("")
            self.simpledoc.paragraph("")

    def get_cell_markup(self, x, y=None, data=None):
        """
        See if a column has formatting (if x and y are supplied) or
        see if a cell has formatting. If it does, return the formatted 
        string, otherwise return data that is escaped (if that column
        has formatting), or just the plain data.
        """
        if x in self.__cell_markup:
            if y is None: 
                return True # markup for this column
            elif y in self.__cell_markup[x]:
                return self.__cell_markup[x][y]
            else:
                return cgi.escape(data)
        else:
            if y is None: 
                return False # no markup for this column
            else:
                return data

    def set_cell_markup(self, x, y, data):
        """
        Set the cell at position [x][y] to a formatted string.
        """
        col_dict = self.__cell_markup.get(x, {})
        col_dict[y] = data
        self.__cell_markup[x] = col_dict
