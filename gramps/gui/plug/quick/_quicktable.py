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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Provide a simplified table creation interface
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import pickle

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.simple import SimpleTable
from gramps.gen.errors import WindowActiveError
from ...utils import model_to_text, text_to_clipboard
from ...widgets.multitreeview import MultiTreeView
from ...ddtargets import DdTargets
from ..quick import run_quick_report_by_name
from ...editors import (EditPerson, EditEvent, EditFamily, EditCitation,
                         EditSource, EditPlace, EditRepository, EditNote,
                         EditMedia)

#-------------------------------------------------------------------------
#
# QuickTable class
#
#-------------------------------------------------------------------------
class QuickTable(SimpleTable):
    """
    Provide a simplified table creation interface.
    """
    def set_callback(self, which, callback):
        """
        Override (or add) a function for click/double-click
        """
        if which == "leftclick":
            self._callback_leftclick = callback
        elif which == "leftdouble":
            self._callback_leftdouble = callback

    def button_press_event(self, treeview, event):
        wid = treeview.get_toplevel()
        try:
            winmgr = self.simpledoc.doc.uistate.gwm
            self.track = winmgr.get_item_from_window(wid).track
        except:
            self.track = []
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
                    index = store.get_value(node, 0)  # index Below,
        # you need index, treeview, path, button_code,
        # func, and event_time
        if index is not None:
            if self._link[index]:
                objclass, handle = self._link[index]
            else:
                return False
            if (self.simpledoc.doc.uistate.get_export_mode() and
                    objclass != 'Filter'):
                return False  # avoid edition during export
            self.popup = Gtk.Menu()
            popup = self.popup
            menu_item = Gtk.MenuItem(label=_("Copy all"))
            menu_item.connect("activate", lambda widget: text_to_clipboard(
                              model_to_text(treeview.get_model())))
            popup.append(menu_item)
            menu_item.show()
            # Now add more items to popup menu, if available
            # See details (edit, etc):
            menu_item = Gtk.MenuItem(label=_("the object|See %s details") %
                                     glocale.trans_objclass(objclass))
            menu_item.connect(
                "activate", lambda widget: self.on_table_doubleclick(treeview))
            popup.append(menu_item)
            menu_item.show()
            # Add other items to menu:
            if objclass == 'Person':
                menu_item = Gtk.MenuItem(label=_("the object|Make %s active")
                                         % glocale.trans_objclass('Person'))
                menu_item.connect("activate",
                                  lambda widget: self.on_table_click(treeview))
                popup.append(menu_item)
                menu_item.show()
            if (self.simpledoc.doc.dbstate.db !=
                    self.simpledoc.doc.dbstate.db.basedb):
                if (objclass == 'Filter' and
                    handle[0] in ['Person', 'Family', 'Place', 'Event',
                                  'Repository', 'Note', 'Media',
                                  'Citation', 'Source']):
                    menu_item = Gtk.MenuItem(label=_("See data not in Filter"))
                    menu_item.connect(
                        "activate",
                        lambda widget: self.show_not_in_filter(handle[0]))
                    popup.append(menu_item)
                    menu_item.show()
            # Show the popup menu:
            popup.popup(None, None, func, None, button_code, event_time)
            return True
        return False

    def show_not_in_filter(self, obj_class):
        run_quick_report_by_name(self.simpledoc.doc.dbstate,
                                 self.simpledoc.doc.uistate,
                                 'filterbyname',
                                 'Inverse %s' % obj_class,
                                 track=self.track)

    def on_table_doubleclick(self, obj):
        """
        Handle events on tables. obj is a treeview
        """
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
        elif self._link[index]:
            objclass, handle = self._link[index]
            if isinstance(handle, list):
                handle = handle[0]
            if objclass == 'Person':
                person = self.access.dbase.get_person_from_handle(handle)
                if person:
                    try:
                        EditPerson(self.simpledoc.doc.dbstate,
                                   self.simpledoc.doc.uistate, [], person)
                        return True # handled event
                    except WindowActiveError:
                        pass
            elif objclass == 'Event':
                event = self.access.dbase.get_event_from_handle(handle)
                if event:
                    try:
                        EditEvent(self.simpledoc.doc.dbstate,
                                  self.simpledoc.doc.uistate, [], event)
                        return True # handled event
                    except WindowActiveError:
                        pass
            elif objclass == 'Family':
                ref = self.access.dbase.get_family_from_handle(handle)
                if ref:
                    try:
                        EditFamily(self.simpledoc.doc.dbstate,
                                   self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except WindowActiveError:
                        pass
            elif objclass == 'Citation':
                ref = self.access.dbase.get_citation_from_handle(handle)
                if ref:
                    try:
                        EditCitation(self.simpledoc.doc.dbstate,
                                     self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except WindowActiveError:
                        pass
            elif objclass == 'Source':
                ref = self.access.dbase.get_source_from_handle(handle)
                if ref:
                    try:
                        EditSource(self.simpledoc.doc.dbstate,
                                   self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except WindowActiveError:
                        pass
            elif objclass == 'Place':
                ref = self.access.dbase.get_place_from_handle(handle)
                if ref:
                    try:
                        EditPlace(self.simpledoc.doc.dbstate,
                                   self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except WindowActiveError:
                        pass
            elif objclass == 'Repository':
                ref = self.access.dbase.get_repository_from_handle(handle)
                if ref:
                    try:
                        EditRepository(self.simpledoc.doc.dbstate,
                                   self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except WindowActiveError:
                        pass
            elif objclass == 'Note':
                ref = self.access.dbase.get_note_from_handle(handle)
                if ref:
                    try:
                        EditNote(self.simpledoc.doc.dbstate,
                                 self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except WindowActiveError:
                        pass
            elif objclass == 'Media':
                ref = self.access.dbase.get_media_from_handle(handle)
                if ref:
                    try:
                        EditMedia(self.simpledoc.doc.dbstate,
                                  self.simpledoc.doc.uistate, [], ref)
                        return True # handled event
                    except WindowActiveError:
                        pass
            elif objclass == 'PersonList':
                run_quick_report_by_name(self.simpledoc.doc.dbstate,
                                         self.simpledoc.doc.uistate,
                                         'filterbyname',
                                         'list of people',
                                         handle=handle,
                                         track=self.track)
            elif objclass == 'Filter':
                if isinstance(handle, list):
                    handle = handle[0]
                run_quick_report_by_name(self.simpledoc.doc.dbstate,
                                         self.simpledoc.doc.uistate,
                                         'filterbyname',
                                         handle, track=self.track)
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
        elif self._link[index]:
            objclass, handle = self._link[index]
            if isinstance(handle, list):
                handle = handle[0]
            if objclass == 'Person':
                from gi.repository import GLib
                # If you emmit the signal here and it causes this table to be deleted,
                # then you'll crash Python:
                #self.simpledoc.doc.uistate.set_active(handle, 'Person')
                # So, let's return from this, then change the active person:
                return GLib.timeout_add(100, self.simpledoc.doc.uistate.set_active, handle, 'Person')
                return True
        return False # didn't handle event

    def object_drag_data_get(self, widget, context, sel_data, info, time):
        tree_selection = widget.get_selection()
        model, paths = tree_selection.get_selected_rows()
        retval = []
        for path in paths:
            node = model.get_iter(path)
            index = model.get_value(node,0)
            if (index is not None and self._link[index]):
                retval.append(self._link[index])
        sel_data.set(DdTargets.HANDLE_LIST.atom_drag_type, 8, pickle.dumps(retval))
        return True

    def toggle(self, obj, path, col):
        """
        obj - column widget
        path - row
        col - column
        """
        self.treeview.get_model()[path][col] = not \
            self.treeview.get_model()[path][col]

    def write(self, document):
        self.simpledoc = document
        buffer = self.simpledoc.doc.buffer
        text_view = self.simpledoc.doc.text_view
        text_view.set_sensitive(False)
        model_index = 1 # start after index
        if self._sort_col:
            sort_index = self._columns.index(self._sort_col)
        else:
            sort_index = 0
        treeview = MultiTreeView()
        treeview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
             [],
                                          Gdk.DragAction.COPY)
        tglist = Gtk.TargetList.new([])
        tglist.add(DdTargets.HANDLE_LIST.atom_drag_type, Gtk.TargetFlags.SAME_WIDGET,
                   0)
        treeview.drag_source_set_target_list(tglist)
        #treeview.enable_model_drag_dest(DdTargets.all_targets(),
        #                                Gdk.DragAction.DEFAULT)
        treeview.connect('drag_data_get', self.object_drag_data_get)
        treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        #treeview.connect('row-activated', on_table_doubleclick, self)
        #treeview.connect('cursor-changed', on_table_click, self)
        treeview.connect('button-press-event', self.button_press_event)
        treeview.connect('select-cursor-row', self.button_press_event)
        renderer = Gtk.CellRendererText()
        types = [int] # index
        cnt = 0
        sort_data = []
        sort_data_types = []
        for col in self._columns:
            if self.get_cell_type(cnt) == "text":
                types.append(str)
                if self.get_cell_markup(cnt):
                    column = Gtk.TreeViewColumn(col,renderer,markup=model_index)
                else:
                    column = Gtk.TreeViewColumn(col,renderer,text=model_index)
            elif self.get_cell_type(cnt) == "checkbox":
                types.append(bool)
                toggle_renderer = Gtk.CellRendererToggle()
                toggle_renderer.set_property('activatable', True)
                toggle_renderer.connect("toggled", self.toggle, model_index)
                column = Gtk.TreeViewColumn(col, toggle_renderer)
                column.add_attribute(toggle_renderer, "active", model_index)
            column.set_resizable(True)
            if self._sort_vals[cnt] != []:
                sort_data.append(self._sort_vals[cnt])
                column.set_sort_column_id(len(self._columns) +
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
        model = Gtk.ListStore(*types)
        treeview.set_model(model)
        treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        iter = buffer.get_end_iter()
        anchor = buffer.create_child_anchor(iter)
        text_view.add_child_at_anchor(treeview, anchor)
        self.treeview= treeview
        count = 0
        for data in self._rows:
            col = 0
            rowdata = []
            for cell in data:
                rowdata.append(self.get_cell_markup(col, count, cell))
                col += 1
            try:
                model.append(row=([count] + list(rowdata) + [col[count] for col in sort_data]))
            except KeyError as msg:
                print (msg)
                if sort_data:
                    print("Quicktable: error in row %d: data: %s, sort data: %d" % (count, rowdata, len(sort_data[0])))
                else:
                    print("Quicktable: error in row %d: data: %s" % (count, rowdata))
            count += 1
        text_view.show_all()
        self.simpledoc.paragraph("")
        self.simpledoc.paragraph("")
        while Gtk.events_pending():
            Gtk.main_iteration()
        text_view.set_sensitive(True)
