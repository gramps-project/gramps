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

"""
Support classes to simplify GEDCOM importing
"""

import re
import RelLib

NAME_RE    = re.compile(r"/?([^/]*)(/([^/]*)(/([^/]*))?)?")
SURNAME_RE = re.compile(r"/([^/]*)/([^/]*)")

#-------------------------------------------------------------------------
#
# CurrentState
#
#-------------------------------------------------------------------------
class CurrentState:
    """
    Keeps track of the current state variables
    """
    def __init__(self, person=None, level=0, event=None, event_ref=None):
        """
        Initializes the object
        """
        self.name_cnt = 0
        self.person = person
        self.level = level
        self.event = event
        self.event_ref = event_ref
        self.source_ref = None

    def __getattr__(self, name):
        """
        Returns the value associated with the specified attribute.
        """
        return self.__dict__.get(name)

    def __setattr__(self, name, value):
        """
        Sets the value associated with the specified attribute.
        """
        self.__dict__[name] = value

#-------------------------------------------------------------------------
#
# PlaceParser
#
#-------------------------------------------------------------------------
class PlaceParser:
    """
    Provides the ability to parse GEDCOM FORM statements for places, and
    the parse the line of text, mapping the text components to Location
    values based of the FORM statement.
    """

    __field_map = {
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
        self.parse_function = []
	
        if line:
            self.parse_form(line)

    def parse_form(self, line):
        """
        Parses the GEDCOM PLAC.FORM into a list of function
        pointers (if possible). It does this my mapping the text strings
        (separated by commas) to the corresponding RelLib.Location
        method via the __field_map variable
        """
        for item in line.data.split(','):
            item = item.lower().strip()
            fcn = self.__field_map.get(item, lambda x, y: None)
            self.parse_function.append(fcn)

    def load_place(self, place, text):
        """
        Takes the text string representing a place, splits it into
        its subcomponents (comma separated), and calls the approriate
        function based of its position, depending on the parsed value
        from the FORM statement.
        """
        items = [item.strip() for item in text.split(',')]
        if len(items) != len(self.parse_function):
            return
        loc = place.get_main_location()
        index = 0
        for item in items:
            self.parse_function[index](loc, item)
            index += 1

#-------------------------------------------------------------------------
#
# IdFinder
#
#-------------------------------------------------------------------------
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

#-------------------------------------------------------------------------
#
# IdMapper
#
#-------------------------------------------------------------------------
class IdMapper:

    def __init__(self, trans, find_next, translate):
        if translate:
            self.__getitem__ = self.get_translate
        else:
            self.__getitem__ = self.no_translate
        self.trans = trans
        self.find_next = find_next
        self.swap = {}
    
    def clean(self, gid):
        temp = gid.strip()
        if len(temp) > 1 and temp[0] == '@' and temp[-1] == '@':
            temp = temp[1:-1]
        return temp

    def no_translate(self, gid):
        return self.clean(gid)
        
    def get_translate(self, gid):
        gid = self.clean(gid)
        new_id = self.swap.has_key(gid)
        if new_id:
            return new_id
        else:
            if self.trans.get(str(gid)):
                new_val = self.find_next()
            else:
                new_val = gid
        self.swap[gid] = new_val
        return new_val

#------------------------------------------------------------------------
#
# Support functions
#
#------------------------------------------------------------------------
def parse_name_personal(text):
    """
    Parses a GEDCOM NAME value into an Name structure
    """
    name = RelLib.Name()

    match = SURNAME_RE.match(text)
    if match:
        names = match.groups()
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

def extract_id(value):
    """
    Extracts a value to use for the GRAMPS ID value from the GEDCOM
    reference token. The value should be in the form of @XYZ@, and the
    returned value will be XYZ
    """
    return value.strip()[1:-1]
