# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from collections import defaultdict

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------

from gramps.plugins.gramplet.cloudgramplet import CloudGramplet 
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale


# ------------------------------------------------------------------------
#
# SurnameCloudGramplet class
#
# ------------------------------------------------------------------------
class SurnameCloudGramplet(CloudGramplet):
    def init(self):
        CloudGramplet.init(self)

    def get_items(self):
        items = []

        for person in self.dbstate.db.iter_people():
            allnames = [person.get_primary_name()] + person.get_alternate_names()
            allnames = [name.get_group_name().strip() for name in allnames]
            items.append((allnames , person.handle))
        return items
