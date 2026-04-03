#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010 Nick Hall
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
A module that provides pluggable assist panels.  These provide a
persistent panel visible alongside the main Gramps view area.
"""

# -------------------------------------------------------------------------
#
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.plug import START
from .pluginmanager import GuiPluginManager


# -------------------------------------------------------------------------
#
# AssistPanelManager class
#
# -------------------------------------------------------------------------
class AssistPanelManager:
    """
    Manages one or more ASSISTPANEL plugins in a container widget on the
    right-hand side of the main Gramps window.  Analogous to Navigator
    for SIDEBAR plugins.
    """

    def __init__(self, viewmanager):
        self.viewmanager = viewmanager
        self.pages = {}
        self._active_page = None
        self.active_cat = None
        self.active_view = None

        self.top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.top.show()

        self.select_button = Gtk.ComboBoxText()
        self.select_button.hide()
        self.top.pack_end(self.select_button, False, True, 0)

        self.stack = Gtk.Stack(homogeneous=False)
        self.stack.show()
        self.stack.connect("notify::visible-child-name", self.cb_switch_page)
        self.top.pack_start(self.stack, True, True, 0)

        self.select_button.bind_property(
            "active-id",
            self.stack,
            "visible-child-name",
            GObject.BindingFlags.BIDIRECTIONAL,
        )

    def load_plugins(self, dbstate, uistate):
        """
        Load the assist panel plugins.
        """
        plugman = GuiPluginManager.get_instance()

        for pdata in plugman.get_reg_assist_panels():
            module = plugman.load_plugin(pdata)
            if not module:
                print("Error loading assist panel '%s': skipping content" % pdata.name)
                continue

            panel_class = getattr(module, pdata.assistpanelclass)
            panel_page = panel_class(dbstate, uistate)
            self.add(pdata.panel_label, panel_page, pdata.order)

        # Forward db_changed to active plugin whenever the database changes
        dbstate.connect("database-changed", self._on_database_changed)

    def _on_database_changed(self, db):
        """
        Called when the active database changes.
        """
        try:
            panel = self.pages[self.stack.get_visible_child_name()]
        except KeyError:
            return
        panel.db_changed(db)

    def has_plugins(self):
        """
        Return True if at least one assist panel plugin was loaded.
        """
        return len(self.pages) > 0

    def get_top(self):
        """
        Return the top container widget for the GUI.
        """
        return self.top

    def add(self, title, panel, order):
        """
        Add a page to the assist panel manager for a plugin.
        """
        self.pages[title] = panel
        page = panel.get_top()
        self.stack.add_named(page, title)

        if order == START:
            self.select_button.prepend(id=title, text=title)
            self.select_button.set_active_id(title)
        else:
            self.select_button.append(id=title, text=title)

        if len(self.stack.get_children()) == 2:
            self.select_button.show_all()

    def view_changed(self, cat_num, view_num):
        """
        Called when a Gramps view is changed.
        """
        self.active_cat = cat_num
        self.active_view = view_num

        try:
            panel = self.pages[self.stack.get_visible_child_name()]
        except KeyError:
            return
        panel.view_changed(cat_num, view_num)

    def cb_switch_page(self, stack, pspec):
        """
        Called when the user has switched to a new assist panel plugin page.
        """
        old_page = self._active_page
        if old_page is not None:
            self.pages[old_page].inactive()

        title = stack.get_visible_child_name()
        if title is None:
            # May happen during the time that the widgets have been created, but
            # the pages haven't been added.
            return
        self.pages[title].active(self.active_cat, self.active_view)
        if self.active_view is not None:
            self.pages[title].view_changed(self.active_cat, self.active_view)
        self._active_page = title
