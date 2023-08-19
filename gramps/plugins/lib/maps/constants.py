#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010-2016 Serge Noiraud
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

"Geography constants"

# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------
import os
import gi
from gi.repository import OsmGpsMap as osmgpsmap
from gramps.gen.lib import EventType
from gramps.gen.const import USER_CACHE

gi.require_version("OsmGpsMap", "1.0")

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
GEOGRAPHY_PATH = os.path.join(USER_CACHE, "maps")

ICONS = {
    EventType.BIRTH: "gramps-geo-birth",
    EventType.DEATH: "gramps-geo-death",
    EventType.MARRIAGE: "gramps-geo-marriage",
}

# map providers
OPENSTREETMAP = 1
OPENSTREETMAP_RENDERER = 2
OPENAERIALMAP = 3
MAPS_FOR_FREE = 4
OPENCYCLEMAP = 5
OSM_PUBLIC_TRANSPORT = 6
OSMC_TRAILS = 7
GOOGLE_STREET = 8
GOOGLE_SATELLITE = 9
GOOGLE_HYBRID = 10
VIRTUAL_EARTH_STREET = 11
VIRTUAL_EARTH_SATELLITE = 12
VIRTUAL_EARTH_HYBRID = 13
YAHOO_STREET = 14
YAHOO_SATELLITE = 15
YAHOO_HYBRID = 16
# PERSONAL = 30

TILES_PATH = {
    OPENSTREETMAP: "openstreetmap",
    OPENSTREETMAP_RENDERER: "openstreetmaprenderer",
    OPENAERIALMAP: "openaerialmap",
    MAPS_FOR_FREE: "mapsforfree",
    OPENCYCLEMAP: "opencyclemap",
    OSM_PUBLIC_TRANSPORT: "publictransport",
    OSMC_TRAILS: "osmctrails",
    GOOGLE_STREET: "googlestreet",
    GOOGLE_SATELLITE: "googlesat",
    GOOGLE_HYBRID: "googlehybrid",
    VIRTUAL_EARTH_STREET: "virtualearthstreet",
    VIRTUAL_EARTH_SATELLITE: "virtualearthsat",
    VIRTUAL_EARTH_HYBRID: "virtualearthhybrid",
    YAHOO_STREET: "yahoostreet",
    YAHOO_SATELLITE: "yahoosat",
    YAHOO_HYBRID: "yahoohybrid",
    # PERSONAL: "personal",
}

MAP_TITLE = {
    OPENSTREETMAP: "OpenStreetMap",
    OPENSTREETMAP_RENDERER: "OpenStreetMap renderer",
    OPENAERIALMAP: "OpenAerialMap",
    MAPS_FOR_FREE: "Maps For Free",
    OPENCYCLEMAP: "OpenCycleMap",
    OSM_PUBLIC_TRANSPORT: "Public Transport",
    OSMC_TRAILS: "OSMC Trails",
    GOOGLE_STREET: "Google street",
    GOOGLE_SATELLITE: "Google sat",
    GOOGLE_HYBRID: "Google hybrid",
    VIRTUAL_EARTH_STREET: "Virtualearth street",
    VIRTUAL_EARTH_SATELLITE: "Virtualearth sat",
    VIRTUAL_EARTH_HYBRID: "Virtualearth hybrid",
    YAHOO_STREET: "Yahoo street",
    YAHOO_SATELLITE: "Yahoo sat",
    YAHOO_HYBRID: "Yahoo hybrid",
    # PERSONAL: "Personal map",
}

MAP_TYPE = {
    OPENSTREETMAP: osmgpsmap.MapSource_t.OPENSTREETMAP,
    MAPS_FOR_FREE: osmgpsmap.MapSource_t.MAPS_FOR_FREE,
    OPENCYCLEMAP: osmgpsmap.MapSource_t.OPENCYCLEMAP,
    OSM_PUBLIC_TRANSPORT: osmgpsmap.MapSource_t.OSM_PUBLIC_TRANSPORT,
    GOOGLE_STREET: osmgpsmap.MapSource_t.GOOGLE_STREET,
    GOOGLE_SATELLITE: osmgpsmap.MapSource_t.GOOGLE_SATELLITE,
    GOOGLE_HYBRID: osmgpsmap.MapSource_t.GOOGLE_HYBRID,
    VIRTUAL_EARTH_STREET: osmgpsmap.MapSource_t.VIRTUAL_EARTH_STREET,
    VIRTUAL_EARTH_SATELLITE: osmgpsmap.MapSource_t.VIRTUAL_EARTH_SATELLITE,
    VIRTUAL_EARTH_HYBRID: osmgpsmap.MapSource_t.VIRTUAL_EARTH_HYBRID,
    # PERSONAL: None,
}
