#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Nick Hall
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
Helper class for importing places.
"""
from collections import OrderedDict

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Place, PlaceName, PlaceType, PlaceRef


# -------------------------------------------------------------------------
#
# PlaceImport class
#
# -------------------------------------------------------------------------
class PlaceImport:
    """
    Helper class for importing places.
    """

    def __init__(self, db):
        self.db = db
        self.loc2handle = {}
        self.handle2loc = OrderedDict()

    def store_location(self, location, handle):
        """
        Store the location of a place already in the database.
        """
        self.loc2handle[location] = handle
        self.handle2loc[handle] = location

    def remove_location(self, handle):
        """
        Remove the location of a place already in the database.
        """
        if handle in self.handle2loc:
            loc = self.handle2loc[handle]
            del self.loc2handle[loc]
            del self.handle2loc[handle]

    def generate_hierarchy(self, trans):
        """
        Generate missing places in the place hierarchy.
        """
        for handle, location in self.handle2loc.items():
            # find title and type
            for type_num, name in enumerate(location):
                if name:
                    break

            loc = list(location)
            loc[type_num] = ""

            # find top parent
            parent = None
            for n in range(7):
                if loc[n]:
                    tup = tuple([""] * n + loc[n:])
                    parent = self.loc2handle.get(tup)
                    if parent:
                        break

            # create missing parent places
            if parent:
                n -= 1
            while n > type_num:
                if loc[n]:
                    # TODO for Arabic, should the next comma be translated?
                    title = ", ".join([item for item in loc[n:] if item])
                    parent = self.__add_place(loc[n], n, parent, title, trans)
                    self.loc2handle[tuple([""] * n + loc[n:])] = parent
                n -= 1

            # link to existing place
            if parent:
                place = self.db.get_place_from_handle(handle)
                placeref = PlaceRef()
                placeref.ref = parent
                place.set_placeref_list([placeref])
                self.db.commit_place(place, trans, place.get_change_time())

    def __add_place(self, name, type_num, parent, title, trans):
        """
        Add a missing place to the database.
        """
        place = Place()
        place_name = PlaceName()
        place_name.set_value(name)
        place.name = place_name
        place.title = title
        place.place_type = PlaceType(7 - type_num)
        if parent is not None:
            placeref = PlaceRef()
            placeref.ref = parent
            place.set_placeref_list([placeref])
        handle = self.db.add_place(place, trans)
        self.db.commit_place(place, trans)
        return handle
