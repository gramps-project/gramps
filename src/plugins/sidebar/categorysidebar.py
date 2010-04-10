#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
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
import config
from gui.basesidebar import BaseSidebar
from gui.viewmanager import get_available_views, views_to_show

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
    'Notes': 'gramps-notes'}

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

        self.window = gtk.ScrolledWindow()
        self.pages = {}
        self.page_defs = {}
        
        self.ui_category = {}
        self.view_toggle_actions = {}
        self.cat_view_group = None
        self.merge_ids = []

        vbox = gtk.VBox()
        self.window.add_with_viewport(vbox)
        self.window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.window.show()
        
        self.views = get_available_views()
        defaults = views_to_show(self.views,
                                 config.get('preferences.use-last-view'))
        self.current_views = defaults[2]
        
        use_text = config.get('interface.sidebar-text')
        for cat_num, cat_views in enumerate(self.views):
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
                    vbox.pack_start(button, False)
                    
                    # Enable view switching during DnD
                    button.drag_dest_set(0, [], 0)
                    button.connect('drag_motion', self.cb_switch_page_on_dnd,
                                   cat_num)
                    vbox.show_all()

                self.page_defs[(cat_num, view_num)] = page

                pageid = (page[0].id + '_%i' % view_num)
                uimenuitems += '\n<menuitem action="%s"/>' % pageid
                uitoolitems += '\n<toolitem action="%s"/>' % pageid
                # id, stock, button text, UI, tooltip, page
                if view_num < 9:
                    modifier = "<CONTROL>%d" % ((view_num % 9) + 1)
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
        # Open the default view
        self.__category_clicked(self.buttons[defaults[0]], defaults[0])

    def get_top(self):
        """
        Return the top container widget for the GUI.
        """
        return self.window

    def view_changed(self, page_num):
        """
        Called when the active view is changed.
        """
        cat_num = view_num = None
        for key in self.pages:
            if self.pages[key] == page_num:
                cat_num, view_num = key
                break

        # Save last view in configuration
        view_id = self.views[cat_num][view_num][0].id
        config.set('preferences.last-view', view_id)
        last_views = config.get('preferences.last-views')
        if len(last_views) != len(self.views):
            # If the number of categories has changed then reset the defaults
            last_views = [''] * len(self.views)
        last_views[cat_num] = view_id 
        config.set('preferences.last-views', last_views)
        config.save()

        # Add buttons to the toolbar for the different view in the category
        uimanager = self.viewmanager.uimanager
        if self.cat_view_group:
            if self.cat_view_group in uimanager.get_action_groups(): 
                uimanager.remove_action_group(self.cat_view_group)
                
            map(uimanager.remove_ui, self.merge_ids)

        if cat_num in self.ui_category:
            self.cat_view_group = gtk.ActionGroup('categoryviews')
            self.cat_view_group.add_radio_actions(
                    self.view_toggle_actions[cat_num], value=view_num,
                    on_change=self.cb_view_clicked, user_data=cat_num)
            self.cat_view_group.set_sensitive(True)
            uimanager.insert_action_group(self.cat_view_group, 1)
            mergeid = uimanager.add_ui_from_string(self.ui_category[cat_num])
            self.merge_ids.append(mergeid)

        # Set new button as selected
        self.handlers_block()
        for index, button in enumerate(self.buttons):
            if index == cat_num:
                button.set_active(True)
            else:
                button.set_active(False)
        self.handlers_unblock()

    def handlers_block(self):
        """
        Block signals to the buttons to prevent spurious events.
        """
        for idx in range(len(self.buttons)):
            self.buttons[idx].handler_block(self.button_handlers[idx])
        
    def handlers_unblock(self):
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
        self.__goto_page(cat_num, view_num)

    def __category_clicked(self, button, cat_num):
        """
        Called when a button causes a category change.
        """
        view_num = self.current_views[cat_num]
        self.__goto_page(cat_num, view_num)
        
        # If the click is on the same view we're in, 
        # restore the button state to active
        if not button.get_active():
            button.set_active(True)

    def __goto_page(self, cat_num, view_num):
        """
        Create the page if it doesn't exist and make it the current page.
        """
        self.current_views[cat_num] = view_num
        
        page_num = self.pages.get((cat_num, view_num))
        if page_num is None:
            page = self.page_defs[(cat_num, view_num)]
            page_num = self.viewmanager.create_page(page[0], page[1])
            self.pages[(cat_num, view_num)] = page_num
            
        self.current_views[cat_num] = view_num    
        self.viewmanager.goto_page(page_num)
        
    def __make_sidebar_button(self, use_text, index, page_title, page_stock):
        """
        Create the sidebar button. The page_title is the text associated with
        the button.
        """
        # create the button
        button = gtk.ToggleButton()
        button.set_relief(gtk.RELIEF_NONE)
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
        hbox = gtk.HBox()
        hbox.show()
        image = gtk.Image()
        if use_text:
            image.set_from_stock(page_stock, gtk.ICON_SIZE_BUTTON)
        else:
            image.set_from_stock(page_stock, gtk.ICON_SIZE_DND)
        image.show()
        hbox.pack_start(image, False, False)
        hbox.set_spacing(4)

        # add text if requested
        if use_text:
            label = gtk.Label(page_title)
            label.show()
            hbox.pack_start(label, False, True)
            
        button.add(hbox)
        return button

    def cb_switch_page_on_dnd(self, widget, context, xpos, ypos, time, page_no):
        """
        Switches the page based on drag and drop.
        """
        self.handlers_block()
        if self.viewmanager.notebook.get_current_page() != page_no:
            self.viewmanager.notebook.set_current_page(page_no)
        self.handlers_unblock()
