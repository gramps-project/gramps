#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Donald N. Allingham
# Copyright (C) 2009  Douglas S. Blank
# Copyright (C) 2011       Tim G L Lyons
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
# Simple/_SimpleTable.py
# $Id$
#

"""
Provide a simplified table creation interface
"""

import cgi
import copy
from gen.ggettext import sgettext as _
from TransUtils import trans_objclass
import cPickle as pickle

import gen.lib
import Errors
import config
import gen.datehandler

class SimpleTable(object):
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
        self.__cell_type = {} # [col] = "text"
        self.__rows = []
        self.__raw_data = []
        self.__link = []
        self.__sort_col = None
        self.__sort_reverse = False
        self.__link_col = None
        self._callback_leftclick = None
        self._callback_leftdouble = None
        self.model_index_of_column = {}

    def get_row_count(self):
        return len(self.__rows)

    def get_row(self, index):
        return self.__rows[index]

    def get_raw_data(self, index):
        return self.__raw_data[index]

    def columns(self, *cols):
        """
        Set the columns
        """
        self.__columns = [unicode(col) for col in cols]
        self.__sort_vals = [[] for i in range(len(self.__columns))]

    def set_callback(self, which, callback):
        """
        Override (or add) a function for click/double-click
        """
        if which == "leftclick":
            self._callback_leftclick = callback
        elif which == "leftdouble":
            self._callback_leftdouble = callback

    def button_press_event(self, treeview, event):
        import gtk
        index = None
        button_code = None
        event_time = None
        func = None
        if type(event) == bool: # enter
            button_code = 3
            event_time = 0
            selection = treeview.get_selection()
            store, paths = selection.get_selected_rows()
            tpath = paths[0] if len(paths) > 0 else None
            node = store.get_iter(tpath) if tpath else None
            if node:
                treeview.grab_focus()
                index = store.get_value(node, 0) 
                # FIXME: make popup come where cursor is
                #rectangle = treeview.get_visible_rect()
                #column = treeview.get_column(0)
                #rectangle = treeview.get_cell_area("0:0", 
                #x, y = rectangle.x, rectangle.y
                #func = lambda menu: (x, y, True)
        elif event.button == 3:
            button_code = 3
            event_time = event.time
            x = int(event.x)
            y = int(event.y)
            path_info = treeview.get_path_at_pos(x, y)
            func = None
            if path_info is not None:
                path, col, cellx, celly = path_info
                selection = treeview.get_selection()
                store, paths = selection.get_selected_rows()
                tpath = paths[0] if len(paths) > 0 else None
                node = store.get_iter(tpath) if tpath else None
                if path:
                    treeview.grab_focus()
                    treeview.set_cursor(path, col, 0)
                if store and node:
                    index = store.get_value(node, 0) # index Below,
        # you need index, treeview, path, button_code,
        # func, and event_time
        if index is not None:
            popup = gtk.Menu()
            if (index is not None and self.__link[index]):
            # See details (edit, etc):
                objclass, handle = self.__link[index]
                menu_item = gtk.MenuItem(_("the object|See %s details") % trans_objclass(objclass))
                menu_item.connect("activate", 
                  lambda widget: self.on_table_doubleclick(treeview))
                popup.append(menu_item)
                menu_item.show()
            # Add other items to menu:
            if (self._callback_leftclick or 
                (index is not None and self.__link[index])):
                objclass, handle = self.__link[index]
                if objclass == 'Person':
                    menu_item = gtk.MenuItem(_("the object|Make %s active") % trans_objclass('Person'))
                    menu_item.connect("activate", 
                      lambda widget: self.on_table_click(treeview))
                    popup.append(menu_item)
                    menu_item.show()
            if (self.simpledoc.doc.dbstate.db != 
                self.simpledoc.doc.dbstate.db.basedb and
                (index is not None and self.__link[index])):
                objclass, handle = self.__link[index]
                if (objclass == 'Filter' and 
                    handle[0] in ['Person', 'Family', 'Place', 'Event',
                                  'Repository', 'Note', 'MediaObject',
                                  'Citation', 'Source']):
                    menu_item = gtk.MenuItem(_("See data not in Filter"))
                    menu_item.connect("activate", 
                      lambda widget: self.show_not_in_filter(handle[0]))
                    popup.append(menu_item)
                    menu_item.show()
            # Show the popup menu:
            popup.popup(None, None, func, button_code, event_time)
            return True        
        return False

    def show_not_in_filter(self, obj_class):
        from QuickReports import run_quick_report_by_name
        run_quick_report_by_name(self.simpledoc.doc.dbstate,
                                 self.simpledoc.doc.uistate, 
                                 'filterbyname', 
                                 'Inverse %s' % obj_class)

    def on_table_doubleclick(self, obj):
        """
        Handle events on tables. obj is a treeview
        """
        from gui.editors import (EditPerson, EditEvent, EditFamily, EditCitation, EditSource,
                                 EditPlace, EditRepository, EditNote, EditMedia)
        selection = obj.get_selection()
        store, paths = selection.get_selected_rows()
        tpath = paths[0] if len(paths) > 0 else None
        node = store.get_iter(tpath) if tpath else None
        if not node:
            return
        index = store.get_value(node, 0) # index
        if self._callback_leftdouble:
            self._callback_leftdouble(store.get_value(node, 1))
            return True
        elif self.__link[index]:
            objclass, handle = self.__link[index]
            if isinstance(handle, list):
                handle = handle[0]
            if objclass == 'Person':
                person = self.access.dbase.get_person_from_handle(handle)
                if person:
                    try:
                        EditPerson(self.simpledoc.doc.dbstate, 
                                   self.simpledoc.doc.uistate, [], person)
                        return True # handled event
                    except Errors.WindowActiveError:
                        pass
            elif objclass == 'Event':
                event = self.access.dbase.get_event_from_handle(handle)
                if event:
                    try:
                        EditEvent(self.simpledoc.doc.dbstate, 
                                  self.simpledoc.doc.uistate, [], event)
                        return True # handled event
                    except Errors.WindowActiveError:
                        pass
            elif objclass == 'Family':
                ref = self.access.dbase.get_family_from_handle(handle)
                if ref:
                    try:
                        EditFamily(self.simpledoc.doc.dbstate, 
                                   self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except Errors.WindowActiveError:
                        pass
            elif objclass == 'Citation':
                ref = self.access.dbase.get_citation_from_handle(handle)
                if ref:
                    try:
                        EditCitation(self.simpledoc.doc.dbstate, 
                                     self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except Errors.WindowActiveError:
                        pass
            elif objclass == 'Source':
                ref = self.access.dbase.get_source_from_handle(handle)
                if ref:
                    try:
                        EditSource(self.simpledoc.doc.dbstate, 
                                   self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except Errors.WindowActiveError:
                        pass
            elif objclass == 'Place':
                ref = self.access.dbase.get_place_from_handle(handle)
                if ref:
                    try:
                        EditPlace(self.simpledoc.doc.dbstate, 
                                   self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except Errors.WindowActiveError:
                        pass
            elif objclass == 'Repository':
                ref = self.access.dbase.get_repository_from_handle(handle)
                if ref:
                    try:
                        EditRepository(self.simpledoc.doc.dbstate, 
                                   self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except Errors.WindowActiveError:
                        pass
            elif objclass == 'Note':
                ref = self.access.dbase.get_note_from_handle(handle)
                if ref:
                    try:
                        EditNote(self.simpledoc.doc.dbstate, 
                                 self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except Errors.WindowActiveError:
                        pass
            elif objclass in ['Media', 'MediaObject']:
                ref = self.access.dbase.get_object_from_handle(handle)
                if ref:
                    try:
                        EditMedia(self.simpledoc.doc.dbstate, 
                                  self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except Errors.WindowActiveError:
                        pass
            elif objclass == 'PersonList':
                from QuickReports import run_quick_report_by_name
                run_quick_report_by_name(self.simpledoc.doc.dbstate,
                                         self.simpledoc.doc.uistate, 
                                         'filterbyname', 
                                         'list of people',
                                         handles=handle)
            elif objclass == 'Filter':
                from QuickReports import run_quick_report_by_name
                if isinstance(handle, list):
                    handle = handle[0]
                run_quick_report_by_name(self.simpledoc.doc.dbstate,
                                         self.simpledoc.doc.uistate, 
                                         'filterbyname', 
                                         handle)
        return False # didn't handle event

    def on_table_click(self, obj):
        """
        Handle events on tables. obj is a treeview
        """
        selection = obj.get_selection()
        store, paths = selection.get_selected_rows()
        tpath = paths[0] if len(paths) > 0 else None
        node = store.get_iter(tpath)
        if not node:
            return
        index = store.get_value(node, 0) # index
        if self._callback_leftclick:
            self._callback_leftclick(store.get_value(node, 1))
            return True
        elif self.__link[index]:
            objclass, handle = self.__link[index]
            if isinstance(handle, list):
                handle = handle[0]
            if objclass == 'Person':
                import gobject
                # If you emmit the signal here and it causes this table to be deleted, 
                # then you'll crash Python:
                #self.simpledoc.doc.uistate.set_active(handle, 'Person')
                # So, let's return from this, then change the active person:
                return gobject.timeout_add(100, self.simpledoc.doc.uistate.set_active, handle, 'Person')
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
        col is either a number (column) or a (object_type_name, handle).
        """
        self.__link_col = col

    def row(self, *data):
        """
        Add a row of data.
        """
        retval = [] 
        link   = None
        row = len(self.__rows)
        self.__raw_data.append([])
        for col in range(len(data)):
            item = data[col]
            self.__raw_data[-1].append(item)
            # FIXME: add better text representations of these objects
            if item is None:
                retval.append("")
            elif isinstance(item, basestring):
                if item == "checkbox": 
                    retval.append("")
                    self.set_cell_type(col, "checkbox")
                else:
                    retval.append(item)
            elif isinstance(item, (int, float, long)):
                retval.append(item)
                self.row_sort_val(col, item)
            elif isinstance(item, gen.lib.Person):
                retval.append(self.access.describe(item))
                if (self.__link_col == col or link is None):
                    link = ('Person', item.handle)
            elif isinstance(item, gen.lib.Family): 
                retval.append(self.access.describe(item))
                if (self.__link_col == col or link is None):
                    link = ('Family', item.handle)
            elif isinstance(item, gen.lib.Citation): 
                retval.append(self.access.describe(item))
                if (self.__link_col == col or link is None):
                    link = ('Citation', item.handle)
            elif isinstance(item, gen.lib.Source): 
                retval.append(self.access.describe(item))
                if (self.__link_col == col or link is None):
                    link = ('Source', item.handle)
            elif isinstance(item, gen.lib.Event):
                retval.append(self.access.describe(item))
                if (self.__link_col == col or link is None):
                    link = ('Event', item.handle)
            elif isinstance(item, gen.lib.MediaObject):
                retval.append(self.access.describe(item))
                if (self.__link_col == col or link is None):
                    link = ('Media', item.handle)
            elif isinstance(item, gen.lib.Place):
                retval.append(self.access.describe(item))
                if (self.__link_col == col or link is None):
                    link = ('Place', item.handle)
            elif isinstance(item, gen.lib.Repository):
                retval.append(self.access.describe(item))
                if (self.__link_col == col or link is None):
                    link = ('Repository', item.handle)
            elif isinstance(item, gen.lib.Note):
                retval.append(self.access.describe(item))
                if (self.__link_col == col or link is None):
                    link = ('Note', item.handle)
            elif isinstance(item, gen.lib.Date):
                text = gen.datehandler.displayer.display(item)
                retval.append(text)
                if item.get_valid():
                    if item.format:
                        self.set_cell_markup(col, row, 
                                             item.format % cgi.escape(text))
                    self.row_sort_val(col, item.sortval)
                else:
                    # sort before others:
                    self.row_sort_val(col, -1)
                    # give formatted version:
                    invalid_date_format = config.get('preferences.invalid-date-format')
                    self.set_cell_markup(col, row,
                                         invalid_date_format % cgi.escape(text))
                if (self.__link_col == col or link is None):
                    link = ('Date', item)
            elif isinstance(item, gen.lib.Span):
                text = str(item)
                retval.append(text)
                self.row_sort_val(col, item)
            elif isinstance(item, list): # [text, "PersonList", handle, ...]
                retval.append(item[0])
                link = (item[1], item[2:])
            else:
                retval.append(str(item))
        self.__link.append(link)
        self.__rows.append(retval)

    def sort(self, column_name, reverse=False):
        self.__sort_col = column_name
        self.__sort_reverse = reverse

    def __sort(self):
        idx = self.__columns.index(self.__sort_col)
        # FIXME: move raw_data with this
        if self.__sort_reverse:
            self.__rows.sort(lambda a, b: -cmp(a[idx],b[idx]))
        else:
            self.__rows.sort(lambda a, b: cmp(a[idx],b[idx]))

    def toggle(self, obj, path, col):
        """
        obj - column widget
        path - row
        col - column
        """
        self.treeview.get_model()[path][col] = not \
            self.treeview.get_model()[path][col]

    def write(self, document):
        self.simpledoc = document # simpledoc; simpledoc.doc = docgen object
        if self.simpledoc.doc.type == "standard":
            doc = self.simpledoc.doc
            columns = len(self.__columns)
            doc.start_table('simple', 'Table')
            doc._tbl.set_column_widths([100/columns] * columns)
            doc._tbl.set_columns(columns)
            if self.title:
                doc.start_row()
                doc.start_cell('TableHead', span=columns) 
                doc.start_paragraph('TableTitle')
                doc.write_text(_(self.title))
                doc.end_paragraph()
                doc.end_cell()
                doc.end_row()
            if self.__sort_col:
                self.__sort()
            doc.start_row()
            for col in self.__columns:
                doc.start_cell('TableHeaderCell', span=1) 
                doc.write_text(col, 'TableTitle')
                doc.end_cell()
            doc.end_row()
            index = 0
            for row in self.__rows:
                doc.start_row()
                for col in row:
                    doc.start_cell('TableDataCell', span=1) 
                    obj_type, handle = None, None
                    if isinstance(self.__link_col, tuple):
                        obj_type, handle = self.__link_col
                    elif isinstance(self.__link_col, list):
                        obj_type, handle = self.__link_col[index]
                    elif self.__link[index]:
                        obj_type, handle = self.__link[index]
                    if obj_type:
                        if obj_type.lower() == "url":
                            doc.start_link(handle)
                        else:
                            doc.start_link("/%s/%s" % 
                                           (obj_type.lower(), handle))
                    doc.write_text(col, 'Normal')
                    if obj_type:
                        doc.stop_link()
                    doc.end_cell()
                doc.end_row()
                index += 1
            doc.end_table()
            doc.start_paragraph("Normal")
            doc.end_paragraph()
        elif self.simpledoc.doc.type == "gtk":
            import gtk
            from gui.widgets.multitreeview import MultiTreeView
            from ScratchPad import ScratchPadListView, ACTION_COPY
            from DdTargets import DdTargets
            buffer = self.simpledoc.doc.buffer
            text_view = self.simpledoc.doc.text_view
            model_index = 1 # start after index
            if self.__sort_col:
                sort_index = self.__columns.index(self.__sort_col)
            else:
                sort_index = 0
            treeview = MultiTreeView()
            treeview.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                 [(DdTargets.HANDLE_LIST.drag_type, gtk.TARGET_SAME_WIDGET, 0)],
                                              gtk.gdk.ACTION_COPY)
            #treeview.enable_model_drag_dest(DdTargets.all_targets(),
            #                                gtk.gdk.ACTION_DEFAULT)            
            treeview.connect('drag_data_get', self.object_drag_data_get)
            treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
            #treeview.connect('row-activated', on_table_doubleclick, self)
            #treeview.connect('cursor-changed', on_table_click, self)
            treeview.connect('button-press-event', self.button_press_event)
            treeview.connect('select-cursor-row', self.button_press_event)
            renderer = gtk.CellRendererText()
            types = [int] # index
            cnt = 0
            sort_data = []
            sort_data_types = []
            for col in self.__columns:
                if self.get_cell_type(cnt) == "text":
                    types.append(str)
                    if self.get_cell_markup(cnt):
                        column = gtk.TreeViewColumn(col,renderer,markup=model_index)
                    else:
                        column = gtk.TreeViewColumn(col,renderer,text=model_index)
                elif self.get_cell_type(cnt) == "checkbox":
                    types.append(bool)
                    toggle_renderer = gtk.CellRendererToggle()
                    toggle_renderer.set_property('activatable', True)
                    toggle_renderer.connect("toggled", self.toggle, model_index)
                    column = gtk.TreeViewColumn(col, toggle_renderer)
                    column.add_attribute(toggle_renderer, "active", model_index)
                column.set_resizable(True)
                if self.__sort_vals[cnt] != []:
                    sort_data.append(self.__sort_vals[cnt])
                    column.set_sort_column_id(len(self.__columns) + 
                                              len(sort_data))
                    sort_data_types.append(int)
                else:
                    column.set_sort_column_id(model_index)
                treeview.append_column(column)
                self.model_index_of_column[col] = model_index
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
            treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
            iter = buffer.get_end_iter()
            anchor = buffer.create_child_anchor(iter)
            text_view.add_child_at_anchor(treeview, anchor)
            self.treeview= treeview
            count = 0
            for data in self.__rows:
                col = 0
                rowdata = []
                for cell in data:
                    rowdata.append(self.get_cell_markup(col, count, cell))
                    col += 1
                try:
                    model.append(row=([count] + list(rowdata) + [col[count] for col in sort_data]))
                except:
                    print "error in row %d: data: %s, sort data: %d" % (count, rowdata, len(sort_data[0]))
                count += 1
            text_view.show_all()
            self.simpledoc.paragraph("")
            self.simpledoc.paragraph("")

    def object_drag_data_get(self, widget, context, sel_data, info, time):
        tree_selection = widget.get_selection()
        model, paths = tree_selection.get_selected_rows()
        retval = []
        for path in paths:
            node = model.get_iter(path)
            index = model.get_value(node,0)
            if (index is not None and self.__link[index]):
                retval.append(self.__link[index])
        sel_data.set(sel_data.target, 8, pickle.dumps(retval))
        return True

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

    def get_cell_type(self, col):
        """
        See if a column has a type, else return "text" as default.
        """
        if col in self.__cell_type:
            return self.__cell_type[col]
        return "text"

    def set_cell_markup(self, x, y, data):
        """
        Set the cell at position [x][y] to a formatted string.
        """
        col_dict = self.__cell_markup.get(x, {})
        col_dict[y] = data
        self.__cell_markup[x] = col_dict

    def set_cell_type(self, col, value):
        """
        Set the cell type at position [x].
        """
        self.__cell_type[col] = value
