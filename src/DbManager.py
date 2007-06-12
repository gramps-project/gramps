#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"""
Provides the management of databases. This includes opening, renaming,
creating, and deleting of databases.
"""

__author__   = "Donald N. Allingham"
__revision__ = "$Revision: 8197 $"

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import const
import os
import time
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".DbManager")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import QuestionDialog
import GrampsDb
import GrampsDbUtils
import Config

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
DEFAULT_DIR = os.path.join(const.home_dir, "grampsdb")
DEFAULT_TITLE = _("Family Tree")
NAME_FILE     = "name.txt"
META_NAME     = "meta_data.db"

NAME_COL  = 0
PATH_COL  = 1
FILE_COL  = 2
DATE_COL  = 3
OPEN_COL  = 5
STOCK_COL = 6

class DbManager:
    """
    Database Manager. Opens a database manager window that allows users to
    create, rename, delete and open databases.
    """

    def __init__(self, dbstate, parent=None):
        """
        Creates the top level window from the glade description, and extracts
        the GTK widgets that are needed.
        """
        self.glade = gtk.glade.XML(const.gladeFile, "dbmanager", "gramps")
        self.top = self.glade.get_widget('dbmanager')
        if parent:
            self.top.set_transient_for(parent)

        self.connect = self.glade.get_widget('ok')
        self.cancel  = self.glade.get_widget('cancel')
        self.new     = self.glade.get_widget('new')
        self.remove  = self.glade.get_widget('remove')
        self.dblist  = self.glade.get_widget('dblist')
        self.rename  = self.glade.get_widget('rename')
        self.repair  = self.glade.get_widget('repair')
        self.model   = None
        self.dbstate = dbstate
        self.column  = None
        self.data_to_delete = None

        if dbstate:
            self.active  = dbstate.db.get_save_path()
        else:
            self.active = None

        self.selection = self.dblist.get_selection()

        self.current_names = []

        self.connect_signals()
        self.build_interface()
        self.populate()

    def connect_signals(self):
        """
        Connects the signals to the buttons on the interface. 
        """
        self.remove.connect('clicked', self.remove_db)
        self.new.connect('clicked', self.new_db)
        self.rename.connect('clicked', self.rename_db)
        self.repair.connect('clicked', self.repair_db)
        self.selection.connect('changed', self.selection_changed)
        self.dblist.connect('button-press-event', self.button_press)

    def button_press(self, obj, event):
        """
        Checks for a double click event. In the tree view, we want to 
        treat a double click as if it was OK button press. However, we have
        to make sure that an item was selected first.
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            data = self.selection.get_selected()
            if data[1]:
                self.top.response(gtk.RESPONSE_OK)
            return True
        return False

    def selection_changed(self, selection):
        """
        Called with the selection is changed in the TreeView. What we
        are trying to detect is the selection or unselection of a row.
        When a row is unselected, the Open, Rename, and Remove buttons
        are set insensitive. If a row is selected, the rename and remove
        buttons are disabled, and the Open button is disabled if the
        row represents a open database.
        """

        # Get the current selection
        store, node = selection.get_selected()

        if not node:
            self.connect.set_sensitive(False)
            self.rename.set_sensitive(False)
            self.repair.set_sensitive(False)
            self.remove.set_sensitive(False)
        else:
            if store.get_value(node, OPEN_COL):
                self.connect.set_sensitive(False)
            else:
                self.connect.set_sensitive(True)
            self.rename.set_sensitive(True)
            self.repair.set_sensitive(True)
            self.remove.set_sensitive(True)

    def build_interface(self):
        """
        Builds the columns for the TreeView. The columns are:

        Icon, Database Name, Last Modified

        The Icon column gets its data from column 6 of the database model.
        It is expecting either None, or a GTK stock icon name

        The Database Name column is an editable column. We connect to the
        'edited' signal, so that we can change the name when the user changes
        the column.

        The last modified column simply displays the last modification time.
        """

        # build the icon column
        render = gtk.CellRendererPixbuf()
        icon_column = gtk.TreeViewColumn('', render, stock_id=STOCK_COL)
        self.dblist.append_column(icon_column)

        # build the database name column
        render = gtk.CellRendererText()
        render.set_property('editable', True)
        render.connect('edited', self.change_name)
        self.column = gtk.TreeViewColumn(_('Family tree name'), render, 
                                         text=NAME_COL)
        self.dblist.append_column(self.column)

        # build the last modified cocolumn
        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_('Last modified'), render, text=DATE_COL)
        self.dblist.append_column(column)

        # set the rules hit
        self.dblist.set_rules_hint(True)

    def populate(self):
        """
        Builds the display model.
        """

        self.model = gtk.ListStore(str, str, str, str, int, bool, str)

        # make the default directory if it does not exist
        try:
            if not os.path.isdir(DEFAULT_DIR):
                os.mkdir(DEFAULT_DIR)
        except (IOError, OSError), msg:
            LOG.error(_("Could not make database directory: ") + str(msg))

        self.current_names = []
        for dpath in os.listdir(DEFAULT_DIR):
            dirpath = os.path.join(DEFAULT_DIR, dpath)
            path_name = os.path.join(dirpath, NAME_FILE)
            if os.path.isfile(path_name):
                name = file(path_name).readline().strip()

                (tval, last) = time_val(dirpath)
                (enable, stock_id) = icon_values(dirpath, self.active)

                self.current_names.append(
                    (name, os.path.join(DEFAULT_DIR, dpath), path_name,
                     last, tval, enable, stock_id))

        self.current_names.sort()
        for items in self.current_names:
            data = [items[0], items[1], items[2], items[3], 
                    items[4], items[5], items[6]]
            self.model.append(data)
        self.dblist.set_model(self.model)

    def run(self):
        """
        Runs the dialog, returning None if nothing has been chosen,
        or the path and name if something has been selected
        """
        value = self.top.run()
        if value == gtk.RESPONSE_OK:
            (model, node) = self.selection.get_selected()
            if node:
                self.top.destroy()
                return (model.get_value(node, PATH_COL),
                        model.get_value(node, NAME_COL))
        self.top.destroy()
        return None

    def change_name(self, text, path, new_text):
        """
        Changes the name of the database. This is a callback from the
        column, which has been marked as editable. 

        If the new string is empty, do nothing. Otherwise, renaming the
        database is simply changing the contents of the name file.
        """
        if len(new_text) > 0:
            node = self.model.get_iter(path)
            filename = self.model.get_value(node, FILE_COL)
            try:
                name_file = open(filename, "w")
                name_file.write(new_text)
                name_file.close()
                self.model.set_value(node, NAME_COL, new_text)
            except (OSError, IOError), msg:
                QuestionDialog.ErrorDialog(
                    _("Could not rename family tree"),
                    str(msg))

    def remove_db(self, obj):
        """
        Callback associated with the Remove button. Get the selected
        row and data, then call the verification dialog.
        """
        store, node = self.selection.get_selected()
        self.data_to_delete = store[store.get_path(node)]

        QuestionDialog.QuestionDialog(
            _("Remove the '%s' database?") % self.data_to_delete[0],
            _("Removing this database will permanently destroy the data."),
            _("Remove database"),
            self.really_delete_db)

        # rebuild the display
        self.populate()

    def really_delete_db(self):
        """
        Delete the selected database. If the databse is open, close it first.
        Then scan the database directory, deleting the files, and finally
        removing the directory.
        """

        # close the database if the user has requested to delete the
        # active database
        if self.data_to_delete[OPEN_COL]:
            self.dbstate.no_database()
            
        try:
            for (top, dirs, files) in os.walk(self.data_to_delete[1]):
                for filename in files:
                    os.unlink(os.path.join(top, filename))
            os.rmdir(self.data_to_delete[1])
        except (IOError, OSError), msg:
            QuestionDialog.ErrorDialog(_("Could not delete family tree"),
                                       str(msg))
            
    def rename_db(self, obj):
        """
        Start the rename process by calling the start_editing option on 
        the line with the cursor.
        """
        store, node = self.selection.get_selected()
        path = self.model.get_path(node)
        self.dblist.set_cursor(path, focus_column=self.column, 
                               start_editing=True)

    def repair_db(self, obj):
        """
        Start the rename process by calling the start_editing option on 
        the line with the cursor.
        """
        store, node = self.selection.get_selected()
        dirname = store[node][1]
        opened = store[node][5]
        if opened:
            self.dbstate.no_database()
        
        # delete files that are not backup files or the .txt file
        for filename in os.listdir(dirname):
            if os.path.splitext(filename)[1] not in (".gbkp", ".txt"):
                os.unlink(os.path.join(dirname,filename))

        dbclass = GrampsDb.gramps_db_factory(db_type = "x-directory/normal")
        db = dbclass(Config.get(Config.TRANSACTIONS))
        db.set_save_path(dirname)
        db.load(dirname, None)
        GrampsDbUtils.Backup.restore(db)
        db.close()

    def new_db(self, obj):
        """
        Callback wrapper around the actual routine that creates the
        new database. Catch OSError and IOError and display a warning 
        message.
        """
        try:
            self.mk_db()
        except (OSError, IOError), msg:
            QuestionDialog.ErrorDialog(_("Could not create family tree"),
                                       str(msg))

    def mk_db(self):
        """
        Create a new database.
        """

        new_path = find_next_db_dir()

        os.mkdir(new_path)
        path_name = os.path.join(new_path, NAME_FILE)

        name_list = [ name[0] for name in self.current_names ]

        title = find_next_db_name(name_list)

        name_file = open(path_name, "w")
        name_file.write(title)
        name_file.close()

        self.current_names.append(title)
        node = self.model.append([title, new_path, path_name, 
                                  _("Never"), 0, False, ''])
        self.selection.select_iter(node)

        path = self.model.get_path(node)
        self.dblist.set_cursor(path, focus_column=self.column, 
                               start_editing=True)

