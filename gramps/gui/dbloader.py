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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Handling of loading new/existing databases.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
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
from gi.repository import Gtk
from gi.repository import GObject

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db.dbconst import DBBACKEND
from gramps.gen.db.utils import make_database
_ = glocale.translation.gettext
from gramps.cli.grampscli import CLIDbLoader
from gramps.gen.config import config
from gramps.gen.db.exceptions import (DbUpgradeRequiredError,
                                      BsddbDowngradeError,
                                      DbVersionError,
                                      DbPythonError,
                                      DbEnvironmentError,
                                      BsddbUpgradeRequiredError,
                                      BsddbDowngradeRequiredError,
                                      PythonUpgradeRequiredError,
                                      PythonDowngradeError,
                                      DbConnectionError)
from .pluginmanager import GuiPluginManager
from .dialog import (DBErrorDialog, ErrorDialog, QuestionDialog2,
                            WarningDialog)
from .user import User
from gramps.gen.errors import DbError
from .managedwindow import ManagedWindow

#-------------------------------------------------------------------------
#
# DbLoader class
#
#-------------------------------------------------------------------------
class DbLoader(CLIDbLoader):
    def __init__(self, dbstate, uistate):
        CLIDbLoader.__init__(self, dbstate)
        self.uistate = uistate
        self.import_info = None

    def _warn(self, title, warnmessage):
        WarningDialog(title, warnmessage,
                      parent=self.uistate.window)

    def _errordialog(self, title, errormessage):
        """
        Show the error.
        In the GUI, the error is shown, and a return happens
        """
        ErrorDialog(title, errormessage,
                    parent=self.uistate.window)
        return 1

    def _dberrordialog(self, msg):
        import traceback
        exc = traceback.format_exc()
        try:
            DBErrorDialog(str(msg.value),
                          parent=self.uistate.window)
            _LOG.error(str(msg.value))
        except:
            DBErrorDialog(str(msg),
                          parent=self.uistate.window)
            _LOG.error(str(msg) +"\n" + exc)

    def import_file(self):
        self.import_info = None
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
                parent=self.uistate.window)
            if not warn_dialog.run():
                return False

        GrampsImportFileDialog(self.dbstate, self.uistate,
                               callback=self.set_info)

    def set_info(self, info):
        self.import_info = info

    def import_info_text(self):
        """
        On import the importer can construct an info object about the import.
        If so, this method will return this text, otherwise the empty string
        is returned
        """
        if self.import_info is None:
            return ""
        return self.import_info.info_text()

    def read_file(self, filename, username=None, password=None):
        """
        This method takes care of changing database, and loading the data.
        In 3.0 we only allow reading of real databases of filetype
        'x-directory/normal'

        This method should only return on success.
        Returning on failure makes no sense, because we cannot recover,
        since database has already been changed.
        Therefore, any errors should raise exceptions.

        On success, return with the disabled signals. The post-load routine
        should enable signals, as well as finish up with other UI goodies.
        """

        if os.path.exists(filename):
            if not os.access(filename, os.W_OK):
                mode = "r"
                self._warn(_('Read only database'),
                                             _('You do not have write access '
                                               'to the selected file.'))
            else:
                mode = "w"
        else:
            mode = 'w'

        dbid_path = os.path.join(filename, DBBACKEND)
        if os.path.isfile(dbid_path):
            with open(dbid_path) as fp:
                dbid = fp.read().strip()
        else:
            dbid = "bsddb"

        db = make_database(dbid)
        db.disable_signals()
        self.dbstate.no_database()

        if db.requires_login() and username is None:
            login = GrampsLoginDialog(self.uistate)
            credentials = login.run()
            if credentials is None:
                return
            username, password = credentials

        self._begin_progress()

        force_schema_upgrade = False
        force_bsddb_upgrade = False
        force_bsddb_downgrade = False
        force_python_upgrade = False
        try:
            while True:
                try:
                    db.load(filename, self._pulse_progress,
                            mode, force_schema_upgrade,
                            force_bsddb_upgrade,
                            force_bsddb_downgrade,
                            force_python_upgrade,
                            username=username,
                            password=password)
                    if self.dbstate.is_open():
                        self.dbstate.db.close(
                            user=User(callback=self._pulse_progress,
                                      uistate=self.uistate,
                                      dbstate=self.dbstate))
                    self.dbstate.change_database(db)
                    break
                except DbUpgradeRequiredError as msg:
                    if QuestionDialog2(_("Are you sure you want "
                                         "to upgrade this Family Tree?"),
                                       str(msg),
                                       _("I have made a backup,\n"
                                         "please upgrade my Family Tree"),
                                       _("Cancel"),
                                       parent=self.uistate.window).run():
                        force_schema_upgrade = True
                        force_bsddb_upgrade = False
                        force_bsddb_downgrade = False
                        force_python_upgrade = False
                    else:
                        self.dbstate.no_database()
                        break
                except BsddbUpgradeRequiredError as msg:
                    if QuestionDialog2(_("Are you sure you want "
                                         "to upgrade this Family Tree?"),
                                       str(msg),
                                       _("I have made a backup,\n"
                                         "please upgrade my Family Tree"),
                                       _("Cancel"),
                                       parent=self.uistate.window).run():
                        force_schema_upgrade = False
                        force_bsddb_upgrade = True
                        force_bsddb_downgrade = False
                        force_python_upgrade = False
                    else:
                        self.dbstate.no_database()
                        break
                except BsddbDowngradeRequiredError as msg:
                    if QuestionDialog2(_("Are you sure you want "
                                         "to downgrade this Family Tree?"),
                                       str(msg),
                                       _("I have made a backup,\n"
                                         "please downgrade my Family Tree"),
                                       _("Cancel"),
                                       parent=self.uistate.window).run():
                        force_schema_upgrade = False
                        force_bsddb_upgrade = False
                        force_bsddb_downgrade = True
                        force_python_upgrade = False
                    else:
                        self.dbstate.no_database()
                        break
                except PythonUpgradeRequiredError as msg:
                    if QuestionDialog2(_("Are you sure you want "
                                         "to upgrade this Family Tree?"),
                                       str(msg),
                                       _("I have made a backup,\n"
                                         "please upgrade my Family Tree"),
                                       _("Cancel"),
                                       parent=self.uistate.window).run():
                        force_schema_upgrade = False
                        force_bsddb_upgrade = False
                        force_bsddb_downgrade = False
                        force_python_upgrade = True
                    else:
                        self.dbstate.no_database()
                        break
        # Get here is there is an exception the while loop does not handle
        except BsddbDowngradeError as msg:
            self.dbstate.no_database()
            self._warn( _("Cannot open database"), str(msg))
        except DbVersionError as msg:
            self.dbstate.no_database()
            self._errordialog( _("Cannot open database"), str(msg))
        except DbPythonError as msg:
            self.dbstate.no_database()
            self._errordialog( _("Cannot open database"), str(msg))
        except DbEnvironmentError as msg:
            self.dbstate.no_database()
            self._errordialog( _("Cannot open database"), str(msg))
        except PythonDowngradeError as msg:
            self.dbstate.no_database()
            self._warn( _("Cannot open database"), str(msg))
        except DbConnectionError as msg:
            self.dbstate.no_database()
            self._warn(_("Cannot open database"), str(msg))
        except OSError as msg:
            self.dbstate.no_database()
            self._errordialog(
                _("Could not open file: %s") % filename, str(msg))
        except DbError as msg:
            self.dbstate.no_database()
            self._dberrordialog(msg)
        except Exception as newerror:
            self.dbstate.no_database()
            self._dberrordialog(str(newerror))
        self._end_progress()
        return True

