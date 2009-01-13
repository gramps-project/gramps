# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

import sys
import re
import urllib
import posixpath
import cgi

from BasicUtils import name_displayer
from DataViews import register, Gramplet
from PluginUtils import *
from QuickReports import run_quick_report_by_name, get_quick_report_list
from ReportBase import ReportUtils
from gen.utils import set_birth_death_index
from TransUtils import sgettext as _
from Utils import media_path_full
import Config
import DateHandler
import gen.lib
import Errors

from ReportBase  import (CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY,
                         CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE, 
                         CATEGORY_QR_MISC, CATEGORY_QR_PLACE, 
                         CATEGORY_QR_REPOSITORY)

#
# Hello World, in Gramps Gramplets
#
# First, you need a function or class that takes a single argument
# a GuiGramplet:

#from DataViews import register
#def init(gui):
#    gui.set_text("Hello world!")

# In this function, you can do some things to update the gramplet,
# like set text of the main scroll window.

# Then, you need to register the gramplet:

#register(type="gramplet", # case in-senstitive keyword "gramplet"
#         name="Hello World Gramplet", # gramplet name, unique among gramplets
#         height = 20,
#         content = init, # function/class; takes guigramplet
#         title="Sample Gramplet", # default title, user changeable
#         )

# There are a number of arguments that you can provide, including:
# name, height, content, title, expand, state, data

# Here is a Gramplet object. It has a number of method possibilities:
#  init- run once, on construction
#  active_changed- run when active-changed is triggered
#  db_changed- run when db-changed is triggered
#  main- run once per db change, main process (a generator)

# You should call update() to run main; don't call main directly

class CalendarGramplet(Gramplet):
    def init(self):
        import gtk
        self.set_tooltip(_("Double-click a day for details"))
        self.gui.calendar = gtk.Calendar()
        self.gui.calendar.connect('day-selected-double-click', self.double_click)
        self.gui.calendar.connect('month-changed', self.refresh)
        self.dbstate.db.connect('person-rebuild', self.update)

        db_signals = ['event-add',
                      'event-update', 
                      'event-delete', 
                      'event-rebuild',
                      ]
        for signal in db_signals:
            self.dbstate.db.connect(signal, lambda *args: self.run_update(signal, *args))

        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.calendar)
        self.gui.calendar.show()
        self.birthdays = True
        self.dates = {}

    def db_changed(self):
        self.update()

    def run_update(self, signal, *args):
        self.update()

    def refresh(self, *obj):
        self.gui.calendar.freeze()
        self.gui.calendar.clear_marks()
        year, month, day = self.gui.calendar.get_date()
        for date in self.dates:
            if ((date[0] == year) and
                (date[1] == month + 1) and
                (date[2] > 0 and date[2] <= day)):
                self.gui.calendar.mark_day(date[2])
        self.gui.calendar.thaw()

    def main(self):
        self.dates = {}
        # for each day in events
        people = self.gui.dbstate.db.get_person_handles(sort_handles=False)
        cnt = 0
        for person_handle in people:
            if cnt % 350 == 0:
                yield True
            person = self.gui.dbstate.db.get_person_from_handle(person_handle)
            birth_ref = person.get_birth_ref()
            birth_date = None
            if birth_ref:
                birth_event = self.gui.dbstate.db.get_event_from_handle(birth_ref.ref)
                birth_date = birth_event.get_date_object()
            if self.birthdays and birth_date is not None:
                year = birth_date.get_year()
                month = birth_date.get_month()
                day = birth_date.get_day()
                #age = self.year - year
                self.dates[(year, month, day)] = birth_event.handle
            cnt += 1
        self.refresh()

    def double_click(self, obj):
        # bring up events on this day
        year, month, day = self.gui.calendar.get_date()
        month += 1
        date = gen.lib.Date()
        date.set_yr_mon_day(year, month, day)
        run_quick_report_by_name(self.gui.dbstate, 
                                 self.gui.uistate, 
                                 'onthisday', 
                                 date)

class LogGramplet(Gramplet):
    def init(self):
        self.set_tooltip(_("Click name to change active\nDouble-click name to edit"))
        self.set_text(_("Log for this Session"))
        self.gui.force_update = True # will always update, even if minimized
        self.last_log = None
        self.append_text("\n")

    def db_changed(self):
        self.append_text("Opened data base -----------\n")
        self.dbstate.db.connect('person-add', 
                                lambda handles: self.log(_('Person'), _('Added'), handles))
        self.dbstate.db.connect('person-delete', 
                                lambda handles: self.log(_('Person'), _('Deleted'), handles))
        self.dbstate.db.connect('person-update', 
                                lambda handles: self.log(_('Person'), _('Edited'), handles))
        self.dbstate.db.connect('family-add', 
                                lambda handles: self.log(_('Family'), _('Added'), handles))
        self.dbstate.db.connect('family-delete', 
                                lambda handles: self.log(_('Family'), _('Deleted'), handles))
        self.dbstate.db.connect('family-update', 
                                lambda handles: self.log(_('Family'), _('Added'), handles))
    
    def active_changed(self, handle):
        self.log(_('Person'), _('Selected'), [handle])

    def log(self, ltype, action, handles):
        for handle in set(handles):
            if self.last_log == (ltype, action, handle):
                continue
            self.last_log = (ltype, action, handle)
            self.append_text("%s: " % action)
            if ltype == _("Person"):
                person = self.dbstate.db.get_person_from_handle(handle)
                name = name_displayer.display(person)
            elif ltype == _("Family"):
                family = self.dbstate.db.get_family_from_handle(handle)
                father_name = _("unknown")
                mother_name = _("unknown")
                if family:
                    father_handle = family.get_father_handle()
                    if father_handle:
                        father = self.dbstate.db.get_person_from_handle(father_handle)
                        if father:
                            father_name = name_displayer.display(father)
                    mother_handle = family.get_mother_handle()
                    if mother_handle:
                        mother = self.dbstate.db.get_person_from_handle(mother_handle)
                        mother_name = name_displayer.display(mother)
                name = _("%s and %s") % (mother_name, father_name)
            self.link(name, ltype, handle)
            self.append_text("\n")

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
        people = self.dbstate.db.get_person_handles(sort_handles=False)
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
            if cnt % 350 == 0:
                yield True
            cnt += 1
        total_people = cnt
        surname_sort = []
        total = 0
        cnt = 0
        for surname in surnames:
            surname_sort.append( (surnames[surname], surname) )
            total += surnames[surname]
            if cnt % 350 == 0:
                yield True
            cnt += 1
        total_surnames = cnt
        surname_sort.sort(lambda a,b: -cmp(a,b))
        line = 0
        ### All done!
        self.set_text("")
        for (count, surname) in surname_sort:
            if len(surname) == 0:
                text = "%s, %d%% (%d)\n" %  (Config.get(Config.NO_SURNAME_TEXT),
                                             int((float(count)/total) * 100),
                                             count)
            else:
                text = "%s, %d%% (%d)\n" %  (surname, int((float(count)/total) * 100), 
                                             count)
            self.append_text(" %d. " % (line + 1))
            self.link(text, 'Surname', representative_handle[surname])
            line += 1
            if line >= self.top_size:
                break
        self.append_text(("\n" + _("Total unique surnames") + ": %d\n") % 
                         total_surnames)
        self.append_text((_("Total people") + ": %d") % total_people, "begin")
        
