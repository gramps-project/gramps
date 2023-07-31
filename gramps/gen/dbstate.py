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

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import sys
import logging
import inspect

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from .db import DbReadBase
from .proxy.proxybase import ProxyDbBase
from .utils.callback import Callback
from .config import config
from .db.dbconst import DBLOGNAME
from .db.dummydb import DummyDb

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
LOG = logging.getLogger(".dbstate")
_LOG = logging.getLogger(DBLOGNAME)


class DbState(Callback):
    """
    Provide a class to encapsulate the state of the database.
    """

    __signals__ = {
        "database-changed": ((DbReadBase, ProxyDbBase),),
        "no-database": None,
    }

    def __init__(self):
        """
        Initalize the state with an empty (and useless) DummyDb. This is just a
        place holder until a real DB is assigned.
        """
        Callback.__init__(self)
        self.db = DummyDb()
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
        if __debug__ and _LOG.isEnabledFor(logging.DEBUG):
            class_name = self.__class__.__name__
            func_name = "is_open"
            frame = inspect.currentframe()
            c_frame = frame.f_back
            c_code = c_frame.f_code
            _LOG.debug(
                "calling %s.%s()... from file %s, line %s in %s",
                class_name,
                func_name,
                c_code.co_filename,
                c_frame.f_lineno,
                c_code.co_name,
            )
        return (self.db is not None) and self.db.is_open()

    def change_database(self, database):
        """
        Closes the existing db, and opens a new one.
        Retained for backward compatibility.
        """
        if database:
            self.emit("no-database", ())
            if self.is_open():
                self.db.close()
            self.change_database_noclose(database)

    def change_database_noclose(self, database):
        """
        Change the current database. and resets the configuration prefixes.
        """
        self.db = database
        self.db.set_prefixes(
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
        self.open = True

    def signal_change(self):
        """
        Emits the database-changed signal with the new database
        """
        self.emit("database-changed", (self.db,))

    def no_database(self):
        """
        Closes the database without a new database (except for the DummyDb)
        """
        self.emit("no-database", ())
        if self.is_open():
            self.db.close()
        self.db = DummyDb()
        self.open = False
        self.emit("database-changed", (self.db,))

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
        self.emit("database-changed", (self.db,))

    def pop_proxy(self):
        """
        Remove the previously applied proxy.

        >>> dbstate.apply_proxy(gen.proxy.LivingProxyDb, 1)
        >>> dbstate.pop_proxy()
        >>> dbstate.apply_proxy(gen.proxy.PrivateProxyDb)
        >>> dbstate.pop_proxy()
        """
        self.db = self.stack.pop()
        self.emit("database-changed", (self.db,))
