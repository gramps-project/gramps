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
from time import localtime

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
import collections
log = logging.getLogger(".ExportVCal")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gui.plug.export import WriterOptionBox
from gramps.gen.utils.db import family_name
from gramps.gen.lib import Date, EventType
from gramps.gui.glade import Glade
from gramps.gen.display.place import displayer as _pd

class CalendarWriter(object):
    def __init__(self, database, filename, user, option_box=None):
        self.db = database
        self.filename = filename
        self.user = user
        self.option_box = option_box
        if isinstance(self.user.callback, collections.Callable): # callback is really callable
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

        self.dirname = os.path.dirname (filename)
        try:
            self.g = open(filename,"w")
        except IOError as msg:
            msg2 = _("Could not create %s") % filename
            self.user.notify_error(msg2, str(msg))
            return False
        except:
            self.user.notify_error(_("Could not create %s") % filename)
            return False

        self.writeln("BEGIN:VCALENDAR")
        self.writeln("PRODID:-//GNU//Gramps//EN")
        self.writeln("VERSION:1.0")

        self.total = (len([x for x in self.db.iter_person_handles()]) + 
                      len([x for x in self.db.iter_family_handles()]))
        for key in self.db.iter_person_handles():
            self.write_person(key)
            self.update()

        for key in self.db.iter_family_handles():
            self.write_family(key)
            self.update()

        self.writeln("")
        self.writeln("END:VCALENDAR")
        
        self.g.close()
        return True
    
    def write_family(self, family_handle):
        family = self.db.get_family_from_handle(family_handle)
        if family:
            for event_ref in family.get_event_ref_list():
                event = self.db.get_event_from_handle(event_ref.ref)
                if event.get_type() == EventType.MARRIAGE:
                    m_date = event.get_date_object()
                    place_handle = event.get_place_handle()
                    # feature requests 2356, 1657: avoid genitive form
                    text = _("Marriage of %s") % family_name(family, self.db)
                    if place_handle:
                        place_title = _pd.display_event(self.db, event)
                        self.write_vevent( text, m_date, place_title)
                    else:
                        self.write_vevent( text, m_date)
                    
    def write_person(self, person_handle):
        person = self.db.get_person_from_handle(person_handle)
        if person:
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = self.db.get_event_from_handle(birth_ref.ref)
                if birth:
                    b_date = birth.get_date_object()
                    place_handle = birth.get_place_handle()
                    if place_handle:
                        # feature requests 2356, 1657: avoid genitive form
                        place_title = _pd.display_event(self.db, birth)
                        self.write_vevent(_("Birth of %s") % 
                            person.get_primary_name().get_name(), 
                            b_date, place_title)
                    else:
                        # feature requests 2356, 1657: avoid genitive form
                        self.write_vevent(_("Birth of %s") %
                            person.get_primary_name().get_name(), 
                            b_date)
                        
            death_ref = person.get_death_ref()
            if death_ref:
                death = self.db.get_event_from_handle(death_ref.ref)
                if death:
                    d_date = death.get_date_object()
                    place_handle = death.get_place_handle()
                    if place_handle:
                        # feature requests 2356, 1657: avoid genitive form
                        place_title = _pd.display_event(self.db, death)
                        self.write_vevent(_("Death of %s") % 
                            person.get_primary_name().get_name(), 
                            d_date, 
                            place_title)
                    else:
                        # feature requests 2356, 1657: avoid genitive form
                        self.write_vevent(_("Death of %s") % 
                            person.get_primary_name().get_name(), 
                            d_date)

    
    def format_single_date(self, subdate, thisyear, cal):
        retval = ""
        (day, month, year, sl) = subdate

        if thisyear:
            year = localtime().tm_year
        
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

    def write_vevent(self, event_text, date, location=""):
        date_string = self.format_date(date)
        if date_string is not "":
            self.writeln("")
            self.writeln("BEGIN:VEVENT")
            self.writeln("SUMMARY:%s" % event_text)
            if location:
                self.writeln("LOCATION:%s" % location)
            self.writeln(date_string)
            self.writeln("END:VEVENT")

            date_string = self.format_date(date, 1)
            self.writeln("")
            self.writeln("BEGIN:VEVENT")
            self.writeln("SUMMARY:"+_("Anniversary: %s") % event_text)
            if location:
                self.writeln("LOCATION:%s" % location)
            self.writeln("RRULE:FREQ=YEARLY")
            self.writeln(date_string)
            self.writeln("END:VEVENT")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database, filename, user, option_box=None):
    cw = CalendarWriter(database, filename, user, option_box)
    return cw.export_data(filename)
