#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009       Benny Malengier
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
Group common stuff Gramps GUI elements must be able to do when tracking a DB:

   * connect to db signals
   * listen to db changes to update themself on relevant changes
   * determine if the GUI has become out of sync with the db
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.utils.callman import CallbackManager

#-------------------------------------------------------------------------
#
# DbGUIElement class
#
#-------------------------------------------------------------------------
class DbGUIElement:
    """
    Most interaction with the DB should be done via the callman attribute.
    On initialization, the method :meth:`_connect_db_signals` is called.
    Inheriting objects are advised to group the setup of the callman attribute
    here.

    .. attribute callman: a :class:`.CallbackManager` object, to be used to
                          track specific changes in the db and set up callbacks
    """
    def __init__(self, database):
        self.callman = CallbackManager(database)
        self._connect_db_signals()

    def _add_db_signal(self, name, callback):
        """
        Convenience function to add a custom db signal. The attributes are just
        passed to the callman object.
        For primary objects, use the register method of the callman attribute.

        :param name: name of the signal to connect to
        :type name: string
        :param callback: function to call when signal is emitted
        :type callback: a funtion or method with the correct signature for the
                signal
        """
        self.callman.add_db_signal(name, callback)

    def _connect_db_signals(self):
        """
        Convenience method that is called on initialization of DbGUIElement.
        Use this to group setup of the callman attribute.
        Also called in _change_db method
        """
        pass

    def _cleanup_callbacks(self):
        """
        Remove all db callbacks.
        This is done automatically on destruction of the object, but is
        normally needed earlier, calling this method does so.
        Use _change_db method if you need to remove the callbacks because the
        database has changed
        """
        database = self.callman.database
        if database.is_open():
            #a closed database has disconnected all signals
            self.callman.disconnect_all()
        #set a new callback manager
        self.callman = CallbackManager(database)

    def _change_db(self, database):
        """
        Change the database the GUI element works on to database.
        This removes all callbacks and all registered handles.

        :param database: the new database to connect to
        """
        dbold = self.callman.database
        if dbold.is_open():
            #a closed database has disconnected all signals
            self.callman.disconnect_all()
        #set a new callback manager on new database
        self.callman = CallbackManager(database)
        self._connect_db_signals()
