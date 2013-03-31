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
import sys
import time
import urllib2
import urlparse
import tempfile
from gen.ggettext import gettext as _
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
from gen.plug import BasePluginManager
import config
import constfunc
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
# functions
#
#-------------------------------------------------------------------------
def _errordialog(title, errormessage):
    """
    Show the error. A title for the error and an errormessage
    """
    print _('ERROR: %s \n       %s') % (title, errormessage)
    sys.exit()

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
    IND_NAME = 0
    IND_PATH = 1
    IND_PATH_NAMEFILE = 2
    IND_TVAL_STR = 3
    IND_TVAL = 4
    IND_USE_ICON_BOOL = 5
    IND_STOCK_ID =6
    
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
    
    ERROR = _errordialog
    def __init__(self, dbstate):
        self.dbstate = dbstate
        self.msg = None
        
        if dbstate:
            self.active  = dbstate.db.get_save_path()
        else:
            self.active = None
        
        self.current_names = []
        if dbstate:
            self._populate_cli()

    def empty(self, val):
        """Callback that does nothing
        """
        pass

    def get_dbdir_summary(self, dirpath, name):
        """
        Returns (people_count, bsddb_version, schema_version) of
        current DB.
        Returns ("Unknown", "Unknown", "Unknown") if invalid DB or other error.
        """
        if config.get('preferences.use-bsddb3'):
            from bsddb3 import dbshelve, db
        else:
            from bsddb import dbshelve, db

        from gen.db import META, PERSON_TBL
        from  gen.db.dbconst import BDBVERSFN

        bdbversion_file = os.path.join(dirpath, BDBVERSFN)
        if os.path.isfile(bdbversion_file):
            vers_file = open(bdbversion_file)
            bsddb_version = vers_file.readline().strip()
        else:
            return "Unknown", "Unknown", "Unknown"
        
        current_bsddb_version = str(db.version())
        if bsddb_version != current_bsddb_version:
            return "Unknown", bsddb_version, "Unknown"
        
        env = db.DBEnv()
        flags = db.DB_CREATE | db.DB_PRIVATE |\
            db.DB_INIT_MPOOL |\
            db.DB_INIT_LOG | db.DB_INIT_TXN
        try:
            env.open(dirpath, flags)
        except Exception as msg:
            LOG.warning("Error opening db environment for '%s': %s" %
                        (name, str(msg)))
            try:
                env.close()
            except Exception as msg:
                LOG.warning("Error closing db environment for '%s': %s" %
                        (name, str(msg)))
            return "Unknown", bsddb_version, "Unknown"
        dbmap1 = dbshelve.DBShelf(env)
        fname = os.path.join(dirpath, META + ".db")
        try:
            dbmap1.open(fname, META, db.DB_HASH, db.DB_RDONLY)
        except:
            env.close()
            return "Unknown", bsddb_version, "Unknown"
        schema_version = dbmap1.get('version', default=None)
        dbmap1.close()
        dbmap2 = dbshelve.DBShelf(env)
        fname = os.path.join(dirpath, PERSON_TBL + ".db")
        try:
            dbmap2.open(fname, PERSON_TBL, db.DB_HASH, db.DB_RDONLY)
        except:
            env.close()
            return "Unknown", bsddb_version, schema_version
        count = len(dbmap2)
        dbmap2.close()
        env.close()
        return (count, bsddb_version, schema_version)

    def family_tree_summary(self):
        """
        Return a list of dictionaries of the known family trees.
        """
        # make the default directory if it does not exist
        summary_list = []
        for item in self.current_names:
            (name, dirpath, path_name, last, 
             tval, enable, stock_id) = item
            count, bsddb_version, schema_version = self.get_dbdir_summary(dirpath, name)
            retval = {}
            retval[_("Number of people")] = count
            if enable:
                retval[_("Locked?")] = _("yes")
            else:
                retval[_("Locked?")] = _("no")
            retval[_("Bsddb version")] = bsddb_version
            retval[_("Schema version")] = schema_version
            retval[_("Family tree")] = name.encode(sys.getfilesystemencoding())
            retval[_("Path")] = dirpath
            retval[_("Last accessed")] = time.strftime('%x %X', 
                                                    time.localtime(tval))
            summary_list.append( retval )
        return summary_list

    def _populate_cli(self):
        """ Get the list of current names in the database dir
        """
        # make the default directory if it does not exist
        dbdir = os.path.expanduser(config.get('behavior.database-path'))
        dbdir = dbdir.encode(sys.getfilesystemencoding())
        db_ok = make_dbdir(dbdir)

        self.current_names = []
        if db_ok:
            for dpath in os.listdir(dbdir):
                dirpath = os.path.join(dbdir, dpath)
                path_name = os.path.join(dirpath, NAME_FILE)
                if os.path.isfile(path_name):
                    f = open(path_name)
                    name = f.readline().strip()
                    f.close()

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
        newdb = gen.db.DbBsddb()
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
        pmgr = BasePluginManager.get_instance()
        # Allow URL names here; make temp file if necessary
        url = urlparse.urlparse(filename)
        if url.scheme != "":
            if url.scheme == "file":
                filename = urllib2.url2pathname(filename[7:])
            else:
                url_fp = urllib2.urlopen(filename) # open URL
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

                new_path, name = self._create_new_db(name)
    
                # Create a new database
                self.__start_cursor(_("Importing data..."))
                dbclass = gen.db.DbBsddb
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

    def rename_database(self, filepath, new_text):
        """
        Renames the database by writing the new value to the name.txt file
        Returns old_name, new_name if success, None, None if no success
        """
        try:
            name_file = open(filepath, "r")
            old_text=name_file.read()
            name_file.close()
            name_file = open(filepath, "w")
            name_file.write(new_text)
            name_file.close()
        except (OSError, IOError), msg:
            CLIDbManager.ERROR(_("Could not rename family tree"),
                  str(msg))
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
        msg = unicode(str(msg), sys.getfilesystemencoding())
        LOG.error(_("\nERROR: Wrong database path in Edit Menu->Preferences.\n"
                    "Open preferences and set correct database path.\n\n"
                    "Details: Could not make database directory:\n    %s\n\n") % msg)
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
        dbdir = os.path.expanduser(config.get('behavior.database-path'))
        dbdir = dbdir.encode(sys.getfilesystemencoding())
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
        if constfunc.win():
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
        ifile = open(fname)
        username = ifile.read().strip()
        # Convert username to unicode according to system encoding
        # Otherwise problems with non ASCII characters in
        # username in Windows
        username = unicode(username, sys.getfilesystemencoding())
        # feature request 2356: avoid genitive form
        last = _("Locked by %s") % username
        ifile.close()
    except (OSError, IOError):
        last = _("Unknown")
    return last
