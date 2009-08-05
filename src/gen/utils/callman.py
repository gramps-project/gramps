#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
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
Module providing support for callback handling in the GUI
  * track object handles
  * register new handles
  * manage callback functions
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
PERSONKEY = 'person'
FAMILYKEY = 'family'
EVENTKEY = 'event'
PLACEKEY = 'place'
MEDIAKEY = 'media'
SOURCEKEY = 'source'
REPOKEY = 'repository'
NOTEKEY = 'note'

ADD = '-add'
UPDATE = '-update'
DELETE = '-delete'
REBUILD = '-rebuild'

KEYS = [PERSONKEY, FAMILYKEY, EVENTKEY, PLACEKEY, MEDIAKEY, SOURCEKEY,
        REPOKEY, NOTEKEY]

METHODS = [ADD, UPDATE, DELETE, REBUILD]
METHODS_LIST = [ADD, UPDATE, DELETE]
METHODS_NONE = [REBUILD]

PERSONCLASS = 'Person'
FAMILYCLASS = 'Family'
EVENTCLASS = 'Event'
PLACECLASS = 'Place'
MEDIACLASS = 'MediaObject'
SOURCECLASS = 'Source'
REPOCLASS = 'Repository'
NOTECLASS = 'Note'

CLASS2KEY = {
            PERSONCLASS: PERSONKEY,
            FAMILYCLASS: FAMILYKEY,
            EVENTCLASS: EVENTKEY,
            PLACECLASS: PLACEKEY,
            MEDIACLASS: MEDIAKEY,
            SOURCECLASS: SOURCEKEY,
            REPOCLASS: REPOKEY,
            NOTECLASS: NOTEKEY
            }

def _return(*args):
    """
    Function that does nothing with the arguments
    """
    return True

#-------------------------------------------------------------------------
#
# CallbackManager class
#
#-------------------------------------------------------------------------

