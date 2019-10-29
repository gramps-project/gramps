#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Douglas S. Blank
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

This Gramplet shows textual distributions of age breakdowns of various types.
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from collections import defaultdict

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.lib import ChildRefType
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class AgeStatsGramplet(Gramplet):

    def init(self):
        self.max_age = 110
        self.max_mother_diff = 40
        self.max_father_diff = 60
        self.chart_width = 60

    def build_options(self):
        from gramps.gen.plug.menu import NumberOption
        self.add_option(NumberOption(_("Max age"),
                                     self.max_age, 5, 150, 5))
        self.add_option(NumberOption(_("Max age of Mother at birth"),
                                     self.max_mother_diff, 5, 150, 5))
        self.add_option(NumberOption(_("Max age of Father at birth"),
                                     self.max_father_diff, 5, 150, 5))
        self.add_option(NumberOption(_("Chart width"),
                                     self.chart_width, 45, 150))

    def save_options(self):
        self.max_age = int(self.get_option(_("Max age")).get_value())
        self.max_mother_diff = int(self.get_option(_("Max age of Mother at birth")).get_value())
        self.max_father_diff = int(self.get_option(_("Max age of Father at birth")).get_value())
        self.chart_width = int(self.get_option(_("Chart width")).get_value())

    def on_load(self):
        self.no_wrap()
        tag = self.gui.buffer.create_tag("fixed")
        tag.set_property("font", "Courier 8")
        if len(self.gui.data) == 4:
            self.max_age = int(self.gui.data[0])
            self.max_mother_diff = int(self.gui.data[1])
            self.max_father_diff = int(self.gui.data[2])
            self.chart_width = int(self.gui.data[3])

    def save_update_options(self, widget=None):
        self.max_age = int(self.get_option(_("Max age")).get_value())
        self.max_mother_diff = int(self.get_option(_("Max age of Mother at birth")).get_value())
        self.max_father_diff = int(self.get_option(_("Max age of Father at birth")).get_value())
        self.chart_width = int(self.get_option(_("Chart width")).get_value())
        self.gui.data = [self.max_age,
                         self.max_mother_diff,
                         self.max_father_diff,
                         self.chart_width]
        self.update()

    def db_changed(self):
        self.update()

    def main(self):
        self.clear_text()
        age_dict = defaultdict(int)
        mother_dict = defaultdict(int)
        father_dict = defaultdict(int)
        age_handles = [[] for i in range(self.max_age)]
        mother_handles = [[] for i in range(self.max_mother_diff)]
        father_handles = [[] for i in range(self.max_father_diff)]
        text = ""
        count = 0
        for p in self.dbstate.db.iter_people():
            if count % 300 == 0:
                yield True
            # if birth_date and death_date, compute age
            birth_ref = p.get_birth_ref()
            birth_date = None
            if birth_ref:
                birth_event = self.dbstate.db.get_event_from_handle(birth_ref.ref)
                birth_date = birth_event.get_date_object()
            death_ref = p.get_death_ref()
            death_date = None
            if death_ref:
                death_event = self.dbstate.db.get_event_from_handle(death_ref.ref)
                death_date = death_event.get_date_object()
            if death_date and birth_date and birth_date.get_year() != 0:
                age = death_date.get_year() - birth_date.get_year()
                if age >= 0 and age < self.max_age:
                    age_dict[age] += 1
                    age_handles[age].append(p.handle)
                #else:
                #    print "Age out of range: %d for %s" % (age,
                #                                           p.get_primary_name().get_first_name()
                #                                           + " " + p.get_primary_name().get_surname())
            # for each parent m/f:
            family_list = p.get_parent_family_handle_list()
            for family_handle in family_list:
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family:
                    childrel = [(ref.get_mother_relation(),
                                 ref.get_father_relation()) for ref in
                                family.get_child_ref_list()
                                if ref.ref == p.handle] # get first, if more than one
                    if childrel[0][0] == ChildRefType.BIRTH:
                        m_handle = family.get_mother_handle()
                    else:
                        m_handle = None
                    if childrel[0][1] == ChildRefType.BIRTH:
                        f_handle = family.get_father_handle()
                    else:
                        f_handle = None
                    # if they have a birth_date, compute difference each m/f
                    if f_handle:
                        f = self.dbstate.db.get_person_from_handle(f_handle)
                        bref = f.get_birth_ref()
                        if bref:
                            bevent = self.dbstate.db.get_event_from_handle(bref.ref)
                            bdate = bevent.get_date_object()
                            if bdate and birth_date and birth_date.get_year() != 0:
                                diff = birth_date.get_year() - bdate.get_year()
                                if diff >= 0 and diff < self.max_father_diff:
                                    father_dict[diff] += 1
                                    father_handles[diff].append(f_handle)
                                #else:
                                #    print "Father diff out of range: %d for %s" % (diff,
                                #                                                   p.get_primary_name().get_first_name()
                                #                                                   + " " + p.get_primary_name().get_surname())
                    if m_handle:
                        m = self.dbstate.db.get_person_from_handle(m_handle)
                        bref = m.get_birth_ref()
                        if bref:
                            bevent = self.dbstate.db.get_event_from_handle(bref.ref)
                            bdate = bevent.get_date_object()
                            if bdate and birth_date and birth_date.get_year() != 0:
                                diff = birth_date.get_year() - bdate.get_year()
                                if diff >= 0 and diff < self.max_mother_diff:
                                    mother_dict[diff] += 1
                                    mother_handles[diff].append(m_handle)
                                #else:
                                #    print "Mother diff out of range: %d for %s" % (diff,
                                #                                                   p.get_primary_name().get_first_name()
                                #                                                   + " " + p.get_primary_name().get_surname())
            count += 1
        width = self.chart_width
        graph_width = width - 8
        self.create_bargraph(age_dict, age_handles, _("Lifespan Age Distribution"), _("Age"), graph_width, 5, self.max_age)
        self.create_bargraph(father_dict, father_handles, _("Father - Child Age Diff Distribution"), _("Diff"), graph_width, 5, self.max_father_diff)
        self.create_bargraph(mother_dict, mother_handles, _("Mother - Child Age Diff Distribution"), _("Diff"), graph_width, 5, self.max_mother_diff)
        start, end = self.gui.buffer.get_bounds()
        self.gui.buffer.apply_tag_by_name("fixed", start, end)
        self.append_text("", scroll_to="begin")

    def ticks(self, width, start=0, stop=100, fill=" "):
        """ Returns the tickmark numbers for a graph axis """
        count = int(width / 10.0)
        retval = "%-3d" % start
        space = int((width - count * 3) / float(count - 1))
        incr = (stop - start) / float(count - 1)
        lastincr = 0
        for i in range(count - 2):
            retval += " " * space
            newincr = int(start + (i + 1) * incr)
            if newincr != lastincr:
                retval += "%3d" % newincr
            else:
                retval += " | "
            lastincr = newincr
        rest = width - len(retval) - 3 + 1
        retval += " " * rest
        retval += "%3d" % int(stop)
        return retval

    def format(self, text, width, align="left", borders="||", fill=" "):
        """ Returns a formatted string for nice, fixed-font display """
        if align == "center":
            text = text.center(width, fill)
        elif align == "left":
            text = (text + (fill * width))[:width]
        elif align == "right":
            text = ((fill * width) + text)[-width:]
        if borders[0] is not None:
            text = borders[0] + text
        if borders[1] is not None:
            text = text + borders[1]
        return text

    def compute_stats(self, hash):
        """ Returns the statistics of a dictionary of data """
        #print "compute_stats", hash
        hashkeys = sorted(hash)
        count = sum(hash.values())
        sumval = sum(k * hash[k] for k in hash)
        minval = min(hashkeys)
        maxval = max(hashkeys)
        median = 0
        average = 0
        if count > 0:
            current = 0
            for k in hashkeys:
                if current + hash[k] > count/2:
                    median = k
                    break
                current += hash[k]
            average = sumval/float(count)
        retval = _("Statistics") + ":\n"
        retval += "  " + _("Total") + ": %d\n" % count
        retval += "  " + _("Minimum") + ": %d\n" % minval
        retval += "  " + _("Average") + glocale.format_string(": %.1f\n", average)
        retval += "  " + _("Median") + ": %d\n" % median
        retval += "  " + _("Maximum") + ": %d\n" % maxval
        return retval

    def make_handles_set(self, min, max, handles):
        retval = []
        for i in range(min, max):
            try:
                retval.extend(handles[i])
            except:
                pass
        return retval

    def create_bargraph(self, hash, handles, title, column, graph_width, bin_size, max_val):
        """
        Create a bargraph based on the data in hash. hash is a dict, like:
        hash = {12: 4, 20: 6, 35: 13, 50: 5}
        where the key is the age, and the value stored is the count.
        """
        # first, binify:
        #print "create_bargraph", hash
        bin = [0] * int(max_val/bin_size)
        for value, hash_value in hash.items():
            bin[int(value/bin_size)] += hash_value
        text = ""
        max_bin = float(max(bin))
        if max_bin != 0:
            i = 0
            self.append_text(
                "--------" +
                self.format("", graph_width-4, fill="-", borders="++") +
                "-----\n")
            self.append_text(
                column.center(8) +
                self.format(title, graph_width-4, align="center") +
                "  %  " + "\n")
            self.append_text(
                "--------" +
                self.format("", graph_width-4, fill="-", borders="++") +
                "-----\n")
            for bin in bin:
                self.append_text((" %3d-%3d" % (i * 5, (i+1)* 5,)))
                selected = self.make_handles_set(i * 5, (i+1) *5, handles)
                self.link(self.format("X" * int(bin/max_bin * (graph_width-4)),
                                      graph_width-4),
                          'PersonList',
                          selected,
                          tooltip=_("Double-click to see %d people") %
                          len(selected))
                procent = (float(len(selected)) /
                           (float(sum(hash.values())))*100)
                self.append_text(glocale.format("%#5.2f", procent))
                self.append_text("\n")
                i += 1
            self.append_text(
                "--------" +
                self.format("", graph_width-4, fill="-", borders="++") +
                "-----\n")
            self.append_text(
                "    %   " +
                self.ticks(graph_width-4, start=0,
                           stop=int(max_bin/(float(sum(hash.values())))*100)) +
                "\n\n")
            self.append_text(self.compute_stats(hash))
