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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from collections import defaultdict

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

_YIELD_INTERVAL = 350

#------------------------------------------------------------------------
#
# Local functions
#
#------------------------------------------------------------------------
def make_tag_size(n, counts, mins=8, maxs=20):
    # return font sizes mins to maxs
    diff = maxs - mins
    # based on counts (biggest to smallest)
    if len(counts) > 1:
        position = diff - (diff * (float(counts.index(n)) / (len(counts) - 1)))
    else:
        position = 0
    return int(position) + mins

#------------------------------------------------------------------------
#
# SurnameCloudGramplet class
#
#------------------------------------------------------------------------
class SurnameCloudGramplet(Gramplet):
    def init(self):
        self.set_tooltip(_("Double-click surname for details"))
        self.top_size = 150 # will be overwritten in load
        self.min_font = 8
        self.max_font = 20
        self.set_text(_("No Family Tree loaded."))

    def db_changed(self):
        self.connect(self.dbstate.db, 'person-add', self.update)
        self.connect(self.dbstate.db, 'person-delete', self.update)
        self.connect(self.dbstate.db, 'person-update', self.update)
        self.connect(self.dbstate.db, 'person-rebuild', self.update)
        self.connect(self.dbstate.db, 'family-rebuild', self.update)

    def on_load(self):
        if len(self.gui.data) == 3:
            self.top_size = int(self.gui.data[0])
            self.min_font = int(self.gui.data[1])
            self.max_font = int(self.gui.data[2])

    def save_update_options(self, widget=None):
        self.top_size = int(self.get_option(_("Number of surnames")).get_value())
        self.min_font = int(self.get_option(_("Min font size")).get_value())
        self.max_font = int(self.get_option(_("Max font size")).get_value())
        self.gui.data = [self.top_size, self.min_font, self.max_font]
        self.update()

    def main(self):
        self.set_text(_("Processing...") + "\n")
        yield True
        surnames = defaultdict(int)
        representative_handle = {}

        cnt = 0
        namelist = []
        for person in self.dbstate.db.iter_people():
            allnames = [person.get_primary_name()] + person.get_alternate_names()
            allnames = set([name.get_group_name().strip() for name in allnames])
            for surname in allnames:
                surnames[surname] += 1
                representative_handle[surname] = person.handle
            cnt += 1
            if not cnt % _YIELD_INTERVAL:
                yield True
            # Count unique surnames
            for name in [person.get_primary_name()] + person.get_alternate_names():
                if not name.get_surname().strip() in namelist \
                    and not name.get_surname().strip() == "":
                    namelist.append(name.get_surname().strip())

        total_people = cnt
        surname_sort = []
        total = cnt = 0
        for surname in surnames:
            surname_sort.append((surnames[surname], surname))
            total += surnames[surname]
            cnt += 1
            if not cnt % _YIELD_INTERVAL:
                yield True

        surname_sort.sort(reverse=True)
        cloud_names = []
        cloud_values = []
        for (count, surname) in surname_sort:
            cloud_names.append((count, surname))
            cloud_values.append(count)

        cloud_names.sort(key=lambda k: k[1])
        line = 0
        ### All done!
        # Now, find out how many we can display without going over top_size:
        totals = defaultdict(int)
        for (count, givensubname) in cloud_names: # givensubname_sort:
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
        # now, limit counts to only include those that we can display:

        mins = self.min_font
        maxs = self.max_font
        # Ok, now we can show those counts > include_greater_than:
        good_counts = []
        for (count, surname) in cloud_names: # surname_sort:
            if count > include_greater_than:
                good_counts.append(count)
        counts = list(set(good_counts))
        counts.sort(reverse=True)
        showing = 0
        self.set_text("")
        for (count, surname) in cloud_names: # surname_sort:
            if count > include_greater_than:
                if len(surname) == 0:
                    text = config.get('preferences.no-surname-text')
                else:
                    text = surname
                size = make_tag_size(count, counts, mins=mins, maxs=maxs)
                self.link(text, 'Surname', representative_handle[surname], size,
                          "%s, %d%% (%d)" % (text,
                                             int((float(count)/total_people) * 100),
                                             count))
                self.append_text(" ")
                showing += 1
        self.append_text(("\n\n" + _("Total unique surnames") + ": %d\n") %
                         len(namelist))
        self.append_text((_("Total surnames showing") + ": %d\n") % showing)
        self.append_text((_("Total people") + ": %d") % total_people, "begin")

    def build_options(self):
        from gramps.gen.plug.menu import NumberOption
        self.top_size_option = NumberOption(_("Number of surnames"), self.top_size, 1, 150)
        self.add_option(self.top_size_option)
        self.min_option = NumberOption(_("Min font size"), self.min_font, 1, 50)
        self.add_option(self.min_option)
        self.max_option = NumberOption(_("Max font size"), self.max_font, 1, 50)
        self.add_option(self.max_option)

    def save_options(self):
        self.top_size = int(self.get_option(_("Number of surnames")).get_value())
        self.min_font = int(self.get_option(_("Min font size")).get_value())
        self.max_font = int(self.get_option(_("Max font size")).get_value())

