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
# Python modules
#
#------------------------------------------------------------------------
import cgi

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from DataViews import register, Gramplet
from TransUtils import sgettext as _
from BasicUtils import name_displayer
from ReportBase import ReportUtils
import DateHandler
import gen

#------------------------------------------------------------------------
#
# Gramplet class
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
        from gen.plug.menu import NumberOption
        self.add_option(NumberOption(_("Max generations"), 
                                     self.max_generations, 1, 100))

    def save_options(self):
        self.max_generations = int(self.get_option(_("Max generations")).get_value())

    def on_load(self):
        if len(self.gui.data) > 0:
            self.max_generations = int(self.gui.data[0])
        if len(self.gui.data) > 1:
            self.show_dates = int(self.gui.data[1])
        if len(self.gui.data) > 2:
            self.box_mode = self.gui.data[2] # ASCII or UTF

    def on_save(self):
        self.gui.data = [self.max_generations, self.show_dates, self.box_mode]

    def db_changed(self):
        """
        If a person or family changes, the ancestors of active person might have
        changed.
        """
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('family-add', self.update)
        self.dbstate.db.connect('family-delete', self.update)
        self.dbstate.db.connect('person-rebuild', self.update)
        self.dbstate.db.connect('family-rebuild', self.update)

    def active_changed(self, handle):
        self.update()

    def get_boxes(self, generation, what):
        retval = u""
        if self.box_mode == "UTF":
            space = u"  "
        elif self.box_mode == "ASCII":
            space = u"    "
        space_len = len(space) + 2
        for i in range(generation+1):
            if self._boxes[i]:
                retval += space + u"|"
            else:
                retval += space + u" "
        if retval[-1] == u' ':
            if what == 'sf':
                retval = retval[:-space_len] + u"/"
            elif what == 'sm':
                retval = retval[:-space_len] + u"\\"
        elif retval.endswith(u"|" + space + u"|"):
            retval = retval[:-space_len] + u"+"
        if self.box_mode == "UTF":
            retval += u"-"
            retval = retval.replace(u"\\", u"\u2514")
            retval = retval.replace(u"-",  u"\u2500")
            retval = retval.replace(u"|",  u"\u2502")
            retval = retval.replace(u"/",  u"\u250c")
        elif self.box_mode == "ASCII":
            retval += u"--"
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
                    boxes = boxes.replace("+", u"\u250c")
                else:
                    boxes = boxes.replace("+", u"/")
            else:
                if self.box_mode == "UTF":
                    boxes = boxes.replace("+", u"\u2514")
                else:
                    boxes = boxes.replace("+", u"\\")
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
                self.append_text(u"o" + (u"\u2500" * 3))
            elif self.box_mode == "ASCII":
                self.append_text(u"o---")
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
        birth = ReportUtils.get_birth_or_fallback(self.dbstate.db, person)
        if birth and birth.get_type != gen.lib.EventType.BIRTH:
            sdate = DateHandler.get_date(birth)
            if sdate:
                bdate  = "<i>%s</i>" % cgi.escape(sdate)
            else:
                bdate = ""
        elif birth:
            bdate  = cgi.escape(DateHandler.get_date(birth))
        else:
            bdate = ""

        death = ReportUtils.get_death_or_fallback(self.dbstate.db, person)
        if death and death.get_type != gen.lib.EventType.DEATH:
            sdate = DateHandler.get_date(death)
            if sdate:
                ddate  = "<i>%s</i>" % cgi.escape(sdate)
            else:
                ddate = ""
        elif death:
            ddate  = cgi.escape(DateHandler.get_date(death))
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
        active_person = self.dbstate.get_active_person()
        if not active_person:
            return False
        #no wrap in Gramplet
        self.no_wrap()
        self.process_person(active_person.handle, 1, "f") # father
        self.process_person(active_person.handle, 0, "a") # active #FIXME: should be 1?
        self.process_person(active_person.handle, 1, "m") # mother
        gens = self._generations.keys()
        gens.sort()
        self.append_text(_("\nBreakdown by generation:\n"))
        all = [active_person.handle]
        for g in gens:
            count = len(self._generations[g])
            handles = self._generations[g]
            self.append_text("     ")
            if g == 0:
                self.link(_("Generation 1"), 'PersonList', handles, 
                          tooltip=_("Double-click to see people in generation"))
                self.append_text(_(" has 1 of 1 individual (100.00% complete)\n"))
            else:
                all.extend(handles)
                self.link(_("Generation %d") % g, 'PersonList', handles,
                          tooltip=_("Double-click to see people in generation"))
                self.append_text(_(" has %d of %d individuals (%.2f%% complete)\n") % 
                                 (count, 2**(g-1), float(count)/2**(g-1) * 100))
        self.link(_("All generations"), 'PersonList', all,
                  tooltip=_("Double-click to see all generations"))
        self.append_text(_(" have %d individuals\n") % len(all))
        # Set to a fixed font
        if self.box_mode == "UTF":
            start, end = self.gui.buffer.get_bounds()
            self.gui.buffer.apply_tag_by_name("fixed", start, end)
        self.append_text("", scroll_to="begin")

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(type="gramplet", 
         name="Pedigree Gramplet", 
         tname=_("Pedigree Gramplet"), 
         height=300,
         content = PedigreeGramplet,
         title=_("Pedigree"),
         expand=True,
         detached_width = 600,
         detached_height = 400,
         )

