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

# $Id$

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gobject
import gnome

try:
    from gnomevfs import get_mime_type
except:
    from gnome.vfs import get_mime_type
    
#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
import const
import QuestionDialog
import PluginMgr
import GrampsBSDDB
import GrampsXMLDB
import GrampsGEDDB
import GrampsKeys
import RecentFiles
import ReadGrdb
import WriteGrdb
import WriteXML
import WriteGedcom

from bsddb import db

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
        
#-------------------------------------------------------------------------
#
# DbPrompter
#
#-------------------------------------------------------------------------
class DbPrompter:
    """Make sure a database is opened"""
    
    def __init__(self,parent,want_new,parent_window=None):
        self.parent = parent
        self.parent_window = parent_window
        opendb = gtk.glade.XML(const.gladeFile, "opendb","gramps")
        top = opendb.get_widget('opendb')
        if parent_window:
            top.set_transient_for(parent_window)
        title = opendb.get_widget('title')

        Utils.set_titles(top,title,_('Open a database'))

        new = opendb.get_widget("new")
        new.set_active(want_new)

        while 1:
            top.show()
            response = top.run()
            top.hide()
            if response == gtk.RESPONSE_OK:
                if new.get_active():
                    prompter = NewNativeDbPrompter(self.parent,
                                                   self.parent_window)
                else:
                    prompter = ExistingDbPrompter(self.parent,
                                                  self.parent_window)
                if prompter.chooser():
                    break
            elif response == gtk.RESPONSE_CANCEL:
                break
            elif response == gtk.RESPONSE_HELP:
                try:
                    gnome.help_display('gramps-manual','choose-db-start')
                except gobject.GError,msg:
                    QuestionDialog.ErrorDialog(_('Help not available'),msg)

        top.destroy()
        if response == gtk.RESPONSE_CANCEL:
            gtk.main_quit()

#-------------------------------------------------------------------------
#
# ExistingDbPrompter
#
#-------------------------------------------------------------------------
class ExistingDbPrompter:
    """
    This class allows to open an existing database. 
    
    Any data format is allowed. The available formats are obtained
    from the plugins. If the selected format is non-native (non-grdb)
    then the call is made to set up a new native grdb database. 
    
    """
    
    def __init__(self,state):
        self.state = state
        self.parent_window = state.window

    def chooser(self):
        """
        Select the new file. 
        Return 1 when selection is made and 0 otherwise.
        """
        choose = gtk.FileChooserDialog(_('GRAMPS: Open database'),
                                           self.parent_window,
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
                    return self.open_native(self.state,filename,filetype)
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
            for (importData,mime_filter,mime_type,native_format,format_name) in PluginMgr.import_list:
                if filetype == mime_type or the_file == mime_type:
                    QuestionDialog.OkDialog(
                        _("Opening non-native format"), 
                        _("New GRAMPS database has to be set up "
                          "when opening non-native formats. The "
                          "following dialog will let you select "
                          "the new database."),
                        self.parent_window)
                    prompter = NewNativeDbPrompter(self.parent,self.parent_window)
                    if prompter.chooser():
                        importData(self.state.db,filename)
                        #self.parent.import_tool_callback()
                        return True
                    else:
                        return False
            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename,
                _('File type "%s" is unknown to GRAMPS.\n\nValid types are: GRAMPS database, GRAMPS XML, GRAMPS package, and GEDCOM.') % filetype)
        choose.destroy()
        return False

