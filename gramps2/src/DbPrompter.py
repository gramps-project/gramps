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
    
    def __init__(self,parent,parent_window=None):
        self.parent = parent
        self.parent_window = parent_window

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
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('All files'))
        mime_filter.add_pattern('*')
        choose.add_filter(mime_filter)
        
        # Always add native format filter
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('GRAMPS databases'))
        mime_filter.add_mime_type(const.app_gramps)
        choose.add_filter(mime_filter)

        # Always add native format filter
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('GRAMPS XML databases'))
        mime_filter.add_mime_type(const.app_gramps_xml)
        choose.add_filter(mime_filter)

        # Always add native format filter
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('GEDCOM files'))
        mime_filter.add_mime_type(const.app_gedcom)
        choose.add_filter(mime_filter)

        # Add more data type selections if opening existing db
        for (importData,mime_filter,mime_type,native_format) in PluginMgr.import_list:
            if not native_format:
                choose.add_filter(mime_filter)
        
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
            filetype = get_mime_type(filename)
            (the_path,the_file) = os.path.split(filename)
            choose.destroy()
            try:
                if open_native(self.parent,filename,filetype):
                    return True
            except:
                QuestionDialog.ErrorDialog(
                    _("Could not open file: %s") % filename)
                return False

            # The above native formats did not work, so we need to 
            # look up the importer for this format
            # and create an empty native database to import data in
            for (importData,mime_filter,mime_type,native_format) in PluginMgr.import_list:
                if filetype == mime_type or the_file == mime_type:
                    QuestionDialog.OkDialog(
                        _("Opening non-native format"), 
                        _("New gramps database has to be set up "
                          "when opening non-native formats. The "
                          "following dialog will let you select "
                          "the new database."),
                        self.parent_window)
                    prompter = NewNativeDbPrompter(self.parent,self.parent_window)
                    if prompter.chooser():
                        importData(self.parent.db,filename)
                        self.parent.import_tool_callback()
                        return True
                    else:
                        return False
            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename,
                _('The type "%s" is not in the list of known file types') % filetype )
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
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('All files'))
        mime_filter.add_pattern('*')
        choose.add_filter(mime_filter)
        
        # Always add native format filter
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('GRAMPS databases'))
        mime_filter.add_mime_type(const.app_gramps)
        choose.add_filter(mime_filter)

        # Add more data type selections if opening existing db
        for (importData,mime_filter,mime_type,native_format) in PluginMgr.import_list:
            choose.add_filter(mime_filter)
        
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
            filetype = get_mime_type(filename)

            if filetype == 'application/x-gramps':
                choose.destroy()
                ReadGrdb.importData(self.parent.db,filename)
                self.parent.import_tool_callback()
                return True

            (the_path,the_file) = os.path.split(filename)
            GrampsKeys.save_last_import_dir(the_path)
            for (importData,mime_filter,mime_type,native_format) in PluginMgr.import_list:
                if filetype == mime_type or the_file == mime_type:
                    choose.destroy()
                    importData(self.parent.db,filename)
                    self.parent.import_tool_callback()
                    return True
            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename,
                _('The type "%s" is not in the list of known file types') % filetype )
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
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('All files'))
        mime_filter.add_pattern('*')
        choose.add_filter(mime_filter)
        
        # Always add native format filter
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('GRAMPS databases'))
        mime_filter.add_mime_type(const.app_gramps)
        choose.add_filter(mime_filter)

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
                self.parent.read_file(filename)
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

        # Always add automatic (macth all files) filter
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('All files'))
        mime_filter.add_pattern('*')
        choose.add_filter(mime_filter)
        
        # Always add native format filter
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('GRAMPS databases'))
        mime_filter.add_mime_type(const.app_gramps)
        choose.add_filter(mime_filter)

        # Always add native format filter
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('GRAMPS XML databases'))
        mime_filter.add_mime_type(const.app_gramps_xml)
        choose.add_filter(mime_filter)

        # Always add native format filter
        mime_filter = gtk.FileFilter()
        mime_filter.set_name(_('GEDCOM files'))
        mime_filter.add_mime_type(const.app_gedcom)
        choose.add_filter(mime_filter)

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
                os.system('touch %s' % filename)
                filetype = get_mime_type(filename)
                (the_path,the_file) = os.path.split(filename)
                choose.destroy()
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
                self.parent.read_file(filename)
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
# Helper function
#
#-------------------------------------------------------------------------
def open_native(parent,filename,filetype):
    """
    Open native database and return the status.
    """

    (the_path,the_file) = os.path.split(filename)
    GrampsKeys.save_last_import_dir(the_path)

    success = False
    if filetype == const.app_gramps:
        parent.db = GrampsBSDDB.GrampsBSDDB()
        msgxml = gtk.glade.XML(const.gladeFile, "load_message","gramps")
        msg_top = msgxml.get_widget('load_message')
        msg_label = msgxml.get_widget('message')

        def update_msg(msg):
            msg_label.set_text("<i>%s</i>" % msg)
            msg_label.set_use_markup(True)
            while gtk.events_pending():
                gtk.main_iteration()

        parent.read_file(filename,update_msg)
        msg_top.destroy()
        success = True
    elif filetype == const.app_gramps_xml:
        parent.db = GrampsXMLDB.GrampsXMLDB()
        parent.read_file(filename)
        success = True
    elif filetype == const.app_gedcom:
        parent.db = GrampsGEDDB.GrampsGEDDB()
        parent.read_file(filename)
        success = True

    if success:
        # Add the file to the recent items
        RecentFiles.recent_files(filename,filetype)
        parent.build_recent_menu()

    return success
