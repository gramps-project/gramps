#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010       Nick Hall
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
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gui.basesidebar import BaseSidebar
from Utils import navigation_label
from gui.views.navigationview import NavigationView

#-------------------------------------------------------------------------
#
# HistorySidebar class
#
#-------------------------------------------------------------------------
class HistorySidebar(BaseSidebar):
    """
    A sidebar displaying history for the current navigation type.
    """
    def __init__(self, dbstate, uistate):

        self.viewmanager = uistate.viewmanager
        self.dbstate = dbstate

        self.window = gtk.ScrolledWindow()

        self.model = gtk.ListStore(str, str)
        list = gtk.TreeView(self.model)
        list.set_headers_visible(False)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Name', cell)
        column.add_attribute(cell, "text", 1)
        list.append_column(column)
        list.show_all()

        self.selection = list.get_selection()
        self.selection.connect('changed', self.row_changed)

        self.window.add_with_viewport(list)
        self.window.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_AUTOMATIC)
        self.window.show()

        self.signal = None
        self.view = None
        self.nav_type = None
        self.hobj = None

    def get_top(self):
        """
        Return the top container widget for the GUI.
        """
        return self.window

    def loaded(self):
        """
        Called after all the sidebar plugins have been loaded.
        """
        pass
        
    def view_changed(self, page_num):
        """
        Called when the active view is changed.
        """
        self.__setup_list(self.viewmanager.pages[page_num])

    def __setup_list(self, view):
        """
        Setup the history list when the view changes.
        """
        if self.signal is not None:
            self.hobj.disconnect(self.signal)

        if not isinstance(view, NavigationView):
            self.model.clear()
            return

        self.view = view
        self.nav_type = view.navigation_type()
        self.hobj = view.get_history()
        self.signal = self.hobj.connect('active-changed', self.history_changed)

        self.__populate_list()

    def __populate_list(self):
        """
        Populate the history list from the history object.
        """
        self.model.clear()
        for handle in self.hobj.history:
            name, obj = navigation_label(self.dbstate.db, self.nav_type, handle)
            self.model.append((handle, name))

        # Select the active row in the history
        if self.hobj.index >= 0:
            self.selection.select_path(self.hobj.index)

    def history_changed(self, handle):
        """
        Run when the history changes.
        """
        self.__populate_list()

    def row_changed(self, selection):
        """
        Run when the user selects a different row in the history list.
        """
        model, iter = selection.get_selected()
        if iter:
            handle = model.get_value(iter, 0)
            if handle != self.view.get_active():
                self.view.goto_handle(handle)
