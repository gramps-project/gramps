#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Brian G. Matherly
# Copyright (C) 2009       Gary Burton
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
Provide the management of databases. This includes opening, renaming,
creating, and deleting of databases.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import time
import copy
import subprocess
from urllib.parse import urlparse

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".DbManager")

from gramps.gen.constfunc import win
if win():
    _RCS_FOUND = os.system("rcs -V >nul 2>nul") == 0
    if _RCS_FOUND and "TZ" not in os.environ:
        # RCS requires the "TZ" variable be set.
        os.environ["TZ"] = str(time.timezone)
else:
    _RCS_FOUND = os.system("rcs -V >/dev/null 2>/dev/null") == 0

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.plug import BasePluginManager
_ = glocale.translation.gettext
from gramps.gui.display import display_help
from gramps.gen.const import URL_WIKISTRING, URL_MANUAL_PAGE
from .user import User
from .dialog import ErrorDialog, QuestionDialog, QuestionDialog2, ICON
from .pluginmanager import GuiPluginManager
from gramps.cli.clidbman import CLIDbManager, NAME_FILE, time_val
from .managedwindow import ManagedWindow
from .ddtargets import DdTargets
from gramps.gen.recentfiles import rename_filename, remove_filename
from .glade import Glade
from gramps.gen.db.exceptions import DbException
from gramps.gen.config import config
from gramps.gui.listmodel import ListModel

_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")


#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = _('%s_-_Manage_Family_Trees') % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('Family_Trees_manager_window')

ARCHIVE       = "rev.gramps"
ARCHIVE_V     = "rev.gramps,v"

NAME_COL  = 0
PATH_COL  = 1
FILE_COL  = 2
DATE_COL  = 3
DSORT_COL = 4
OPEN_COL  = 5
ICON_COL = 6
BACKEND_COL = 7

RCS_BUTTON = { True : _('_Extract'), False : _('_Archive') }

class Information(ManagedWindow):
    def __init__(self, uistate, data, parent):
        super().__init__(uistate, [], self)
        self.window = Gtk.Dialog('Gramp')
        self.set_window(self.window, None, _("Database Information"))
        self.window.set_modal(True)
        self.ok = self.window.add_button(_('_OK'), Gtk.ResponseType.OK)
        self.ok.connect('clicked', self.on_ok_clicked)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_default_size(600, 400)
        s = Gtk.ScrolledWindow()
        titles = [
            (_('Setting'),0,150),
            (_('Value'),1,400)
        ]
        treeview = Gtk.TreeView()
        model = ListModel(treeview, titles)
        for key, value in sorted(data.items()):
            model.add((key, str(value),), key)
        s.add(treeview)
        self.window.vbox.pack_start(s, True, True, 0)
        self.show()

    def on_ok_clicked(self, obj):
        self.window.close()

    def build_menu_names(self, obj):
        return (_('Database Information'), None)

