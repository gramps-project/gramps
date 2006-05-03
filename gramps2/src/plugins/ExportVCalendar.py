#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Martin Hawlisch
# Copyright (C) 2005-2006  Donald N. Allingham
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
#
# $Id$

"Export Events to vCalendar"

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
from time import localtime

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".ExportVCal")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters import GenericFilter, Rules, build_filter_menu
import const
import Utils
from RelLib import Date
import Errors
from gettext import gettext as _
from QuestionDialog import ErrorDialog
from PluginUtils import register_export

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class CalendarWriterOptionBox:
    """
    Create a VBox with the option widgets and define methods to retrieve
    the options. 
    """
    def __init__(self,person):
        self.person = person

    def get_option_box(self):

        glade_file = "%s/vcalendarexport.glade" % os.path.dirname(__file__)
        if not os.path.isfile(glade_file):
            glade_file = "plugins/vcalendarexport.glade"

        self.topDialog = gtk.glade.XML(glade_file,"calendarExport","gramps")

        filter_obj = self.topDialog.get_widget("filter")
        self.copy = 0

        all = GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(Rules.Everyone([]))

        if self.person:
            des = GenericFilter()
            des.set_name(_("Descendants of %s") %
                         self.person.get_primary_name().get_name())
            des.add_rule(Rules.IsDescendantOf(
                [self.person.get_gramps_id(),1]))

            ans = GenericFilter()
            ans.set_name(_("Ancestors of %s") %
                         self.person.get_primary_name().get_name())
            ans.add_rule(Rules.IsAncestorOf(
                [self.person.get_gramps_id(),1]))
            
            com = GenericFilter()
            com.set_name(_("People with common ancestor with %s") %
                         self.person.get_primary_name().get_name())
            com.add_rule(Rules.HasCommonAncestorWith(
                [self.person.get_gramps_id()]))
            
            self.filter_menu = build_filter_menu(
                [all,des,ans,com])
        else:
            self.filter_menu = build_filter_menu([all])
        filter_obj.set_menu(self.filter_menu)

        the_box = self.topDialog.get_widget('vbox1')
        the_parent = self.topDialog.get_widget('dialog-vbox1')
        the_parent.remove(the_box)
        self.topDialog.get_widget("calendarExport").destroy()
        return the_box

    def parse_options(self):
        self.cfilter = self.filter_menu.get_active().get_data("filter")


