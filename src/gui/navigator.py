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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$

"""
A module that provides pluggable sidebars.  These provide an interface to
manage pages in the main Gramps window.
"""
#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.plug import (START, END)

#-------------------------------------------------------------------------
#
# Navigator class
#
#-------------------------------------------------------------------------
class Navigator(object):
    """
    A class which defines the graphical representation of the Gramps navigator.
    """
    def __init__(self, viewmanager):

        self.viewmanager = viewmanager
        self.pages = []
        self.top = gtk.VBox()
        
        frame = gtk.Frame()
        hbox = gtk.HBox()
        hbox.show()
        frame.add(hbox)
        frame.show()
        
        self.select_button = gtk.ToggleButton()
        self.select_button.set_relief(gtk.RELIEF_NONE)
        select_hbox = gtk.HBox()
        self.title_label = gtk.Label('')
        arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_NONE)
        select_hbox.pack_start(self.title_label, False)
        select_hbox.pack_end(arrow, False)
        self.select_button.add(select_hbox)

        self.select_button.connect('button_press_event',
                                   self.__menu_button_pressed)

        #close_button = gtk.Button()
        #img = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        #close_button.set_image(img)
        #close_button.set_relief(gtk.RELIEF_NONE)
        #close_button.connect('clicked', self.cb_close_clicked)
        hbox.pack_start(self.select_button, False)
        #hbox.pack_end(close_button, False)

        self.top.pack_end(frame, False)        

        self.menu = gtk.Menu()
        self.menu.show()
        self.menu.connect('deactivate', cb_menu_deactivate, self.select_button)

        self.notebook = gtk.Notebook()
        self.notebook.show()
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook.connect('switch_page', self.cb_switch_page)
        self.top.show()
        self.top.pack_start(self.notebook, True)
        
    def get_top(self):
        """
        Return the top container widget for the GUI.
        """
        return self.top
        
    def add(self, title, sidebar, order):
        """
        Add a page to the sidebar for a plugin.
        """
        self.pages.append((title, sidebar))
        index = self.notebook.append_page(sidebar.get_top(), gtk.Label(title))

        menu_item = gtk.MenuItem(title)
        if order == START:
            self.menu.prepend(menu_item)
            self.notebook.set_current_page(index)
        else:
            self.menu.append(menu_item)
        menu_item.connect('activate', self.cb_menu_activate, index)
        menu_item.show()

        if self.notebook.get_n_pages() == 2:
            self.select_button.show_all()

    def view_changed(self, cat_num, view_num):
        """
        Called when a Gramps view is changed.
        """
        for page in self.pages:
            page[1].view_changed(cat_num, view_num)

    def __menu_button_pressed(self, button, event):
        """
        Called when the button to select a sidebar page is pressed.
        """
        if event.button == 1 and event.type == gtk.gdk.BUTTON_PRESS:
            button.grab_focus()
            button.set_active(True)

            self.menu.popup(None, None, cb_menu_position, event.button,
                            event.time, button)

    def cb_menu_activate(self, menu, index):
        """
        Called when an item in the popup menu is selected.
        """        
        self.notebook.set_current_page(index)

    def cb_switch_page(self, notebook, unused, index):
        """
        Called when the user has switched to a new sidebar plugin page.
        """
        if self.pages:
            self.title_label.set_text(self.pages[index][0])

    def cb_close_clicked(self, button):
        """
        Called when the sidebar is closed.
        """
        uimanager = self.viewmanager.uimanager
        uimanager.get_action('/MenuBar/ViewMenu/Navigator').activate()

#-------------------------------------------------------------------------
#
# Functions
#
#-------------------------------------------------------------------------
def cb_menu_position(menu, button):
    """
    Determine the position of the popup menu.
    """
    x_pos, y_pos = button.window.get_origin()
    x_pos += button.allocation.x
    y_pos += button.allocation.y + button.allocation.height
    
    return (x_pos, y_pos, False)

def cb_menu_deactivate(menu, button):
    """
    Called when the popup menu disappears.
    """
    button.set_active(False)