#-------------------------------------------------------------------------
#
# ImportDbPrompter
#
#-------------------------------------------------------------------------
class ImportDbPrompter:
    """
    This class allows to import a database. The data is imported into
    the currently opened database, so we don't have to worry about
    setting up the native database.
    
    Any data format is allowed. The available formats are obtained
    from the plugins. 
    
    """
    
    def __init__(self,parent,parent_window=None):
        self.parent = parent
        self.parent_window = parent_window

    def chooser(self):
        """
        Select the new file. 
        Return 1 when selection is made and 0 otherwise.
        """
        choose = gtk.FileChooserDialog(_('GRAMPS: Import database'),
                                           self.parent_window,
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
        for (importData,mime_filter,mime_type,native_format,format_name) in PluginMgr.import_list:
            if not native_format:
                choose.add_filter(mime_filter)
                format_list.append(mime_type)
                _KNOWN_FORMATS[mime_type] = format_name

        (box,type_selector) = format_maker(format_list)
        choose.set_extra_widget(box)

        # Suggested folder: try last open file, import, then last export, 
        # then home.
        default_dir = GrampsKeys.get_last_import_dir()
        if len(default_dir)<=1:
            default_dir = os.path.split(GrampsKeys.get_lastfile())[0] + os.path.sep
        if len(default_dir)<=1:
            default_dir = GrampsKeys.get_last_export_dir()
        if len(default_dir)<=1:
            default_dir = '~/'

        choose.set_current_folder(default_dir)
        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = choose.get_filename()
            filetype = type_selector.get_value()
            if filetype == 'auto':
                try:
                    filetype = get_mime_type(filename)
                except RuntimeError,msg:
                    QuestionDialog.ErrorDialog(
                        _("Could not open file: %s") % filename,
                        str(msg))
                    return False
                    
            if filetype == const.app_gramps:
                choose.destroy()
                ReadGrdb.importData(self.parent.db,filename)
                self.parent.import_tool_callback()
                return True
            elif filetype == const.app_gramps_xml:
                choose.destroy()
                import ReadXML
                ReadXML.importData(self.parent.db,filename,self.parent.update_bar)
                return True
            elif filetype == const.app_gedcom:
                choose.destroy()
                import ReadGedcom
                ReadGedcom.importData(self.parent.db,filename)
                return True

            (the_path,the_file) = os.path.split(filename)
            GrampsKeys.save_last_import_dir(the_path)
            for (importData,mime_filter,mime_type,native_format,format_name) in PluginMgr.import_list:
                if filetype == mime_type or the_file == mime_type:
                    choose.destroy()
                    importData(self.parent.db,filename)
                    self.parent.import_tool_callback()
                    return True
            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename,
                _('File type "%s" is unknown to GRAMPS.\n\nValid types are: GRAMPS database, GRAMPS XML, GRAMPS package, and GEDCOM.') % filetype)
        choose.destroy()
        return False

#-------------------------------------------------------------------------
#
# NewNativeDbPrompter
#
#-------------------------------------------------------------------------
class NewNativeDbPrompter:
    """
    This class allows to set up a new empty native (grdb) database.
    The filename is forced to have an '.grdb' extension. If not given,
    it is appended. 
    """
    
    def __init__(self,parent,parent_window=None):
        self.parent = parent
        self.parent_window = parent_window

    def chooser(self):
        """
        Select the new file. Suggest the Untitled_X.grdb name.
        Return 1 when selection is made and 0 otherwise.
        """
        choose = gtk.FileChooserDialog(_('GRAMPS: Create GRAMPS database'),
                                           self.parent_window,
                                           gtk.FILE_CHOOSER_ACTION_SAVE,
                                           (gtk.STOCK_CANCEL,
                                            gtk.RESPONSE_CANCEL,
                                            gtk.STOCK_OPEN,
                                            gtk.RESPONSE_OK))
        self.parent.clear_database()

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
                    self.parent.db.close()
                except:
                    pass
                self.parent.db = GrampsBSDDB.GrampsBSDDB()
                self.read_file(filename)
                # Add the file to the recent items
                RecentFiles.recent_files(filename,const.app_gramps)
                self.parent.build_recent_menu()
                return True
            else:
                choose.destroy()
                return False
        choose.destroy()
        return False