#-------------------------------------------------------------------------
#
# FileChooser filters: what to show in the file chooser
#
#-------------------------------------------------------------------------
def add_all_files_filter(chooser):
    """
    Add an all-permitting filter to the file chooser dialog.
    """
    mime_filter = Gtk.FileFilter()
    mime_filter.set_name(_('All files'))
    mime_filter.add_pattern('*')
    chooser.add_filter(mime_filter)

#-------------------------------------------------------------------------
#
# Format selectors: explictly set the format of the file
#
#-------------------------------------------------------------------------
class GrampsFormatWidget(Gtk.ComboBox):

    def __init__(self):
        Gtk.ComboBox.__init__(self, model=None)

    def set(self, format_list):
        self.store = Gtk.ListStore(GObject.TYPE_STRING)
        self.set_model(self.store)
        cell = Gtk.CellRendererText()
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

def format_maker():
    """
    A factory function making format selection widgets.

    Accepts a list of formats to include into selector.
    The auto selection is always added as the first one.
    The returned box contains both the label and the selector.
    """
    pmgr = GuiPluginManager.get_instance()
    format_list = [ ('auto', _('Automatically detected')) ]

    for plugin in pmgr.get_import_plugins():
        format_list.append( (plugin.get_extension(), plugin.get_name()) )

    type_selector = GrampsFormatWidget()
    type_selector.set(format_list)

    box = Gtk.Box()
    label = Gtk.Label(label=_('Select file _type:'))
    label.set_use_underline(True)
    label.set_mnemonic_widget(type_selector)
    box.pack_start(label, expand=False, fill=False, padding=6)
    box.add(type_selector)
    box.show_all()
    return (box, type_selector)

