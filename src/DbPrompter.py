#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
import shutil
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

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
import const
import QuestionDialog
import Plugins

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
            response = top.run()
            if response == gtk.RESPONSE_OK:
                if new.get_active():
                    prompter = NewNativeDbPrompter(self.parent,self.parent_window)
                else:
                    prompter = ExistingDbPrompter(self.parent,self.parent_window)
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
        choose.set_local_only(gtk.FALSE)
        # Always add automatic (macth all files) filter
        filter = gtk.FileFilter()
        filter.set_name(_('Automatic'))
        filter.add_pattern('*')
        choose.add_filter(filter)
        
        # Always add native format filter
        filter = gtk.FileFilter()
        filter.set_name(_('GRAMPS databases'))
        filter.add_mime_type('application/x-gramps')
        choose.add_filter(filter)

        # Add more data type selections if opening existing db
        for (importData,filter,mime_type) in Plugins._imports:
            choose.add_filter(filter)
        
        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = choose.get_filename()
            filetype = gnome.vfs.get_mime_type(filename)
            if filetype == 'application/x-gramps':
                choose.destroy()
                self.parent.read_file(filename)
                return 1
            (junk,the_file) = os.path.split(filename)
            for (importData,filter,mime_type) in Plugins._imports:
                if filetype == mime_type or the_file == mime_type:
                    choose.destroy()
                    QuestionDialog.OkDialog( _("Opening non-native format"), 
                                _("New gramps database has to be set up "
                                  "when opening non-native formats. The "
                                  "following dialog will let you select "
                                  "the new database."),
                                self.parent_window)
                    prompter = NewNativeDbPrompter(self.parent,self.parent_window)
                    if prompter.chooser():
                        importData(self.parent.db,filename)
                        self.parent.import_tool_callback()
                        return 1
                    else:
                        return 0
            QuestionDialog.ErrorDialog( _("Could not open file: %s") % filename,
                        _('The type "%s" is not in the list of known file types') % filetype )
            return 0

        else:
            choose.destroy()
            return 0

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
        choose.set_local_only(gtk.FALSE)
        # Always add automatic (macth all files) filter
        filter = gtk.FileFilter()
        filter.set_name(_('Automatic'))
        filter.add_pattern('*')
        choose.add_filter(filter)
        
#   FIXME: Uncomment when we have grdb importer
#
#        # Always add native format filter
#        filter = gtk.FileFilter()
#        filter.set_name(_('GRAMPS databases'))
#        filter.add_mime_type('application/x-gramps')
#        choose.add_filter(filter)

        # Add more data type selections if opening existing db
        for (importData,filter,mime_type) in Plugins._imports:
            choose.add_filter(filter)
        
        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = choose.get_filename()
            filetype = gnome.vfs.get_mime_type(filename)
#   FIXME: Uncomment when we have grdb importer
#
#            if filetype == 'application/x-gramps':
#                choose.destroy()
#                self.parent.read_file(filename)
#                return 1
            (junk,the_file) = os.path.split(filename)
            for (importData,filter,mime_type) in Plugins._imports:
                if filetype == mime_type or the_file == mime_type:
                    choose.destroy()
                    importData(self.parent.db,filename)
                    self.parent.import_tool_callback()
                    return 1
            QuestionDialog.ErrorDialog( _("Could not open file: %s") % filename,
                        _('The type "%s" is not in the list of known file types') % filetype )
            return 0

        else:
            choose.destroy()
            return 0


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
        filter = gtk.FileFilter()
        filter.set_name(_('Automatic'))
        filter.add_pattern('*')
        choose.add_filter(filter)
        
        # Always add native format filter
        filter = gtk.FileFilter()
        filter.set_name(_('GRAMPS databases'))
        filter.add_mime_type('application/x-gramps')
        choose.add_filter(filter)

        new_filename = Utils.get_new_filename('grdb')
        
        choose.set_filename(new_filename)
        choose.set_current_name(os.path.split(new_filename)[1])

        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = choose.get_filename()
            if os.path.splitext(filename)[1] != ".grdb":
                filename = filename + ".grdb"
            choose.destroy()
            self.parent.read_file(filename)
            return 1
        else:
            choose.destroy()
            return 0
