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
Provide the management of databases from CLI. This includes opening, renaming,
creating, and deleting of databases.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import re
import os
import sys
import ast
import time
from urllib.parse import urlparse
from urllib.request import urlopen, url2pathname
import tempfile
import logging

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.plug import BasePluginManager
from gramps.gen.config import config
from gramps.gen.constfunc import win
from gramps.gen.db.dbconst import DBLOGNAME, DBBACKEND
from gramps.gen.db.utils import make_database, get_dbid_from_path
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
LOG = logging.getLogger(".clidbman")
_LOG = logging.getLogger(DBLOGNAME)

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
DEFAULT_TITLE = _("Family Tree")
NAME_FILE = "name.txt"
META_NAME = "meta_data.db"
UNAVAILABLE = _('Unavailable')

#-------------------------------------------------------------------------
#
# functions
#
#-------------------------------------------------------------------------
def _errordialog(title, errormessage):
    """
    Show the error. A title for the error and an errormessage
    """
    print(_('ERROR: %(title)s \n       %(message)s') % {
        'title': title,
        'message': errormessage})
    sys.exit()

#-------------------------------------------------------------------------
#
# CLIDbManager
#
#-------------------------------------------------------------------------
class CLIDbManager:
    """
    Database manager without GTK functionality, allows users to create and
    open databases
    """
    IND_NAME = 0
    IND_PATH = 1
    IND_PATH_NAMEFILE = 2
    IND_TVAL_STR = 3
    IND_TVAL = 4
    IND_USE_ICON_BOOL = 5
    IND_STOCK_ID = 6

    ICON_NONE = 0
    ICON_RECOVERY = 1
    ICON_LOCK = 2
    ICON_OPEN = 3

    ICON_MAP = {
        ICON_NONE : None,
        ICON_RECOVERY : None,
        ICON_LOCK : None,
        ICON_OPEN : None,
        }

    ERROR = _errordialog
    def __init__(self, dbstate):
        self.dbstate = dbstate
        self.msg = None

        if dbstate and dbstate.is_open():
            self.active = dbstate.db.get_save_path()
        else:
            self.active = None

        self.current_names = []
        if dbstate:
            self._populate_cli()

    def empty(self, val):
        """
        Callback that does nothing
        """
        pass

    def get_dbdir_summary(self, dirpath, name):
        """
        dirpath: full path to database
        name: proper name of family tree

        Returns dictionary of summary item.
        Should include at least, if possible:

        _("Path")
        _("Family Tree")
        _("Last accessed")
        _("Database")
        _("Locked?")

        and these details:

        _("Number of people")
        _("Version")
        _("Schema version")
        """
        dbid = get_dbid_from_path(dirpath)
        if not self.is_locked(dirpath):
            try:
                database = make_database(dbid)
                database.load(dirpath, None, update=False)
                retval = database.get_summary()
                database.close(update=False)
            except Exception as msg:
                retval = {_("Unavailable"): str(msg)[:74] + "..."}
        else:
            retval = {_("Unavailable"): "locked"}
        retval.update({_("Family Tree"): name,
                       _("Path"): dirpath,
                       _("Database"): self.get_backend_name_from_dbid(dbid),
                       _("Last accessed"): time_val(dirpath)[1],
                       _("Locked?"): self.is_locked(dirpath),
                      })
        return retval

    def get_backend_name_from_dbid(self, dbid):
        pmgr = BasePluginManager.get_instance()
        for plugin in pmgr.get_reg_databases():
            if plugin.id == dbid:
                return plugin._name
        return UNAVAILABLE

    def print_family_tree_summaries(self, database_names=None):
        """
        Prints a detailed list of the known family trees.
        """
        print(_('Gramps Family Trees:'))
        for item in self.current_names:
            (name, dirpath, path_name, last,
             tval, enable, stock_id, backend_type) = item
            if (database_names is None or
                    any([(re.match("^" + dbname + "$", name) or
                          dbname == name)
                         for dbname in database_names])):
                summary = self.get_dbdir_summary(dirpath, name)
                print(_('Family Tree "%s":') % summary[_("Family Tree")])
                for item in sorted(summary):
                    if item != "Family Tree":
                        # translators: needed for French, ignore otherwise
                        print('   ' + _("%(str1)s: %(str2)s"
                                       ) % {'str1' : item,
                                            'str2' : summary[item]})

    def family_tree_summary(self, database_names=None):
        """
        Return a list of dictionaries of the known family trees.
        """
        # make the default directory if it does not exist
        summary_list = []
        for item in self.current_names:
            (name, dirpath, path_name, last,
             tval, enable, stock_id, backend_type) = item
            if (database_names is None or
                    any([(re.match("^" + dbname + "$", name) or
                          dbname == name)
                         for dbname in database_names])):
                retval = self.get_dbdir_summary(dirpath, name)
                summary_list.append(retval)
        return summary_list

    def _populate_cli(self):
        """
        Get the list of current names in the database dir
        """
        # make the default directory if it does not exist
        dbdir = os.path.expanduser(config.get('database.path'))
        db_ok = make_dbdir(dbdir)

        self.current_names = []
        if db_ok:
            for dpath in os.listdir(dbdir):
                dirpath = os.path.join(dbdir, dpath)
                path_name = os.path.join(dirpath, NAME_FILE)
                backend_type = get_dbid_from_path(dirpath)
                if os.path.isfile(path_name):
                    with open(path_name, 'r', encoding='utf8') as file:
                        name = file.readline().strip()

                    (tval, last) = time_val(dirpath)
                    (enable, stock_id) = self.icon_values(
                        dirpath, self.active, self.dbstate.is_open())

                    if stock_id == 'gramps-lock':
                        last = find_locker_name(dirpath)

                    self.current_names.append(
                        (name, os.path.join(dbdir, dpath), path_name,
                         last, tval, enable, stock_id, backend_type))

        self.current_names.sort()

    def get_family_tree_path(self, name):
        """
        Given a name, return None if name not existing or the path to the
        database if it is a known database name.
        """
        for data in self.current_names:
            if data[0] == name:
                return data[1]
        return None

    def family_tree_list(self):
        """
        Return a list of name, dirname of the known family trees
        """
        lst = [(x[0], x[1]) for x in self.current_names]
        return lst

    def __start_cursor(self, msg):
        """
        Do needed things to start import visually, eg busy cursor
        """
        print(_('Starting Import, %s') % msg)

    def __end_cursor(self):
        """
        Set end of a busy cursor
        """
        print(_('Import finished...'))

    def create_new_db_cli(self, title=None, create_db=True, dbid=None):
        """
        Create a new database.
        """
        new_path = find_next_db_dir()

        os.mkdir(new_path)
        path_name = os.path.join(new_path, NAME_FILE)

        if title is None:
            name_list = [name[0] for name in self.current_names]
            title = find_next_db_name(name_list)

        with open(path_name, "w", encoding='utf8') as name_file:
            name_file.write(title)

        if create_db:
            if dbid is None:
                dbid = config.get('database.backend')
            newdb = make_database(dbid)

        backend_path = os.path.join(new_path, DBBACKEND)
        with open(backend_path, "w", encoding='utf8') as backend_file:
            backend_file.write(dbid)

        (tval, last) = time_val(new_path)

        self.current_names.append((title, new_path, path_name,
                                   last, tval, False, "", dbid))
        return new_path, title

    def _create_new_db(self, title=None, dbid=None, edit_entry=False):
        """
        Create a new database, do extra stuff needed
        """
        return self.create_new_db_cli(title, dbid=dbid)

    def import_new_db(self, filename, user):
        """
        Attempt to import the provided file into a new database.
        A new database will only be created if an appropriate importer was
        found.

        :param filename: a fully-qualified path, filename, and
                         extension to open.

        :param user: a :class:`.cli.user.User` or :class:`.gui.user.User`
                     instance for managing user interaction.

        :returns: A tuple of (new_path, name) for the new database
                  or (None, None) if no import was performed.
        """
        pmgr = BasePluginManager.get_instance()
        # check to see if it isn't a filename directly:
        if not os.path.isfile(filename):
            # Allow URL names here; make temp file if necessary
            url = urlparse(filename)
            if url.scheme != "":
                if url.scheme == "file":
                    filename = url2pathname(filename[7:])
                else:
                    url_fp = urlopen(filename) # open URL
                    # make a temp local file:
                    ext = os.path.splitext(url.path)[1]
                    fd, filename = tempfile.mkstemp(suffix=ext)
                    temp_fp = os.fdopen(fd, "w")
                    # read from URL:
                    data = url_fp.read()
                    # write locally:
                    temp_fp.write(data)
                    url_fp.close()
                    temp_fp.close()

        (name, ext) = os.path.splitext(os.path.basename(filename))
        format = ext[1:].lower()

        for plugin in pmgr.get_import_plugins():
            if format == plugin.get_extension():

                dbid = config.get('database.backend')
                new_path, name = self._create_new_db(name, dbid=dbid,
                                                     edit_entry=False)

                # Create a new database
                self.__start_cursor(_("Importing data..."))

                dbase = make_database(dbid)
                dbase.load(new_path, user.callback)

                import_function = plugin.get_import_function()
                import_function(dbase, filename, user)

                # finish up
                self.__end_cursor()
                dbase.close()

                return new_path, name
        return None, None

    def is_locked(self, dbpath):
        """
        Returns True if there is a lock file in the dirpath
        """
        if os.path.isfile(os.path.join(dbpath, "lock")):
            return True
        return False

    def needs_recovery(self, dbpath):
        """
        Returns True if the database in dirpath needs recovery
        """
        if os.path.isfile(os.path.join(dbpath, "need_recover")):
            return True
        return False

    def backend_unavailable(self, dbpath):
        """
        Returns True if the database in dirpath has an unavailable backend
        """
        dbid = get_dbid_from_path(dbpath)
        return self.get_backend_name_from_dbid(dbid) == UNAVAILABLE

    def remove_database(self, dbname, user=None):
        """
        Deletes a database folder given a pattenr that matches
        its proper name.
        """
        dbdir = os.path.expanduser(config.get('database.path'))
        match_list = []
        for dpath in os.listdir(dbdir):
            dirpath = os.path.join(dbdir, dpath)
            path_name = os.path.join(dirpath, NAME_FILE)
            if os.path.isfile(path_name):
                with open(path_name, 'r', encoding='utf8') as file:
                    name = file.readline().strip()
                if re.match("^" + dbname + "$", name) or dbname == name:
                    match_list.append((name, dirpath))
        if len(match_list) == 0:
            CLIDbManager.ERROR("Family tree not found",
                               "No matching family tree found: '%s'" % dbname)
        # now delete them:
        for (name, directory) in match_list:
            if user is None or user.prompt(
                    _('Remove family tree warning'),
                    _('Are you sure you want to remove '
                      'the family tree named\n"%s"?'
                     ) % name,
                    _('yes'), _('no'), default_label=_('no')):
                try:
                    for (top, dirs, files) in os.walk(directory):
                        for filename in files:
                            os.unlink(os.path.join(top, filename))
                    os.rmdir(directory)
                except (IOError, OSError) as msg:
                    CLIDbManager.ERROR(_("Could not delete Family Tree"),
                                       str(msg))

    def rename_database(self, filepath, new_text):
        """
        Renames the database by writing the new value to the name.txt file
        Returns old_name, new_name if success, None, None if no success
        """
        try:
            with open(filepath, "r", encoding='utf8') as name_file:
                old_text = name_file.read()
            with open(filepath, "w", encoding='utf8') as name_file:
                name_file.write(new_text)
        except (OSError, IOError) as msg:
            CLIDbManager.ERROR(_("Could not rename Family Tree"), str(msg))
            return None, None
        return old_text, new_text

    def break_lock(self, dbpath):
        """
        Breaks the lock on a database
        """
        if os.path.exists(os.path.join(dbpath, "lock")):
            os.unlink(os.path.join(dbpath, "lock"))

    def icon_values(self, dirpath, active, is_open):
        """
        If the directory path is the active path, then return values
        that indicate to use the icon, and which icon to use.
        """
        if os.path.isfile(os.path.join(dirpath, "need_recover")):
            return (True, self.ICON_MAP[self.ICON_RECOVERY])
        elif dirpath == active and is_open:
            return (True, self.ICON_MAP[self.ICON_OPEN])
        elif os.path.isfile(os.path.join(dirpath, "lock")):
            return (True, self.ICON_MAP[self.ICON_LOCK])
        else:
            return (False, self.ICON_MAP[self.ICON_NONE])