class GrampsLoginDialog(ManagedWindow):

    def __init__(self, uistate):
        """
        A login dialog to obtain credentials to connect to a database
        """
        self.title = _("Login")
        ManagedWindow.__init__(self, uistate, [], self.__class__, modal=True)

        dialog = Gtk.Dialog(parent=uistate.window)
        grid = Gtk.Grid()
        grid.set_border_width(6)
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)
        label = Gtk.Label(label=_('Username: '))
        grid.attach(label, 0, 0, 1, 1)
        self.username = Gtk.Entry()
        self.username.set_hexpand(True)
        grid.attach(self.username, 1, 0, 1, 1)
        label = Gtk.Label(label=_('Password: '))
        grid.attach(label, 0, 1, 1, 1)
        self.password = Gtk.Entry()
        self.password.set_hexpand(True)
        self.password.set_visibility(False)
        self.password.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        grid.attach(self.password, 1, 1, 1, 1)
        dialog.vbox.pack_start(grid, True, True, 0)
        dialog.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL,
                           _('Login'), Gtk.ResponseType.OK)
        self.set_window(dialog, None, self.title)

    def run(self):
        self.show()
        response = self.window.run()
        username = self.username.get_text()
        password = self.password.get_text()
        if response == Gtk.ResponseType.CANCEL:
            self.close()
            return None
        elif response == Gtk.ResponseType.OK:
            self.close()
            return (username, password)