def make_tag_size(n, counts, mins=8, maxs=20):
    # return font sizes mins to maxs
    diff = maxs - mins
    # based on counts (biggest to smallest)
    if len(counts) > 1:
        position = diff - (diff * (float(counts.index(n)) / (len(counts) - 1)))
    else:
        position = 0
    return int(position) + mins

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
        people = self.dbstate.db.get_person_handles(sort_handles=False)
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
            if cnt % 350 == 0:
                yield True
            cnt += 1
        total_people = cnt
        surname_sort = []
        total = 0
        cnt = 0
        for surname in surnames:
            surname_sort.append( (surnames[surname], surname) )
            total += surnames[surname]
            if cnt % 350 == 0:
                yield True
            cnt += 1
        total_surnames = cnt
        surname_sort.sort(lambda a,b: -cmp(a,b))
        cloud_names = []
        cloud_values = []
        cnt = 0
        for (count, surname) in surname_sort:
            cloud_names.append( (count, surname) )
            cloud_values.append( count )
            cnt += 1
        cloud_names.sort(lambda a,b: cmp(a[1], b[1]))
        counts = list(set(cloud_values))
        counts.sort()
        counts.reverse()
        line = 0
        ### All done!
        # Now, find out how many we can display without going over top_size:
        totals = {}
        for (count, givensubname) in cloud_names: # givensubname_sort:
            totals[count] = totals.get(count, 0) + 1
        sums = totals.keys()
        sums.sort()
        sums.reverse()
        total = 0
        include_greater_than = 0
        for s in sums:
            if total + totals[s] <= self.top_size:
                total += totals[s]
            else:
                include_greater_than = s
                break
        # Ok, now we can show those counts > include_greater_than:
        print
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

class RelativesGramplet(Gramplet):
    """
    This gramplet gives a list of clickable relatives of the active person.
    Clicking them, changes the active person.
    """
    def init(self):
        self.set_text(_("No Family Tree loaded."))
        self.set_tooltip(_("Click name to make person active\n") +
                         _("Right-click name to edit person"))

    def db_changed(self):
        """
        If person or family changes, the relatives of active person might have
        changed
        """
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('family-add', self.update)
        self.dbstate.db.connect('family-delete', self.update)
        self.dbstate.db.connect('person-rebuild', self.update)
        self.dbstate.db.connect('family-rebuild', self.update)

    def active_changed(self, handle):
        self.update()

    def main(self): # return false finishes
        """
        Generator which will be run in the background.
        """
        self.set_text("")
        database = self.dbstate.db
        active_person = self.dbstate.get_active_person()
        if not active_person:
            return
        name = name_displayer.display(active_person)
        self.append_text(_("Active person: %s") % name)
        self.append_text("\n\n")
        #obtain families
        famc = 0
        for family_handle in active_person.get_family_handle_list():
            famc += 1
            family = database.get_family_from_handle(family_handle)
            if not family: continue
            if active_person.handle == family.get_father_handle():
                spouse_handle = family.get_mother_handle()
            else:
                spouse_handle = family.get_father_handle()
            if spouse_handle:
                spouse = database.get_person_from_handle(spouse_handle)
                spousename = name_displayer.display(spouse)
                text = "%s" %  spousename
                self.append_text(_("%d. Partner: ") % (famc))
                self.link(text, 'Person', spouse_handle)
                self.append_text("\n")
            else:
                self.append_text(_("%d. Partner: Not known") % (famc))
                self.append_text("\n")
            #obtain children
            childc = 0
            for child_ref in family.get_child_ref_list():
                childc += 1
                child = database.get_person_from_handle(child_ref.ref)
                childname = name_displayer.display(child)
                text = "%s" %  childname
                self.append_text("   %d.%-3d: " % (famc, childc))
                self.link(text, 'Person', child_ref.ref)
                self.append_text("\n")
            yield True
        #obtain parent families
        self.append_text("\n")
        self.append_text(_("Parents:"))
        self.append_text("\n")
        famc = 0
        for family_handle in active_person.get_parent_family_handle_list():
            famc += 1
            family = database.get_family_from_handle(family_handle)
            mother_handle = family.get_mother_handle()
            father_handle = family.get_father_handle()
            if mother_handle:
                mother = database.get_person_from_handle(mother_handle)
                mothername = name_displayer.display(mother)
                text = "%s" %  mothername
                self.append_text(_("   %d.a Mother: ") % (famc))
                self.link(text, 'Person', mother_handle)
                self.append_text("\n")
            else:
                self.append_text(_("   %d.a Mother: ") % (famc))
                self.append_text(_("Unknown"))
                self.append_text("\n")
            if father_handle:
                father = database.get_person_from_handle(father_handle)
                fathername = name_displayer.display(father)
                text = "%s" %  fathername
                self.append_text(_("   %d.b Father: ") % (famc))
                self.link(text, 'Person', father_handle)
                self.append_text("\n")
            else:
                self.append_text(_("   %d.b Father: ") % (famc))
                self.append_text(_("Unknown"))
                self.append_text("\n")

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
        # in case we need it:
        tag = self.gui.buffer.create_tag("fixed")
        tag.set_property("font", "Courier 9")

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

class StatsGramplet(Gramplet):
    def init(self):
        self.set_text(_("No Family Tree loaded."))
        self.set_tooltip(_("Double-click item to see matches"))

    def db_changed(self):
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-edit', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('family-add', self.update)
        self.dbstate.db.connect('family-delete', self.update)
        self.dbstate.db.connect('person-rebuild', self.update)
        self.dbstate.db.connect('family-rebuild', self.update)

    def main(self):
        self.set_text(_("Processing..."))
        database = self.dbstate.db
        personList = database.get_person_handles(sort_handles=False)
        familyList = database.get_family_handles()

        with_photos = 0
        total_photos = 0
        incomp_names = 0
        disconnected = 0
        missing_bday = 0
        males = 0
        females = 0
        unknowns = 0
        bytes = 0
        namelist = []
        notfound = []

        pobjects = len(database.get_media_object_handles())
        for photo_id in database.get_media_object_handles():
            photo = database.get_object_from_handle(photo_id)
            fullname = media_path_full(database, photo.get_path())
            try:
                bytes = bytes + posixpath.getsize(fullname)
            except:
                notfound.append(photo.get_path())

        cnt = 0
        for person_handle in personList:
            person = database.get_person_from_handle(person_handle)
            if not person:
                continue
            length = len(person.get_media_list())
            if length > 0:
                with_photos = with_photos + 1
                total_photos = total_photos + length

            person = database.get_person_from_handle(person_handle)
            names = [person.get_primary_name()] + person.get_alternate_names()
            for name in names:
                if name.get_first_name() == "" or name.get_group_name() == "":
                    incomp_names = incomp_names + 1
                if name.get_group_name() not in namelist:
                    namelist.append(name.get_group_name())
            if ((not person.get_main_parents_family_handle()) and 
                (not len(person.get_family_handle_list()))):
                disconnected = disconnected + 1
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = database.get_event_from_handle(birth_ref.ref)
                if not DateHandler.get_date(birth):
                    missing_bday = missing_bday + 1
            else:
                missing_bday = missing_bday + 1
            if person.get_gender() == gen.lib.Person.FEMALE:
                females = females + 1
            elif person.get_gender() == gen.lib.Person.MALE:
                males = males + 1
            else:
                unknowns += 1
            if cnt % 200 == 0:
                yield True
            cnt += 1

        self.clear_text()
        self.append_text(_("Individuals") + "\n")
        self.append_text("----------------------------\n")
        self.link(_("Number of individuals") + ":",
                  'Filter', 'all people')
        self.append_text(" %s" % len(personList))
        self.append_text("\n")
        self.link("%s:" % _("Males"), 'Filter', 'males')
        self.append_text(" %s" % males)
        self.append_text("\n")
        self.link("%s:" % _("Females"), 'Filter', 'females')
        self.append_text(" %s" % females)
        self.append_text("\n")
        self.link("%s:" % _("Individuals with unknown gender"),
                  'Filter', 'people with unknown gender')
        self.append_text(" %s" % unknowns)
        self.append_text("\n")
        self.link("%s:" % _("Individuals with incomplete names"),
                  'Filter', 'people with incomplete names')
        self.append_text(" %s" % incomp_names)
        self.append_text("\n")
        self.link("%s:" % _("Individuals missing birth dates"),
                  'Filter', 'people with missing birth dates')
        self.append_text(" %s" % missing_bday)
        self.append_text("\n")
        self.link("%s:" % _("Disconnected individuals"),
                  'Filter', 'disconnected people')
        self.append_text(" %s" % disconnected)
        self.append_text("\n")
        self.append_text("\n%s\n" % _("Family Information"))
        self.append_text("----------------------------\n")
        self.link("%s:" % _("Number of families"),
                  'Filter', 'all families')
        self.append_text(" %s" % len(familyList))
        self.append_text("\n")
        self.link("%s:" % _("Unique surnames"), 
                  'Filter', 'unique surnames')
        self.append_text(" %s" % len(namelist))
        self.append_text("\n")
        self.append_text("\n%s\n" % _("Media Objects"))
        self.append_text("----------------------------\n")
        self.link("%s:" % _("Individuals with media objects"),
                  'Filter', 'people with media')
        self.append_text(" %s" % with_photos)
        self.append_text("\n")
        self.link("%s:" % _("Total number of media object references"),
                  'Filter', 'media references')
        self.append_text(" %s" % total_photos)
        self.append_text("\n")
        self.link("%s:" % _("Number of unique media objects"),
                  'Filter', 'unique media')
        self.append_text(" %s" % pobjects)
        self.append_text("\n")

        self.link("%s:" % _("Total size of media objects"),
                  'Filter', 'media by size')
        self.append_text(" %d %s" % (bytes, _("bytes")))
        self.append_text("\n")
        self.link("%s:" % _("Missing Media Objects"),
                  'Filter', 'missing media')
        self.append_text(" %s\n" % len(notfound))
        self.append_text("", scroll_to="begin")

