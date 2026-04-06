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
from collections import defaultdict

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

_YIELD_INTERVAL = 350


def make_tag_size(n, counts, mins=8, maxs=20):
    # return font sizes mins to maxs
    diff = maxs - mins
    # based on counts (biggest to smallest)
    if len(counts) > 1:
        position = diff - (diff * (float(counts.index(n)) / (len(counts) - 1)))
    else:
        position = 0
    return int(position) + mins


class PlaceCloudGramplet(Gramplet):
    def init(self):
        self.set_tooltip(_("Double-click place name for details"))
        self.top_size = 100  # will be overwritten in load
        self.set_text(_("No Family Tree loaded."))

    def db_changed(self):
        self.connect(self.dbstate.db, "place-add", self.update)
        self.connect(self.dbstate.db, "place-delete", self.update)
        self.connect(self.dbstate.db, "place-update", self.update)

    def on_load(self):
        if len(self.gui.data) > 0:
            self.top_size = int(self.gui.data[0])

    def on_save(self):
        self.gui.data = [self.top_size]

    def main(self):
        self.set_text(_("Processing...") + "\n")
        yield True
        placenames = defaultdict(int)


        cnt = 0
        for place in self.dbstate.db.iter_places():
            placename = place.name.get_value()
            placenames[placename] += 1
            cnt += 1
            if not cnt % _YIELD_INTERVAL:
                yield True

        total_people = cnt
        placenames_sort = []

        total = cnt = 0
        for placename in placenames:
            placenames_sort.append((placenames[placename], placename))
            total += placenames[placename]
            cnt += 1
            if not cnt % _YIELD_INTERVAL:
                yield True

        total_placenames = cnt
        placenames_sort.sort(reverse=True)
        cloud_names = []
        cloud_values = []

        for count, placename in placenames_sort:
            cloud_names.append((count, placename))
            cloud_values.append(count)

        cloud_names.sort(key=lambda k: k[1])
        counts = sorted(set(cloud_values), reverse=True)

        ### All done!
        # Now, find out how many we can display without going over top_size:
        totals = defaultdict(int)
        for count, placename in cloud_names:
            totals[count] += 1
        sums = sorted(totals, reverse=True)
        total = 0
        include_greater_than = 0
        for s in sums:
            if total + totals[s] <= self.top_size:
                total += totals[s]
            else:
                include_greater_than = s
                break
        # Ok, now we can show those counts > include_greater_than:

        self.set_text("")
        showing = 0
        for count, placename in cloud_names:
            if count > include_greater_than:
                if len(placename) == 0:
                    text = config.get("preferences.no-surname-text")
                else:
                    text = placename
                size = make_tag_size(count, counts)
                self.link(
                    text,
                    "", # TODO : Is link a good choice for place name ? Which link_type is requiered ? 
                    text,
                    size,
                    "%s, %.2f%% (%d)"
                    % (text, (float(count) / total_people) * 100, count),
                )
                self.append_text(" ")
                showing += 1

        self.append_text(
            ("\n\n" + _("Total unique places name") + ": %d\n") % total_placenames
        )
        self.append_text((_("Total places name showing") + ": %d\n") % showing)
        self.append_text((_("Total places") + ": %d") % total_people, "begin")