class DbManager(CLIDbManager):
    """
    Database Manager. Opens a database manager window that allows users to
    create, rename, delete and open databases.
    """
    ICON_MAP = {
                CLIDbManager.ICON_NONE : None,
                CLIDbManager.ICON_RECOVERY : 'dialog-error',
                CLIDbManager.ICON_LOCK : 'gramps-lock',
                CLIDbManager.ICON_OPEN : 'document-open',
               }

    ERROR = ErrorDialog

    def __init__(self, uistate, dbstate, parent=None):
        """
        Create the top level window from the glade description, and extracts
        the GTK widgets that are needed.
        """
        self.uistate = uistate
        CLIDbManager.__init__(self, dbstate)
        self.glade = Glade(toplevel='dbmanager')
        self.top = self.glade.toplevel

        if parent:
            self.top.set_transient_for(parent)

        for attr in ['connect', 'cancel', 'new', 'remove', 'info',
                     'dblist', 'rename', 'repair', 'rcs', 'msg']:
            setattr(self, attr, self.glade.get_object(attr))

        self.model = None
        self.column  = None
        self.lock_file = None
        self.data_to_delete = None

        self.selection = self.dblist.get_selection()

        self.__connect_signals()
        self.__build_interface()
        self._populate_model()
        self.before_change = ""
        self.after_change = ""

    def __connect_signals(self):
        """
        Connects the signals to the buttons on the interface.
        """
        ddtarget = DdTargets.URI_LIST
        self.top.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        tglist = Gtk.TargetList.new([])
        tglist.add(ddtarget.atom_drag_type, ddtarget.target_flags,
                   ddtarget.app_id)
        self.top.drag_dest_set_target_list(tglist)

        self.remove.connect('clicked', self.__remove_db)
        self.new.connect('clicked', self.__new_db)
        self.rename.connect('clicked', self.__rename_db)
        self.info.connect('clicked', self.__info_db)
        self.repair.connect('clicked', self.__repair_db)
        self.selection.connect('changed', self.__selection_changed)
        self.dblist.connect('button-press-event', self.__button_press)
        self.dblist.connect('key-press-event', self.__key_press)
        self.top.connect('drag_data_received', self.__drag_data_received)
        self.top.connect('drag_motion', drag_motion)
        self.top.connect('drag_drop', drop_cb)
        self.define_help_button(self.glade.get_object('help'),
                WIKI_HELP_PAGE, WIKI_HELP_SEC)

        if _RCS_FOUND:
            self.rcs.connect('clicked', self.__rcs)

    def define_help_button(self, button, webpage='', section=''):
        button.connect('clicked', lambda x: display_help(webpage,
                                                               section))

    def __button_press(self, obj, event):
        """
        Checks for a double click event. In the tree view, we want to
        treat a double click as if it was OK button press. However, we have
        to make sure that an item was selected first.
        """
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            if self.connect.get_property('sensitive'):
                self.top.response(Gtk.ResponseType.OK)
                return True
        return False

    def __key_press(self, obj, event):
        """
        Grab ENTER so it does not start editing the cell, but behaves
        like double click instead
        """
        if event.keyval in (_RETURN, _KP_ENTER):
            if self.connect.get_property('sensitive'):
                self.top.response(Gtk.ResponseType.OK)
                return True
        return False

    def __selection_changed(self, selection):
        """
        Called when the selection is changed in the TreeView.
        """
        self.__update_buttons(selection)

    def __update_buttons(self, selection):
        """
        What we are trying to detect is the selection or unselection of a row.
        When a row is unselected, the Open, Rename, and Remove buttons
        are set insensitive. If a row is selected, the rename and remove
        buttons are disabled, and the Open button is disabled if the
        row represents a open database.
        """

        # Get the current selection
        store, node = selection.get_selected()

        # if nothing is selected
        if not node:
            self.connect.set_sensitive(False)
            self.rename.set_sensitive(False)
            self.info.set_sensitive(False)
            self.rcs.set_sensitive(False)
            self.repair.set_sensitive(False)
            self.remove.set_sensitive(False)
            return

        path = self.model.get_path(node)
        if path is None:
            return

        is_rev = len(path.get_indices()) > 1
        self.rcs.set_label(RCS_BUTTON[is_rev])

        if store.get_value(node, ICON_COL) == 'document-open':
            self.connect.set_sensitive(False)
            if _RCS_FOUND:
                self.rcs.set_sensitive(True)
        else:
            self.connect.set_sensitive(not is_rev)
            if _RCS_FOUND and is_rev:
                self.rcs.set_sensitive(True)
            else:
                self.rcs.set_sensitive(False)

        if store.get_value(node, ICON_COL) == 'dialog-error':
            path = store.get_value(node, PATH_COL)
            backup = os.path.join(path, "person.gbkp")
            self.repair.set_sensitive(os.path.isfile(backup))
        else:
            self.repair.set_sensitive(False)

        self.rename.set_sensitive(True)
        self.info.set_sensitive(True)
        self.remove.set_sensitive(True)
        self.new.set_sensitive(True)

    def __build_interface(self):
        """
        Builds the columns for the TreeView. The columns are:

        Icon, Database Name, Last Modified, Backend Type

        The Icon column gets its data from column 6 of the database model.
        It is expecting either None, or a GTK stock icon name

        The Database Name column is an editable column. We connect to the
        'edited' signal, so that we can change the name when the user changes
        the column.

        The last accessed column simply displays the last time famtree was
        opened.

        The Backend Type column is a string based on database backend.
        """
        # Put some help on the buttons:
        dbid = config.get('behavior.database-backend')
        backend_type = self.get_backend_name_from_dbid(dbid)
        self.new.set_tooltip_text(backend_type)

        # build the database name column
        render = Gtk.CellRendererText()
        render.set_property('ellipsize', Pango.EllipsizeMode.END)
        render.connect('edited', self.__change_name)
        render.connect('editing-canceled', self.__stop_edit)
        render.connect('editing-started', self.__start_edit)
        self.column = Gtk.TreeViewColumn(_('Family Tree name'), render,
                                         text=NAME_COL)
        self.column.set_sort_column_id(NAME_COL)
        self.column.set_sort_indicator(True)
        self.column.set_resizable(True)
        self.column.set_min_width(250)
        self.dblist.append_column(self.column)
        self.name_renderer = render

        # build the icon column
        render = Gtk.CellRendererPixbuf()
        #icon_column = Gtk.TreeViewColumn(_('Status'), render,
                                         #icon_name=ICON_COL)
        icon_column = Gtk.TreeViewColumn(_('Status'), render)
        icon_column.set_cell_data_func(render, bug_fix)
        icon_column.set_sort_column_id(ICON_COL)
        self.dblist.append_column(icon_column)

        # build the backend column
        render = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_('Database Type'), render, text=BACKEND_COL)
        column.set_sort_column_id(BACKEND_COL)
        column.set_sort_indicator(True)
        column.set_resizable(True)
        self.dblist.append_column(column)

        # build the last accessed column
        render = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_('Last accessed'), render, text=DATE_COL)
        column.set_sort_column_id(DSORT_COL)
        self.dblist.append_column(column)

    def __populate(self):
        """
        Builds the data and the display model.
        """
        self._populate_cli()
        self._populate_model()

    def _populate_model(self):
        """
        Builds the display model.
        """
        self.model = Gtk.TreeStore(str, str, str, str, int, bool, str, str)

        #use current names to set up the model
        for items in self.current_names:
            data = list(items[:8])
            backend_type = self.get_backend_name_from_dbid(data[7])
            version = str(".".join([str(v) for v in items[8]]))
            node = self.model.append(None, data[:-1] + [backend_type + ", " + version])
            for rdata in find_revisions(os.path.join(items[1], ARCHIVE_V)):
                data = [rdata[2], rdata[0], items[1], rdata[1], 0, False, "", 
                        backend_type + ", " + version]
                self.model.append(node, data)
        self.model.set_sort_column_id(NAME_COL, Gtk.SortType.ASCENDING)
        self.dblist.set_model(self.model)

    def existing_name(self, name, skippath=None):
        """
        Return true if a name is present in the model already.
        If skippath given, the name of skippath is not considered
        """
        iter = self.model.get_iter_first()
        while (iter):
            path = self.model.get_path(iter)
            if path == skippath:
                pass
            else:
                itername = self.model.get_value(iter, NAME_COL)
                if itername.strip() == name.strip():
                    return True
            iter = self.model.iter_next(iter)
        return False

    def run(self):
        """
        Runs the dialog, returning None if nothing has been chosen,
        or the path and name if something has been selected
        """
        while True:
            value = self.top.run()
            if value == Gtk.ResponseType.OK:
                store, node = self.selection.get_selected()
                # don't open a locked file
                if store.get_value(node, ICON_COL) == 'gramps-lock':
                    self.__ask_to_break_lock(store, node)
                    continue
                # don't open a version
                if len(store.get_path(node).get_indices()) > 1:
                    continue
                if node:
                    self.top.destroy()
                    del self.selection
                    del self.name_renderer
                    path = store.get_value(node, PATH_COL)
                    return (path, store.get_value(node, NAME_COL))
            else:
                self.top.destroy()
                del self.selection
                del self.name_renderer
                return None

    def __ask_to_break_lock(self, store, node):
        """
        Prompts the user for permission to break the lock file that another
        process has set on the file.
        """
        path = store.get_path(node)
        self.lock_file = store[path][PATH_COL]

        QuestionDialog(
            _("Break the lock on the '%s' database?") % store[path][0],
            _("Gramps believes that someone else is actively editing "
              "this database. You cannot edit this database while it "
              "is locked. If no one is editing the database you may "
              "safely break the lock. However, if someone else is editing "
              "the database and you break the lock, you may corrupt the "
              "database."),
            _("Break lock"),
            self.__really_break_lock, self.top)

    def __really_break_lock(self):
        """
        Deletes the lock file associated with the selected database, then updates
        the display appropriately.
        """
        try:
            self.break_lock(self.lock_file)
            store, node = self.selection.get_selected()
            dbpath = store.get_value(node, PATH_COL)
            (tval, last) = time_val(dbpath)
            store.set_value(node, OPEN_COL, 0)
            store.set_value(node, ICON_COL, "")
            store.set_value(node, DATE_COL, last)
            store.set_value(node, DSORT_COL, tval)
        except IOError:
            return

    def __stop_edit(self, *args):
        self.name_renderer.set_property('editable', False)
        self.__update_buttons(self.selection)

    def __start_edit(self, *args):
        """
        Do not allow to click Load while changing name, to force users to finish
        the action of renaming. Hack around the fact that clicking button
        sends a 'editing-canceled' signal loosing the new name
        """
        self.connect.set_sensitive(False)
        self.rename.set_sensitive(False)
        self.info.set_sensitive(False)
        self.rcs.set_sensitive(False)
        self.repair.set_sensitive(False)
        self.remove.set_sensitive(False)
        self.new.set_sensitive(False)

    def __change_name(self, renderer_sel, path, new_text):
        """
        Change the name of the database. This is a callback from the
        column, which has been marked as editable.

        If the new string is empty, do nothing. Otherwise, renaming the
        database is simply changing the contents of the name file.
        """
        #path is a string, convert to TreePath first
        path = Gtk.TreePath(path=path)
        if len(new_text) > 0:
            node = self.model.get_iter(path)
            old_text = self.model.get_value(node, NAME_COL)
            if self.model.get_value(node, ICON_COL) != None:
                # this database is loaded. We must change the title
                # in case we change the name several times before quitting,
                # we save the first old name.
                if self.before_change == "":
                    self.before_change = old_text
                self.after_change = new_text
            if not old_text.strip() == new_text.strip():
                if len(path.get_indices()) > 1 :
                    self.__rename_revision(path, new_text)
                else:
                    self.__rename_database(path, new_text)

        self.name_renderer.set_property('editable', False)
        self.__update_buttons(self.selection)

    def __rename_revision(self, path, new_text):
        """
        Renames the RCS revision using the rcs command. The rcs command
        is in the format of:

           rcs -mREV:NEW_NAME archive

        """
        node = self.model.get_iter(path)
        db_dir = self.model.get_value(node, FILE_COL)
        rev = self.model.get_value(node, PATH_COL)
        archive = os.path.join(db_dir, ARCHIVE_V)

        cmd = [ "rcs", "-x,v", "-m%s:%s" % (rev, new_text), archive ]

        proc = subprocess.Popen(cmd, stderr = subprocess.PIPE)
        status = proc.wait()
        message = "\n".join(proc.stderr.readlines())
        proc.stderr.close()
        del proc

        if status != 0:
            DbManager.ERROR(
                _("Rename failed"),
                _("An attempt to rename a version failed "
                  "with the following message:\n\n%s") % message
                )
        else:
            self.model.set_value(node, NAME_COL, new_text)
            #scroll to new position
            store, node = self.selection.get_selected()
            tree_path = store.get_path(node)
            self.dblist.scroll_to_cell(tree_path, None, False, 0.5, 0.5)

    def __rename_database(self, path, new_text):
        """
        Renames the database by writing the new value to the name.txt file
        """
        new_text = new_text.strip()
        node = self.model.get_iter(path)
        filename = self.model.get_value(node, FILE_COL)
        if self.existing_name(new_text, skippath=path):
            DbManager.ERROR(_("Could not rename the Family Tree."),
                  _("Family Tree already exists, choose a unique name."))
            return
        old_text, new_text = self.rename_database(filename, new_text)
        if not (old_text is None):
            rename_filename(old_text, new_text)
            self.model.set_value(node, NAME_COL, new_text)
        #scroll to new position
        store, node = self.selection.get_selected()
        tree_path = store.get_path(node)
        self.dblist.scroll_to_cell(tree_path, None, False, 0.5, 0.5)

    def __rcs(self, obj):
        """
        Callback for the RCS button. If the tree path is > 1, then we are
        on an RCS revision, in which case we can check out. If not, then
        we can only check in.
        """
        store, node = self.selection.get_selected()
        tree_path = store.get_path(node)
        if len(tree_path.get_indices()) > 1:
            parent_node = store.get_iter((tree_path[0],))
            parent_name = store.get_value(parent_node, NAME_COL)
            name = store.get_value(node, NAME_COL)
            revision = store.get_value(node, PATH_COL)
            db_path = store.get_value(node, FILE_COL)

            self.__checkout_copy(parent_name, name, revision, db_path)
        else:
            base_path = self.dbstate.db.get_save_path()
            archive = os.path.join(base_path, ARCHIVE)
            check_in(self.dbstate.db, archive, User(), self.__start_cursor)
            self.__end_cursor()

        self.__populate()

    def __checkout_copy(self, parent_name, name, revision, db_path):
        """
        Create a new database, then extracts a revision from RCS and
        imports it into the db
        """
        new_path, newname = self._create_new_db("%s : %s" % (parent_name, name))

        self.__start_cursor(_("Extracting archive..."))

        dbase = self.dbstate.make_database("bsddb")
        dbase.load(new_path, None)

        self.__start_cursor(_("Importing archive..."))
        check_out(dbase, revision, db_path, User())
        self.__end_cursor()
        dbase.close()

    def __remove_db(self, obj):
        """
        Callback associated with the Remove button. Get the selected
        row and data, then call the verification dialog.
        """
        store, node = self.selection.get_selected()
        path = store.get_path(node)
        self.data_to_delete = store[path]

        if len(path.get_indices()) == 1:
            QuestionDialog(
                _("Remove the '%s' Family Tree?") % self.data_to_delete[0],
                _("Removing this Family Tree will permanently destroy the data."),
                _("Remove Family Tree"),
                self.__really_delete_db, parent=self.top)
        else:
            rev = self.data_to_delete[0]
            parent = store[(path[0],)][0]
            QuestionDialog(
                _("Remove the '%(revision)s' version of '%(database)s'") % {
                    'revision' : rev,
                    'database' : parent
                    },
                _("Removing this version will prevent you from "
                  "extracting it in the future."),
                _("Remove version"),
                self.__really_delete_version, parent=self.top)

    def __really_delete_db(self):
        """
        Delete the selected database. If the database is open, close it first.
        Then scan the database directory, deleting the files, and finally
        removing the directory.
        """

        # close the database if the user has requested to delete the
        # active database
        if self.data_to_delete[PATH_COL] == self.active:
            self.dbstate.no_database()

        store, node = self.selection.get_selected()
        path = store.get_path(node)
        node = self.model.get_iter(path)
        filename = self.model.get_value(node, FILE_COL)
        try:
            name_file = open(filename, "r")
            file_name_to_delete=name_file.read()
            name_file.close()
            remove_filename(file_name_to_delete)
            directory = self.data_to_delete[1]
            for (top, dirs, files) in os.walk(directory):
                for filename in files:
                    os.unlink(os.path.join(top, filename))
            os.rmdir(directory)
        except (IOError, OSError) as msg:
            DbManager.ERROR(_("Could not delete Family Tree"),
                            str(msg))
        # rebuild the display
        self.__populate()

    def __really_delete_version(self):
        """
        Delete the selected database. If the database is open, close it first.
        Then scan the database directory, deleting the files, and finally
        removing the directory.
        """
        db_dir = self.data_to_delete[FILE_COL]
        rev = self.data_to_delete[PATH_COL]
        archive = os.path.join(db_dir, ARCHIVE_V)

        cmd = [ "rcs", "-x,v", "-o%s" % rev, "-q", archive ]

        proc = subprocess.Popen(cmd, stderr = subprocess.PIPE)
        status = proc.wait()
        message = "\n".join(proc.stderr.readlines())
        proc.stderr.close()
        del proc

        if status != 0:
            DbManager.ERROR(
                _("Deletion failed"),
                _("An attempt to delete a version failed "
                  "with the following message:\n\n%s") % message
                )

        # rebuild the display
        self.__populate()

    def __rename_db(self, obj):
        """
        Start the rename process by calling the start_editing option on
        the line with the cursor.
        """
        store, node = self.selection.get_selected()
        path = self.model.get_path(node)
        self.name_renderer.set_property('editable', True)
        self.dblist.set_cursor(path, self.column, True)

    def __info_db(self, obj):
        """
        Show info on this database.
        """
        store, node = self.selection.get_selected()
        name = store[node][0]
        dirname = store[node][1]
        # if this is open, get info from there, otherwise, temp open?
        summary = self.get_dbdir_summary(dirname, name)
        Information(self.uistate, summary, parent=self.top)

    def __repair_db(self, obj):
        """
        Start the repair process by calling the start_editing option on
        the line with the cursor.
        """
        store, node = self.selection.get_selected()
        dirname = store[node][1]

        #First ask user if he is really sure :-)
        yes_no = QuestionDialog2(
            _("Repair Family Tree?"),
            _(
              "If you click %(bold_start)sProceed%(bold_end)s, Gramps will "
              "attempt to recover your Family Tree from the last good "
              "backup. There are several ways this can cause unwanted "
              "effects, so %(bold_start)sbackup%(bold_end)s the "
              "Family Tree first.\nThe Family Tree you have selected "
              "is stored in %(dirname)s.\n\n"
              "Before doing a repair, verify that the Family Tree can "
              "really no longer be opened, as the database back-end can "
              "recover from some errors automatically.\n\n"
              "%(bold_start)sDetails:%(bold_end)s Repairing a Family Tree "
              "actually uses the last backup of the Family Tree, which "
              "Gramps stored on last use. If you have worked for "
              "several hours/days without closing Gramps, then all "
              "this information will be lost! If the repair fails, then "
              "the original Family Tree will be lost forever, hence "
              "a backup is needed. If the repair fails, or too much "
              "information is lost, you can fix the original "
              "Family Tree manually. For details, see the webpage\n"
              "%(gramps_wiki_recover_url)s\n"
              "Before doing a repair, try to open the Family Tree "
              "in the normal manner. Several errors that trigger the "
              "repair button can be fixed automatically. "
              "If this is the case, you can disable the repair button "
              "by removing the file %(recover_file)s in the "
              "Family Tree directory."
             ) % { 'bold_start'   : '<b>' ,
                   'bold_end'     : '</b>' ,
                   'recover_file' : '<i>need_recover</i>' ,
                   'gramps_wiki_recover_url' :
                       URL_WIKISTRING + 'Recover_corrupted_family_tree',
                   'dirname'      : dirname },
            _("Proceed, I have taken a backup"),
            _("Stop"))
        prompt = yes_no.run()
        if not prompt:
            return

        opened = store[node][OPEN_COL]
        if opened:
            self.dbstate.no_database()

        # delete files that are not backup files or the .txt file
        for filename in os.listdir(dirname):
            if os.path.splitext(filename)[1] not in (".gbkp", ".txt"):
                fname = os.path.join(dirname, filename)
                os.unlink(fname)

        newdb = self.dbstate.make_database("bsddb")
        newdb.write_version(dirname)

        dbase = self.dbstate.make_database("bsddb")
        dbase.set_save_path(dirname)
        dbase.load(dirname, None)

        self.__start_cursor(_("Rebuilding database from backup files"))

        try:
            dbase.restore()
        except DbException as msg:
            DbManager.ERROR(_("Error restoring backup data"), msg)

        self.__end_cursor()

        dbase.close()
        self.dbstate.no_database()
        self.__populate()

    def __start_cursor(self, msg):
        """
        Set the cursor to the busy state, and displays the associated
        message
        """
        self.msg.set_label(msg)
        self.top.get_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
        while (Gtk.events_pending()):
            Gtk.main_iteration()

    def __end_cursor(self):
        """
        Set the cursor back to normal and clears the message
        """
        self.top.get_window().set_cursor(None)
        self.msg.set_label("")

    def __new_db(self, obj):
        """
        Callback wrapper around the actual routine that creates the
        new database. Catch OSError and IOError and display a warning
        message.
        """
        self.new.set_sensitive(False)
        dbid = config.get('behavior.database-backend')
        if dbid:
            try:
                self._create_new_db(dbid=dbid)
            except (OSError, IOError) as msg:
                DbManager.ERROR(_("Could not create Family Tree"),
                                str(msg))
        self.new.set_sensitive(True)

    def get_backend_name_from_dbid(self, dbid):
        pmgr = GuiPluginManager.get_instance()
        for plugin in pmgr.get_reg_databases():
            if plugin.id == dbid:
                return plugin._name
        return _("Unknown")

    def _create_new_db(self, title=None, create_db=True, dbid=None):
        """
        Create a new database, append to model
        """
        new_path, title = self.create_new_db_cli(title, create_db, dbid)
        path_name = os.path.join(new_path, NAME_FILE)
        (tval, last) = time_val(new_path)
        backend_type = self.get_backend_name_from_dbid(dbid)
        node = self.model.append(None, [title, new_path, path_name,
                                        last, tval, False, '', backend_type])
        self.selection.select_iter(node)
        path = self.model.get_path(node)
        self.name_renderer.set_property('editable', True)
        self.dblist.set_cursor(path, self.column, True)
        return new_path, title

    def __drag_data_received(self, widget, context, xpos, ypos, selection,
                             info, rtime):
        """
        Handle the reception of drag data
        """
        drag_value = selection.get_data()
        fname = None
        type = None
        title = None
        # Allow any type of URL ("file://", "http://", etc):
        if drag_value and urlparse(drag_value).scheme != "":
            fname, title = [], []
            for treename in [v.strip() for v in drag_value.split("\n") if v.strip() != '']:
                f, t = self.import_new_db(treename, User())
                fname.append(f)
                title.append(t)
        return fname, title

