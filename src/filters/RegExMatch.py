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

"Names that match a regular expression"

import Filter
import re
import Utils
import intl
_ = intl.gettext

class RegExMatch(Filter.Filter):
    "Names that match a regular expression"

    def __init__(self,text):
        self.ok = 1
        try:
            self.regexp = re.compile(text,re.IGNORECASE)
        except:
            self.ok = 0
        Filter.Filter.__init__(self,text)

    def match(self,person):
        if self.ok == 0:
            return 0
        else:
            return self.regexp.search(Utils.phonebook_name(person))

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
Filter.register_filter(RegExMatch,
                       description=_("Names that match a regular expression"),
                       label=_("Text"),
                       qualifier=1)







