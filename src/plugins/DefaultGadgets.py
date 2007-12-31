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

__author__ = "Douglas Blank <dblank@cs.brynmawr.edu>"
__version__ = "$Revision: $"

import sys
import os
import re
import time
import string
import urllib

import gen.lib
from DataViews import register, Gadget
from BasicUtils import name_displayer
from QuickReports import run_quick_report_by_name
import DateHandler

#
# Hello World, in Gramps Gadgets
#
# First, you need a function or class that takes a single argument
# a GuiGadget:

#from DataViews import register
#def init(gui):
#    gui.set_text("Hello world!")

# In this function, you can do some things to update the gadget,
# like set text of the main scroll window.

# Then, you need to register the gadget:

#register(type="gadget", # case in-senstitive keyword "gadget"
#         name="Hello World Gadget", # gadget name, unique among gadgets
#         height = 20,
#         content = init, # function/class; takes guigadget
#         title="Sample Gadget", # default title, user changeable
#         )

# There are a number of arguments that you can provide, including:
# name, height, content, title, expand, state, data

# Here is a Gadget object. It has a number of method possibilities:
#  init- run once, on construction
#  active_changed- run when active-changed is triggered
#  db_changed- run when db-changed is triggered
#  main- run once per db change, main process (a generator)

# You should call update() to run main; don't call main directly

class CalendarGadget(Gadget):
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
        print "signal:", signal
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

class LogGadget(Gadget):
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

    def log_person_add(self, handles):
        self.get_person(handles, "person-add")
    def log_person_delete(self, handles):
        self.get_person(handles, "person-delete")
    def log_person_update(self, handles):
        self.get_person(handles, "person-update")
    def log_family_add(self, handles):
        self.append_text("family-add: %s" % handles)
    def log_family_delete(self, handles):
        self.append_text("family-delete: %s" % handles)
    def log_family_update(self, handles):
        self.append_text("family-update: %s" % handles)
    def log_active_changed(self, handles):
        self.get_person([handles], "active-changed")

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

class TopSurnamesGadget(Gadget):
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
            self.append_text("  %d. " % (line + 1))
            self.link(surname, 'Surname', representative_handle[surname])
            self.append_text(", %d%% (%d)\n" % 
                             (int((float(count)/total) * 100), count))
            line += 1
            if line >= self.top_size:
                break
        self.append_text(("\n" + _("Total unique surnames") + ": %d\n") % 
                         total_surnames)
        self.append_text((_("Total people") + ": %d") % total_people)
        
class StatsGadget(Gadget):
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
            try:
                bytes = bytes + posixpath.getsize(photo.get_path())
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

class PythonGadget(Gadget):
    def init(self):
        self.tooltip = _("Enter Python expressions")
        self.env = {"dbstate": self.gui.dbstate,
                    "uistate": self.gui.uistate,
                    "self": self,
                    }
        # GUI setup:
        self.gui.textview.set_editable(True)
        self.set_text("Python %s\n> " % sys.version)
        self.gui.textview.connect('key-press-event', self.on_enter)

    def format_exception(self, max_tb_level=10):
        retval = ''
        cla, exc, trbk = sys.exc_info()
        retval += "ERROR: %s %s" %(cla, exc)
        return retval

    def on_enter(self, widget, event):
        if event.keyval == 65293: # enter, where to get this?
            buffer = widget.get_buffer()
            line_cnt = buffer.get_line_count()
            start = buffer.get_iter_at_line(line_cnt - 1)
            end = buffer.get_end_iter()
            line = buffer.get_text(start, end)
            if line.startswith("> "):
                self.append_text("\n")
                line = line[2:]
            # update states, in case of change:
            self.env["dbstate"] = self.gui.dbstate
            self.env["uistate"] = self.gui.uistate
            _retval = None
            if "_retval" in self.env:
                del self.env["_retval"]
            exp1 = """_retval = """ + string.strip(line)
            exp2 = string.strip(line)
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
                self.append_text("%s\n" % str(_retval))
                self.append_text("> ")
            else:
                self.append_text("> ")
            return True
        return False

class TODOGadget(Gadget):
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
    text = """
Welcome to GRAMPS!

GRAMPS is a software package designed for genealogical research. Although similar to other genealogical programs, GRAMPS offers some unique and powerful features.

GRAMPS is an Open Source Software package, which means you are free to make copies and distribute it to anyone you like. It's developed and maintained by a worldwide team of volunteers whose goal is to make GRAMPS powerful, yet easy to use.

Getting Started

The first thing you must do is to create a new Family Tree. To create a new Family Tree (sometimes called a database) select "Family Trees" from the menu, pick "Manage Family Trees", press "New" and name your database. For more details, please read the User Manual, or the on-line manual at http://gramps-project.org.

You are currently reading from the "My Gramps" page, where you can add your own gadgets.

You can right-click on the background of this page to add additional gadgets and change the number of columns. You can also drag the Properties button to reposition the gadget on this page, and detach the gadget to float above GRAMPS. If you close GRAMPS with a gadget detached, it will re-opened detached the next time you start GRAMPS.

"""
    gui.set_text(text)


class NewsGadget(Gadget):
    URL = "http://www.gramps-project.org/wiki/index.php?title=%s&action=raw"

    def init(self):
        self.tooltip = _("Read news from the GRAMPS wiki")

    def main(self):
        continuation = self.process('News')
        retval = True
        while retval:
            retval, text = continuation.next()
            self.cleanup(text)
            yield True
        self.cleanup(text)
        yield False

    def cleanup(self, text):
        # final text
        text = text.replace("<BR>", "\n")
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        text = text.strip()
        self.set_text(text)
        
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


register(type="gadget", 
         name= "Top Surnames Gadget", 
         tname=_("1Top Surnames Gadget"), 
         height=230,
         content = TopSurnamesGadget,
         title=_("Top Surnames"),
         )

register(type="gadget", 
         name="Statistics Gadget", 
         tname=_("1Statistics Gadget"), 
         height=230,
         expand=True,
         content = StatsGadget,
         title=_("Statistics"),
         )

register(type="gadget", 
         name="Session Log Gadget", 
         tname=_("1Session Log Gadget"), 
         height=230,
         data=['no'],
         content = LogGadget,
         title=_("Session Log"),
         )

register(type="gadget", 
         name="Python Gadget", 
         tname=_("1Python Gadget"), 
         height=250,
         content = PythonGadget,
         title=_("Python Shell"),
         )

register(type="gadget", 
         name=_("TODO Gadget"), 
         tname=_("1TODO Gadget"), 
         height=300,
         expand=True,
         content = TODOGadget,
         title=_("TODO List"),
         )

register(type="gadget", 
         name="Welcome Gadget", 
         tname=_("1Welcome Gadget"), 
         height=300,
         expand=True,
         content = make_welcome_content,
         title=_("Welcome to GRAMPS!"),
         )

register(type="gadget", 
         name="Calendar Gadget", 
         tname=_("1Calendar Gadget"), 
         height=200,
         content = CalendarGadget,
         title=_("Calendar"),
         )

register(type="gadget", 
         name="News Gadget", 
         tname=_("1News Gadget"), 
         height=300,
         expand=True,
         content = NewsGadget,
         title=_("News"),
         )