def find_next_db_name(name_list):
    """
    Scan the name list, looking for names that do not yet exist.
    Use the DEFAULT_TITLE as the basis for the database name.
    """
    i = 1
    while True:
        title = "%s %d" % (DEFAULT_TITLE, i)
        if title not in name_list:
            return title
        i += 1

def find_next_db_dir():
    """
    Searches the default directory for the first available default
    database name. Base the name off the current time. In all actuality,
    the first should be valid.
    """
    while True:
        base = "%x" % int(time.time())
        new_path = os.path.join(DEFAULT_DIR, base)
        if not os.path.isdir(new_path):
            break
    return new_path

def time_val(dirpath):
    """
    Return the last modified time of the database. We do this by looking
    at the modification time of the meta db file. If this file does not 
    exist, we indicate that database as never modified.
    """
    meta = os.path.join(dirpath, META_NAME)
    if os.path.isfile(meta):
        tval = os.stat(meta)[9]
        last = time.asctime(time.localtime(tval))
    else:
        tval = 0
        last = _("Never")
    return (tval, last)

def icon_values(dirpath, active):
    """
    If the directory path is the active path, then return values
    that indicate to use the icon, and which icon to use.
    """
    if dirpath == active:
        return (True, gtk.STOCK_OPEN)
    else:
        return (False, "")

