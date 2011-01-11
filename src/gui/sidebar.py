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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Sidebar class
#
#-------------------------------------------------------------------------
class Sidebar(object):
    """
    A class which defines the graphical representation of the Gramps sidebar.
    """
    def __init__(self, changed_callback, close_callback):

        self.changed_callback = changed_callback
        self.close_callback = close_callback
        self.pages = []
        self.top = gtk.VBox()
        
        frame = gtk.Frame()
        hbox = gtk.HBox()
        frame.add(hbox)
        
        select_button = gtk.ToggleButton()
        select_button.set_relief(gtk.RELIEF_NONE)
        select_hbox = gtk.HBox()
        self.title_label = gtk.Label()
        arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_NONE)
        select_hbox.pack_start(self.title_label, False)
        select_hbox.pack_end(arrow, False)
        select_button.add(select_hbox)

        select_button.connect('button_press_event', self.__menu_button_pressed)

        close_button = gtk.Button()
        img = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close_button.set_image(img)
        close_button.set_relief(gtk.RELIEF_NONE)
        close_button.connect('clicked', self.__close_clicked)
        hbox.pack_start(select_button, False)
        hbox.pack_end(close_button, False)
        #frame.show_all()
        
        self.top.pack_start(frame, False)        

        self.menu = gtk.Menu()
        self.menu.show()
        self.menu.connect('deactivate', self.__menu_deactivate, select_button)

        self.notebook = gtk.Notebook()
        self.notebook.show()
        self.notebook.set_show_tabs(True)
        self.notebook.set_show_border(False)
        self.notebook.connect('switch_page', self.__switch_page)
        self.top.pack_start(self.notebook, True)
        self.top.show()
        
    def get_display(self):
        """
        Return the top container widget for the GUI.
        """
        return self.top

    def show(self):
        """
        Display the sidebar.
        """
        self.top.show()

    def hide(self):
        """
        Hide the sidebar.
        """
        self.top.hide()

    def set_current_page(self, page_num):
        """
        Set the sidebar page.
        """
        self.notebook.set_current_page(page_num)

    def get_page_type(self):
        """
        Return the type of the active page.
        """
        return self.pages[self.notebook.get_current_page()][1]
        
    def add(self, title, container, page_type):
        """
        Add a page to the sidebar.
        """
        menu_item = gtk.MenuItem(title)
        self.pages.append([title, page_type, menu_item])
        index = self.notebook.append_page(container, gtk.Label(title))
        menu_item.connect('activate', self.__menu_activate, index)
        menu_item.show()
        self.menu.append(menu_item)
        self.notebook.set_current_page(index)

    def remove(self, page_type):
        """
        Replace a page in the sidebar.
        """
        position = self.__get_page(page_type)
        if position is not None:
            self.notebook.remove_page(position)
            self.menu.remove(self.pages[position][2])
            self.pages = self.pages[:position] + self.pages[position+1:]

    def __get_page(self, page_type):
        """
        Return the page number of the page with the given type.
        """
        for page_num, page in enumerate(self.pages):
            if page[1] == page_type:
                return page_num
        return None

    def __menu_button_pressed(self, button, event):
        """
        Called when the button to select a sidebar page is pressed.
        """
        if event.button == 1 and event.type == gtk.gdk.BUTTON_PRESS:
            button.grab_focus()
            button.set_active(True)

            self.menu.popup(None, None, self.__menu_position, event.button,
                            event.time, button)
            
    def __menu_position(self, menu, button):
        """
        Determine the position of the popup menu.
        """
        x, y = button.window.get_origin()
        x += button.allocation.x
        y += button.allocation.y + button.allocation.height
        
        return (x, y, False)
        
    def __menu_activate(self, menu, index):
        """
        Called when an item in the popup menu is selected.
        """
        self.notebook.set_current_page(index)

    def __menu_deactivate(self, menu, button):
        """
        Called when the popup menu disappears.
        """
        button.set_active(False)

    def __switch_page(self, notebook, unused, index):
        """
        Called when the user has switched to a new sidebar page.
        """
        if self.pages:
            self.title_label.set_markup('<b>%s</b>' % self.pages[index][0])
            active = self.top.get_property('visible')
            self.changed_callback(self.pages[index][1], active, index)

    def __close_clicked(self, button):
        """
        Called when the sidebar is closed.
        """
        self.close_callback()
