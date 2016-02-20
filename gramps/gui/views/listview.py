#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Nick Hall
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Provide the base classes for GRAMPS' DataView classes
"""

#----------------------------------------------------------------
#
# python modules
#
#----------------------------------------------------------------
import pickle
import time
import logging

LOG = logging.getLogger('.gui.listview')

#----------------------------------------------------------------
#
# gtk
#
#----------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango

#----------------------------------------------------------------
#
# Gramps
#
#----------------------------------------------------------------
from .pageview import PageView
from .navigationview import NavigationView
from ..actiongroup import ActionGroup
from ..columnorder import ColumnOrder
from gramps.gen.config import config
from gramps.gen.errors import WindowActiveError
from ..filters import SearchBar
from ..widgets.menuitem import add_menuitem
from gramps.gen.const import CUSTOM_FILTERS
from gramps.gen.utils.debug import profile
from gramps.gen.utils.string import data_recover_msg
from ..dialog import QuestionDialog, QuestionDialog2
from ..editors import FilterEditor
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from ..ddtargets import DdTargets
from ..plug.quick import create_quickreport_menu, create_web_connect_menu
from ..utils import is_right_click
from ..widgets.interactivesearchbox import InteractiveSearchBox

#----------------------------------------------------------------
#
# Constants
#
#----------------------------------------------------------------
TEXT = 1
MARKUP = 2
ICON = 3

#----------------------------------------------------------------
#
# ListView
#
#----------------------------------------------------------------
class ListView(NavigationView):
    COLUMNS = []
    #listview config settings that are always present related to the columns
    CONFIGSETTINGS = (
        ('columns.visible', []),
        ('columns.rank', []),
        ('columns.size', [])
        )
    ADD_MSG = ""
    EDIT_MSG = ""
    DEL_MSG = ""
    MERGE_MSG = ""
    FILTER_TYPE = None  # Set in inheriting class
    QR_CATEGORY = -1

    def __init__(self, title, pdata, dbstate, uistate,
                 make_model, signal_map, bm_type, nav_group,
                 multiple=False, filter_class=None):
        NavigationView.__init__(self, title, pdata, dbstate, uistate,
                                bm_type, nav_group)
        #default is listviews keep themself in sync with database
        self._dirty_on_change_inactive = False

        self.filter_class = filter_class
        self.pb_renderer = Gtk.CellRendererPixbuf()
        self.renderer = Gtk.CellRendererText()
        self.renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        self.sort_col = 0
        self.sort_order = Gtk.SortType.ASCENDING
        self.columns = []
        self.make_model = make_model
        self.model = None
        self.signal_map = signal_map
        self.multiple_selection = multiple
        self.generic_filter = None
        dbstate.connect('database-changed', self.change_db)
        self.connect_signals()

    def no_database(self):
        ## TODO GTK3: This is never called!! Dbguielement disconnects
        ## signals on database changed, so it cannot be called
        ## Undo part of Revision 20296 if all works good.
        self.list.set_model(None)
        self.model.destroy()
        self.model = None
        self.build_tree()

    ####################################################################
    # Build interface
    ####################################################################
    def build_widget(self):
        """
        Builds the interface and returns a Gtk.Container type that
        contains the interface. This containter will be inserted into
        a Gtk.Notebook page.
        """
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox.set_border_width(4)
        self.vbox.set_spacing(4)

        self.search_bar = SearchBar(self.dbstate, self.uistate,
                                    self.search_build_tree)
        filter_box = self.search_bar.build()

        self.list = Gtk.TreeView()
        self.list.set_headers_visible(True)
        self.list.set_headers_clickable(True)
        self.list.set_fixed_height_mode(True)
        self.list.connect('button-press-event', self._button_press)
        self.list.connect('key-press-event', self._key_press)
        self.list.connect('start-interactive-search',self.open_all_nodes)
        self.searchbox = InteractiveSearchBox(self.list)

        if self.drag_info():
            self.list.connect('drag_data_get', self.drag_data_get)
            self.list.connect('drag_begin', self.drag_begin)
        if self.drag_dest_info():
            self.list.connect('drag_data_received', self.drag_data_received)
            self.list.drag_dest_set(Gtk.DestDefaults.MOTION |
                                    Gtk.DestDefaults.DROP,
                                    [self.drag_dest_info().target()],
                                    Gdk.DragAction.MOVE |
                                    Gdk.DragAction.COPY)
            tglist = Gtk.TargetList.new([])
            tglist.add(self.drag_dest_info().atom_drag_type,
                       self.drag_dest_info().target_flags,
                       self.drag_dest_info().app_id)
            self.list.drag_dest_set_target_list(tglist)

        scrollwindow = Gtk.ScrolledWindow()
        scrollwindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                                Gtk.PolicyType.AUTOMATIC)
        scrollwindow.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrollwindow.add(self.list)

        self.vbox.pack_start(filter_box, False, True, 0)
        self.vbox.pack_start(scrollwindow, True, True, 0)

        self.renderer = Gtk.CellRendererText()
        self.renderer.set_property('ellipsize', Pango.EllipsizeMode.END)

        self.columns = []
        self.build_columns()
        self.selection = self.list.get_selection()
        if self.multiple_selection:
            self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.selection.connect('changed', self.row_changed)

        self.setup_filter()
        return self.vbox

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. We extend beyond the normal here,
        since we want to have more than one action group for the PersonView.
        Most PageViews really won't care about this.
        """

        NavigationView.define_actions(self)

        self.edit_action = ActionGroup(name=self.title + '/ChangeOrder')
        self.edit_action.add_actions([
                ('Add', 'list-add', _("_Add..."), "<PRIMARY>Insert",
                    self.ADD_MSG, self.add),
                ('Remove', 'list-remove', _("_Remove"), "<PRIMARY>Delete",
                    self.DEL_MSG, self.remove),
                ('Merge', 'gramps-merge', _('_Merge...'), None,
                    self.MERGE_MSG, self.merge),
                ('ExportTab', None, _('Export View...'), None, None,
                    self.export),
                ])

        self._add_action_group(self.edit_action)

        self._add_action('Edit', 'gtk-edit', _("action|_Edit..."),
                         accel="<PRIMARY>Return",
                         tip=self.EDIT_MSG,
                         callback=self.edit)

    def build_columns(self):
        list(map(self.list.remove_column, self.columns))

        self.columns = []

        index = 0
        for pair in self.column_order():
            if not pair[0]: continue
            col_name, col_type, col_icon = self.COLUMNS[pair[1]]

            if col_type == ICON:
                column = Gtk.TreeViewColumn(col_name, self.pb_renderer)
                column.set_cell_data_func(self.pb_renderer, self.icon, pair[1])
            else:
                column = Gtk.TreeViewColumn(col_name, self.renderer)
                if col_type == MARKUP:
                    column.add_attribute(self.renderer, 'markup', pair[1])
                else:
                    column.add_attribute(self.renderer, 'text', pair[1])

            if col_icon is not None:
                image = Gtk.Image()
                image.set_from_icon_name(col_icon, Gtk.IconSize.MENU)
                image.set_tooltip_text(col_name)
                image.show()
                column.set_widget(image)

            if self.model and self.model.color_column() is not None:
                column.set_cell_data_func(self.renderer, self.foreground_color)

            column.connect('clicked', self.column_clicked, index)

            column.set_resizable(True)
            column.set_clickable(True)
            column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            column.set_fixed_width(pair[2])

            self.columns.append(column)
            self.list.append_column(column)
            index += 1

    def icon(self, column, renderer, model, iter_, col_num):
        '''
        Set the icon-name property of the cell renderer.  We use a cell data
        function because there is a problem returning None from a model.
        '''
        icon_name = model.get_value(iter_, col_num)
        if icon_name == '':
            icon_name = None
        renderer.set_property('icon-name', icon_name)

    def foreground_color(self, column, renderer, model, iter_, data=None):
        '''
        Set the foreground color of the cell renderer.  We use a cell data
        function because we don't want to set the color of untagged rows.
        '''
        fg_color = model.get_value(iter_, model.color_column())
        #for color errors, typically color column is badly set
        if fg_color:
            renderer.set_property('foreground', fg_color)
        else:
            LOG.debug('Bad color set: ' + str(fg_color))

    def set_active(self):
        """
        Called when the page is displayed.
        """
        NavigationView.set_active(self)
        self.uistate.viewmanager.tags.tag_enable()
        self.uistate.show_filter_results(self.dbstate,
                                         self.model.displayed(),
                                         self.model.total())

    def set_inactive(self):
        """
        Called when the page is no longer displayed.
        """
        NavigationView.set_inactive(self)
        self.uistate.viewmanager.tags.tag_disable()

    def __build_tree(self):
        profile(self._build_tree)

    def build_tree(self, force_sidebar=False):
        if self.active:
            cput0 = time.clock()
            if not self.search_bar.is_visible():
                filter_info = (True, self.generic_filter, False)
            else:
                value = self.search_bar.get_value()
                filter_info = (False, value, value[0] in self.exact_search())

            if self.dirty or not self.model:
                if self.model:
                    self.list.set_model(None)
                    self.model.destroy()
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

            self.dirty = False
            cput4 = time.clock()
            self.uistate.show_filter_results(self.dbstate,
                                             self.model.displayed(),
                                             self.model.total())
            LOG.debug(self.__class__.__name__ + ' build_tree ' +
                    str(time.clock() - cput0) + ' sec')
            LOG.debug('parts ' + str(cput1-cput0) + ' , '
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

    def get_viewtype_stock(self):
        """Type of view in category, default listview is a flat list
        """
        return 'gramps-tree-list'

    def filter_editor(self, obj):
        try:
            FilterEditor(self.FILTER_TYPE , CUSTOM_FILTERS,
                         self.dbstate, self.uistate)
        except WindowActiveError:
            return

    def setup_filter(self):
        """Build the default filters and add them to the filter menu."""
        self.search_bar.setup_filter(
            [(self.COLUMNS[pair[1]][0], pair[1], pair[1] in self.exact_search())
                for pair in self.column_order() if pair[0]])

    def sidebar_toggled(self, active, data=None):
        """
        Called when the sidebar is toggled.
        """
        if active:
            self.search_bar.hide()
        else:
            self.search_bar.show()

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

        iter_ = self.model.get_iter_from_handle(handle)
        if iter_:
            if not (self.model.get_flags() & Gtk.TreeModelFlags.LIST_ONLY):
                # Expand tree
                parent_iter = self.model.iter_parent(iter_)
                if parent_iter:
                    parent_path = self.model.get_path(parent_iter)
                    if parent_path:
                        parent_path_list = parent_path.get_indices()
                        for i in range(len(parent_path_list)):
                            expand_path = Gtk.TreePath(
                                    tuple([x for x in parent_path_list[:i+1]]))
                            self.list.expand_row(expand_path, False)

            # Select active object
            path = self.model.get_path(iter_)
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
            from ..dialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"),
                _("A bookmark could not be set because "
                  "nothing was selected."))

    ####################################################################
    #
    ####################################################################

    def drag_info(self):
        """
        Specify the drag type for a single selected row
        """
        return None

    def drag_list_info(self):
        """
        Specify the drag type for a multiple selected rows
        """
        return DdTargets.LINK_LIST

    def drag_dest_info(self):
        """
        Specify the drag type for objects dropped on the view
        """
        return None

    def drag_begin(self, widget, context):
        widget.drag_source_set_icon_name(self.get_stock())

    def drag_data_get(self, widget, context, sel_data, info, time):
        selected_ids = self.selected_handles()

        #Gtk.selection_add_target(widget, sel_data.get_selection(),
        #                         Gdk.atom_intern(self.drag_info().drag_type, False),
        #                         self.drag_info().app_id)

        if len(selected_ids) == 1:
            data = (self.drag_info().drag_type, id(self), selected_ids[0], 0)
            sel_data.set(self.drag_info().atom_drag_type, 8, pickle.dumps(data))
        elif len(selected_ids) > 1:
            data = (self.drag_list_info().drag_type, id(self),
                    [(self.drag_list_info().drag_type, handle)
                        for handle in selected_ids],
                    0)
            sel_data.set(self.drag_list_info().atom_drag_type, 8, pickle.dumps(data))
        else:
            # pass empty
            data = (self.drag_info().drag_type, id(self), [], 0)
            sel_data.set(self.drag_list_info().atom_drag_type, 8, pickle.dumps(data))

    def set_column_order(self):
        """
        change the order of the columns to that given in config file
        after config file changed. We reset the sort to the first column
        """
        #now we need to rebuild the model so it contains correct column info
        self.dirty = True
        #make sure we sort on first column. We have no idea where the
        # column that was sorted on before is situated now.
        self.sort_col = 0
        self.sort_order = Gtk.SortType.ASCENDING
        self.setup_filter()
        self.build_tree()

    def column_order(self):
        """
        Column order is obtained from the config file of the listview.
        A column order is a list of 3-tuples. The order in the list is the
        order the columns must appear in.
        For a column, the 3-tuple should be (enable, modelcol, sizecol), where
            enable: show this column or don't show it
            modelcol: column in the datamodel this column is build of
            size: size the column should have
        """
        order = self._config.get('columns.rank')
        size = self._config.get('columns.size')
        vis =  self._config.get('columns.visible')

        colord = [(1 if val in vis else 0, val, size)
            for val, size in zip(order, size)]
        return colord

    def get_column_widths(self):
        return [column.get_width() for column in self.columns]

    def remove_selected_objects(self):
        """
        Function to remove selected objects
        """
        prompt = True
        if len(self.selected_handles()) > 1:
            q = QuestionDialog2(
                _("Multiple Selection Delete"),
                _("More than one item has been selected for deletion. "
                  "Select the option indicating how to delete the items:"),
                _("Delete All"),
                _("Confirm Each Delete"))
            prompt = not q.run()

        if not prompt:
            self.uistate.set_busy_cursor(True)

        for handle in self.selected_handles():
            (query, is_used, object) = self.remove_object_from_handle(handle)
            if prompt:
                if is_used:
                    msg = _('This item is currently being used. '
                            'Deleting it will remove it from the database and '
                            'from all other items that reference it.')
                else:
                    msg = _('Deleting item will remove it from the database.')

                msg += ' ' + data_recover_msg
                #descr = object.get_description()
                #if descr == "":
                descr = object.get_gramps_id()
                self.uistate.set_busy_cursor(True)
                QuestionDialog(_('Delete %s?') % descr, msg,
                               _('_Delete Item'), query.query_response)
                self.uistate.set_busy_cursor(False)
            else:
                query.query_response()

        if not prompt:
            self.uistate.set_busy_cursor(False)

    def blist(self, store, path, iter_, sel_list):
        '''GtkTreeSelectionForeachFunc
            construct a list sel_list with all selected handles
        '''
        handle = store.get_handle_from_iter(iter_)
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
        self.uistate.set_busy_cursor(True)
        self.uistate.push_message(self.dbstate, _("Column clicked, sorting..."))
        cput = time.clock()
        same_col = False
        if self.sort_col != data:
            order = Gtk.SortType.ASCENDING
        else:
            same_col = True
            if (self.columns[data].get_sort_order() == Gtk.SortType.DESCENDING
                or not self.columns[data].get_sort_indicator()):
                order = Gtk.SortType.ASCENDING
            else:
                order = Gtk.SortType.DESCENDING

        self.sort_col = data
        self.sort_order = order
        handle = self.first_selected()

        if not self.search_bar.is_visible():
            filter_info = (True, self.generic_filter, False)
        else:
            value = self.search_bar.get_value()
            filter_info = (False, value, value[0] in self.exact_search())

        if same_col:
            # activate when https://bugzilla.gnome.org/show_bug.cgi?id=684558
            # is resolved
            if False:
                self.model.reverse_order()
            else:
                ## GTK 3.6 rows_reordered not exposed by gi, we need to reconnect
                ## model to obtain desired effect, but this collapses nodes ...
                self.list.set_model(None)
                self.model.reverse_order()
                self.list.set_model(self.model)
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

        self.uistate.set_busy_cursor(False)

        LOG.debug('   ' + self.__class__.__name__ + ' column_clicked ' +
                    str(time.clock() - cput) + ' sec')

    def __display_column_sort(self):
        for i, c in enumerate(self.columns):
            c.set_sort_indicator(i == self.sort_col)
        self.columns[self.sort_col].set_sort_order(self.sort_order)

    def connect_signals(self):
        """
        Connect database signals defined in the signal map.
        """
        for sig in self.signal_map:
            self.callman.add_db_signal(sig, self.signal_map[sig])
        self.callman.add_db_signal('tag-update', self.tag_updated)

    def change_db(self, db):
        """
        Called when the database is changed.
        """
        self.list.set_model(None)
        self._change_db(db)
        self.connect_signals()

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
                self.list.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                      [],
                                      Gdk.DragAction.COPY)
                #TODO GTK3: wourkaround here for bug https://bugzilla.gnome.org/show_bug.cgi?id=680638
                tglist = Gtk.TargetList.new([])
                dtype = self.drag_info()
                tglist.add(dtype.atom_drag_type, dtype.target_flags, dtype.app_id)
                self.list.drag_source_set_target_list(tglist)
        elif len(selected_ids) > 1:
            if self.drag_list_info():
                self.list.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                      [],
                                      Gdk.DragAction.COPY)
                #TODO GTK3: wourkaround here for bug https://bugzilla.gnome.org/show_bug.cgi?id=680638
                tglist = Gtk.TargetList.new([])
                dtype = self.drag_list_info()
                tglist.add(dtype.atom_drag_type, dtype.target_flags, dtype.app_id)
                self.list.drag_source_set_target_list(tglist)

        self.uistate.modify_statusbar(self.dbstate)

    def row_add(self, handle_list):
        """
        Called when an object is added.
        """
        if self.active or \
           (not self.dirty and not self._dirty_on_change_inactive):
            cput = time.clock()
            list(map(self.model.add_row_by_handle, handle_list))
            LOG.debug('   ' + self.__class__.__name__ + ' row_add ' +
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
            #store selected handles
            self._sel_handles_before_update = self.selected_handles()
            list(map(self.model.update_row_by_handle, handle_list))
            LOG.debug('   ' + self.__class__.__name__ + ' row_update ' +
                    str(time.clock() - cput) + ' sec')
            # Ensure row is still selected after a change of postion in tree.
            if self._sel_handles_before_update:
                #we can only set one selected again, we take last
                self.goto_handle(self._sel_handles_before_update[-1])
            elif handle_list and not self.selected_handles():
                self.goto_handle(handle_list[-1])
        else:
            self.dirty = True

    def row_delete(self, handle_list):
        """
        Called when an object is deleted.
        """
        if self.active or \
           (not self.dirty and not self._dirty_on_change_inactive):
            cput = time.clock()
            list(map(self.model.delete_row_by_handle, handle_list))
            LOG.debug('   '  + self.__class__.__name__ + ' row_delete ' +
                    str(time.clock() - cput) + ' sec')
            if self.active:
                self.uistate.show_filter_results(self.dbstate,
                                                 self.model.displayed(),
                                                 self.model.total())
        else:
            self.dirty = True

    def object_build(self, *args):
        """
        Called when the tree must be rebuilt and bookmarks redrawn.
        """
        self.dirty = True
        if self.active:
            # Save the currently selected handles, if any:
            selected_ids = self.selected_handles()
            self.bookmarks.redraw()
            self.build_tree()
            # Reselect one, if it still exists after rebuild:
            nav_type = self.navigation_type()
            lookup_handle = self.dbstate.db.get_table_metadata(nav_type)['handle_func']
            for handle in selected_ids:
                # Still exist?
                if lookup_handle(handle):
                    # Select it, and stop selecting:
                    self.change_active(handle)
                    break

    def _button_press(self, obj, event):
        """
        Called when a mouse is clicked.
        """
        if not self.dbstate.open:
            return False
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            if self.model.get_flags() & Gtk.TreeModelFlags.LIST_ONLY:
                self.edit(obj)
                return True
            else:
                # Tree
                store, paths = self.selection.get_selected_rows()
                if paths:
                    firstsel = self.model.get_iter(paths[0])
                    handle = self.model.get_handle_from_iter(firstsel)
                    if len(paths)==1 and handle is None:
                        return self.expand_collapse_tree_branch()
                    else:
                        self.edit(obj)
                        return True
        elif is_right_click(event):
            menu = self.uistate.uimanager.get_widget('/Popup')
            if menu:
                # Quick Reports
                qr_menu = self.uistate.uimanager.\
                            get_widget('/Popup/QuickReport')
                if qr_menu and self.QR_CATEGORY > -1 :
                    (ui, qr_actions) = create_quickreport_menu(
                                            self.QR_CATEGORY,
                                            self.dbstate,
                                            self.uistate,
                                            self.first_selected())
                    self.__build_menu(qr_menu, qr_actions)

                # Web Connects
                web_menu = self.uistate.uimanager.\
                                get_widget('/Popup/WebConnect')
                if web_menu:
                    web_actions = create_web_connect_menu(
                                        self.dbstate,
                                        self.uistate,
                                        self.navigation_type(),
                                        self.first_selected())
                    self.__build_menu(web_menu, web_actions)

                menu.popup(None, None, None, None, event.button, event.time)
                return True

        return False

    def __build_menu(self, menu, actions):
        """
        Build a submenu for quick reports and web connects
        """
        if self.get_active() and len(actions) > 1:
            sub_menu = Gtk.Menu()
            for action in actions[1:]:
                add_menuitem(sub_menu, action[2], None, action[5])
            menu.set_submenu(sub_menu)
            menu.show()
        else:
            menu.hide()

    def _key_press(self, obj, event):
        """
        Called when a key is pressed on a listview
        """
        if not self.dbstate.open:
            return False
        if self.model.get_flags() & Gtk.TreeModelFlags.LIST_ONLY:
            # Flat list
            return self._key_press_flat(obj, event)
        else:
            # Tree
            return self._key_press_tree(obj, event)

    def _key_press_flat(self, obj, event):
        """
        Called when a key is pressed on a flat listview
        ENTER --> edit selection
        """
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self.edit(obj)
            return True
        # Custom interactive search
        if event.string:
            return self.searchbox.treeview_keypress(obj, event)
        return False

    def _key_press_tree(self, obj, event):
        """
        Called when a key is pressed on a tree listview
        ENTER --> edit selection or open group node
        SHIFT+ENTER --> open group node and all children nodes
        """
        if (event.get_state() & Gdk.ModifierType.SHIFT_MASK and
            event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter)):
            store, paths = self.selection.get_selected_rows()
            if paths:
                iter_ = self.model.get_iter(paths[0])
                handle = self.model.get_handle_from_iter(iter_)
                if len(paths) == 1 and handle is None:
                    return self.expand_collapse_tree_branch()
        elif event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                store, paths = self.selection.get_selected_rows()
                if paths:
                    iter_ = self.model.get_iter(paths[0])
                    handle = self.model.get_handle_from_iter(iter_)
                    if len(paths) == 1 and handle is None:
                        return self.expand_collapse_tree()
                    else:
                        self.edit(obj)
                        return True
        elif event.string:
            # Custom interactive search
            return self.searchbox.treeview_keypress(obj, event)
        return False

    def expand_collapse_tree(self):
        """
        Expand or collapse the selected group node.
        Return True if change done, False otherwise
        """
        store, paths = self.selection.get_selected_rows()
        if paths:
            firstsel = paths[0]
            iter_ = self.model.get_iter(firstsel)
            handle = self.model.get_handle_from_iter(iter_)
            if handle:
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
            iter_ = self.model.get_iter(firstsel)
            handle = self.model.get_handle_from_iter(iter_)
            if handle:
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

    def on_delete(self):
        """
        Save the column widths when the view is shutdown.
        """
        widths = self.get_column_widths()
        order = self._config.get('columns.rank')
        size = self._config.get('columns.size')
        vis =  self._config.get('columns.visible')
        newsize = []
        index = 0
        for val, size in zip(order, size):
            if val in vis:
                size = widths[index]
                index += 1
            newsize.append(size)
        self._config.set('columns.size', newsize)
        PageView.on_delete(self)

    ####################################################################
    # Export data
    ####################################################################
    def export(self, obj):
        chooser = Gtk.FileChooserDialog(
            _("Export View as Spreadsheet"),
            self.uistate.window,
            Gtk.FileChooserAction.SAVE,
            (_('_Cancel'), Gtk.ResponseType.CANCEL,
             _('_Save'), Gtk.ResponseType.OK))
        chooser.set_do_overwrite_confirmation(True)

        combobox = Gtk.ComboBoxText()
        label = Gtk.Label(label=_("Format:"))
        label.set_halign(Gtk.Align.END)
        box = Gtk.Box()
        box.pack_start(label, True, True, padding=12)
        box.pack_start(combobox, False, False, 0)
        combobox.append_text(_('CSV'))
        combobox.append_text(_('OpenDocument Spreadsheet'))
        combobox.set_active(0)
        box.show_all()
        chooser.set_extra_widget(box)

        while True:
            value = chooser.run()
            fn = chooser.get_filename()
            fl = combobox.get_active()
            if value == Gtk.ResponseType.OK:
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
        from gramps.gen.utils.docgen import CSVTab, ODSTab
        ofile = None
        data_cols = [pair[1] for pair in self.column_order() if pair[0]]

        column_names = [self.COLUMNS[i][0] for i in data_cols]
        if type == 0:
            ofile = CSVTab(len(column_names))
        else:
            ofile = ODSTab(len(column_names))

        ofile.open(name)
        ofile.start_page()
        ofile.start_row()

        # Headings
        if self.model.get_flags() & Gtk.TreeModelFlags.LIST_ONLY:
            headings = column_names
        else:
            levels = self.model.get_tree_levels()
            headings = levels + column_names[1:]
            data_cols = data_cols[1:]

        list(map(ofile.write_cell, headings))
        ofile.end_row()

        if self.model.get_flags() & Gtk.TreeModelFlags.LIST_ONLY:
            # Flat model
            for row in self.model:
                ofile.start_row()
                for index in data_cols:
                    ofile.write_cell(row[index])
                ofile.end_row()
        else:
            # Tree model
            iter_ = self.model.get_iter((0,))
            if iter_:
                self.write_node(iter_, len(levels), [], ofile, data_cols)

        ofile.end_page()
        ofile.close()

    def write_node(self, iter_, depth, level, ofile, data_cols):

        while iter_:
            new_level = level + [self.model.get_value(iter_, 0)]
            if self.model.get_handle_from_iter(iter_):
                ofile.start_row()
                padded_level = new_level + [''] * (depth - len(new_level))
                list(map(ofile.write_cell, padded_level))
                for index in data_cols:
                    ofile.write_cell(self.model.get_value(iter_, index))
                ofile.end_row()

            first_child = self.model.iter_children(iter_)
            self.write_node(first_child, depth, new_level, ofile, data_cols)

            iter_ = self.model.iter_next(iter_)

    ####################################################################
    # Template functions
    ####################################################################
    def get_bookmarks(self):
        """
        Template function to get bookmarks.
        We could implement this in the NavigationView
        """
        raise NotImplementedError

    def edit(self, obj, data=None):
        """
        Template function to allow the editing of the selected object
        """
        raise NotImplementedError

    def remove(self, handle, data=None):
        """
        Template function to allow the removal of an object by its handle
        """
        raise NotImplementedError

    def add(self, obj, data=None):
        """
        Template function to allow the adding of a new object
        """
        raise NotImplementedError

    def merge(self, obj, data=None):
        """
        Template function to allow the merger of two objects.
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

        store, selected = self.selection.get_selected_rows()
        for path in selected:
            self.list.expand_row(path, False)

        self.uistate.set_busy_cursor(False)
        self.uistate.modify_statusbar(self.dbstate)

    def close_branch(self, obj):
        """
        Collapse the selected branches.
        :param obj: not used, present only to allow the use of the method in
            event callback
        """
        store, selected = self.selection.get_selected_rows()
        for path in selected:
            self.list.collapse_row(path)

    def can_configure(self):
        """
        See :class:`~gui.views.pageview.PageView
        :return: bool
        """
        return True

    def config_connect(self):
        """
        Overwriten from  :class:`~gui.views.pageview.PageView method
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """
        #func = self.config_callback(self.build_tree)
        #self._config.connect('columns.visible', func)
        #self._config.connect('columns.rank', func)
        pass

    def _get_configure_page_funcs(self):
        """
        Return a list of functions that create gtk elements to use in the
        notebook pages of the Configure dialog

        :return: list of functions
        """
        def columnpage(configdialog):
            flat = self.model.get_flags() & Gtk.TreeModelFlags.LIST_ONLY
            column_names = [col[0] for col in self.COLUMNS]
            return _('Columns'), ColumnOrder(self._config, column_names,
                                            self.get_column_widths(),
                                            self.set_column_order,
                                            tree=not flat)
        return [columnpage]
