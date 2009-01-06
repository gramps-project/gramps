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

from gettext import gettext as _

from DataViews import Gramplet, register
import Config

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
        self.tooltip = _("Double-click given name for details")
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
        people = self.dbstate.db.get_person_handles(sort_handles=False)
        givensubnames = {}
        representative_handle = {}
        cnt = 0
        for person_handle in people:
            person = self.dbstate.db.get_person_from_handle(person_handle)
            if person:
                allnames = [person.get_primary_name()] + person.get_alternate_names()
                allnames = set([name.get_first_name().strip() for name in allnames])
                for givenname in allnames:
                    for givensubname in givenname.split():
                        givensubnames[givensubname] = givensubnames.get(givensubname, 0) + 1
                        representative_handle[givensubname] = person_handle
            if cnt % 350 == 0:
                yield True
            cnt += 1
        total_people = cnt
        givensubname_sort = []
        total = 0
        cnt = 0
        for givensubname in givensubnames:
            givensubname_sort.append( (givensubnames[givensubname], givensubname) )
            total += givensubnames[givensubname]
            if cnt % 350 == 0:
                yield True
            cnt += 1
        total_givensubnames = cnt
        givensubname_sort.sort(lambda a,b: -cmp(a,b))
        cloud_names = []
        cloud_values = []
        cnt = 0
        for (count, givensubname) in givensubname_sort:
            cloud_names.append( (count, givensubname) )
            cloud_values.append( count )
            if cnt > self.top_size:
                break
            cnt += 1
        cloud_names.sort(lambda a,b: cmp(a[1], b[1]))
        counts = list(set(cloud_values))
        counts.sort()
        counts.reverse()
        line = 0
        ### All done!
        self.set_text("")
        for (count, givensubname) in cloud_names: # givensubname_sort:
            if len(givensubname) == 0:
                text = Config.get(Config.NO_SURNAME_TEXT)
            else:
                text = givensubname
            size = make_tag_size(count, counts)
            self.link(text, 'Given', text, size,
                      "%s, %d%% (%d)" % (text, 
                                        int((float(count)/total) * 100), 
                                        count))
            self.append_text(" ")
            line += 1
            if line >= self.top_size:
                break
        self.append_text(("\n" + _("Total unique given names") + ": %d\n") % 
                         total_givensubnames)
        self.append_text((_("Total people") + ": %d") % total_people, "begin")

register(type="gramplet", 
         name= "Given Name Cloud Gramplet", 
         tname=_("Given Name Cloud Gramplet"), 
         height=300,
         expand=True,
         content = GivenNameCloudGramplet,
         title=_("Given Name Cloud"),
         )
