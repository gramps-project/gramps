#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2014       Nick Hall
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
from ..utils.location import get_location_list

try:
    from ..config import config
    WITH_GRAMPS_CONFIG=True
except ImportError:
    WITH_GRAMPS_CONFIG=False

#-------------------------------------------------------------------------
#
# PlaceDisplay class
#
#-------------------------------------------------------------------------
class PlaceDisplay(object):

    def __init__(self):
        if WITH_GRAMPS_CONFIG:
            self.default_format = config.get('preferences.place-format')
        else:
            self.default_format = 0

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
        if self.default_format == 0:
            return place.title
        elif self.default_format == 1:
            names = [item[0] for item in get_location_list(db, place, date)]
            return ", ".join(names)

displayer = PlaceDisplay()
