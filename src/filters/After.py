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

"People with an event after ..."

import Filter
import Date
from gettext import gettext as _

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class EventAfter(Filter.Filter):
    "People with an event after ..."

    def __init__(self,text):
        self.date = Date.Date()
        self.date.set(text)
        Filter.Filter.__init__(self,text)

    def match(self,p):
        for event in p.get_event_list() + [p.get_birth(), p.get_death()]:
            if self.date.get_date() == "" or event.get_date() == "":
                continue
            if event.get_date_object().greater_than(self.date):
                return 1
        return 0

#--------------------------------------------------------------------
#
# 
#
#--------------------------------------------------------------------
Filter.register_filter(EventAfter,
                       description=_("People with an event after ..."),
                       label=_("Date"),
                       qualifier=1)

