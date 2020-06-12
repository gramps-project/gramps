# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program - Records plugin
#
# Copyright (C) 2020      Paul Culley
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

# ------------------------------------------------------------------------
#
# Standard Python modules
#
# ------------------------------------------------------------------------
import datetime

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.lib.placegrouptype import PlaceGroupType as P_G
from gramps.gen.lib.placetype import PlaceType
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value):  # enable deferred translations (see Python docs 22.1.3.4)
    return value


COUNTRY = "Country"  # 1
STATE = "State"  # 2
COUNTY = "County"  # 3
CITY = "City"  # 4
PARISH = "Parish"  # 5
LOCALITY = "Locality"  # 6
STREET = "Street"  # 7
PROVINCE = "Province"  # 8
REGION = "Region"  # 9
DEPARTMENT = "Department"  # 10
NEIGHBORHOOD = "Neighborhood"  # 11
DISTRICT = "District"  # 12
BOROUGH = "Borough"  # 13
MUNICIPALITY = "Municipality"  # 14
TOWN = "Town"  # 15
VILLAGE = "Village"  # 16
HAMLET = "Hamlet"  # 17
FARM = "Farm"  # 18
BUILDING = "Building"  # 19
NUMBER = "Number"  # 20

# The data map (dict) contains a tuple with key as a handle
#   name
#   native name
#   countries
#   color
#   probable group (used for legacy XML import)
#   gettext method (or None if standard method)
DATAMAP = {
    COUNTRY: (_T_("Country"), "Country", "#FFFF00000000", P_G(P_G.COUNTRY), None),
    STATE: (_T_("State"), "State", "#0000FFFFFFFF", P_G(P_G.REGION), None),
    COUNTY: (_T_("County"), "County", "#0000FFFFFFFF", P_G(P_G.REGION), None),
    CITY: (_T_("City"), "City", "#0000FFFF0000", P_G(P_G.PLACE), None),
    PARISH: (_T_("Parish"), "Parish", "#0000FFFFFFFF", P_G(P_G.REGION), None),
    LOCALITY: (_T_("Locality"), "Locality", "#0000FFFF0000", P_G(P_G.PLACE), None),
    STREET: (_T_("Street"), "Street", "#0000FFFF0000", P_G(P_G.OTHER), None),
    PROVINCE: (_T_("Province"), "Province", "#0000FFFFFFFF", P_G(P_G.REGION), None),
    REGION: (_T_("Region"), "Region", "#0000FFFFFFFF", P_G(P_G.REGION), None),
    DEPARTMENT: (
        _T_("Department"),
        "Department",
        "#0000FFFFFFFF",
        P_G(P_G.REGION),
        None,
    ),
    NEIGHBORHOOD: (
        _T_("Neighborhood"),
        "Neighborhood",
        "#0000FFFF0000",
        P_G(P_G.PLACE),
        None,
    ),
    DISTRICT: (_T_("District"), "District", "#0000FFFF0000", P_G(P_G.PLACE), None),
    BOROUGH: (_T_("Borough"), "Borough", "#0000FFFF0000", P_G(P_G.PLACE), None),
    MUNICIPALITY: (
        _T_("Municipality"),
        "Municipality",
        "#0000FFFF0000",
        P_G(P_G.PLACE),
        None,
    ),
    TOWN: (_T_("Town"), "Town", "#0000FFFF0000", P_G(P_G.PLACE), None),
    VILLAGE: (_T_("Village"), "Village", "#0000FFFF0000", P_G(P_G.PLACE), None),
    HAMLET: (_T_("Hamlet"), "Hamlet", "#0000FFFF0000", P_G(P_G.PLACE), None),
    FARM: (_T_("Farm"), "Farm", "#0000FFFF0000", P_G(P_G.PLACE), None),
    BUILDING: (_T_("Building"), "Building", "#0000FFFF0000", P_G(P_G.BUILDING), None),
    NUMBER: (_T_("Number"), "Number", "#0000FFFF0000", P_G(P_G.OTHER), None),
}


def load_on_reg(_dbstate, _uistate, _plugin):
    """
    Runs when plugin is registered.
    """
    for hndl, tup in DATAMAP.items():
        # for these common elements, the category is '!!'
        PlaceType.register_placetype(hndl, tup, "!!")
    PlaceType.update_name_map()
