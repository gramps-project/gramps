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
# Gramplet class
#
#------------------------------------------------------------------------
class TopSurnamesGramplet(Gramplet):
    def init(self):
        self.set_tooltip(_("Double-click surname for details"))
        self.top_size = 10 # will be overwritten in load
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
        people = self.dbstate.db.iter_person_handles()
        surnames = {}
        representative_handle = {}

        cnt = 0
        for person_handle in people:
            person = self.dbstate.db.get_person_from_handle(person_handle)
            if person:
                cnt += 1
                allnames = [person.get_primary_name()] + person.get_alternate_names()
                allnames = set([name.get_group_name().strip() for name in allnames])
                for surname in allnames:
                    surnames[surname] = surnames.get(surname, 0) + 1
                    representative_handle[surname] = person_handle
            if not cnt % _YIELD_INTERVAL:
                yield True

        total_people = cnt
        surname_sort = []
        total = 0

        for cnt, surname in enumerate(surnames):
            surname_sort.append( (surnames[surname], surname) )
            total += surnames[surname]
            if not cnt % _YIELD_INTERVAL:
                yield True

        total_surnames = cnt
        surname_sort.sort(reverse=True)
        line = 0
        ### All done!
        self.set_text("")
        nosurname = Config.get(Config.NO_SURNAME_TEXT)
        for (count, surname) in surname_sort:
            text = "%s, " % (surname if surname else nosurname)
            text += "%d%% (%d)\n" % (int((float(count)/total) * 100), count)
            self.append_text(" %d. " % (line + 1))
            self.link(text, 'Surname', representative_handle[surname])
            line += 1
            if line >= self.top_size:
                break
        self.append_text(("\n" + _("Total unique surnames") + ": %d\n") % 
                         total_surnames)
        self.append_text((_("Total people") + ": %d") % total_people, "begin")
        
#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(type="gramplet", 
         name= "Top Surnames Gramplet", 
         tname=_("Top Surnames Gramplet"), 
         height=230,
         content = TopSurnamesGramplet,
         title=_("Top Surnames"),
         )

