#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
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
Handling of loading new/existing databases.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import sys
from bsddb.db import DBAccessError, DBRunRecoveryError, \
    DBPageNotFoundError, DBInvalidArgError
from gettext import gettext as _
import logging

#-------------------------------------------------------------------------
#
# Set up logging
#
#-------------------------------------------------------------------------
_LOG = logging.getLogger(".")

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
import Mime
import GrampsDb
import GrampsDbUtils
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

OPEN_FORMATS = [const.app_gramps_xml, const.app_gedcom]

#-------------------------------------------------------------------------
#
# DbLoader class
#
#-------------------------------------------------------------------------
class DbLoader:
    def __init__(self, dbstate, uistate):
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

        (box, type_selector) = format_maker(OPEN_FORMATS)
        choose.set_extra_widget(box)

        choose.set_current_folder(get_default_dir())
        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = unicode(choose.get_filename(),
                               sys.getfilesystemencoding())
            if self.check_errors(filename):
                return ('','')

            filetype = type_selector.get_value()
            if filetype == 'auto':
                filetype = Mime.get_type(filename)
            (the_path, the_file) = os.path.split(filename)
            choose.destroy()
            if filetype in OPEN_FORMATS:
                self.read_file(filename, filetype)
                try:
                    os.chdir(os.path.dirname(filename))
                except:
                    return ('', '')
                return (filename, filetype)
            elif filetype in [const.app_gramps_package, const.app_geneweb]:
                QuestionDialog.ErrorDialog(
                    _("Could not open file: %s") % filename, 
                    _('Files of type "%s" cannot be opened directly.\n\n'
                      'Please create a new GRAMPS database and import '
                      'the file.') % filetype)
                return ('', '')
            else:
                QuestionDialog.ErrorDialog(
                    _("Could not open file: %s") % filename, 
                    _('File type "%s" is unknown to GRAMPS.\n\n'
                      'Valid types are: GRAMPS database, GRAMPS XML, '
                      'GRAMPS package, and GEDCOM.') % filetype)
                return ('', '')
        choose.destroy()
        return ('', '')

    def new_file(self):
        choose = gtk.FileChooserDialog(
            _('GRAMPS: Create GRAMPS database'), 
            self.uistate.window, 
            gtk.FILE_CHOOSER_ACTION_SAVE, 
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
             gtk.STOCK_NEW, gtk.RESPONSE_OK))

        # Always add automatic (macth all files) filter
        add_all_files_filter(choose)
        add_grdb_filter(choose)

        default_dir = get_default_dir()
        new_filename = Utils.get_new_filename('grdb', default_dir)
        
        choose.set_current_folder(default_dir)
        choose.set_current_name(os.path.split(new_filename)[1])

        while (True):
            response = choose.run()
            if response == gtk.RESPONSE_OK:
                filename = unicode(choose.get_filename(),
                                   sys.getfilesystemencoding())
                if self.check_errors(filename):
                    return ('','')

                ext = os.path.splitext(filename)[1].lower()
                if ext == ".ged":
                    filetype = const.app_gedcom
                elif ext == ".gramps":
                    filetype = const.app_gramps_xml
                elif ext == ".grdb":
                    filetype = const.app_gramps
                else:
                    filename = filename + ".grdb"
                    filetype = const.app_gramps
                    
                choose.destroy()
                try:
                    self.dbstate.db.close()
                except:
                    pass

                self.read_file(filename, filetype)
                    
                try:
                    os.chdir(os.path.dirname(filename))
                except:
                    return ('', '')
                self.dbstate.db.db_is_open = True
                return (filename, filetype)
            else:
                choose.destroy()
                return ('', '')
        choose.destroy()
        return ('', '')

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

        (box, type_selector) = format_maker(OPEN_FORMATS)
        choose.set_extra_widget(box)

        default_dir = get_default_dir()
        new_filename = Utils.get_new_filename('grdb', default_dir)
        
        choose.set_current_folder(default_dir)
        choose.set_current_name(os.path.split(new_filename)[1])

        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = unicode(choose.get_filename(),
                               sys.getfilesystemencoding())
            if self.check_errors(filename):
                return ('','')

            # Do not allow saving as into the currently open file
            if filename == self.dbstate.db.full_name:
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
            if filetype not in OPEN_FORMATS:
                QuestionDialog.ErrorDialog(
                    _("Could not open file: %s") % filename,
                    _("Unknown type: %s") % filetype
                    )
                return ('','')
            choose.destroy()
            self.open_saved_as(filename, filetype)
            return (filename, filetype)
        else:
            choose.destroy()
            return ('','')

    def import_file(self):
        # First thing first: import is a batch transaction
        # so we will lose the undo history. Warn the user.

        if self.dbstate.db.get_number_of_people() > 0:
            warn_dialog = QuestionDialog.QuestionDialog2(
                _('Undo history warning'),
                _('Proceeding with import will erase the undo history '
                  'for this session. In particular, you will not be able '
                  'to revert the import or any changes made prior to it.\n\n'
                  'If you think you may want to revert the import, '
                  'please stop here and backup your database.'),
                _('_Proceed with import'), _('_Stop'),
                self.uistate.window)
            if not warn_dialog.run():
                return False
        
        choose = gtk.FileChooserDialog(
            _('GRAMPS: Import database'), 
            self.uistate.window, 
            gtk.FILE_CHOOSER_ACTION_OPEN, 
            (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL, 
             gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        choose.set_local_only(False)

        # Always add automatic (macth all files) filter
        add_all_files_filter(choose)
        add_grdb_filter(choose)
        add_xml_filter(choose)
        add_gedcom_filter(choose)

        format_list = OPEN_FORMATS[:]

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
            default_dir = get_default_dir()

        choose.set_current_folder(default_dir)
        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = unicode(choose.get_filename(),
                               sys.getfilesystemencoding())
            if self.check_errors(filename):
                return False

            # Do not allow importing from the currently open file
            if filename == self.dbstate.db.full_name:
                return False
            
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
            if filetype in OPEN_FORMATS:
                importer = GrampsDbUtils.gramps_db_reader_factory(filetype)
                self.do_import(choose, importer, filename)
                return True

            # Then we try all the known plugins
            (the_path, the_file) = os.path.split(filename)
            Config.set(Config.RECENT_IMPORT_DIR, the_path)
            for (importData, mime_filter, mime_type, native_format, format_name) \
                    in import_list:
                if filetype == mime_type or the_file == mime_type:
                    self.do_import(choose, importData, filename)
                    return True

            # Finally, we give up and declare this an unknown format
            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename, 
                _('File type "%s" is unknown to GRAMPS.\n\n'
                  'Valid types are: GRAMPS database, GRAMPS XML, '
                  'GRAMPS package, and GEDCOM.') % filetype)

        choose.destroy()
        return False

    def check_errors(self, filename):
        """
        This methods runs common error checks and returns True if any found.
        In this process, warning dialog can pop up.
        """

        if type(filename) not in (str, unicode):
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

        return False

    def read_file(self, filename, filetype):
        """
        This method takes care of changing database, and loading the data.
        
        This method should only return on success.
        Returning on failure makes no sense, because we cannot recover,
        since database has already beeen changed.
        Therefore, any errors should raise exceptions.

        On success, return with the disabled signals. The post-load routine
        should enable signals, as well as finish up with other UI goodies.
        """

        if os.path.exists(filename):
            if not os.access(filename, os.W_OK):
                mode = "r"
                QuestionDialog.WarningDialog(_('Read only database'), 
                                             _('You do not have write access '
                                               'to the selected file.'))
            else:
                mode = "w"
        elif filetype == 'unknown':
            QuestionDialog.WarningDialog(
                _('Missing or Invalid database'),
                _('%s could not be found.\n'
                  'It is possible that this file no longer exists '
                  'or has been moved.') % filename)
            return False
        else:
            mode = 'w'

        try:
            dbclass = GrampsDb.gramps_db_factory(db_type = filetype)
        except GrampsDb.GrampsDbException, msg:
            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename, 
                _("This may be caused by an improper installation of GRAMPS.") +
                "\n" + str(msg))
            return
                
        
        self.dbstate.change_database(dbclass(Config.get(Config.TRANSACTIONS)))
        self.dbstate.db.disable_signals()

        self.uistate.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.uistate.progress.show()
        
        try:
            self.dbstate.db.load(filename, self.uistate.pulse_progressbar, mode)
            self.dbstate.db.set_save_path(filename)
            try:
                os.chdir(os.path.dirname(filename))
            except:
                print "could not change directory"
        except OSError, msg:
            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename, str(msg))
        except DBRunRecoveryError, msg:
            QuestionDialog.ErrorDialog(
                _("Low level database corruption detected"),
                _("GRAMPS has detected a problem in the underlying "
                  "Berkeley database. Please exit the program, and GRAMPS "
                  "will attempt to run the recovery repair operation "
                  "the next time you open this database. If this "
                  "problem persists, create a new database, import "
                  "from a backup database, and report the problem to "
                  "gramps-bugs@lists.sourceforge.net."))
        except (DBAccessError, DBPageNotFoundError, DBInvalidArgError), msg:
            QuestionDialog.ErrorDialog(
                _("Could not open file: %s") % filename,
                str(msg[1]))
        except Exception:
            _LOG.error("Failed to open database.", exc_info=True)

        return True
    
    def open_saved_as(self, filename, filetype):
        dbclass = GrampsDb.gramps_db_factory(db_type = filetype)
        new_database = dbclass()

        old_database = self.dbstate.db

        self.dbstate.change_database_noclose(new_database)
        old_database.disable_signals()
        new_database.disable_signals()

        self.uistate.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.uistate.progress.show()

        try:
            new_database.load_from(old_database, filename,
                                   self.uistate.pulse_progressbar)
            old_database.close()
        except Exception:
            _LOG.error("Failed to open database.", exc_info=True)
            return False

    def do_import(self, dialog, importer, filename):
        dialog.destroy()
        self.uistate.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.uistate.progress.show()

        try:
            importer(self.dbstate.db, filename, self.uistate.pulse_progressbar)
            dirname = os.path.dirname(filename) + os.path.sep
            Config.set(Config.RECENT_IMPORT_DIR, dirname)
        except Exception:
            _LOG.error("Failed to import database.", exc_info=True)

#-------------------------------------------------------------------------
#
# default dir selection
#
#-------------------------------------------------------------------------
def get_default_dir():
    # Suggested folder: try last open file, last import, last export, 
    # then home.
    default_dir = os.path.dirname(Config.get(Config.RECENT_FILE))
    if default_dir:
        default_dir += os.path.sep
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_IMPORT_DIR)
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_EXPORT_DIR)
        if len(default_dir)<=1:
            default_dir = '~/'
    else:
        default_dir = "~/"
    return default_dir

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
    for fmt in OPEN_FORMATS:
        mime_filter.add_mime_type(fmt)
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