class PythonGramplet(Gramplet):
    def init(self):
        self.prompt = ">"
        self.set_tooltip(_("Enter Python expressions"))
        self.env = {"dbstate": self.gui.dbstate,
                    "uistate": self.gui.uistate,
                    "self": self,
                    _("class name|Date"): gen.lib.Date,
                    }
        # GUI setup:
        self.gui.textview.set_editable(True)
        self.set_text("Python %s\n%s " % (sys.version, self.prompt))
        self.gui.textview.connect('key-press-event', self.on_key_press)

    def format_exception(self, max_tb_level=10):
        retval = ''
        cla, exc, trbk = sys.exc_info()
        retval += _("Error") + (" : %s %s" %(cla, exc))
        return retval

    def process_command(self, command):
        # update states, in case of change:
        self.env["dbstate"] = self.gui.dbstate
        self.env["uistate"] = self.gui.uistate
        _retval = None
        if "_retval" in self.env:
            del self.env["_retval"]
        exp1 = """_retval = """ + command
        exp2 = command.strip()
        try:
            _retval = eval(exp2, self.env)
        except:
            try:
                exec exp1 in self.env
            except:
                try:
                    exec exp2 in self.env
                except:
                    _retval = self.format_exception()
        if "_retval" in self.env:
            _retval = self.env["_retval"]
        return _retval

    def on_key_press(self, widget, event):
        import gtk
        if (event.keyval == gtk.keysyms.Home or
            ((event.keyval == gtk.keysyms.a and 
              event.get_state() & gtk.gdk.CONTROL_MASK))): 
            buffer = widget.get_buffer()
            cursor_pos = buffer.get_property("cursor-position")
            iter = buffer.get_iter_at_offset(cursor_pos)
            line_cnt = iter.get_line()
            start = buffer.get_iter_at_line(line_cnt)
            start.forward_chars(2)
            buffer.place_cursor(start)
            return True
        elif (event.keyval == gtk.keysyms.End or 
              (event.keyval == gtk.keysyms.e and 
               event.get_state() & gtk.gdk.CONTROL_MASK)): 
            buffer = widget.get_buffer()
            end = buffer.get_end_iter()
            buffer.place_cursor(end)
            return True
        elif event.keyval == gtk.keysyms.Return: 
            echo = False
            buffer = widget.get_buffer()
            cursor_pos = buffer.get_property("cursor-position")
            iter = buffer.get_iter_at_offset(cursor_pos)
            line_cnt = iter.get_line()
            start = buffer.get_iter_at_line(line_cnt)
            line_len = iter.get_chars_in_line()
            buffer_cnt = buffer.get_line_count()
            if (buffer_cnt - line_cnt) > 1:
                line_len -= 1
                echo = True
            end = buffer.get_iter_at_line_offset(line_cnt, line_len)
            line = buffer.get_text(start, end)
            self.append_text("\n")
            if line.startswith(self.prompt):
                line = line[1:].strip()
            else:
                self.append_text("%s " % self.prompt)
                end = buffer.get_end_iter()
                buffer.place_cursor(end)
                return True
            if echo:
                self.append_text(("%s " % self.prompt) + line)
                end = buffer.get_end_iter()
                buffer.place_cursor(end)
                return True
            _retval = self.process_command(line)
            if _retval is not None:
                self.append_text("%s\n" % str(_retval))
            self.append_text("%s " % self.prompt)
            end = buffer.get_end_iter()
            buffer.place_cursor(end)
            return True
        return False

class QueryGramplet(PythonGramplet):
    def init(self):
        self.prompt = "$"
        self.set_tooltip(_("Enter SQL query"))
        # GUI setup:
        self.gui.textview.set_editable(True)
        self.set_text("Structured Query Language\n%s " % self.prompt)
        self.gui.textview.connect('key-press-event', self.on_key_press)

    def process_command(self, command):
        retval = run_quick_report_by_name(self.gui.dbstate, 
                                          self.gui.uistate, 
                                          'query', 
                                          command)
        return retval

class TODOGramplet(Gramplet):
    def init(self):
        # GUI setup:
        self.set_tooltip(_("Enter text"))
        self.gui.textview.set_editable(True)
        self.append_text(_("Enter your TODO list here."))

    def on_load(self):
        self.load_data_to_text()

    def on_save(self):
        self.gui.data = [] # clear out old data
        self.save_text_to_data()

class FAQGramplet(Gramplet):
    def init(self):
        self.set_use_markup(True)
        self.clear_text()
        self.render_text("Draft of a <a wiki='FAQ'>Frequently Asked Questions</a> Gramplet\n\n")
        self.render_text("  1. <a href='http://bugs.gramps-project.org/'>Test 1</a>\n")
        self.render_text("  2. <a href='http://gramps-project.org//'>Test 2</a>\n")

