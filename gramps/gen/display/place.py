#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2014-2015  Nick Hall
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
Class handling displaying of places.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..config import config
from ..utils.location import get_location_list
from ..lib import PlaceType

#-------------------------------------------------------------------------
#
# PlaceDisplay class
#
#-------------------------------------------------------------------------
class PlaceDisplay:

    def display_event(self, db, event):
        if not event:
            return ""
        place_handle = event.get_place_handle()
        if place_handle:
            place = db.get_place_from_handle(place_handle)
            return self.display(db, place, event.get_date_object())
        else:
            return ""

    def display(self, db, place, date=None):
        if not place:
            return ""
        if not config.get('preferences.place-auto'):
            return place.title
        else:
            lang = config.get('preferences.place-lang')
            places = get_location_list(db, place, date, lang)

            if config.get('preferences.place-restrict') > 0:
                index = _find_populated_place(places)
                if index is not None:
                    if config.get('preferences.place-restrict') == 1:
                        places = places[:index+1]
                    else:
                        places = places[index:]

            if config.get('preferences.place-number'):
                types = [item[1] for item in places]
                try:
                    idx = types.index(PlaceType.NUMBER)
                except ValueError:
                    idx = None
                if idx is not None and len(places) > idx+1:
                    combined = (places[idx][0] + ' ' + places[idx+1][0],
                                places[idx+1][1])
                    places = places[:idx] + [combined] + places[idx+2:]

            names = [item[0] for item in places]
            if config.get('preferences.place-reverse'):
                names.reverse()

            return ", ".join(names)

def _find_populated_place(places):
    populated_place = None
    for index, item in enumerate(places):
        if int(item[1]) in [PlaceType.HAMLET, PlaceType.VILLAGE,
                            PlaceType.TOWN, PlaceType.CITY]:
            populated_place = index
    return populated_place

displayer = PlaceDisplay()
