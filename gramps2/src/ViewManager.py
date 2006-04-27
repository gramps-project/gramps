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
from bsddb import db
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
from PluginUtils import Plugins, Report, Tool, PluginStatus, \
     relationship_class, load_plugins, \
     import_list, tool_list, report_list
import DisplayState
import const
import Config
import GrampsDb
import GrampsCfg
import Errors
import Utils
import QuestionDialog
import PageView
import Navigation
import TipOfDay
import Bookmarks
import RecentFiles
import NameDisplay
import Mime
import GrampsWidgets

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
    <separator/>
    <placeholder name="CommonEdit"/>
    <menuitem action="CmpMerge"/>
    <menuitem action="FastMerge"/>
    <separator/>
    <menuitem action="Preferences"/>
    <menuitem action="ColumnEdit"/>
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
        self.keypress_function = {}
        self.file_loaded = False
        self._build_main_window()
        self._connect_signals()

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
        openbtn.show()
        openbtn.connect('clicked', self.open_activate)
        openbtn.set_sensitive(False)
        self.uistate.set_open_widget(openbtn)
        toolbar.insert(openbtn, 1)

        self.person_nav = Navigation.PersonNavigation(self.uistate)
        self._navigation_type[PageView.NAVIGATION_PERSON] = (self.person_nav,
                                                             None)
        self.recent_manager = DisplayState.RecentDocsMenu(self.uistate,
                                                          self.state, 
                                                          self.read_file)
        self.recent_manager.build()

        self.window.show()

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

    def _connect_signals(self):
        """
        connects the signals needed
        """
        self.window.connect('destroy', self.quit)
        self.notebook.connect('switch-page', self.change_page)

    def _init_lists(self):
        self._file_action_list = [
            ('FileMenu', None, '_File'), 
            ('New', gtk.STOCK_NEW, '_New', "<control>n", None,
             self.new_activate),
            ('Open', gtk.STOCK_OPEN, '_Open', "<control>o", None,
             self.open_activate), 
            ('OpenRecent', None, 'Open _Recent'), 
            ('Quit', gtk.STOCK_QUIT, '_Quit', "<control>q", None, self.quit), 
            ('ViewMenu', None, '_View'), 
            ('EditMenu', None, '_Edit'), 
            ('Preferences', gtk.STOCK_PREFERENCES, '_Preferences', None, None,
             self.preferences_activate), 
            ('HelpMenu', None, '_Help'), 
            ('HomePage', None, _('GRAMPS _home page'), None, None,
             self.home_page_activate), 
            ('MailingLists', None, _('GRAMPS _mailing lists'), None, None,
             self.mailing_lists_activate), 
            ('ReportBug', None, _('_Report a bug'), None, None,
             self.report_bug_activate), 
            ('About', gtk.STOCK_ABOUT, '_About', None, None, self.about), 
            ('PluginStatus', None, '_Plugin status', None, None,
             self.plugin_status), 
            ('FAQ', None, '_FAQ', None, None, self.faq_activate), 
            ('UserManual', gtk.STOCK_HELP, '_User Manual', 'F1', None,
             self.manual_activate), 
            ('TipOfDay', None, 'Tip of the day', None, None,
             self.tip_of_day_activate), 
            ]

        self._action_action_list = [
            ('SaveAs', gtk.STOCK_SAVE_AS, '_Save As'), 
            ('Export', gtk.STOCK_SAVE_AS, '_Export', "<control>e", None,
             self.export_data), 
            ('Abandon', gtk.STOCK_REVERT_TO_SAVED, '_Abandon changes and quit'), 
            ('CmpMerge', None, '_Compare and merge'), 
            ('FastMerge', None, '_Fast merge'), 
            ('ScratchPad', gtk.STOCK_PASTE, '_ScratchPad', None, None,
             self.scratchpad), 
            ('Import', gtk.STOCK_CONVERT, '_Import', "<control>i", None,
             self.import_data), 
            ('Reports', gtk.STOCK_DND_MULTIPLE, '_Reports', None, None,
             self.reports_clicked), 
            ('Tools', gtk.STOCK_EXECUTE, '_Tools', None, None,
             self.tools_clicked),
            ('EditMenu', None, '_Edit'), 
            ('ColumnEdit', gtk.STOCK_PROPERTIES, '_Column Editor'), 
            ('GoMenu', None, '_Go'), 
            ('BookMenu', None, '_Bookmarks'), 
            ('ReportsMenu', None, '_Reports'), 
            ('ToolsMenu', None, '_Tools'), 
            ('WindowsMenu', None, '_Windows'),
            ('F2', None, None, "F2", None, self.keypress),
            ('F3', None, None, "F3", None, self.keypress),
            ('F4', None, None, "F4", None, self.keypress),
            ('F5', None, None, "F5", None, self.keypress),
            ('F6', None, None, "F6", None, self.keypress),
            ('F7', None, None, "F7", None, self.keypress),
            ('F8', None, None, "F8", None, self.keypress),
            ('F9', None, None, "F9", None, self.keypress),
            ('F11', None, None, "F11", None, self.keypress),
            ('F12', None, None, "F12", None, self.keypress),
            ]

        self._file_toggle_action_list = [
            ('Sidebar', None, '_Sidebar', None, None, self.sidebar_toggle,
             self.show_sidebar ), 
            ('Toolbar', None, '_Toolbar', None, None, self.toolbar_toggle,
             self.show_toolbar ), 
            ]

        self._undo_action_list = [
            ('Undo', gtk.STOCK_UNDO, '_Undo', '<control>z', None, self.undo),
            ]

        self._redo_action_list = [
            ('Redo', gtk.STOCK_REDO, '_Redo', '<shift><control>z', None,
             self.redo),
            ]

        self._navigation_type = {
            PageView.NAVIGATION_NONE: (None, None), 
            PageView.NAVIGATION_PERSON: (None, None), 
            }

    def keypress(self, action):
        name = action.get_name()
        func = self.keypress_function.get(name)
        if func:
            func()
        else:
            self.uistate.push_message(_("Key %s is not bound") % name)

    def init_interface(self):
        self._init_lists()

        self.create_pages()
        self.change_page(None, None)
        if not self.file_loaded:
            self.actiongroup.set_visible(False)
        self.fileactions.set_sensitive(False)
        self.do_load_plugins()
        self.build_tools_menu()
        self.build_report_menu()
        self.fileactions.set_sensitive(True)
        self.uistate.widget.set_sensitive(True)

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

    def _build_ui_manager(self):
        self.merge_ids = []
        self.uimanager = gtk.UIManager()

        accelgroup = self.uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)

        self.actiongroup = gtk.ActionGroup('MainWindow')
        self.fileactions = gtk.ActionGroup('FileWindow')
        self.undoactions = gtk.ActionGroup('Undo')
        self.redoactions = gtk.ActionGroup('Redo')

        self.fileactions.add_actions(self._file_action_list)
        self.actiongroup.add_actions(self._action_action_list)
        self.fileactions.add_toggle_actions(self._file_toggle_action_list)

        self.undoactions.add_actions(self._undo_action_list)
        self.undoactions.set_sensitive(False)
        
        self.redoactions.add_actions(self._redo_action_list)
        self.redoactions.set_sensitive(False)

        merge_id = self.uimanager.add_ui_from_string(uidefault)
        
        self.uimanager.insert_action_group(self.fileactions, 1)
        self.uimanager.insert_action_group(self.actiongroup, 1)
        self.uimanager.insert_action_group(self.undoactions, 1)
        self.uimanager.insert_action_group(self.redoactions, 1)
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
            self.notebook.append_page(page_display, hbox)
            self.pages.append(page)

            # create the button and add it to the sidebar
            button = gtk.ToggleButton()
            if page_stock:
                button.set_use_stock(True)
                button.set_label(page_stock)
            else:
                button.set_label(page_title)
            button.set_border_width(4)
            button.set_relief(gtk.RELIEF_NONE)
            button.set_alignment(0, 0.5)
            button.connect('clicked',
                           lambda x, y : self.notebook.set_current_page(y),
                           index)
            button.show()
            index += 1
            self.bbox.pack_start(button, False)
            self.buttons.append(button)

        self.active_page = self.pages[0]
        self.buttons[0].set_active(True)
        self.active_page.set_active()

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

    def open_activate(self, obj):

        choose = gtk.FileChooserDialog(
            _('GRAMPS: Open database'), 
            self.uistate.window, 
            gtk.FILE_CHOOSER_ACTION_OPEN, 
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
             gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        # Always add automatic (macth all files) filter
        add_all_files_filter(choose)
        add_grdb_filter(choose)
        add_xml_filter(choose)
        add_gedcom_filter(choose)

        format_list = [const.app_gramps, const.app_gramps_xml, const.app_gedcom]

        # Add more data type selections if opening existing db
        for data in import_list:
            mime_filter = data[1]
            mime_type = data[2]
            native_format = data[2]
            format_name = data[3]
            
            if not native_format:
                choose.add_filter(mime_filter)
                format_list.append(mime_type)
                _KNOWN_FORMATS[mime_type] = format_name
        
        (box, type_selector) = format_maker(format_list)
        choose.set_extra_widget(box)

        # Suggested folder: try last open file, last import, last export, 
        # then home.
        default_dir = os.path.split(Config.get(Config.RECENT_FILE))[0] + os.path.sep
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_IMPORT_DIR)
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_EXPORT_DIR)
        if len(default_dir)<=1:
            default_dir = '~/'

        choose.set_current_folder(default_dir)
        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = choose.get_filename()
            if len(filename) == 0:
                return False
            filetype = type_selector.get_value()
            if filetype == 'auto':
                filetype = Mime.get_type(filename)
            (the_path, the_file) = os.path.split(filename)
            choose.destroy()
            if filetype in [const.app_gramps, const.app_gramps_xml, 
                                const.app_gedcom]:
    
                try:
                    return self.open_native(filename, filetype)
                except db.DBInvalidArgError, msg:
                    QuestionDialog.ErrorDialog(
                        _("Could not open file: %s") % filename, msg[1])
                    return False
                except:
                    log.error("Failed to open native.", exc_info=True)
                    return False

            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename, 
                _('File type "%s" is unknown to GRAMPS.\n\n'
                  'Valid types are: GRAMPS database, GRAMPS XML, '
                  'GRAMPS package, and GEDCOM.') % filetype)
        choose.destroy()
        return False

    def new_activate(self, obj):

        choose = gtk.FileChooserDialog(
            _('GRAMPS: Create GRAMPS database'), 
            self.uistate.window, 
            gtk.FILE_CHOOSER_ACTION_SAVE, 
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
             gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        # Always add automatic (macth all files) filter
        add_all_files_filter(choose)
        add_grdb_filter(choose)

        # Suggested folder: try last open file, import, then last export, 
        # then home.
        default_dir = os.path.split(Config.get(Config.RECENT_FILE))[0] + os.path.sep
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_IMPORT_DIR)
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_EXPORT_DIR)
        if len(default_dir)<=1:
            default_dir = '~/'

        new_filename = Utils.get_new_filename('grdb', default_dir)
        
        choose.set_current_folder(default_dir)
        choose.set_current_name(os.path.split(new_filename)[1])

        while (True):
            response = choose.run()
            if response == gtk.RESPONSE_OK:
                filename = choose.get_filename()
                if filename == None:
                    continue
                if os.path.splitext(filename)[1] != ".grdb":
                    filename = filename + ".grdb"
                choose.destroy()
                try:
                    self.state.db.close()
                except:
                    pass
                factory = GrampsDb.gramps_db_factory
                self.state.change_database(factory(const.app_gramps)())
                self.uistate.clear_history()
                self.read_file(filename)
                self.state.signal_change()
                self.change_page(None, None)
                # Add the file to the recent items
                RecentFiles.recent_files(filename, const.app_gramps)
                self.recent_manager.build()
                return True
            else:
                choose.destroy()
                return False
        choose.destroy()
        return False
        
    def open_native(self, filename, filetype):
        """
        Open native database and return the status.
        """
        
        (the_path, the_file) = os.path.split(filename)
        Config.set(Config.RECENT_IMPORT_DIR,the_path)
        
        factory = GrampsDb.gramps_db_factory
        success = False
        if filetype == const.app_gramps:
            self.state.change_database(factory(db_type = const.app_gramps)())
            success = self.read_file(filename) #, update_msg)
            self.state.signal_change()
            self.change_page(None, None)
        elif filetype == const.app_gramps_xml:
            self.state.change_database(factory(db_type = const.app_gramps_xml)())
            success = self.read_file(filename)
            self.state.signal_change()
            self.change_page(None, None)
        elif filetype == const.app_gedcom:
            self.state.change_database(factory(db_type = const.app_gedcom)())
            success = self.read_file(filename)
            self.state.signal_change()
            self.change_page(None, None)

        if success:
            # Add the file to the recent items
            RecentFiles.recent_files(filename, filetype)
            self.recent_manager.build()

        self.actiongroup.set_visible(True)
        self.uistate.clear_history()
        return success

    def read_file(self, filename, callback=None):
        mode = "w"
        filename = os.path.normpath(os.path.abspath(filename))

        if os.path.isdir(filename):
            QuestionDialog.ErrorDialog(
                _('Cannot open database'), 
                _('The selected file is a directory, not '
                  'a file.\nA GRAMPS database must be a file.'))
            return False
        elif os.path.exists(filename):
            if not os.access(filename, os.R_OK):
                QuestionDialog.ErrorDialog(
                    _('Cannot open database'), 
                    _('You do not have read access to the selected '
                      'file.'))
                return False
            elif not os.access(filename, os.W_OK):
                mode = "r"
                QuestionDialog.WarningDialog(
                    _('Read only database'), 
                    _('You do not have write access '
                      'to the selected file.'))

        try:
            os.chdir(os.path.dirname(filename))
        except:
            print "could not change directory"


        # emit the database change signal so the that models do not
        # attempt to update the screen while we are loading the
        # new data
        
        self.state.emit('database-changed', (GrampsDb.GrampsDbBase(), ))

        try:
            if self.load_database(filename, callback, mode=mode):
                if filename[-1] == '/':
                    filename = filename[:-1]
                name = os.path.basename(filename)
                if self.state.db.readonly:
                    msg =  "%s (%s) - GRAMPS" % (name, _('Read Only'))
                    self.uistate.window.set_title(msg)
                else:
                    msg = "%s - GRAMPS" % name
                    self.uistate.window.set_title(msg)
            else:
                Config.set(Config.RECENT_FILE,"")
                QuestionDialog.ErrorDialog(
                    _('Cannot open database'), 
                    _('The database file specified could not be opened.'))
                return False
        except ( IOError, OSError, Errors.FileVersionError), msg:
            QuestionDialog.ErrorDialog(_('Cannot open database'), str(msg))
            return False
        except (db.DBAccessError, db.DBError), msg:
            QuestionDialog.ErrorDialog(
                _('Cannot open database'), 
                _('%s could not be opened.' % filename) + '\n' + msg[1])
            return False
        except Exception:
            log.error("Failed to open database.", exc_info=True)
            return False
        
        # Undo/Redo always start with standard labels and insensitive state
        #self.undo_callback(None)
        #self.redo_callback(None)
        self.file_loaded = True
        self.actiongroup.set_visible(True)
        return True

    def load_database(self, name, callback=None, mode="w"):
        self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.progress.show()
        if not self.state.db.load(name, self.uistate.pulse_progressbar, mode):
            return False
        self.progress.hide()
        return self.post_load(name, callback)

    def post_load(self, name, callback=None):
        if not self.state.db.version_supported():
            raise Errors.FileVersionError(
                    "The database version is not supported by this "
                    "version of GRAMPS.\nPlease upgrade to the "
                    "corresponding version or use XML for porting"
                    "data between different database versions.")
        
        self.state.db.set_save_path(name)

        res = self.state.db.get_researcher()
        owner = GrampsCfg.get_researcher()
        if res.get_name() == "" and owner.get_name():
            self.state.db.set_researcher(owner)

        self.setup_bookmarks()

        self.state.db.request_rebuild()

        Config.set(Config.RECENT_FILE,name)
    
        self.relationship = self.RelClass(self.state.db)
        self.state.change_active_person(self.state.db.find_initial_person())
        self.change_page(None, None)
        self.state.db.undo_callback = self.change_undo_label
        self.state.db.redo_callback = self.change_redo_label
        self.actiongroup.set_visible(True)
        self.window.window.set_cursor(None)
        return True

    def change_undo_label(self, label):
        self.uimanager.remove_action_group(self.undoactions)
        self.undoactions = gtk.ActionGroup('Undo')
        if label:
            self.undoactions.add_actions([
                ('Undo', gtk.STOCK_UNDO, label, '<control>z', None, self.undo)])
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
        ScratchPad.ScratchPadWindow(self.state, self.uistate)

    def undo(self, obj):
        self.state.db.undo()

    def redo(self, obj):
        self.state.db.redo()

    def export_data(self, obj):
        import Exporter
        Exporter.Exporter(self.state, self.uistate)

    def import_data(self, obj):
        choose = gtk.FileChooserDialog(_('GRAMPS: Import database'), 
                                           self.uistate.window, 
                                           gtk.FILE_CHOOSER_ACTION_OPEN, 
                                           (gtk.STOCK_CANCEL, 
                                            gtk.RESPONSE_CANCEL, 
                                            gtk.STOCK_OPEN, 
                                            gtk.RESPONSE_OK))
        choose.set_local_only(False)
        # Always add automatic (macth all files) filter
        add_all_files_filter(choose)
        add_grdb_filter(choose)
        add_xml_filter(choose)
        add_gedcom_filter(choose)

        format_list = [const.app_gramps,const.app_gramps_xml,const.app_gedcom]

        # Add more data type selections if opening existing db
        for data in import_list:
            mime_filter = data[1]
            mime_type = data[2]
            native_format = data[3]
            format_name = data[4]

            if not native_format:
                choose.add_filter(mime_filter)
                format_list.append(mime_type)
                _KNOWN_FORMATS[mime_type] = format_name

        (box, type_selector) = format_maker(format_list)
        choose.set_extra_widget(box)

        # Suggested folder: try last open file, import, then last export, 
        # then home.
        default_dir = Config.get(Config.RECENT_IMPORT_DIR)
        if len(default_dir)<=1:
            base_path = os.path.split(Config.get(Config.RECENT_FILE))[0]
            default_dir = base_path + os.path.sep
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_EXPORT_DIR)
        if len(default_dir)<=1:
            default_dir = '~/'

        choose.set_current_folder(default_dir)
        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = choose.get_filename()
            filetype = type_selector.get_value()
            if filetype == 'auto':
                try:
                    filetype = Mime.get_type(filename)
                except RuntimeError, msg:
                    QuestionDialog.ErrorDialog(
                        _("Could not open file: %s") % filename, 
                        str(msg))
                    return False
                    
            # First we try our best formats
            if filetype in (const.app_gramps, 
                            const.app_gramps_xml, 
                            const.app_gedcom):
                self._do_import(choose, 
                                GrampsDb.gramps_db_reader_factory(filetype), 
                                filename)
                return True

            # Then we try all the known plugins
            (the_path, the_file) = os.path.split(filename)
            Config.set(Config.RECENT_IMPORT_DIR,the_path)
            for (importData, mime_filter, mime_type, 
                 native_format, format_name) in import_list:
                if filetype == mime_type or the_file == mime_type:
                    self._do_import(choose, importData, filename)
                    return True

            # Finally, we give up and declare this an unknown format
            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename, 
                _('File type "%s" is unknown to GRAMPS.\n\n'
                  'Valid types are: GRAMPS database, GRAMPS XML, '
                  'GRAMPS package, and GEDCOM.') % filetype)

        choose.destroy()
        return False

    def _do_import(self, dialog, importer, filename):
        dialog.destroy()
        self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.progress.show()
        importer(self.state.db, filename, self.uistate.pulse_progressbar)
        self.uistate.clear_history()
        self.progress.hide()
        self.window.window.set_cursor(None)

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
                                              Report.standalone_categories, 
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
                    (item[0], item[1], item[2], item[4], item[3]))
            else:
                hash_data[category] = [
                    (item[0], item[1], item[2], item[4], item[3])]
                
        # Sort categories, skipping the unsupported
        catlist = [item for item in hash_data.keys() if item != Plugins.UNSUPPORTED]
        catlist.sort()
        for key in catlist:
            new_key = key.replace(' ', '-')
            f.write('<menu action="%s">' % new_key)
            actions.append((new_key, None, key))
            lst = hash_data[key]
            lst.sort(by_menu_name)
            for name in lst:
                new_key = name[2].replace(' ', '-')
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
            lst = hash_data[key]
            lst.sort(by_menu_name)
            for name in lst:
                new_key = name[2].replace(' ', '-')
                f.write('<menuitem action="%s"/>' % new_key)
                actions.append((new_key, None, name[2], None, None, 
                                func(name, self.state, self.uistate)))
            f.write('</menu>')

        f.write('</menu></menubar></ui>')
        return (f.getvalue(), actions)