def drag_motion(wid, context, xpos, ypos, time_stamp):
    """
    DND callback that is called on a DND drag motion begin
    """
    Gdk.drag_status(context, Gdk.DragAction.COPY, time_stamp)
    return True

def drop_cb(wid, context, xpos, ypos, time_stamp):
    """
    DND callback that finishes the DND operation
    """
    Gtk.drag_finish(context, True, False, time_stamp)
    return True

def find_revisions(name):
    """
    Finds all the revisions of the specified RCS archive.
    """
    import re

    rev  = re.compile("\s*revision\s+([\d\.]+)")
    date = re.compile("date:\s+(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)[-+]\d\d;")

    if not os.path.isfile(name) or not _RCS_FOUND:
        return []

    rlog = [ "rlog", "-x,v", "-zLT" , name ]

    proc = subprocess.Popen(rlog, stdout = subprocess.PIPE)
    proc.wait()

    revlist = []
    date_str = ""
    rev_str = ""
    com_str = ""

    get_next = False
    if os.path.isfile(name):
        for line in proc.stdout:
            if not isinstance(line, str):
                # we assume utf-8 ...
                line = line.decode('utf-8')
            match = rev.match(line)
            if match:
                rev_str = copy.copy(match.groups()[0])
                continue
            match = date.match(line)
            if match:
                date_str = time.strftime('%x %X',
                        time.strptime(match.groups()[0], '%Y-%m-%d %H:%M:%S'))

                get_next = True
                continue
            if get_next:
                get_next = False
                com_str = line.strip()
                revlist.append((rev_str, date_str, com_str))
    proc.stdout.close()
    del proc
    return revlist



