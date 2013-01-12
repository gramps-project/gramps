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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id: categorysidebar.py 20634 2012-11-07 17:53:14Z bmcage $

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gui.basesidebar import BaseSidebar

#-------------------------------------------------------------------------
#
# DropdownSidebar class
#
#-------------------------------------------------------------------------
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
        vbox = Gtk.VBox()
        self.window.add_with_viewport(vbox)
        self.window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.window.show()
        
        use_text = config.get('interface.sidebar-text')
        for cat_num, cat_name, cat_icon in categories:

            # create the button and add it to the sidebar
            button = self.__make_sidebar_button(use_text, cat_num,
                                                cat_name, cat_icon)
            vbox.pack_start(button, False, True, 0)
            
            # Enable view switching during DnD
            button.drag_dest_set(0, [], 0)
            button.connect('drag_motion', self.cb_switch_page_on_dnd, cat_num)

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
        for idx in range(len(self.buttons)):
            self.buttons[idx].handler_block(self.button_handlers[idx])
        
    def __handlers_unblock(self):
        """
        Unblock signals to the buttons.
        """
        for idx in range(len(self.buttons)):
            self.buttons[idx].handler_unblock(self.button_handlers[idx])

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
        # Make the button inactive.  It will be set to active in the
        # view_changed method if the change was successful.
        button.set_active(False)
        self.viewmanager.goto_page(cat_num, None)

    def __view_clicked(self, button, cat_num):
        """
        Called when a view drop-down arrow is clicked.
        """
        menu = Gtk.Menu()
        for item in self.views[cat_num]:
            menuitem = Gtk.ImageMenuItem(label=item[1])
            image = Gtk.Image.new_from_stock(item[2], Gtk.IconSize.MENU)
            image.show()
            menuitem.set_image(image)
            menuitem.connect("activate", self.cb_menu_clicked, cat_num, item[0])
            menuitem.show()
            menu.append(menuitem)
        menu.popup(None, None, cb_menu_position, button, 0, 0)

    def cb_menu_clicked(self, menuitem, cat_num, view_num):
        """
        Called when a view is selected from a drop-down menu.
        """
        self.viewmanager.goto_page(cat_num, view_num)

    def __make_sidebar_button(self, use_text, index, page_title, page_stock):
        """
        Create the sidebar button. The page_title is the text associated with
        the button.
        """
        top = Gtk.HBox()
        
        # create the button
        button = Gtk.ToggleButton()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_alignment(0, 0.5)
        self.buttons.append(button)

        button2 = Gtk.Button()
        button2.set_relief(Gtk.ReliefStyle.NONE)
        button2.set_alignment(0.5, 0.5)
        arrow = Gtk.Arrow(Gtk.ArrowType.DOWN, Gtk.ShadowType.NONE)
        button2.add(arrow)
        button2.connect('clicked', self.__view_clicked, index)
        
        # add the tooltip
        button.set_tooltip_text(page_title)

        # connect the signal, along with the index as user data
        handler_id = button.connect('clicked', self.__category_clicked, index)
        self.button_handlers.append(handler_id)
        button.show()

        # add the image. If we are using text, use the BUTTON (larger) size. 
        # otherwise, use the smaller size
        hbox = Gtk.HBox()
        hbox.show()
        image = Gtk.Image()
        if use_text:
            image.set_from_stock(page_stock, Gtk.IconSize.BUTTON)
        else:
            image.set_from_stock(page_stock, Gtk.IconSize.DND)
        image.show()
        hbox.pack_start(image, False, False, 0)
        hbox.set_spacing(4)

        # add text if requested
        if use_text:
            label = Gtk.Label(label=page_title)
            label.show()
            hbox.pack_start(label, False, True, 0)
            
        button.add(hbox)
        
        top.pack_start(button, False, True, 0)
        top.pack_start(button2, False, True, 0)
       
        return top

    def cb_switch_page_on_dnd(self, widget, context, xpos, ypos, time, page_no):
        """
        Switches the page based on drag and drop.
        """
        self.__handlers_block()
        if self.viewmanager.notebook.get_current_page() != page_no:
            self.viewmanager.notebook.set_current_page(page_no)
        self.__handlers_unblock()

def cb_menu_position(menu, button):
    """
    Determine the position of the popup menu.
    """
    ret_val, x_pos, y_pos = button.get_window().get_origin()
    x_pos += button.get_allocation().x
    y_pos += button.get_allocation().y + button.get_allocation().height
    
    return (x_pos, y_pos, False)
