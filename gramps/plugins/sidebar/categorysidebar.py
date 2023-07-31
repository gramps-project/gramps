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

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gui.basesidebar import BaseSidebar

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
UICATEGORY = """<ui>
<toolbar name="ToolBar">
  <placeholder name="ViewsInCategory">%s
  </placeholder>
</toolbar>
</ui>
"""


# -------------------------------------------------------------------------
#
# CategorySidebar class
#
# -------------------------------------------------------------------------
class CategorySidebar(BaseSidebar):
    """
    A sidebar displaying a column of toggle buttons that allows the user to
    change the current view.
    """

    def __init__(self, dbstate, uistate, categories, views):
        self.viewmanager = uistate.viewmanager

        self.buttons = []
        self.button_handlers = []

        self.ui_category = {}
        self.merge_ids = []

        self.window = Gtk.ScrolledWindow()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(vbox)
        self.window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.window.show()

        use_text = config.get("interface.sidebar-text")
        for cat_num, cat_name, cat_icon in categories:
            # create the button and add it to the sidebar
            button = self.__make_sidebar_button(use_text, cat_num, cat_name, cat_icon)
            vbox.pack_start(button, False, True, 0)

            # Enable view switching during DnD
            button.drag_dest_set(0, [], 0)
            button.connect("drag_motion", self.cb_switch_page_on_dnd, cat_num)

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
        # Add buttons to the toolbar for the different view in the category
        uimanager = self.viewmanager.uimanager
        list(map(uimanager.remove_ui, self.merge_ids))
        if cat_num in self.ui_category:
            mergeid = uimanager.add_ui_from_string(self.ui_category[cat_num])
            self.merge_ids.append(mergeid)

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

    def cb_view_clicked(self, radioaction, current, cat_num):
        """
        Called when a button causes a view change.
        """
        view_num = radioaction.get_current_value()
        self.viewmanager.goto_page(cat_num, view_num)

    def __category_clicked(self, button, cat_num):
        """
        Called when a button causes a category change.
        """
        # Make the button active.  If it was already active the category will
        # not change.
        button.set_active(True)
        self.viewmanager.goto_page(cat_num, None)

    def __make_sidebar_button(self, use_text, index, page_title, page_stock):
        """
        Create the sidebar button. The page_title is the text associated with
        the button.
        """
        # create the button
        button = Gtk.ToggleButton()
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.buttons.append(button)

        # add the tooltip
        button.set_tooltip_text(page_title)

        # connect the signal, along with the index as user data
        handler_id = button.connect("clicked", self.__category_clicked, index)
        self.button_handlers.append(handler_id)
        button.show()

        # add the image. If we are using text, use the BUTTON (larger) size.
        # otherwise, use the smaller size
        hbox = Gtk.Box()
        hbox.show()
        image = Gtk.Image()
        if use_text:
            image.set_from_icon_name(page_stock, Gtk.IconSize.BUTTON)
        else:
            image.set_from_icon_name(page_stock, Gtk.IconSize.DND)
        image.show()
        hbox.pack_start(image, False, False, 0)
        hbox.set_spacing(4)

        # add text if requested
        if use_text:
            label = Gtk.Label(label=page_title)
            label.show()
            hbox.pack_start(label, False, True, 0)

        button.add(hbox)
        return button

    def cb_switch_page_on_dnd(self, widget, context, xpos, ypos, time, page_no):
        """
        Switches the page based on drag and drop.
        """
        self.__handlers_block()
        if self.viewmanager.notebook.get_current_page() != page_no:
            self.viewmanager.notebook.set_current_page(page_no)
        self.__handlers_unblock()

    def inactive(self):
        """
        Called when the sidebar is hidden.
        """
        uimanager = self.viewmanager.uimanager
        list(map(uimanager.remove_ui, self.merge_ids))
