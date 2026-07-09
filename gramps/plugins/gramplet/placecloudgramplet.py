# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009       Pander Musubi
# Copyright (C) 2009       Douglas S. Blank
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
#
#

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.plugins.gramplet.cloudgramplet import CloudGramplet


class PlaceCloudGramplet(CloudGramplet):
    """Implementation of a Cloud gramplet for place name"""

    def init(self):
        CloudGramplet.init(self)
        self.set_value_name("place name")
        self.set_item_name("place")

    def db_changed(self):
        self.connect(self.dbstate.db, "place-add", self.update)
        self.connect(self.dbstate.db, "place-delete", self.update)
        self.connect(self.dbstate.db, "place-update", self.update)

    def get_items(self) -> list:
        items = []

        for place in self.dbstate.db.iter_places():
            placename = place.name.get_value()
            items.append((placename,place.handle))

        return items

