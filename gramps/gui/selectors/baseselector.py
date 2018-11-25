#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
#               2009-2011  Gary Burton
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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from ..managedwindow import ManagedWindow
from ..filters import SearchBar
from ..glade import Glade
from ..widgets.interactivesearchbox import InteractiveSearchBox
from ..display import display_help
from gramps.gen.const import URL_MANUAL_PAGE

#-------------------------------------------------------------------------
#
# SelectEvent
#
#-------------------------------------------------------------------------
class BaseSelector(ManagedWindow):
    """Base class for the selectors, showing a dialog from which to select
        one of the primary objects
    """

    NONE   = -1
    TEXT   =  0
    MARKUP =  1
    IMAGE  =  2

    def __init__(self, dbstate, uistate, track=[], filter=None, skip=set(),
                 show_search_bar = True, default=None):
        """Set up the dialog with the dbstate and uistate, track of parent
            windows for ManagedWindow, initial filter for the model, skip with
            set of handles to skip in the view, and search_bar to show the
            SearchBar at the top or not.
        """
        self.filter = (2, filter, False)

        # Set window title, some selectors may set self.title in their __init__
        if not hasattr(self, 'title'):
            self.title = self.get_window_title()

        ManagedWindow.__init__(self, uistate, track, self)

        self.renderer = Gtk.CellRendererText()
        self.track_ref_for_deletion("renderer")
        self.renderer.set_property('ellipsize',Pango.EllipsizeMode.END)

        self.db = dbstate.db
        self.tree = None
        self.model = None

        self.glade = Glade()

        window = self.glade.toplevel
        self.showall =  self.glade.get_object('showall')
        title_label = self.glade.get_object('title')
        vbox = self.glade.get_object('select_person_vbox')
        self.tree =  self.glade.get_object('plist')
        self.tree.set_headers_visible(True)
        self.tree.set_headers_clickable(True)
        self.tree.connect('row-activated', self._on_row_activated)
        self.tree.grab_focus()
        self.define_help_button(
            self.glade.get_object('help'), self.WIKI_HELP_PAGE,
            self.WIKI_HELP_SEC)

        # connect to signal for custom interactive-search
        self.searchbox = InteractiveSearchBox(self.tree)
        self.tree.connect('key-press-event', self.searchbox.treeview_keypress)

        #add the search bar
        self.search_bar = SearchBar(dbstate, uistate, self.build_tree, apply_clear=self.apply_clear)
        filter_box = self.search_bar.build()
        self.setup_filter()
        vbox.pack_start(filter_box, False, False, 0)
        vbox.reorder_child(filter_box, 1)

        self.set_window(window,title_label,self.title)

        #set up sorting
        self.sort_col = 0
        self.setupcols = True
        self.columns = []
        self.sortorder = Gtk.SortType.ASCENDING

        self.skip_list=skip
        self.selection = self.tree.get_selection()
        self.track_ref_for_deletion("selection")

        self._local_init()
        self._set_size()

        self.show()
        #show or hide search bar?
        self.set_show_search_bar(show_search_bar)
        #Hide showall if no filter is specified
        if self.filter[1] is not None:
            self.showall.connect('toggled', self.show_toggle)
            self.showall.show()
        else:
            self.showall.hide()
        while Gtk.events_pending():
            Gtk.main_iteration()
        self.build_tree()
        loading = self.glade.get_object('loading')
        loading.hide()

        if default:
            self.goto_handle(default)

    def goto_handle(self, handle):
        """
        Goto the correct row.
        """
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
                            self.tree.expand_row(expand_path, False)

            # Select active object
            path = self.model.get_path(iter_)
            self.selection.unselect_all()
            self.selection.select_path(path)
            self.tree.scroll_to_cell(path, None, 1, 0.5, 0)
        else:
            self.selection.unselect_all()

    def add_columns(self,tree):
        tree.set_fixed_height_mode(True)
        titles = self.get_column_titles()
        for ix in range(len(titles)):
            item = titles[ix]
            if item[2] == BaseSelector.NONE:
                continue
            elif item[2] == BaseSelector.TEXT:
                column = Gtk.TreeViewColumn(item[0],self.renderer,text=item[3])
            elif item[2] == BaseSelector.MARKUP:
                column = Gtk.TreeViewColumn(item[0],self.renderer,markup=item[3])
            column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            column.set_fixed_width(item[1])
            column.set_resizable(True)
            #connect click
            column.connect('clicked', self.column_clicked, ix)
            column.set_clickable(True)
            ##column.set_sort_column_id(ix) # model has its own sort implemented
            self.columns.append(column)
            tree.append_column(column)

    def build_menu_names(self, obj):
        return (self.title, None)

    def get_selected_ids(self):
        mlist = []
        self.selection.selected_foreach(self.select_function, mlist)
        return mlist

    def first_selected(self):
        """ first selected entry in the Selector tree
        """
        mlist = []
        self.selection.selected_foreach(self.select_function, mlist)
        return mlist[0] if mlist else None

    def select_function(self, store, path, iter_, id_list):
        handle = store.get_handle_from_iter(iter_)
        id_list.append(handle)

    def run(self):
        val = self.window.run()
        result = None
        if val == Gtk.ResponseType.OK:
            id_list = self.get_selected_ids()
            if id_list and id_list[0]:
                result = self.get_from_handle_func()(id_list[0])
            self.close()
        elif val != Gtk.ResponseType.DELETE_EVENT:
            self.close()
        return result

    def _on_row_activated(self, treeview, path, view_col):
        self.window.response(Gtk.ResponseType.OK)

    def _local_init(self):
        # define selector-specific init routine
        pass

    def get_window_title(self):
        assert False, "Must be defined in the subclass"

    def get_model_class(self):
        assert False, "Must be defined in the subclass"

    def get_column_titles(self):
        """
        Defines the columns to show in the selector. Must be defined in the
        subclasses.
        :returns: a list of tuples with four entries. The four entries should
                be 0: column header string, 1: column width,
                2: TEXT, MARKUP or IMAGE, 3: column in the model that must be
                used.
        """
        raise NotImplementedError

    def get_from_handle_func(self):
        assert False, "Must be defined in the subclass"

    def set_show_search_bar(self, value):
        """make the search bar at the top shown
        """
        self.show_search_bar = value
        if not self.search_bar :
            return
        if self.show_search_bar :
            self.search_bar.show()
        else :
            self.search_bar.hide()

    def column_order(self):
        """
        returns a tuple indicating the column order of the model
        """
        return [(1, row[3], row[1], row[0]) for row in self.get_column_titles()]

    def exact_search(self):
        """
        Returns a tuple indicating columns requiring an exact search
        """
        return ()

    def setup_filter(self):
        """
        Builds the default filters and add them to the filter bar.
        """
        cols = [(pair[3], pair[1], pair[0] in self.exact_search())
                    for pair in self.column_order()
                        if pair[0]
                ]
        self.search_bar.setup_filter(cols)

    def build_tree(self):
        """
        Builds the selection people see in the Selector
        """
        if not self.filter[1]:
            filter_info = (False, self.search_bar.get_value(), False)
        else:
            filter_info = self.filter
        if self.model:
            sel = self.first_selected()
        else:
            sel = None

        #set up cols the first time
        if self.setupcols :
            self.add_columns(self.tree)

        #reset the model with correct sorting
        self.clear_model()
        self.model = self.get_model_class()(
            self.db, self.uistate, self.sort_col, self.sortorder,
            sort_map=self.column_order(), skip=self.skip_list,
            search=filter_info)

        self.tree.set_model(self.model)

        #sorting arrow in column header (not on start, only on click)
        if not self.setupcols :
            for i in range(len(self.columns)):
                enable_sort_flag = (i==self.sort_col)
                self.columns[i].set_sort_indicator(enable_sort_flag)
            self.columns[self.sort_col].set_sort_order(self.sortorder)

        # set the search column to be the sorted column
        search_col = self.column_order()[self.sort_col][1]
        self.tree.set_search_column(search_col)

        self.setupcols = False
        if sel:
            self.goto_handle(sel)

    def column_clicked(self, obj, data):
        if self.sort_col != data:
            self.sortorder = Gtk.SortType.ASCENDING
            self.sort_col = data
        else:
            if (self.columns[data].get_sort_order() == Gtk.SortType.DESCENDING
                or not self.columns[data].get_sort_indicator()):
                self.sortorder = Gtk.SortType.ASCENDING
            else:
                self.sortorder = Gtk.SortType.DESCENDING
            self.model.reverse_order()
        self.build_tree()

        return True

    def show_toggle(self, obj):
        filter_info = None if obj.get_active() else self.filter
        self.clear_model()
        self.model = self.get_model_class()(
            self.db, self.uistate, self.sort_col, self.sortorder,
            sort_map=self.column_order(), skip=self.skip_list,
            search=filter_info)
        self.tree.set_model(self.model)
        self.tree.grab_focus()

    def clear_model(self):
        if self.model:
            self.tree.set_model(None)
            if hasattr(self.model, 'destroy'):
                self.model.destroy()
            self.model = None

    def apply_clear(self):
        self.showall.set_active(False)

    def _cleanup_on_exit(self):
        """Unset all things that can block garbage collection.
        Finalize rest
        """
        self.clear_model()
        self.db = None
        self.tree = None
        self.columns = None
        self.search_bar.destroy()

    def close(self, *obj):
        ManagedWindow.close(self)
        self._cleanup_on_exit()

    def define_help_button(self, button, webpage='', section=''):
        """ Setup to deal with help button """
        button.connect('clicked', lambda x: display_help(webpage, section))
