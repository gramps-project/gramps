#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

"People with an event location of ..."

import Filter
import re
from gettext import gettext as _

class EventPlace(Filter.Filter):
    """Finds people with a specfied event location in any field"""

    def __init__(self,text):
        self.ok = 1
        try:
            self.regexp = re.compile(text,re.IGNORECASE)
        except:
            self.ok = 0
        Filter.Filter.__init__(self,text)

    def match(self,person):
        list = person.get_event_list()[:]
        list.append(person.get_birth())
        list.append(person.get_death())
        for event in list:
            if self.regexp.search(event.get_place_name()):
                return 1
            place = event.get_place_id()
            if not place:
                continue
            locs = [place.get_main_location()] + place.get_alternate_locations()
            for location in locs:
                if self.regexp.search(location.get_city()):
                    return 1
                if self.regexp.search(location.get_parish()):
                    return 1
                if self.regexp.search(location.get_county()):
                    return 1
                if self.regexp.search(location.get_state()):
                    return 1
                if self.regexp.search(location.get_country()):
                    return 1
        return 0

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
Filter.register_filter(EventPlace,
                       description=_("People with an event location of ..."),
                       label=_("Place"),
                       qualifier=1)
