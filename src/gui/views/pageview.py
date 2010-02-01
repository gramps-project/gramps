#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
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
Provide the base class for GRAMPS' DataView classes
"""

#----------------------------------------------------------------
#
# python modules
#
#----------------------------------------------------------------
import logging

_LOG = logging.getLogger('.pageview')

#----------------------------------------------------------------
#
# gtk
#
#----------------------------------------------------------------
import gtk
from gen.ggettext import gettext as _

#----------------------------------------------------------------
#
# GRAMPS 
#
#----------------------------------------------------------------
import Errors
from gui.dbguielement import DbGUIElement
from gui.widgets.menutoolbuttonaction import MenuToolButtonAction
from gui.configure import ConfigureDialog
from config import config

#------------------------------------------------------------------------------
#
# PageView
#
#------------------------------------------------------------------------------
class PageView(DbGUIElement):
    """
    The PageView class is the base class for all Data Views in GRAMPS.  All 
    Views should derive from this class. The ViewManager understands the public
    interface of this class
    
    The following attributes are available
    ..attribute:: active
      is the view active at the moment (visible in Gramps as the main view)
    ..attribute:: dirty
      bool, is the view current with the database or not. A dirty view triggers
      a rebuild when it becomes active
    ..attribute:: _dirty_on_change_inactive
      read/write bool by inheriting classes. 
      Views can behave two ways to signals:
      1. if the view is inactive, set it dirty, and rebuild the view when 
          it becomes active. In this case, this method returns True
      2. if the view is inactive, try to stay in sync with database. Only 
         rebuild or other large changes make view dirty
    ..attribute:: title
      title of the view
    ..attribute:: dbstate
      the dbstate
    ..attribute:: uistate
      the displaystate
    ..attribute:: category
      the category to which the view belongs. Views in the same category are
      placed behind the same button in the sidebar
    """

    CONFIGSETTINGS = []

    def __init__(self, title, dbstate, uistate):
        self.title = title
        self.dbstate = dbstate
        self.uistate = uistate
        self.action_list = []
        self.action_toggle_list = []
        self.action_toolmenu_list = []
        self.action_toolmenu = {} #easy access to toolmenuaction and proxies
        self.action_group = None
        self.additional_action_groups = []
        self.additional_uis = []
        self.widget = None
        self.ui_def = '<ui></ui>'
        self.dirty = True
        self.active = False
        self._dirty_on_change_inactive = True
        self.func_list = {}
        self.category = "Miscellaneous"
        self.ident = None
        self.translated_category = _("Miscellaneous")

        self.dbstate.connect('no-database', self.disable_action_group)
        self.dbstate.connect('database-changed', self.enable_action_group)
        
        self.model = None
        self.selection = None
        self.handle_col = 0
        
        self._config = None
        self.__configure_content = None

        DbGUIElement.__init__(self, dbstate.db)

    def call_function(self, key):
        """
        Calls the function associated with the key value
        """
        self.func_list.get(key)()

    def post(self):
        """
        Called after a page is created.
        """
        pass
    
    def set_active(self):
        """
        Called with the PageView is set as active. If the page is "dirty",
        then we rebuild the data.
        """
        self.active = True
        if self.dirty:
            self.uistate.set_busy_cursor(True)
            self.build_tree()
            self.uistate.set_busy_cursor(False)
            
    def set_inactive(self):
        """
        Marks page as being inactive (not currently displayed)
        """
        self.active = False

    def build_tree(self):
        """
        Rebuilds the current display. This must be overridden by the derived
        class.
        """
        raise NotImplementedError

    def navigation_type(self):
        """
        Indictates the navigation type. Currently, we only support navigation
        for views that are Person centric.
        """
        return None
    
    def ui_definition(self):
        """
        returns the XML UI definition for the UIManager
        """
        return self.ui_def

    def additional_ui_definitions(self):
        """
        Return any additional interfaces for the UIManager that the view
        needs to define.
        """
        return self.additional_uis

    def disable_action_group(self):
        """
        Turns off the visibility of the View's action group, if defined
        """
        if self.action_group:
            self.action_group.set_visible(False)

    def enable_action_group(self, obj):
        """
        Turns on the visibility of the View's action group, if defined
        """
        if self.action_group:
            self.action_group.set_visible(True)

    def get_stock(self):
        """
        Return image associated with the view category, which is used for the 
        icon for the button.
        """
        return gtk.STOCK_MISSING_IMAGE

    def get_viewtype_stock(self):
        """
        Return immage associated with the viewtype inside a view category, it
        will be used for the icon on the button to select view in the category
        """
        return gtk.STOCK_MISSING_IMAGE

    def get_title(self):
        """
        Return the title of the view. This is used to define the text for the
        button, and for the tab label.
        """
        return self.title


    def set_category(self, category):
        """
        Set the category of the view. This is used to define the text for the
        button, and for the tab label.

        category - a tuple of the form (category, translated-category)
        """
        if isinstance(category, tuple):
            self.category = category[0]
            self.translated_category = category[1]
        else:
            raise AttributeError("View category must be (name, translated-name)")

    def get_category(self):
        """
        Return the category name of the view. This is used to define
        the text for the button, and for the tab label.
        """
        return self.category

    def get_translated_category(self):
        """
        Return the translated category name of the view. This is used
        to define the text for the button, and for the tab label.
        """
        return self.translated_category

    def set_ident(self, ident):
        """
        Set the id of the view. This is an unique ident
        """
        self.ident = ident

    def get_display(self):
        """
        Builds the graphical display, returning the top level widget.
        """
        if not self.widget:
            self.widget = self.build_widget()
        return self.widget

    def build_widget(self):
        """
        Builds the container widget for the interface. Must be overridden by the
        the base class. Returns a gtk container widget.
        """
        raise NotImplementedError

    def define_actions(self):
        """
        Defines the UIManager actions. Called by the ViewManager to set up the
        View. The user typically defines self.action_list and 
        self.action_toggle_list in this function. 

        Derived classes must override this function.
        """
        raise NotImplementedError

    def __build_action_group(self):
        """
        Create an UIManager ActionGroup from the values in self.action_list
        and self.action_toggle_list. The user should define these in 
        self.define_actions
        """
        self.action_group = gtk.ActionGroup(self.title)
        if len(self.action_list) > 0:
            self.action_group.add_actions(self.action_list)
        if len(self.action_toggle_list) > 0:
            self.action_group.add_toggle_actions(self.action_toggle_list)
        for action_toolmenu in self.action_toolmenu_list:
            self.action_toolmenu[action_toolmenu[0]] = \
                    MenuToolButtonAction(action_toolmenu[0], #unique name
                                         action_toolmenu[1], #label
                                         action_toolmenu[2], #tooltip
                                         action_toolmenu[3], #callback
                                         action_toolmenu[4]  #arrow tooltip
                                        )
            self.action_group.add_action(
                                    self.action_toolmenu[action_toolmenu[0]])

    def _add_action(self, name, stock_icon, label, accel=None, tip=None, 
                   callback=None):
        """
        Add an action to the action list for the current view. 
        """
        self.action_list.append((name, stock_icon, label, accel, tip, 
                                 callback))

    def _add_toggle_action(self, name, stock_icon, label, accel=None, 
                           tip=None, callback=None, value=False):
        """
        Add a toggle action to the action list for the current view. 
        """
        self.action_toggle_list.append((name, stock_icon, label, accel, 
                                        tip, callback, value))
    
    def _add_toolmenu_action(self, name, label, tooltip, callback, 
                             arrowtooltip):
        """
        Add a menu action to the action list for the current view. 
        """
        self.action_toolmenu_list.append((name, label, tooltip, callback,
                                          arrowtooltip))

    def get_actions(self):
        """
        Return the actions that should be used for the view. This includes the
        standard action group (which handles the main toolbar), along with 
        additional action groups.

        If the action group is not defined, we build it the first time. This 
        allows us to delay the intialization until it is really needed.

        The ViewManager uses this function to extract the actions to install 
        into the UIManager.
        """
        if not self.action_group:
            self.__build_action_group()
        return [self.action_group] + self.additional_action_groups

    def _add_action_group(self, group):
        """
        Allows additional action groups to be added to the view. 
        """
        self.additional_action_groups.append(group)

    def change_page(self):
        """
        Called when the page changes.
        """
        self.uistate.clear_filter_results()

    def edit(self, obj):
        """
        Template function to allow the editing of the selected object
        """
        raise NotImplementedError

    def remove(self, handle):
        """
        Template function to allow the removal of an object by its handle
        """
        raise NotImplementedError

    def remove_object_from_handle(self, handle):
        """
        Template function to allow the removal of an object by its handle
        """
        raise NotImplementedError

    def add(self, obj):
        """
        Template function to allow the adding of a new object
        """
        raise NotImplementedError
    
    def _key_press(self, obj, event):
        """
        Define the action for a key press event
        """
        # TODO: This is never used? (replaced in ListView)
        #act if no modifier, and allow Num Lock as MOD2_MASK
        if not event.state or event.state  in (gtk.gdk.MOD2_MASK, ):
            if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
                self.edit(obj)
                return True
        return False

    def on_delete(self):
        """
        Method called on shutdown. Data views should put code here
        that should be called when quiting the main application.
        """
        pass

    def init_config(self):
        """
        If you need a view with a config, then call this method in the 
        build_tree method. It will set up a config file for the 
        view, and use CONFIGSETTINGS to set the config defaults. 
        The config is later accessbile via self._config
        So you can do 
        self._config.get("section.variable1")
        self._config.set("section.variable1", value)
        self._config.save()
        
        CONFIGSETTINGS should be a list with tuples like 
        ("section.variable1", value)
        """
        if self._config:
            return
        self._config = config.register_manager(self.ident, 
                                               use_config_path=True)
        for section, value in self.CONFIGSETTINGS:
            self._config.register(section, value)
        self._config.init()
        self.config_connect()

    def config_connect(self):
        """
        Overwrite this method to set connects to the config file to monitor
        changes. This method will be called after the ini file is initialized
        Eg:
            self.config.connect("section.option", self.callback)
        """
        pass

    def config_callback(self, callback):
        """
        Convenience wrappen to create a callback for a config setting
        :param callback: a callback function to call.
        """
        return lambda arg1, arg2, arg3, arg4: callback()

    def can_configure(self):
        """
        Inheriting classes should set if the view has a configure window or not
        :return: bool
        """
        return False

    def configure(self):
        """
        Open the configure dialog for the view.
        """
        if not self.__configure_content:
            self.__configure_content = self._get_configure_page_funcs()
        title = _("Configure %(cat)s - %(view)s") % \
                        {'cat': self.get_category(), 'view': self.get_title()}
        try:
            ConfigureDialog(self.uistate, self.dbstate, 
                            self.__configure_content,
                            self, self._config, dialogtitle=title)
        except Errors.WindowActiveError:
            return

    def _get_configure_page_funcs(self):
        """
        Return a list of functions that create gtk elements to use in the 
        notebook pages of the Configure view
        
        :return: list of functions
        """
        raise NotImplementedError
