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

import gen.lib
from DataViews import register, Gramplet
from BasicUtils import name_displayer
from Utils import media_path_full
from QuickReports import run_quick_report_by_name
import DateHandler
from TransUtils import sgettext as _
import Config

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
        self.tooltip = _("Double-click a day for details")
        self.gui.calendar = gtk.Calendar()
        self.gui.calendar.connect('day-selected-double-click', self.double_click)
        self.gui.calendar.connect('month-changed', self.refresh)
        db_signals = ['event-add',
                      'event-update', 
                      'event-delete', 
                      'event-rebuild',
                      ]
        for signal in db_signals:
            self.dbstate.db.connect(signal, lambda *args: self.run_update(signal, *args))

        self.gui.scrolledwindow.remove(self.gui.textview)
        self.gui.scrolledwindow.add_with_viewport(self.gui.calendar)
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
            if self.birthdays and birth_date != None:
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
        self.tooltip = _("Click name to change active\nDouble-click name to edit")
        self.set_text(_("Log for this Session"))
        self.append_text("\n--------------------\n")
        self.history = {}

    def db_changed(self):
        self.dbstate.db.connect('person-add', self.log_person_add)
        self.dbstate.db.connect('person-delete', self.log_person_delete)
        self.dbstate.db.connect('person-update', self.log_person_update)
        self.dbstate.db.connect('family-add', self.log_family_add)
        self.dbstate.db.connect('family-delete', self.log_family_delete)
        self.dbstate.db.connect('family-update', self.log_family_update)
    
    def on_load(self):
        if len(self.gui.data) > 0:
            self.show_duplicates = self.gui.data[0]

    def on_save(self):
        self.gui.data = [self.show_duplicates]

    def active_changed(self, handle):
        self.log_active_changed(handle)

    # FIXME: added support for family display and clicks
    def log_person_add(self, handles):
        self.get_person(handles, _("Added"))
    def log_person_delete(self, handles):
        self.get_person(handles, _("Deleted"))
    def log_person_update(self, handles):
        self.get_person(handles, _("Updated"))
    def log_family_add(self, handles):
        self.append_text(_("Added") + ": family\n" )
    def log_family_delete(self, handles):
        self.append_text(_("Deleted") + ": family\n" )
    def log_family_update(self, handles):
        self.append_text(_("Updated") + ": family\n" )
    def log_active_changed(self, handles):
        self.get_person([handles], _("Selected"))

    def get_person(self, handles, ltype):
        for person_handle in handles:
            if ((self.show_duplicates == "no" and 
                 ltype + ": " + person_handle not in self.history) or
                self.show_duplicates == "yes"):
                self.append_text("%s: " % ltype)
                self.history[ltype + ": " + person_handle] = 1
                person = self.dbstate.db.get_person_from_handle(person_handle)
                if person:
                    self.link(name_displayer.display(person), 'Person', 
                              person_handle)
                else:
                    self.link(_("Unknown"), 'Person', person_handle)
                self.append_text("\n")

class TopSurnamesGramplet(Gramplet):
    def init(self):
        self.tooltip = _("Double-click surname for details")
        self.top_size = 10 # will be overwritten in load
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
        surnames = {}
        representative_handle = {}
        cnt = 0
        for person_handle in people:
            person = self.dbstate.db.get_person_from_handle(person_handle)
            if person:
                surname = person.get_primary_name().get_surname().strip()
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
        self.tooltip = _("Double-click surname for details")
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
        surnames = {}
        representative_handle = {}
        cnt = 0
        for person_handle in people:
            person = self.dbstate.db.get_person_from_handle(person_handle)
            if person:
                surname = person.get_primary_name().get_surname().strip()
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
        for (count, surname) in cloud_names: # surname_sort:
            if len(surname) == 0:
                text = Config.get(Config.NO_SURNAME_TEXT)
            else:
                text = surname
            size = make_tag_size(count, counts)
            self.link(text, 'Surname', representative_handle[surname], size,
                      "%s, %d%% (%d)" % (text, 
                                        int((float(count)/total) * 100), 
                                        count))
            self.append_text(" ")
            line += 1
            if line >= self.top_size:
                break
        self.append_text(("\n" + _("Total unique surnames") + ": %d\n") % 
                         total_surnames)
        self.append_text((_("Total people") + ": %d") % total_people, "begin")

