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
Provides the database state class
"""

__author__ = "Donald N. Allingham"
__revision__ = "$Revision: 8032 $"

from GrampsDb import GrampsDBCallback, GrampsDbBase
import Config

class DbState(GrampsDBCallback):
    """
    Provides a class to encapsulate the state of the database..
    """

    __signals__ = {
        'database-changed' : (GrampsDbBase, ), 
        'active-changed'   : (str, ), 
        'no-database'      :  None, 
        }

    def __init__(self):
        """
        Initalize the state with an empty (and useless) GrampsDbBase. This is
        just a place holder until a real DB is assigned.
        """
        GrampsDBCallback.__init__(self)
        self.db      = GrampsDbBase()
        self.open    = False
        self.active  = None
        self.sighndl = None

    def change_active_person(self, person):
        """
        Changes the active person and emits a signal to notify those who
        are interested.
        """
        self.active = person
        if person:
            try:
                self.emit('active-changed', (person.handle, ))
            except:
                self.emit('active-changed', ("", ))

    def change_active_handle(self, handle):
        """
        Changes the active person based on the person's handle
        """
        self.change_active_person(self.db.get_person_from_handle(handle))

    def get_active_person(self):
        """
        Gets the current active person. Creates a new instance to make sure that
        the data is active.
        """
        if self.active: 
            self.active = self.db.get_person_from_handle(self.active.handle)
        return self.active

    def change_database(self, database):
        """
        Closes the existing db, and opens a new one.
        """
        self.db.close()
        self.change_database_noclose(database)

    def change_database_noclose(self, database):
        """
        Changes the current database. and resets the configuration prefixes.
        """
        self.db = database
        self.db.set_prefixes(
            Config.get(Config.IPREFIX),
            Config.get(Config.OPREFIX),
            Config.get(Config.FPREFIX),
            Config.get(Config.SPREFIX),
            Config.get(Config.PPREFIX),
            Config.get(Config.EPREFIX),
            Config.get(Config.RPREFIX),
            Config.get(Config.NPREFIX) )

        self.active = None
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
        self.db.close()
        self.db = GrampsDbBase()
        self.active = None
        self.open = False
        self.emit('database-changed', (self.db, ))
