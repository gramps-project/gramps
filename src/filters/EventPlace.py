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
import string
import re
import RelLib
import intl
_ = intl.gettext

class EventPlace(Filter.Filter):
    "People with an event location of ..."

    def __init__(self,text):
        self.ok = 1
        try:
            self.regexp = re.compile(text,re.IGNORECASE)
        except:
            self.ok = 0
        Filter.Filter.__init__(self,text)

    def match(self,person):
        val = 0
        list = person.getEventList()[:]
        list.append(person.getBirth())
        list.append(person.getDeath())
        for event in list:
            if self.regexp.search(event.getPlace().get_title()):
                val = 1
                break
        return val

def create(text):
    return EventPlace(text)

def need_qualifier():
    return 1

def get_name():
    return _("People with an event location of ...")
