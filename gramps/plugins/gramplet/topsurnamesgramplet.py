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
from gramps.gen.plug import Gramplet
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Person
from gramps.gen.plug.menu import NumberOption
from gramps.gen.types import PersonHandle

_ = glocale.translation.sgettext

# ------------------------------------------------------------------------
#
# Constants
#
# ------------------------------------------------------------------------
_YIELD_INTERVAL = 350

NUM_SURNAMES = _("Number of Surnames to display")


# ------------------------------------------------------------------------
#
# Helper functions
#
# ------------------------------------------------------------------------
def record_surnames(
    person: Person,
    surnames: dict[str, int],
    representative_handle: dict[str, PersonHandle],
) -> None:
    """
    Tally one person's surnames and choose representatives for them.

    The person is counted under every group name taken from their primary and
    alternate names.  They become the representative for a surname only when it
    is their primary group name, or when no representative has been chosen yet.
    The Same Surnames quick view re-derives the surname from the
    representative's primary name, so a representative whose primary surname
    differs would open a report for a different surname than the one clicked.
    """
    primary_name = person.get_primary_name()
    primary_surname = primary_name.get_group_name().strip()
    allnames = set(
        name.get_group_name().strip()
        for name in [primary_name] + person.get_alternate_names()
    )
    for surname in allnames:
        surnames[surname] += 1
        if surname == primary_surname or surname not in representative_handle:
            representative_handle[surname] = person.handle


# ------------------------------------------------------------------------
#
# TopSurnamesGramplet class
#
# ------------------------------------------------------------------------
class TopSurnamesGramplet(Gramplet):
    def init(self):
        self.set_tooltip(_("Double-click surname for details"))
        self.top_size = 10  # will be overwritten in load
        self.set_text(_("No Family Tree loaded."))

    def db_changed(self):
        self.connect(self.dbstate.db, "person-add", self.update)
        self.connect(self.dbstate.db, "person-delete", self.update)
        self.connect(self.dbstate.db, "person-update", self.update)
        self.connect(self.dbstate.db, "person-rebuild", self.update)
        self.connect(self.dbstate.db, "family-rebuild", self.update)
        self.set_text(_("No Family Tree loaded."))

    def build_options(self):
        self.add_option(NumberOption(NUM_SURNAMES, self.top_size, 10, 1000))

    def save_options(self):
        self.top_size = int(self.get_option(NUM_SURNAMES).get_value())

    def on_load(self):
        if len(self.gui.data) == 1:
            self.top_size = int(self.gui.data[0])

    def on_save(self):
        self.gui.data = [self.top_size]

    def main(self):
        self.set_text(_("Processing...") + "\n")
        surnames: dict[str, int] = defaultdict(int)
        representative_handle: dict[str, PersonHandle] = {}

        cnt = 0
        for person in self.dbstate.db.iter_people():
            record_surnames(person, surnames, representative_handle)
            cnt += 1
            if not cnt % _YIELD_INTERVAL:
                yield True

        total_people = cnt
        surname_sort = []
        total = 0

        cnt = 0
        for surname in surnames:
            surname_sort.append((surnames[surname], surname))
            total += surnames[surname]
            cnt += 1
            if not cnt % _YIELD_INTERVAL:
                yield True

        total_surnames = cnt
        surname_sort.sort(reverse=True)
        line = 0
        ### All done!
        self.set_text("")
        nosurname = config.get("preferences.no-surname-text")
        for count, surname in surname_sort:
            text = "%s, " % (surname if surname else nosurname)
            text += "%d%% (%d)\n" % (int((float(count) / total) * 100), count)
            self.append_text(" %d. " % (line + 1))
            self.link(text, "Surname", representative_handle[surname])
            line += 1
            if line >= self.top_size:
                break
        self.append_text(
            ("\n" + _("Total unique surnames") + ": %d\n") % total_surnames
        )
        self.append_text((_("Total people") + ": %d") % total_people, "begin")
