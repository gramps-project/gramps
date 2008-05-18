#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

# $Id:DbLoader.py 9912 2008-01-22 09:17:46Z acraphae $

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
import gobject

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Config
import Mime
import gen.db
import GrampsDbUtils
import Utils
from PluginUtils import PluginManager
from QuestionDialog import (DBErrorDialog, ErrorDialog, QuestionDialog2, 
                            WarningDialog)
import Errors

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

#connection between main mime type, name, and list of alternative mime types
_KNOWN_FORMATS = { 
    const.APP_GRAMPS        : [_('GRAMPS (grdb)'), []], 
    const.APP_GRAMPS_XML    : [_('GRAMPS XML'), []], 
    const.APP_GEDCOM        : [_('GEDCOM'), []], 
}

OPEN_FORMATS = [const.APP_GRAMPS_XML, const.APP_GEDCOM]

#-------------------------------------------------------------------------
#
# DbLoader class
#
#-------------------------------------------------------------------------
class DbLoader:
    def __init__(self, dbstate, uistate):
        self.dbstate = dbstate
        self.uistate = uistate
        self.import_info = None

    def import_file(self):
        # First thing first: import is a batch transaction
        # so we will lose the undo history. Warn the user.

        if self.dbstate.db.get_number_of_people() > 0:
            warn_dialog = QuestionDialog2(
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
            
        pmgr = PluginManager.get_instance()
        
        choose_db_dialog = gtk.FileChooserDialog(_('GRAMPS: Import database'), 
                                       self.uistate.window, 
                                       gtk.FILE_CHOOSER_ACTION_OPEN, 
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                        'gramps-import', gtk.RESPONSE_OK))
        choose_db_dialog.set_local_only(False)

        # Always add automatic (match all files) filter
        add_all_files_filter(choose_db_dialog)   # *
        #add_grdb_filter(choose_db_dialog)        # .grdb no longer native!
        add_xml_filter(choose_db_dialog)         # .gramps
        add_gedcom_filter(choose_db_dialog)      # .ged

        format_list = OPEN_FORMATS[:]

        # Add more data type selections if opening existing db
        for data in pmgr.get_import_list():
            mime_filter = data[1]
            mime_types = data[2]
            native_format = data[3]
            format_name = data[4]

            if not native_format:
                choose_db_dialog.add_filter(mime_filter)
                format_list.append(mime_types[0])
                _KNOWN_FORMATS[mime_types[0]] = [format_name, mime_types[1:]]

        (box, type_selector) = format_maker(format_list)
        choose_db_dialog.set_extra_widget(box)

        # Suggested folder: try last open file, import, then last export, 
        # then home.
        default_dir = Config.get(Config.RECENT_IMPORT_DIR)
        if len(default_dir)<=1:
            default_dir = get_default_dir()

        choose_db_dialog.set_current_folder(default_dir)
        while True:
            response = choose_db_dialog.run()
            if response == gtk.RESPONSE_CANCEL:
                break
            elif response == gtk.RESPONSE_OK:
                filename = Utils.get_unicode_path(choose_db_dialog.get_filename())
                if self.check_errors(filename):
                    # displays errors if any
                    continue

                # Do not allow importing from the currently open file
                if filename == self.dbstate.db.full_name:
                    ErrorDialog(_("Cannot import from current file")) 
                    continue

                filetype = type_selector.get_value()
                if filetype == 'auto':
                    try:
                        filetype = Mime.get_type(filename)
                    except RuntimeError, msg:
                        ErrorDialog(_("Could not open file: %s") % filename, 
                                    str(msg))
                        continue

                # First we try our best formats
                if filetype in OPEN_FORMATS or filetype in _KNOWN_FORMATS:
                    importer = GrampsDbUtils.gramps_db_reader_factory(filetype)
                    self.do_import(choose_db_dialog, importer, filename)
                    return True

                (the_path, the_file) = os.path.split(filename)
                Config.set(Config.RECENT_IMPORT_DIR, the_path)
                # Then we try all the known plugins
                for (importData, mime_filter, mime_types, native_format, 
                     format_name) in pmgr.get_import_list():
                    if filetype in mime_types:
                        self.do_import(choose_db_dialog, importData, filename)
                        return True

                # Finally, we give up and declare this an unknown format
                ErrorDialog(
                    _("Could not open file: %s") % filename, 
                    _('File type "%s" is unknown to GRAMPS.\n\n'
                      'Valid types are: GRAMPS database, GRAMPS XML, '
                      'GRAMPS package, and GEDCOM.') % filetype)

        choose_db_dialog.destroy()
        return False

    def check_errors(self, filename):
        """
        Run common error checks and return True if any found.
        
        In this process, a warning dialog can pop up.
        
        """

        if type(filename) not in (str, unicode):
            return True

        filename = os.path.normpath(os.path.abspath(filename))

        if len(filename) == 0:
            return True
        elif os.path.isdir(filename):
            ErrorDialog(
                _('Cannot open database'), 
                _('The selected file is a directory, not '
                  'a file.\nA GRAMPS database must be a file.'))
            return True
        elif os.path.exists(filename):
            if not os.access(filename, os.R_OK):
                ErrorDialog(
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
                ErrorDialog(
                    _('Cannot create database'), 
                    _('You do not have write access to the selected file.'))
                return True

        return False

    def read_file(self, filename):
        """
        This method takes care of changing database, and loading the data.
        In 3.0 we only allow reading of real databases of filetype 
        'x-directory/normal'
        
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
                WarningDialog(_('Read only database'), 
                                             _('You do not have write access '
                                               'to the selected file.'))
            else:
                mode = "w"
        else:
            mode = 'w'

        dbclass = gen.db.GrampsDBDir
        
        self.dbstate.change_database(dbclass())
        self.dbstate.db.disable_signals()

        self.uistate.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.uistate.progress.show()
        
        try:
            self.dbstate.db.load(filename, self.uistate.pulse_progressbar, mode)
            self.dbstate.db.set_save_path(filename)
        except gen.db.FileVersionDeclineToUpgrade:
            self.dbstate.no_database()
        except gen.db.exceptions.FileVersionError, msg:
            ErrorDialog( _("Cannot open database"), str(msg))
            self.dbstate.no_database()
        except OSError, msg:
            ErrorDialog(
                _("Could not open file: %s") % filename, str(msg))
        except Errors.DbError, msg:
            DBErrorDialog(str(msg.value))
            self.dbstate.no_database()
        except Exception:
            _LOG.error("Failed to open database.", exc_info=True)
        return True

    def do_import(self, dialog, importer, filename):
        self.import_info = None
        dialog.destroy()
        self.uistate.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.uistate.progress.show()

        try:
            #an importer can return an object with info, object.info_text() 
            #returns that info. Otherwise None is set to import_info
            self.import_info = importer(self.dbstate.db, filename,
                            self.uistate.pulse_progressbar)
            dirname = os.path.dirname(filename) + os.path.sep
            Config.set(Config.RECENT_IMPORT_DIR, dirname)
        except UnicodeError, msg:
            ErrorDialog(
                _("Could not import file: %s") % filename, 
                _("This file incorrectly identifies its character "
                  "set, so it cannot be accurately imported. Please fix the "
                  "encoding, and import again") + "\n\n %s" % msg)
        except Exception:
            _LOG.error("Failed to import database.", exc_info=True)
    
    def import_info_text(self):
        """
        On import the importer can construct an info object about the import.
        If so, this method will return this text, otherwise the empty string
        is returned
        """
        if self.import_info is None:
            return u""
        return self.import_info.info_text()

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
    mime_filter.set_name(_('GRAMPS 2.x databases'))
    mime_filter.add_mime_type(const.APP_GRAMPS)
    chooser.add_filter(mime_filter)

def add_xml_filter(chooser):
    """
    Add a GRAMPS XML filter to the file chooser dialog.
    """
    mime_filter = gtk.FileFilter()
    mime_filter.set_name(_('GRAMPS XML databases'))
    mime_filter.add_mime_type(const.APP_GRAMPS_XML)
    chooser.add_filter(mime_filter)

def add_gedcom_filter(chooser):
    """
    Add a GEDCOM filter to the file chooser dialog.
    """
    mime_filter = gtk.FileFilter()
    mime_filter.set_name(_('GEDCOM files'))
    mime_filter.add_mime_type(const.APP_GEDCOM)
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
        self.store = gtk.ListStore(gobject.TYPE_STRING)
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
            format_list.append( (format, _KNOWN_FORMATS[format][0]) )

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
