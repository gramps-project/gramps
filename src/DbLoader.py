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

# $Id: ViewManager.py 6678 2006-05-16 03:35:10Z dallingham $

"""
Handling of loading new/existing databases.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GTK+ modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Config
import Errors
import Mime
import GrampsDb
import Utils
from PluginUtils import import_list
import QuestionDialog

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
# DbLoader class
#
#-------------------------------------------------------------------------
class DbLoader:
    def __init__(self,dbstate,uistate):
        self.dbstate = dbstate
        self.uistate = uistate

    def open_file(self):
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

        format_list = [const.app_gramps,const.app_gramps_xml,const.app_gedcom]

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
        default_dir = os.path.split(Config.get(Config.RECENT_FILE))[0] \
                      + os.path.sep
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
            if self.check_errors(filename):
                return ('','')

            filetype = type_selector.get_value()
            if filetype == 'auto':
                filetype = Mime.get_type(filename)
            (the_path, the_file) = os.path.split(filename)
            choose.destroy()
            if filetype in [const.app_gramps,const.app_gramps_xml,
                            const.app_gedcom]:
    
                self.read_file(filename,filetype)
                return (filename,filetype)
            else:
                QuestionDialog.ErrorDialog(
                    _("Could not open file: %s") % filename, 
                    _('File type "%s" is unknown to GRAMPS.\n\n'
                      'Valid types are: GRAMPS database, GRAMPS XML, '
                      'GRAMPS package, and GEDCOM.') % filetype)
                return ('','')
        choose.destroy()
        return ('','')

    def new_file(self):
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
                if self.check_errors(filename):
                    return ('','')
                if os.path.splitext(filename)[1] != ".grdb":
                    filename = filename + ".grdb"
                choose.destroy()
                try:
                    self.dbstate.db.close()
                except:
                    pass
                filetype = const.app_gramps
                self.read_file(filename,filetype)
                return (filename,filetype)
            else:
                choose.destroy()
                return ('','')
        choose.destroy()
        return ('','')

    def save_as(self):
        choose = gtk.FileChooserDialog(
            _('GRAMPS: Create GRAMPS database'), 
            self.uistate.window, 
            gtk.FILE_CHOOSER_ACTION_SAVE, 
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
             gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        # Always add automatic (macth all files) filter
        add_all_files_filter(choose)
        add_gramps_files_filter(choose)
        add_grdb_filter(choose)
        add_xml_filter(choose)
        add_gedcom_filter(choose)

        format_list = [const.app_gramps,const.app_gramps_xml,const.app_gedcom]
        (box, type_selector) = format_maker(format_list)
        choose.set_extra_widget(box)

        # Suggested folder: try last open file, import, then last export, 
        # then home.
        default_dir = os.path.split(Config.get(Config.RECENT_FILE))[0] \
                      + os.path.sep
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_IMPORT_DIR)
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_EXPORT_DIR)
        if len(default_dir)<=1:
            default_dir = '~/'

        new_filename = Utils.get_new_filename('grdb', default_dir)
        
        choose.set_current_folder(default_dir)
        choose.set_current_name(os.path.split(new_filename)[1])

        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = choose.get_filename()
            if self.check_errors(filename):
                return ('','')

            filetype = type_selector.get_value()
            if filetype == 'auto':
                try:
                    the_file = open(filename,'wb')
                    the_file.close()
                    filetype = Mime.get_type(filename)
                    os.remove(filename)
                except RuntimeError, msg:
                    QuestionDialog.ErrorDialog(
                        _("Could not open file: %s") % filename, 
                        str(msg))
                    return ('','')
            # First we try our best formats
            if filetype not in (const.app_gramps, 
                                const.app_gramps_xml, 
                                const.app_gedcom):
                QuestionDialog.ErrorDialog(
                    _("Could not open file: %s") % filename,
                    _("Unknown type: %s") % filetype
                    )
                return ('','')
            choose.destroy()
            try:
                return self.open_saved_as(filename,filetype)
            except:
                log.error("Failed to save as", exc_info=True)
                return False
        else:
            choose.destroy()
            return ('','')

    def check_errors(self,filename):
        """
        This methods runs common errir checks and returns True if any found.
        In this process, warning dialog can pop up.
        """

        if type(filename) not in (str,unicode):
            return True

        filename = os.path.normpath(os.path.abspath(filename))

        if len(filename) == 0:
            return True
        elif os.path.isdir(filename):
            QuestionDialog.ErrorDialog(
                _('Cannot open database'), 
                _('The selected file is a directory, not '
                  'a file.\nA GRAMPS database must be a file.'))
            return True
        elif os.path.exists(filename):
            if not os.access(filename, os.R_OK):
                QuestionDialog.ErrorDialog(
                    _('Cannot open database'), 
                    _('You do not have read access to the selected '
                      'file.'))
                return True
        else:
            try:
                f = file(filename,'w')
                f.close()
                os.remove(filename)
            except IOError:
                QuestionDialog.ErrorDialog(
                    _('Cannot create database'), 
                    _('You do not have write access to the selected file.'))
                return True

        # FIXME: not sure what this is for at this point
        try:
            os.chdir(os.path.dirname(filename))
        except:
            print "could not change directory"

        return False

    def read_file(self, filename, filetype):
        """
        This method takes care of enabling/disabling/emittin signals,
        changing database, and loading the data.
        
        This method should only return on success.
        Returning on failure makes no sense, because we cannot recover,
        since database has already beeen changed.
        Therefore, any errors should raise exceptions.

        We return with the disabled signals. The post-load routine
        should enable signals, as well as finish up with other UI goodies.
        """

        filename = os.path.normpath(os.path.abspath(filename))

        if os.path.exists(filename) and (not os.access(filename, os.W_OK)):
            mode = "r"
            QuestionDialog.WarningDialog(_('Read only database'), 
                                         _('You do not have write access '
                                           'to the selected file.'))
        else:
            mode = "w"

        # emit the database change signal so the that models do not
        # attempt to update the screen while we are loading the
        # new data       
        #self.dbstate.emit('database-changed', (GrampsDb.GrampsDbBase(), ))

        factory = GrampsDb.gramps_db_factory
        self.dbstate.change_database(factory(db_type = filetype)())
        self.dbstate.db.disable_signals()

        try:
            self.uistate.window.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.WATCH))
            self.uistate.progress.show()
            success = self.dbstate.db.load(filename,
                                           self.uistate.pulse_progressbar,
                                           mode)
        except Exception:
            log.error("Failed to open database.", exc_info=True)

#-------------------------------------------------------------------------
#
# FileChooser filters: what to show in the file chooser
#
#-------------------------------------------------------------------------
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
# Format selectors: explictly set the format of the file
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
