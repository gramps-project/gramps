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

from .db import DbBsddbRead
from .db import DbReadBase
from .proxy.proxybase import ProxyDbBase
from .utils.callback import Callback
from .config import config

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
        Initalize the state with an empty (and useless) DbBsddbRead. This is
        just a place holder until a real DB is assigned.
        """
        Callback.__init__(self)
        self.db      = DbBsddbRead()
        self.open    = False
        self.stack = []

    def change_database(self, database):
        """
        Closes the existing db, and opens a new one.
        Retained for backward compatibility.
        """
        self.emit('no-database', ())
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
            config.get('preferences.nprefix') )
        self.open = True

    def signal_change(self):
        """
        Emits the database-changed signal with the new database
        """
        self.emit('database-changed', (self.db, ))

    def no_database(self):
        """
        Closes the database without a new database
        """
        self.emit('no-database', ())
        self.db.close()
        self.db = DbBsddbRead()
        self.db.db_is_open = False
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

        >>> dbstate.apply_proxy(gen.proxy.LivingProxyDb, 1)
        >>> dbstate.apply_proxy(gen.proxy.PrivateProxyDb)
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
