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

"Names that contain a substring"

import Filter
import string
import Utils
import intl
_ = intl.gettext

class SubString(Filter.Filter):
    "Names that contain a substring"

    def match(self,person):
        s1 = string.lower(Utils.phonebook_name(person))
        s2 = string.lower(self.text)
        return string.find(s1,s2) >= 0

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
Filter.register_filter(SubString,
                       description=_("Names that contain a substring"),
                       label=_("Text"),
                       qualifier=1)

