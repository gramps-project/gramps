#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
import os
import time
import subprocess
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".DbManager")

if os.sys.platform == "win32":
    _rcs_found = os.system("rcs -V >nul 2>nul") == 0
else:
    _rcs_found = os.system("rcs -V >/dev/null 2>/dev/null") == 0

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
import const
import QuestionDialog
import GrampsDb
import GrampsDbUtils
import Config

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
DEFAULT_TITLE = _("Family Tree")
NAME_FILE     = "name.txt"
META_NAME     = "meta_data.db"
ARCHIVE       = "rev.gramps"
ARCHIVE_V     = "rev.gramps,v"

NAME_COL  = 0
PATH_COL  = 1
FILE_COL  = 2
DATE_COL  = 3
DSORT_COL = 4
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
        self.rcs     = self.glade.get_widget('rcs')
        self.msg     = self.glade.get_widget('msg')
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

        self.__connect_signals()
        self.__build_interface()
        self.__populate()

    def __connect_signals(self):
        """
        Connects the signals to the buttons on the interface. 
        """
        self.remove.connect('clicked', self.__remove_db)
        self.new.connect('clicked', self.__new_db)
        self.rename.connect('clicked', self.__rename_db)
        self.repair.connect('clicked', self.__repair_db)
        if _rcs_found:
            self.rcs.connect('clicked', self.__rcs)
        self.selection.connect('changed', self.__selection_changed)
        self.dblist.connect('button-press-event', self.__button_press)

    def __button_press(self, obj, event):
        """
        Checks for a double click event. In the tree view, we want to 
        treat a double click as if it was OK button press. However, we have
        to make sure that an item was selected first.
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            store, node = self.selection.get_selected()
            # don't open a locked file
            if store.get_value(node,STOCK_COL) == 'gramps-lock':
                self.__ask_to_break_lock(store, node)
                return
            # don't open a version
            if len(store.get_path(node)) > 1:
                return
            if store.get_value(node,PATH_COL):
                self.top.response(gtk.RESPONSE_OK)
            return True
        return False

    def __selection_changed(self, selection):
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
            self.rcs.hide()
            self.repair.hide()
            self.remove.set_sensitive(False)
        else:

            is_rev = len(self.model.get_path(node)) > 1

            if is_rev:
                self.rcs.set_label(_("Restore"))
            else:
                self.rcs.set_label(_("Archive"))
            self.rename.set_sensitive(True)
        
            if store.get_value(node, OPEN_COL):
                self.connect.set_sensitive(False)
                if _rcs_found:
                    self.rcs.show()
            else:
                self.connect.set_sensitive(not is_rev)
                if _rcs_found and is_rev:
                    self.rcs.show()
                else:
                    self.rcs.hide()
            if store.get_value(node, STOCK_COL) == gtk.STOCK_DIALOG_ERROR:
                path = store.get_value(node, PATH_COL)
                if os.path.isfile(os.path.join(path,"person.gbkp")):
                    self.repair.show()
                else:
                    self.repair.hide()
            else:
                self.repair.hide()
                
            self.remove.set_sensitive(True)

    def __build_interface(self):
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

        # build the database name column
        render = gtk.CellRendererText()
        render.set_property('editable', True)
        render.connect('edited', self.__change_name)
        self.column = gtk.TreeViewColumn(_('Family tree name'), render, 
                                         text=NAME_COL)
        self.column.set_sort_column_id(NAME_COL)
        self.dblist.append_column(self.column)

        # build the icon column
        render = gtk.CellRendererPixbuf()
        icon_column = gtk.TreeViewColumn(_('Status'), render, 
                                         stock_id=STOCK_COL)
        self.dblist.append_column(icon_column)

        # build the last modified cocolumn
        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_('Last modified'), render, text=DATE_COL)
        column.set_sort_column_id(DSORT_COL)
        self.dblist.append_column(column)

        # set the rules hit
        self.dblist.set_rules_hint(True)

    def __populate(self):
        """
        Builds the display model.
        """
        self.model = gtk.TreeStore(str, str, str, str, int, bool, str)

        # make the default directory if it does not exist

        dbdir = os.path.expanduser(Config.get(Config.DATABASE_PATH))

        try:
            if not os.path.isdir(dbdir):
                os.makedirs(dbdir)
        except (IOError, OSError), msg:
            LOG.error(_("Could not make database directory: ") + str(msg))

        self.current_names = []
        
        for dpath in os.listdir(dbdir):
            dirpath = os.path.join(dbdir, dpath)
            path_name = os.path.join(dirpath, NAME_FILE)
            if os.path.isfile(path_name):
                name = file(path_name).readline().strip()

                (tval, last) = time_val(dirpath)
                (enable, stock_id) = icon_values(dirpath, self.active, 
                                                 self.dbstate.db.is_open())

                if (stock_id == 'gramps-lock'):
                    try:
                        fname = os.path.join(dirpath, "lock")
                        f = open(fname)
                        last = f.read().strip()
                        f.close()
                    except:
                        last = _("Unknown")

                self.current_names.append(
                    (name, os.path.join(dbdir, dpath), path_name,
                     last, tval, enable, stock_id))

        self.current_names.sort()
        for items in self.current_names:
            data = [items[0], items[1], items[2], items[3], 
                    items[4], items[5], items[6]]
            node = self.model.append(None, data)
            for rdata in find_revisions(os.path.join(items[1], ARCHIVE_V)):
                data = [ rdata[2], rdata[0], items[1], rdata[1], 0, False, "" ]
                self.model.append(node, data)
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

    def __ask_to_break_lock(self, store, node):
        path = store.get_path(node)
        self.lock_file = store[path][PATH_COL]

        QuestionDialog.QuestionDialog(
            _("Break the lock on the '%s' database?") % store[path][0],
            _("GRAMPS believes that someone else is actively editing "
              "this database. You cannot edit this database while it "
              "is locked. If no one is editing the database you may "
              "safely break the lock. However, if someone else is editing "
              "the database and you break the lock, you may corrupt the "
              "database."),
            _("Break lock"),
            self.__really_break_lock)

    def __really_break_lock(self):
        try:
            os.unlink(os.path.join(self.lock_file, "lock"))
            store, node = self.selection.get_selected()
            dbpath = store.get_value(node, PATH_COL)
            (tval, last) = time_val(dbpath)
            store.set_value(node, OPEN_COL, 0)
            store.set_value(node, STOCK_COL, "")
            store.set_value(node, DATE_COL, last)
            store.set_value(node, DSORT_COL, tval)
        except:
            pass

    def __change_name(self, text, path, new_text):
        """
        Changes the name of the database. This is a callback from the
        column, which has been marked as editable. 

        If the new string is empty, do nothing. Otherwise, renaming the
        database is simply changing the contents of the name file.
        """
        if len(new_text) > 0 and text != new_text:
            if len(path) > 1 :
                self.__rename_revision(path, new_text)
            else:
                self.__rename_database(path, new_text)

    def __rename_revision(self, path, new_text):
        node = self.model.get_iter(path)
        db_dir = self.model.get_value(node, FILE_COL)
        rev = self.model.get_value(node, PATH_COL)
        archive = os.path.join(db_dir, ARCHIVE_V)

        cmd = [ "rcs", "-m%s:%s" % (rev, new_text), archive ]

        proc = subprocess.Popen(cmd, stderr = subprocess.PIPE)
        status = proc.wait()
        message = "\n".join(proc.stderr.readlines())
        proc.stderr.close()
        del proc

        if status != 0:
            from QuestionDialog import ErrorDialog
            
            ErrorDialog(
                _("Rename failed"),
                _("An attempt to rename a version failed "
                  "with the following message:\n\n%s") % message
                )
        else:
            self.model.set_value(node, NAME_COL, new_text)

    def __rename_database(self, path, new_text):
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

    def __rcs(self, obj):
        store, node = self.selection.get_selected()
        tree_path = store.get_path(node)
        if len(tree_path) > 1:
            parent_node = store.get_iter((tree_path[0],))
            parent_name = store.get_value(parent_node, NAME_COL)
            name = store.get_value(node, NAME_COL)
            revision = store.get_value(node, PATH_COL)
            db_path = store.get_value(node, FILE_COL)

            new_path = self.__create_new_db("%s : %s" % (parent_name, name))
            trans = Config.TRANSACTIONS
            dbtype = 'x-directory/normal'

            self.__start_cursor(_("Extracting archive..."))
            db = GrampsDb.gramps_db_factory(dbtype)(trans)
            db.load(new_path, None)

            self.__start_cursor(_("Importing archive..."))
            check_out(db, revision, db_path, name, None)
            self.__end_cursor()
            db.close()
            self.__populate()
        else:
            base_path = self.dbstate.db.get_save_path()
            archive = os.path.join(base_path, ARCHIVE) 
            check_in(self.dbstate.db, archive, None, self.__start_cursor)
            self.__end_cursor()
            self.__populate()
        
    def __remove_db(self, obj):
        """
        Callback associated with the Remove button. Get the selected
        row and data, then call the verification dialog.
        """
        store, node = self.selection.get_selected()
        path = store.get_path(node)
        self.data_to_delete = store[path]

        if len(path) == 1:
            QuestionDialog.QuestionDialog(
                _("Remove the '%s' database?") % self.data_to_delete[0],
                _("Removing this database will permanently destroy the data."),
                _("Remove database"),
                self.__really_delete_db)
        else:
            rev = self.data_to_delete[0]
            parent = store[(path[0],)][0]
            QuestionDialog.QuestionDialog(
                _("Remove the '%s' version of %s") % (rev, parent),
                _("Removing this version will prevent you from "
                  "restoring it in the future."),
                _("Remove version"),
                self.__really_delete_version)

    def __really_delete_db(self):
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
        # rebuild the display
        self.__populate()
            
    def __really_delete_version(self):
        """
        Delete the selected database. If the databse is open, close it first.
        Then scan the database directory, deleting the files, and finally
        removing the directory.
        """
        db_dir = self.data_to_delete[FILE_COL]
        rev = self.data_to_delete[PATH_COL]
        archive = os.path.join(db_dir, ARCHIVE_V)

        cmd = [ "rcs", "-o%s" % rev, archive ]

        proc = subprocess.Popen(cmd, stderr = subprocess.PIPE)
        status = proc.wait()
        message = "\n".join(proc.stderr.readlines())
        proc.stderr.close()
        del proc

        if status != 0:
            from QuestionDialog import ErrorDialog
            
            ErrorDialog(
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
        self.dblist.set_cursor(path, focus_column=self.column, 
                               start_editing=True)

    def __repair_db(self, obj):
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
                fname = os.path.join(dirname,filename)
                os.unlink(fname)

        dbclass = GrampsDb.gramps_db_factory(db_type = "x-directory/normal")
        db = dbclass(Config.get(Config.TRANSACTIONS))
        db.set_save_path(dirname)
        db.load(dirname, None)

        self.__start_cursor(_("Rebuilding database from backup files"))
        GrampsDbUtils.Backup.restore(db)
        self.__end_cursor()

        db.close()
        self.dbstate.no_database()
        self.__populate()

    def __start_cursor(self, msg):
        """
        Sets the cursor to the busy state, and displays the associated
        message
        """
        self.msg.set_label(msg)
        self.top.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        while (gtk.events_pending()):
            gtk.main_iteration()

    def __end_cursor(self):
        """
        Sets the cursor back to normal and clears the message
        """
        self.top.window.set_cursor(None)
        self.msg.set_label("")

    def __new_db(self, obj):
        """
        Callback wrapper around the actual routine that creates the
        new database. Catch OSError and IOError and display a warning 
        message.
        """
        try:
            self.__create_new_db()
        except (OSError, IOError), msg:
            QuestionDialog.ErrorDialog(_("Could not create family tree"),
                                       str(msg))

    def __create_new_db(self, title=None):
        """
        Create a new database.
        """

        new_path = find_next_db_dir()

        os.mkdir(new_path)
        path_name = os.path.join(new_path, NAME_FILE)

        if title == None:
            name_list = [ name[0] for name in self.current_names ]
            title = find_next_db_name(name_list)

        name_file = open(path_name, "w")
        name_file.write(title)
        name_file.close()

        self.current_names.append(title)
        node = self.model.append(None, [title, new_path, path_name, 
                                        _("Never"), 0, False, ''])
        self.selection.select_iter(node)

        path = self.model.get_path(node)
        self.dblist.set_cursor(path, focus_column=self.column, 
                               start_editing=True)
        return new_path

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
        dbdir = os.path.expanduser(Config.get(Config.DATABASE_PATH))
        new_path = os.path.join(dbdir, base)
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

def icon_values(dirpath, active, open):
    """
    If the directory path is the active path, then return values
    that indicate to use the icon, and which icon to use.
    """
    if os.path.isfile(os.path.join(dirpath,"need_recover")):
        return (True, gtk.STOCK_DIALOG_ERROR)
    elif dirpath == active and open:
        return (True, gtk.STOCK_OPEN)
    elif os.path.isfile(os.path.join(dirpath,"lock")):
        return (True, 'gramps-lock')
    else:
        return (False, "")

def find_revisions(name):
    """
    Finds all the revisions of the specfied RCS archive.
    """
    import re

    rev  = re.compile("\s*revision\s+([\d\.]+)")
    date = re.compile("date:\s+(\d\d\d\d/\d\d/\d\d \d\d:\d\d:\d\d);")

    if not os.path.isfile(name):
        return []

    rlog = [ "rlog" , name ]

    proc = subprocess.Popen(rlog, stdout = subprocess.PIPE)
    proc.wait()

    revlist = []
    date_str = ""
    rev_str = ""
    com_str = ""
    
    get_next = False
    if os.path.isfile(name):
        for line in proc.stdout:
            match = rev.match(line)
            if match:
                rev_str = match.groups()[0]
                continue
            match = date.match(line)
            if match:
                date_str = time.asctime(time.strptime(match.groups()[0],
                                                      '%Y/%m/%d %H:%M:%S'))
                
                get_next = True
                continue
            if get_next:
                get_next = False
                com_str = line.strip()
                revlist.append((rev_str, date_str, com_str))
    return revlist

def check_out(db, rev, path, name, callback):
    co   = [ "co", "-q%s" % rev] + [ os.path.join(path, ARCHIVE),
                                     os.path.join(path, ARCHIVE_V)]

    proc = subprocess.Popen(co, stderr = subprocess.PIPE)
    status = proc.wait()
    message = "\n".join(proc.stderr.readlines())
    proc.stderr.close()
    del proc

    if status != 0:
        from QuestionDialog import ErrorDialog

        ErrorDialog(
            _("Retrieve failed"),
            _("An attempt to retrieve the data failed "
              "with the following message:\n\n%s") % message
            )
        return 

    rdr = GrampsDbUtils.gramps_db_reader_factory(const.app_gramps_xml)
    xml_file = os.path.join(path, ARCHIVE)
    rdr(db, xml_file, callback)
    os.unlink(xml_file)

def check_in(db, filename, callback, cursor_func = None):
    init = [ "rcs", '-i', '-U', '-q', '-t-"GRAMPS database"', ]
    ci   = [ "ci", "-q", "-f" ]

    glade = gtk.glade.XML(const.gladeFile, "comment", "gramps")
    top = glade.get_widget('comment')
    text = glade.get_widget('description')

    top.run()
    comment = text.get_text()
    top.destroy()

    if not os.path.isfile(filename + ",v") :
        proc = subprocess.Popen(init + [filename + ",v"],
                                stderr = subprocess.PIPE)
        status = proc.wait()
        message = "\n".join(proc.stderr.readlines())
        proc.stderr.close()
        del proc

    if cursor_func:
        cursor_func(_("Creating data to be archived..."))
    xmlwrite = GrampsDbUtils.XmlWriter(db, callback, False, 0)
    xmlwrite.write(filename)
            
    cmd = ci + ['-m%s' % comment, filename, filename + ",v" ]

    if cursor_func:
        cursor_func(_("Saving archive..."))
    proc = subprocess.Popen(
        cmd,
        stdin = subprocess.PIPE,
        stderr = subprocess.PIPE )
    proc.stdin.close()
    message = "\n".join(proc.stderr.readlines())
    proc.stderr.close()
    status = proc.wait()
    del proc

    if status != 0:
        from QuestionDialog import ErrorDialog

        ErrorDialog(
            _("Archiving failed"),
            _("An attempt to archive the data failed "
              "with the following message:\n\n%s") % message
            )