def by_menu_name(a, b):
    return cmp(a[2], b[2])

def add_all_files_filter(chooser):
    """
    Add an all-permitting filter to the file chooser dialog.
    """
    mime_filter = gtk.FileFilter()
    mime_filter.set_name(_('All files'))
    mime_filter.add_pattern('*')
    chooser.add_filter(mime_filter)

def add_gramps_files_filter(chooser):
    """
    Add an all-GRAMPS filter to the file chooser dialog.
    """
    mime_filter = gtk.FileFilter()
    mime_filter.set_name(_('All GRAMPS files'))
    mime_filter.add_mime_type(const.app_gramps)
    mime_filter.add_mime_type(const.app_gramps_xml)
    mime_filter.add_mime_type(const.app_gedcom)
    chooser.add_filter(mime_filter)

def add_grdb_filter(chooser):
    """
    Add a GRDB filter to the file chooser dialog.
    """
    mime_filter = gtk.FileFilter()
    mime_filter.set_name(_('GRAMPS databases'))
    mime_filter.add_mime_type(const.app_gramps)
    chooser.add_filter(mime_filter)

def add_xml_filter(chooser):
    """
    Add a GRAMPS XML filter to the file chooser dialog.
    """
    mime_filter = gtk.FileFilter()
    mime_filter.set_name(_('GRAMPS XML databases'))
    mime_filter.add_mime_type(const.app_gramps_xml)
    chooser.add_filter(mime_filter)

