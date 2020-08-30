# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2009       Gary Burton
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
from html import escape

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.datehandler import get_date
from gramps.gen.lib import EventType
from gramps.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gramps.gen.plug.menu import (NumberOption, BooleanOption,
                                  EnumeratedListOption)
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
ngettext = glocale.translation.ngettext # else "nearby" comments are ignored

#------------------------------------------------------------------------
#
# PedigreeGramplet class
#
#------------------------------------------------------------------------
class PedigreeGramplet(Gramplet):
    def init(self):
        self.set_text(_("No Family Tree loaded."))
        self.set_tooltip(_("Move mouse over links for options"))
        self.set_use_markup(True)
        self.max_generations = 100
        self.show_dates = 1
        self.box_mode = "UTF"

    def build_options(self):
        self.add_option(NumberOption(_("Max generations"),
                                     self.max_generations, 1, 100))
        self.add_option(BooleanOption(_("Show dates"), bool(self.show_dates)))
        elist = EnumeratedListOption(_("Line type"), self.box_mode)
        elist.add_item("UTF", "UTF")
        elist.add_item("ASCII", "ASCII")
        self.add_option(elist)

    def save_options(self):
        self.max_generations = int(self.get_option(_("Max generations")).get_value())
        self.show_dates = int(self.get_option(_("Show dates")).get_value())
        self.box_mode = self.get_option(_("Line type")).get_value()

    def on_load(self):
        if len(self.gui.data) == 3:
            self.max_generations = int(self.gui.data[0])
            self.show_dates = int(self.gui.data[1])
            self.box_mode = self.gui.data[2] # "ASCII" or "UTF"

    def save_update_options(self, widget=None):
        self.max_generations = int(self.get_option(_("Max generations")).get_value())
        self.show_dates = int(self.get_option(_("Show dates")).get_value())
        self.box_mode = self.get_option(_("Line type")).get_value()
        self.gui.data = [self.max_generations, self.show_dates, self.box_mode]
        self.update()

    def db_changed(self):
        """
        If a person or family changes, the ancestors of active person might have
        changed.
        """
        self.connect(self.dbstate.db, 'person-add', self.update)
        self.connect(self.dbstate.db, 'person-delete', self.update)
        self.connect(self.dbstate.db, 'family-add', self.update)
        self.connect(self.dbstate.db, 'family-delete', self.update)
        self.connect(self.dbstate.db, 'person-rebuild', self.update)
        self.connect(self.dbstate.db, 'family-rebuild', self.update)

    def active_changed(self, handle):
        self.update()

    def get_boxes(self, generation, what):
        retval = ""
        if self.box_mode == "UTF":
            space = "  "
        elif self.box_mode == "ASCII":
            space = "    "
        space_len = len(space) + 2
        for i in range(generation+1):
            if self._boxes[i]:
                retval += space + "|"
            else:
                retval += space + " "
        if retval[-1] == ' ':
            if what == 'sf':
                retval = retval[:-space_len] + "/"
            elif what == 'sm':
                retval = retval[:-space_len] + "\\"
        elif retval.endswith("|" + space + "|"):
            retval = retval[:-space_len] + "+"
        if self.box_mode == "UTF":
            retval += "-"
            retval = retval.replace("\\", "\u2514")
            retval = retval.replace("-", "\u2500")
            retval = retval.replace("|", "\u2502")
            retval = retval.replace("/", "\u250c")
        elif self.box_mode == "ASCII":
            retval += "--"
        return retval

    def set_box(self, pos, value):
        self._boxes[pos] = value

    def process_person(self, handle, generation, what):
        if generation > self.max_generations:
            return
        person = self.dbstate.db.get_person_from_handle(handle)
        family_list = person.get_parent_family_handle_list()
        if what == "f":
            if len(family_list) > 0:
                family = self.dbstate.db.get_family_from_handle(family_list[0])
                father = family.get_father_handle()
                mother = family.get_mother_handle()
                if father:
                    self.process_person(father, generation + 1, "f")
                    self.set_box(generation, 1)
                    self.process_person(father, generation + 1, "sf")
                    self.process_person(father, generation + 1, "m")
                elif mother:
                    self.set_box(generation, 1)
        elif what[0] == "s":
            boxes = self.get_boxes(generation, what)
            if what[-1] == 'f':
                if self.box_mode == "UTF":
                    boxes = boxes.replace("+", "\u250c")
                else:
                    boxes = boxes.replace("+", "/")
            else:
                if self.box_mode == "UTF":
                    boxes = boxes.replace("+", "\u2514")
                else:
                    boxes = boxes.replace("+", "\\")
            self.append_text(boxes)
            self.link(name_displayer.display_name(person.get_primary_name()),
                      'Person', person.handle,
                      tooltip=_("Click to make active\n") + \
                          _("Right-click to edit"))
            if self.show_dates:
                self.append_text(" ")
                self.render_text(self.info_string(person))
            self.append_text("\n")
            if generation not in self._generations:
                self._generations[generation] = []
            self._generations[generation].append(handle)
        elif what == "a":
            if self.box_mode == "UTF":
                self.append_text("o" + ("\u2500" * 3))
            elif self.box_mode == "ASCII":
                self.append_text("o---")
            self.append_text("%s  " % name_displayer.display_name(person.get_primary_name()))
            if self.show_dates:
                self.render_text(self.info_string(person))
            self.append_text("\n")
            if generation not in self._generations:
                self._generations[generation] = []
            self._generations[generation].append(handle)
        elif what == "m":
            if len(family_list) > 0:
                family = self.dbstate.db.get_family_from_handle(family_list[0])
                mother = family.get_mother_handle()
                if mother:
                    self.process_person(mother, generation + 1, "f")
                    self.process_person(mother, generation + 1, "sm")
                    self.set_box(generation, 0)
                    self.process_person(mother, generation + 1, "m")
            self.set_box(generation, 0) # regardless, turn off line if on

    def info_string(self, person):
        birth = get_birth_or_fallback(self.dbstate.db, person)
        if birth and birth.get_type() != EventType.BIRTH:
            sdate = get_date(birth)
            if sdate:
                bdate = "<i>%s</i>" % escape(sdate)
            else:
                bdate = ""
        elif birth:
            bdate = escape(get_date(birth))
        else:
            bdate = ""

        death = get_death_or_fallback(self.dbstate.db, person)
        if death and death.get_type() != EventType.DEATH:
            sdate = get_date(death)
            if sdate:
                ddate = "<i>%s</i>" % escape(sdate)
            else:
                ddate = ""
        elif death:
            ddate = escape(get_date(death))
        else:
            ddate = ""

        if bdate and ddate:
            value = _("(b. %(birthdate)s, d. %(deathdate)s)") % {
                'birthdate' : bdate,
                'deathdate' : ddate
                }
        elif bdate:
            value = _("(b. %s)") % (bdate)
        elif ddate:
            value = _("(d. %s)") % (ddate)
        else:
            value = ""
        return value

    def main(self): # return false finishes
        """
        Generator which will be run in the background.
        """
        self._boxes = [0] * (self.max_generations + 1)
        self._generations = {}
        self.gui.buffer.set_text("")
        active_handle = self.get_active('Person')
        if active_handle is None:
            return
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        #no wrap in Gramplet
        self.no_wrap()
        if active_person is None:
            return
        self.process_person(active_person.handle, 1, "f") # father
        self.process_person(active_person.handle, 0, "a") # active #FIXME: should be 1?
        self.process_person(active_person.handle, 1, "m") # mother
        gens = sorted(self._generations)
        self.append_text(_("\nBreakdown by generation:\n"))
        all = [active_person.handle]
        percent_sign = _("%", "percent sign or text string")
        for g in gens:
            yield True
            count = len(self._generations[g])
            handles = self._generations[g]
            self.append_text("     ")
            if g == 0:
                self.link(_("Generation 1"), 'PersonList', handles,
                          tooltip=_("Double-click to see people in generation"))
                percent = glocale.format('%.2f', 100) + percent_sign
                self.append_text(_(" has 1 of 1 individual (%(percent)s complete)\n") %  {'percent': percent})
            else:
                all.extend(handles)
                self.link(_("Generation %d") % g, 'PersonList', handles,
                          tooltip=_("Double-click to see people in generation %d") % g)
                percent = glocale.format('%.2f', float(count)/2**(g-1) * 100) + percent_sign
                self.append_text(
                    # translators: leave all/any {...} untranslated
                    ngettext(" has {count_person} of {max_count_person} "
                             "individuals ({percent} complete)\n",
                             " has {count_person} of {max_count_person} "
                             "individuals ({percent} complete)\n", 2**(g-1)
                            ).format(count_person=count,
                                     max_count_person=2**(g-1),
                                     percent=percent))
        self.link(_("All generations"), 'PersonList', all,
                  tooltip=_("Double-click to see all generations"))
        self.append_text(
            # translators: leave all/any {...} untranslated
            ngettext(" have {number_of} individual\n",
                     " have {number_of} individuals\n", len(all)
                    ).format(number_of=len(all)))
        # Set to a fixed font
        if self.box_mode == "UTF":
            start, end = self.gui.buffer.get_bounds()
            self.gui.buffer.apply_tag_by_name("fixed", start, end)
        self.append_text("", scroll_to="begin")