class RelativesGramplet(Gramplet):
    """
    This gramplet gives a list of clickable relatives of the active person.
    Clicking them, changes the active person.
    """
    def init(self):
        self.set_text(_("No Family Tree loaded."))
        self.tooltip = _("Click name to make person active\n") + \
                         _("Right-click name to edit person")

    def db_changed(self):
        """
        If person or family changes, the relatives of active person might have
        changed
        """
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('family-add', self.update)
        self.dbstate.db.connect('family-delete', self.update)

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
        self.tooltip = _("Click name to make person active\n") + \
                         _("Right-click name to edit person")
        self.max_generations = 100

    def db_changed(self):
        """
        If person or family changes, the relatives of active person might have
        changed
        """
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('family-add', self.update)
        self.dbstate.db.connect('family-delete', self.update)

    def active_changed(self, handle):
        self.update()

    def get_boxes(self, generation):
        retval = ""
        for i in range(generation+1):
            if self._boxes[i]:
                retval += " |"
            else:
                retval += "  "
        return retval + "--"

    def process_person(self, handle, generation, what):
        if generation > self.max_generations:
            return
        person = self.dbstate.db.get_person_from_handle(handle)
        family_list = person.get_parent_family_handle_list()
        if what == "f":
            if len(family_list) > 0:
                family = self.dbstate.db.get_family_from_handle(family_list[0])
                father = family.get_father_handle()
                if father:
                    self.process_person(father, generation + 1, "f")
                    self._boxes[generation] = 1
                    self.process_person(father, generation + 1, "s")
                    self.process_person(father, generation + 1, "m")
        if what == "s":
            self.append_text(self.get_boxes(generation))
            self.link(name_displayer.display_name(person.get_primary_name()),
                      'Person', person.handle)
            self.append_text("\n")
        if what == "m":
            if len(family_list) > 0:
                family = self.dbstate.db.get_family_from_handle(family_list[0])
                mother = family.get_mother_handle()
                if mother:
                    self.process_person(mother, generation + 1, "f")
                    self.process_person(mother, generation + 1, "s")
                    self._boxes[generation] = 0
                    self.process_person(mother, generation + 1, "m")

    def main(self): # return false finishes
        """
        Generator which will be run in the background.
        """
        self._boxes = [0] * self.max_generations
        self.set_text("")
        active_person = self.dbstate.get_active_person()
        if not active_person:
            return False
        self.process_person(active_person.handle, 1, "f")
        self.process_person(active_person.handle, 1, "s")
        self.process_person(active_person.handle, 1, "m")
        self.append_text("", scroll_to="begin")