def add_gedcom_filter(chooser):
    """
    Add a GEDCOM filter to the file chooser dialog.
    """
    mime_filter = gtk.FileFilter()
    mime_filter.set_name(_('GEDCOM files'))
    mime_filter.add_mime_type(const.app_gedcom)
    chooser.add_filter(mime_filter)

def make_report_callback(lst, dbstate, uistate):
    return lambda x: Report.report(dbstate.db, dbstate.get_active_person(), 
                                   lst[0], lst[1], lst[2], lst[3], lst[4])

def make_tool_callback(lst, dbstate, uistate):
    return lambda x: Tool.gui_tool(dbstate, uistate,  
                                   lst[0], lst[1], lst[2], lst[3], lst[4], 
                                   dbstate.db.request_rebuild)

#-------------------------------------------------------------------------
#
# Format selectors and filters
#
#-------------------------------------------------------------------------
class GrampsFormatWidget(gtk.ComboBox):

    def __init__(self):
        gtk.ComboBox.__init__(self, model=None)

    def set(self, format_list):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.format_list = format_list
        
        for format, label in format_list:
            self.store.append(row=[label])
        self.set_active(False)

    def get_value(self):
        active = self.get_active()
        if active < 0:
            return None
        return self.format_list[active][0]

def format_maker(formats):
    """
    A factory function making format selection widgets.
    
    Accepts a list of formats to include into selector.
    The auto selection is always added as the first one.
    The returned box contains both the label and the selector.
    """
    format_list = [ ('auto', _('Automatically detected')) ]
    for format in formats:
        if _KNOWN_FORMATS.has_key(format):
            format_list.append( (format, _KNOWN_FORMATS[format]) )

    type_selector = GrampsFormatWidget()
    type_selector.set(format_list)

    box = gtk.HBox()
    label = gtk.Label(_('Select file _type:'))
    label.set_use_underline(True)
    label.set_mnemonic_widget(type_selector)
    box.pack_start(label, expand=False, fill=False, padding=6)
    box.add(type_selector)
    box.show_all()
    return (box, type_selector)
