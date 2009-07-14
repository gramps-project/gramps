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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# $Id$

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from DataViews import register, Gramplet
from TransUtils import sgettext as _
import Config

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
# Gramplet class
#
#------------------------------------------------------------------------
class SurnameCloudGramplet(Gramplet):
    def init(self):
        self.set_tooltip(_("Double-click surname for details"))
        self.top_size = 100 # will be overwritten in load
        self.set_text(_("No Family Tree loaded."))

    def db_changed(self):
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('person-update', self.update)
        self.dbstate.db.connect('person-rebuild', self.update)
        self.dbstate.db.connect('family-rebuild', self.update)

    def on_load(self):
        if len(self.gui.data) > 0:
            self.top_size = int(self.gui.data[0])

    def on_save(self):
        self.gui.data = [self.top_size]

    def main(self):
        self.set_text(_("Processing...") + "\n")
        yield True
        people = self.dbstate.db.iter_person_handles()
        surnames = {}
        representative_handle = {}

        cnt = 0
        for person_handle in people:
            person = self.dbstate.db.get_person_from_handle(person_handle)
            if person:
                allnames = [person.get_primary_name()] + person.get_alternate_names()
                allnames = set([name.get_group_name().strip() for name in allnames])
                for surname in allnames:
                    surnames[surname] = surnames.get(surname, 0) + 1
                    representative_handle[surname] = person_handle
            if not cnt % _YIELD_INTERVAL:
                yield True
            cnt += 1

        total_people = cnt
        surname_sort = []
        total = cnt = 0
        for surname in surnames:
            surname_sort.append( (surnames[surname], surname) )
            total += surnames[surname]
            if not cnt % _YIELD_INTERVAL:
                yield True
            cnt += 1

        total_surnames = cnt
        surname_sort.sort(reverse=True)
        cloud_names = []
        cloud_values = []
        for (count, surname) in surname_sort:
            cloud_names.append( (count, surname) )
            cloud_values.append( count )

        cloud_names.sort(key=lambda k:k[1])
        counts = list(set(cloud_values))
        counts.sort(reverse=True)
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
        showing = 0
        self.set_text("")
        for (count, surname) in cloud_names: # surname_sort:
            if count > include_greater_than:
                if len(surname) == 0:
                    text = Config.get(Config.NO_SURNAME_TEXT)
                else:
                    text = surname
                size = make_tag_size(count, counts)
                self.link(text, 'Surname', representative_handle[surname], size,
                          "%s, %d%% (%d)" % (text, 
                                             int((float(count)/total_people) * 100), 
                                             count))
                self.append_text(" ")
                showing += 1
        self.append_text(("\n\n" + _("Total unique surnames") + ": %d\n") % 
                         total_surnames)
        self.append_text((_("Total surnames showing") + ": %d\n") % showing)
        self.append_text((_("Total people") + ": %d") % total_people, "begin")

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(type="gramplet", 
         name= "Surname Cloud Gramplet", 
         tname=_("Surname Cloud Gramplet"), 
         height=300,
         expand=True,
         content = SurnameCloudGramplet,
         title=_("Surname Cloud"),
         )

