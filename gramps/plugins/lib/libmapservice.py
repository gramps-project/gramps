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
#
"""
Base class for map services. Example: open place in openstreetmap.org
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.utils.place import conv_lat_lon
from gramps.gui.display import display_url

class MapService:
    """Generic base class for map services
       A service is a singleton, we only need one to exist
       Usage is as a callable when used
    """
    def __init__(self):
        self.database = None
        self.items = None
        self.url = ''

    def __call__(self, database, items, uistate):
        """Callable class, usable as a function. This guarantees the class is
           instantiated once when a service is registered. Afterward only calls
           occur
           database: Database to work on
           items: list of tuples (place_handle, description), where description
                  is None or a string to use for marker (eg 'birth John Doe')
           uistate: This is only used for transient windows if needed
        """
        self.database = database
        self.items = items
        self.uistate = uistate
        self.url = ''
        #An instance is called, we display the result
        self.calc_url()
        self.__display()
        self._free()

    def _get_first_place(self):
        """Obtain the first place object"""
        place_handle = self.items[0][0]

        return self.database.get_place_from_handle(place_handle), \
                        self.items[0][1]

    def _all_places(self):
        """Obtain a list generator of all place objects
            Usage as an iterator:
                for place, descr in mapservice.all_places()
        """
        for handle, descr in self.items:
            yield self.database.get_place_from_handle(handle), descr

    def _lat_lon(self, place, format="D.D8"):
        """return the lat, lon value of place in the requested format
           None, None if invalid
        """
        return conv_lat_lon(place.get_latitude(),
                            place.get_longitude(), format)

    def calc_url(self):
        """Base class needs to overwrite this, calculation of the self.path"""
        raise NotImplementedError

    def __display(self):
        """Show the url in an external browser"""
        if self.url:
            display_url(self.url)

    def _free(self):
        """Allow garbage collection to do it's work"""
        self.items = None
