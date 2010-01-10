#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009       Nick Hall
# Copyright (C) 2009       Benny Malengier
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

"""
Provide the base classes for GRAMPS' DataView classes
"""

#----------------------------------------------------------------
#
# python modules
#
#----------------------------------------------------------------
import cPickle as pickle
import time
import logging

_LOG = logging.getLogger('.gui.listview')

#----------------------------------------------------------------
#
# gtk
#
#----------------------------------------------------------------
import gtk
import pango

#----------------------------------------------------------------
#
# GRAMPS 
#
#----------------------------------------------------------------
from gui.views.navigationview import NavigationView
import config
import TreeTips
import Errors
from Filters import SearchBar
from gui.utils import add_menuitem
import const
import Utils
from QuestionDialog import QuestionDialog, QuestionDialog2
from TransUtils import sgettext as _

#----------------------------------------------------------------
#
# Constants
#
#----------------------------------------------------------------

NAVIGATION_NONE   = -1
NAVIGATION_PERSON = 0

LISTFLAT = 0
LISTTREE = 1

#----------------------------------------------------------------
#
# ListView
#
#----------------------------------------------------------------
class ListView(NavigationView):

    ADD_MSG = ""
    EDIT_MSG = ""
    DEL_MSG = ""
    FILTER_TYPE = None  # Set in inheriting class
    QR_CATEGORY = -1

    def __init__(self, title, dbstate, uistate, columns, handle_col, 
                 make_model, signal_map, get_bookmarks, bm_type, nav_group,
                 multiple=False, filter_class=None, markup=False):

        NavigationView.__init__(self, title, dbstate, uistate, 
                              get_bookmarks, bm_type, nav_group)
        #default is listviews keep themself in sync with database
        self._dirty_on_change_inactive = False
        
        self.filter_class = filter_class
        self.renderer = gtk.CellRendererText()
        self.renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        self.sort_col = 0
        self.sort_order = gtk.SORT_ASCENDING
        self.columns = []
        self.colinfo = columns
        self.handle_col = handle_col
        self.make_model = make_model
        self.model = None
        self.signal_map = signal_map
        self.multiple_selection = multiple
        self.generic_filter = None
        self.markup_required = markup
        dbstate.connect('database-changed', self.change_db)

    def type_list(self):
        """
        set the listtype, this governs eg keybinding
        """
        return LISTFLAT

    ####################################################################
    # Build interface
    ####################################################################
    def build_widget(self):
        """
        Builds the interface and returns a gtk.Container type that
        contains the interface. This containter will be inserted into
        a gtk.Notebook page.
        """
        self.vbox = gtk.VBox()
        self.vbox.set_border_width(4)
        self.vbox.set_spacing(4)
        
        self.search_bar = SearchBar(self.dbstate, self.uistate, 
                                    self.search_build_tree)
        filter_box = self.search_bar.build()

        self.list = gtk.TreeView()
        self.list.set_rules_hint(True)
        self.list.set_headers_visible(True)
        self.list.set_headers_clickable(True)
        self.list.set_fixed_height_mode(True)
        self.list.connect('button-press-event', self._button_press)
        if self.type_list() == LISTFLAT:
            # Flat list
            self.list.connect('key-press-event', self._key_press)
        else:
            # Tree
            self.list.connect('key-press-event', self._key_press_tree)
        if self.drag_info():
            self.list.connect('drag_data_get', self.drag_data_get)
            self.list.connect('drag_begin', self.drag_begin)

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrollwindow.add(self.list)

        self.vbox.pack_start(filter_box, False)
        self.vbox.pack_start(scrollwindow, True)

        self.renderer = gtk.CellRendererText()
        self.renderer.set_property('ellipsize', pango.ELLIPSIZE_END)

        self.columns = []
        self.build_columns()
        self.selection = self.list.get_selection()
        if self.multiple_selection:
            self.selection.set_mode(gtk.SELECTION_MULTIPLE)
        self.selection.connect('changed', self.row_changed)

        self.setup_filter()

        if self.filter_class:
            return self.build_filter_container(self.vbox, self.filter_class)
        else:
            return self.vbox

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. We extend beyond the normal here, 
        since we want to have more than one action group for the PersonView.
        Most PageViews really won't care about this.
        """
        
        NavigationView.define_actions(self)

        self.edit_action = gtk.ActionGroup(self.title + '/ChangeOrder')
        self.edit_action.add_actions([
                ('Add', gtk.STOCK_ADD, _("_Add..."), "<control>Insert", 
                    self.ADD_MSG, self.add), 
                ('Remove', gtk.STOCK_REMOVE, _("_Remove"), "<control>Delete", 
                    self.DEL_MSG, self.remove), 
                ('ExportTab', None, _('Export View...'), None, None,
                    self.export), 
                ])

        self._add_action_group(self.edit_action)

        self._add_action('Edit', gtk.STOCK_EDIT, _("action|_Edit..."), 
                         accel="<control>Return", 
                         tip=self.EDIT_MSG, 
                         callback=self.edit)
        
        self._add_toggle_action('Filter', None, _('_Filter'), 
                                callback=self.filter_toggle_action)

    def build_columns(self):
        for column in self.columns:
            self.list.remove_column(column)
            
        self.columns = []

        index = 0
        for pair in self.column_order():
            if not pair[0]: continue
            name = self.colinfo[pair[1]]

            column = gtk.TreeViewColumn(name, self.renderer)
            
            if self.model and self.model.marker_column() is not None:
                mcol = self.model.marker_column()
                column.add_attribute(self.renderer, 'foreground', mcol)

            if self.markup_required and pair[1] != 0:
                column.add_attribute(self.renderer, 'markup', pair[1])
            else:
                column.add_attribute(self.renderer, 'text', pair[1])

            column.connect('clicked', self.column_clicked, index)
            column.set_resizable(True)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_fixed_width(pair[2])
            column.set_clickable(True)
            self.columns.append(column)
            self.list.append_column(column)
            index += 1

    def set_active(self):
        NavigationView.set_active(self)
        self.uistate.show_filter_results(self.dbstate, 
                                         self.model.displayed(), 
                                         self.model.total())

    def __build_tree(self):
        Utils.profile(self._build_tree)

    def build_tree(self):
        if self.active:
            cput0 = time.clock()
            if config.get('interface.filter'):
                filter_info = (True, self.generic_filter, False)
            else:
                value = self.search_bar.get_value()
                filter_info = (False, value, value[0] in self.exact_search())

            if self.dirty or not self.model:
                self.model = self.make_model(self.dbstate.db, self.sort_col, 
                                             search=filter_info,
                                             sort_map=self.column_order())
            else:
                #the entire data to show is already in memory.
                #run only the part that determines what to show
                self.list.set_model(None)
                self.model.set_search(filter_info)
                self.model.rebuild_data()
            
            cput1 = time.clock()
            self.build_columns()
            cput2 = time.clock()
            self.list.set_model(self.model)
            cput3 = time.clock()
            self.__display_column_sort()
            self.goto_active(None)

            if const.USE_TIPS and self.model.tooltip_column is not None:
                self.tooltips = TreeTips.TreeTips(
                    self.list, self.model.tooltip_column, True)
            self.dirty = False
            cput4 = time.clock()
            self.uistate.show_filter_results(self.dbstate, 
                                             self.model.displayed(), 
                                             self.model.total())
            _LOG.debug(self.__class__.__name__ + ' build_tree ' +
                    str(time.clock() - cput0) + ' sec')
            _LOG.debug('parts ' + str(cput1-cput0) + ' , ' 
                             + str(cput2-cput1) + ' , ' 
                             + str(cput3-cput2) + ' , ' 
                             + str(cput4-cput3) + ' , ' 
                             + str(time.clock() - cput4))
            
        else:
            self.dirty = True

    def search_build_tree(self):
        self.build_tree()

    def exact_search(self):
        """
        Returns a tuple indicating columns requiring an exact search
        """
        return ()

    ####################################################################
    # Filter
    ####################################################################
    def build_filter_container(self, box, filter_class):
        self.filter_sidebar = filter_class(self.dbstate, self.uistate, 
                                           self.filter_clicked)
        self.filter_pane = self.filter_sidebar.get_widget()

        hpaned = gtk.HBox()
        hpaned.pack_start(self.vbox, True, True)
        hpaned.pack_end(self.filter_pane, False, False)
        self.filter_toggle(None, None, None, None)
        return hpaned

    def filter_toggle(self, client, cnxn_id, entry, data):
        if config.get('interface.filter'):
            self.search_bar.hide()
            self.filter_pane.show()
        else:
            self.search_bar.show()
            self.filter_pane.hide()

    def post(self):
        if self.filter_class:
            if config.get('interface.filter'):
                self.search_bar.hide()
                self.filter_pane.show()
            else:
                self.search_bar.show()
                self.filter_pane.hide()

    def get_viewtype_stock(self):
        """Type of view in category, default listview is a flat list
        """
        return 'gramps-tree-list'

    def filter_clicked(self):
        self.generic_filter = self.filter_sidebar.get_filter()
        self.build_tree()
        
    def filter_toggle_action(self, obj):
        if obj.get_active():
            self.search_bar.hide()
            self.filter_pane.show()
            active = True
        else:
            self.search_bar.show()
            self.filter_pane.hide()
            active = False
        config.set('interface.filter', active)
        self.build_tree()

    def filter_editor(self, obj):
        from FilterEditor import FilterEditor

        try:
            FilterEditor(self.FILTER_TYPE , const.CUSTOM_FILTERS, 
                         self.dbstate, self.uistate)
        except Errors.WindowActiveError:
            return

    def setup_filter(self):
        """Build the default filters and add them to the filter menu."""
        self.search_bar.setup_filter(
            [(self.colinfo[pair[1]], pair[1])
                for pair in self.column_order() if pair[0]])

    ####################################################################
    # Navigation
    ####################################################################
    def goto_handle(self, handle):
        """
        Go to a given handle in the list.
        Required by the NavigationView interface.
        
        We have a bit of a problem due to the nature of how GTK works.
        We have to unselect the previous path and select the new path. However, 
        these cause a row change, which calls the row_change callback, which
        can end up calling change_active_person, which can call
        goto_active_person, causing a bit of recusion. Confusing, huh?

        Unfortunately, row_change has to be able to call change_active_person, 
        because this can occur from the interface in addition to programatically.

        To handle this, we set the self.inactive variable that we can check
        in row_change to look for this particular condition.
        """
        if not handle or handle in self.selected_handles():
            return

        if self.type_list() == LISTFLAT:
            # Flat
            try:
                path = self.model.on_get_path(handle)
            except:
                path = None
        else:
            # Tree
            path = None
            node = self.model.get_node(handle)
            if node:
                parent_node = self.model.on_iter_parent(node)
                if parent_node:
                    parent_path = self.model.on_get_path(parent_node)
                    if parent_path:
                        self.list.expand_row(parent_path, False)
                path = self.model.on_get_path(node)

        if path:
            self.selection.unselect_all()
            self.selection.select_path(path)
            self.list.scroll_to_cell(path, None, 1, 0.5, 0)
        else:
            self.selection.unselect_all()
            self.uistate.push_message(self.dbstate, 
                                      _("Active object not visible"))

    def add_bookmark(self, obj):
        mlist = []
        self.selection.selected_foreach(self.blist, mlist)

        if mlist:
            self.bookmarks.add(mlist[0])
        else:
            from QuestionDialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"), 
                _("A bookmark could not be set because "
                  "nothing was selected."))

    ####################################################################
    # 
    ####################################################################

    def drag_info(self):
        return None

    def drag_list_info(self):
        return None

    def drag_begin(self, widget, context):
        widget.drag_source_set_icon_stock(self.get_stock())
        return True
        
    def drag_data_get(self, widget, context, sel_data, info, time):
        selected_ids = self.selected_handles()

        if selected_ids:
            data = (self.drag_info().drag_type, id(self), selected_ids[0], 0)
            sel_data.set(sel_data.target, 8 , pickle.dumps(data))
        return True

    def set_column_order(self, clist):
        """
        change the order of the columns to that given in clist
        """
        self.column_ord_setfunc(clist)
        #now we need to rebuild the model so it contains correct column info
        self.dirty = True
        #make sure we sort on first column. We have no idea where the 
        # column that was sorted on before is situated now. 
        self.sort_col = 0
        self.sort_order = gtk.SORT_ASCENDING
        self.setup_filter()
        self.build_tree()

    def column_order(self):
        """
        Must be set by children. The method that obtains the column order
        to be used. Format: see ColumnOrder.
        """
        raise NotImplementedError

    def column_ord_setfunc(self, clist):
        """
        Must be set by children. The method that stores the column order
        given by clist (result of ColumnOrder class).
        """
        raise NotImplementedError

    def _column_editor(self, obj):
        """
        Causes the View to display a column editor. This should be overridden
        by any class that provides columns (such as a list based view)
        """
        raise NotImplemented
        
    def remove_selected_objects(self):
        """
        Function to remove selected objects
        """
        prompt = True
        if len(self.selected_handles()) > 1:
            q = QuestionDialog2(
                _("Remove selected items?"),
                _("More than one item has been selected for deletion. "
                  "Ask before deleting each one?"),
                _("Yes"),
                _("No"))
            prompt = q.run()
            
        if not prompt:
            self.uistate.set_busy_cursor(1)

        for handle in self.selected_handles():
            (query, is_used, object) = self.remove_object_from_handle(handle)
            if prompt:
                if is_used:
                    msg = _('This item is currently being used. '
                            'Deleting it will remove it from the database and '
                            'from all other items that reference it.')
                else:
                    msg = _('Deleting item will remove it from the database.')
                
                msg += ' ' + Utils.data_recover_msg
                #descr = object.get_description()
                #if descr == "":
                descr = object.get_gramps_id()
                self.uistate.set_busy_cursor(1)
                QuestionDialog(_('Delete %s?') % descr, msg,
                               _('_Delete Item'), query.query_response)
                self.uistate.set_busy_cursor(0)
            else:
                query.query_response()

        if not prompt:
            self.uistate.set_busy_cursor(0)
        
    def blist(self, store, path, node, sel_list):
        if store.get_flags() & gtk.TREE_MODEL_LIST_ONLY:
            handle = store.get_value(node, self.handle_col)
        else:
            handle = store.get_handle(store.on_get_iter(path))

        if handle is not None:
            sel_list.append(handle)

    def selected_handles(self):
        mlist = []
        if self.selection:
            self.selection.selected_foreach(self.blist, mlist)
        return mlist

    def first_selected(self):
        mlist = []
        self.selection.selected_foreach(self.blist, mlist)
        if mlist:
            return mlist[0]
        else:
            return None

    ####################################################################
    # Signal handlers
    ####################################################################
    def column_clicked(self, obj, data):
        """
        Called when a column is clicked.

        obj     A TreeViewColumn object of the column clicked
        data    The column index
        """
        self.uistate.set_busy_cursor(1)
        self.uistate.push_message(self.dbstate, _("Column clicked, sorting..."))
        cput = time.clock()
        same_col = False
        if self.sort_col != data:
            order = gtk.SORT_ASCENDING
        else:
            same_col = True
            if (self.columns[data].get_sort_order() == gtk.SORT_DESCENDING
                or not self.columns[data].get_sort_indicator()):
                order = gtk.SORT_ASCENDING
            else:
                order = gtk.SORT_DESCENDING

        self.sort_col = data
        self.sort_order = order
        handle = self.first_selected()

        if config.get('interface.filter'):
            filter_info = (True, self.generic_filter, False)
        else:
            value = self.search_bar.get_value()
            if value[0] in self.exact_search():
                filter_info = (False, value, True)
            else:
                filter_info = (False, value, False)

        if same_col:
            self.list.set_model(None)
            self.model.reverse_order()
        else:
            self.model = self.make_model(self.dbstate.db, self.sort_col, 
                                         self.sort_order, 
                                         search=filter_info, 
                                         sort_map=self.column_order())
        
        self.list.set_model(self.model)
        self.__display_column_sort()

        if handle:
            self.goto_handle(handle)

        # set the search column to be the sorted column
        search_col = self.column_order()[data][1]
        self.list.set_search_column(search_col)
        
        self.uistate.set_busy_cursor(0)
        
        _LOG.debug('   ' + self.__class__.__name__ + ' column_clicked ' +
                    str(time.clock() - cput) + ' sec')

    def __display_column_sort(self):
        for i in xrange(len(self.columns)):
            enable_sort_flag = (i==self.sort_col)
            self.columns[i].set_sort_indicator(enable_sort_flag)
        self.columns[self.sort_col].set_sort_order(self.sort_order)

    def change_db(self, db):
        """
        Called when the database is changed.
        """
        self._change_db(db)
        for sig in self.signal_map:
            self.callman.add_db_signal(sig, self.signal_map[sig])

        self.bookmarks.update_bookmarks(self.get_bookmarks())
        if self.active:
            #force rebuild of the model on build of tree
            self.dirty = True
            self.build_tree()
            self.bookmarks.redraw()
        else:
            self.dirty = True

    def row_changed(self, selection):
        """
        Called with a list selection is changed.

        Check the selected objects in the list and return those that have
        handles attached.  Set the active object to the first item in the
        list. If no row is selected, set the active object to None.
        """
        selected_ids = self.selected_handles()
        if len(selected_ids) > 0:
            self.change_active(selected_ids[0])

        if len(selected_ids) == 1:
            if self.drag_info():
                self.list.drag_source_set(gtk.gdk.BUTTON1_MASK, 
                                      [self.drag_info().target()], 
                                      gtk.gdk.ACTION_COPY)
        elif len(selected_ids) > 1:
            if self.drag_list_info():
                self.list.drag_source_set(gtk.gdk.BUTTON1_MASK, 
                                      [self.drag_list_info().target()], 
                                      gtk.gdk.ACTION_COPY)

        self.uistate.modify_statusbar(self.dbstate)

    def row_add(self, handle_list):
        """
        Called when an object is added.
        """
        if self.active or \
           (not self.dirty and not self._dirty_on_change_inactive):
            cput = time.clock()
            for handle in handle_list:
                self.model.add_row_by_handle(handle)
            _LOG.debug('   ' + self.__class__.__name__ + ' row_add ' +
                    str(time.clock() - cput) + ' sec')
            if self.active:
                self.uistate.show_filter_results(self.dbstate, 
                                                 self.model.displayed(), 
                                                 self.model.total())
        else:
            self.dirty = True

    def row_update(self, handle_list):
        """
        Called when an object is updated.
        """
        if self.model:
            self.model.prev_handle = None
        if self.active or \
           (not self.dirty and not self._dirty_on_change_inactive):
            cput = time.clock()
            for handle in handle_list:
                self.model.update_row_by_handle(handle)
            _LOG.debug('   ' + self.__class__.__name__ + ' row_update ' +
                    str(time.clock() - cput) + ' sec')
            # Ensure row is still selected after a change of postion in tree.
            if not self.selected_handles():
                self.goto_handle(handle)
        else:
            self.dirty = True

    def row_delete(self, handle_list):
        """
        Called when an object is deleted.
        """
        if self.active or \
           (not self.dirty and not self._dirty_on_change_inactive):
            cput = time.clock()
            map(self.model.delete_row_by_handle, handle_list)
            _LOG.debug('   '  + self.__class__.__name__ + ' row_delete ' +
                    str(time.clock() - cput) + ' sec')
            if self.active:
                self.uistate.show_filter_results(self.dbstate, 
                                                 self.model.displayed(), 
                                                 self.model.total())
        else:
            self.dirty = True

    def object_build(self):
        """
        Called when the tree must be rebuilt and bookmarks redrawn.
        """
        self.dirty = True
        if self.active:
            self.bookmarks.redraw()
            self.build_tree()

    def _button_press(self, obj, event):
        """
        Called when a mouse is clicked.
        """
        if not self.dbstate.open:
            return False
        from QuickReports import create_quickreport_menu
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            if self.type_list() == LISTFLAT:
                self.edit(obj)
                return True
            else:
                # Tree
                store, paths = self.selection.get_selected_rows()
                if paths:
                    firstsel = paths[0]
                    firstnode = self.model.on_get_iter(firstsel)
                    if len(paths)==1 and firstnode.handle is None:
                        return self.expand_collapse_tree_branch()
                    else:
                        self.edit(obj)
                        return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu = self.uistate.uimanager.get_widget('/Popup')
            #construct quick reports if needed
            if menu and self.QR_CATEGORY > -1 :
                qr_menu = self.uistate.uimanager.\
                            get_widget('/Popup/QuickReport').get_submenu()
                if qr_menu :
                    self.uistate.uimanager.\
                            get_widget('/Popup/QuickReport').remove_submenu()
                reportactions = []
                if menu and self.get_active():
                    (ui, reportactions) = create_quickreport_menu(
                                            self.QR_CATEGORY, 
                                            self.dbstate, 
                                            self.uistate,
                                            self.first_selected())
                if len(reportactions) > 1 :
                    qr_menu = gtk.Menu()
                    for action in reportactions[1:] :
                        add_menuitem(qr_menu, action[2], None, action[5])
                    self.uistate.uimanager.get_widget('/Popup/QuickReport').\
                            set_submenu(qr_menu)
            if menu:
                menu.popup(None, None, None, event.button, event.time)
                return True
            
        return False
    
    def _key_press(self, obj, event):
        """
        Called when a key is pressed on a flat listview
        ENTER --> edit selection
        """
        if not self.dbstate.open:
            return False
        if not event.state or event.state in (gtk.gdk.MOD2_MASK, ):
            if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
                self.edit(obj)
                return True
        return False

    def _key_press_tree(self, obj, event):
        """
        Called when a key is pressed on a tree listview
        ENTER --> edit selection or open group node
        SHIFT+ENTER --> open group node and all children nodes
        """
        if not self.dbstate.open:
            return False
        if not event.state or event.state  in (gtk.gdk.MOD2_MASK, ):
            if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
                store, paths = self.selection.get_selected_rows()
                if paths:
                    firstsel = paths[0]
                    firstnode = self.model.on_get_iter(firstsel)
                    if len(paths)==1 and firstnode.handle is None:
                        return self.expand_collapse_tree()
                    else:
                        self.edit(obj)
                        return True
        elif event.state in (gtk.gdk.SHIFT_MASK, ):
            if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
                store, paths = self.selection.get_selected_rows()
                if paths:
                    firstsel = paths[0]
                    firstnode = self.model.on_get_iter(firstsel)
                    if len(paths)==1 and firstnode.handle is None:
                        return self.expand_collapse_tree_branch()
            
        return False

    def expand_collapse_tree(self):
        """
        Expand or collapse the selected group node.
        Return True if change done, False otherwise
        """
        store, paths = self.selection.get_selected_rows()
        if paths:
            firstsel = paths[0]
            firstnode = self.model.on_get_iter(firstsel)
            if firstnode.handle:
                return False
            if self.list.row_expanded(firstsel):
                self.list.collapse_row(firstsel)
            else:
                self.list.expand_row(firstsel, False)
            return True
        return False

    def expand_collapse_tree_branch(self):
        """
        Expand or collapse the selected group node with all children.
        Return True if change done, False otherwise
        """
        store, paths = self.selection.get_selected_rows()
        if paths:
            firstsel = paths[0]
            firstnode = self.model.on_get_iter(firstsel)
            if firstnode.handle:
                return False
            if self.list.row_expanded(firstsel):
                self.list.collapse_row(firstsel)
            else:
                self.open_branch(None)
            return True
        return False

    def key_delete(self):
        self.remove(None)

    def change_page(self):
        """
        Called when a page is changed.
        """
        NavigationView.change_page(self)
        if self.model:
            self.uistate.show_filter_results(self.dbstate, 
                                             self.model.displayed(), 
                                             self.model.total())
        self.edit_action.set_visible(True)
        self.edit_action.set_sensitive(not self.dbstate.db.readonly)

    ####################################################################
    # Export data
    ####################################################################
    def export(self, obj):
        chooser = gtk.FileChooserDialog(
            _("Export View as Spreadsheet"), 
            self.uistate.window, 
            gtk.FILE_CHOOSER_ACTION_SAVE, 
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
             gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        chooser.set_do_overwrite_confirmation(True)

        combobox = gtk.combo_box_new_text()
        label = gtk.Label(_("Format:"))
        label.set_alignment(1.0, 0.5)
        box = gtk.HBox()
        box.pack_start(label, True, True, padding=12)
        box.pack_start(combobox, False, False)
        combobox.append_text(_('CSV'))
        combobox.append_text(_('OpenDocument Spreadsheet'))
        combobox.set_active(0)
        box.show_all()
        chooser.set_extra_widget(box)

        while True:
            value = chooser.run()
            fn = chooser.get_filename()
            fl = combobox.get_active()
            if value == gtk.RESPONSE_OK:
                if fn:
                    chooser.destroy()
                    break
            else:
                chooser.destroy()
                return
        self.write_tabbed_file(fn, fl)

    def write_tabbed_file(self, name, type):
        """
        Write a tabbed file to the specified name. 
        
        The output file type is determined by the type variable.
        """
        from docgen import CSVTab, ODSTab
        ofile = None
        data_cols = [pair[1] for pair in self.column_order() if pair[0]]

        column_names = [self.colinfo[i] for i in data_cols]
        if type == 0:
            ofile = CSVTab(len(column_names))                        
        else:
            ofile = ODSTab(len(column_names))
        
        ofile.open(name)
        ofile.start_page()
        ofile.start_row()

        # Headings
        if self.model.get_flags() & gtk.TREE_MODEL_LIST_ONLY:
            headings = column_names
        else:
            levels = self.model.get_tree_levels()
            headings = levels + column_names[1:]
            data_cols = data_cols[1:]

        map(ofile.write_cell, headings)
        ofile.end_row()

        if self.model.get_flags() & gtk.TREE_MODEL_LIST_ONLY:
            # Flat model
            for row in self.model:
                ofile.start_row()
                for index in data_cols:
                    ofile.write_cell(row[index])
                ofile.end_row()
        else:
            # Tree model
            node = self.model.on_get_iter((0,))
            self.write_node(node, len(levels), [], ofile, data_cols)
        
        ofile.end_page()
        ofile.close()
        
    def write_node(self, node, depth, level, ofile, data_cols):
        if node is None:
            return
        while node is not None:
            new_level = level + [self.model.on_get_value(node, 0)]
            if self.model.get_handle(node):
                ofile.start_row()
                padded_level = new_level + [''] * (depth - len(new_level))
                map(ofile.write_cell, padded_level)
                for index in data_cols:
                    ofile.write_cell(self.model.on_get_value(node, index))
                ofile.end_row()

            first_child = self.model.on_iter_children(node)
            self.write_node(first_child, depth, new_level, ofile, data_cols)
            node = self.model.on_iter_next(node)

    ####################################################################
    # Template functions
    ####################################################################
    def get_bookmarks(self):
        """
        Template function to get bookmarks.
        We could implement this in the NavigationView
        """
        raise NotImplementedError
        
    def edit(self, obj):
        """
        Template function to allow the editing of the selected object
        """
        raise NotImplementedError

    def remove(self, handle):
        """
        Template function to allow the removal of an object by its handle
        """
        raise NotImplementedError

    def add(self, obj):
        """
        Template function to allow the adding of a new object
        """
        raise NotImplementedError

    def remove_object_from_handle(self, handle):
        """
        Template function to allow the removal of an object by its handle
        """
        raise NotImplementedError

    def open_all_nodes(self, obj):
        """
        Method for Treeviews to open all groups
        obj: for use of method in event callback 
        """
        self.uistate.status_text(_("Updating display..."))
        self.uistate.set_busy_cursor(True)

        self.list.expand_all()

        self.uistate.set_busy_cursor(False)
        self.uistate.modify_statusbar(self.dbstate)

    def close_all_nodes(self, obj):
        """
        Method for Treeviews to close all groups
        obj: for use of method in event callback
        """
        self.list.collapse_all()

    def open_branch(self, obj):
        """
        Expand the selected branches and all children.
        obj: for use of method in event callback
        """
        self.uistate.status_text(_("Updating display..."))
        self.uistate.set_busy_cursor(True)
        
        selected = self.selection.get_selected_rows()
        for path in selected[1]:
            self.list.expand_row(path, True)

        self.uistate.set_busy_cursor(False)
        self.uistate.modify_statusbar(self.dbstate)
        
    def close_branch(self, obj):
        """
        Collapse the selected branches.
        obj: for use of method in event callback
        """
        selected = self.selection.get_selected_rows()
        for path in selected[1]:
            self.list.collapse_row(path)
