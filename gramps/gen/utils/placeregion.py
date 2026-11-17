#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Place region utility functions.

Return the places located in a region around some coordinates. This
module only needs a database. No GUI, no map and no network are
required. It reuses the same code type as the place selection dialog
used by the geography views.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import math

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..lib import PlaceType
from .place import conv_lat_lon


def get_location(db, place):
    """
    Get the location values for the place: its name and the names of its
    parents when they are related to a country, a state, a county or
    another type of region.
    """
    parent_place = None
    country = state = county = other = ""
    place_name = place.name.get_value()
    parent_list = place.get_placeref_list()
    while parent_list:
        place = db.get_place_from_handle(parent_list[0].ref)
        parent_list = place.get_placeref_list()
        if int(place.get_type()) == PlaceType.COUNTY:
            county = place.name.get_value()
            if parent_place is None:
                parent_place = place.get_handle()
        elif int(place.get_type()) == PlaceType.STATE:
            state = place.name.get_value()
            if parent_place is None:
                parent_place = place.get_handle()
        elif int(place.get_type()) == PlaceType.COUNTRY:
            country = place.name.get_value()
            if parent_place is None:
                parent_place = place.get_handle()
        else:
            other = place.name.get_value()
            if parent_place is None:
                parent_place = place.get_handle()
    return (country, state, county, place_name, other)


def get_places_in_region(db, lat, lon, radius=1.0):
    """
    Return the places located in a region around the given coordinates.

    The region is a circle centered on the latitude and the longitude,
    with the given radius in degrees.

    Returns a list of (handle, country, state, county, name, other)
    tuples, sorted by country, state, county and name. The places with
    wrong or missing coordinates are ignored.
    """
    candidates = {}
    for place in db.iter_places():
        latn = place.get_latitude()
        lonn = place.get_longitude()
        if not latn or not lonn:
            continue
        latn, dummy_ignore = conv_lat_lon(latn, "0", "D.D8")
        if not latn:
            continue
        dummy_ignore, lonn = conv_lat_lon("0", lonn, "D.D8")
        if not lonn:
            continue
        if math.hypot(lat - float(latn), lon - float(lonn)) <= radius:
            candidates[place.get_handle()] = place
    places = []
    for handle, place in candidates.items():
        country, state, county, name, other = get_location(db, place)
        places.append((handle, country, state, county, name, other))
    places.sort(key=lambda row: (row[1], row[2], row[3], row[4]))
    return places
