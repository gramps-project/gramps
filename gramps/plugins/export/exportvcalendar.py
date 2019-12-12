#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Martin Hawlisch
# Copyright (C) 2005-2006, 2008  Donald N. Allingham
# Copyright (C) 2008  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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

"Export Events to vCalendar."

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
import sys
import time

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
from collections import abc
log = logging.getLogger(".ExportVCal")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gui.plug.export import WriterOptionBox
from gramps.gen.utils.db import family_name
from gramps.gen.lib import Date, EventType
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as _pd


class CalendarWriter:
    def __init__(self, database, filename, user, option_box=None):
        self.db = database
        self.filename = filename
        self.user = user
        self.option_box = option_box
        if isinstance(self.user.callback, abc.Callable):  # is really callable
            self.update = self.update_real
        else:
            self.update = self.update_empty

        self.plist = {}
        self.flist = {}

        self.count = 0
        self.oldval = 0

        self.persons_details_done = []
        self.persons_notes_done = []
        self.person_ids = {}

        if option_box:
            self.option_box.parse_options()
            self.db = option_box.get_filtered_database(self.db)

    def update_empty(self):
        pass

    def update_real(self):
        self.count += 1
        newval = int(100 * self.count / self.total)
        if newval != self.oldval:
            self.user.callback(newval)
            self.oldval = newval

    def writeln(self, text):
        self.g.write('%s\n' % text)

    def export_data(self, filename):

        self.dirname = os.path.dirname(filename)
        try:
            with open(filename, "w", encoding='utf8',
                      newline='\r\n') as self.g:
                self.writeln("BEGIN:VCALENDAR")
                self.writeln("PRODID:-//GNU//Gramps//EN")
                self.writeln("VERSION:2.0")

                p_hndls = self.db.get_person_handles()
                p_hndls.sort()
                f_hndls = self.db.get_family_handles()
                f_hndls.sort()
                self.total = len(p_hndls) + len(f_hndls)
                for key in p_hndls:
                    self.write_person(key)
                    self.update()

                for key in f_hndls:
                    self.write_family(key)
                    self.update()

                self.writeln("END:VCALENDAR")

            return True
        except IOError as msg:
            msg2 = _("Could not create %s") % filename
            self.user.notify_error(msg2, str(msg))
            return False
        except:
            self.user.notify_error(_("Could not create %s") % filename)
            return False

    def write_family(self, family_handle):
        family = self.db.get_family_from_handle(family_handle)
        if family:
            for event_ref in family.get_event_ref_list():
                event = self.db.get_event_from_handle(event_ref.ref)
                if event and event.get_type() == EventType.MARRIAGE:
                    # feature requests 2356, 1657: avoid genitive form
                    text = "%s - %s" % (family_name(family, self.db),
                                        _("Marriage"))
                    self.write_vevent(text, event)

    def write_person(self, person_handle):
        person = self.db.get_person_from_handle(person_handle)
        if person:
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = self.db.get_event_from_handle(birth_ref.ref)
                if birth:
                    # feature requests 2356, 1657: avoid genitive form
                    self.write_vevent("%s - %s" %
                                      (name_displayer.display(person),
                                       _("Birth")), birth)

            death_ref = person.get_death_ref()
            if death_ref:
                death = self.db.get_event_from_handle(death_ref.ref)
                if death:
                    # feature requests 2356, 1657: avoid genitive form
                    self.write_vevent("%s - %s" %
                                      (name_displayer.display(person),
                                       _("Death")), death)

    def format_single_date(self, subdate, thisyear, cal):
        retval = ""
        (day, month, year, sl) = subdate

        if thisyear:
            year = time.localtime().tm_year

        if not cal == Date.CAL_GREGORIAN:
            return ""

        if year > 0:
            if month > 0:
                if day > 0:
                    retval = "%s%02d%02d" % (year, month, day)
        return retval

    def format_date(self, date, thisyear=0):
        retval = ""
        if date.get_modifier() == Date.MOD_TEXTONLY:
            return ""
        elif not date.is_empty():
            mod = date.get_modifier()
            cal = cal = date.get_calendar()
            if mod == Date.MOD_SPAN or mod == Date.MOD_RANGE:
                start = self.format_single_date(date.get_start_date(),
                                                thisyear, cal)
                end = self.format_single_date(date.get_stop_date(),
                                              thisyear, cal)
                if start and end:
                    retval = "DTSTART:%sT000001\nDTEND:%sT235959" % (start,
                                                                     end)
            elif mod == Date.MOD_NONE:
                start = self.format_single_date(date.get_start_date(),
                                                thisyear, cal)
                if start:
                    retval = "DTSTART:%sT000001\nDTEND:%sT235959" % (start,
                                                                     start)
        return retval

    def write_vevent(self, event_text, event):
        date = event.get_date_object()
        place_handle = event.get_place_handle()
        date_string = self.format_date(date, 1)
        if date_string is not "":
            # self.writeln("")
            self.writeln("BEGIN:VEVENT")
            time_s = time.gmtime(event.change)
            self.writeln("DTSTAMP:%04d%02d%02dT%02d%02d%02dZ" % time_s[0:6])
            self.writeln("UID:%s@gramps.com" % event.handle)
            self.writeln(fold("SUMMARY:%s %s" % (date.get_year(), event_text)))
            if place_handle:
                location = _pd.display_event(self.db, event)
                if location:
                    self.writeln("LOCATION:%s" % location)
            self.writeln("RRULE:FREQ=YEARLY")
            self.writeln(date_string)
            self.writeln("END:VEVENT")

# -------------------------------------------------------------------------


def fold(txt):
    """ Limit line length to 75 octets (per RFC 5545) """
    l_len = 0
    text = ''
    for char in txt:
        c_len = len(char.encode('utf8'))
        if c_len + l_len > 75:
            l_len = 1
            text += '\n ' + char
        else:
            l_len += c_len
            text += char
    return text


def exportData(database, filename, user, option_box=None):
    cw = CalendarWriter(database, filename, user, option_box)
    return cw.export_data(filename)