def make_welcome_content(gui):
    text = _(
        'Welcome to GRAMPS!\n\n'
        'GRAMPS is a software package designed for genealogical research.'
        ' Although similar to other genealogical programs, GRAMPS offers '
        'some unique and powerful features.\n\n'
        'GRAMPS is an Open Source Software package, which means you are '
        'free to make copies and distribute it to anyone you like. It\'s '
        'developed and maintained by a worldwide team of volunteers whose'
        ' goal is to make GRAMPS powerful, yet easy to use.\n\n'
        'Getting Started\n\n'
        'The first thing you must do is to create a new Family Tree. To '
        'create a new Family Tree (sometimes called a database) select '
        '"Family Trees" from the menu, pick "Manage Family Trees", press '
        '"New" and name your database. For more details, please read the '
        'User Manual, or the on-line manual at http://gramps-project.org.\n\n'
        'You are currently reading from the "Gramplets" page, where you can'
        ' add your own gramplets.\n\n'
        'You can right-click on the background of this page to add additional'
        ' gramplets and change the number of columns. You can also drag the '
        'Properties button to reposition the gramplet on this page, and detach'
        ' the gramplet to float above GRAMPS. If you close GRAMPS with a gramplet'
        ' detached, it will re-open detached the next time you start '
        'GRAMPS.'
            )
    gui.set_text(text)

class NewsGramplet(Gramplet):
    URL = "http://www.gramps-project.org/wiki/index.php?title=%s&action=raw"

    def init(self):
        self.set_tooltip(_("Read news from the GRAMPS wiki"))

    def main(self):
        continuation = self.process('News')
        retval = True
        while retval:
            retval, text = continuation.next()
            self.set_text(text)
            yield True
        self.cleanup(text)
        yield False

    def cleanup(self, text):
        # final text
        text = text.replace("<BR>", "\n")
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        text = text.strip()
        ## Wiki text:
        pattern = re.compile('\[\[(.*?)\|(.*?)\]\]')
        matches = pattern.findall(text)
        for (g1, g2) in matches:
            text = text.replace("[[%s|%s]]" % (g1, g2), "<U>%s</U>" % g2)
        pattern = re.compile('\[\[(.*?)\]\]')
        matches = pattern.findall(text)
        for match in matches:
            text = text.replace("[[%s]]" % match, "<U>%s</U>" % match)
        pattern = re.compile('\[(.*?) (.*?)\]')
        matches = pattern.findall(text)
        for (g1, g2) in matches:
            text = text.replace("[%s %s]" % (g1, g2), "<U>%s</U>" % g2)
        pattern = re.compile("'''(.*?)'''")
        matches = pattern.findall(text)
        for match in matches:
            text = text.replace("'''%s'''" % match, "<B>%s</B>" % match)
        text = "News from <I>www.gramps-project.org</I>:\n\n" + text
        self.clear_text()
        self.set_use_markup(True)
        self.render_text(text)
        self.append_text("", scroll_to="begin")
        
    def process(self, title):
        #print "processing '%s'..." % title
        title = title.replace(" ", "_")
        yield True, (_("Reading") + " '%s'..." % title)
        fp = urllib.urlopen(self.URL % title)
        text = fp.read()
        #text = text.replace("\n", " ")
        html = re.findall('<.*?>', text)
        for exp in html:
            text = text.replace(exp, "")
        text = text.replace("\n", "<BR>")
        fp.close()
        pattern = '{{.*?}}'
        matches = re.findall(pattern, text)
        #print "   before:", text
        for match in matches:
            page = match[2:-2]
            oldtext = match
            if "|" in page:
                template, heading, body = page.split("|", 2)
                if template.lower() == "release":
                    newtext = "GRAMPS " + heading + " released.<BR><BR>"
                else:
                    newtext = heading + "<BR><BR>"
                newtext += body + "<BR>"
                text = text.replace(oldtext, newtext)
            else: # a macro/redirect
                continuation = self.process("Template:" + page)
                retval = True
                while retval:
                    retval, newtext = continuation.next()
                    yield True, newtext
                text = text.replace(oldtext, newtext)
        #print "    after:", text
        pattern = '#REDIRECT \[\[.*?\]\]'
        matches = re.findall(pattern, text)
        #print "   before:", text
        for match in matches:
            page = match[12:-2]
            oldtext = match
            continuation = self.process(page)
            retval = True
            while retval:
                retval, newtext = continuation.next()
                yield True, newtext
            text = text.replace(oldtext, newtext)
        #print "    after:", text
        yield False, text

class AgeOnDateGramplet(Gramplet):
    def init(self):
        import gtk
        # GUI setup:
        self.set_tooltip(_("Enter a date, click Run"))
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        # label, entry
        description = gtk.TextView()
        description.set_wrap_mode(gtk.WRAP_WORD)
        description.set_editable(False)
        buffer = description.get_buffer()
        buffer.set_text(_("Enter a date in the entry below and click Run."
                          " This will compute the ages for everyone in your"
                          " Family Tree on that date. You can then sort by"
                          " the age column, and double-click the row to view"
                          " or edit."))
        label = gtk.Label()
        label.set_text(_("Date") + ":")
        self.entry = gtk.Entry()
        button = gtk.Button(_("Run"))
        button.connect("clicked", self.run)
        ##self.filter = 
        hbox.pack_start(label, False)
        hbox.pack_start(self.entry, True)
        vbox.pack_start(description, True)
        vbox.pack_start(hbox, False)
        vbox.pack_start(button, False)
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(vbox)
        vbox.show_all()

    def run(self, obj):
        text = self.entry.get_text()
        date = DateHandler.parser.parse(text)
        run_quick_report_by_name(self.gui.dbstate, 
                                 self.gui.uistate, 
                                 'ageondate', 
                                 date)

class QuickViewGramplet(Gramplet):
    def active_changed(self, handle):
        self.update()
        
    def main(self):
        qv_type = self.get_option(_("View Type"))
        quick_type = qv_type.get_value()
        qv_option = self.get_option(_("Quick Views"))
        quick_view = qv_option.get_value()
        if quick_type == CATEGORY_QR_PERSON:
            active = self.dbstate.get_active_person()
            if active:
                run_quick_report_by_name(self.gui.dbstate, 
                                         self.gui.uistate, 
                                         quick_view,
                                         active.handle,
                                         container=self.gui.textview)
        else:
            active_list = []
            for item in self.gui.uistate.viewmanager.pages:
                if (item.get_title() == _("Families") and
                    quick_type == CATEGORY_QR_FAMILY):
                    active_list = item.selected_handles()
                elif (item.get_title() == _("Events") and
                    quick_type == CATEGORY_QR_EVENT):
                    active_list = item.selected_handles()
                elif (item.get_title() == _("Sources") and
                    quick_type == CATEGORY_QR_SOURCE):
                    active_list = item.selected_handles()
                elif (item.get_title() == _("Places") and
                    quick_type == CATEGORY_QR_PLACE):
                    active_list = item.selected_handles()
                elif (item.get_title() == _("Repositories") and
                    quick_type == CATEGORY_QR_REPOSITORY):
                    active_list = item.selected_handles()
            if len(active_list) > 0:
                run_quick_report_by_name(self.gui.dbstate, 
                                         self.gui.uistate, 
                                         quick_view,
                                         active_list[0],
                                         container=self.gui.textview)

    def build_options(self):
        from gen.plug.menu import EnumeratedListOption
        # Add types:
        type_list = EnumeratedListOption(_("View Type"), CATEGORY_QR_PERSON)
        for item in [(CATEGORY_QR_PERSON, "Person"), 
                     (CATEGORY_QR_FAMILY, "Family"), 
                     (CATEGORY_QR_EVENT, "Event"), 
                     (CATEGORY_QR_SOURCE, "Source"), 
                     (CATEGORY_QR_PLACE, "Place"), 
                     (CATEGORY_QR_REPOSITORY, "Repository")]:
            type_list.add_item(item[0], item[1])
        # Add particular lists:
        qv_list = get_quick_report_list(CATEGORY_QR_PERSON)
        list_option = EnumeratedListOption(_("Quick Views"), qv_list[0][2])
        for item in qv_list:
            #(title, category, name, status)
            list_option.add_item(item[2], item[0])
        self.add_option(type_list)
        self.add_option(list_option)
        type_widget = self.get_option_widget(_("View Type"))
        type_widget.value_changed = self.rebuild_option_list

    def rebuild_option_list(self):
        qv_option = self.get_option(_("View Type"))
        list_option = self.get_option(_("Quick Views"))
        list_option.clear()
        qv_list = get_quick_report_list(qv_option.get_value())
        for item in qv_list:
            #(title, category, name, status)
            list_option.add_item(item[2], item[0])

