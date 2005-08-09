#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------

from gettext import gettext as _
from bsddb import db
import os

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk
try:
    from gnomevfs import get_mime_type
except:
    from gnome.vfs import get_mime_type

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import DbState
import DbPrompter
import const
import PluginMgr
import GrampsKeys
import GrampsDbBase
import GrampsBSDDB
import GrampsGEDDB
import GrampsXMLDB
import GrampsCfg
import Errors
import DisplayTrace
import Utils

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
    <menuitem action="OpenRecent"/>
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
  </menu>
  <menu action="GoMenu">
    <placeholder name="CommonGo"/>
  </menu>
  <menu action="BookMenu">
    <menuitem action="AddBook"/>
    <menuitem action="EditBook"/>
    <menuitem action="GoToBook"/>
  </menu>
  <menu action="ReportsMenu">
  </menu>
  <menu action="ToolsMenu">
  </menu>
  <menu action="WindowsMenu">
  </menu>
  <menu action="HelpMenu">
    <menuitem action="About"/>
  </menu>
</menubar>
<toolbar name="ToolBar">
  <toolitem action="New"/>  
  <toolitem action="Open"/>  
  <separator/>
  <placeholder name="CommonNavigation"/>
  <separator/>
  <toolitem action="ScratchPad"/>  
  <toolitem action="Reports"/>  
  <toolitem action="Tools"/>  
  <separator/>
  <placeholder name="CommonEdit"/>
