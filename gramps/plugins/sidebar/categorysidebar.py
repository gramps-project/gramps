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
# $Id$

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
from gramps.gui.viewmanager import get_available_views, views_to_show

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
UICATEGORY = '''<ui>
<menubar name="MenuBar">
  <menu action="ViewMenu">
    <placeholder name="ViewsInCategory">%s
    </placeholder>
  </menu>
</menubar>
<toolbar name="ToolBar">
  <placeholder name="ViewsInCategory">%s
  </placeholder>
</toolbar>
</ui>
'''

CATEGORY_ICON = {
    'Gramplets': 'gramps-gramplet',
    'People': 'gramps-person',
    'Relationships': 'gramps-relation',
    'Families': 'gramps-family',
    'Events': 'gramps-event',
    'Ancestry': 'gramps-pedigree',
    'Places': 'gramps-place',
    'Geography': 'gramps-geo',
    'Sources': 'gramps-source',
    'Repositories': 'gramps-repository',
    'Media': 'gramps-media',
    'Notes': 'gramps-notes',
    'Citations': 'gramps-citation',
}

#-------------------------------------------------------------------------
#
# CategorySidebar class
#
#-------------------------------------------------------------------------
class CategorySidebar(BaseSidebar):
    """
    A sidebar displaying a column of toggle buttons that allows the user to
    change the current view.
    """
    def __init__(self, dbstate, uistate):

        self.viewmanager = uistate.viewmanager

        self.buttons = []
        self.button_handlers = []

        self.ui_category = {}
        self.view_toggle_actions = {}
        self.cat_view_group = None
        self.merge_ids = []

        self.window = Gtk.ScrolledWindow()
        vbox = Gtk.VBox()
        self.window.add_with_viewport(vbox)
        self.window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.window.show()
        
        use_text = config.get('interface.sidebar-text')
        for cat_num, cat_views in enumerate(self.viewmanager.get_views()):
            uimenuitems = ''
            uitoolitems = ''
            self.view_toggle_actions[cat_num] = []
            for view_num, page in enumerate(cat_views):

                if view_num == 0:
                    category = page[0].category[1]
                    cat_icon = CATEGORY_ICON.get(page[0].category[0])
                    if cat_icon is None:
                        cat_icon = 'gramps-view'

                    # create the button and add it to the sidebar
                    button = self.__make_sidebar_button(use_text, cat_num,
                                                        category, cat_icon)
                    vbox.pack_start(button, False, True, 0)
                    
                    # Enable view switching during DnD
                    button.drag_dest_set(0, [], 0)
                    button.connect('drag_motion', self.cb_switch_page_on_dnd,
                                   cat_num)
                    vbox.show_all()

                pageid = (page[0].id + '_%i' % view_num)
                uimenuitems += '\n<menuitem action="%s"/>' % pageid
                uitoolitems += '\n<toolitem action="%s"/>' % pageid
                # id, stock, button text, UI, tooltip, page
                if view_num < 9:
                    modifier = "<PRIMARY><ALT>%d" % ((view_num % 9) + 1)
                else:
                    modifier = ""

                stock_icon = page[0].stock_icon
                if stock_icon is None:
                    stock_icon = cat_icon
                self.view_toggle_actions[cat_num].append((pageid, 
                            stock_icon,
                            page[0].name, modifier, page[0].name, view_num))

            if len(cat_views) > 1:
                #allow for switching views in a category
                self.ui_category[cat_num] = UICATEGORY % (uimenuitems,
                                                        uitoolitems)

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
        if self.cat_view_group:
            if self.cat_view_group in uimanager.get_action_groups(): 
                uimanager.remove_action_group(self.cat_view_group)
                
            map(uimanager.remove_ui, self.merge_ids)

        if cat_num in self.ui_category:
            self.cat_view_group = Gtk.ActionGroup('categoryviews')
            self.cat_view_group.add_radio_actions(
                    self.view_toggle_actions[cat_num], value=view_num,
                    on_change=self.cb_view_clicked, user_data=cat_num)
            self.cat_view_group.set_sensitive(True)
            uimanager.insert_action_group(self.cat_view_group, 1)
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
        Called when a button causes a category change.
        """
        # Make the button inactive.  It will be set to active in the
        # view_changed method if the change was successful.
        button.set_active(False)
        self.viewmanager.goto_page(cat_num, None)

    def __make_sidebar_button(self, use_text, index, page_title, page_stock):
        """
        Create the sidebar button. The page_title is the text associated with
        the button.
        """
        # create the button
        button = Gtk.ToggleButton()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_alignment(0, 0.5)
        self.buttons.append(button)

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
        return button

    def cb_switch_page_on_dnd(self, widget, context, xpos, ypos, time, page_no):
        """
        Switches the page based on drag and drop.
        """
        self.__handlers_block()
        if self.viewmanager.notebook.get_current_page() != page_no:
            self.viewmanager.notebook.set_current_page(page_no)
        self.__handlers_unblock()