def check_out(dbase, rev, path, user):
    """
    Checks out the revision from rcs, and loads the resulting XML file
    into the database.
    """
    co_cmd   = [ "co", "-x,v", "-q%s" % rev] + [ os.path.join(path, ARCHIVE),
                                                 os.path.join(path, ARCHIVE_V)]

    proc = subprocess.Popen(co_cmd, stderr = subprocess.PIPE)
    status = proc.wait()
    message = "\n".join(proc.stderr.readlines())
    proc.stderr.close()
    del proc

    if status != 0:
        user.notify_error(
            _("Retrieve failed"),
            _("An attempt to retrieve the data failed "
              "with the following message:\n\n%s") % message
            )
        return

    pmgr = GuiPluginManager.get_instance()
    for plugin in pmgr.get_import_plugins():
        if plugin.get_extension() == "gramps":
            rdr = plugin.get_import_function()

    xml_file = os.path.join(path, ARCHIVE)
    rdr(dbase, xml_file, user)
    os.unlink(xml_file)

def check_in(dbase, filename, user, cursor_func = None):
    """
    Checks in the specified file into RCS
    """
    init   = [ "rcs", '-x,v', '-i', '-U', '-q', '-t-"Gramps database"' ]
    ci_cmd = [ "ci", '-x,v', "-q", "-f" ]
    archive_name = filename + ",v"

    glade = Glade(toplevel='comment')
    top = glade.toplevel
    text = glade.get_object('description')
    top.run()
    comment = text.get_text()
    top.destroy()

    if not os.path.isfile(archive_name):
        cmd = init + [archive_name]
        proc = subprocess.Popen(cmd,
                                stderr = subprocess.PIPE)
        status = proc.wait()
        message = "\n".join(proc.stderr.readlines())
        proc.stderr.close()
        del proc

        if status != 0:
            ErrorDialog(
                _("Archiving failed"),
                _("An attempt to create the archive failed "
                  "with the following message:\n\n%s") % message
                )

    if cursor_func:
        cursor_func(_("Creating data to be archived..."))

    plugin_manager = GuiPluginManager.get_instance()
    for plugin in plugin_manager.get_export_plugins():
        if plugin.get_extension() == "gramps":
            export_function = plugin.get_export_function()
            export_function(dbase, filename, user)

    if cursor_func:
        cursor_func(_("Saving archive..."))

    cmd = ci_cmd + ['-m%s' % comment, filename, archive_name ]
    proc = subprocess.Popen(cmd,
                            stderr = subprocess.PIPE)

    status = proc.wait()
    message = "\n".join(proc.stderr.readlines())
    proc.stderr.close()
    del proc

    if status != 0:
        ErrorDialog(
            _("Archiving failed"),
            _("An attempt to archive the data failed "
              "with the following message:\n\n%s") % message
            )

def bug_fix(column, renderer, model, iter_, data):
    """
    Cell data function to set the status column.

    There is a bug in pygobject which prevents us from setting a value to
    None using the TreeModel set_value method.  Instead we set it to an empty
    string and convert it to None here.
    """
    icon_name = model.get_value(iter_, ICON_COL)
    if icon_name == '':
        icon_name = None
    renderer.set_property('icon-name', icon_name)
