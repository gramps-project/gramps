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


class GivenNameCloudGramplet(CloudGramplet):
    def init(self):
        CloudGramplet.init(self)
        self.set_value_name("given name")
        self.set_item_name("person")
        self.set_preference_no_value("preferences.no-given-text")
        self.set_link_type("Given")

    def db_changed(self):
        self.connect(self.dbstate.db, "person-add", self.update)
        self.connect(self.dbstate.db, "person-delete", self.update)
        self.connect(self.dbstate.db, "person-update", self.update)

    def get_items(self):
        items = []

        for person in self.dbstate.db.iter_people():
            allnames = [person.get_primary_name()] + person.get_alternate_names()
            for name in allnames:
                name = name.get_first_name().strip()
                items.append((name,name))
        return items
        

