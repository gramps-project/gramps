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

"""
Eniro Sweden (Denmark) Maps map service plugin. Opens place in kartor.eniro.se
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
from QuestionDialog import ErrorDialog, WarningDialog

MAP_NAMES_SWEDEN = ("SVERIGE", "SWEDEN", "SUEDOIS", "ROUTSI", "SCHWEDEN")
MAP_NAMES_DENMARK = ("DANMARK", "DENMARK", "DANOIS", "TANSKA", "DÄNEMARK")


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
        path= ""
        # First see if we are in Sweden or Denmark
        country = place.get_main_location().get_country()
        if country.upper() in MAP_NAMES_SWEDEN or country.upper() in MAP_NAMES_DENMARK:
            descr = place.get_title()
            x, y = self._lat_lon(place, format="RT90")
            city = place.get_main_location().get_city()
            street = place.get_main_location().get_street()
            parish = place.get_main_location().get_parish()
            county = place.get_main_location().get_county()
            state = place.get_main_location().get_state()
 
            # Build a description string that will work for Eniro
            if street:
                place_descr = street
            else:
                place_descr = u' ' + descr
            if parish:
                place_descr += u', ' + parish + _(" parish")
            if city:
                place_descr += u',  ' + city 

            if x and y:
                    if county:
                        place_descr += u' ' + county
                    if state:
                        place_descr += u' ' + state + u' län'
                    path = "http://www.eniro.se/partner.fcgi?pis=1&x=%s&y=%s&zoom_level=5" \
                           "&map_size=0&title=%s&city=%s&partner=gramps"
                    # Note x and y are swapped!
                    path = path % (y , x, place_descr.strip(), parish.strip())
                    path = path.replace(" ","%20")

            elif city and country:
                if country.upper() in MAP_NAMES_SWEDEN:
                    path = "http://kartor.eniro.se/query?&what=map_adr&mop=aq&geo_area=%s" \
                           "&partner=gramps"
                    path = path % ( place_descr.strip())
                    path = path.replace(" ","%20")
                else:
                    WarningDialog(_("Map not availabel in Denmark without coordinates") )
                    self.url = ""
                    return
            else:
                WarningDialog(_("You need latitude and longitud,\n or city and country") )
        else:
            WarningDialog(_("Map not availabel for %s,\n only for Sweden and Denmark") % country)

        self.url = path

    
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
    tooltip= _("Opens on kartor.eniro.se"),
    author_name="Peter Landgren",
    author_email="peter.talken@telia.com"
    )