class CalendarWriter:
    def __init__(self,database,person,cl=0,filename="",option_box=None):
        self.db = database
        self.person = person
        self.option_box = option_box
        self.cl = cl
        self.filename = filename

        self.plist = {}
        self.flist = {}
        
        self.persons_details_done = []
        self.persons_notes_done = []
        self.person_ids = {}
        
        if not option_box:
            self.cl_setup()
        else:
            self.option_box.parse_options()

            if self.option_box.cfilter == None:
                for p in self.db.get_person_handles(sort_handles=False):
                    self.plist[p] = 1
            else:
                try:
                    for p in self.option_box.cfilter.apply(self.db, self.db.get_person_handles(sort_handles=False)):
                        self.plist[p] = 1
                except Errors.FilterError, msg:
                    (m1,m2) = msg.messages()
                    ErrorDialog(m1,m2)
                    return

            self.flist = {}
            for key in self.plist:
                p = self.db.get_person_from_handle(key)
                for family_handle in p.get_family_handle_list():
                    self.flist[family_handle] = 1
 
    def cl_setup(self):
        for p in self.db.get_person_handles(sort_handles=False):
            self.plist[p] = 1

        self.flist = {}

        for key in self.plist:
            p = self.db.get_person_from_handle(key)
            for family_handle in p.get_family_handle_list():
                self.flist[family_handle] = 1

    def writeln(self,text):
        self.g.write('%s\n' % (text.encode('iso-8859-1')))

    def export_data(self,filename):

        self.dirname = os.path.dirname (filename)
        try:
            self.g = open(filename,"w")
        except IOError,msg:
            msg2 = _("Could not create %s") % filename
            ErrorDialog(msg2,str(msg))
            return 0
        except:
            ErrorDialog(_("Could not create %s") % filename)
            return 0

        self.writeln("BEGIN:VCALENDAR");
        self.writeln("PRODID:-//GNU//Gramps//EN");
        self.writeln("VERSION:1.0");
        for key in self.plist:
            self.write_person(key)

        for key in self.flist:
            self.write_family(key)

        self.writeln("");
        self.writeln("END:VCALENDAR");
        
        self.g.close()
        return 1
    
    def write_family(self,family_handle):
        family = self.db.get_family_from_handle(family_handle)
        if family:
            for event_ref in family.get_event_ref_list():
                event = self.db.get_event_from_handle(event_ref.ref)
                if int(event.get_type()) == RelLib.EventType.MARRIAGE:
                    m_date = event.get_date_object()
                    place_handle = event.get_place_handle()
                    text = _("Marriage of %s") % Utils.family_name(family,self.db)
                    if place_handle:
                        place = self.db.get_place_from_handle(place_handle)
                        self.write_vevent( text, m_date, place.get_title())
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
                        place = self.db.get_place_from_handle(place_handle)
                        self.write_vevent(_("Birth of %s") % person.get_primary_name().get_name(), b_date, place.get_title())
                    else:
                        self.write_vevent(_("Birth of %s") % person.get_primary_name().get_name(), b_date)
                        
            death_ref = person.get_death_ref()
            if death_ref:
                death = self.db.get_event_from_handle(death_ref.ref)
                if death:
                    d_date = death.get_date_object()
                    place_handle = death.get_place_handle()
                    if place_handle:
                        place = self.db.get_place_from_handle(place_handle)
                        self.write_vevent(_("Death of %s") % person.get_primary_name().get_name(), d_date, place.get_title())
                    else:
                        self.write_vevent(_("Death of %s") % person.get_primary_name().get_name(), d_date)

    
    def format_single_date(self,subdate,thisyear,cal):
        retval = ""
        (day,month,year,sl) = subdate

        if thisyear:
            year = localtime().tm_year
        
        if not cal == Date.CAL_GREGORIAN:
            return ""

        if year > 0:
            if month > 0:
                if day > 0:
                    retval = "%s%02d%02d" % (year, month, day)
        return retval

    
    def format_date(self,date,thisyear=0):
        retval = ""
        strval = date.get_text()
        if strval:
            return ""
        elif not date.is_empty():
            mod = date.get_modifier()
            cal = cal = date.get_calendar()
            if mod == Date.MOD_SPAN or mod == Date.MOD_RANGE:
                start = self.format_single_date(date.get_start_date(),thisyear,cal)
                end = self.format_single_date(date.get_stop_date(),thisyear,cal)
                if start and end:
                    retval = "DTSTART:%sT000001\nDTEND:%sT235959" % (start,end)
            elif mod == Date.MOD_NONE:
                start = self.format_single_date(date.get_start_date(),thisyear,cal)
                if start:
                    retval = "DTSTART:%sT000001\nDTEND:%sT235959" % (start,start)
        return retval

    def write_vevent(self, event_text, date, location=""):
        date_string = self.format_date(date)
        if date_string is not "":
            self.writeln("");
            self.writeln("BEGIN:VEVENT");
            self.writeln("SUMMARY:%s" % event_text);
            if location:
                self.writeln("LOCATION:%s" % location);
            self.writeln(date_string)
            self.writeln("END:VEVENT");

            date_string = self.format_date(date,1)
            self.writeln("");
            self.writeln("BEGIN:VEVENT");
            self.writeln("SUMMARY:"+_("Anniversary: %s") % event_text);
            if location:
                self.writeln("LOCATION:%s" % location);
            self.writeln("RRULE:YD1 #0")
            self.writeln(date_string)
            self.writeln("END:VEVENT");

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database,filename,person,option_box):
    ret = 0
    cw = CalendarWriter(database,person,0,filename,option_box)
    ret = cw.export_data(filename)
    return ret

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
_title = _('vCalendar')
_description = _('vCalendar is used in many calendaring and pim applications.')
_config = (_('vCalendar export options'),CalendarWriterOptionBox)
_filename = 'vcs'

register_export(exportData,_title,_description,_config,_filename)
