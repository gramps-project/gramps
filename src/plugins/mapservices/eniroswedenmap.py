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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#
"""
Eniro Sweden (Denmark) map service plugin. Opens place in kartor.eniro.se
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import PluginManager
from libmapservice import MapService
from QuestionDialog import WarningDialog

# Make upper case of translaed country so string search works later
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

def _build_title(self):
    """ Builds descrition string for title parameter in url """
    descr = self.get_title()
    parish = self.get_main_location().get_parish()
    city = self.get_main_location().get_city()
    state = self.get_main_location().get_state()
    title_descr = ""
    if descr:
        title_descr += descr.strip()
    if parish:
        title_descr += u', ' + parish.strip() + _(" parish")
    if city:
        title_descr += u', ' + city.strip()
    if state:
        title_descr += u', ' + state.strip() + _(" state")
    return _strip_leading_comma(title_descr)
 
def _build_city(self):
    """ Builds description string for city parameter in url """
    county = self.get_main_location().get_county()
    # Build a title description string that will work for Eniro
    city_descr = _build_area(self)
    if county:
        city_descr += u', ' + county
    return _strip_leading_comma(city_descr)

def _build_area(self):
    """ Builds string for area parameter in url """
    street = self.get_main_location().get_street()
    city = self.get_main_location().get_city()
    # Build a title description string that will work for Eniro
    area_descr = ""
    if street:
        area_descr += street.strip() 
    if city:
        area_descr += u', ' + city 
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
        country = place.get_main_location().get_country().upper().strip()
        country_given = (country in MAP_NAMES_SWEDEN or \
                         country in MAP_NAMES_DENMARK)
        # Now check if country is defined
        if not country_given:
            WarningDialog(_("Eniro map not available for %s") % country, \
                          _("Only for Sweden and Denmark") )
            return
        # Chech if we are in the vicinity defined by
        # 54 33' 0" < lat < 66 9' 0", 54.55 and 69.05
        # 8 3' 0" < long < 24 9' 0", 8.05 and 24.15 
        latitude, longitude = self._lat_lon(place)
        if latitude == None or longitude == None:
            coord_ok = False
        else:
            latitude = float(latitude) 
            longitude = float(longitude)
            # Check if coordinates are inside Sweden and Denmark
            if (54.55 < latitude < 69.05) and (8.05 < longitude < 24.15):
                coord_ok = True
            else:
                msg2 = _("Latitude not within %s to %s\n") + \
                       _("Longitude not within %s to %s")
                msg2 = msg2 % (54.55, 69.05, 8.05, 24.15)
                WarningDialog(_("Eniro map not available"), msg2 )
                return
        if coord_ok:
            place_title = _build_title(place)
            place_city =  _build_city(place)
            x_coord, y_coord = self._lat_lon(place, format="RT90")
            # Set zoom level to 5 if Sweden/Denmark
            zoom = 5
            path = "http://www.eniro.se/partner.fcgi?pis=1&x=%s&y=%s" \
                   "&zoom_level=%i&map_size=0&title=%s&city=%s&partner=gramps"
            # Note x and y are swapped!
            path = path % (y_coord , x_coord, zoom, place_title, place_city)
            self.url = path.replace(" ","%20")
            return

        place_area = _build_area(place)
        if country_given and place_area:
            if country in MAP_NAMES_SWEDEN:
                path = "http://kartor.eniro.se/query?&what=map_adr&mop=aq" \
                       "&geo_area=%s&partner=gramps"
                path = path % (place_area)
                self.url = path.replace(" ","%20")
                return
            else:
                WarningDialog(_("Eniro map not available"), \
                              _("Coordinates needed in Denmark") )
                self.url = ""
                return
        
        WarningDialog(_("Eniro map not available"), 
                      _("Latitude and longitude,\n" \
                        "or street and city needed") )
        return
   
#------------------------------------------------------------------------
#
# Register map service
#
#------------------------------------------------------------------------
PluginManager.get_instance().register_mapservice(
    name = 'EniroMaps',
    mapservice = EniroSVMapService(),
    translated_name = _("EniroMaps"),
    status = _("Stable"),
    tooltip= _("Opens 'kartor.eniro.se' for places in Denmark and Sweden"),
    author_name="Peter Landgren",
    author_email="peter.talken@telia.com"
    )
