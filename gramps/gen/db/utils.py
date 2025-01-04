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

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import logging
import os

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from ..config import config
from ..const import GRAMPS_LOCALE as glocale
from ..const import PLUGINS_DIR, USER_PLUGINS
from ..constfunc import get_env_var, win
from ..lib import NameOriginType
from ..plug import BasePluginManager
from .dbconst import DBBACKEND, DBLOCKFN, DBLOGNAME

_ = glocale.translation.gettext

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
            if __debug__ and _LOG.isEnabledFor(logging.DEBUG):
                import inspect

                frame = inspect.currentframe()
                c_frame = frame.f_back
                c_code = c_frame.f_code
                _LOG.debug(
                    "Database class instance created Class:%s instance:%s. "
                    "Called from File %s, line %s, in %s",
                    db.__class__.__name__,
                    hex(id(db)),
                    c_code.co_filename,
                    c_frame.f_lineno,
                    c_code.co_name,
                )
            return db
        raise Exception(f"can't load database backend: '{plugin_id}'")
    raise Exception(f"no such database backend: '{plugin_id}'")


def open_database(dbname, force_unlock=False, callback=None):
    """
    Open a database by name and return the database.
    """
    data = lookup_family_tree(dbname)
    database = None
    if data:
        dbpath, locked, _, backend = data
        if (not locked) or (locked and force_unlock):
            database = make_database(backend)
            database.load(dbpath, callback=callback)
    return database


def lookup_family_tree(dbname):
    """
    Find a Family Tree given its name, and return properties.
    """
    dbdir = os.path.expanduser(config.get("database.path"))
    for dpath in os.listdir(dbdir):
        dirpath = os.path.join(dbdir, dpath)
        path_name = os.path.join(dirpath, "name.txt")
        if os.path.isfile(path_name):
            with open(path_name, "r", encoding="utf8") as file:
                name = file.readline().strip()
            if dbname == name:
                locked = False
                locked_by = None
                backend = get_dbid_from_path(dirpath)
                try:
                    fname = os.path.join(dirpath, "lock")
                    with open(fname, "r", encoding="utf8") as ifile:
                        locked_by = ifile.read().strip()
                        locked = True
                except (OSError, IOError):
                    pass
                return (dirpath, locked, locked_by, backend)
    return None


def get_dbid_from_path(dirpath):
    """
    Return a database backend from a directory path.
    """
    dbid = "bsddb"
    dbid_path = os.path.join(dirpath, DBBACKEND)
    if os.path.isfile(dbid_path):
        with open(dbid_path, encoding="utf8") as file:
            dbid = file.read().strip()
    return dbid


def import_as_dict(filename, user, skp_imp_adds=True):
    """
    Import the filename into a InMemoryDB and return it.
    """
    db = make_database("sqlite")
    db.load(":memory:")
    db.set_feature("skip-import-additions", skp_imp_adds)
    db.set_prefixes(
        config.get("preferences.iprefix"),
        config.get("preferences.oprefix"),
        config.get("preferences.fprefix"),
        config.get("preferences.sprefix"),
        config.get("preferences.cprefix"),
        config.get("preferences.pprefix"),
        config.get("preferences.eprefix"),
        config.get("preferences.rprefix"),
        config.get("preferences.nprefix"),
    )
    status = import_from_filename(db, filename, user)
    return db if status else None


def import_from_filename(db, filename, user):
    """
    Import a file into a database.
    """
    (_, ext) = os.path.splitext(os.path.basename(filename))
    extension = ext[1:].lower()
    pmgr = BasePluginManager.get_instance()
    import_list = pmgr.get_reg_importers()
    for pdata in import_list:
        if extension == pdata.extension:
            mod = pmgr.load_plugin(pdata)
            if not mod:
                return False
            import_function = getattr(mod, pdata.import_function)
            results = import_function(db, filename, user)
            if results is None:
                return False
            return True
    return False


def find_surname_name(surname_list):
    """
    Create a surname-string to use for sort and index.

    All non pa/matronymic surnames are used in indexing.
    pa/matronymic not as they change for every generation!

    Returns a string.
    """
    if surname_list:
        surn = " ".join(
            [
                surname.surname
                for surname in surname_list
                if surname.origintype.value
                not in [NameOriginType.PATRONYMIC, NameOriginType.MATRONYMIC]
            ]
        )
    else:
        surn = ""
    return surn


def clear_lock_file(name):
    """
    Clear the lock file.
    """
    try:
        os.unlink(os.path.join(name, DBLOCKFN))
    except OSError:
        return


def write_lock_file(name):
    """
    Write the lock file.
    """
    if not os.path.isdir(name):
        os.mkdir(name)
    with open(os.path.join(name, DBLOCKFN), "w", encoding="utf8") as lock_file:
        if win():
            user = get_env_var("USERNAME")
            host = get_env_var("USERDOMAIN")
            if not user:
                user = _("Unknown")
        else:
            host = os.uname()[1]
            # An ugly workaround for os.getlogin() issue with Konsole
            try:
                user = os.getlogin()
            except:
                # not win, so don't need get_env_var.
                # under cron getlogin() throws and there is no USER.
                user = os.environ.get("USER", "noUSER")
        if host:
            text = f"{user}@{host}"
        else:
            text = user
        # Save only the username and host, so the massage can be
        # printed with correct locale in DbManager.py when a lock is found
        lock_file.write(text)
