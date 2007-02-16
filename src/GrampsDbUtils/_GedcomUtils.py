#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

import re

import RelLib

class PlaceParser:

    field_map = {
	'addr'          : RelLib.Location.set_street,
	'subdivision'   : RelLib.Location.set_street,
	'addr1'         : RelLib.Location.set_street,
	'adr1'          : RelLib.Location.set_street,
	'city'          : RelLib.Location.set_city,
	'town'          : RelLib.Location.set_city,
	'village'       : RelLib.Location.set_city,
	'county'        : RelLib.Location.set_county,
	'country'       : RelLib.Location.set_country,
	'state'         : RelLib.Location.set_state,
	'state/province': RelLib.Location.set_state,
	'region'        : RelLib.Location.set_state,
	'province'      : RelLib.Location.set_state,
	'area code'     : RelLib.Location.set_postal_code,
	}

    def __init__(self, line=None):
        self.pf = []
	
	if line:
	    self.parse_form(line)

    def parse_form(self, line):
        for item in line.data.split(','):
            item = item.lower().strip()
            fcn = self.field_map.get(item, lambda x, y: None)
            self.pf.append(fcn)

    def load_place(self, place, text):
	items = [item.strip() for item in text.split(',')]
	if len(items) != len(self.pf):
	    return
	loc = place.get_main_location()
	index = 0
	for item in items:
	    self.pf[index](loc, item)
	    index += 1
	

class IdFinder:
    """
    Provides method of finding the next available ID.
    """
    def __init__(self, keys, prefix):
        """
        Initializes the object.
        """
        self.ids = set(keys)
        self.index = 0
        self.prefix = prefix

    def find_next(self):
        """
        Returns the next available GRAMPS' ID for a Event object based
        off the person ID prefix.

        @return: Returns the next available index
        @rtype: str
        """
        index = self.prefix % self.index
        while str(index) in self.ids:
            self.index += 1
            index = self.prefix % self.index
        self.ids.add(index)
        self.index += 1
        return index

#------------------------------------------------------------------------
#
# Support functions
#
#------------------------------------------------------------------------

NAME_RE    = re.compile(r"/?([^/]*)(/([^/]*)(/([^/]*))?)?")
SURNAME_RE = re.compile(r"/([^/]*)/([^/]*)")

def parse_name_personal(self, text):
    name = RelLib.Name()

    m = SURNAME_RE.match(text)
    if m:
        names = m.groups()
        name.set_first_name(names[1].strip())
        name.set_surname(names[0].strip())
    else:
        try:
            names = NAME_RE.match(text).groups()
            name.set_first_name(names[0].strip())
            name.set_surname(names[2].strip())
            name.set_suffix(names[4].strip())
        except:
            name.set_first_name(text.strip())
    return name

def extract_id(self):
    """
    Extracts a value to use for the GRAMPS ID value from the GEDCOM
    reference token. The value should be in the form of @XXX@, and the
    returned value will be XXX
    """
    return value.strip()[1:-1]