def make_dbdir(dbdir):
    """
    Create the default database directory, as defined by dbdir
    """
    try:
        if not os.path.isdir(dbdir):
            os.makedirs(dbdir)
    except (IOError, OSError) as msg:
        LOG.error(_("\nERROR: Wrong database path in Edit Menu->Preferences.\n"
                    "Open preferences and set correct database path.\n\n"
                    "Details: Could not make database directory:\n    %s\n\n"),
                  str(msg))
        return False
    return True

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
        dbdir = os.path.expanduser(config.get('database.path'))
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
        # This gives creation date in Windows, but correct date in Linux
        if win():
            # Try to use last modified date instead in Windows
            # and check that it is later than the creation date.
            tval_mod = os.stat(meta)[8]
            if tval_mod > tval:
                tval = tval_mod
        last = time.strftime('%x %X', time.localtime(tval))
    else:
        tval = 0
        last = _("Never")
    return (tval, last)

def find_locker_name(dirpath):
    """
    Opens the lock file if it exists, reads the contexts which is "USERNAME"
    and returns the contents, with correct string before "USERNAME",
    so the message can be printed with correct locale.
    If a file is encountered with errors, we return 'Unknown'
    This data can eg be displayed in the time column of the manager
    """
    try:
        fname = os.path.join(dirpath, "lock")
        with open(fname, 'r', encoding='utf8') as ifile:
            username = ifile.read().strip()
            # feature request 2356: avoid genitive form
            last = _("Locked by %s") % username
    except (OSError, IOError, UnicodeDecodeError):
        last = _("Unknown")
    return last
