#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2012       Gary Burton
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
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

"""
Manages the main window and the pluggable views
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from collections import defaultdict
import os
import time
import datetime
from io import StringIO
import gc

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
from gi.repository import Gtk
from gi.repository import Gdk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.cli.grampscli import CLIManager
from .user import User
from .plug import tool
from gramps.gen.plug import START
from gramps.gen.plug import REPORT
from gramps.gen.plug.report._constants import standalone_categories
from .plug import (PluginWindows, ReportPluginDialog, ToolPluginDialog)
from .plug.report import report, BookSelector
from .utils import AvailableUpdates
from .pluginmanager import GuiPluginManager
from gramps.gen.relationship import get_relationship_calculator
from .displaystate import DisplayState, RecentDocsMenu
from gramps.gen.const import (HOME_DIR, ICON, URL_BUGTRACKER, URL_HOMEPAGE,
                              URL_MAILINGLIST, URL_MANUAL_PAGE, URL_WIKISTRING,
                              WIKI_EXTRAPLUGINS, URL_BUGHOME)
from gramps.gen.constfunc import is_quartz
from gramps.gen.config import config
from gramps.gen.errors import WindowActiveError
from .dialog import ErrorDialog, WarningDialog, QuestionDialog2, InfoDialog
from .widgets import Statusbar
from .undohistory import UndoHistory
from gramps.gen.utils.file import media_path_full
from .dbloader import DbLoader
from .display import display_help, display_url
from .configure import GrampsPreferences
from .aboutdialog import GrampsAboutDialog
from .navigator import Navigator
from .views.tags import Tags
from .actiongroup import ActionGroup
from gramps.gen.lib import (Person, Surname, Family, Media, Note, Place,
                            Source, Repository, Citation, Event, EventType,
                            ChildRef)
from gramps.gui.editors import (EditPerson, EditFamily, EditMedia, EditNote,
                                EditPlace, EditSource, EditRepository,
                                EditCitation, EditEvent)
from gramps.gen.db.exceptions import DbWriteFailure
from .managedwindow import ManagedWindow

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
if is_quartz():
    try:
        import gi
        gi.require_version('GtkosxApplication', '1.0')
        from gi.repository import GtkosxApplication as QuartzApp
        _GTKOSXAPPLICATION = True
    except:
        print("Failed to import gtk_osxapplication")
        _GTKOSXAPPLICATION = False
else:
    _GTKOSXAPPLICATION = False

_UNSUPPORTED = ("Unsupported", _("Unsupported"))

UIDEFAULT = '''<ui>
<menubar name="MenuBar">
  <menu action="FileMenu">
    <menuitem action="Open"/>
    <menu action="OpenRecent">
    </menu>
    <menuitem action="Close"/>
    <separator/>
    <menuitem action="Import"/>
    <menuitem action="Export"/>
    <placeholder name="LocalExport"/>
    <menuitem action="Backup"/>
    <separator/>
    <menuitem action="Abandon"/>
    <menuitem action="Quit"/>
  </menu>
  <menu action="AddMenu">
    <menuitem action="PersonAdd"/>
    <separator/>
    <menuitem action="FamilyAdd"/>
    <separator/>
    <menuitem action="EventAdd"/>
    <separator/>
    <menuitem action="PlaceAdd"/>
    <menuitem action="SourceAdd"/>
    <menuitem action="CitationAdd"/>
    <menuitem action="RepositoryAdd"/>
    <menuitem action="MediaAdd"/>
    <menuitem action="NoteAdd"/>
  </menu>
  <menu action="EditMenu">
    <menuitem action="Undo"/>
    <menuitem action="Redo"/>
    <menuitem action="UndoHistory"/>
    <separator/>
    <placeholder name="CommonEdit"/>
    <separator/>
    <placeholder name="TagMenu"/>
    <separator/>
    <menuitem action="Clipboard"/>
    <separator/>
    <menuitem action="Preferences"/>
  </menu>
  <menu action="ViewMenu">
    <menuitem action="ConfigView"/>
    <menuitem action="Navigator"/>
    <menuitem action="Toolbar"/>
    <placeholder name="Bars"/>
    <menuitem action="Fullscreen"/>
    <separator/>
    <placeholder name="ViewsInCategory"/>
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
    <menuitem action="Books"/>
    <separator/>
    <placeholder name="P_ReportsMenu"/>
  </menu>
  <menu action="ToolsMenu">
    <placeholder name="P_ToolsMenu"/>
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
  <placeholder name="CommonEdit"/>
  <placeholder name="TagTool"/>
  <toolitem action="Clipboard"/>
  <separator/>
  <toolitem action="ConfigView"/>
  <placeholder name="ViewsInCategory"/>
  <separator/>
  <toolitem action="Reports"/>
  <toolitem action="Tools"/>
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
<accelerator action="<PRIMARY>1"/>
<accelerator action="<PRIMARY>2"/>
<accelerator action="<PRIMARY>3"/>
<accelerator action="<PRIMARY>4"/>
<accelerator action="<PRIMARY>5"/>
<accelerator action="<PRIMARY>6"/>
<accelerator action="<PRIMARY>7"/>
<accelerator action="<PRIMARY>8"/>
<accelerator action="<PRIMARY>9"/>
<accelerator action="<PRIMARY>0"/>
<accelerator action="<PRIMARY>BackSpace"/>
<accelerator action="<PRIMARY>J"/>
<accelerator action="<PRIMARY>N"/>
<accelerator action="<PRIMARY>P"/>
</ui>
'''

WIKI_HELP_PAGE_FAQ = '%s_-_FAQ' % URL_MANUAL_PAGE
WIKI_HELP_PAGE_KEY = '%s_-_Keybindings' % URL_MANUAL_PAGE
WIKI_HELP_PAGE_MAN = '%s' % URL_MANUAL_PAGE

#-------------------------------------------------------------------------
#
# ViewManager
#
#-------------------------------------------------------------------------
class ViewManager(CLIManager):
    """
    **Overview**

    The ViewManager is the session manager of the program.
    Specifically, it manages the main window of the program. It is closely tied
    into the Gtk.UIManager to control all menus and actions.

    The ViewManager controls the various Views within the Gramps programs.
    Views are organised in categories. The categories can be accessed via
    a sidebar. Within a category, the different views are accesible via the
    toolbar of view menu.

    A View is a particular way of looking a information in the Gramps main
    window. Each view is separate from the others, and has no knowledge of
    the others.

    Examples of current views include:

    - Person View
    - Relationship View
    - Family View
    - Source View

    The View Manager does not have to know the number of views, the type of
    views, or any other details about the views. It simply provides the
    method of containing each view, and has methods for creating, deleting and
    switching between the views.

    """

    def __init__(self, dbstate, view_category_order, user=None):
        """
        The viewmanager is initialised with a dbstate on which Gramps is
        working, and a fixed view_category_order, which is the order in which
        the view categories are accessible in the sidebar.
        """
        CLIManager.__init__(self, dbstate, setloader=False, user=user)
        if _GTKOSXAPPLICATION:
            self.macapp = QuartzApp.Application()
            self.macapp.set_use_quartz_accelerators(False)

        self.view_category_order = view_category_order

        #set pluginmanager to GUI one
        self._pmgr = GuiPluginManager.get_instance()
        self.merge_ids = []
        self.toolactions = None
        self.tool_menu_ui_id = None
        self.reportactions = None
        self.report_menu_ui_id = None

        self.active_page = None
        self.pages = []
        self.page_lookup = {}
        self.views = None
        self.current_views = [] # The current view in each category
        self.view_changing = False

        self.show_navigator = config.get('interface.view')
        self.show_toolbar = config.get('interface.toolbar-on')
        self.fullscreen = config.get('interface.fullscreen')

        self.__build_main_window() # sets self.uistate
        if self.user is None:
            self.user = User(error=ErrorDialog,
                             parent=self.window,
                             callback=self.uistate.pulse_progressbar,
                             uistate=self.uistate,
                             dbstate=self.dbstate)
        self.__connect_signals()
        if _GTKOSXAPPLICATION:
            self.macapp.ready()

        self.do_reg_plugins(self.dbstate, self.uistate)
        #plugins loaded now set relationship class
        self.rel_class = get_relationship_calculator()
        self.uistate.set_relationship_class()
        # Need to call after plugins have been registered
        self.uistate.connect('update-available', self.process_updates)
        self.check_for_updates()
        # Set autobackup
        self.uistate.connect('autobackup', self.autobackup)
        self.uistate.set_backup_timer()

    def check_for_updates(self):
        """
        Check for add-on updates.
        """
        howoften = config.get("behavior.check-for-addon-updates")
        update = False
        if howoften != 0: # update never if zero
            year, mon, day = list(map(
                int, config.get("behavior.last-check-for-addon-updates").split("/")))
            days = (datetime.date.today() - datetime.date(year, mon, day)).days
            if howoften == 1 and days >= 30: # once a month
                update = True
            elif howoften == 2 and days >= 7: # once a week
                update = True
            elif howoften == 3 and days >= 1: # once a day
                update = True
            elif howoften == 4: # always
                update = True

        if update:
            AvailableUpdates(self.uistate).start()

    def process_updates(self, addon_update_list):
        """
        Called when add-on updates are available.
        """
        rescan = PluginWindows.UpdateAddons(self.uistate, [],
                                            addon_update_list).rescan
        self.do_reg_plugins(self.dbstate, self.uistate, rescan=rescan)

    def _errordialog(self, title, errormessage):
        """
        Show the error.
        In the GUI, the error is shown, and a return happens
        """
        ErrorDialog(title, errormessage,
                    parent=self.uistate.window)
        return 1

    def __build_main_window(self):
        """
        Builds the GTK interface
        """
        width = config.get('interface.main-window-width')
        height = config.get('interface.main-window-height')
        horiz_position = config.get('interface.main-window-horiz-position')
        vert_position = config.get('interface.main-window-vert-position')

        self.window = Gtk.Window()
        self.window.set_icon_from_file(ICON)
        self.window.set_default_size(width, height)
        self.window.move(horiz_position, vert_position)
        #Set the mnemonic modifier on Macs to alt-ctrl so that it
        #doesn't interfere with the extended keyboard, see
        #https://gramps-project.org/bugs/view.php?id=6943
        if is_quartz():
            self.window.set_mnemonic_modifier(
                Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(vbox)
        hpane = Gtk.Paned()
        self.ebox = Gtk.EventBox()

        self.navigator = Navigator(self)
        self.ebox.add(self.navigator.get_top())
        hpane.add1(self.ebox)
        hpane.show()

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_show_tabs(False)
        self.notebook.show()
        self.__init_lists()
        self.__build_ui_manager()

        hpane.add2(self.notebook)
        self.menubar = self.uimanager.get_widget('/MenuBar')
        self.toolbar = self.uimanager.get_widget('/ToolBar')
        self.__attach_menubar(vbox)
        vbox.pack_start(self.toolbar, False, True, 0)
        vbox.pack_start(hpane, True, True, 0)
        self.statusbar = Statusbar()
        self.statusbar.show()
        vbox.pack_end(self.statusbar, False, True, 0)
        vbox.show()

        self.uistate = DisplayState(self.window, self.statusbar,
                                    self.uimanager, self)

        # Create history objects
        for nav_type in ('Person', 'Family', 'Event', 'Place', 'Source',
                         'Citation', 'Repository', 'Note', 'Media'):
            self.uistate.register(self.dbstate, nav_type, 0)

        self.dbstate.connect('database-changed', self.uistate.db_changed)

        self.tags = Tags(self.uistate, self.dbstate)

        self.sidebar_menu = self.uimanager.get_widget(
            '/MenuBar/ViewMenu/Sidebar/')

        # handle OPEN button, insert it into the toolbar. Unfortunately,
        # UIManager has no built in support for and Open Recent button

        openbtn = self.__build_open_button()
        self.uistate.set_open_widget(openbtn)
        self.toolbar.insert(openbtn, 0)

        self.recent_manager = RecentDocsMenu(
            self.uistate, self.dbstate, self._read_recent_file)
        self.recent_manager.build()

        self.db_loader = DbLoader(self.dbstate, self.uistate)

        self.__setup_navigator()

        if self.show_toolbar:
            self.toolbar.show()
        else:
            self.toolbar.hide()

        if self.fullscreen:
            self.window.fullscreen()

        self.window.set_title("%s - Gramps" % _('No Family Tree'))
        self.window.show()

    def __setup_navigator(self):
        """
        If we have enabled te sidebar, show it, and turn off the tabs. If
        disabled, hide the sidebar and turn on the tabs.
        """
        if self.show_navigator:
            self.ebox.show()
        else:
            self.ebox.hide()

    def __build_open_button(self):
        """
        Build the OPEN button. Since GTK's UIManager does not have support for
        the Open Recent button, we must build in on our own.
        """
        openbtn = Gtk.MenuToolButton()
        openbtn.set_icon_name('gramps')
        openbtn.connect('clicked', self.__open_activate)
        openbtn.set_sensitive(False)
        openbtn.set_tooltip_text(_("Connect to a recent database"))
        openbtn.show()
        return openbtn

    def __connect_signals(self):
        """
        Connects the signals needed
        """
        self.del_event = self.window.connect('delete-event', self.quit)
        self.notebook.connect('switch-page', self.view_changed)
        if _GTKOSXAPPLICATION:
            self.macapp.connect('NSApplicationWillTerminate', self.quit)

    def __init_lists(self):
        """
        Initialize the actions lists for the UIManager
        """
        self._file_action_list = [
            ('FileMenu', None, _('_Family Trees')),
            ('Open', 'gramps-db', _('_Manage Family Trees...'), "<PRIMARY>o",
             _("Manage databases"), self.__open_activate),
            ('OpenRecent', None, _('Open _Recent'), None,
             _("Open an existing database")),
            ('Quit', 'application-exit', _('_Quit'), "<PRIMARY>q", None,
             self.quit),
            ('ViewMenu', None, _('_View')),
            ('EditMenu', None, _('_Edit')),
            ('Preferences', 'preferences-system', _('_Preferences...'), None,
             None, self.preferences_activate),
            ('HelpMenu', None, _('_Help')),
            ('HomePage', None, _('Gramps _Home Page'), None, None,
             home_page_activate),
            ('MailingLists', None, _('Gramps _Mailing Lists'), None, None,
             mailing_lists_activate),
            ('ReportBug', None, _('_Report a Bug'), None, None,
             report_bug_activate),
            ('ExtraPlugins', None, _('_Extra Reports/Tools'), None, None,
             extra_plugins_activate),
            ('About', 'help-about', _('_About'), None, None,
             self.display_about_box),
            ('PluginStatus', None, _('_Plugin Manager'), None, None,
             self.__plugin_status),
            ('FAQ', None, _('_FAQ'), None, None, faq_activate),
            ('KeyBindings', None, _('_Key Bindings'), None, None, key_bindings),
            ('UserManual', 'help-browser', _('_User Manual'), 'F1', None,
             manual_activate),
            ('TipOfDay', None, _('Tip of the Day'), None, None,
             self.tip_of_day_activate),
            ]

        self._readonly_action_list = [
            ('Close', None, _('_Close'), "<control>w",
             _("Close the current database"), self.close_database),
            ('Export', 'gramps-export', _('_Export...'), "<PRIMARY>e", None,
             self.export_data),
            ('Backup', None, _("Make Backup..."), None,
             _("Make a Gramps XML backup of the database"), self.quick_backup),
            ('Abandon', 'document-revert',
             _('_Abandon Changes and Quit'), None, None, self.abort),
            ('Reports', 'gramps-reports', _('_Reports'), None,
             _("Open the reports dialog"), self.reports_clicked),
            ('GoMenu', None, _('_Go')),
            ('ReportsMenu', None, _('_Reports')),
            ('Books', None, _('Books...'), None, None, self.run_book),
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
            ('<PRIMARY>1', None, '<PRIMARY>1', "<PRIMARY>1", None,
             self.__gocat),
            ('<PRIMARY>2', None, '<PRIMARY>2', "<PRIMARY>2", None,
             self.__gocat),
            ('<PRIMARY>3', None, '<PRIMARY>3', "<PRIMARY>3", None,
             self.__gocat),
            ('<PRIMARY>4', None, '<PRIMARY>4', "<PRIMARY>4", None,
             self.__gocat),
            ('<PRIMARY>5', None, '<PRIMARY>5', "<PRIMARY>5", None,
             self.__gocat),
            ('<PRIMARY>6', None, '<PRIMARY>6', "<PRIMARY>6", None,
             self.__gocat),
            ('<PRIMARY>7', None, '<PRIMARY>7', "<PRIMARY>7", None,
             self.__gocat),
            ('<PRIMARY>8', None, '<PRIMARY>8', "<PRIMARY>8", None,
             self.__gocat),
            ('<PRIMARY>9', None, '<PRIMARY>9', "<PRIMARY>9", None,
             self.__gocat),
            ('<PRIMARY>0', None, '<PRIMARY>0', "<PRIMARY>0", None,
             self.__gocat),
            # NOTE: CTRL+ALT+NUMBER is set in src/plugins/sidebar/cat...py
            ('<PRIMARY>BackSpace', None, '<PRIMARY>BackSpace',
             "<PRIMARY>BackSpace", None, self.__keypress),
            ('<PRIMARY>Delete', None, '<PRIMARY>Delete',
             "<PRIMARY>Delete", None, self.__keypress),
            ('<PRIMARY>Insert', None, '<PRIMARY>Insert',
             "<PRIMARY>Insert", None, self.__keypress),
            ('F12', None, 'F12', "F12", None, self.__keypress),
            ('<PRIMARY>J', None, '<PRIMARY>J',
             "<PRIMARY>J", None, self.__keypress),
            ('<PRIMARY>N', None, '<PRIMARY>N', "<PRIMARY>N", None,
             self.__next_view),
            ('<PRIMARY>P', None, '<PRIMARY>P', "<PRIMARY>P", None,
             self.__prev_view),
            ]

        self._action_action_list = [
            ('Clipboard', 'edit-paste', _('Clip_board'), "<PRIMARY>b",
             _("Open the Clipboard dialog"), self.clipboard),
            ('AddMenu', None, _('_Add')),
            #('AddNewMenu', None, _('New')),
            ('PersonAdd', None, _('Person'), "<shift><Alt>p", None,
             self.add_new_person),
            ('FamilyAdd', None, _('Family'), "<shift><Alt>f", None,
             self.add_new_family),
            ('EventAdd', None, _('Event'), "<shift><Alt>e", None,
             self.add_new_event),
            ('PlaceAdd', None, _('Place'), "<shift><Alt>l", None,
             self.add_new_place),
            ('SourceAdd', None, _('Source'), "<shift><Alt>s", None,
             self.add_new_source),
            ('CitationAdd', None, _('Citation'), "<shift><Alt>c", None,
             self.add_new_citation),
            ('RepositoryAdd', None, _('Repository'), "<shift><Alt>r", None,
             self.add_new_repository),
            ('MediaAdd', None, _('Media'), "<shift><Alt>m", None,
             self.add_new_media),
            ('NoteAdd', None, _('Note'), "<shift><Alt>n", None,
             self.add_new_note),
            #--------------------------------------
            ('Import', 'gramps-import', _('_Import...'), "<PRIMARY>i", None,
             self.import_data),
            ('Tools', 'gramps-tools', _('_Tools'), None,
             _("Open the tools dialog"), self.tools_clicked),
            ('BookMenu', None, _('_Bookmarks')),
            ('ToolsMenu', None, _('_Tools')),
            ('ConfigView', 'gramps-config', _('_Configure...'),
             '<shift><PRIMARY>c', _('Configure the active view'),
             self.config_view),
            ]

        self._file_toggle_action_list = [
            ('Navigator', None, _('_Navigator'), "<PRIMARY>m", None,
             self.navigator_toggle, self.show_navigator),
            ('Toolbar', None, _('_Toolbar'), None, None, self.toolbar_toggle,
             self.show_toolbar),
            ('Fullscreen', None, _('F_ull Screen'), "F11", None,
             self.fullscreen_toggle, self.fullscreen),
            ]

        self._undo_action_list = [
            ('Undo', 'edit-undo', _('_Undo'), '<PRIMARY>z', None,
             self.undo),
            ]

        self._redo_action_list = [
            ('Redo', 'edit-redo', _('_Redo'), '<shift><PRIMARY>z', None,
             self.redo),
            ]

        self._undo_history_action_list = [
            ('UndoHistory', 'gramps-undo-history',
             _('Undo History...'), "<PRIMARY>H", None, self.undo_history),
            ]

    def run_book(self, action):
        """
        Run a book.
        """
        try:
            BookSelector(self.dbstate, self.uistate)
        except WindowActiveError:
            return

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

    def __gocat(self, action):
        """
        Callback that is called on ctrl+number press. It moves to the
        requested category like __next_view/__prev_view. 0 is 10
        """
        cat = int(action.get_name()[-1])
        if cat == 0:
            cat = 10
        cat -= 1
        if cat >= len(self.current_views):
            #this view is not present
            return False
        self.goto_page(cat, None)

    def __next_view(self, action):
        """
        Callback that is called when the next category action is selected.  It
        selects the next category as the active category. If we reach the end,
        we wrap around to the first.
        """
        curpage = self.notebook.get_current_page()
        #find cat and view of the current page
        for key in self.page_lookup:
            if self.page_lookup[key] == curpage:
                cat_num, view_num = key
                break
        #now go to next category
        if cat_num >= len(self.current_views)-1:
            self.goto_page(0, None)
        else:
            self.goto_page(cat_num+1, None)

    def __prev_view(self, action):
        """
        Callback that is called when the previous category action is selected.
        It selects the previous category as the active category. If we reach
        the beginning of the list, we wrap around to the last.
        """
        curpage = self.notebook.get_current_page()
        #find cat and view of the current page
        for key in self.page_lookup:
            if self.page_lookup[key] == curpage:
                cat_num, view_num = key
                break
        #now go to next category
        if cat_num > 0:
            self.goto_page(cat_num-1, None)
        else:
            self.goto_page(len(self.current_views)-1, None)

    def init_interface(self):
        """
        Initialize the interface.
        """
        self.views = self.get_available_views()
        defaults = views_to_show(self.views,
                                 config.get('preferences.use-last-view'))
        self.current_views = defaults[2]

        self.navigator.load_plugins(self.dbstate, self.uistate)

        self.goto_page(defaults[0], defaults[1])

        self.fileactions.set_sensitive(False)
        self.__build_tools_menu(self._pmgr.get_reg_tools())
        self.__build_report_menu(self._pmgr.get_reg_reports())
        self._pmgr.connect('plugins-reloaded',
                           self.__rebuild_report_and_tool_menus)
        self.fileactions.set_sensitive(True)
        self.uistate.widget.set_sensitive(True)
        if not self.file_loaded:
            self.actiongroup.set_sensitive(False)
            self.readonlygroup.set_sensitive(False)
            self.undoactions.set_sensitive(False)
            self.redoactions.set_sensitive(False)
            self.undohistoryactions.set_sensitive(False)
            self.actiongroup.set_visible(False)
            self.readonlygroup.set_visible(False)
            self.undoactions.set_visible(False)
            self.redoactions.set_visible(False)
            self.undohistoryactions.set_visible(False)
        self.uimanager.ensure_update()
        config.connect("interface.statusbar", self.__statusbar_key_update)

    def __statusbar_key_update(self, client, cnxn_id, entry, data):
        """
        Callback function for statusbar key update
        """
        self.uistate.modify_statusbar(self.dbstate)

    def post_init_interface(self, show_manager=True):
        """
        Showing the main window is deferred so that
        ArgHandler can work without it always shown
        """
        self.window.show()
        if not self.dbstate.is_open() and show_manager:
            self.__open_activate(None)

    def do_reg_plugins(self, dbstate, uistate, rescan=False):
        """
        Register the plugins at initialization time. The plugin status window
        is opened on an error if the user has requested.
        """
        # registering plugins
        self.uistate.status_text(_('Registering plugins...'))
        error = CLIManager.do_reg_plugins(self, dbstate, uistate,
                                          rescan=rescan)

        #  get to see if we need to open the plugin status window
        if error and config.get('behavior.pop-plugin-status'):
            self.__plugin_status()

        self.uistate.push_message(self.dbstate, _('Ready'))

    def close_database(self, action=None, make_backup=True):
        """
        Close the database
        """
        self.dbstate.no_database()
        self.post_close_db()

    def no_del_event(self, *obj):
        """ Routine to prevent window destroy with default handler if user
        hits 'x' multiple times. """
        return True

    def quit(self, *obj):
        """
        Closes out the program, backing up data
        """
        # mark interface insenstitive to prevent unexpected events
        self.uistate.set_sensitive(False)
        # the following prevents reentering quit if user hits 'x' again
        self.window.disconnect(self.del_event)
        # the following prevents premature closing of main window if user
        # hits 'x' multiple times.
        self.window.connect('delete-event', self.no_del_event)

        # backup data
        if config.get('database.backup-on-exit'):
            self.autobackup()

        # close the database
        if self.dbstate.is_open():
            self.dbstate.db.close(user=self.user)

        # have each page save anything, if they need to:
        self.__delete_pages()

        # save the current window size
        (width, height) = self.window.get_size()
        config.set('interface.main-window-width', width)
        config.set('interface.main-window-height', height)
        # save the current window position
        (horiz_position, vert_position) = self.window.get_position()
        config.set('interface.main-window-horiz-position', horiz_position)
        config.set('interface.main-window-vert-position', vert_position)
        config.save()
        Gtk.main_quit()

    def abort(self, obj=None):
        """
        Abandon changes and quit.
        """
        if self.dbstate.db.abort_possible:

            dialog = QuestionDialog2(
                _("Abort changes?"),
                _("Aborting changes will return the database to the state "
                  "it was before you started this editing session."),
                _("Abort changes"),
                _("Cancel"),
                parent=self.uistate.window)

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
                  'limit.'), parent=self.uistate.window)

    def __init_action_group(self, name, actions, sensitive=True, toggles=None):
        """
        Initialize an action group for the UIManager
        """
        new_group = ActionGroup(name=name)
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
        self.uimanager = Gtk.UIManager()

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

    def __attach_menubar(self, vbox):
        """
        Attach the menubar
        """
        vbox.pack_start(self.menubar, False, True, 0)
        if _GTKOSXAPPLICATION:
            self.menubar.hide()
            quit_item = self.uimanager.get_widget("/MenuBar/FileMenu/Quit")
            about_item = self.uimanager.get_widget("/MenuBar/HelpMenu/About")
            prefs_item = self.uimanager.get_widget(
                "/MenuBar/EditMenu/Preferences")
            self.macapp.set_menu_bar(self.menubar)
            self.macapp.insert_app_menu_item(about_item, 0)
            self.macapp.insert_app_menu_item(prefs_item, 1)

    def preferences_activate(self, obj):
        """
        Open the preferences dialog.
        """
        try:
            GrampsPreferences(self.uistate, self.dbstate)
        except WindowActiveError:
            return

    def tip_of_day_activate(self, obj):
        """
        Display Tip of the day
        """
        from .tipofday import TipOfDay
        TipOfDay(self.uistate)

    def __plugin_status(self, obj=None, data=None):
        """
        Display plugin status dialog
        """
        try:
            PluginWindows.PluginStatus(self.dbstate, self.uistate, [])
        except WindowActiveError:
            pass

    def navigator_toggle(self, obj, data=None):
        """
        Set the sidebar based on the value of the toggle button. Save the
        results in the configuration settings
        """
        if obj.get_active():
            self.ebox.show()
            config.set('interface.view', True)
            self.show_navigator = True
        else:
            self.ebox.hide()
            config.set('interface.view', False)
            self.show_navigator = False
        config.save()

    def toolbar_toggle(self, obj, data=None):
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

    def fullscreen_toggle(self, obj, data=None):
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

    def get_views(self):
        """
        Return the view definitions.
        """
        return self.views

    def goto_page(self, cat_num, view_num):
        """
        Create the page if it doesn't exist and make it the current page.
        """
        if view_num is None:
            view_num = self.current_views[cat_num]
        else:
            self.current_views[cat_num] = view_num

        page_num = self.page_lookup.get((cat_num, view_num))
        if page_num is None:
            page_def = self.views[cat_num][view_num]
            page_num = self.notebook.get_n_pages()
            self.page_lookup[(cat_num, view_num)] = page_num
            self.__create_page(page_def[0], page_def[1])

        self.notebook.set_current_page(page_num)
        return self.pages[page_num]

    def get_category(self, cat_name):
        """
        Return the category number from the given category name.
        """
        for cat_num, cat_views in enumerate(self.views):
            if cat_name == cat_views[0][0].category[1]:
                return cat_num
        return None

    def __create_dummy_page(self, pdata, error):
        """ Create a dummy page """
        from .views.pageview import DummyPage
        return DummyPage(pdata.name, pdata, self.dbstate, self.uistate,
                         _("View failed to load. Check error output."), error)

    def __create_page(self, pdata, page_def):
        """
        Create a new page and set it as the current page.
        """
        try:
            page = page_def(pdata, self.dbstate, self.uistate)
        except:
            import traceback
            LOG.warning("View '%s' failed to load.", pdata.id)
            traceback.print_exc()
            page = self.__create_dummy_page(pdata, traceback.format_exc())

        try:
            page_display = page.get_display()
        except:
            import traceback
            print("ERROR: '%s' failed to create view" % pdata.name)
            traceback.print_exc()
            page = self.__create_dummy_page(pdata, traceback.format_exc())
            page_display = page.get_display()

        page.define_actions()
        page.post()

        self.pages.append(page)

        # create icon/label for notebook tab (useful for debugging)
        hbox = Gtk.Box()
        image = Gtk.Image()
        image.set_from_icon_name(page.get_stock(), Gtk.IconSize.MENU)
        hbox.pack_start(image, False, True, 0)
        hbox.add(Gtk.Label(label=pdata.name))
        hbox.show_all()
        page_num = self.notebook.append_page(page.get_display(), hbox)
        if not self.file_loaded:
            self.actiongroup.set_sensitive(False)
            self.readonlygroup.set_sensitive(False)
            self.undoactions.set_sensitive(False)
            self.redoactions.set_sensitive(False)
            self.undohistoryactions.set_sensitive(False)
            self.actiongroup.set_visible(False)
            self.readonlygroup.set_visible(False)
            self.undoactions.set_visible(False)
            self.redoactions.set_visible(False)
            self.undohistoryactions.set_visible(False)
        self.uimanager.ensure_update()
        return page

    def view_changed(self, notebook, page, page_num):
        """
        Called when the notebook page is changed.
        """
        if self.view_changing:
            return
        self.view_changing = True

        cat_num = view_num = None
        for key in self.page_lookup:
            if self.page_lookup[key] == page_num:
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

        self.navigator.view_changed(cat_num, view_num)
        self.__change_page(page_num)
        self.view_changing = False

    def __change_page(self, page_num):
        """
        Perform necessary actions when a page is changed.
        """
        if not self.dbstate.is_open():
            return

        self.__disconnect_previous_page()

        self.active_page = self.pages[page_num]
        self.active_page.set_active()
        self.__connect_active_page(page_num)

        self.uimanager.ensure_update()
        if _GTKOSXAPPLICATION:
            self.macapp.sync_menubar()

        while Gtk.events_pending():
            Gtk.main_iteration()

        self.active_page.change_page()

    def __delete_pages(self):
        """
        Calls on_delete() for each view
        """
        for page in self.pages:
            page.on_delete()

    def __disconnect_previous_page(self):
        """
        Disconnects the previous page, removing the old action groups
        and removes the old UI components.
        """
        list(map(self.uimanager.remove_ui, self.merge_ids))

        if self.active_page is not None:
            self.active_page.set_inactive()
            groups = self.active_page.get_actions()
            for grp in groups:
                if grp in self.uimanager.get_action_groups():
                    self.uimanager.remove_action_group(grp)
            self.active_page = None

    def __connect_active_page(self, page_num):
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

        configaction = self.actiongroup.get_action('ConfigView')
        if self.active_page.can_configure():
            configaction.set_sensitive(True)
        else:
            configaction.set_sensitive(False)

    def import_data(self, obj):
        """
        Imports a file
        """
        if self.dbstate.is_open():
            self.db_loader.import_file()
            infotxt = self.db_loader.import_info_text()
            if infotxt:
                InfoDialog(_('Import Statistics'), infotxt,
                           parent=self.window)
            self.__post_load()

    def __open_activate(self, obj):
        """
        Called when the Open button is clicked, opens the DbManager
        """
        from .dbman import DbManager
        dialog = DbManager(self.uistate, self.dbstate, self, self.window)
        value = dialog.run()
        if value:
            if self.dbstate.is_open():
                self.dbstate.db.close(user=self.user)
            (filename, title) = value
            self.db_loader.read_file(filename)
            if self.dbstate.db.is_open():
                self._post_load_newdb(filename, 'x-directory/normal', title)
        else:
            if dialog.after_change != "":
                # We change the title of the main window.
                old_title = self.uistate.window.get_title()
                if old_title:
                    delim = old_title.find(' - ')
                    tit1 = old_title[:delim]
                    tit2 = old_title[delim:]
                    new_title = dialog.after_change
                    if '<=' in tit2:
                        ## delim2 = tit2.find('<=') + 3
                        ## tit3 = tit2[delim2:-1]
                        new_title += tit2.replace(']', '') + ' => ' + tit1 + ']'
                    else:
                        new_title += tit2 + ' <= [' + tit1 + ']'
                    self.uistate.window.set_title(new_title)

    def __post_load(self):
        """
        This method is for the common UI post_load, both new files
        and added data like imports.
        """
        self.dbstate.db.undo_callback = self.__change_undo_label
        self.dbstate.db.redo_callback = self.__change_redo_label
        self.__change_undo_label(None)
        self.__change_redo_label(None)
        self.dbstate.db.undo_history_callback = self.undo_history_update
        self.undo_history_close()

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

        rw = not self.dbstate.db.readonly
        if rw:
            msg = "%s - Gramps" % name
        else:
            msg = "%s (%s) - Gramps" % (name, _('Read Only'))
        self.uistate.window.set_title(msg)

        self.__change_page(self.notebook.get_current_page())
        self.actiongroup.set_visible(rw)
        self.readonlygroup.set_visible(True)
        self.undoactions.set_visible(rw)
        self.redoactions.set_visible(rw)
        self.undohistoryactions.set_visible(rw)
        self.actiongroup.set_sensitive(rw)
        self.readonlygroup.set_sensitive(True)
        self.undoactions.set_sensitive(rw)
        self.redoactions.set_sensitive(rw)
        self.undohistoryactions.set_sensitive(rw)

        self.recent_manager.build()

        # Call common __post_load method for GUI update after a change
        self.__post_load()

    def post_close_db(self):
        """
        Called after a database is closed to do GUI stuff.
        """
        self.undo_history_close()
        self.uistate.window.set_title("%s - Gramps" % _('No Family Tree'))
        self.actiongroup.set_sensitive(False)
        self.readonlygroup.set_sensitive(False)
        self.undohistoryactions.set_sensitive(False)
        self.uistate.clear_filter_results()
        self.__disconnect_previous_page()
        self.actiongroup.set_visible(False)
        self.readonlygroup.set_visible(False)
        self.undoactions.set_visible(False)
        self.redoactions.set_visible(False)
        self.undohistoryactions.set_visible(False)
        self.uimanager.ensure_update()
        config.set('paths.recent-file', '')
        config.save()

    def enable_menu(self, enable):
        """ Enable/disable the menues.  Used by the dbloader for import to
        prevent other operations during import.  Needed because simpler methods
        don't work under Gnome with application menus at top of screen (instead
        of Gramps window).
        Note: enable must be set to False on first call.
        """
        if not enable:
            self.action_st = (
                self.actiongroup.get_sensitive(),
                self.readonlygroup.get_sensitive(),
                self.undoactions.get_sensitive(),
                self.redoactions.get_sensitive(),
                self.undohistoryactions.get_sensitive(),
                self.fileactions.get_sensitive(),
                self.toolactions.get_sensitive(),
                self.reportactions.get_sensitive(),
                self.recent_manager.action_group.get_sensitive())
            self.actiongroup.set_sensitive(enable)
            self.readonlygroup.set_sensitive(enable)
            self.undoactions.set_sensitive(enable)
            self.redoactions.set_sensitive(enable)
            self.undohistoryactions.set_sensitive(enable)
            self.fileactions.set_sensitive(enable)
            self.toolactions.set_sensitive(enable)
            self.reportactions.set_sensitive(enable)
            self.recent_manager.action_group.set_sensitive(enable)
        else:
            self.actiongroup.set_sensitive(self.action_st[0])
            self.readonlygroup.set_sensitive(self.action_st[1])
            self.undoactions.set_sensitive(self.action_st[2])
            self.redoactions.set_sensitive(self.action_st[3])
            self.undohistoryactions.set_sensitive(self.action_st[4])
            self.fileactions.set_sensitive(self.action_st[5])
            self.toolactions.set_sensitive(self.action_st[6])
            self.reportactions.set_sensitive(self.action_st[7])
            self.recent_manager.action_group.set_sensitive(self.action_st[8])

    def __change_undo_label(self, label):
        """
        Change the UNDO label
        """
        self.uimanager.remove_action_group(self.undoactions)
        self.undoactions = Gtk.ActionGroup(name='Undo')
        if label:
            self.undoactions.add_actions([
                ('Undo', 'edit-undo', label, '<PRIMARY>z', None, self.undo)])
        else:
            self.undoactions.add_actions([
                ('Undo', 'edit-undo', _('_Undo'),
                 '<PRIMARY>z', None, self.undo)])
            self.undoactions.set_sensitive(False)
        self.uimanager.insert_action_group(self.undoactions, 1)

    def __change_redo_label(self, label):
        """
        Change the REDO label
        """
        self.uimanager.remove_action_group(self.redoactions)
        self.redoactions = Gtk.ActionGroup(name='Redo')
        if label:
            self.redoactions.add_actions([
                ('Redo', 'edit-redo', label, '<shift><PRIMARY>z',
                 None, self.redo)])
        else:
            self.redoactions.add_actions([
                ('Redo', 'edit-undo', _('_Redo'),
                 '<shift><PRIMARY>z', None, self.redo)])
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

    def quick_backup(self, obj):
        """
        Make a quick XML back with or without media.
        """
        try:
            QuickBackup(self.dbstate, self.uistate, self.user)
        except WindowActiveError:
            return

    def autobackup(self):
        """
        Backup the current family tree.
        """
        if self.dbstate.db.is_open() and self.dbstate.db.has_changed:
            self.uistate.set_busy_cursor(True)
            self.uistate.progress.show()
            self.uistate.push_message(self.dbstate, _("Autobackup..."))
            try:
                self.__backup()
            except DbWriteFailure as msg:
                self.uistate.push_message(self.dbstate,
                                          _("Error saving backup data"))
            self.uistate.set_busy_cursor(False)
            self.uistate.progress.hide()

    def __backup(self):
        """
        Backup database to a Gramps XML file.
        """
        from gramps.plugins.export.exportxml import XmlWriter
        backup_path = config.get('database.backup-path')
        compress = config.get('database.compress-backup')
        writer = XmlWriter(self.dbstate.db, self.user, strip_photos=0,
                           compress=compress)
        timestamp = '{0:%Y-%m-%d-%H-%M-%S}'.format(datetime.datetime.now())
        backup_name = "%s-%s.gramps" % (self.dbstate.db.get_dbname(),
                                        timestamp)
        filename = os.path.join(backup_path, backup_name)
        writer.write(filename)

    def reports_clicked(self, obj):
        """
        Displays the Reports dialog
        """
        try:
            ReportPluginDialog(self.dbstate, self.uistate, [])
        except WindowActiveError:
            return

    def tools_clicked(self, obj):
        """
        Displays the Tools dialog
        """
        try:
            ToolPluginDialog(self.dbstate, self.uistate, [])
        except WindowActiveError:
            return

    def clipboard(self, obj):
        """
        Displays the Clipboard
        """
        from .clipboard import ClipboardWindow
        try:
            ClipboardWindow(self.dbstate, self.uistate)
        except WindowActiveError:
            return

    # ---------------Add new xxx --------------------------------
    def add_new_person(self, obj):
        """
        Add a new person to the database.  (Global keybinding)
        """
        person = Person()
        #the editor requires a surname
        person.primary_name.add_surname(Surname())
        person.primary_name.set_primary_surname(0)

        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except WindowActiveError:
            pass

    def add_new_family(self, obj):
        """
        Add a new family to the database.  (Global keybinding)
        """
        family = Family()
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass

    def add_new_event(self, obj):
        """
        Add a new custom/unknown event (Note you type first letter of event)
        """
        try:
            event = Event()
            event.set_type(EventType.UNKNOWN)
            EditEvent(self.dbstate, self.uistate, [], event)
        except WindowActiveError:
            pass

    def add_new_place(self, obj):
        """Add a new place to the place list"""
        try:
            EditPlace(self.dbstate, self.uistate, [], Place())
        except WindowActiveError:
            pass

    def add_new_source(self, obj):
        """Add a new source to the source list"""
        try:
            EditSource(self.dbstate, self.uistate, [], Source())
        except WindowActiveError:
            pass

    def add_new_repository(self, obj):
        """Add a new repository to the repository list"""
        try:
            EditRepository(self.dbstate, self.uistate, [], Repository())
        except WindowActiveError:
            pass

    def add_new_citation(self, obj):
        """
        Add a new citation
        """
        try:
            EditCitation(self.dbstate, self.uistate, [], Citation())
        except WindowActiveError:
            pass

    def add_new_media(self, obj):
        """Add a new media object to the media list"""
        try:
            EditMedia(self.dbstate, self.uistate, [], Media())
        except WindowActiveError:
            pass

    def add_new_note(self, obj):
        """Add a new note to the note list"""
        try:
            EditNote(self.dbstate, self.uistate, [], Note())
        except WindowActiveError:
            pass
    # ------------------------------------------------------------------------

    def config_view(self, obj):
        """
        Displays the configuration dialog for the active view
        """
        self.active_page.configure()

    def undo(self, obj):
        """
        Calls the undo function on the database
        """
        self.uistate.set_busy_cursor(True)
        self.dbstate.db.undo()
        self.uistate.set_busy_cursor(False)

    def redo(self, obj):
        """
        Calls the redo function on the database
        """
        self.uistate.set_busy_cursor(True)
        self.dbstate.db.redo()
        self.uistate.set_busy_cursor(False)

    def undo_history(self, obj):
        """
        Displays the Undo history window
        """
        try:
            self.undo_history_window = UndoHistory(self.dbstate, self.uistate)
        except WindowActiveError:
            return

    def export_data(self, obj):
        """
        Calls the ExportAssistant to export data
        """
        if self.dbstate.is_open():
            from .plug.export import ExportAssistant
            try:
                ExportAssistant(self.dbstate, self.uistate)
            except WindowActiveError:
                return

    def __rebuild_report_and_tool_menus(self):
        """
        Callback that rebuilds the tools and reports menu
        """
        self.__build_tools_menu(self._pmgr.get_reg_tools())
        self.__build_report_menu(self._pmgr.get_reg_reports())
        self.uistate.set_relationship_class()

    def __build_tools_menu(self, tool_menu_list):
        """
        Builds a new tools menu
        """
        if self.toolactions:
            self.uistate.uimanager.remove_action_group(self.toolactions)
            self.uistate.uimanager.remove_ui(self.tool_menu_ui_id)
        self.toolactions = Gtk.ActionGroup(name='ToolWindow')
        (uidef, actions) = self.build_plugin_menu(
            'ToolsMenu', tool_menu_list, tool.tool_categories,
            make_plugin_callback)
        self.toolactions.add_actions(actions)
        self.tool_menu_ui_id = self.uistate.uimanager.add_ui_from_string(uidef)
        self.uimanager.insert_action_group(self.toolactions, 1)
        self.uistate.uimanager.ensure_update()

    def __build_report_menu(self, report_menu_list):
        """
        Builds a new reports menu
        """
        if self.reportactions:
            self.uistate.uimanager.remove_action_group(self.reportactions)
            self.uistate.uimanager.remove_ui(self.report_menu_ui_id)
        self.reportactions = Gtk.ActionGroup(name='ReportWindow')
        (udef, actions) = self.build_plugin_menu(
            'ReportsMenu', report_menu_list, standalone_categories,
            make_plugin_callback)
        self.reportactions.add_actions(actions)
        self.report_menu_ui_id = self.uistate.uimanager.add_ui_from_string(udef)
        self.uimanager.insert_action_group(self.reportactions, 1)
        self.uistate.uimanager.ensure_update()

    def build_plugin_menu(self, text, item_list, categories, func):
        """
        Builds a new XML description for a menu based on the list of plugindata
        """
        actions = []
        ofile = StringIO()
        ofile.write('<ui><menubar name="MenuBar"><menu action="%s">'
                    '<placeholder name="%s">' % (text, 'P_'+ text))

        menu = Gtk.Menu()
        menu.show()

        hash_data = defaultdict(list)
        for pdata in item_list:
            if not pdata.supported:
                category = _UNSUPPORTED
            else:
                category = categories[pdata.category]
            hash_data[category].append(pdata)

        # Sort categories, skipping the unsupported
        catlist = sorted(item for item in hash_data if item != _UNSUPPORTED)

        for key in catlist:
            new_key = key[0].replace(' ', '-')
            ofile.write('<menu action="%s">' % new_key)
            actions.append((new_key, None, key[1]))
            pdatas = hash_data[key]
            pdatas.sort(key=lambda x: x.name)
            for pdata in pdatas:
                new_key = pdata.id.replace(' ', '-')
                menu_name = ("%s...") % pdata.name
                ofile.write('<menuitem action="%s"/>' % new_key)
                actions.append((new_key, None, menu_name, None, None,
                                func(pdata, self.dbstate, self.uistate)))
            ofile.write('</menu>')

        # If there are any unsupported items we add separator
        # and the unsupported category at the end of the menu
        if _UNSUPPORTED in hash_data:
            ofile.write('<separator/>')
            ofile.write('<menu action="%s">' % _UNSUPPORTED[0])
            actions.append((_UNSUPPORTED[0], None, _UNSUPPORTED[1]))
            pdatas = hash_data[_UNSUPPORTED]
            pdatas.sort(key=lambda x: x.name)
            for pdata in pdatas:
                new_key = pdata.id.replace(' ', '-')
                menu_name = ("%s...") % pdata.name
                ofile.write('<menuitem action="%s"/>' % new_key)
                actions.append((new_key, None, menu_name, None, None,
                                func(pdata, self.dbstate, self.uistate)))
            ofile.write('</menu>')

        ofile.write('</placeholder></menu></menubar></ui>')
        return (ofile.getvalue(), actions)

    def display_about_box(self, obj):
        """Display the About box."""
        about = GrampsAboutDialog(self.uistate.window)
        about.run()
        about.destroy()

    def get_available_views(self):
        """
        Query the views and determine what views to show and in which order

        :Returns: a list of lists containing tuples (view_id, viewclass)
        """
        pmgr = GuiPluginManager.get_instance()
        view_list = pmgr.get_reg_views()
        viewstoshow = defaultdict(list)
        for pdata in view_list:
            mod = pmgr.load_plugin(pdata)
            if not mod or not hasattr(mod, pdata.viewclass):
                #import of plugin failed
                try:
                    lasterror = pmgr.get_fail_list()[-1][1][1]
                except:
                    lasterror = '*** No error found, '
                    lasterror += 'probably error in gpr.py file ***'
                ErrorDialog(
                    _('Failed Loading View'),
                    _('The view %(name)s did not load and reported an error.'
                      '\n\n%(error_msg)s\n\n'
                      'If you are unable to fix the fault yourself then you '
                      'can submit a bug at %(gramps_bugtracker_url)s '
                      'or contact the view author (%(firstauthoremail)s).\n\n'
                      'If you do not want Gramps to try and load this view '
                      'again, you can hide it by using the Plugin Manager '
                      'on the Help menu.'
                     ) % {'name': pdata.name,
                          'gramps_bugtracker_url': URL_BUGHOME,
                          'firstauthoremail': pdata.authors_email[0]
                                              if pdata.authors_email else '...',
                          'error_msg': lasterror},
                    parent=self.uistate.window)
                continue
            viewclass = getattr(mod, pdata.viewclass)

            # pdata.category is (string, trans-string):
            if pdata.order == START:
                viewstoshow[pdata.category[0]].insert(0, (pdata, viewclass))
            else:
                viewstoshow[pdata.category[0]].append((pdata, viewclass))

        # First, get those in order defined, if exists:
        resultorder = [viewstoshow[cat]
                       for cat in config.get("interface.view-categories")
                       if cat in viewstoshow]

        # Next, get the rest in some order:
        resultorder.extend(viewstoshow[cat]
                           for cat in sorted(viewstoshow.keys())
                           if viewstoshow[cat] not in resultorder)
        return resultorder

def key_bindings(obj):
    """
    Display key bindings
    """
    display_help(webpage=WIKI_HELP_PAGE_KEY)

def manual_activate(obj):
    """
    Display the Gramps manual
    """
    display_help(webpage=WIKI_HELP_PAGE_MAN)

def report_bug_activate(obj):
    """
    Display the bug tracker web site
    """
    display_url(URL_BUGTRACKER)

def home_page_activate(obj):
    """
    Display the Gramps home page
    """
    display_url(URL_HOMEPAGE)

def mailing_lists_activate(obj):
    """
    Display the mailing list web page
    """
    display_url(URL_MAILINGLIST)

def extra_plugins_activate(obj):
    """
    Display the wiki page with extra plugins
    """
    display_url(URL_WIKISTRING+WIKI_EXTRAPLUGINS)

def faq_activate(obj):
    """
    Display FAQ
    """
    display_help(webpage=WIKI_HELP_PAGE_FAQ)

def run_plugin(pdata, dbstate, uistate):
    """
    run a plugin based on it's PluginData:
      1/ load plugin.
      2/ the report is run
    """
    pmgr = GuiPluginManager.get_instance()
    mod = pmgr.load_plugin(pdata)
    if not mod:
        #import of plugin failed
        failed = pmgr.get_fail_list()
        if failed:
            error_msg = failed[-1][1][1]
        else:
            error_msg = "(no error message)"
        ErrorDialog(
            _('Failed Loading Plugin'),
            _('The plugin %(name)s did not load and reported an error.\n\n'
              '%(error_msg)s\n\n'
              'If you are unable to fix the fault yourself then you can '
              'submit a bug at %(gramps_bugtracker_url)s or contact '
              'the plugin author (%(firstauthoremail)s).\n\n'
              'If you do not want Gramps to try and load this plugin again, '
              'you can hide it by using the Plugin Manager on the '
              'Help menu.') % {'name' : pdata.name,
                               'gramps_bugtracker_url' : URL_BUGHOME,
                               'firstauthoremail' : pdata.authors_email[0]
                                                    if pdata.authors_email
                                                    else '...',
                               'error_msg' : error_msg},
            parent=uistate.window)
        return

    if pdata.ptype == REPORT:
        report(dbstate, uistate, uistate.get_active('Person'),
               getattr(mod, pdata.reportclass),
               getattr(mod, pdata.optionclass),
               pdata.name, pdata.id,
               pdata.category, pdata.require_active)
    else:
        tool.gui_tool(dbstate=dbstate, user=User(uistate=uistate),
                      tool_class=getattr(mod, pdata.toolclass),
                      options_class=getattr(mod, pdata.optionclass),
                      translated_name=pdata.name,
                      name=pdata.id,
                      category=pdata.category,
                      callback=dbstate.db.request_rebuild)
    gc.collect(2)

def make_plugin_callback(pdata, dbstate, uistate):
    """
    Makes a callback for a report/tool menu item
    """
    return lambda x: run_plugin(pdata, dbstate, uistate)

def views_to_show(views, use_last=True):
    """
    Determine based on preference setting which views should be shown
    """
    current_cat = 0
    current_cat_view = 0
    default_cat_views = [0] * len(views)
    if use_last:
        current_page_id = config.get('preferences.last-view')
        default_page_ids = config.get('preferences.last-views')
        found = False
        for indexcat, cat_views in enumerate(views):
            cat_view = 0
            for pdata, page_def in cat_views:
                if not found:
                    if pdata.id == current_page_id:
                        current_cat = indexcat
                        current_cat_view = cat_view
                        default_cat_views[indexcat] = cat_view
                        found = True
                        break
                if pdata.id in default_page_ids:
                    default_cat_views[indexcat] = cat_view
                cat_view += 1
        if not found:
            current_cat = 0
            current_cat_view = 0
    return current_cat, current_cat_view, default_cat_views

class QuickBackup(ManagedWindow): # TODO move this class into its own module

    def __init__(self, dbstate, uistate, user):
        """
        Make a quick XML back with or without media.
        """
        self.dbstate = dbstate
        self.user = user

        ManagedWindow.__init__(self, uistate, [], self.__class__)
        window = Gtk.Dialog('',
                            self.uistate.window,
                            Gtk.DialogFlags.DESTROY_WITH_PARENT, None)
        self.set_window(window, None, _("Gramps XML Backup"))
        self.setup_configs('interface.quick-backup', 500, 150)
        close_button = window.add_button(_('_Close'),
                                         Gtk.ResponseType.CLOSE)
        ok_button = window.add_button(_('_OK'),
                                      Gtk.ResponseType.APPLY)
        vbox = window.get_content_area()
        hbox = Gtk.Box()
        label = Gtk.Label(label=_("Path:"))
        label.set_justify(Gtk.Justification.LEFT)
        label.set_size_request(90, -1)
        label.set_halign(Gtk.Align.START)
        hbox.pack_start(label, False, True, 0)
        path_entry = Gtk.Entry()
        dirtext = config.get('paths.quick-backup-directory')
        path_entry.set_text(dirtext)
        hbox.pack_start(path_entry, True, True, 0)
        file_entry = Gtk.Entry()
        button = Gtk.Button()
        button.connect("clicked",
                       lambda widget:
                       self.select_backup_path(widget, path_entry))
        image = Gtk.Image()
        image.set_from_icon_name('document-open', Gtk.IconSize.BUTTON)
        image.show()
        button.add(image)
        hbox.pack_end(button, False, True, 0)
        vbox.pack_start(hbox, False, True, 0)
        hbox = Gtk.Box()
        label = Gtk.Label(label=_("File:"))
        label.set_justify(Gtk.Justification.LEFT)
        label.set_size_request(90, -1)
        label.set_halign(Gtk.Align.START)
        hbox.pack_start(label, False, True, 0)
        struct_time = time.localtime()
        file_entry.set_text(
            config.get('paths.quick-backup-filename'
                      ) % {"filename": self.dbstate.db.get_dbname(),
                           "year": struct_time.tm_year,
                           "month": struct_time.tm_mon,
                           "day": struct_time.tm_mday,
                           "hour": struct_time.tm_hour,
                           "minutes": struct_time.tm_min,
                           "seconds": struct_time.tm_sec,
                           "extension": "gpkg"})
        hbox.pack_end(file_entry, True, True, 0)
        vbox.pack_start(hbox, False, True, 0)
        hbox = Gtk.Box()
        fbytes = 0
        mbytes = "0"
        for media in self.dbstate.db.iter_media():
            fullname = media_path_full(self.dbstate.db, media.get_path())
            try:
                fbytes += os.path.getsize(fullname)
                length = len(str(fbytes))
                if fbytes <= 999999:
                    mbytes = "< 1"
                else:
                    mbytes = str(fbytes)[:(length-6)]
            except OSError:
                pass
        label = Gtk.Label(label=_("Media:"))
        label.set_justify(Gtk.Justification.LEFT)
        label.set_size_request(90, -1)
        label.set_halign(Gtk.Align.START)
        hbox.pack_start(label, False, True, 0)
        include = Gtk.RadioButton.new_with_mnemonic_from_widget(
            None, "%s (%s %s)" % (_("Include"),
                                  mbytes, _("Megabyte|MB")))
        exclude = Gtk.RadioButton.new_with_mnemonic_from_widget(include,
                                                                _("Exclude"))
        include.connect("toggled", lambda widget: self.media_toggle(widget,
                                                                    file_entry))
        include_mode = config.get('preferences.quick-backup-include-mode')
        if include_mode:
            include.set_active(True)
        else:
            exclude.set_active(True)
        hbox.pack_start(include, False, True, 0)
        hbox.pack_end(exclude, False, True, 0)
        vbox.pack_start(hbox, False, True, 0)
        self.show()
        dbackup = window.run()
        if dbackup == Gtk.ResponseType.APPLY:
            # if file exists, ask if overwrite; else abort
            basefile = file_entry.get_text()
            basefile = basefile.replace("/", r"-")
            filename = os.path.join(path_entry.get_text(), basefile)
            if os.path.exists(filename):
                question = QuestionDialog2(
                    _("Backup file already exists! Overwrite?"),
                    _("The file '%s' exists.") % filename,
                    _("Proceed and overwrite"),
                    _("Cancel the backup"),
                    parent=self.window)
                yes_no = question.run()
                if not yes_no:
                    current_dir = path_entry.get_text()
                    if current_dir != dirtext:
                        config.set('paths.quick-backup-directory', current_dir)
                    self.close()
                    return
            position = self.window.get_position() # crock
            window.hide()
            self.window.move(position[0], position[1])
            self.uistate.set_busy_cursor(True)
            self.uistate.pulse_progressbar(0)
            self.uistate.progress.show()
            self.uistate.push_message(self.dbstate, _("Making backup..."))
            if include.get_active():
                from gramps.plugins.export.exportpkg import PackageWriter
                writer = PackageWriter(self.dbstate.db, filename, self.user)
                writer.export()
            else:
                from gramps.plugins.export.exportxml import XmlWriter
                writer = XmlWriter(self.dbstate.db, self.user,
                                   strip_photos=0, compress=1)
                writer.write(filename)
            self.uistate.set_busy_cursor(False)
            self.uistate.progress.hide()
            self.uistate.push_message(self.dbstate,
                                      _("Backup saved to '%s'") % filename)
            config.set('paths.quick-backup-directory', path_entry.get_text())
        else:
            self.uistate.push_message(self.dbstate, _("Backup aborted"))
        if dbackup != Gtk.ResponseType.DELETE_EVENT:
            self.close()

    def select_backup_path(self, widget, path_entry):
        """
        Choose a backup folder. Make sure there is one highlighted in
        right pane, otherwise FileChooserDialog will hang.
        """
        fdialog = Gtk.FileChooserDialog(
            title=_("Select backup directory"),
            parent=self.window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(_('_Cancel'),
                     Gtk.ResponseType.CANCEL,
                     _('_Apply'),
                     Gtk.ResponseType.OK))
        mpath = path_entry.get_text()
        if not mpath:
            mpath = HOME_DIR
        fdialog.set_current_folder(os.path.dirname(mpath))
        fdialog.set_filename(os.path.join(mpath, "."))
        status = fdialog.run()
        if status == Gtk.ResponseType.OK:
            filename = fdialog.get_filename()
            if filename:
                path_entry.set_text(filename)
        fdialog.destroy()
        return True

    def media_toggle(self, widget, file_entry):
        """
        Toggles media include values in the quick backup dialog.
        """
        include = widget.get_active()
        config.set('preferences.quick-backup-include-mode', include)
        extension = "gpkg" if include else "gramps"
        filename = file_entry.get_text()
        if "." in filename:
            base, ext = filename.rsplit(".", 1)
            file_entry.set_text("%s.%s" % (base, extension))
        else:
            file_entry.set_text("%s.%s" % (filename, extension))
