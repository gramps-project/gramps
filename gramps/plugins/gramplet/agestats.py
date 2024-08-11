#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Douglas S. Blank
# Copyright (C) 2019  Nick Hall
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
#

"""
Age Stats Gramplet

This Gramplet shows distributions of age breakdowns of various types.
"""
# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from collections import defaultdict

# -------------------------------------------------------------------------
#
# Gtk modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.lib import Date, ChildRefType
from gramps.gui.widgets import Histogram
from gramps.gui.plug.quick import run_quick_report_by_name
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


class AgeStatsGramplet(Gramplet):
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

        self.max_age = 110
        self.max_mother_diff = 55
        self.max_father_diff = 70

    def db_changed(self):
        self.connect(self.dbstate.db, "person-add", self.update)
        self.connect(self.dbstate.db, "person-delete", self.update)
        self.connect(self.dbstate.db, "person-update", self.update)
        self.connect(self.dbstate.db, "event-update", self.update)

    def build_gui(self):
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox.set_margin_start(6)
        self.vbox.set_margin_end(6)
        self.vbox.set_margin_top(6)
        self.vbox.set_margin_bottom(6)
        self.vbox.set_spacing(12)
        return self.vbox

    def build_options(self):
        from gramps.gen.plug.menu import NumberOption

        self.add_option(NumberOption(_("Max age"), self.max_age, 5, 150, 5))
        self.add_option(
            NumberOption(
                _("Max age of Mother at birth"), self.max_mother_diff, 5, 150, 5
            )
        )
        self.add_option(
            NumberOption(
                _("Max age of Father at birth"), self.max_father_diff, 5, 150, 5
            )
        )

    def save_options(self):
        self.max_age = int(self.get_option(_("Max age")).get_value())
        self.max_mother_diff = int(
            self.get_option(_("Max age of Mother at birth")).get_value()
        )
        self.max_father_diff = int(
            self.get_option(_("Max age of Father at birth")).get_value()
        )

    def on_load(self):
        if len(self.gui.data) == 3:
            self.max_age = int(self.gui.data[0])
            self.max_mother_diff = int(self.gui.data[1])
            self.max_father_diff = int(self.gui.data[2])

    def save_update_options(self, widget=None):
        self.max_age = int(self.get_option(_("Max age")).get_value())
        self.max_mother_diff = int(
            self.get_option(_("Max age of Mother at birth")).get_value()
        )
        self.max_father_diff = int(
            self.get_option(_("Max age of Father at birth")).get_value()
        )
        self.gui.data = [self.max_age, self.max_mother_diff, self.max_father_diff]
        self.update()

    def main(self):
        for widget in self.vbox.get_children():
            self.vbox.remove(widget)
        if not self.dbstate.is_open():
            return
        age_dict = defaultdict(int)
        mother_dict = defaultdict(int)
        father_dict = defaultdict(int)
        age_handles = defaultdict(list)
        mother_handles = defaultdict(list)
        father_handles = defaultdict(list)
        text = ""
        count = 0
        for person in self.dbstate.db.iter_people():
            if count % 300 == 0:
                yield True
            # if birth_date and death_date, compute age
            birth_date = self.get_date("BIRTH", person)
            death_date = self.get_date("DEATH", person)
            if birth_date:
                if death_date:
                    age = (death_date - birth_date).tuple()[0]
                    if age >= 0:
                        age_dict[age] += 1
                        age_handles[age].append(person.handle)

                # for each parent m/f:
                mother, father = self.get_birth_parents(person)
                if mother:
                    bdate = self.get_date("BIRTH", mother)
                    if bdate:
                        diff = (birth_date - bdate).tuple()[0]
                        if diff >= 0:
                            mother_dict[diff] += 1
                            mother_handles[diff].append(mother.handle)
                if father:
                    bdate = self.get_date("BIRTH", father)
                    if bdate:
                        diff = (birth_date - bdate).tuple()[0]
                        if diff >= 0:
                            father_dict[diff] += 1
                            father_handles[diff].append(father.handle)

            count += 1

        self.create_histogram(
            age_dict,
            age_handles,
            _("Lifespan Age Distribution"),
            _("Age"),
            5,
            self.max_age,
        )
        self.create_histogram(
            father_dict,
            father_handles,
            _("Father - Child Age Diff Distribution"),
            _("Diff"),
            5,
            self.max_father_diff,
        )
        self.create_histogram(
            mother_dict,
            mother_handles,
            _("Mother - Child Age Diff Distribution"),
            _("Diff"),
            5,
            self.max_mother_diff,
        )

    def get_date(self, event_type, person):
        """
        Find the birth or death date of a given person.
        """
        if event_type == "BIRTH":
            ref = person.get_birth_ref()
        else:
            ref = person.get_death_ref()
        if ref:
            event = self.dbstate.db.get_event_from_handle(ref.ref)
            date = event.get_date_object()
            if date.is_valid():
                return date
        return None

    def get_birth_parents(self, person):
        """
        Find the biological parents of a given person.
        """
        m_handle = None
        f_handle = None
        family_list = person.get_parent_family_handle_list()
        for family_handle in family_list:
            family = self.dbstate.db.get_family_from_handle(family_handle)
            if family:
                childrel = [
                    (ref.get_mother_relation(), ref.get_father_relation())
                    for ref in family.get_child_ref_list()
                    if ref.ref == person.handle
                ]
                if childrel[0][0] == ChildRefType.BIRTH:
                    m_handle = family.get_mother_handle()
                if childrel[0][1] == ChildRefType.BIRTH:
                    f_handle = family.get_father_handle()
        mother = None
        father = None
        if m_handle:
            mother = self.dbstate.db.get_person_from_handle(m_handle)
        if f_handle:
            father = self.dbstate.db.get_person_from_handle(f_handle)
        return mother, father

    def compute_stats(self, data):
        """
        Create a table of statistics based on a dictionary of data.
        """
        keys = sorted(data)
        count = sum(data.values())
        sumval = sum(k * data[k] for k in data)
        minval = min(keys)
        maxval = max(keys)
        median = 0
        average = 0
        if count > 0:
            current = 0
            for k in keys:
                if current + data[k] > count / 2:
                    median = k
                    break
                current += data[k]
            average = sumval / float(count)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label(label=_("Statistics") + ":")
        label.set_halign(Gtk.Align.START)
        vbox.pack_start(label, False, False, 0)
        grid = Gtk.Grid()
        grid.set_margin_start(12)
        grid.set_column_spacing(12)
        rows = [
            [_("Total"), "%d" % count],
            [_("Minimum"), "%d" % minval],
            [_("Average"), glocale.format_string("%.1f", average)],
            [_("Median"), "%d" % median],
            [_("Maximum"), "%d" % maxval],
        ]
        for row, value in enumerate(rows):
            label1 = Gtk.Label(label=value[0] + ":")
            label1.set_halign(Gtk.Align.START)
            grid.attach(label1, 0, row, 1, 1)
            label2 = Gtk.Label(label=value[1])
            label2.set_halign(Gtk.Align.END)
            grid.attach(label2, 1, row, 1, 1)
        vbox.pack_start(grid, False, False, 0)
        vbox.show_all()

        return vbox

    def create_histogram(self, data, handles, title, column, interval, max_val):
        """
        Create a histogram based on a dictionary of data, like:
        data = {12: 4, 20: 6, 35: 13, 50: 5}
        where the key is the age, and the value stored is the count.
        """
        if len(data) == 0:
            return

        buckets = [0] * (int(max_val / interval) + 1)
        handle_data = defaultdict(list)
        for value, count in data.items():
            if value > max_val:
                buckets[int(max_val / interval)] += count
                handle_data[int(max_val / interval)].extend(handles[value])
            else:
                buckets[int(value / interval)] += count
                handle_data[int(value / interval)].extend(handles[value])

        labels = []
        for i in range(int(max_val / interval)):
            labels.append(
                "%d-%d"
                % (
                    i * interval,
                    (i + 1) * interval,
                )
            )
        labels.append("%d+" % ((i + 1) * interval,))

        hist = Histogram()
        hist.set_title(title)
        hist.set_bucket_axis(column)
        hist.set_value_axis("%")
        hist.set_values(buckets)
        hist.set_labels(labels)
        hist.set_tooltip(_("Double-click to see %d people"))
        hist.set_highlight([len(labels) - 1])
        hist.connect("clicked", self.on_bar_clicked, handle_data)
        hist.show()
        self.vbox.pack_start(hist, True, True, 0)

        stats = self.compute_stats(data)
        self.vbox.pack_start(stats, False, False, 0)

    def on_bar_clicked(self, _dummy, value, handle_data):
        """
        Called when a histogram bar is double-clicked.
        """
        run_quick_report_by_name(
            self.gui.dbstate,
            self.gui.uistate,
            "filterbyname",
            "list of people",
            handles=handle_data[value],
        )
