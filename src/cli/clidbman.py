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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Provide the management of databases from CLI. This includes opening, renaming,
creating, and deleting of databases.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import time
from gettext import gettext as _
#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".clidbman")

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import gen.db
from gen.plug import PluginManager
import config

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------

DEFAULT_TITLE = _("Family Tree")
NAME_FILE     = "name.txt"
META_NAME     = "meta_data.db"

#-------------------------------------------------------------------------
#
# CLIDbManager
#
#-------------------------------------------------------------------------
class CLIDbManager(object):
    """
    Database manager without GTK functionality, allows users to create and
    open databases
    """
    ICON_NONE     = 0
    ICON_RECOVERY = 1
    ICON_LOCK     = 2
    ICON_OPEN     = 3
    
    ICON_MAP = {
                ICON_NONE : None,
                ICON_RECOVERY : None,
                ICON_LOCK : None,
                ICON_OPEN : None,
               }
    
    def __init__(self, dbstate):
        self.dbstate = dbstate
        self.msg = None
        
        if dbstate:
            self.active  = dbstate.db.get_save_path()
        else:
            self.active = None
        
        self.current_names = []
        self._populate_cli()

    def empty(self, val):
        """Callback that does nothing
        """
        pass

    def get_dbdir_summary(self, file_name):
        """
        Returns (people_count, version_number) of current DB.
        Returns ("Unknown", "Unknown") if invalid DB or other error.
        """
        from bsddb import dbshelve, db
        from gen.db import META, PERSON_TBL
        env = db.DBEnv()
        flags = db.DB_CREATE | db.DB_PRIVATE |\
            db.DB_INIT_MPOOL | db.DB_INIT_LOCK |\
            db.DB_INIT_LOG | db.DB_INIT_TXN | db.DB_THREAD
        try:
            env.open(file_name, flags)
        except:
            return "Unknown", "Unknown"
        dbmap1 = dbshelve.DBShelf(env)
        fname = os.path.join(file_name, META + ".db")
        try:
            dbmap1.open(fname, META, db.DB_HASH, db.DB_RDONLY)
        except:
            return "Unknown", "Unknown"
        version = dbmap1.get('version', default=None)
        dbmap1.close()
        dbmap2 = dbshelve.DBShelf(env)
        fname = os.path.join(file_name, PERSON_TBL + ".db")
        try:
            dbmap2.open(fname, PERSON_TBL, db.DB_HASH, db.DB_RDONLY)
        except:
            env.close()
            return "Unknown", "Unknown"
        count = len(dbmap2)
        dbmap2.close()
        env.close()
        return (count, version)

    def family_tree_summary(self):
        """
        Return a list of dictionaries of the known family trees.
        """
        # make the default directory if it does not exist
        list = []
        for item in self.current_names:
            (name, dirpath, path_name, last, 
             tval, enable, stock_id) = item
            count, version = self.get_dbdir_summary(dirpath)
            retval = {}
            retval["Number of people"] = count
            if enable:
                retval["Locked?"] = "yes"
            else:
                retval["Locked?"] = "no"
            retval["DB version"] = version
            retval["Family tree"] = name
            retval["Path"] = dirpath
            retval["Last accessed"] = time.strftime('%x %X', 
                                                    time.localtime(tval))
            list.append( retval )
        return list

    def _populate_cli(self):
        """ Get the list of current names in the database dir
        """
        # make the default directory if it does not exist
        dbdir = os.path.expanduser(config.get('behavior.database-path'))
        make_dbdir(dbdir)

        self.current_names = []
        
        for dpath in os.listdir(dbdir):
            dirpath = os.path.join(dbdir, dpath)
            path_name = os.path.join(dirpath, NAME_FILE)
            if os.path.isfile(path_name):
                name = file(path_name).readline().strip()

                (tval, last) = time_val(dirpath)
                (enable, stock_id) = self.icon_values(dirpath, self.active, 
                                                 self.dbstate.db.is_open())

                if (stock_id == 'gramps-lock'):
                    last = find_locker_name(dirpath)

                self.current_names.append(
                    (name, os.path.join(dbdir, dpath), path_name,
                     last, tval, enable, stock_id))

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
        """Return a list of name, dirname of the known family trees
        """
        lst = [(x[0], x[1]) for x in self.current_names]
        return lst

    def __start_cursor(self, msg):
        """
        Do needed things to start import visually, eg busy cursor
        """
        print _('Starting Import, %s') % msg

    def __end_cursor(self):
        """
        Set end of a busy cursor
        """
        print _('Import finished...')

    def create_new_db_cli(self, title=None):
        """
        Create a new database.
        """
        new_path = find_next_db_dir()

        os.mkdir(new_path)
        path_name = os.path.join(new_path, NAME_FILE)

        if title is None:
            name_list = [ name[0] for name in self.current_names ]
            title = find_next_db_name(name_list)
        
        name_file = open(path_name, "w")
        name_file.write(title)
        name_file.close()

        # write the version number into metadata
        newdb = gen.db.GrampsDBDir()
        newdb.write_version(new_path)

        (tval, last) = time_val(new_path)
        
        self.current_names.append((title, new_path, path_name,
                                   last, tval, False, ""))
        return new_path, title

    def _create_new_db(self, title=None):
        """
        Create a new database, do extra stuff needed
        """
        return self.create_new_db_cli(title)

    def import_new_db(self, filename, callback):
        """
        Attempt to import the provided file into a new database.
        A new database will only be created if an appropriate importer was 
        found.
        
        @return: A tuple of (new_path, name) for the new database
                 or (None, None) if no import was performed.
        """
        pmgr = PluginManager.get_instance()
        (name, ext) = os.path.splitext(os.path.basename(filename))
        format = ext[1:].lower()

        for plugin in pmgr.get_import_plugins():
            if format == plugin.get_extension():

                new_path, name = self._create_new_db(name)
    
                # Create a new database
                self.__start_cursor(_("Importing data..."))
                dbclass = gen.db.GrampsDBDir
                dbase = dbclass()
                dbase.load(new_path, callback)
    
                import_function = plugin.get_import_function()
                import_function(dbase, filename, callback)
    
                # finish up
                self.__end_cursor()
                dbase.close()
                
                return new_path, name
        return None, None

    def is_locked(self, dbpath):
        """
        returns True if there is a lock file in the dirpath
        """
        if os.path.isfile(os.path.join(dbpath,"lock")):
            return True
        return False

    def needs_recovery(self, dbpath):
        """
        returns True if the database in dirpath needs recovery
        """
        if os.path.isfile(os.path.join(dbpath,"need_recover")):
            return True
        return False

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
        if os.path.isfile(os.path.join(dirpath,"need_recover")):
            return (True, self.ICON_MAP[self.ICON_RECOVERY])
        elif dirpath == active and is_open:
            return (True, self.ICON_MAP[self.ICON_OPEN])
        elif os.path.isfile(os.path.join(dirpath,"lock")):
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
    except (IOError, OSError), msg:
        LOG.error(_("Could not make database directory: ") + str(msg))

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
        dbdir = os.path.expanduser(config.get('behavior.database-path'))
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
        ifile = open(fname)
        username = ifile.read().strip()
        last = _("Locked by %s") % username
        ifile.close()
    except (OSError, IOError):
        last = _("Unknown")
    return last
