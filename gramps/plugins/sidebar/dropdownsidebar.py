#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2010       Nick Hall
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

# -------------------------------------------------------------------------
#
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gio

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gui.basesidebar import BaseSidebar
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# DropdownSidebar class
#
# -------------------------------------------------------------------------
class DropdownSidebar(BaseSidebar):
    """
    A sidebar displaying toggle buttons and buttons with drop-down menus that
    allows the user to change the current view.
    """

    def __init__(self, dbstate, uistate, categories, views):
        self.viewmanager = uistate.viewmanager
        self.views = views

        self.buttons = []
        self.button_handlers = []

        self.window = Gtk.ScrolledWindow()
        grid = Gtk.Grid()
        self.window.add(grid)
        self.window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.window.show()

        use_text = config.get("interface.sidebar-text")
        for cat_num, cat_name, cat_icon in categories:
            self.__make_category(grid, use_text, cat_num, cat_name, cat_icon)

        grid.show_all()

        action_group = Gio.SimpleActionGroup()
        action_group.add_action_entries(
            [
                ("select", self.__menu_selected, "(ii)"),
            ],
            None,
        )
        self.window.insert_action_group("sidebar", action_group)

    def get_top(self):
        """
        Return the top container widget for the GUI.
        """
        return self.window

    def view_changed(self, cat_num, view_num):
        """
        Called when the active view is changed.
        """
        # Set new button as selected
        self.__handlers_block()
        for index, button in enumerate(self.buttons):
            if index == cat_num:
                button.set_active(True)
            else:
                button.set_active(False)
        self.__handlers_unblock()

    def __handlers_block(self):
        """
        Block signals to the buttons to prevent spurious events.
        """
        for idx, button in enumerate(self.buttons):
            button.handler_block(self.button_handlers[idx])

    def __handlers_unblock(self):
        """
        Unblock signals to the buttons.
        """
        for idx, button in enumerate(self.buttons):
            button.handler_unblock(self.button_handlers[idx])

    def __category_clicked(self, button, cat_num):
        """
        Called when a category button is clicked.
        """
        # Make the button active.  If it was already active the category will
        # not change.
        button.set_active(True)
        self.viewmanager.goto_page(cat_num, None)

    def __make_menu(self, cat_num):
        """
        Called when a view drop-down arrow is clicked.
        """
        menu = Gio.Menu()
        for view_num, label, icon in self.views[cat_num]:
            menuitem = Gio.MenuItem.new(
                label=label, detailed_action=f"sidebar.select(({cat_num}, {view_num}))"
            )
            menuitem.set_icon(Gio.ThemedIcon.new(iconname=icon))
            menu.append_item(menuitem)
        return menu

    def __menu_selected(self, action, parameter, data):
        """
        Called when a view is selected from a drop-down menu.
        """
        cat_num = parameter.get_child_value(0).get_int32()
        view_num = parameter.get_child_value(1).get_int32()
        self.viewmanager.goto_page(cat_num, view_num)

    def __make_category(self, grid, use_text, cat_num, cat_name, cat_icon):
        """
        Create a row in the sidebar for a category.
        """
        # create the button
        button = Gtk.ToggleButton()
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.buttons.append(button)

        # create the drop-down button to display views
        if len(self.views[cat_num]) > 1:
            dropdown = Gtk.MenuButton(use_popover=False)
            dropdown.set_relief(Gtk.ReliefStyle.NONE)
            dropdown.set_tooltip_text(_("Click to select a view"))
            menu = self.__make_menu(cat_num)
            dropdown.set_menu_model(menu)
            grid.attach(dropdown, 1, cat_num, 1, 1)
            dropdown.set_align_widget(grid)

        # add the tooltip
        button.set_tooltip_text(cat_name)

        # connect the signal, along with the cat_num as user data
        handler_id = button.connect("clicked", self.__category_clicked, cat_num)
        self.button_handlers.append(handler_id)
        button.show()

        # add the image. If we are using text, use the BUTTON (larger) size.
        # otherwise, use the smaller size
        hbox = Gtk.Box()
        hbox.show()
        image = Gtk.Image()
        if use_text:
            image.set_from_icon_name(cat_icon, Gtk.IconSize.BUTTON)
        else:
            image.set_from_icon_name(cat_icon, Gtk.IconSize.DND)
        image.show()
        hbox.pack_start(image, False, False, 0)
        hbox.set_spacing(4)

        # add text if requested
        if use_text:
            label = Gtk.Label(label=cat_name)
            label.show()
            hbox.pack_start(label, False, True, 0)

        button.add(hbox)

        # Enable view switching during DnD
        button.drag_dest_set(0, [], 0)
        button.connect("drag_motion", self.cb_switch_page_on_dnd, cat_num)

        grid.attach(button, 0, cat_num, 1, 1)

    def cb_switch_page_on_dnd(self, widget, context, xpos, ypos, time, page_no):
        """
        Switches the page based on drag and drop.
        """
        self.__handlers_block()
        if self.viewmanager.notebook.get_current_page() != page_no:
            self.viewmanager.notebook.set_current_page(page_no)
        self.__handlers_unblock()
