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

# ------------------------------------------------------------------------
#
# SurnameCloudGramplet class
#
# ------------------------------------------------------------------------
class SurnameCloudGramplet(CloudGramplet):
    def init(self):
        CloudGramplet.init(self)
        self.set_value_name("surname")
        self.set_item_name("person")
        self.set_preference_no_value("preferences.no-surname-text")
        self.set_link_type("Surname")

    def db_changed(self):
        self.connect(self.dbstate.db, "person-add", self.update)
        self.connect(self.dbstate.db, "person-delete", self.update)
        self.connect(self.dbstate.db, "person-update", self.update)
        self.connect(self.dbstate.db, "person-rebuild", self.update)
        self.connect(self.dbstate.db, "family-rebuild", self.update)

    def get_items(self):
        items = []

        for person in self.dbstate.db.iter_people():
            allnames = [person.get_primary_name()] + person.get_alternate_names()
            for name in allnames:
                name = name.get_group_name().strip()
                items.append((name , person.handle))
        return items