class StatsGramplet(Gramplet):
    def init(self):
        self.set_text(_("No Family Tree loaded."))

    def db_changed(self):
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('family-add', self.update)
        self.dbstate.db.connect('family-delete', self.update)

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
            name = person.get_primary_name()
            if name.get_first_name() == "" or name.get_surname() == "":
                incomp_names = incomp_names + 1
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
            if name.get_surname() not in namelist:
                namelist.append(name.get_surname())
            if cnt % 200 == 0:
                yield True
            cnt += 1

        text = _("Individuals") + "\n"
        text = text + "----------------------------\n"
        text = text + "%s: %d\n" % (_("Number of individuals"),len(personList))
        text = text + "%s: %d\n" % (_("Males"),males)
        text = text + "%s: %d\n" % (_("Females"),females)
        text = text + "%s: %d\n" % (_("Individuals with unknown gender"),unknowns)
        text = text + "%s: %d\n" % (_("Individuals with incomplete names"),incomp_names)
        text = text + "%s: %d\n" % (_("Individuals missing birth dates"),missing_bday)
        text = text + "%s: %d\n" % (_("Disconnected individuals"),disconnected)
        text = text + "\n%s\n" % _("Family Information")
        text = text + "----------------------------\n"
        text = text + "%s: %d\n" % (_("Number of families"),len(familyList))
        text = text + "%s: %d\n" % (_("Unique surnames"),len(namelist))
        text = text + "\n%s\n" % _("Media Objects")
        text = text + "----------------------------\n"
        text = text + "%s: %d\n" % (_("Individuals with media objects"),with_photos)
        text = text + "%s: %d\n" % (_("Total number of media object references"),total_photos)
        text = text + "%s: %d\n" % (_("Number of unique media objects"),pobjects)
        text = text + "%s: %d %s\n" % (_("Total size of media objects"),bytes,\
                                        _("bytes"))

        if len(notfound) > 0:
            text = text + "\n%s\n" % _("Missing Media Objects")
            text = text + "----------------------------\n"
            for p in notfound:
                text = text + "%s\n" % p
        self.set_text(text)

class PythonGramplet(Gramplet):
    def init(self):
        self.tooltip = _("Enter Python expressions")
        self.env = {"dbstate": self.gui.dbstate,
                    "uistate": self.gui.uistate,
                    "self": self,
                    _("class name|Date"): gen.lib.Date,
                    }
        # GUI setup:
        self.gui.textview.set_editable(True)
        self.set_text("Python %s\n> " % sys.version)
        self.gui.textview.connect('key-press-event', self.on_key_press)

    def format_exception(self, max_tb_level=10):
        retval = ''
        cla, exc, trbk = sys.exc_info()
        retval += _("Error") + (" : %s %s" %(cla, exc))
        return retval

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
            if line.startswith(">"):
                line = line[1:].strip()
            else:
                self.append_text("> ")
                return True
            if echo:
                self.append_text("> " + line)
                end = buffer.get_end_iter()
                buffer.place_cursor(end)
                return True
            # update states, in case of change:
            self.env["dbstate"] = self.gui.dbstate
            self.env["uistate"] = self.gui.uistate
            _retval = None
            if "_retval" in self.env:
                del self.env["_retval"]
            exp1 = """_retval = """ + line
            exp2 = line.strip()
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
            if _retval != None:
                self.append_text("%s" % str(_retval))
            self.append_text("\n> ")
            end = buffer.get_end_iter()
            buffer.place_cursor(end)
            return True
        return False

class TODOGramplet(Gramplet):
    def init(self):
        # GUI setup:
        self.tooltip = _("Enter text")
        self.gui.textview.set_editable(True)
        self.append_text(_("Enter your TODO list here."))

    def on_load(self):
        self.load_data_to_text()

    def on_save(self):
        self.gui.data = [] # clear out old data
        self.save_text_to_data()

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
        ' detached, it will re-opened detached the next time you start '
        'GRAMPS.'
            )
    gui.set_text(text)

class NewsGramplet(Gramplet):
    URL = "http://www.gramps-project.org/wiki/index.php?title=%s&action=raw"

    def init(self):
        self.tooltip = _("Read news from the GRAMPS wiki")

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
        self.set_use_markup(True)
        self.render_text(text)
        
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
        self.tooltip = _("Enter a date, click Run")
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        # label, entry
        description = gtk.TextView()
        description.set_wrap_mode(gtk.WRAP_WORD)
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
        self.gui.scrolledwindow.remove(self.gui.textview)
        self.gui.scrolledwindow.add_with_viewport(vbox)
        vbox.show_all()

    def run(self, obj):
        text = self.entry.get_text()
        date = DateHandler.parser.parse(text)
        run_quick_report_by_name(self.gui.dbstate, 
                                 self.gui.uistate, 
                                 'ageondate', 
                                 date)


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
         )