#-------------------------------------------------------------------------
#
# NewSaveasDbPrompter
#
#-------------------------------------------------------------------------
class NewSaveasDbPrompter:
    """
    This class allows to select a new empty InMemory database and then
    to save current data into it and then continue editing it.
    """
    
    def __init__(self,parent,parent_window=None):
        self.parent = parent
        self.parent_window = parent_window

    def chooser(self):
        """
        Select the new file. Suggest the Untitled_X.grdb name.
        Return 1 when selection is made and 0 otherwise.
        """
        choose = gtk.FileChooserDialog(_('GRAMPS: Select filename for a new database'),
                                           self.parent_window,
                                           gtk.FILE_CHOOSER_ACTION_SAVE,
                                           (gtk.STOCK_CANCEL,
                                            gtk.RESPONSE_CANCEL,
                                            gtk.STOCK_SAVE,
                                            gtk.RESPONSE_OK))
        choose.set_local_only(False)
        (box,type_selector) = format_maker([const.app_gramps,
                                    const.app_gramps_xml,
                                    const.app_gedcom])
        choose.set_extra_widget(box)

        # Always add automatic (macth all files) filter
        add_all_files_filter(choose)
        add_gramps_files_filter(choose)
        add_grdb_filter(choose)
        add_xml_filter(choose)
        add_gedcom_filter(choose)

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
                filetype = type_selector.get_value()
                if filetype == 'auto':
                    new_file = open(filename, "w")
                    new_file.close()
                    filetype = get_mime_type(filename)
                (the_path,the_file) = os.path.split(filename)
                choose.destroy()
                if filetype not in [const.app_gramps,const.app_gramps_xml,
                                    const.app_gedcom]:
                    QuestionDialog.ErrorDialog(
                        _("Could not save file: %s") % filename,
                        _('File type "%s" is unknown to GRAMPS.\n\nValid types are: GRAMPS database, GRAMPS XML, GRAMPS package, and GEDCOM.') % filetype)
                    return False
                if filetype == const.app_gramps:
                    WriteGrdb.exportData(self.parent.db,filename,None,None)
                    self.parent.db.close()
                    self.parent.db = GrampsBSDDB.GrampsBSDDB()
                elif filetype == const.app_gramps_xml:
                    WriteXML.exportData(self.parent.db,filename,None,None)
                    self.parent.db.close()
                    self.parent.db = GrampsXMLDB.GrampsXMLDB()
                elif filetype == const.app_gedcom:
                    WriteGedcom.exportData(self.parent.db,filename,None,None)
                    self.parent.db.close()
                    self.parent.db = GrampsGEDDB.GrampsGEDDB()
                self.read_file(filename)
                # Add the file to the recent items
                RecentFiles.recent_files(filename,const.app_gramps)
                self.parent.build_recent_menu()
                return True
            else:
                choose.destroy()
                return False
        choose.destroy()
        return False

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
                return False
        except ( IOError, OSError, Errors.FileVersionError), msg:
            ErrorDialog(_('Cannot open database'),str(msg))
            return False
        except (db.DBAccessError,db.DBError), msg:
            ErrorDialog(_('Cannot open database'),
                        _('%s could not be opened.' % filename) + '\n' + msg[1])
            return False
        except Exception:
            DisplayTrace.DisplayTrace()
            return False
        
        return True

    def load_database(self,name,callback=None,mode="w"):

        filename = name

        if self.state.db.load(filename,callback,mode) == 0:
            return 0

        #val = self.post_load(name,callback)
        return val


    def open_native(self,filename,filetype):
        """
        Open native database and return the status.
        """
        
        (the_path,the_file) = os.path.split(filename)
        GrampsKeys.save_last_import_dir(the_path)
        
        success = False
        if filetype == const.app_gramps:
            state.db = GrampsBSDDB.GrampsBSDDB()
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
            state.db = GrampsXMLDB.GrampsXMLDB()
            success = self.read_file(filename)
        elif filetype == const.app_gedcom:
            state.db = GrampsGEDDB.GrampsGEDDB()
            success = self.read_file(filename)

        #if success:
        # Add the file to the recent items
        #RecentFiles.recent_files(filename,filetype)
        #parent.build_recent_menu()

        return success




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
