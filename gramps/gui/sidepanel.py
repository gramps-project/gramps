#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Doug Blank
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
A module that provides pluggable side panels.  These provide a
persistent panel visible alongside the main Gramps view area.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import abc
import logging
from typing import TYPE_CHECKING

# -------------------------------------------------------------------------
#
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject, Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.db import DbReadBase
from gramps.gen.dbstate import DbState
from gramps.gen.plug import START
from .pluginmanager import GuiPluginManager

if TYPE_CHECKING:
    from .displaystate import DisplayState

# -------------------------------------------------------------------------
#
# Module-level logger
#
# -------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -------------------------------------------------------------------------
#
# BaseSidePanel class
#
# -------------------------------------------------------------------------
class BaseSidePanel(abc.ABC):
    """
    The base class for all side panel plugins.
    """

    def __init__(self, dbstate: DbState, uistate: "DisplayState") -> None:
        """
        Initialise the side panel.

        Subclasses should call super().__init__(dbstate, uistate) to have
        self.dbstate and self.uistate set automatically.

        :param dbstate: The Gramps database state.
        :type dbstate: DbState
        :param uistate: The Gramps UI state.
        :type uistate: "DisplayState"
        """
        self.dbstate = dbstate
        self.uistate = uistate

    @abc.abstractmethod
    def get_top(self) -> Gtk.Widget:
        """
        Return the top container widget for the GUI.

        :returns: The top-level widget for this panel.
        :rtype: Gtk.Widget
        """

    @abc.abstractmethod
    def view_changed(self, cat_num: int, view_num: int) -> None:
        """
        Called when the active view is changed.

        :param cat_num: The category number of the new view.
        :type cat_num: int
        :param view_num: The view number within the category.
        :type view_num: int
        """

    def db_changed(self, db: DbReadBase) -> None:
        """
        Called when the database is changed (opened or closed).

        :param db: The new database object (may be a NullDB when closed).
        :type db: DbReadBase
        """

    def active(self, cat_num: int, view_num: int) -> None:
        """
        Called when the panel becomes visible.

        :param cat_num: The active category number.
        :type cat_num: int
        :param view_num: The active view number within the category.
        :type view_num: int
        """

    def inactive(self) -> None:
        """
        Called when the panel is hidden.
        """


# -------------------------------------------------------------------------
#
# SidePanelManager class
#
# -------------------------------------------------------------------------
class SidePanelManager:
    """
    Manages one or more SIDEPANEL plugins in a container widget on the
    right-hand side of the main Gramps window.  Analogous to Navigator
    for SIDEBAR plugins.
    """

    def __init__(self, viewmanager: object) -> None:
        """
        Initialise the side panel manager.

        :param viewmanager: The Gramps view manager instance.
        :type viewmanager: ViewManager
        """
        self.viewmanager = viewmanager
        self.pages: dict[str, BaseSidePanel] = {}
        self._active_page: str | None = None
        self.active_cat: int | None = None
        self.active_view: int | None = None

        self.top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.top.show()

        self.select_button = Gtk.ComboBoxText()
        self.select_button.hide()
        self.top.pack_start(self.select_button, False, False, 0)

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

    def load_plugins(self, dbstate: DbState, uistate: "DisplayState") -> None:
        """
        Load the side panel plugins.

        :param dbstate: The Gramps database state.
        :type dbstate: DbState
        :param uistate: The Gramps UI state.
        :type uistate: "DisplayState"
        """
        plugman = GuiPluginManager.get_instance()

        for pdata in plugman.get_reg_side_panels():
            module = plugman.load_plugin(pdata)
            if not module:
                LOG.warning(
                    "Error loading side panel '%s': skipping content", pdata.name
                )
                continue

            if not pdata.sidepanelclass:
                LOG.warning(
                    "Side panel '%s' has no sidepanelclass set: skipping", pdata.name
                )
                continue
            panel_class = getattr(module, pdata.sidepanelclass)
            panel_page = panel_class(dbstate, uistate)
            self.add(pdata.id, pdata.panel_label, panel_page, pdata.order)

        dbstate.connect("database-changed", self._on_database_changed)

        saved_page = config.get("interface.side-panel-page")
        if saved_page and saved_page in self.pages:
            self.stack.set_visible_child_name(saved_page)
            self.select_button.set_active_id(saved_page)

    def _on_database_changed(self, db: DbReadBase) -> None:
        """
        Called when the active database changes; notifies all loaded panels.

        :param db: The new database object.
        :type db: DbReadBase
        """
        for panel in self.pages.values():
            panel.db_changed(db)

    def has_plugins(self) -> bool:
        """
        Return True if at least one side panel plugin was loaded.

        :returns: True if one or more plugins are loaded, False otherwise.
        :rtype: bool
        """
        return len(self.pages) > 0

    def get_top(self) -> Gtk.Box:
        """
        Return the top container widget for the GUI.

        :returns: The top-level container widget.
        :rtype: Gtk.Box
        """
        return self.top

    def add(self, plugin_id: str, title: str, panel: BaseSidePanel, order: int) -> None:
        """
        Add a page to the side panel manager for a plugin.

        :param plugin_id: The unique plugin ID used as the internal page key.
        :type plugin_id: str
        :param title: The display title for this panel page.
        :type title: str
        :param panel: The side panel plugin instance.
        :type panel: BaseSidePanel
        :param order: Insertion order constant (START or END).
        :type order: int
        """
        self.pages[plugin_id] = panel
        page = panel.get_top()
        self.stack.add_named(page, plugin_id)

        if order == START:
            self.select_button.prepend(id=plugin_id, text=title)
            self.select_button.set_active_id(plugin_id)
        else:
            self.select_button.append(id=plugin_id, text=title)

        if len(self.pages) == 2:
            self.select_button.show_all()

    def view_changed(self, cat_num: int, view_num: int) -> None:
        """
        Called when a Gramps view is changed.

        :param cat_num: The new active category number.
        :type cat_num: int
        :param view_num: The new active view number within the category.
        :type view_num: int
        """
        self.active_cat = cat_num
        self.active_view = view_num

        try:
            panel = self.pages[self.stack.get_visible_child_name()]
        except KeyError:
            return
        panel.view_changed(cat_num, view_num)

    def cb_switch_page(self, stack: Gtk.Stack, pspec: GObject.ParamSpec) -> None:
        """
        Called when the user has switched to a new side panel plugin page.

        :param stack: The Gtk.Stack widget emitting the signal.
        :type stack: Gtk.Stack
        :param pspec: The GObject parameter spec for the changed property.
        :type pspec: GObject.ParamSpec
        """
        old_page = self._active_page
        if old_page is not None:
            panel = self.pages.get(old_page)
            if panel is not None:
                panel.inactive()

        plugin_id = stack.get_visible_child_name()
        if plugin_id is None:
            # May happen during the time that the widgets have been created, but
            # the pages haven't been added.
            return
        panel = self.pages.get(plugin_id)
        if (
            panel is not None
            and self.active_cat is not None
            and self.active_view is not None
        ):
            panel.active(self.active_cat, self.active_view)
            panel.view_changed(self.active_cat, self.active_view)
        self._active_page = plugin_id
        config.set("interface.side-panel-page", plugin_id)
        config.save()
