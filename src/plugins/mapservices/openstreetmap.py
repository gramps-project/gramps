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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $id: $
#
"""
OpenStreetMap map service plugin. Open place in openstreetmap.org
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gen.ggettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from libmapservice import MapService


class OpensStreetMapService(MapService):
    """Map  service using http://openstreetmap.org
        Resource: http://wiki.openstreetmap.org/index.php/Name_finder
    """
    def __init__(self):
        MapService.__init__(self)
    
    def calc_url(self):
        """ Determine the url to use 
            Logic: use lat lon if present
                   otherwise use city and country if present
                   otherwise use description of the place
        """
        place = self._get_first_place()[0]
        latitude, longitude = self._lat_lon(place)
        if longitude and latitude:
            self.url = "http://www.openstreetmap.org/" \
                        "?lat=%s&lon=%s&zoom=15" % (latitude, longitude)
                        
            return
        
        city = place.get_main_location().get_city()
        country = place.get_main_location().get_country()
        if city and country:
            self.url = "http://gazetteer.openstreetmap.org/namefinder/"\
                        "?find=%s%%2C%s" % (city, country)
            return
        
        titledescr = place.get_title()
        self.url = "http://gazetteer.openstreetmap.org/namefinder/"\
                        "?find=%s" % '+'.join(titledescr.split())
