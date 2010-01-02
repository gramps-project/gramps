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
Provide the database state class
"""

from gen.db import DbBsddbRead
from gen.utils import Callback
import config
from gui.views.navigationview import (NAVIGATION_PERSON, NAVIGATION_FAMILY,
                                      NAVIGATION_EVENT, NAVIGATION_PLACE,
                                      NAVIGATION_SOURCE, NAVIGATION_REPOSITORY,
                                      NAVIGATION_MEDIA, NAVIGATION_NOTE)
ACTIVE_SIGNALS = ['person-active',
                  'family-active',
                  'event-active',
                  'place-active',
                  'source-active',
                  'repository-active',
                  'media-active',
                  'note-active']

class DbState(Callback):
    """
    Provide a class to encapsulate the state of the database.
    """

    __signals__ = {
        'database-changed'  : (DbBsddbRead, ), 
        'active-changed'    : (str, ), 
        'person-active'     : (str, ),
        'family-active'     : (str, ),
        'event-active'      : (str, ),
        'place-active'      : (str, ),
        'source-active'     : (str, ),
        'repository-active' : (str, ),
        'media-active'      : (str, ),
        'note-active'       : (str, ),
        'no-database'       :  None, 
        }

    def __init__(self):
        """
        Initalize the state with an empty (and useless) DbBsddbRead. This is
        just a place holder until a real DB is assigned.
        """
        Callback.__init__(self)
        self.db      = DbBsddbRead()
        self.open    = False
        self.active  = None # Retained for backward compatibility.
        self.__active_objects = [None] * 8
        self.sighndl = None

    def change_active_person(self, person):
        """
        Change the active person and emits a signal to notify those who
        are interested.
        """
        print 'DbState: change_active_person is deprecated, ' + \
                'use set_active_person instead.'
        if person:
            self.set_active_person(person.get_handle())

    def change_active_handle(self, handle):
        """
        Change the active person based on the person's handle
        """
        print 'DbState: change_active_handle is deprecated, ' + \
                'use set_active_person instead.'
        self.set_active_person(handle)

    def change_database(self, database):
        """
        Closes the existing db, and opens a new one.
        Retained for backward compatibility.
        """
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
            config.get('preferences.pprefix'),
            config.get('preferences.eprefix'),
            config.get('preferences.rprefix'),
            config.get('preferences.nprefix') )

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
        self.db = DbBsddbRead()
        self.db.db_is_open = False
        self.active = None # Retained for backward compatibility.
        self.__active_objects = [None] * 8
        self.open = False
        self.emit('database-changed', (self.db, ))
        
    def get_database(self):
        """
        Get a reference to the current database.
        """
        return self.db

    def set_active(self, navigation_type, handle):
        """
        Set the active handle for the given navigation type.
        """
        handle = str(handle) # This is sometimes unicode.
        old_handle = self.__active_objects[navigation_type]
        if old_handle != handle:
            self.__active_objects[navigation_type] = handle
            signal = ACTIVE_SIGNALS[navigation_type]
            try:
                self.emit(signal, (handle, ))
            except:
                self.emit(signal, ("", ))

            # Retained for backward compatibility.
            if navigation_type == NAVIGATION_PERSON:
                self.active = self.db.get_person_from_handle(handle)
                try:
                    self.emit('active-changed', (handle, ))
                except:
                    self.emit('active-changed', ("", ))

    def get_active(self, navigation_type):
        """
        Return the active handle for the given navigation type.
        """
        handle = self.__active_objects[navigation_type]
        if navigation_type == NAVIGATION_PERSON:
            return self.db.get_person_from_handle(handle)
        elif navigation_type == NAVIGATION_FAMILY:
            return self.db.get_family_from_handle(handle)
        elif navigation_type == NAVIGATION_EVENT:
            return self.db.get_event_from_handle(handle)
        elif navigation_type == NAVIGATION_PLACE:
            return self.db.get_place_from_handle(handle)
        elif navigation_type == NAVIGATION_SOURCE:
            return self.db.get_source_from_handle(handle)
        elif navigation_type == NAVIGATION_REPOSITORY:
            return self.db.get_repository_from_handle(handle)
        elif navigation_type == NAVIGATION_MEDIA:
            return self.db.get_object_from_handle(handle)
        elif navigation_type == NAVIGATION_NOTE:
            return self.db.get_note_from_handle(handle)
            
    ###########################################################################
    # Convenience functions
    ###########################################################################
    def set_active_person(self, handle):
        """Set the active person to the given handle."""
        self.set_active(NAVIGATION_PERSON, handle)

    def get_active_person(self):
        """Return the handle for the active person."""
        return self.get_active(NAVIGATION_PERSON)
        
    def set_active_family(self, handle):
        """Set the active family to the given handle."""
        self.set_active(NAVIGATION_FAMILY, handle)

    def get_active_family(self):
        """Return the handle for the active family."""
        return self.get_active(NAVIGATION_FAMILY)
        
    def set_active_event(self, handle):
        """Set the active event to the given handle."""
        self.set_active(NAVIGATION_EVENT, handle)

    def get_active_event(self):
        """Return the handle for the active event."""
        return self.get_active(NAVIGATION_EVENT)
        
    def set_active_place(self, handle):
        """Set the active place to the given handle."""
        self.set_active(NAVIGATION_PLACE, handle)

    def get_active_place(self):
        """Return the handle for the active place."""
        return self.get_active(NAVIGATION_PLACE)
        
    def set_active_source(self, handle):
        """Set the active source to the given handle."""
        self.set_active(NAVIGATION_SOURCE, handle)

    def get_active_source(self):
        """Return the handle for the active source."""
        return self.get_active(NAVIGATION_SOURCE)
        
    def set_active_repository(self, handle):
        """Set the active repository to the given handle."""
        self.set_active(NAVIGATION_REPOSITORY, handle)

    def get_active_repository(self):
        """Return the handle for the active repository."""
        return self.get_active(NAVIGATION_REPOSITORY)
        
    def set_active_media(self, handle):
        """Set the active media to the given handle."""
        self.set_active(NAVIGATION_MEDIA, handle)

    def get_active_media(self):
        """Return the handle for the active media."""
        return self.get_active(NAVIGATION_MEDIA)
        
    def set_active_note(self, handle):
        """Set the active note to the given handle."""
        self.set_active(NAVIGATION_NOTE, handle)

    def get_active_note(self):
        """Return the handle for the active note."""
        return self.get_active(NAVIGATION_NOTE)
