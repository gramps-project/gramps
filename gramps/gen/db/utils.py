#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
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
Database utilites
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import os
import logging

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from ..plug import BasePluginManager
from ..const import PLUGINS_DIR, USER_PLUGINS
from ..config import config
from .dbconst import DBLOGNAME

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
_LOG = logging.getLogger(DBLOGNAME)

def make_database(plugin_id):
    """
    Make a database, given a plugin id.
    """
    pmgr = BasePluginManager.get_instance()
    pdata = pmgr.get_plugin(plugin_id)

    if not pdata:
        # This might happen if using gramps from outside, and
        # we haven't loaded plugins yet
        pmgr.reg_plugins(PLUGINS_DIR, None, None)
        pmgr.reg_plugins(USER_PLUGINS, None, None, load_on_reg=True)
        pdata = pmgr.get_plugin(plugin_id)

    if pdata:
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

def open_database(dbname, force_unlock=False, callback=None):
    """
    Open a database by name and return the database.
    """
    data = lookup_family_tree(dbname)
    database = None
    if data:
        dbpath, locked, locked_by, backend = data
        if (not locked) or (locked and force_unlock):
            database = make_database(backend)
            database.load(dbpath, callback=callback)
    return database

def lookup_family_tree(dbname):
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

def import_as_dict(filename, user, skp_imp_adds=True):
    """
    Import the filename into a InMemoryDB and return it.
    """
    db = make_database("inmemorydb")
    db.load(None)
    db.set_feature("skip-import-additions", skp_imp_adds)
    status = import_from_filename(db, filename, user)
    return db if status else None

def import_from_filename(db, filename, user):
    """
    Import a file into a database.
    """
    (name, ext) = os.path.splitext(os.path.basename(filename))
    extension = ext[1:].lower()
    pmgr = BasePluginManager.get_instance()
    import_list = pmgr.get_reg_importers()
    for pdata in import_list:
        if extension == pdata.extension:
            mod = pmgr.load_plugin(pdata)
            if not mod:
                for item in pmgr.get_fail_list():
                    name, error_tuple, pdata = item
                    etype, exception, traceback = error_tuple
                return False
            import_function = getattr(mod, pdata.import_function)
            results = import_function(db, filename, user)
            if results is None:
                return False
            else:
                return True
    return False

def find_surname_name(key, data):
    """
    Creating a surname from raw name, to use for sort and index
    returns a byte string
    """
    return __index_surname(data[5])

def __index_surname(surn_list):
    """
    All non pa/matronymic surnames are used in indexing.
    pa/matronymic not as they change for every generation!
    returns a byte string
    """
    from gramps.gen.lib import NameOriginType
    if surn_list:
        surn = " ".join([x[0] for x in surn_list if not (x[3][0] in [
            NameOriginType.PATRONYMIC, NameOriginType.MATRONYMIC])])
    else:
        surn = ""
    return surn