class DataEntryGramplet(Gramplet):
    NO_REL     = 0
    AS_PARENT  = 1
    AS_SPOUSE  = 2
    AS_SIBLING = 3
    AS_CHILD   = 4
    def init(self):
        self.de_column_width = 20
        import gtk
        rows = gtk.VBox()
        self.dirty = False
        self.dirty_person = None
        self.dirty_family = None
        self.de_widgets = {}
        for items in [("Active person", _("Active person"), None, True, 
                       [("Edit person", "", self.edit_person), ("Edit family", _("Family:"), self.edit_family)], 
                       False, 0), 
                      ("APName", _("Surname, Given"), None, False, [], True, 0), 
                      ("APGender", _("Gender"), [_("female"), _("male"), _("unknown")], False, [], True, 2),
                      ("APBirth", _("Birth"), None, False, [], True, 0), 
                      ("APDeath", _("Death"), None, False, [], True, 0)
                     ]:
            pos, text, choices, readonly, callback, dirty, default = items
            row = self.make_row(pos, text, choices, readonly, callback, dirty, default)
            rows.pack_start(row, False)

        # Save and Abandon
        row = gtk.HBox()
        button = gtk.Button(_("Save"))
        button.connect("clicked", self.save_data_edit)
        row.pack_start(button, True)
        button = gtk.Button(_("Abandon"))
        button.connect("clicked", self.abandon_data_edit)
        row.pack_start(button, True)
        rows.pack_start(row, False)

        for items in [("New person", _("New person"), None, True, 0), 
                      ("NPRelation", _("Add relation"), 
                       [_("No relation to active person"),
                        _("Add as a Parent"), 
                        _("Add as a Spouse"), 
                        _("Add as a Sibling"), 
                        _("Add as a Child")],
                       False, 0),
                      ("NPName", _("Surname, Given"), None, False, 0), 
                      ("NPGender", _("Gender"), [_("female"), _("male"), _("unknown")], False, 2),
                      ("NPBirth", _("Birth"), None, False, 0), 
                      ("NPDeath", _("Death"), None, False, 0)
                     ]:
            pos, text, choices, readonly, default = items
            row = self.make_row(pos, text, choices, readonly, default=default)
            rows.pack_start(row, False)

        # Save, Abandon, Clear
        row = gtk.HBox()
        button = gtk.Button(_("Add"))
        button.connect("clicked", self.add_data_entry)
        row.pack_start(button, True)
        button = gtk.Button(_("Copy Active Data"))
        button.connect("clicked", self.copy_data_entry)
        row.pack_start(button, True)
        button = gtk.Button(_("Clear"))
        button.connect("clicked", self.clear_data_entry)
        row.pack_start(button, True)
        rows.pack_start(row, False)

        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(rows)
        rows.show_all()
        self.clear_data_entry(None)

    def main(self): # return false finishes
        if self.dirty:
            return
        self.de_widgets["Active person:Edit family"].hide()
        self.de_widgets["Active person:Edit family:Label"].hide()
        active_person = self.dbstate.get_active_person()
        self.dirty_person = active_person
        self.dirty_family = None
        if active_person:
            self.de_widgets["Active person:Edit person"].show()
            self.de_widgets["Active person:Edit family"].hide()
            self.de_widgets["Active person:Edit family:Label"].hide()
            # Fill in current person edits:
            name = name_displayer.display(active_person)
            self.de_widgets["Active person"].set_text("<i>%s</i> " % name)
            self.de_widgets["Active person"].set_use_markup(True)
            # Name:
            name_obj = active_person.get_primary_name()
            if name_obj:
                self.de_widgets["APName"].set_text("%s, %s" %
                   (name_obj.get_surname(), name_obj.get_first_name()))
            self.de_widgets["APGender"].set_active(active_person.get_gender()) # gender
            # Birth:
            birth = ReportUtils.get_birth_or_fallback(self.dbstate.db, active_person)
            birth_text = ""
            if birth:
                sdate = DateHandler.get_date(birth)
                birth_text += sdate + " "
                place_handle = birth.get_place_handle()
                if place_handle:
                    place = self.dbstate.db.get_place_from_handle(place_handle)
                    place_text = place.get_title()
                    if place_text:
                        birth_text += _("in") + " " + place_text

            self.de_widgets["APBirth"].set_text(birth_text)
            # Death:
            death = ReportUtils.get_death_or_fallback(self.dbstate.db, active_person)
            death_text = ""
            if death:
                sdate = DateHandler.get_date(death)
                death_text += sdate + " "
                place_handle = death.get_place_handle()
                if place_handle:
                    place = self.dbstate.db.get_place_from_handle(place_handle)
                    place_text = place.get_title()
                    if place_text:
                        death_text += _("in") + " " + place_text
            self.de_widgets["APDeath"].set_text(death_text)
            family_list = active_person.get_family_handle_list()
            if len(family_list) > 0:
                self.dirty_family = self.dbstate.db.get_family_from_handle(family_list[0])
                self.de_widgets["Active person:Edit family"].show()
                self.de_widgets["Active person:Edit family:Label"].show()
            else:
                family_list = active_person.get_parent_family_handle_list()
                if len(family_list) > 0:
                    self.dirty_family = self.dbstate.db.get_family_from_handle(family_list[0])
                    self.de_widgets["Active person:Edit family"].show()
                    self.de_widgets["Active person:Edit family:Label"].show()
        else:
            self.clear_data_edit(None)
            self.de_widgets["Active person:Edit person"].hide()
            self.de_widgets["Active person:Edit family"].hide()
            self.de_widgets["Active person:Edit family:Label"].hide()
        self.dirty = False

    def make_row(self, pos, text, choices=None, readonly=False, callback_list=[],
                 mark_dirty=False, default=0):
        import gtk
        # Data Entry: Active Person
        row = gtk.HBox()
        label = gtk.Label()
        if readonly:
            label.set_text("<b>%s</b>" % text)
            label.set_width_chars(self.de_column_width)
            label.set_use_markup(True)
            self.de_widgets[pos] = gtk.Label()
            self.de_widgets[pos].set_alignment(0.0, 0.5)
            self.de_widgets[pos].set_use_markup(True)
            label.set_alignment(0.0, 0.5)
            row.pack_start(label, False)
            row.pack_start(self.de_widgets[pos], False)
        else:
            label.set_text("%s: " % text)
            label.set_width_chars(self.de_column_width)
            label.set_alignment(1.0, 0.5) 
            if choices == None:
                self.de_widgets[pos] = gtk.Entry()
                if mark_dirty:
                    self.de_widgets[pos].connect("changed", self.mark_dirty)
                row.pack_start(label, False)
                row.pack_start(self.de_widgets[pos], True)
            else:
                eventBox = gtk.EventBox()
                self.de_widgets[pos] = gtk.combo_box_new_text()
                eventBox.add(self.de_widgets[pos])
                for add_type in choices:
                    self.de_widgets[pos].append_text(add_type)
                self.de_widgets[pos].set_active(default) 
                if mark_dirty:
                    self.de_widgets[pos].connect("changed", self.mark_dirty)
                row.pack_start(label, False)
                row.pack_start(eventBox, True, True)
        for name, text, callback in callback_list:
            label = gtk.Label()
            label.set_text(text)
            self.de_widgets[pos + ":" + name + ":Label"] = label
            row.pack_start(label, False)
            icon = gtk.STOCK_EDIT
            size = gtk.ICON_SIZE_MENU
            button = gtk.Button()
            image = gtk.Image()
            image.set_from_stock(icon, size)
            button.add(image)
            button.set_relief(gtk.RELIEF_NONE)
            button.connect("clicked", callback)
            self.de_widgets[pos + ":" + name] = button
            row.pack_start(button, False)
        row.show_all()
        return row

    def mark_dirty(self, obj):
        self.dirty = True

    def abandon_data_edit(self, obj):
        self.dirty = False
        self.update()

    def edit_callback(self, person):
        self.dirty = False
        self.update()

    def edit_person(self, obj):
        from Editors import EditPerson
        try:
            EditPerson(self.gui.dbstate, 
                       self.gui.uistate, [], 
                       self.dirty_person,
                       callback=self.edit_callback)
        except Errors.WindowActiveError:
            pass

    def edit_family(self, obj):
        from Editors import EditFamily
        try:
            EditFamily(self.gui.dbstate, 
                       self.gui.uistate, [], 
                       self.dirty_family)
        except Errors.WindowActiveError:
            pass
    
    def process_dateplace(self, text):
        if text == "": return None, None
        prep_in = _("in") # word or phrase that separates date from place
        text = text.strip()
        if (" %s "  % prep_in) in text:
            date, place = text.split((" %s "  % prep_in), 1)
        elif text.startswith("%s "  % prep_in):
            date, place = text.split(("%s "  % prep_in), 1)
        else:
            date, place = text, ""
        date = date.strip()
        place = place.strip()
        if date != "":
            date = DateHandler.parser.parse(date)
        else:
            date = None
        if place != "":
            newq, place = self.get_or_create_place(place)
        else:
            place = None
        return date, place

    def get_or_create_place(self, place_name):
        if place_name == "": return (-1, None)
        place_list = self.dbstate.db.get_place_handles()
        for place_handle in place_list:
            place = self.dbstate.db.get_place_from_handle(place_handle)
            if place.get_title().strip() == place_name:
                return (0, place) # (old, object)
        place = gen.lib.Place()
        place.set_title(place_name)
        self.dbstate.db.add_place(place,self.trans)
        return (1, place) # (new, object)

    def get_or_create_event(self, object, type, date, place):
        """ Add or find a type event on object """
        if date == place == None: return (-1, None)
        # first, see if it exists
        ref_list = object.get_event_ref_list()
        # look for a match, and possible correction
        for ref in ref_list:
            event = self.dbstate.db.get_event_from_handle(ref.ref)
            if event is not None:
                if int(event.get_type()) == type:
                    # Match! Let's update
                    if date:
                        event.set_date_object(date)
                    if place:
                        event.set_place_handle(place.get_handle())
                    self.dbstate.db.commit_event(event, self.trans)
                    return (0, event)
        # else create it:
        event = gen.lib.Event()
        if type:
            event.set_type(gen.lib.EventType(type))
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        self.dbstate.db.add_event(event, self.trans)
        return (1, event)

    def make_event(self, type, date, place):
        if date == place == None: return None
        event = gen.lib.Event()
        event.set_type(gen.lib.EventType(type))
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        self.dbstate.db.add_event(event, self.trans)
        return event

    def make_person(self, firstname, surname, gender):
        person = gen.lib.Person()
        name = gen.lib.Name()
        name.set_type(gen.lib.NameType(gen.lib.NameType.BIRTH))
        name.set_first_name(firstname)
        name.set_surname(surname)
        person.set_primary_name(name)
        person.set_gender(gender)
        return person

    def save_data_edit(self, obj):
        if self.dirty:
            # Save the edits ----------------------------------
            person = self.dirty_person
            # First, get the data:
            gender = self.de_widgets["APGender"].get_active()
            if "," in self.de_widgets["APName"].get_text():
                surname, firstname = self.de_widgets["APName"].get_text().split(",", 1)
            else:
                surname, firstname = self.de_widgets["APName"].get_text(), ""
            surname = surname.strip()
            firstname = firstname.strip()
            name = person.get_primary_name()
            # Now, edit it:
            self.trans = self.dbstate.db.transaction_begin()
            name.set_surname(surname)
            name.set_first_name(firstname)
            person.set_gender(gender)
            birthdate, birthplace = self.process_dateplace(self.de_widgets["APBirth"].get_text().strip())
            new, birthevent = self.get_or_create_event(person, gen.lib.EventType.BIRTH, birthdate, birthplace)
            # reference it, if need be:
            birthref = person.get_birth_ref()
            if birthevent:
                if birthref is None:
                    # need new
                    birthref = gen.lib.EventRef()
                birthref.set_reference_handle(birthevent.get_handle())
                person.set_birth_ref(birthref)
            deathdate, deathplace = self.process_dateplace(self.de_widgets["APDeath"].get_text().strip())
            new, deathevent = self.get_or_create_event(person, gen.lib.EventType.DEATH, deathdate, deathplace)
            # reference it, if need be:
            deathref = person.get_death_ref()
            if deathevent:
                if deathref is None:
                    # need new
                    deathref = gen.lib.EventRef()
                deathref.set_reference_handle(deathevent.get_handle())
                person.set_death_ref(deathref)
            self.dbstate.db.commit_person(person,self.trans)
            self.dbstate.db.transaction_commit(self.trans,
                    (_("Gramplet Data Edit: %s") %  name_displayer.display(person)))
        self.dirty = False
        self.update()

    def add_data_entry(self, obj):
        from QuestionDialog import ErrorDialog
        # First, get the data:
        if "," in self.de_widgets["NPName"].get_text():
            surname, firstname = self.de_widgets["NPName"].get_text().split(",", 1)
        else:
            surname, firstname = self.de_widgets["NPName"].get_text(), ""
        surname = surname.strip()
        firstname = firstname.strip()
        gender = self.de_widgets["NPGender"].get_active()
        if self.dirty:
            current_person = self.dirty_person
        else:
            current_person = self.dbstate.get_active_person()
        # Pre-check to make sure everything is ok: -------------------------------------------
        if surname == "" and firstname == "":
            ErrorDialog(_("Please provide a name."), _("Can't add new person."))
            return
        if self.de_widgets["NPRelation"].get_active() == self.NO_REL:
            # "No relation to active person"
            pass
        elif self.de_widgets["NPRelation"].get_active() == self.AS_PARENT:
            # "Add as a Parent"
            if current_person == None:
                ErrorDialog(_("Please set an active person."), _("Can't add new person as a parent."))
                return
            elif gender == gen.lib.Person.UNKNOWN: # unknown
                ErrorDialog(_("Please set the new person's gender."), _("Can't add new person as a parent."))
                return
        elif self.de_widgets["NPRelation"].get_active() == self.AS_SPOUSE:
            # "Add as a Spouse"
            if current_person == None:
                ErrorDialog(_("Please set an active person."), _("Can't add new person as a spouse."))
                return
            elif (gender == gen.lib.Person.UNKNOWN and 
                  current_person.get_gender() == gen.lib.Person.UNKNOWN): # both genders unknown
                ErrorDialog(_("Please set the new person's gender."), _("Can't add new person as a spouse."))
                return
        elif self.de_widgets["NPRelation"].get_active() == self.AS_SIBLING:
            # "Add as a Sibling"
            if current_person == None:
                ErrorDialog(_("Please set an active person."), _("Can't add new person as a sibling."))
                return
        elif self.de_widgets["NPRelation"].get_active() == self.AS_CHILD:
            # "Add as a Child"
            if current_person == None:
                ErrorDialog(_("Please set an active person."), _("Can't add new person as a child."))
                return
        # Start the transaction: ------------------------------------------------------------
        self.trans = self.dbstate.db.transaction_begin()
        # New person --------------------------------------------------
        # Add birth
        new_birth_date, new_birth_place = self.process_dateplace(self.de_widgets["NPBirth"].get_text().strip())
        birth_event = self.make_event(gen.lib.EventType.BIRTH, new_birth_date, new_birth_place)
        # Add death
        new_death_date, new_death_place = self.process_dateplace(self.de_widgets["NPDeath"].get_text())
        death_event = self.make_event(gen.lib.EventType.DEATH, new_death_date, new_death_place)
        # Now, create the person and events:
        person = self.make_person(firstname, surname, gender)
        # New birth for person:
        if birth_event:
            birth_ref = gen.lib.EventRef()
            birth_ref.set_reference_handle(birth_event.get_handle())
            person.set_birth_ref(birth_ref)
        # New death for person:
        if death_event:
            death_ref = gen.lib.EventRef()
            death_ref.set_reference_handle(death_event.get_handle())
            person.set_death_ref(death_ref)
        self.dbstate.db.add_person(person, self.trans)
        # All error checking done; just add relation:
        if self.de_widgets["NPRelation"].get_active() == self.NO_REL:
            # "No relation to active person"
            pass
        elif self.de_widgets["NPRelation"].get_active() == self.AS_PARENT:
            # "Add as a Parent"
            # Go through current_person parent families
            added = False
            for family_handle in current_person.get_parent_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family:
                    # find one that person would fit as a parent
                    fam_husband_handle = family.get_father_handle()
                    fam_wife_handle = family.get_mother_handle()
                    # can we add person as wife?
                    if fam_wife_handle == None and person.get_gender() == gen.lib.Person.FEMALE:
                        # add the person
                        family.set_mother_handle(person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.add_family_handle(family.get_handle())
                        added = True
                        break
                    elif fam_husband_handle == None and person.get_gender() == gen.lib.Person.MALE:
                        # add the person
                        family.set_father_handle(person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.add_family_handle(family.get_handle())
                        added = True
                        break
            if added:
                self.dbstate.db.commit_family(family, self.trans)
            else:
                family = gen.lib.Family()
                self.dbstate.db.add_family(family, self.trans)
                if person.get_gender() == gen.lib.Person.MALE:
                    family.set_father_handle(person.get_handle())
                elif person.get_gender() == gen.lib.Person.FEMALE:
                    family.set_mother_handle(person.get_handle())
                family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                # add curent_person as child
                childref = gen.lib.ChildRef()
                childref.set_reference_handle(current_person.get_handle())
                family.add_child_ref( childref)
                current_person.add_parent_family_handle(family.get_handle())
                # finalize
                person.add_family_handle(family.get_handle())
                self.dbstate.db.commit_family(family, self.trans)
        elif self.de_widgets["NPRelation"].get_active() == self.AS_SPOUSE:
            # "Add as a Spouse"
            added = False
            family = None
            for family_handle in current_person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family:
                    fam_husband_handle = family.get_father_handle()
                    fam_wife_handle = family.get_mother_handle()
                    if current_person.get_handle() == fam_husband_handle:
                        # can we add person as wife?
                        if fam_wife_handle == None:
                            if person.get_gender() == gen.lib.Person.FEMALE:
                                # add the person
                                family.set_mother_handle(person.get_handle())
                                family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                                person.add_family_handle(family.get_handle())
                                added = True
                                break
                            elif person.get_gender() == gen.lib.Person.UNKNOWN:
                                family.set_mother_handle(person.get_handle())
                                family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                                person.set_gender(gen.lib.Person.FEMALE)
                                self.de_widgets["NPGender"].set_active(gen.lib.Person.FEMALE)
                                person.add_family_handle(family.get_handle())
                                added = True
                                break
                    elif current_person.get_handle() == fam_wife_handle:
                        # can we add person as husband?
                        if fam_husband_handle == None:
                            if person.get_gender() == gen.lib.Person.MALE:
                                # add the person
                                family.set_father_handle(person.get_handle())
                                family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                                person.add_family_handle(family.get_handle())
                                added = True
                                break
                            elif person.get_gender() == gen.lib.Person.UNKNOWN:
                                family.set_father_handle(person.get_handle())
                                family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                                person.add_family_handle(family.get_handle())
                                person.set_gender(gen.lib.Person.MALE)
                                self.de_widgets["NPGender"].set_active(gen.lib.Person.MALE)
                                added = True
                                break
            if added:
                self.dbstate.db.commit_family(family, self.trans)
            else:
                if person.get_gender() == gen.lib.Person.UNKNOWN:
                    if current_person.get_gender() == gen.lib.Person.UNKNOWN:
                        ErrorDialog(_("Please set gender on Active or new person."), 
                                    _("Can't add new person as a spouse."))
                        return
                    elif current_person.get_gender() == gen.lib.Person.MALE:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(current_person.get_handle())
                        family.set_mother_handle(person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.set_gender(gen.lib.Person.FEMALE)
                        self.de_widgets["NPGender"].set_active(gen.lib.Person.FEMALE)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                    elif current_person.get_gender() == gen.lib.Person.FEMALE:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(person.get_handle())
                        family.set_mother_handle(current_person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.set_gender(gen.lib.Person.MALE)
                        self.de_widgets["NPGender"].set_active(gen.lib.Person.MALE)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                elif person.get_gender() == gen.lib.Person.MALE:
                    if current_person.get_gender() == gen.lib.Person.UNKNOWN:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(person.get_handle())
                        family.set_mother_handle(current_person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        current_person.set_gender(gen.lib.Person.FEMALE)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                    elif current_person.get_gender() == gen.lib.Person.MALE:
                        ErrorDialog(_("Same genders on Active and new person."), 
                                    _("Can't add new person as a spouse."))
                        return
                    elif current_person.get_gender() == gen.lib.Person.FEMALE:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(person.get_handle())
                        family.set_mother_handle(current_person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                elif person.get_gender() == gen.lib.Person.FEMALE:
                    if current_person.get_gender() == gen.lib.Person.UNKNOWN:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(current_person.get_handle())
                        family.set_mother_handle(person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        current_person.set_gender(gen.lib.Person.MALE)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                    elif current_person.get_gender() == gen.lib.Person.MALE:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(current_person.get_handle())
                        family.set_mother_handle(person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                    elif current_person.get_gender() == gen.lib.Person.FEMALE:
                        ErrorDialog(_("Same genders on Active and new person."), 
                                    _("Can't add new person as a spouse."))
                        return
        elif self.de_widgets["NPRelation"].get_active() == self.AS_SIBLING:
            # "Add as a Sibling"
            added = False
            for family_handle in current_person.get_parent_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family:
                    childref = gen.lib.ChildRef()
                    childref.set_reference_handle(person.get_handle())
                    family.add_child_ref( childref)
                    person.add_parent_family_handle(family.get_handle())
                    added = True
                    break
            if added:
                self.dbstate.db.commit_family(family, self.trans)
            else:
                family = gen.lib.Family()
                self.dbstate.db.add_family(family, self.trans)
                childref = gen.lib.ChildRef()
                childref.set_reference_handle(person.get_handle())
                family.add_child_ref( childref)
                childref = gen.lib.ChildRef()
                childref.set_reference_handle(current_person.get_handle())
                family.add_child_ref( childref)
                person.add_parent_family_handle(family.get_handle())
                current_person.add_parent_family_handle(family.get_handle())
                self.dbstate.db.commit_family(family, self.trans)
        elif self.de_widgets["NPRelation"].get_active() == self.AS_CHILD:
            # "Add as a Child"
            added = False
            family = None
            for family_handle in current_person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family:
                    childref = gen.lib.ChildRef()
                    childref.set_reference_handle(person.get_handle())
                    family.add_child_ref( childref)
                    person.add_parent_family_handle(family.get_handle())
                    added = True
                    break
            if added:
                self.dbstate.db.commit_family(family, self.trans)
            else:
                if current_person.get_gender() == gen.lib.Person.UNKNOWN:
                    ErrorDialog(_("Please set gender on Active person."), 
                                _("Can't add new person as a child."))
                    return
                else:
                    family = gen.lib.Family()
                    self.dbstate.db.add_family(family, self.trans)
                    childref = gen.lib.ChildRef()
                    childref.set_reference_handle(person.get_handle())
                    family.add_child_ref( childref)
                    person.add_parent_family_handle(family.get_handle())
                    current_person.add_family_handle(family.get_handle())
                    if gen.lib.Person.FEMALE:
                        family.set_mother_handle(current_person.get_handle())
                    else:
                        family.set_father_handle(current_person.get_handle())
                    self.dbstate.db.commit_family(family, self.trans)
        # Commit changes -------------------------------------------------
        if current_person:
            self.dbstate.db.commit_person(current_person, self.trans)
        if person:
            self.dbstate.db.commit_person(person, self.trans)
        self.dbstate.db.transaction_commit(self.trans,
                 (_("Gramplet Data Entry: %s") %  name_displayer.display(person)))

    def copy_data_entry(self, obj):
        self.de_widgets["NPName"].set_text(self.de_widgets["APName"].get_text())
        self.de_widgets["NPBirth"].set_text(self.de_widgets["APBirth"].get_text())
        self.de_widgets["NPDeath"].set_text(self.de_widgets["APDeath"].get_text())
        self.de_widgets["NPGender"].set_active(self.de_widgets["APGender"].get_active())
        # FIXME: put cursor in add surname

    def clear_data_edit(self, obj):
        self.de_widgets["Active person"].set_text("")
        self.de_widgets["APName"].set_text("")
        self.de_widgets["APBirth"].set_text("")
        self.de_widgets["APDeath"].set_text("")
        self.de_widgets["APGender"].set_active(gen.lib.Person.UNKNOWN) 

    def clear_data_entry(self, obj):
        self.de_widgets["NPName"].set_text("")
        self.de_widgets["NPBirth"].set_text("")
        self.de_widgets["NPDeath"].set_text("")
        self.de_widgets["NPRelation"].set_active(self.NO_REL) 
        self.de_widgets["NPGender"].set_active(gen.lib.Person.UNKNOWN) 

    def db_changed(self):
        """
        If person or family changes, the relatives of active person might have
        changed
        """
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('person-edit', self.update)
        self.dbstate.db.connect('family-add', self.update)
        self.dbstate.db.connect('family-delete', self.update)
        self.dbstate.db.connect('person-rebuild', self.update)
        self.dbstate.db.connect('family-rebuild', self.update)
        self.dirty = False
        self.dirty_person = None
        self.clear_data_entry(None)

    def active_changed(self, handle):
        self.update()

register(type="gramplet", 
         name= "Top Surnames Gramplet", 
         tname=_("Top Surnames Gramplet"), 
         height=230,
         content = TopSurnamesGramplet,
         title=_("Top Surnames"),
         )

register(type="gramplet", 
         name= "Surname Cloud Gramplet", 
         tname=_("Surname Cloud Gramplet"), 
         height=300,
         expand=True,
         content = SurnameCloudGramplet,
         title=_("Surname Cloud"),
         )

register(type="gramplet", 
         name="Statistics Gramplet", 
         tname=_("Statistics Gramplet"), 
         height=230,
         expand=True,
         content = StatsGramplet,
         title=_("Statistics"),
         )

register(type="gramplet", 
         name="Session Log Gramplet", 
         tname=_("Session Log Gramplet"), 
         height=230,
         data=['no'],
         content = LogGramplet,
         title=_("Session Log"),
         )

register(type="gramplet", 
         name="Python Gramplet", 
         tname=_("Python Gramplet"), 
         height=250,
         content = PythonGramplet,
         title=_("Python Shell"),
         )

register(type="gramplet", 
         name="TODO Gramplet", 
         tname=_("TODO Gramplet"), 
         height=300,
         expand=True,
         content = TODOGramplet,
         title=_("TODO List"),
         )

register(type="gramplet", 
         name="Welcome Gramplet", 
         tname=_("Welcome Gramplet"), 
         height=300,
         expand=True,
         content = make_welcome_content,
         title=_("Welcome to GRAMPS!"),
         )

register(type="gramplet", 
         name="Calendar Gramplet", 
         tname=_("Calendar Gramplet"), 
         height=200,
         content = CalendarGramplet,
         title=_("Calendar"),
         )

register(type="gramplet", 
         name="News Gramplet", 
         tname=_("News Gramplet"), 
         height=300,
         expand=True,
         content = NewsGramplet,
         title=_("News"),
         )

register(type="gramplet", 
         name="Age on Date Gramplet", 
         tname=_("Age on Date Gramplet"), 
         height=200,
         content = AgeOnDateGramplet,
         title=_("Age on Date"),
         )

register(type="gramplet", 
         name="Relatives Gramplet", 
         tname=_("Relatives Gramplet"), 
         height=200,
         content = RelativesGramplet,
         title=_("Active Person's Relatives"),
         detached_width = 250,
         detached_height = 300,
         )

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

register(type="gramplet", 
         name="FAQ Gramplet", 
         tname=_("FAQ Gramplet"), 
         height=300,
         content = FAQGramplet,
         title=_("FAQ"),
         )

register(type="gramplet", 
         name="Query Gramplet", 
         tname=_("Query Gramplet"), 
         height=300,
         content = QueryGramplet,
         title=_("Query"),
         detached_width = 600,
         detached_height = 400,
         )

register(type="gramplet", 
         name="Quick View Gramplet", 
         tname=_("Quick View Gramplet"), 
         height=300,
         expand=True,
         content = QuickViewGramplet,
         title=_("Quick View"),
         detached_width = 600,
         detached_height = 400,
         )

register(type="gramplet", 
         name="Data Entry Gramplet", 
         tname=_("Data Entry Gramplet"), 
         height=375,
         expand=False,
         content = DataEntryGramplet,
         title=_("Data Entry"),
         detached_width = 510,
         detached_height = 480,
         )

