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

"People who were adopted"

import Filter
from gettext import gettext as _

class HaveAltFamilies(Filter.Filter):
    "People who were adopted"

    def match(self,person):
        for vals in person.get_parent_family_id_list():
            if vals[1] == "Adopted" or vals[2] == "Adopted":
                return 1
        return 0


Filter.register_filter(HaveAltFamilies,
                       description=_("People who were adopted"),
                       qualifier=0)

