# Gramps - a GTK+/GNOME based genealogy program
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009       Peter Landgren
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
# plugins/mapservices/eniroswedenmap.py

"""
Eniro Sweden (Denmark) map service plugin. Opens place in kartor.eniro.se
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.plugins.lib.libmapservice import MapService
from gramps.gui.dialog import WarningDialog
from gramps.gen.utils.location import get_main_location
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.lib import PlaceType

# Make upper case of translated country so string search works later
MAP_NAMES_SWEDEN = [_("Sweden").upper(),
                      "SVERIGE",
                      "SWEDEN",
                      "SUEDOIS",
                      "ROUTSI",
                      "SCHWEDEN", ]
MAP_NAMES_DENMARK = [_("Denmark").upper(),
                       "DANMARK",
                       "DENMARK",
                       "DANOIS",
                       "TANSKA",
                       "DÄNEMARK", ]


def _strip_leading_comma(descr):
    """ Strips leading comma
    and leading and trailing spaces
    """
    if len(descr) > 0 and descr.strip()[0] == ",":
        descr = descr.strip()[1:]
    return descr.strip()

def _build_title(db, place):
    """ Builds descrition string for title parameter in url """
    descr = place_displayer.display(db, place)
    location = get_main_location(db, place)
    parish = location.get(PlaceType.PARISH)
    city = location.get(PlaceType.CITY)
    state = location.get(PlaceType.STATE)
    title_descr = ""
    if descr:
        title_descr += descr.strip()
    if parish:
        # TODO for Arabic, should the next line's comma be translated?
        title_descr += ', ' + parish.strip() + _(" parish")
    if city:
        # TODO for Arabic, should the next line's comma be translated?
        title_descr += ', ' + city.strip()
    if state:
        # TODO for Arabic, should the next line's comma be translated?
        title_descr += ', ' + state.strip() + _(" state")
    return _strip_leading_comma(title_descr)

def _build_city(db, place):
    """ Builds description string for city parameter in url """
    location = get_main_location(db, place)
    county = location.get(PlaceType.COUNTY)
    # Build a title description string that will work for Eniro
    city_descr = _build_area(db, place)
    if county:
        # TODO for Arabic, should the next line's comma be translated?
        city_descr += ', ' + county
    return _strip_leading_comma(city_descr)

def _build_area(db, place):
    """ Builds string for area parameter in url """
    location = get_main_location(db, place)
    street = location.get(PlaceType.STREET)
    city = location.get(PlaceType.CITY)
    # Build a title description string that will work for Eniro
    area_descr = ""
    if street:
        area_descr += street.strip()
    if city:
        # TODO for Arabic, should the next line's comma be translated?
        area_descr += ', ' + city
    return _strip_leading_comma(area_descr)


class EniroSVMapService(MapService):
    """Map  service using http://kartor.eniro.se"""
    def __init__(self):
        MapService.__init__(self)

    def calc_url(self):
        """ Determine the url to use on maps.google.com
            Logic: valid for places within Sweden and
                   Denmark, only if lat lon avalible
                   use lat lon if present
                   otherwise use city and country if present
                   otherwise use description of the place
        """
        place = self._get_first_place()[0]
        path = ""
        # First see if we are in or near Sweden or Denmark
        # Change country to upper case
        location = get_main_location(self.database, place)
        country = location.get(PlaceType.COUNTRY, '').upper().strip()
        country_given = (country in MAP_NAMES_SWEDEN or \
                        country in MAP_NAMES_DENMARK) and (country != "")
        # if no country given, check if we might be in the vicinity defined by
        # 54 33' 0" < lat < 66 9' 0", 54.55 and 69.05
        # 8 3' 0" < long < 24 9' 0", 8.05 and 24.15
        latitude, longitude = self._lat_lon(place)
        if latitude is None or longitude is None:
            coord_ok = False
        else:
            latitude = float(latitude)
            longitude = float(longitude)
            # Check if coordinates are inside Sweden and Denmark
            if (54.55 < latitude < 69.05) and (8.05 < longitude < 24.15):
                coord_ok = True
            else:
                msg2 = _("Latitude not within '54.55' to '69.05'\n") + \
                       _("Longitude not within '8.05' to '24.15'")
                WarningDialog(_("Eniro map not available"), msg2,
                              parent=self.uistate.window)
                return

        if coord_ok:
            place_title = _build_title(self.database, place)
            place_city = _build_city(self.database, place)
            x_coord, y_coord = self._lat_lon(place, format="RT90")
            # Set zoom level to 5 if Sweden/Denmark, others 3
            zoom = 5
            if not country_given:
                zoom = 3
            path = "http://www.eniro.se/partner.fcgi?pis=1&x=%s&y=%s" \
                   "&zoom_level=%i&map_size=0&title=%s&city=%s&partner=gramps"
            # Note x and y are swapped!
            path = path % (y_coord , x_coord, zoom, place_title, place_city)
            self.url = path.replace(" ","%20")
            return

        place_area = _build_area(self.database, place)
        if country_given and place_area:
            if country in MAP_NAMES_SWEDEN:
                path = "http://kartor.eniro.se/query?&what=map_adr&mop=aq" \
                       "&geo_area=%s&partner=gramps"
                path = path % (place_area)
                self.url = path.replace(" ","%20")
                return
            else:
                WarningDialog(_("Eniro map not available"),
                              _("Coordinates needed in Denmark"),
                              parent=self.uistate.window)
                self.url = ""
                return

        WarningDialog(_("Eniro map not available"),
                      _("Latitude and longitude,\n"
                        "or street and city needed"),
                      parent=self.uistate.window)
        return