</toolbar>
</ui>
'''

class ViewManager:

    def __init__(self):

        self.active_page = None
        self.views = []
        self.window = gtk.Window()
        self.window.connect('destroy', lambda w: gtk.main_quit())
        self.window.set_size_request(775,500)

        self.statusbar = gtk.Statusbar()
        self.state = DbState.DbState(self.window,self.statusbar)

        self.RelClass = PluginMgr.relationship_class

        vbox = gtk.VBox()
        self.window.add(vbox)
        hbox = gtk.HBox()
        hbox.set_border_width(4)
        self.ebox = gtk.EventBox()
        self.bbox = gtk.VBox()
        self.ebox.add(self.bbox)
        hbox.pack_start(self.ebox,False)

        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.build_ui_manager()

        hbox.pack_start(self.notebook,True)
        self.menubar = self.uimanager.get_widget('/MenuBar')
        self.toolbar = self.uimanager.get_widget('/ToolBar')
        vbox.pack_start(self.menubar, False)
        vbox.pack_start(self.toolbar, False)
        vbox.add(hbox)
        vbox.pack_end(self.statusbar,False)

        self.notebook.connect('switch-page',self.change_page)

        self.window.show_all()

    def init_interface(self):
        self.create_pages()
        self.change_page(None,None,0)

    def set_color(self,obj):
        style = obj.get_style().copy()
        new_color = style.bg[gtk.STATE_ACTIVE]
        style.bg[gtk.STATE_NORMAL] = new_color
        style.bg[gtk.STATE_PRELIGHT] = new_color
        style.bg[gtk.STATE_ACTIVE] = new_color
        style.bg[gtk.STATE_INSENSITIVE] = new_color
        style.bg[gtk.STATE_SELECTED] = new_color
        obj.set_style(style)

    def build_ui_manager(self):
        self.merge_id = 0
        self.uimanager = gtk.UIManager()

        accelgroup = self.uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)

        self.actiongroup = gtk.ActionGroup('MainWindow')
        self.actiongroup.add_actions([
            # Name         Stock Icon                 Label
            ('FileMenu',   None,                      '_File'),
            ('New',        gtk.STOCK_NEW,             '_New', "<control>n", None, self.on_new_activate),
            ('Open',       gtk.STOCK_OPEN,            '_Open', "<control>o", None, self.on_open_activate),
            ('OpenRecent', gtk.STOCK_OPEN,            'Open _Recent'),
            ('Import',     gtk.STOCK_CONVERT,         '_Import'),
            ('SaveAs',     gtk.STOCK_SAVE_AS,         '_Save As'),
            ('Export',     gtk.STOCK_SAVE_AS,         '_Export'),
            ('Abandon',    gtk.STOCK_REVERT_TO_SAVED, '_Abandon changes and quit'),
            ('Quit',       gtk.STOCK_QUIT,            '_Quit', '<control>q', None, gtk.main_quit),
            ('Undo',       gtk.STOCK_UNDO,            '_Undo', '<control>z' ),
            ('Preferences',gtk.STOCK_PREFERENCES,     '_Preferences'),
            ('ColumnEdit', gtk.STOCK_PROPERTIES,      '_Column Editor'),
            ('CmpMerge',   None,                      '_Compare and merge'),
            ('FastMerge',  None,                      '_Fast merge'),
            ('ScratchPad', gtk.STOCK_PASTE,           '_ScratchPad', None, None, self.on_scratchpad),
            ('Reports',    gtk.STOCK_DND_MULTIPLE,    '_Reports'),
            ('Tools',      gtk.STOCK_EXECUTE,         '_Tools'),
            ('EditMenu',   None,                      '_Edit'),
            ('GoMenu',     None,                      '_Go'),
            ('ViewMenu',   None,                      '_View'),
            ('BookMenu',   None,                      '_Bookmarks'),
            ('AddBook',    gtk.STOCK_INDEX,           '_Add bookmark', '<control>d'),
            ('EditBook',   None,                      '_Edit bookmarks', '<control>b'),
            ('GoToBook',   gtk.STOCK_JUMP_TO,         '_Go to bookmark'),
            ('ReportsMenu',None,                      '_Reports'),
            ('ToolsMenu',  None,                      '_Tools'),
            ('WindowsMenu',None,                      '_Windows'),
            ('HelpMenu',   None,                      '_Help'),
            ('About',      gtk.STOCK_ABOUT,           '_About'),
            ])

        self.actiongroup.add_toggle_actions([
            ('Sidebar', None, '_Sidebar', None, None, self.sidebar_toggle),
            ('Toolbar', None, '_Toolbar', None, None, self.toolbar_toggle),
            ])

        merge_id = self.uimanager.add_ui_from_string(uidefault)
        self.uimanager.insert_action_group(self.actiongroup,1)

    def sidebar_toggle(self,obj):
        if obj.get_active():
            self.ebox.show()
            self.notebook.set_show_tabs(False)
        else:
            self.ebox.hide()
            self.notebook.set_show_tabs(True)

    def toolbar_toggle(self,obj):
        if obj.get_active():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    def register_view(self, view):
        self.views.append(view)

    def create_pages(self):
        self.pages = []
        index = 0
        self.set_color(self.ebox)
        for page_def in self.views:
            page = page_def(self.state)

            # create icon/label for notebook
            hbox = gtk.HBox()
            image = gtk.Image()
            image.set_from_stock(page.get_stock(),gtk.ICON_SIZE_MENU)
            hbox.pack_start(image,False)
            hbox.add(gtk.Label(page.get_title()))
            hbox.show_all()

            # create notebook page and add to notebook
            page_display = page.get_display()
            page_display.show_all()
            self.notebook.append_page(page_display,hbox)
            self.pages.append(page)

            # create the button add it to the sidebar
            button = gtk.Button(stock=page.get_stock(),label=page.get_title())
            button.set_border_width(4)
            button.set_relief(gtk.RELIEF_NONE)
            button.set_alignment(0,0.5)
            button.connect('clicked',lambda x,y : self.notebook.set_current_page(y),
                           index)
            self.set_color(button)
            button.show()
            index += 1
            self.bbox.pack_start(button,False)

    def change_page(self,obj,page,num):
        if self.merge_id:
            self.uimanager.remove_ui(self.merge_id)
        if self.active_page:
            self.uimanager.remove_action_group(self.active_page.get_actions())

        if len(self.pages) > 0:
            self.active_page = self.pages[num]

            self.uimanager.insert_action_group(self.active_page.get_actions(),1)
            self.merge_id = self.uimanager.add_ui_from_string(self.active_page.ui_definition())

    def on_open_activate(self,obj):

        choose = gtk.FileChooserDialog(_('GRAMPS: Open database'),
                                           self.state.window,
                                           gtk.FILE_CHOOSER_ACTION_OPEN,
                                           (gtk.STOCK_CANCEL,
                                            gtk.RESPONSE_CANCEL,
                                            gtk.STOCK_OPEN,
                                            gtk.RESPONSE_OK))

        # Always add automatic (macth all files) filter
        add_all_files_filter(choose)
        add_grdb_filter(choose)
        add_xml_filter(choose)
        add_gedcom_filter(choose)

        format_list = [const.app_gramps,const.app_gramps_xml,const.app_gedcom]
        # Add more data type selections if opening existing db
        for (importData,mime_filter,mime_type,native_format,format_name) in PluginMgr.import_list:
            if not native_format:
                choose.add_filter(mime_filter)
                format_list.append(mime_type)
                _KNOWN_FORMATS[mime_type] = format_name
        
        (box,type_selector) = format_maker(format_list)
        choose.set_extra_widget(box)

        # Suggested folder: try last open file, last import, last export, 
        # then home.
        default_dir = os.path.split(GrampsKeys.get_lastfile())[0] + os.path.sep
        if len(default_dir)<=1:
            default_dir = GrampsKeys.get_last_import_dir()
        if len(default_dir)<=1:
            default_dir = GrampsKeys.get_last_export_dir()
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
                filetype = get_mime_type(filename)
            (the_path,the_file) = os.path.split(filename)
            choose.destroy()
            if filetype in [const.app_gramps,const.app_gramps_xml,
                                const.app_gedcom]:
    
                try:
                    return self.open_native(filename,filetype)
                except db.DBInvalidArgError, msg:
                    QuestionDialog.ErrorDialog(
                        _("Could not open file: %s") % filename, msg[1])
                    return False
                except:
                    import DisplayTrace
                    DisplayTrace.DisplayTrace()
                    return False

            # The above native formats did not work, so we need to 
            # look up the importer for this format
            # and create an empty native database to import data in
#             for (importData,mime_filter,mime_type,native_format,format_name) in PluginMgr.import_list:
#                 if filetype == mime_type or the_file == mime_type:
#                     QuestionDialog.OkDialog(
#                         _("Opening non-native format"), 
#                         _("New GRAMPS database has to be set up "
#                           "when opening non-native formats. The "
#                           "following dialog will let you select "
#                           "the new database."),
#                         self.state.window)
#                     prompter = NewNativeDbPrompter(self.parent,self.parent_window)
#                     if prompter.chooser():
#                         importData(self.state.db,filename)
#                         #self.parent.import_tool_callback()
#                         return True
#                     else:
#                         return False
            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename,
                _('File type "%s" is unknown to GRAMPS.\n\nValid types are: GRAMPS database, GRAMPS XML, GRAMPS package, and GEDCOM.') % filetype)
        choose.destroy()
        return False

    def on_new_activate(self,obj):

        choose = gtk.FileChooserDialog(_('GRAMPS: Create GRAMPS database'),
                                           self.state.window,
                                           gtk.FILE_CHOOSER_ACTION_SAVE,
                                           (gtk.STOCK_CANCEL,
                                            gtk.RESPONSE_CANCEL,
                                            gtk.STOCK_OPEN,
                                            gtk.RESPONSE_OK))

        # Always add automatic (macth all files) filter
        add_all_files_filter(choose)
        add_grdb_filter(choose)

        # Suggested folder: try last open file, import, then last export, 
        # then home.
        default_dir = os.path.split(GrampsKeys.get_lastfile())[0] + os.path.sep
        if len(default_dir)<=1:
            default_dir = GrampsKeys.get_last_import_dir()
        if len(default_dir)<=1:
            default_dir = GrampsKeys.get_last_export_dir()
        if len(default_dir)<=1:
            default_dir = '~/'

        new_filename = Utils.get_new_filename('grdb',default_dir)
        
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
                self.state.db = GrampsBSDDB.GrampsBSDDB()
                self.read_file(filename)
                # Add the file to the recent items
                #RecentFiles.recent_files(filename,const.app_gramps)
                #self.parent.build_recent_menu()
                return True
            else:
                choose.destroy()
                return False
        choose.destroy()
        return False
        
    def open_native(self,filename,filetype):
        """
        Open native database and return the status.
        """
        
        (the_path,the_file) = os.path.split(filename)
        GrampsKeys.save_last_import_dir(the_path)
        
        success = False
        if filetype == const.app_gramps:
            self.state.db = GrampsBSDDB.GrampsBSDDB()
            msgxml = gtk.glade.XML(const.gladeFile, "load_message","gramps")
            msg_top = msgxml.get_widget('load_message')
            msg_label = msgxml.get_widget('message')
            
            def update_msg(msg):
                msg_label.set_text("<i>%s</i>" % msg)
                msg_label.set_use_markup(True)
                while gtk.events_pending():
                    gtk.main_iteration()

            success = self.read_file(filename,update_msg)
            msg_top.destroy()
        elif filetype == const.app_gramps_xml:
            self.state.db = GrampsXMLDB.GrampsXMLDB()
            success = self.read_file(filename)
        elif filetype == const.app_gedcom:
            self.state.db = GrampsGEDDB.GrampsGEDDB()
            success = self.read_file(filename)

        #if success:
        # Add the file to the recent items
        #RecentFiles.recent_files(filename,filetype)
        #parent.build_recent_menu()

        return success

    def read_file(self,filename,callback=None):
        mode = "w"
        filename = os.path.normpath(os.path.abspath(filename))
        
        if os.path.isdir(filename):
            ErrorDialog(_('Cannot open database'),
                        _('The selected file is a directory, not '
                          'a file.\nA GRAMPS database must be a file.'))
            return 0
        elif os.path.exists(filename):
            if not os.access(filename,os.R_OK):
                ErrorDialog(_('Cannot open database'),
                            _('You do not have read access to the selected '
                              'file.'))
                return 0
            elif not os.access(filename,os.W_OK):
                mode = "r"
                WarningDialog(_('Read only database'),
                              _('You do not have write access to the selected '
                                'file.'))

        try:
            if self.load_database(filename,callback,mode=mode) == 1:
                if filename[-1] == '/':
                    filename = filename[:-1]
                name = os.path.basename(filename)
                if self.state.db.readonly:
                    self.state.window.set_title("%s (%s) - GRAMPS" % (name,_('Read Only')))
                else:
                    self.state.window.set_title("%s - GRAMPS" % name)
            else:
                GrampsKeys.save_last_file("")
                ErrorDialog(_('Cannot open database'),
                            _('The database file specified could not be opened.'))
                return 0
        except ( IOError, OSError, Errors.FileVersionError), msg:
            ErrorDialog(_('Cannot open database'),str(msg))
            return 0
        except (db.DBAccessError,db.DBError), msg:
            ErrorDialog(_('Cannot open database'),
                        _('%s could not be opened.' % filename) + '\n' + msg[1])
            return 0
        except Exception:
            DisplayTrace.DisplayTrace()
            return 0
        
        # Undo/Redo always start with standard labels and insensitive state
        #self.undo_callback(None)
        #self.redo_callback(None)
        #self.goto_active_person()
        return 1

    def load_database(self,name,callback=None,mode="w"):

        filename = name

        if self.state.db.load(filename,callback,mode) == 0:
            return 0
        val = self.post_load(name,callback)
        return val

    def post_load(self,name,callback=None):
        if not self.state.db.version_supported():
            raise Errors.FileVersionError(
                    "The database version is not supported by this version of GRAMPS.\n"
                    "Please upgrade to the corresponding version or use XML for porting"
                    "data between different database versions.")
        
        self.state.db.set_save_path(name)

        res = self.state.db.get_researcher()
        owner = GrampsCfg.get_researcher()
        if res.get_name() == "" and owner.get_name():
            self.state.db.set_researcher(owner)

        #self.setup_bookmarks()

        #self.state.db.set_undo_callback(self.undo_callback)
        #self.state.db.set_redo_callback(self.redo_callback)

        if self.state.db.need_upgrade():
            if callback:
                callback(_('Upgrading database...'))
            self.state.db.upgrade()

        GrampsKeys.save_last_file(name)
    
        self.relationship = self.RelClass(self.state.db)
        self.state.emit("database-changed", (self.state.db,))

        #self.change_active_person(self.find_initial_person())
        #self.goto_active_person()
        
        #if callback:
        #    callback(_('Setup complete'))
        #self.enable_buttons(True)
        return 1

    def on_scratchpad(self,obj):
        import ScratchPad
        ScratchPad.ScratchPadWindow(self.db, self)

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

#-------------------------------------------------------------------------
#
# Format selectors and filters
#
#-------------------------------------------------------------------------
class GrampsFormatWidget(gtk.ComboBox):

    def __init__(self):
        gtk.ComboBox.__init__(self,model=None)

    def set(self,format_list):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        self.format_list = format_list
        
        for format,label in format_list:
            self.store.append(row=[label])
        self.set_active(0)

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
    format_list = [ ('auto',_('Automatically detected')) ]
    for format in formats:
        if _KNOWN_FORMATS.has_key(format):
            format_list.append( (format,_KNOWN_FORMATS[format]) )

    type_selector = GrampsFormatWidget()
    type_selector.set(format_list)

    box = gtk.HBox()
    label = gtk.Label(_('Select file _type:'))
    label.set_use_underline(True)
    label.set_mnemonic_widget(type_selector)
    box.pack_start(label,expand=False,fill=False,padding=6)
    box.add(type_selector)
    box.show_all()
    return (box,type_selector)