class GrampsImportFileDialog(ManagedWindow):

    def __init__(self, dbstate, uistate, callback=None):
        """
        A dialog to import a file into Gramps
        """
        self.dbstate = dbstate

        self.title = _("Import Family Tree")
        ManagedWindow.__init__(self, uistate, [], self.__class__, modal=True)
        # the import_dialog.run() below makes it modal, so any change to
        # the previous line's "modal" would require that line to be changed

        pmgr = GuiPluginManager.get_instance()

        import_dialog = Gtk.FileChooserDialog(
            title='', transient_for=self.uistate.window,
            action=Gtk.FileChooserAction.OPEN)
        import_dialog.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL,
                                  _('Import'), Gtk.ResponseType.OK)
        self.set_window(import_dialog, None, self.title)
        self.setup_configs('interface.grampsimportfiledialog', 780, 630)
        import_dialog.set_local_only(False)

        # Always add automatic (match all files) filter
        add_all_files_filter(import_dialog)   # *

        # Add more file type selections for available importers
        for plugin in pmgr.get_import_plugins():
            file_filter = Gtk.FileFilter()
            name = "%s (.%s)" % (plugin.get_name(), plugin.get_extension())
            file_filter.set_name(name)
            file_filter.add_pattern("*.%s" % plugin.get_extension())
            file_filter.add_pattern(plugin.get_extension().capitalize())
            import_dialog.add_filter(file_filter)

        (box, type_selector) = format_maker()
        import_dialog.set_extra_widget(box)

        import_dialog.set_current_folder(config.get('paths.recent-import-dir'))
        while True:
            # the import_dialog.run() makes it modal, so any change to that
            # line would require the ManagedWindow.__init__ to be changed also
            response = import_dialog.run()
            if response == Gtk.ResponseType.CANCEL:
                break
            elif response == Gtk.ResponseType.DELETE_EVENT:
                return
            elif response == Gtk.ResponseType.OK:
                filename = import_dialog.get_filename()
                if self.check_errors(filename):
                    # displays errors if any
                    continue

                (the_path, the_file) = os.path.split(filename)
                config.set('paths.recent-import-dir', the_path)

                extension = type_selector.get_value()
                if extension == 'auto':
                    # Guess the file format based on the file extension.
                    # This will get the lower case extension without a period,
                    # or an empty string.
                    extension = os.path.splitext(filename)[-1][1:].lower()

                for plugin in pmgr.get_import_plugins():
                    if extension == plugin.get_extension():
                        self.close()
                        self.do_import(plugin.get_import_function(),
                                       filename)
                        if callback is not None:
                            callback(self.import_info)
                        return

                # Finally, we give up and declare this an unknown format
                ErrorDialog(
                    _("Could not open file: %s") % filename,
                    _('File type "%s" is unknown to Gramps.\n\n'
                      'Valid types are: Gramps database, Gramps XML, '
                      'Gramps package, GEDCOM, and others.') % extension,
                    parent=self.uistate.window)

        self.close()

    def check_errors(self, filename):
        """
        Run common error checks and return True if any found.

        In this process, a warning dialog can pop up.

        """
        if not isinstance(filename, str):
            return True

        filename = os.path.normpath(os.path.abspath(filename))

        if len(filename) == 0:
            return True
        elif os.path.isdir(filename):
            ErrorDialog(
                _('Cannot open file'),
                _('The selected file is a directory, not a file.\n'),
                parent=self.uistate.window)
            return True
        elif os.path.exists(filename):
            if not os.access(filename, os.R_OK):
                ErrorDialog(
                    _('Cannot open file'),
                    _('You do not have read access to the selected file.'),
                    parent=self.uistate.window)
                return True
        else:
            try:
                f = file(filename,'w')
                f.close()
                os.remove(filename)
            except IOError:
                ErrorDialog(
                    _('Cannot create file'),
                    _('You do not have write access to the selected file.'),
                    parent=self.uistate.window)
                return True

        return False

    def do_import(self, importer, filename):
        self.import_info = None
        self._begin_progress()
        self.uistate.set_sensitive(False)
        self.uistate.viewmanager.enable_menu(False)

        try:
            #an importer can return an object with info, object.info_text()
            #returns that info. Otherwise None is set to import_info
            self.import_info = importer(self.dbstate.db, filename,
                            User(callback=self._pulse_progress,
                                 uistate=self.uistate,
                                 dbstate=self.dbstate))
            dirname = os.path.dirname(filename) + os.path.sep
            config.set('paths.recent-import-dir', dirname)
        except UnicodeError as msg:
            ErrorDialog(
                _("Could not import file: %s") % filename,
                _("This file incorrectly identifies its character "
                  "set, so it cannot be accurately imported. Please fix the "
                  "encoding, and import again") + "\n\n %s" % msg,
                parent=self.uistate.window)
        except Exception:
            _LOG.error("Failed to import database.", exc_info=True)
        self.uistate.set_sensitive(True)
        self.uistate.viewmanager.enable_menu(True)
        self._end_progress()

    def build_menu_names(self, obj): # this is meaningless since it's modal
        return (self.title, None)

    def _begin_progress(self):
        self.uistate.set_busy_cursor(True)
        self.uistate.progress.show()
        self.uistate.pulse_progressbar(0)

    def _pulse_progress(self, value):
        self.uistate.pulse_progressbar(value)

    def _end_progress(self):
        self.uistate.set_busy_cursor(False)
        self.uistate.progress.hide()
