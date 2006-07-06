#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2006  Donald N. Allingham
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
Manages the main window and the pluggable views
"""

__author__ = "Donald N. Allingham"
__revision__ = "$Revision$"

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
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import gobject

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from PluginUtils import Plugins, Tool, PluginStatus, \
     relationship_class, load_plugins, \
     tool_list, report_list
from ReportBase import standalone_categories, report
import DisplayState
import const
import Config
import GrampsCfg
import Errors
import QuestionDialog
import PageView
import Navigation
import TipOfDay
import Bookmarks
import RecentFiles
import NameDisplay
import GrampsWidgets
import UndoHistory
from DbLoader import DbLoader
import GrampsDisplay
def show_url(dialog,link,user_data):
    GrampsDisplay.url(link)
gtk.about_dialog_set_url_hook(show_url,None)

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_KNOWN_FORMATS = { 
    const.app_gramps        : _('GRAMPS (grdb)'), 
    const.app_gramps_xml    : _('GRAMPS XML'), 
    const.app_gedcom        : _('GEDCOM'), 
}

uidefault = '''<ui>
<menubar name="MenuBar">
  <menu action="FileMenu">
    <menuitem action="New"/>
    <menuitem action="Open"/>
    <menu action="OpenRecent">
    </menu>
    <separator/>
    <menuitem action="Import"/>
    <menuitem action="SaveAs"/>
    <menuitem action="Export"/>
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
    <menuitem action="TipOfDay"/>
    <menuitem action="PluginStatus"/>
    <separator/>
    <menuitem action="HomePage"/>
    <menuitem action="MailingLists"/>
    <menuitem action="ReportBug"/>
    <separator/>
    <menuitem action="About"/>
  </menu>
</menubar>
<toolbar name="ToolBar">
  <toolitem action="New"/>  
  <separator/>
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
</ui>
'''

class ViewManager:

    def __init__(self, state):
        """
        Initialize the ViewManager
        """
        self.state = state
        self.active_page = None
        self.views = []
        self.pages = []
        self.file_loaded = False
        self._build_main_window()
        self._connect_signals()
        self.do_load_plugins()

    def _build_main_window(self):
        """
        Builds the GTK interface
        """
        width = Config.get(Config.WIDTH)
        height = Config.get(Config.HEIGHT)

        self.window = gtk.Window()
        self.window.set_icon_from_file(const.icon)
        self.window.set_default_size(width, height)
        
        self.statusbar = gtk.Statusbar()

        self.RelClass = relationship_class

        vbox = gtk.VBox()
        self.window.add(vbox)
        hbox = gtk.HBox()
        self.ebox = gtk.EventBox()
        self.bbox = gtk.VBox()
        self.buttons = []
        self.ebox.add(self.bbox)
        hbox.pack_start(self.ebox, False)
        hbox.show_all()

        self.show_sidebar = Config.get(Config.VIEW)
        self.show_toolbar = Config.get(Config.TOOLBAR_ON)

        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_tab_pos(gtk.POS_LEFT)
        self.notebook.show()
        self._init_lists()
        self._build_ui_manager()

        hbox.pack_start(self.notebook, True)
        self.menubar = self.uimanager.get_widget('/MenuBar')
        self.toolbar = self.uimanager.get_widget('/ToolBar')
        vbox.pack_start(self.menubar, False)
        vbox.pack_start(self.toolbar, False)
        vbox.add(hbox)
        self.progress = gtk.ProgressBar()
        self.progress.set_size_request(100, -1)
        self.progress.hide()
        self.statusbar.show()
        self.warnbtn = GrampsWidgets.WarnButton()
        hbox2 = gtk.HBox()
        hbox2.set_spacing(4)
        hbox2.set_border_width(2)
        hbox2.pack_start(self.progress, False)
        hbox2.pack_start(self.warnbtn, False)
        hbox2.pack_end(self.statusbar, True)
        hbox2.show()
        vbox.pack_end(hbox2, False)
        vbox.show()

        self.uistate = DisplayState.DisplayState(
            self.window, self.statusbar, self.progress, self.warnbtn, 
            self.uimanager, self.state)

        toolbar = self.uimanager.get_widget('/ToolBar')
        openbtn = gtk.MenuToolButton(gtk.STOCK_OPEN)
        openbtn.connect('clicked', self.open_activate)
        openbtn.set_sensitive(False)

        self.uistate.set_open_widget(openbtn)
        toolbar.insert(openbtn, 1)

        self.open_tips = gtk.Tooltips()
        openbtn.set_arrow_tooltip(self.open_tips,
                                  _("Open a recently opened database"),
                                  _("Open a recently opened database"))
        
        openbtn.set_tooltip(self.open_tips,
                            _("Open an existing database"),
                            _("Open an existing database")
                            )
        openbtn.show()
        
        self.person_nav = Navigation.PersonNavigation(self.uistate)
        self._navigation_type[PageView.NAVIGATION_PERSON] = (self.person_nav,
                                                             None)
        self.recent_manager = DisplayState.RecentDocsMenu(
            self.uistate,self.state,self.read_recent_file)
        self.recent_manager.build()

        self.db_loader = DbLoader(self.state,self.uistate)

        if self.show_sidebar:
            self.ebox.show()
            self.notebook.set_show_tabs(False)
        else:
            self.ebox.hide()
            self.notebook.set_show_tabs(True)

        if self.show_toolbar:
            self.toolbar.show()
        else:
            self.toolbar.hide()

        # Showing the main window is deferred so that
        # ArgHandler can work without it always shown
        # But we need to realize it here to have gtk.gdk.window handy
        self.window.realize()

    def _connect_signals(self):
        """
        connects the signals needed
        """
        self.window.connect('destroy', self.quit)
        self.notebook.connect('switch-page', self.change_page)

    def _init_lists(self):
        self._file_action_list = [
            ('FileMenu', None, _('_File')), 
            ('New', gtk.STOCK_NEW, _('_New'), "<control>n",
             _("Create a new database"), self.new_activate),
            ('Open', gtk.STOCK_OPEN, _('_Open'), "<control>o",
             _("Open an existing database"), self.open_activate), 
            ('OpenRecent', None, _('Open _Recent'), None,
             _("Open an existing database")), 
            ('Quit', gtk.STOCK_QUIT, _('_Quit'), "<control>q",None,self.quit),
            ('ViewMenu', None, _('_View')), 
            ('EditMenu', None, _('_Edit')), 
            ('Preferences', gtk.STOCK_PREFERENCES,_('_Preferences'),None, None,
             self.preferences_activate), 
            ('HelpMenu', None, _('_Help')), 
            ('HomePage', None, _('GRAMPS _home page'), None, None,
             self.home_page_activate), 
            ('MailingLists', None, _('GRAMPS _mailing lists'), None, None,
             self.mailing_lists_activate), 
            ('ReportBug', None, _('_Report a bug'), None, None,
             self.report_bug_activate), 
            ('About', gtk.STOCK_ABOUT, _('_About'), None, None, self.about), 
            ('PluginStatus', None,_('_Plugin status'), None, None,
             self.plugin_status), 
            ('FAQ', None, _('_FAQ'), None, None, self.faq_activate), 
            ('UserManual', gtk.STOCK_HELP, _('_User Manual'), 'F1', None,
             self.manual_activate), 
            ('TipOfDay', None, _('Tip of the day'), None, None,
             self.tip_of_day_activate), 
            ]

        self._action_action_list = [
            ('SaveAs', gtk.STOCK_SAVE_AS, _('_Save As'),"<control><shift>s",
             None, self.save_as_activate), 
            ('Export', 'gramps-export', _('_Export'), "<control>e", None,
             self.export_data), 
            ('Abandon', gtk.STOCK_REVERT_TO_SAVED,
             _('_Abandon changes and quit'), None, None, self.abort), 
            ('ScratchPad', gtk.STOCK_PASTE, _('_ScratchPad'), "",
             _("Open the ScratchPad dialog"), self.scratchpad), 
            ('Import', gtk.STOCK_CONVERT, _('_Import'), "<control>i", None,
             self.import_data), 
            ('Reports', gtk.STOCK_DND_MULTIPLE, _('_Reports'), None,
             _("Open the reports dialog"), self.reports_clicked), 
            ('Tools', gtk.STOCK_EXECUTE, _('_Tools'), None,
             _("Open the tools dialog"), self.tools_clicked),
            ('EditMenu', None, _('_Edit')), 
            ('ColumnEdit', gtk.STOCK_PROPERTIES, _('_Column Editor')), 
            ('GoMenu', None, _('_Go')), 
            ('BookMenu', None, _('_Bookmarks')), 
            ('ReportsMenu', None, _('_Reports')), 
            ('ToolsMenu', None, _('_Tools')), 
            ('WindowsMenu', None, _('_Windows')),
            ('F2', None, 'F2', "F2", None, self.keypress),
            ('F3', None, 'F3', "F3", None, self.keypress),
            ('F4', None, 'F4', "F4", None, self.keypress),
            ('F5', None, 'F5', "F5", None, self.keypress),
            ('F6', None, 'F6', "F6", None, self.keypress),
            ('F7', None, 'F7', "F7", None, self.keypress),
            ('F8', None, 'F9', "F8", None, self.keypress),
            ('F9', None, 'F9', "F9", None, self.keypress),
            ('F11', None, 'F11', "F11", None, self.keypress),
            ('F12', None, 'F12', "F12", None, self.keypress),
            ]

        self._file_toggle_action_list = [
            ('Sidebar', None, _('_Sidebar'), None, None, self.sidebar_toggle,
             self.show_sidebar ), 
            ('Toolbar', None, _('_Toolbar'), None, None, self.toolbar_toggle,
             self.show_toolbar ), 
            ]

        self._undo_action_list = [
            ('Undo', gtk.STOCK_UNDO, _('_Undo'),'<control>z', None, self.undo),
            ]

        self._redo_action_list = [
            ('Redo', gtk.STOCK_REDO,_('_Redo'), '<shift><control>z', None,
             self.redo),
            ]

        self._undo_history_action_list = [
            ('UndoHistory', 'gramps-undo-history',
             _('Undo History'), None, None, self.undo_history),
            ]

        self._navigation_type = {
            PageView.NAVIGATION_NONE: (None, None), 
            PageView.NAVIGATION_PERSON: (None, None), 
            }

    def keypress(self, action):
        name = action.get_name()
        try:
            self.active_page.call_function(name)
        except:
            self.uistate.push_message(_("Key %s is not bound") % name)

    def init_interface(self):
        self._init_lists()

        self.create_pages()
        if not self.file_loaded:
            self.actiongroup.set_visible(False)
        self.fileactions.set_sensitive(False)
        self.build_tools_menu()
        self.build_report_menu()
        self.fileactions.set_sensitive(True)
        self.uistate.widget.set_sensitive(True)
        Config.client.notify_add("/apps/gramps/interface/statusbar",
                                 self.statusbar_key_update)

    def statusbar_key_update(self,client,cnxn_id,entry,data):
        self.uistate.modify_statusbar()

    def post_init_interface(self):
        # Showing the main window is deferred so that
        # ArgHandler can work without it always shown
        self.window.show()

    def do_load_plugins(self):
        self.uistate.status_text(_('Loading document formats...'))
        error  = load_plugins(const.docgenDir)
        error |= load_plugins(os.path.join(const.home_dir, "docgen"))
        self.uistate.status_text(_('Loading plugins...'))
        error |= load_plugins(const.pluginsDir)
        error |= load_plugins(os.path.join(const.home_dir, "plugins"))
        if Config.get(Config.POP_PLUGIN_STATUS) and error:
            PluginStatus.PluginStatus(self.state, self.uistate, [])
        self.uistate.push_message(_('Ready'))

    def quit(self, obj=None):
        self.state.db.close()
        (width, height) = self.window.get_size()
        Config.set(Config.WIDTH, width)
        Config.set(Config.HEIGHT, height)
        Config.sync()
        gtk.main_quit()

    def abort(self,obj=None):
        """
        Abandon changes and quit.
        """
        if self.state.db.abort_possible:
            self.state.db.disable_signals()
            while self.state.db.undo():
                pass
            self.quit()
        else:
            QuestionDialog.WarningDialog(
                _("Cannot abandon session's changes"),
                _('Changes cannot be completely abandoned because the '
                  'number of changes made in the session exceeded the '
                  'limit.'))

    def _build_ui_manager(self):
        self.merge_ids = []
        self.uimanager = gtk.UIManager()

        accelgroup = self.uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)

        self.actiongroup = gtk.ActionGroup('MainWindow')
        self.fileactions = gtk.ActionGroup('FileWindow')
        self.undoactions = gtk.ActionGroup('Undo')
        self.redoactions = gtk.ActionGroup('Redo')
        self.undohistoryactions = gtk.ActionGroup('UndoHistory')

        self.fileactions.add_actions(self._file_action_list)
        self.actiongroup.add_actions(self._action_action_list)
        self.fileactions.add_toggle_actions(self._file_toggle_action_list)

        self.undoactions.add_actions(self._undo_action_list)
        self.undoactions.set_sensitive(False)
        
        self.redoactions.add_actions(self._redo_action_list)
        self.redoactions.set_sensitive(False)

        self.undohistoryactions.add_actions(self._undo_history_action_list)

        merge_id = self.uimanager.add_ui_from_string(uidefault)
        
        self.uimanager.insert_action_group(self.fileactions, 1)
        self.uimanager.insert_action_group(self.actiongroup, 1)
        self.uimanager.insert_action_group(self.undoactions, 1)
        self.uimanager.insert_action_group(self.redoactions, 1)
        self.uimanager.insert_action_group(self.undohistoryactions, 1)
        self.uimanager.ensure_update()

    def home_page_activate(self, obj):
        import GrampsDisplay
        GrampsDisplay.url(const.url_homepage)

    def mailing_lists_activate(self, obj):
        import GrampsDisplay
        GrampsDisplay.url( const.url_mailinglist)

    def preferences_activate(self, obj):
        try:
            GrampsCfg.GrampsPreferences(self.uistate)
        except Errors.WindowActiveError:
            pass

    def report_bug_activate(self, obj):
        import GrampsDisplay
        GrampsDisplay.url( const.url_bugtracker)

    def manual_activate(self, obj):
        """Display the GRAMPS manual"""
        try:
            import GrampsDisplay
            GrampsDisplay.help('index')
        except gobject.GError, msg:
            QuestionDialog.ErrorDialog(_("Could not open help"), str(msg))

    def faq_activate(self, obj):
        """Display FAQ"""
        try:
            import GrampsDisplay
            GrampsDisplay.help('faq')
        except gobject.GError, msg:
            QuestionDialog.ErrorDialog(_("Could not open help"), str(msg))

    def tip_of_day_activate(self, obj):
        """Display Tip of the day"""
        TipOfDay.TipOfDay(self.uistate)

    def plugin_status(self, obj):
        """Display Tip of the day"""
        PluginStatus.PluginStatus(self.state, self.uistate, [])

    def about(self, obj):
        about = gtk.AboutDialog()
        about.set_name(const.program_name)
        about.set_version(const.version)
        about.set_copyright(const.copyright_msg)
        try:
            f = open(const.license_file, "r")
            about.set_license(f.read().replace('\x0c', ''))
            f.close()
        except:
            pass
        about.set_comments(const.comments)
        about.set_website_label(_('GRAMPS Homepage'))
        about.set_website('http://gramps-project.org')
        about.set_authors(const.authors)
        about.set_translator_credits(_(const.translators))
        about.set_documenters(const.documenters)
        about.set_logo(gtk.gdk.pixbuf_new_from_file(const.splash))
        about.show()
        about.run()

    def sidebar_toggle(self, obj):
        if obj.get_active():
            self.ebox.show()
            self.notebook.set_show_tabs(False)
            Config.set(Config.VIEW, True)
        else:
            self.ebox.hide()
            self.notebook.set_show_tabs(True)
            Config.set(Config.VIEW, False)
        Config.sync()

    def toolbar_toggle(self, obj):
        if obj.get_active():
            self.toolbar.show()
            Config.set(Config.TOOLBAR_ON, True)
        else:
            self.toolbar.hide()
            Config.set(Config.TOOLBAR_ON, False)
        Config.sync()

    def register_view(self, view):
        self.views.append(view)

    def create_pages(self):
        self.pages = []
        self.prev_nav = PageView.NAVIGATION_NONE

        use_text = Config.get(Config.SIDEBAR_TEXT)
        
        index = 0
        for page_def in self.views:
            page = page_def(self.state, self.uistate)
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
            self.notebook.append_page(page_display, hbox)
            self.pages.append(page)

            # create the button and add it to the sidebar
            button = gtk.ToggleButton()
            hbox = gtk.HBox()
            hbox.show()
            image = gtk.Image()
            if use_text:
                image.set_from_stock(page_stock, gtk.ICON_SIZE_BUTTON)
            else:
                image.set_from_stock(page_stock, gtk.ICON_SIZE_LARGE_TOOLBAR)
            image.show()
            hbox.pack_start(image,False,False)
            hbox.set_spacing(4)

            if use_text:
                label = gtk.Label(page_title)
                label.show()
                hbox.pack_start(label,False,True)

            button.add(hbox)
            button.set_relief(gtk.RELIEF_NONE)
            button.set_alignment(0, 0.5)
            button.connect('clicked',
                           lambda x, y : self.notebook.set_current_page(y),
                           index)
            button.show()
            index += 1
            self.bbox.pack_start(button, False)
            self.buttons.append(button)

        current = Config.get(Config.LAST_VIEW)
        if current > len(self.pages):
            current = 0

        self.active_page = self.pages[current]
        self.buttons[current].set_active(True)
        self.active_page.set_active()
        self.notebook.set_current_page(current)

    def change_page(self, obj, page, num=-1):
        if num == -1:
            num = self.notebook.get_current_page()
        
        for ix in range(len(self.buttons)):
            if ix != num and self.buttons[ix].get_active():
                self.buttons[ix].set_active(False)

        if self.state.open:

            for mergeid in self.merge_ids:
                self.uimanager.remove_ui(mergeid)

            if self.active_page:
                self.active_page.set_inactive()
                groups = self.active_page.get_actions()
                for grp in groups:
                    if grp in self.uimanager.get_action_groups():
                        self.uimanager.remove_action_group(grp)

            if len(self.pages) > 0:
                self.active_page = self.pages[num]
                self.active_page.set_active()
                Config.set(Config.LAST_VIEW,num)
                Config.sync()
                
                old_nav = self._navigation_type[self.prev_nav]
                if old_nav[0] != None:
                    old_nav[0].disable()

                nav_type = self._navigation_type[self.active_page.navigation_type()]
                if nav_type[0] != None:
                    nav_type[0].enable()

                groups = self.active_page.get_actions()

                for grp in groups:
                    self.uimanager.insert_action_group(grp, 1)

                ui = self.active_page.ui_definition()
                self.merge_ids = [self.uimanager.add_ui_from_string(ui)]

                for ui in self.active_page.additional_ui_definitions():
                    mergeid = self.uimanager.add_ui_from_string(ui)
                    self.merge_ids.append(mergeid)
                self.uimanager.ensure_update()
                while gtk.events_pending():
                    gtk.main_iteration()

                self.pages[num].change_page()

    def import_data(self, obj):
        if self.state.db.db_is_open:
            self.db_loader.import_file()
            self.post_load()
        
    def open_activate(self, obj):
        (filename,filetype) = self.db_loader.open_file()
        self.post_load_newdb(filename,filetype)

    def save_as_activate(self,obj):
        if self.state.db.db_is_open:
            (filename,filetype) = self.db_loader.save_as()
            self.post_load_newdb(filename,filetype)

    def new_activate(self,obj):
        (filename,filetype) = self.db_loader.new_file()
        self.post_load_newdb(filename,filetype)

    def read_recent_file(self,filename,filetype):
        self.db_loader.read_file(filename,filetype)
        self.post_load_newdb(filename,filetype)

    def post_load(self):
        # This method is for the common UI post_load, both new files
        # and added data like imports.
        self.uistate.clear_history()
        self.uistate.progress.hide()

        self.state.db.undo_callback = self.change_undo_label
        self.state.db.redo_callback = self.change_redo_label
        self.change_undo_label(None)
        self.change_redo_label(None)
        self.state.db.undo_history_callback = self.undo_history_update
        self.undo_history_close()

        self.window.window.set_cursor(None)

    def post_load_newdb(self, filename, filetype):

        if not filename:
            return

        # This method is for UI stuff when the database has changed.
        # Window title, recent files, etc related to new file.

        self.state.db.set_save_path(filename)

        # Update window title
        if filename[-1] == '/':
            filename = filename[:-1]
        name = os.path.basename(filename)
        if self.state.db.readonly:
            msg =  "%s (%s) - GRAMPS" % (name, _('Read Only'))
            self.uistate.window.set_title(msg)
        else:
            msg = "%s - GRAMPS" % name
            self.uistate.window.set_title(msg)

        res = self.state.db.get_researcher()
        owner = GrampsCfg.get_researcher()
        if res.get_name() == "" and owner.get_name():
            self.state.db.set_researcher(owner)

        self.setup_bookmarks()
        NameDisplay.register_custom_formats(self.state.db.name_formats)

        self.state.db.enable_signals()
        self.state.signal_change()
        self.state.db.request_rebuild()

        Config.set(Config.RECENT_FILE,filename)
    
        self.relationship = self.RelClass(self.state.db)
        self.state.change_active_person(self.state.db.find_initial_person())
        self.change_page(None, None)
        self.actiongroup.set_visible(True)

        self.file_loaded = True

        RecentFiles.recent_files(filename,filetype)
        self.recent_manager.build()
        
        # Call common post_load
        self.post_load()

    def change_undo_label(self, label):
        self.uimanager.remove_action_group(self.undoactions)
        self.undoactions = gtk.ActionGroup('Undo')
        if label:
            self.undoactions.add_actions([
                ('Undo',gtk.STOCK_UNDO,label,'<control>z',None,self.undo)])
        else:
            self.undoactions.add_actions([
                ('Undo', gtk.STOCK_UNDO, '_Undo', 
                 '<control>z', None, self.undo)])
            self.undoactions.set_sensitive(False)
        self.uimanager.insert_action_group(self.undoactions, 1)

    def change_redo_label(self, label):
        self.uimanager.remove_action_group(self.redoactions)
        self.redoactions = gtk.ActionGroup('Redo')
        if label:
            self.redoactions.add_actions([
                ('Redo', gtk.STOCK_REDO, label, '<shift><control>z', 
                 None, self.redo)])
        else:
            self.redoactions.add_actions([
                ('Redo', gtk.STOCK_UNDO, '_Redo', 
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
            pass

    def undo_history_close(self):
        try:
            # Try closing undo history window if it exists
            self.undo_history_window.close()
        except AttributeError:
            # Let it go: history window does not exist
            pass
 
    def setup_bookmarks(self):
        self.bookmarks = Bookmarks.Bookmarks(self.state, self.uistate, 
                                             self.state.db.get_bookmarks())

    def add_bookmark(self, obj):
        if self.state.active:
            self.bookmarks.add(self.state.active.get_handle())
            name = NameDisplay.displayer.display(self.state.active)
            self.uistate.push_message(_("%s has been bookmarked") % name)
        else:
            QuestionDialog.WarningDialog(
                _("Could Not Set a Bookmark"), 
                _("A bookmark could not be set because "
                  "no one was selected."))

    def edit_bookmarks(self, obj):
        self.bookmarks.edit()

    def reports_clicked(self, obj):
        try:
            Plugins.ReportPlugins(self.state, self.uistate, [])
        except Errors.WindowActiveError:
            pass            

    def tools_clicked(self, obj):
        try:
            Plugins.ToolPlugins(self.state, self.uistate, [])
        except Errors.WindowActiveError:
            pass            
        
    def scratchpad(self, obj):
        import ScratchPad
        try:
            ScratchPad.ScratchPadWindow(self.state, self.uistate)
        except Errors.WindowActiveError:
            pass            

    def undo(self, obj):
        self.state.db.undo()

    def redo(self, obj):
        self.state.db.redo()

    def undo_history(self, obj):
        try:
            self.undo_history_window = UndoHistory.UndoHistory(self.state,
                                                               self.uistate)
        except Errors.WindowActiveError:
            pass

    def export_data(self, obj):
        if self.state.db.db_is_open:
            import Exporter
            Exporter.Exporter(self.state, self.uistate)

    def build_tools_menu(self):
        self.toolactions = gtk.ActionGroup('ToolWindow')
        (ui, actions) = self.build_plugin_menu('ToolsMenu', 
                                              tool_list, 
                                              Tool.tool_categories, 
                                              make_tool_callback)
        self.toolactions.add_actions(actions)
        self.uistate.uimanager.add_ui_from_string(ui)
        self.uimanager.insert_action_group(self.toolactions, 1)
        self.uistate.uimanager.ensure_update()
    
    def build_report_menu(self):
        self.reportactions = gtk.ActionGroup('ReportWindow')
        (ui, actions) = self.build_plugin_menu('ReportsMenu', 
                                              report_list, 
                                              standalone_categories, 
                                              make_report_callback)
        self.reportactions.add_actions(actions)
        self.uistate.uimanager.add_ui_from_string(ui)
        self.uimanager.insert_action_group(self.reportactions, 1)
        self.uistate.uimanager.ensure_update()

    def build_plugin_menu(self, text, item_list, categories, func):
        actions = []
        f = StringIO()
        f.write('<ui><menubar name="MenuBar"><menu action="%s">' % text)
        
        menu = gtk.Menu()
        menu.show()
    
        hash_data = {}
        for item in item_list:
            if item[9]:
                category = Plugins.UNSUPPORTED
            else:
                category = categories[item[3]]
            if hash_data.has_key(category):
                hash_data[category].append(
                    (item[0], item[1], item[2], item[4], item[3], item[10]))
            else:
                hash_data[category] = [
                    (item[0], item[1], item[2], item[4], item[3], item[10])]
                
        # Sort categories, skipping the unsupported
        catlist = [item for item in hash_data.keys()
                   if item != Plugins.UNSUPPORTED]
        catlist.sort()
        for key in catlist:
            new_key = key.replace(' ', '-')
            f.write('<menu action="%s">' % new_key)
            actions.append((new_key, None, key))
            lst = hash_data[key]
            lst.sort(by_menu_name)
            for name in lst:
                new_key = name[3].replace(' ', '-')
                f.write('<menuitem action="%s"/>' % new_key)
                actions.append((new_key, None, name[2], None, None, 
                                func(name, self.state, self.uistate)))
            f.write('</menu>')

        # If there are any unsupported items we add separator
        # and the unsupported category at the end of the menu
        if hash_data.has_key(Plugins.UNSUPPORTED):
            f.write('<separator/>')
            f.write('<menu action="%s">' % Plugins.UNSUPPORTED)
            actions.append((Plugins.UNSUPPORTED, None, Plugins.UNSUPPORTED))
            lst = hash_data[Plugins.UNSUPPORTED]
            lst.sort(by_menu_name)
            for name in lst:
                new_key = name[3].replace(' ', '-')
                f.write('<menuitem action="%s"/>' % new_key)
                actions.append((new_key, None, name[2], None, None, 
                                func(name, self.state, self.uistate)))
            f.write('</menu>')

        f.write('</menu></menubar></ui>')
        return (f.getvalue(), actions)

def by_menu_name(a, b):
    return cmp(a[2], b[2])


def make_report_callback(lst, dbstate, uistate):
    return lambda x: report(dbstate, uistate, dbstate.get_active_person(), 
                            lst[0], lst[1], lst[2], lst[3], lst[4], lst[5])

def make_tool_callback(lst, dbstate, uistate):
    return lambda x: Tool.gui_tool(dbstate, uistate,  
                                   lst[0], lst[1], lst[2], lst[3], lst[4], 
                                   dbstate.db.request_rebuild)
