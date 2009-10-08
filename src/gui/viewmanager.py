#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
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

# $Id:ViewManager.py 9912 2008-01-22 09:17:46Z acraphae $

"""
Manages the main window and the pluggable views
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os

from gettext import gettext as _
from cStringIO import StringIO

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".")

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
from cli.grampscli import CLIManager
from PluginUtils import Tool, PluginWindows, \
    ReportPluginDialog, ToolPluginDialog
import ReportBase
import DisplayState
import const
import config
import GrampsCfg
import Errors
from QuestionDialog import (ErrorDialog, WarningDialog, QuestionDialog2, 
                            InfoDialog)
import PageView
import Navigation
import RecentFiles
from BasicUtils import name_displayer
import widgets
import UndoHistory
from gui.dbloader import DbLoader
import GrampsDisplay
from gen.utils import ProgressMonitor
from GrampsAboutDialog import GrampsAboutDialog
import ProgressDialog

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_UNSUPPORTED = _("Unsupported")

UIDEFAULT = '''<ui>
<menubar name="MenuBar">
  <menu action="FileMenu">
    <menuitem action="Open"/>
    <menu action="OpenRecent">
    </menu>
    <separator/>
    <menuitem action="Import"/>
    <menuitem action="Export"/>
    <placeholder name="LocalExport"/>
    <separator/>
    <menuitem action="Abandon"/>
    <menuitem action="Quit"/>
  </menu>
  <menu action="EditMenu">
    <menuitem action="Undo"/>
    <menuitem action="Redo"/>
    <menuitem action="UndoHistory"/>
    <separator/>
    <placeholder name="CommonEdit"/>
    <separator/>
    <menuitem action="ScratchPad"/>
    <placeholder name="Merge"/>
    <separator/>
    <menuitem action="Preferences"/>
  </menu>
  <menu action="ViewMenu">
    <menuitem action="Sidebar"/>
    <menuitem action="Toolbar"/>    
    <menuitem action="Filter"/>    
    <menuitem action="Fullscreen"/>    
    <separator/>
  </menu>
  <menu action="GoMenu">
    <placeholder name="CommonGo"/>
    <placeholder name="CommonHistory"/>
  </menu>
  <menu action="BookMenu">
    <placeholder name="AddEditBook"/>
    <separator/>
    <placeholder name="GoToBook"/>
  </menu>
  <menu action="ReportsMenu">
  </menu>
  <menu action="ToolsMenu">
  </menu>
  <menu action="WindowsMenu">
    <placeholder name="WinMenu"/>
  </menu>
  <menu action="HelpMenu">
    <menuitem action="UserManual"/>
    <menuitem action="FAQ"/>
    <menuitem action="KeyBindings"/>
    <menuitem action="TipOfDay"/>
    <menuitem action="PluginStatus"/>
    <separator/>
    <menuitem action="HomePage"/>
    <menuitem action="MailingLists"/>
    <menuitem action="ReportBug"/>
    <menuitem action="ExtraPlugins"/>
    <separator/>
    <menuitem action="About"/>
  </menu>
</menubar>
<toolbar name="ToolBar">
  <placeholder name="CommonNavigation"/>
  <separator/>
  <toolitem action="ScratchPad"/>  
  <toolitem action="Reports"/>  
  <toolitem action="Tools"/>  
  <separator/>
  <placeholder name="CommonEdit"/>
</toolbar>
<accelerator action="F2"/>
<accelerator action="F3"/>
<accelerator action="F4"/>
<accelerator action="F5"/>
<accelerator action="F6"/>
<accelerator action="F7"/>
<accelerator action="F8"/>
<accelerator action="F9"/>
<accelerator action="F11"/>
<accelerator action="F12"/>
<accelerator action="<CONTROL>BackSpace"/>
<accelerator action="<CONTROL>J"/>
<accelerator action="<CONTROL>N"/>
<accelerator action="<CONTROL>P"/>
</ui>
'''

WIKI_HELP_PAGE_FAQ = '%s_-_FAQ' % const.URL_MANUAL_PAGE
WIKI_HELP_PAGE_KEY = '%s_-_Keybindings' % const.URL_MANUAL_PAGE
WIKI_HELP_PAGE_MAN = '%s' % const.URL_MANUAL_PAGE

#-------------------------------------------------------------------------
#
# ViewManager
#
#-------------------------------------------------------------------------

class ViewManager(CLIManager):
    """
    Overview
    ========

    The ViewManager is the session manager of the program. 
    Specifically, it manages the main window of the program. It is closely tied
    into the gtk.UIManager to control all menus and actions.

    The ViewManager controls the various Views within the GRAMPS programs.
    A View is a particular way of looking a information in the GRAMPS main
    window. Each view is separate from the others, and has no knowledge of
    the others. All Views are held in the DisplayViews module. Examples of
    current views include:

    - Person View
    - Relationship View
    - Family View
    - Source View

    The View Manager does not have to know the number of views, the type of
    views, or any other details about the views. It simply provides the 
    method of containing each view, and switching between the views.
       
    """

    def __init__(self, dbstate):
        CLIManager.__init__(self, dbstate, False)
        self.page_is_changing = False
        self.active_page = None
        self.views = []
        self.pages = []
        self.button_handlers = []
        self.buttons = []
        self.merge_ids = []
        self._key = None

        self.show_sidebar = config.get('interface.view')
        self.show_toolbar = config.get('interface.toolbar-on')
        self.show_filter = config.get('interface.filter')
        self.fullscreen = config.get('interface.fullscreen')

        self.__build_main_window()
        self.__connect_signals()
        self.do_load_plugins()

    def _errordialog(title, errormessage):
        """
        Show the error. 
        In the GUI, the error is shown, and a return happens
        """
        ErrorDialog(title, errormessage)
        return 1
        
    def __build_main_window(self):
        """
        Builds the GTK interface
        """
        width = config.get('interface.width')
        height = config.get('interface.height')

        self.window = gtk.Window()
        self.window.set_icon_from_file(const.ICON)
        self.window.set_default_size(width, height)
        
        self.rel_class = self._pmgr.get_relationship_calculator()

        vbox = gtk.VBox()
        self.window.add(vbox)
        hbox = gtk.HBox()
        self.ebox = gtk.EventBox()
        self.bbox = gtk.VBox()
        self.ebox.add(self.bbox)
        hbox.pack_start(self.ebox, False)
        hbox.show_all()

        self.notebook = gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_show_tabs(False)
        self.notebook.show()
        self.__init_lists()
        self.__build_ui_manager()

        hbox.pack_start(self.notebook, True)
        self.menubar = self.uimanager.get_widget('/MenuBar')
        self.toolbar = self.uimanager.get_widget('/ToolBar')
        vbox.pack_start(self.menubar, False)
        vbox.pack_start(self.toolbar, False)
        vbox.add(hbox)
        vbox.pack_end(self.__setup_statusbar(), False)
        vbox.show()

        self.progress_monitor = ProgressMonitor(
            ProgressDialog.GtkProgressDialog, ("", self.window))

        self.uistate = DisplayState.DisplayState(
            self.window, self.statusbar, self.progress, self.warnbtn, 
            self.uimanager, self.progress_monitor, self)

        self.dbstate.connect('database-changed', self.uistate.db_changed)

        self.filter_menu = self.uimanager.get_widget(
            '/MenuBar/ViewMenu/Filter/')

        # handle OPEN button, insert it into the toolbar. Unfortunately, 
        # UIManager has no built in support for and Open Recent button

        openbtn = self.__build_open_button()
        self.uistate.set_open_widget(openbtn)
        self.toolbar.insert(openbtn, 0)
        
        self.person_nav = Navigation.PersonNavigation(self.dbstate, self.uistate)
        self._navigation_type[PageView.NAVIGATION_PERSON] = (self.person_nav, 
                                                             None)
        self.recent_manager = DisplayState.RecentDocsMenu(
            self.uistate, self.dbstate, self._read_recent_file)
        self.recent_manager.build()

        self.db_loader = DbLoader(self.dbstate, self.uistate)

        self.__setup_sidebar()

        if self.show_toolbar:
            self.toolbar.show()
        else:
            self.toolbar.hide()

        if self.fullscreen:
            self.window.fullscreen()

        # Showing the main window is deferred so that
        # ArgHandler can work without it always shown
        # But we need to realize it here to have gtk.gdk.window handy
        self.window.realize()

    def __setup_statusbar(self):
        """
        Create the statusbar that sits at the bottom of the window
        """
        self.progress = gtk.ProgressBar()
        self.progress.set_size_request(100, -1)
        self.progress.hide()

        self.statusbar = widgets.Statusbar()
        self.statusbar.show()

        self.warnbtn = widgets.WarnButton()

        hbox2 = gtk.HBox()
        hbox2.set_spacing(4)
        hbox2.set_border_width(2)
        hbox2.pack_start(self.progress, False)
        hbox2.pack_start(self.warnbtn, False)
        hbox2.pack_end(self.statusbar, True)
        hbox2.show()
        return hbox2

    def __setup_sidebar(self):
        """
        If we have enabled te sidebar, show it, and turn off the tabs. If 
        disabled, hide the sidebar and turn on the tabs.
        """
        if self.show_sidebar:
            self.ebox.show()
            self.notebook.set_show_tabs(False)
        else:
            self.ebox.hide()
            self.notebook.set_show_tabs(True)

    def __build_open_button(self):
        """
        Build the OPEN button. Since GTK's UIManager does not have support for
        the Open Recent button, we must build in on our own.
        """
        openbtn = gtk.MenuToolButton('gramps-db')
        openbtn.connect('clicked', self.__open_activate)
        openbtn.set_sensitive(False)
        openbtn.set_tooltip_text(_("Connect to a recent database"))
        openbtn.show()
        return openbtn

    def __connect_signals(self):
        """
        connects the signals needed
        """
        self.window.connect('delete-event', self.quit)
        self.notebook.connect('switch-page', self.change_page)

    def __init_lists(self):
        """
        Initialize the actions lists for the UIManager
        """
        self._file_action_list = [
            ('FileMenu', None, _('_Family Trees')), 
            ('Open', 'gramps-db', _('_Manage Family Trees...'), "<control>o", 
             _("Manage databases"), self.__open_activate), 
            ('OpenRecent', None, _('Open _Recent'), None, 
             _("Open an existing database")), 
            ('Quit', gtk.STOCK_QUIT, _('_Quit'), "<control>q", None, 
             self.quit), 
            ('ViewMenu', None, _('_View')), 
            ('EditMenu', None, _('_Edit')), 
            ('Preferences', gtk.STOCK_PREFERENCES, _('_Preferences...'), None,
             None, self.preferences_activate), 
            ('HelpMenu', None, _('_Help')), 
            ('HomePage', None, _('GRAMPS _Home Page'), None, None, 
             home_page_activate),
            ('MailingLists', None, _('GRAMPS _Mailing Lists'), None, None, 
             mailing_lists_activate), 
            ('ReportBug', None, _('_Report a Bug'), None, None, 
             report_bug_activate),
            ('ExtraPlugins', None, _('_Extra Reports/Tools'), None, None, 
             extra_plugins_activate),
            ('About', gtk.STOCK_ABOUT, _('_About'), None, None, 
             display_about_box),
            ('PluginStatus', None, _('_Plugin Status'), None, None, 
             self.__plugin_status), 
            ('FAQ', None, _('_FAQ'), None, None, faq_activate), 
            ('KeyBindings', None, _('_Key Bindings'), None, None, key_bindings),
            ('UserManual', gtk.STOCK_HELP, _('_User Manual'), 'F1', None, 
             manual_activate), 
            ('TipOfDay', None, _('Tip of the Day'), None, None, 
             self.tip_of_day_activate), 
            ]

        self._readonly_action_list = [ 
            ('Export', 'gramps-export', _('_Export...'), "<control>e", None, 
             self.export_data), 
            ('Abandon', gtk.STOCK_REVERT_TO_SAVED, 
             _('_Abandon Changes and Quit'), None, None, self.abort), 
            ('Reports', 'gramps-reports', _('_Reports'), None, 
             _("Open the reports dialog"), self.reports_clicked), 
            ('GoMenu', None, _('_Go')), 
            ('ReportsMenu', None, _('_Reports')), 
            ('WindowsMenu', None, _('_Windows')), 
            ('F2', None, 'F2', "F2", None, self.__keypress), 
            ('F3', None, 'F3', "F3", None, self.__keypress), 
            ('F4', None, 'F4', "F4", None, self.__keypress), 
            ('F5', None, 'F5', "F5", None, self.__keypress), 
            ('F6', None, 'F6', "F6", None, self.__keypress), 
            ('F7', None, 'F7', "F7", None, self.__keypress), 
            ('F8', None, 'F9', "F8", None, self.__keypress), 
            ('F9', None, 'F9', "F9", None, self.__keypress), 
            ('F11', None, 'F11', "F11", None, self.__keypress), 
            ('<CONTROL>BackSpace', None, '<CONTROL>BackSpace', 
             "<CONTROL>BackSpace", None, self.__keypress), 
            ('<CONTROL>Delete', None, '<CONTROL>Delete', 
             "<CONTROL>Delete", None, self.__keypress), 
            ('<CONTROL>Insert', None, '<CONTROL>Insert', 
             "<CONTROL>Insert", None, self.__keypress), 
            ('F12', None, 'F12', "F12", None, self.__keypress), 
            ('<CONTROL>J', None, '<CONTROL>J', 
             "<CONTROL>J", None, self.__keypress), 
            ('<CONTROL>N', None, '<CONTROL>N', "<CONTROL>N", None, 
             self.__next_view), 
            ('<CONTROL>P', None, '<CONTROL>P', "<CONTROL>P", None, 
             self.__prev_view),
            ]

        self._action_action_list = [
            ('ScratchPad', gtk.STOCK_PASTE, _('Clip_board'), "<control>b", 
             _("Open the Clipboard dialog"), self.scratchpad), 
            ('Import', 'gramps-import', _('_Import...'), "<control>i", None, 
             self.import_data), 
            ('Tools', 'gramps-tools', _('_Tools'), None, 
             _("Open the tools dialog"), self.tools_clicked), 
            ('EditMenu', None, _('_Edit')), 
            ('BookMenu', None, _('_Bookmarks')), 
            ('ToolsMenu', None, _('_Tools')), 
            ]

        self._file_toggle_action_list = [
            ('Sidebar', None, _('_Sidebar'), None, None, self.sidebar_toggle, 
             self.show_sidebar ), 
            ('Toolbar', None, _('_Toolbar'), None, None, self.toolbar_toggle, 
             self.show_toolbar ), 
            ('Filter', None, _('_Filter Sidebar'), None, None, 
             filter_toggle, self.show_filter), 
            ('Fullscreen', None, _('F_ull Screen'), "F11", None, 
             self.fullscreen_toggle, self.fullscreen), 
            ]

        self._undo_action_list = [
            ('Undo', gtk.STOCK_UNDO, _('_Undo'), '<control>z', None, 
             self.undo), 
            ]

        self._redo_action_list = [
            ('Redo', gtk.STOCK_REDO, _('_Redo'), '<shift><control>z', None, 
             self.redo), 
            ]

        self._undo_history_action_list = [
            ('UndoHistory', 'gramps-undo-history', 
             _('Undo History...'), "<control>H", None, self.undo_history), 
            ]

        self._navigation_type = {
            PageView.NAVIGATION_NONE: (None, None), 
            PageView.NAVIGATION_PERSON: (None, None), 
            }

    def __keypress(self, action):
        """
        Callback that is called on a keypress. It works by extracting the 
        name of the associated action, and passes that to the active page 
        (current view) so that it can take the associated action.
        """
        name = action.get_name()
        try:
            self.active_page.call_function(name)
        except Exception:
            self.uistate.push_message(self.dbstate, 
                                      _("Key %s is not bound") % name)

    def __next_view(self, action):
        """
        Callback that is called when the next view action is selected.
        It selects the next view as the active view. If we reach the end of
        the list of views, we wrap around to the first view.
        """
        current_page = self.notebook.get_current_page()
        if current_page == len(self.pages)-1:
            new_page = 0
        else:
            new_page = current_page + 1
        if self.show_sidebar:
            #cause a click signal
            self.buttons[new_page].set_active(True)
        else:
            self.notebook.set_current_page(new_page)

    def __prev_view(self, action):
        """
        Callback that is called when the previous view action is selected.
        It selects the previous view as the active view. If we reach the beginning
        of the list of views, we wrap around to the last view.
        """
        current_page = self.notebook.get_current_page()
        if current_page == 0:
            new_page = len(self.pages)-1
        else:
            new_page = current_page - 1
        if self.show_sidebar:
            #cause a click signal
            self.buttons[new_page].set_active(True)
        else:
            self.notebook.set_current_page(new_page)

    def init_interface(self):
        """
        Initialize the interface, creating the pages
        """
        self.__init_lists()
        self.__create_pages()

        if not self.file_loaded:
            self.actiongroup.set_visible(False)
            self.readonlygroup.set_visible(False)
        self.fileactions.set_sensitive(False)
        self.__build_tools_menu(self._pmgr.get_tool_list())
        self.__build_report_menu(self._pmgr.get_report_list())
        self.uistate.set_relationship_class()
        self._pmgr.connect('plugins-reloaded', 
                             self.__rebuild_report_and_tool_menus)
        self.fileactions.set_sensitive(True)
        self.uistate.widget.set_sensitive(True)
        config.connect("interface.statusbar", 
                          self.__statusbar_key_update)
        config.connect("interface.filter", 
                          self.__filter_signal)

    def __statusbar_key_update(self, client, cnxn_id, entry, data):
        """
        Callback function for statusbar key update
        """
        self.uistate.modify_statusbar(self.dbstate)

    def __filter_signal(self, client, cnxn_id, entry, data):
        """
        Callback function for statusbar key update
        """
        if self.filter_menu.get_active() != config.get('interface.filter'):
            self.filter_menu.set_active(config.get('interface.filter'))

    def post_init_interface(self, show_manager=True):
        """
        Showing the main window is deferred so that
        ArgHandler can work without it always shown
        """
        self.window.show()
        if not self.dbstate.db.is_open() and show_manager:
            self.__open_activate(None)

    def post_load_newdb(self, filename, filetype):
        # Attempt to figure out the database title
        path = os.path.join(filename, "name.txt")
        try:
            ifile = open(path)
            title = ifile.readline().strip()
            ifile.close()
        except:
            title = filename
        self._post_load_newdb(filename, filetype, title)

    def do_load_plugins(self):
        """
        Loads the plugins at initialization time. The plugin status window is 
        opened on an error if the user has requested.
        """
        # load plugins
        self.uistate.status_text(_('Loading plugins...'))
        error = CLIManager.do_load_plugins(self)

        #  get to see if we need to open the plugin status window
        if error and config.get('behavior.pop-plugin-status'):
            self.__plugin_status()

        self.uistate.push_message(self.dbstate, _('Ready'))

    def quit(self, *obj):
        """
        Closes out the program, backing up data
        """
        # mark interface insenstitive to prevent unexpected events
        self.uistate.set_sensitive(False)

        # backup data, and close the database
        self.__backup()
        self.dbstate.db.close()

        # have each page save anything, if they need to:
        self.__delete_pages()
        
        # save the current window size
        (width, height) = self.window.get_size()
        config.set('interface.width', width)
        config.set('interface.height', height)
        config.save()
        gtk.main_quit()

    def __backup(self):
        """
        Backup the current file as a backup file.
        """
        import GrampsDbUtils

        if self.dbstate.db.has_changed:
            self.uistate.set_busy_cursor(1)
            self.uistate.progress.show()
            self.uistate.push_message(self.dbstate, _("Autobackup..."))
            GrampsDbUtils.Backup.backup(self.dbstate.db)
            self.uistate.set_busy_cursor(0)
            self.uistate.progress.hide()

    def abort(self, obj=None):
        """
        Abandon changes and quit.
        """
        if self.dbstate.db.abort_possible:

            dialog = QuestionDialog2(
                _("Abort changes?"), 
                _("Aborting changes will return the database to the state "
                  "is was before you started this editing session."), 
                _("Abort changes"), 
                _("Cancel"))

            if dialog.run():
                self.dbstate.db.disable_signals()
                while self.dbstate.db.undo():
                    pass
                self.quit()
        else:
            WarningDialog(
                _("Cannot abandon session's changes"), 
                _('Changes cannot be completely abandoned because the '
                  'number of changes made in the session exceeded the '
                  'limit.'))

    def __init_action_group(self, name, actions, sensitive=True, toggles=None):
        """
        Initialize an action group for the UIManager
        """
        new_group = gtk.ActionGroup(name)
        new_group.add_actions(actions)
        if toggles:
            new_group.add_toggle_actions(toggles)
        new_group.set_sensitive(sensitive)
        self.uimanager.insert_action_group(new_group, 1)
        return new_group

    def __build_ui_manager(self):
        """
        Builds the UIManager, and the associated action groups
        """
        self.uimanager = gtk.UIManager()

        accelgroup = self.uimanager.get_accel_group()

        self.actiongroup = self.__init_action_group(
            'MainWindow', self._action_action_list)
        self.readonlygroup = self.__init_action_group(
            'AllMainWindow', self._readonly_action_list)
        self.undohistoryactions = self.__init_action_group(
            'UndoHistory', self._undo_history_action_list)
        self.fileactions = self.__init_action_group(
            'FileWindow', self._file_action_list, 
            toggles=self._file_toggle_action_list)
        self.undoactions = self.__init_action_group(
            'Undo', self._undo_action_list, sensitive=False)
        self.redoactions = self.__init_action_group(
            'Redo', self._redo_action_list, sensitive=False)
        self.window.add_accel_group(accelgroup)

        self.uimanager.add_ui_from_string(UIDEFAULT)
        self.uimanager.ensure_update()

    def preferences_activate(self, obj):
        """
        Open the preferences dialog.
        """
        try:
            GrampsCfg.GrampsPreferences(self.uistate, self.dbstate)
            self._key = self.uistate.connect('nameformat-changed', 
                                             self.active_page.build_tree)
        except Errors.WindowActiveError:
            return

    def tip_of_day_activate(self, obj):
        """
        Display Tip of the day
        """
        import TipOfDay
        TipOfDay.TipOfDay(self.uistate)

    def __plugin_status(self, obj=None):
        """
        Display plugin status dialog
        """
        try:
            PluginWindows.PluginStatus(self.uistate, [])
        except Errors.WindowActiveError:
            old_win = self.uistate.gwm.get_item_from_id(
                PluginWindows.PluginStatus)
            old_win.close()
            PluginWindows.PluginStatus(self.uistate, [])

    def sidebar_toggle(self, obj):
        """
        Set the sidebar based on the value of the toggle button. Save the 
        results in the configuration settings
        """
        if obj.get_active():
            self.ebox.show()
            self.notebook.set_show_tabs(False)
            config.set('interface.view', True)
            self.show_sidebar = True
        else:
            self.ebox.hide()
            self.notebook.set_show_tabs(True)
            config.set('interface.view', False)
            self.show_sidebar = False
        config.save()

    def toolbar_toggle(self, obj):
        """
        Set the toolbar based on the value of the toggle button. Save the 
        results in the configuration settings
        """
        if obj.get_active():
            self.toolbar.show()
            config.set('interface.toolbar-on', True)
        else:
            self.toolbar.hide()
            config.set('interface.toolbar-on', False)
        config.save()

    def fullscreen_toggle(self, obj):
        """
        Set the main Granps window fullscreen based on the value of the
        toggle button. Save the setting in the config file.
        """
        if obj.get_active():
            self.window.fullscreen()
            config.set('interface.fullscreen', True)
        else:
            self.window.unfullscreen()
            config.set('interface.fullscreen', False)
        config.save()

    def register_view(self, view):
        """
        Allow other objects to register a view with the View Manager
        """
        self.views.append(view)

    def __switch_page_on_dnd(self, widget, context, xpos, ypos, time, page_no):
        """
        Switches the page based on drag and drop
        """
        self.__vb_handlers_block()
        if self.notebook.get_current_page() != page_no:
            self.notebook.set_current_page(page_no)
        self.__vb_handlers_unblock()

    def __delete_pages(self):
        """
        Calls on_delete() for each view
        """
        for page in self.pages:
            page.on_delete()

    def __create_pages(self):
        """
        Create the Views
        """
        self.pages = []
        self.prev_nav = PageView.NAVIGATION_NONE

        use_text = config.get('interface.sidebar-text')
        
        index = 0
        for page_def in self.views:
            page = page_def(self.dbstate, self.uistate)
            page_title = page.get_title()
            page_stock = page.get_stock()

            # create icon/label for notebook
            hbox = gtk.HBox()
            image = gtk.Image()
            image.set_from_stock(page_stock, gtk.ICON_SIZE_MENU)
            hbox.pack_start(image, False)
            hbox.add(gtk.Label(page_title))
            hbox.show_all()

            # create notebook page and add to notebook
            page.define_actions()
            page_display = page.get_display()
            page_display.show_all()
            page.post()
            page_no = self.notebook.append_page(page_display, hbox)
            self.pages.append(page)
            
            # Enable view switching during DnD
            hbox.drag_dest_set(0, [], 0)
            hbox.connect('drag_motion', self.__switch_page_on_dnd, page_no)

            # create the button and add it to the sidebar
            button = self.__make_sidebar_button(use_text, index, 
                                                page_title, page_stock)

            index += 1
            self.bbox.pack_start(button, False)
            self.buttons.append(button)
            
            # Enable view switching during DnD
            button.drag_dest_set(0, [], 0)
            button.connect('drag_motion', self.__switch_page_on_dnd, page_no)

        use_current = config.get('preferences.use-last-view')
        if use_current:
            current_page = config.get('preferences.last-view')
            if current_page >= len(self.pages):
                current_page = 0
        else:
            current_page = 0

        self.active_page = self.pages[current_page]
        self.buttons[current_page].set_active(True)
        self.active_page.set_active()
        self.notebook.set_current_page(current_page)

    def __make_sidebar_button(self, use_text, index, page_title, page_stock):
        """
        Create the sidebar button. The page_title is the text associated with
        the button.
        """

        # create the button
        button = gtk.ToggleButton()
        button.set_relief(gtk.RELIEF_NONE)
        button.set_alignment(0, 0.5)

        # add the tooltip
        button.set_tooltip_text(page_title)
        #self.tips.set_tip(button, page_title)

        # connect the signal, along with the index as user data
        handler_id = button.connect('clicked', self.__vb_clicked, index)
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

    def __vb_clicked(self, button, index):
        """
        Called when the button causes a page change
        """
        if config.get('interface.view'):
            self.__vb_handlers_block()
            self.notebook.set_current_page(index)

            # If the click is on the same view we're in, 
            # restore the button state to active
            if not button.get_active():
                button.set_active(True)
            self.__vb_handlers_unblock()

    def __vb_handlers_block(self):
        """
        Block signals to the buttons to prevent spurious events
        """
        for idx in range(len(self.buttons)):
            self.buttons[idx].handler_block(self.button_handlers[idx])
        
    def __vb_handlers_unblock(self):
        """
        Unblock signals to the buttons
        """
        for idx in range(len(self.buttons)):
            self.buttons[idx].handler_unblock(self.button_handlers[idx])

    def __set_active_button(self, num):
        """
        Set the corresponding button active, while setting the others
        inactive
        """
        for idx in range(len(self.buttons)):
            self.buttons[idx].set_active(idx==num)

    def __disconnect_previous_page(self):
        """
        Disconnects the previous page, removing the old action groups
        and removes the old UI components.
        """
        for mergeid in self.merge_ids:
            self.uimanager.remove_ui(mergeid)
            
        if self.active_page:
            self.active_page.set_inactive()
            groups = self.active_page.get_actions()
            for grp in groups:
                if grp in self.uimanager.get_action_groups():
                    self.uimanager.remove_action_group(grp)

    def __connect_active_page(self):
        """
        Inserts the action groups associated with the current page
        into the UIManager
        """
        for grp in self.active_page.get_actions():
            self.uimanager.insert_action_group(grp, 1)

        uidef = self.active_page.ui_definition()
        self.merge_ids = [self.uimanager.add_ui_from_string(uidef)]

        for uidef in self.active_page.additional_ui_definitions():
            mergeid = self.uimanager.add_ui_from_string(uidef)
            self.merge_ids.append(mergeid)

    def __setup_navigation(self):
        """
        Initialize the navigation scheme
        """
        old_nav = self._navigation_type[self.prev_nav]
        if old_nav[0] is not None:
            old_nav[0].disable()

        page_type = self.active_page.navigation_type()
        nav_type = self._navigation_type[page_type]
        if nav_type[0] is not None:
            nav_type[0].enable()

    def change_page(self, obj, page, num=-1):
        """
        Wrapper for the __do_change_page, to prevent entering into the 
        routine while already in it.
        """
        if not self.page_is_changing:
            self.page_is_changing = True
            self.__do_change_page(num)
            self.page_is_changing = False

    def __do_change_page(self, num):
        """
        Change the page to the new page
        """
        if num == -1:
            num = self.notebook.get_current_page()

        # set button of current page active
        self.__set_active_button(num)

        if self.dbstate.open:
            
            self.__disconnect_previous_page()

            if len(self.pages) > 0:
                self.active_page = self.pages[num]
                self.active_page.set_active()
                config.set('preferences.last-view', num)
                config.save()

                self.__setup_navigation()
                self.__connect_active_page()

                self.uimanager.ensure_update()

                while gtk.events_pending():
                    gtk.main_iteration()

                self.active_page.change_page()
                if self._key:
                    self.uistate.disconnect(self._key)
                    self._key = self.uistate.connect(
                        'nameformat-changed', self.active_page.build_tree)

    def import_data(self, obj):
        """
        Imports a file
        """
        if self.dbstate.db.is_open():
            self.db_loader.import_file()
            infotxt = self.db_loader.import_info_text()
            if infotxt:
                InfoDialog(_('Import Statistics'), infotxt, self.window)
            self.__post_load()
    
    
    def __open_activate(self, obj):
        """
        Called when the Open button is clicked, opens the DbManager
        """
        from dbman import DbManager
        dialog = DbManager(self.dbstate, self.window)
        value = dialog.run()
        if value:
            (filename, title) = value
            self.db_loader.read_file(filename)
            self._post_load_newdb(filename, 'x-directory/normal', title)

    def __post_load(self):
        """
        This method is for the common UI post_load, both new files
        and added data like imports.
        """
        if self.dbstate.active :
            # clear history and fill history with first entry, active person
            self.uistate.clear_history(self.dbstate.active.handle)
        else :
            self.uistate.clear_history(None)
        self.uistate.progress.hide()

        self.dbstate.db.undo_callback = self.__change_undo_label
        self.dbstate.db.redo_callback = self.__change_redo_label
        self.__change_undo_label(None)
        self.__change_redo_label(None)
        self.dbstate.db.undo_history_callback = self.undo_history_update
        self.undo_history_close()

        self.uistate.window.window.set_cursor(None)

    def _post_load_newdb(self, filename, filetype, title=None):
        """
        The method called after load of a new database. 
        Inherit CLI method to add GUI part
        """
        self._post_load_newdb_nongui(filename, title)
        self._post_load_newdb_gui(filename, filetype, title)
        
    def _post_load_newdb_gui(self, filename, filetype, title=None):
        """
        Called after a new database is loaded to do GUI stuff
        """
        # GUI related post load db stuff
        # Update window title
        if filename[-1] == os.path.sep:
            filename = filename[:-1]
        name = os.path.basename(filename)
        if title:
            name = title

        if self.dbstate.db.readonly:
            msg =  "%s (%s) - GRAMPS" % (name, _('Read Only'))
            self.uistate.window.set_title(msg)
            self.actiongroup.set_sensitive(False)
        else:
            msg = "%s - GRAMPS" % name
            self.uistate.window.set_title(msg)
            self.actiongroup.set_sensitive(True)

        self.setup_bookmarks()
        
        self.change_page(None, None)
        self.actiongroup.set_visible(True)
        self.readonlygroup.set_visible(True)
        
        self.recent_manager.build()
        
        # Call common __post_load method for GUI update after a change
        self.__post_load()

    def __change_undo_label(self, label):
        """
        Change the UNDO label
        """
        self.uimanager.remove_action_group(self.undoactions)
        self.undoactions = gtk.ActionGroup('Undo')
        if label:
            self.undoactions.add_actions([
                ('Undo', gtk.STOCK_UNDO, label, '<control>z', None, self.undo)])
        else:
            self.undoactions.add_actions([
                ('Undo', gtk.STOCK_UNDO, _('_Undo'), 
                 '<control>z', None, self.undo)])
            self.undoactions.set_sensitive(False)
        self.uimanager.insert_action_group(self.undoactions, 1)

    def __change_redo_label(self, label):
        """
        Change the REDO label
        """
        self.uimanager.remove_action_group(self.redoactions)
        self.redoactions = gtk.ActionGroup('Redo')
        if label:
            self.redoactions.add_actions([
                ('Redo', gtk.STOCK_REDO, label, '<shift><control>z', 
                 None, self.redo)])
        else:
            self.redoactions.add_actions([
                ('Redo', gtk.STOCK_UNDO, _('_Redo'), 
                 '<shift><control>z', None, self.redo)])
            self.redoactions.set_sensitive(False)
        self.uimanager.insert_action_group(self.redoactions, 1)

    def undo_history_update(self):
        """
        This function is called to update both the state of
        the Undo History menu item (enable/disable) and
        the contents of the Undo History window.
        """
        try:
            # Try updating undo history window if it exists
            self.undo_history_window.update()
        except AttributeError:
            # Let it go: history window does not exist
            return

    def undo_history_close(self):
        """
        Closes the undo history
        """
        try:
            # Try closing undo history window if it exists
            if self.undo_history_window.opened:
                self.undo_history_window.close()
        except AttributeError:
            # Let it go: history window does not exist
            return
 
    def setup_bookmarks(self):
        """
        Initialize the bookmarks based of the database. This needs to
        be called anytime the database changes.
        """
        import Bookmarks
        self.bookmarks = Bookmarks.Bookmarks(
            self.dbstate, self.uistate, self.dbstate.db.get_bookmarks())

    def add_bookmark(self, obj):
        """
        Add a bookmark to the bookmark list
        """
        if self.dbstate.active:
            self.bookmarks.add(self.dbstate.active.get_handle())
            name = name_displayer.display(self.dbstate.active)
            self.uistate.push_message(self.dbstate, 
                                      _("%s has been bookmarked") % name)
        else:
            WarningDialog(
                _("Could Not Set a Bookmark"), 
                _("A bookmark could not be set because "
                  "no one was selected."))

    def edit_bookmarks(self, obj):
        """
        Displays the Bookmark editor
        """
        self.bookmarks.edit()

    def reports_clicked(self, obj):
        """
        Displays the Reports dialog
        """
        try:
            ReportPluginDialog(self.dbstate, self.uistate, [])
        except Errors.WindowActiveError:
            return

    def tools_clicked(self, obj):
        """
        Displays the Tools dialog
        """
        try:
            ToolPluginDialog(self.dbstate, self.uistate, [])
        except Errors.WindowActiveError:
            return          
        
    def scratchpad(self, obj):
        """
        Displays the Clipboard (was scratchpad)
        """
        import ScratchPad
        try:
            ScratchPad.ScratchPadWindow(self.dbstate, self.uistate)
        except Errors.WindowActiveError:
            return

    def undo(self, obj):
        """
        Calls the undo function on the database
        """
        self.uistate.set_busy_cursor(1)
        self.dbstate.db.undo()
        self.uistate.set_busy_cursor(0)

    def redo(self, obj):
        """
        Calls the redo function on the database
        """
        self.uistate.set_busy_cursor(1)
        self.dbstate.db.redo()
        self.uistate.set_busy_cursor(0)

    def undo_history(self, obj):
        """
        Displays the Undo history window
        """
        try:
            self.undo_history_window = UndoHistory.UndoHistory(self.dbstate, 
                                                               self.uistate)
        except Errors.WindowActiveError:
            return

    def export_data(self, obj):
        """
        Calls the ExportAssistant to export data
        """
        if self.dbstate.db.db_is_open:
            import ExportAssistant
            try:
                ExportAssistant.ExportAssistant(self.dbstate, self.uistate)
            except Errors.WindowActiveError:
                return

    def __rebuild_report_and_tool_menus(self):
        """
        Callback that rebuilds the tools and reports menu
        """
        tool_menu_list = self._pmgr.get_tool_list()
        report_menu_list = self._pmgr.get_report_list()
        self.__build_tools_menu(tool_menu_list)
        self.__build_report_menu(report_menu_list)
        self.uistate.set_relationship_class()

    def __build_tools_menu(self, tool_menu_list):
        """
        Builds a new tools menu
        """
        self.toolactions = gtk.ActionGroup('ToolWindow')
        (uidef, actions) = self.build_plugin_menu(
            'ToolsMenu', tool_menu_list, Tool.tool_categories, 
            make_tool_callback)
        self.toolactions.add_actions(actions)
        self.uistate.uimanager.add_ui_from_string(uidef)
        self.uimanager.insert_action_group(self.toolactions, 1)
        self.uistate.uimanager.ensure_update()
    
    def __build_report_menu(self, report_menu_list):
        """
        Builds a new reports menu
        """
        self.reportactions = gtk.ActionGroup('ReportWindow')
        (uidef, actions) = self.build_plugin_menu(
            'ReportsMenu', report_menu_list, ReportBase.standalone_categories, 
            make_report_callback)
        self.reportactions.add_actions(actions)
        self.uistate.uimanager.add_ui_from_string(uidef)
        self.uimanager.insert_action_group(self.reportactions, 1)
        self.uistate.uimanager.ensure_update()

    def build_plugin_menu(self, text, item_list, categories, func):
        """
        Builds a new XML description for a menu based on the item list
        """
        actions = []
        ofile = StringIO()
        ofile.write('<ui><menubar name="MenuBar"><menu action="%s">' % text)
        
        menu = gtk.Menu()
        menu.show()
    
        hash_data = {}
        for item in item_list:
            if item[9]:
                category = _UNSUPPORTED
            else:
                category = categories[item[3]]
            if category in hash_data:
                hash_data[category].append(
                    (item[0], item[1], item[2], item[4], item[3], item[10]))
            else:
                hash_data[category] = [
                    (item[0], item[1], item[2], item[4], item[3], item[10])]
                
        # Sort categories, skipping the unsupported
        catlist = [item for item in hash_data
                   if item != _UNSUPPORTED]
        catlist.sort()
        for key in catlist:
            new_key = key.replace(' ', '-')
            ofile.write('<menu action="%s">' % new_key)
            actions.append((new_key, None, key))
            lst = hash_data[key]
            lst.sort(by_menu_name)
            for name in lst:
                new_key = name[3].replace(' ', '-')
                menu_name = ("%s...") % name[2]
                ofile.write('<menuitem action="%s"/>' % new_key)
                actions.append((new_key, None, menu_name, None, None, 
                                func(name, self.dbstate, self.uistate)))
            ofile.write('</menu>')

        # If there are any unsupported items we add separator
        # and the unsupported category at the end of the menu
        if _UNSUPPORTED in hash_data:
            ofile.write('<separator/>')
            ofile.write('<menu action="%s">' % _UNSUPPORTED)
            actions.append((_UNSUPPORTED, None, _UNSUPPORTED))
            lst = hash_data[_UNSUPPORTED]
            lst.sort(by_menu_name)
            for name in lst:
                new_key = name[3].replace(' ', '-')
                ofile.write('<menuitem action="%s"/>' % new_key)
                actions.append((new_key, None, name[2], None, None, 
                                func(name, self.dbstate, self.uistate)))
            ofile.write('</menu>')

        ofile.write('</menu></menubar></ui>')
        return (ofile.getvalue(), actions)

def display_about_box(obj):
    """Display the About box."""
    about = GrampsAboutDialog()
    about.run()
    about.destroy()

def filter_toggle(obj):
    """
    Save the filter state to the config settings on change
    """
    config.set('interface.filter', obj.get_active())
    config.save()

def key_bindings(obj):
    """
    Display key bindings
    """
    GrampsDisplay.help(webpage=WIKI_HELP_PAGE_KEY)

def manual_activate(obj):
    """
    Display the GRAMPS manual
    """
    GrampsDisplay.help(webpage=WIKI_HELP_PAGE_MAN)

def report_bug_activate(obj):
    """
    Display the bug tracker web site
    """
    GrampsDisplay.url(const.URL_BUGTRACKER)

def home_page_activate(obj):
    """
    Display the GRAMPS home page
    """
    GrampsDisplay.url(const.URL_HOMEPAGE)

def mailing_lists_activate(obj):
    """
    Display the mailing list web page
    """
    GrampsDisplay.url(const.URL_MAILINGLIST)

def extra_plugins_activate(obj):
    """
    Display the wiki page with extra plugins
    """
    GrampsDisplay.url(const.URL_WIKISTRING+const.WIKI_EXTRAPLUGINS)

def faq_activate(obj):
    """
    Display FAQ
    """
    GrampsDisplay.help(webpage=WIKI_HELP_PAGE_FAQ)

def by_menu_name(first, second):
    """
    Sorts menu item lists
    """
    return cmp(first[2], second[2])

def make_report_callback(lst, dbstate, uistate):
    """
    Makes a callback for a report menu item
    """
    return lambda x: ReportBase.report(
        dbstate, uistate, dbstate.get_active_person(), 
        lst[0], lst[1], lst[2], lst[3], lst[4], lst[5])

def make_tool_callback(lst, dbstate, uistate):
    """
    Makes a callback for a tool menu item
    """
    return lambda x: Tool.gui_tool(dbstate, uistate,  
                                   lst[0], lst[1], lst[2], lst[3], lst[4], 
                                   dbstate.db.request_rebuild)