class CallbackManager(object):
    """
    Manage callback handling from GUI to the db. 
    It is unique to a db and some GUI element. When a db is changed, one should
    destroy the CallbackManager and set up a new one (or delete the GUI element
    as it shows info from a previous db).
    
    Track changes to your relevant objects, calling callback functions as 
    needed.
    """
    def __init__(self, database):
        """
        :param database: database to which to connect the callbacks of this 
            CallbackManager object
        :type database: a class:`~gen.db.base.GrampsDbBase` object
        """
        #no handles to track
        self.database = database
        self.__handles = {
                PERSONKEY: [],
                FAMILYKEY: [],
                EVENTKEY: [],
                PLACEKEY: [],
                MEDIAKEY: [],
                SOURCEKEY: [],
                REPOKEY: [],
                NOTEKEY: [],
                }
        #no custom callbacks to do
        self.custom_signal_keys = []
        #set up callbacks to do nothing
        self.__callbacks = {}
        self.__init_callbacks()

    def __init_callbacks(self):
        """
        set up callbacks to do nothing
        """
        self.__callbacks = {}
        for key in KEYS:
            for method in METHODS:
                self.__callbacks[key+method] = [_return, None]

    def disconnect_all(self):
        """
        Disconnect from all signals from the database
        This method should always be called before a the callback methods
        become invalid.
        """
        for key in self.custom_signal_keys:
            self.database.disconnect(key)
        self.custom_signal_keys = []
        for key, value in self.__callbacks.iteritems():
            if not value[1] is None:
                self.database.disconnect(value[1])
        self.__init_callbacks()
    
    def register_obj(self, baseobj, directonly=False):
        """
        Convenience method, will register all directly and not directly 
        referenced prim objects connected to baseobj with the CallbackManager
        If directonly is True, only directly registered objects will be
        registered.
        Note that baseobj is not registered itself as it can be a sec obj.
        """
        if directonly:
            self.register_handles(directhandledict(baseobj))
        else:
            self.register_handles(handledict(baseobj))
        
    def register_handles(self, ahandledict):
        """
        Register handles that need to be tracked by the manager.
        This function can be called several times, adding to existing 
        registered handles.
        
        :param ahandledict: a dictionary with key one of the KEYS, 
            and value a list of handles to track
        """
        for key in KEYS:
            handles = ahandledict.get(key)
            if handles:
                self.__handles[key] = list(
                                      set(self.__handles[key]).union(handles))

    def unregister_handles(self, ahandledict):
        """
        All handles in handledict are no longer tracked
        
        :param handledict: a dictionary with key one of the KEYS, 
            and value a list of handles to track
        """
        for key in KEYS:
            handles = ahandledict.get(key)
            if handles:
                for handle in handles:
                    self.__handles[key].remove(handle)
    
    def unregister_all(self):
        """
        Unregister all handles that are registered
        """
        self.__handles = {
                PERSONKEY: [],
                FAMILYKEY: [],
                EVENTKEY: [],
                PLACEKEY: [],
                MEDIAKEY: [],
                SOURCEKEY: [],
                REPOKEY: [],
                NOTEKEY: [],
                }
    
    def register_callbacks(self, callbackdict):
        """
        register callback functions that need to be called for a specific 
        db action. This function can be called several times, adding to and if
        needed overwriting, existing callbacks.
        No db connects are done. If a signal already is connected to the db,
        it is removed from the connect list of the db.
        
        :param callbackdict: a dictionary with key one of KEYS+METHODS, or one
            of KEYS, and value a function to be called when signal is raised.
        """
        for key in KEYS:
            function = callbackdict.get(key)
            if function:
                for method in METHODS:
                    self.__add_callback(key+method, function)
            for method in METHODS:
                function = callbackdict.get(key+method)
                if function:
                    self.__add_callback(key+method, function)

    def connect_all(self, keys=None):
        """
        Convenience function, connects all database signals related to the 
        primary objects given in keys to the callbacks attached to self. 
        Note that only those callbacks registered with register_callbacks will
        effectively result in an action, so one can connect to all keys 
        even if not all keys have a registered callback.
        
        :param keys: list of keys of primary objects for which to connect the 
            signals, default is no connects being done. One can enable signal 
            activity to needed objects by passing a list, eg 
            keys=[callman.SOURCEKEY, callman.PLACEKEY], or to all with 
            keys=callman.KEYS
        """
        if keys is None:
            return
        for key in keys:
            for method in METHODS:
                signal = key + method
                self.__do_unconnect(signal)
                self.__callbacks[signal][1] = self.database.connect(
                                        signal, 
                                        self.__callbackcreator(key, signal))

    def __do_callback(self, signal, *arg):
        """
        Execute a specific callback. This is only actually done if one of the
        registered handles is involved. 
        Arg must conform to the requirements of the signal emitter. 
        For a GrampsDbBase that is that arg must be not given (rebuild 
        methods), or arg[0] must be the list of handles affected.
        """
        key = signal.split('-')[0]
        if arg:
            handles = arg[0]
            affected = list(set(self.__handles[key]).intersection(handles))
            if affected:
                self.__callbacks[signal][0](affected)
        else:
            affected = self.__handles[key]
            if affected:
                self.__callbacks[signal][0]()
    
    def __add_callback(self, signal, callback):
        """
        Add a callback to a signal. There can be only one callback per signal 
        that is managed, so if there is a previous one, it is removed
        """
        self.__do_unconnect(signal)
        self.__callbacks[signal] = [callback, None]

    def __do_unconnect(self, signal):
        """
        unconnect a signal from the database if it is already connected
        """
        oldcall, oldconnectkey = self.__callbacks[signal]
        if not oldconnectkey is None:
            self.database.disconnect(oldconnectkey)

    def add_db_signal(self, name, callback):
        """
        Do a custom db connect signal outside of the primary object ones
        managed automatically.
        """
        self.custom_signal_keys.append(self.database.connect(name, callback))
    
    def __callbackcreator(self, key, signal):
        """
        helper function, a lambda function needs a string to be defined 
        explicitly. This function creates the correct lambda function to use
        as callback based on the key/signal one needs to connect to. 
        AttributeError is raised for unknown key or signal.
        """
        if key == PERSONKEY:
            if signal == 'person-update':
                return lambda arg: self.__do_callback('person-update', *(arg,))
            elif signal == 'person-add':
                return lambda arg: self.__do_callback('person-add', *(arg,))
            elif signal == 'person-delete':
                return lambda arg: self.__do_callback('person-delete', *(arg,))
            elif signal == 'person-rebuild':
                return lambda *arg: self.__do_callback('person-rebuild')
            else:
                raise AttributeError, 'Signal ' + signal + 'not supported.'
        elif key == FAMILYKEY:
            if signal == 'family-update':
                return lambda arg: self.__do_callback('family-update', *(arg,))
            elif signal == 'family-add':
                return lambda arg: self.__do_callback('family-add', *(arg,))
            elif signal == 'family-delete':
                return lambda arg: self.__do_callback('family-delete', *(arg,))
            elif signal == 'family-rebuild':
                return lambda *arg: self.__do_callback('family-rebuild')
            else:
                raise AttributeError, 'Signal ' + signal + 'not supported.'
        elif key == EVENTKEY:
            if signal == 'event-update':
                return lambda arg: self.__do_callback('event-update', *(arg,))
            elif signal == 'event-add':
                return lambda arg: self.__do_callback('event-add', *(arg,))
            elif signal == 'event-delete':
                return lambda arg: self.__do_callback('event-delete', *(arg,))
            elif signal == 'event-rebuild':
                return lambda *arg: self.__do_callback('event-rebuild')
            else:
                raise AttributeError, 'Signal ' + signal + 'not supported.'
        elif key == PLACEKEY:
            if signal == 'place-update':
                return lambda arg: self.__do_callback('place-update', *(arg,))
            elif signal == 'place-add':
                return lambda arg: self.__do_callback('place-add', *(arg,))
            elif signal == 'place-delete':
                return lambda arg: self.__do_callback('place-delete', *(arg,))
            elif signal == 'place-rebuild':
                return lambda *arg: self.__do_callback('place-rebuild')
            else:
                raise AttributeError, 'Signal ' + signal + 'not supported.'
        elif key == SOURCEKEY:
            if signal == 'source-update':
                return lambda arg: self.__do_callback('source-update', *(arg,))
            elif signal == 'source-add':
                return lambda arg: self.__do_callback('source-add', *(arg,))
            elif signal == 'source-delete':
                return lambda arg: self.__do_callback('source-delete', *(arg,))
            elif signal == 'source-rebuild':
                return lambda *arg: self.__do_callback('source-rebuild')
            else:
                raise AttributeError, 'Signal ' + signal + 'not supported.'
        elif key == REPOKEY:
            if signal == 'repository-update':
                return lambda arg: self.__do_callback('repository-update', 
                                                      *(arg,))
            elif signal == 'repository-add':
                return lambda arg: self.__do_callback('repository-add', 
                                                      *(arg,))
            elif signal == 'repository-delete':
                return lambda arg: self.__do_callback('repository-delete', 
                                                      *(arg,))
            elif signal == 'repository-rebuild':
                return lambda *arg: self.__do_callback('repository-rebuild')
            else:
                raise AttributeError, 'Signal ' + signal + 'not supported.'
        elif key == MEDIAKEY:
            if signal == 'media-update':
                return lambda arg: self.__do_callback('media-update', *(arg,))
            elif signal == 'media-add':
                return lambda arg: self.__do_callback('media-add', *(arg,))
            elif signal == 'media-delete':
                return lambda arg: self.__do_callback('media-delete', *(arg,))
            elif signal == 'media-rebuild':
                return lambda *arg: self.__do_callback('media-rebuild')
            else:
                raise AttributeError, 'Signal ' + signal + 'not supported.'
        elif key == NOTEKEY:
            if signal == 'note-update':
                return lambda arg: self.__do_callback('note-update', *(arg,))
            elif signal == 'note-add':
                return lambda arg: self.__do_callback('note-add', *(arg,))
            elif signal == 'note-delete':
                return lambda arg: self.__do_callback('note-delete', *(arg,))
            elif signal == 'note-rebuild':
                return lambda *arg: self.__do_callback('note-rebuild')
            else:
                raise AttributeError, 'Signal ' + signal + 'not supported.'
        else:
            raise AttributeError, 'Signal ' + signal + 'not supported.'

def directhandledict(baseobj):
    """
    Build a handledict from baseobj with all directly referenced objects
    """
    handles = {
                PERSONKEY: [],
                FAMILYKEY: [],
                EVENTKEY: [],
                PLACEKEY: [],
                MEDIAKEY: [],
                SOURCEKEY: [],
                REPOKEY: [],
                NOTEKEY: [],
                }
    for classn, handle in baseobj.get_referenced_handles():
        handles[CLASS2KEY[classn]].append(handle)
    return handles

def handledict(baseobj):
    """
    Build a handledict from baseobj with all directly and not directly 
    referenced base obj that are present
    """
    handles = {
                PERSONKEY: [],
                FAMILYKEY: [],
                EVENTKEY: [],
                PLACEKEY: [],
                MEDIAKEY: [],
                SOURCEKEY: [],
                REPOKEY: [],
                NOTEKEY: [],
                }
    for classn, handle in baseobj.get_referenced_handles_recursively():
        handles[CLASS2KEY[classn]].append(handle)
    return handles

