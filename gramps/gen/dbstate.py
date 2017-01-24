#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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
Provide the database state class
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import sys
import os
import logging
import inspect

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from .db import DbReadBase
from .proxy.proxybase import ProxyDbBase
from .utils.callback import Callback
from .config import config
from gramps.gen.db.dbconst import DBLOGNAME

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
LOG = logging.getLogger(".dbstate")
_LOG = logging.getLogger(DBLOGNAME)

class DbState(Callback):
    """
    Provide a class to encapsulate the state of the database.
    """

    __signals__ = {
        'database-changed' : ((DbReadBase, ProxyDbBase), ),
        'no-database' :  None,
        }

    def __init__(self):
        """
        Initalize the state with an empty (and useless) DummyDb. This is just a
        place holder until a real DB is assigned.
        """
        Callback.__init__(self)
        self.db = self.make_database("dummydb")
        self.open = False  #  Deprecated - use DbState.is_open()
        self.stack = []

    def is_open(self):
        """
        Returns True if DbState.db refers to a database object instance, AND the
        database is open.

        This tests both for the existence of the database and its being open, so
        that for the time being, the use of the dummy database on closure can
        continue, but at some future time, this could be altered to just set the
        database to none.

        This replaces tests on DbState.open, DbState.db, DbState.db.is_open()
        and DbState.db.db_is_open all of which are deprecated.
        """
        class_name = self.__class__.__name__
        func_name = "is_open"
        caller_frame = inspect.stack()[1]
        _LOG.debug('calling %s.%s()... from file %s, line %s in %s',
                  class_name, func_name, os.path.split(caller_frame[1])[1],
                  caller_frame[2], caller_frame[3])
        return (self.db is not None) and self.db.is_open()

    def change_database(self, database):
        """
        Closes the existing db, and opens a new one.
        Retained for backward compatibility.
        """
        if database:
            self.emit('no-database', ())
            if self.is_open():
                self.db.close()
            self.change_database_noclose(database)

    def change_database_noclose(self, database):
        """
        Change the current database. and resets the configuration prefixes.
        """
        self.db = database
        self.db.set_prefixes(
            config.get('preferences.iprefix'),
            config.get('preferences.oprefix'),
            config.get('preferences.fprefix'),
            config.get('preferences.sprefix'),
            config.get('preferences.cprefix'),
            config.get('preferences.pprefix'),
            config.get('preferences.eprefix'),
            config.get('preferences.rprefix'),
            config.get('preferences.nprefix'))
        self.open = True

    def signal_change(self):
        """
        Emits the database-changed signal with the new database
        """
        self.emit('database-changed', (self.db, ))

    def no_database(self):
        """
        Closes the database without a new database (except for the DummyDb)
        """
        self.emit('no-database', ())
        if self.is_open():
            self.db.close()
        self.db = self.make_database("dummydb")
        self.open = False
        self.emit('database-changed', (self.db, ))

    def get_database(self):
        """
        Get a reference to the current database.
        """
        return self.db

    def apply_proxy(self, proxy, *args, **kwargs):
        """
        Add a proxy to the current database. Use pop_proxy() to
        revert to previous db.

        >>> dbstate.apply_proxy(gramps.gen.proxy.LivingProxyDb, 0)
        >>> dbstate.apply_proxy(gramps.gen.proxy.PrivateProxyDb)

        >>> from gramps.gen.filters.rules.person import (IsDescendantOf,
                                                         IsAncestorOf)
        >>> from gramps.gen.filters import GenericFilter
        >>> filter = GenericFilter()
        >>> filter.set_logical_op("or")
        >>> filter.add_rule(IsDescendantOf([db.get_default_person().gramps_id,
                                            True]))
        >>> filter.add_rule(IsAncestorOf([db.get_default_person().gramps_id,
                                          True]))
        >>> dbstate.apply_proxy(gramps.gen.proxy.FilterProxyDb, filter)
        """
        self.stack.append(self.db)
        self.db = proxy(self.db, *args, **kwargs)
        self.emit('database-changed', (self.db, ))

    def pop_proxy(self):
        """
        Remove the previously applied proxy.

        >>> dbstate.apply_proxy(gen.proxy.LivingProxyDb, 1)
        >>> dbstate.pop_proxy()
        >>> dbstate.apply_proxy(gen.proxy.PrivateProxyDb)
        >>> dbstate.pop_proxy()
        """
        self.db = self.stack.pop()
        self.emit('database-changed', (self.db, ))

    def make_database(self, plugin_id):
        """
        Make a database, given a plugin id.
        """
        from .plug import BasePluginManager
        from .const import PLUGINS_DIR, USER_PLUGINS

        pmgr = BasePluginManager.get_instance()
        pdata = pmgr.get_plugin(plugin_id)

        if not pdata:
            # This might happen if using gramps from outside, and
            # we haven't loaded plugins yet
            pmgr.reg_plugins(PLUGINS_DIR, self, None)
            pmgr.reg_plugins(USER_PLUGINS, self, None, load_on_reg=True)
            pdata = pmgr.get_plugin(plugin_id)

        if pdata:
            if pdata.reset_system:
                if self.modules_is_set():
                    self.reset_modules()
                else:
                    self.save_modules()
            mod = pmgr.load_plugin(pdata)
            if mod:
                database = getattr(mod, pdata.databaseclass)
                db = database()
                import inspect
                caller_frame = inspect.stack()[1]
                _LOG.debug("Database class instance created Class:%s instance:%s. "
                           "Called from File %s, line %s, in %s"
                           % ((db.__class__.__name__, hex(id(db)))
                             + (os.path.split(caller_frame[1])[1],)
                             + tuple(caller_frame[i] for i in range(2, 4))))
                return db
            else:
                raise Exception("can't load database backend: '%s'" % plugin_id)
        else:
            raise Exception("no such database backend: '%s'" % plugin_id)

    def open_database(self, dbname, force_unlock=False, callback=None):
        """
        Open a database by name and return the database.
        """
        data = self.lookup_family_tree(dbname)
        database = None
        if data:
            dbpath, locked, locked_by, backend = data
            if (not locked) or (locked and force_unlock):
                database = self.make_database(backend)
                database.load(dbpath, callback=callback)
        return database

    def lookup_family_tree(self, dbname):
        """
        Find a Family Tree given its name, and return properties.
        """
        dbdir = os.path.expanduser(config.get('database.path'))
        for dpath in os.listdir(dbdir):
            dirpath = os.path.join(dbdir, dpath)
            path_name = os.path.join(dirpath, "name.txt")
            if os.path.isfile(path_name):
                with open(path_name, 'r', encoding='utf8') as file:
                    name = file.readline().strip()
                if dbname == name:
                    locked = False
                    locked_by = None
                    backend = None
                    fname = os.path.join(dirpath, "database.txt")
                    if os.path.isfile(fname):
                        with open(fname, 'r', encoding='utf8') as ifile:
                            backend = ifile.read().strip()
                    else:
                        backend = "bsddb"
                    try:
                        fname = os.path.join(dirpath, "lock")
                        with open(fname, 'r', encoding='utf8') as ifile:
                            locked_by = ifile.read().strip()
                            locked = True
                    except (OSError, IOError):
                        pass
                    return (dirpath, locked, locked_by, backend)
        return None

    def import_from_filename(self, db, filename, user=None):
        """
        Import the filename into the db.
        """
        from .plug import BasePluginManager
        from .const import PLUGINS_DIR, USER_PLUGINS
        from gramps.cli.user import User
        pmgr = BasePluginManager.get_instance()
        if user is None:
            user = User()
        (name, ext) = os.path.splitext(os.path.basename(filename))
        extension = ext[1:].lower()
        import_list = pmgr.get_reg_importers()
        if import_list == []:
            # This might happen if using gramps from outside, and
            # we haven't loaded plugins yet
            pmgr.reg_plugins(PLUGINS_DIR, self, None)
            pmgr.reg_plugins(USER_PLUGINS, self, None, load_on_reg=True)
            import_list = pmgr.get_reg_importers()
        for pdata in import_list:
            if extension == pdata.extension:
                mod = pmgr.load_plugin(pdata)
                if not mod:
                    for item in pmgr.get_fail_list():
                        name, error_tuple, pdata = item
                        etype, exception, traceback = error_tuple
                        print("ERROR:", name, exception)
                    return False
                import_function = getattr(mod, pdata.import_function)
                results = import_function(db, filename, user)
                return True
        return False

    ## Work-around for databases that need sys refresh (django):
    def modules_is_set(self):
        LOG.info("modules_is_set?")
        if hasattr(self, "_modules"):
            return self._modules != None
        else:
            self._modules = None
            return False

    def reset_modules(self):
        LOG.info("reset_modules!")
        # First, clear out old modules:
        for key in list(sys.modules.keys()):
            del sys.modules[key]
        # Next, restore previous:
        for key in self._modules:
            sys.modules[key] = self._modules[key]

    def save_modules(self):
        LOG.info("save_modules!")
        self._modules = sys.modules.copy()

