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

"People with an event before ..."

import Filter
import string
import Date
import RelLib

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class EventBefore(Filter.Filter):
    "People with an event before ..."

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,text):
        self.date = Date.Date()
        self.date.set(text)
        self.text = text

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def match(self,person):
        val = 0
        list = person.getEventList()[:]
        list.append(person.getBirth())
        list.append(person.getDeath())
        for event in list:
            if self.date.getDate() == "" or event.getDate() == "":
                continue
            if self.date > event.getDateObj():
                val = 1
                break
        return val

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def create(text):
    return EventBefore(text)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def need_qualifier():
    return 1
