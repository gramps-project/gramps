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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#
#
from gettext import gettext as _

from gen.plug import Gramplet
import config

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

class GivenNameCloudGramplet(Gramplet):
    def init(self):
        self.set_tooltip(_("Double-click given name for details"))
        self.top_size = 100 # will be overwritten in load
        self.set_text(_("No Family Tree loaded."))

    def db_changed(self):
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('person-update', self.update)

    def on_load(self):
        if len(self.gui.data) > 0:
            self.top_size = int(self.gui.data[0])

    def on_save(self):
        self.gui.data = [self.top_size]

    def main(self):
        self.set_text(_("Processing...") + "\n")
        yield True
        givensubnames = {}
        representative_handle = {}

        cnt = 0
        for person in self.dbstate.db.iter_people():
            allnames = [person.get_primary_name()] + person.get_alternate_names()
            allnames = set(name.get_first_name().strip() for name in allnames)
            for givenname in allnames:
                for givensubname in givenname.split():
                    givensubnames[givensubname] = givensubnames.get(givensubname, 0) + 1
                    representative_handle[givensubname] = person.handle
            cnt += 1
            if not cnt % _YIELD_INTERVAL:
                yield True

        total_people = cnt
        givensubname_sort = []
		
        total = cnt = 0
        for givensubname in givensubnames:
            givensubname_sort.append( (givensubnames[givensubname], givensubname) )
            total += givensubnames[givensubname]
            cnt += 1
            if not cnt % _YIELD_INTERVAL:
                yield True

        total_givensubnames = cnt
        givensubname_sort.sort(reverse=True)
        cloud_names = []
        cloud_values = []

        for count, givensubname in givensubname_sort:
            cloud_names.append( (count, givensubname) )
            cloud_values.append( count )

        cloud_names.sort(key=lambda k: k[1])
        counts = sorted(set(cloud_values), reverse=True)
        line = 0
        ### All done!
        # Now, find out how many we can display without going over top_size:
        totals = {}
        for (count, givensubname) in cloud_names: # givensubname_sort:
            totals[count] = totals.get(count, 0) + 1
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
        for (count, givensubname) in cloud_names: # givensubname_sort:
            if count > include_greater_than:
                if len(givensubname) == 0:
                    text = config.get('preferences.no-surname-text')
                else:
                    text = givensubname
                size = make_tag_size(count, counts)
                self.link(text, 'Given', text, size,
                          "%s, %.2f%% (%d)" % 
                          (text, 
                           (float(count)/total_people) * 100, 
                           count))
                self.append_text(" ")
                showing += 1

        self.append_text(("\n\n" + _("Total unique given names") + ": %d\n") % 
                         total_givensubnames)
        self.append_text((_("Total given names showing") + ": %d\n") % showing)
        self.append_text((_("Total people") + ": %d") % total_people, "begin")
