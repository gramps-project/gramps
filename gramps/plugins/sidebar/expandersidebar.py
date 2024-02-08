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
# $Id: categorysidebar.py 20634 2012-11-07 17:53:14Z bmcage $

# -------------------------------------------------------------------------
#
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
import logging

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gui.basesidebar import BaseSidebar


# -------------------------------------------------------------------------
#
# ExpanderSidebar class
#
# -------------------------------------------------------------------------
class ExpanderSidebar(BaseSidebar):
    """
    A sidebar displaying toggle buttons and buttons with drop-down menus that
    allows the user to change the current view.
    """

    def __init__(self, dbstate, uistate, categories, views):
        self.viewmanager = uistate.viewmanager
        self.views = views

        self.expanders = []
        self.buttons = []
        self.button_handlers = []
        self.lookup = {}

        self.window = Gtk.ScrolledWindow()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(vbox)
        self.window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.window.show()

        use_text = config.get("interface.sidebar-text")
        for cat_num, cat_name, cat_icon in categories:
            expander = Gtk.Expander()
            self.expanders.append(expander)

            catbox = Gtk.Box()
            image = Gtk.Image()
            image.set_from_icon_name(cat_icon, Gtk.IconSize.BUTTON)
            catbox.pack_start(image, False, False, 4)
            if use_text:
                label = Gtk.Label(label=cat_name)
                catbox.pack_start(label, False, True, 4)
            catbox.set_tooltip_text(cat_name)
            expander.set_label_widget(catbox)

            viewbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            for view_num, view_name, view_icon in views[cat_num]:
                # create the button and add it to the sidebar
                button = self.__make_sidebar_button(
                    use_text, cat_num, view_num, view_name, view_icon
                )

                viewbox.pack_start(button, False, False, 0)
            expander.add(viewbox)
            vbox.pack_start(expander, False, True, 0)

            # Enable view switching during DnD
            # catbox.drag_dest_set(0, [], 0)
            # catbox.connect('drag_motion', self.cb_switch_page_on_dnd, cat_num)

        vbox.show_all()

    def get_top(self):
        """
        Return the top container widget for the GUI.
        """
        return self.window

    def view_changed(self, cat_num, view_num):
        """
        Called when the active view is changed.
        """
        # Expand category
        if cat_num is not None:
            self.expanders[cat_num].set_expanded(True)
        # Set new button as selected
        button_num = self.lookup.get((cat_num, view_num))
        self.__handlers_block()
        for index, button in enumerate(self.buttons):
            if index == button_num:
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

    def cb_view_clicked(self, radioaction, current, cat_num):
        """
        Called when a button causes a view change.
        """
        view_num = radioaction.get_current_value()
        self.viewmanager.goto_page(cat_num, view_num)

    def __category_clicked(self, button, cat_num):
        """
        Called when a category button is clicked.
        """
        # Make the button active.  If it was already active the category will
        # not change.
        button.set_active(True)
        self.viewmanager.goto_page(cat_num, None)

    def __view_clicked(self, button, cat_num, view_num):
        """
        Called when a view button is clicked.
        """
        self.viewmanager.goto_page(cat_num, view_num)

    def cb_menu_clicked(self, menuitem, cat_num, view_num):
        """
        Called when a view is selected from a drop-down menu.
        """
        self.viewmanager.goto_page(cat_num, view_num)

    def __make_sidebar_button(self, use_text, cat_num, view_num, view_name, view_icon):
        """
        Create the sidebar button. The page_title is the text associated with
        the button.
        """
        top = Gtk.Box()

        # create the button
        button = Gtk.ToggleButton()
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.buttons.append(button)
        self.lookup[(cat_num, view_num)] = len(self.buttons) - 1

        # add the tooltip
        button.set_tooltip_text(view_name)

        # connect the signal, along with the index as user data
        handler_id = button.connect("clicked", self.__view_clicked, cat_num, view_num)
        self.button_handlers.append(handler_id)
        button.show()

        # add the image. If we are using text, use the BUTTON (larger) size.
        # otherwise, use the smaller size
        hbox = Gtk.Box()
        hbox.show()
        image = Gtk.Image()
        if use_text:
            image.set_from_icon_name(view_icon, Gtk.IconSize.BUTTON)
        else:
            image.set_from_icon_name(view_icon, Gtk.IconSize.DND)
        image.show()
        hbox.pack_start(image, False, False, 0)
        hbox.set_spacing(4)

        # add text if requested
        if use_text:
            label = Gtk.Label(label=view_name)
            label.show()
            hbox.pack_start(label, False, True, 0)

        button.add(hbox)

        top.pack_start(button, False, True, 0)

        return top

    def cb_switch_page_on_dnd(self, widget, context, xpos, ypos, time, page_no):
        """
        Switches the page based on drag and drop.
        """
        self.__handlers_block()
        if self.viewmanager.notebook.get_current_page() != page_no:
            self.viewmanager.notebook.set_current_page(page_no)
        self.__handlers_unblock()
