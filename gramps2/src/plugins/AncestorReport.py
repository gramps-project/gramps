#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

"Text Reports/Ahnentafel Report"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import string
from gettext import gettext as _

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import Report
import BaseDoc
import RelLib
import Errors
import DateHandler
from QuestionDialog import ErrorDialog
import ReportOptions
import const

_dd = DateHandler.displayer

#------------------------------------------------------------------------
#
# AncestorReport
#
#------------------------------------------------------------------------
class AncestorReport(Report.Report):

    def __init__(self,database,person,options_class):
        """
        Creates the AncestorReport object that produces the Ahnentafel report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        max_gen   - Maximum number of generations to include.
        pg_breaks - Whether to include page breaks between generations.
        document  - BaseDoc instance for the output file. Any class derived
                    from BaseDoc may be used
        output    - name of the output file. 
                    None if report is not a standalone, in which case
                    somebody must take care of opening and initializing report
                    prior to writing.
        newpage   - if True, newpage is made before writing a report

        """

        Report.Report.__init__(self,database,person,options_class)

        self.map = {}
        (self.max_generations,self.pgbrk) \
                        = options_class.get_report_generations()

    def filter(self,person_handle,index,generation=1):
        if not person_handle or generation >= self.max_generations:
            return
        self.map[index] = person_handle

        person = self.database.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            self.filter(family.get_father_handle(),index*2,generation+1)
            self.filter(family.get_mother_handle(),(index*2)+1,generation+1)

    def write_report(self):

        self.filter(self.start_person.get_handle(),1)

        name = self.start_person.get_primary_name().get_regular_name()
        self.doc.start_paragraph("AHN-Title")
        title = _("Ahnentafel Report for %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()
    
        keys = self.map.keys()
        keys.sort()
        generation = 0

        for key in keys :
            if generation == 0 or key >= ( 1 << 30):
                if self.pgbrk and generation > 0:
                    self.doc.page_break()
                self.doc.start_paragraph("AHN-Generation")
                t = _("%s Generation") % AncestorReport.gen[generation+1]
                self.doc.write_text(t)
                self.doc.end_paragraph()
                generation = generation + 1

            self.doc.start_paragraph("AHN-Entry","%s." % str(key))
            person_handle = self.map[key]
            person = self.database.get_person_from_handle(person_handle)
            name = person.get_primary_name().get_regular_name()
        
            self.doc.start_bold()
            self.doc.write_text(name)
            self.doc.end_bold()
            if name[-1:] == '.':
                self.doc.write_text(" ")
            else:
                self.doc.write_text(". ")

            # Check birth record
        
            birth_handle = person.get_birth_handle()
            if birth_handle:
                birth = self.database.get_event_from_handle(birth_handle)
                date = birth.get_date_object()
                date_text = _dd.display(date)
                place_handle = birth.get_place_handle()
                if place_handle:
                    place = self.database.get_place_from_handle(place_handle).get_title()
                else:
                    place = u''
                if place[-1:] == '.':
                    place = place[:-1]
                if date_text != "" or place_handle:
                    if date_text != "":
                        if date.get_day_valid() and date.get_month_valid():
                            if place != "":
                                t = _("%s was born on %s in %s. ") % \
                                    (name,date_text,place)
                            else:
                                t = _("%s was born on %s. ") % \
                                    (name,date_text)
                        else:
                            if place != "":
                                t = _("%s was born in the year %s in %s. ") % \
                                    (name,date_text,place)
                            else:
                                t = _("%s was born in the year %s. ") % \
                                    (name,date_text)
                        self.doc.write_text(t)

            buried = None
            for event_handle in person.get_event_list():
                event = self.database.get_event_from_handle(event_handle)
                if string.lower(event.get_name()) == "burial":
                    buried = event
        
            death_handle = person.get_death_handle()
            if death_handle:
                death = self.database.get_event_from_handle(death_handle)
                date = death.get_date_object()
                date_text = _dd.display(date)
                place_handle = death.get_place_handle()
                if place_handle:
                    place = self.database.get_place_from_handle(place_handle).get_title()
                else:
                    place = u''
                if place[-1:] == '.':
                    place = place[:-1]
                if date_text != "" or place_handle:
                    if person.get_gender() == RelLib.Person.male:
                        male = 1
                    else:
                        male = 0

                    if date_text != "":
                        if date.get_day_valid() and date.get_month_valid():
                            if male:
                                if place != "":
                                    t = _("He died on %s in %s") % \
                                        (date_text,place)
                                else:
                                    t = _("He died on %s") % date_text
                            else:
                                if place != "":
                                    t = _("She died on %s in %s") % \
                                        (date_text,place)
                                else:
                                    t = _("She died on %s") % date_text
                        else:
                            if male:
                                if place != "":
                                    t = _("He died in the year %s in %s") % \
                                        (date_text,place)
                                else:
                                    t = _("He died in the year %s") % date_text
                            else:
                                if place != "":
                                    t = _("She died in the year %s in %s") % \
                                        (date_text,place)
                                else:
                                    t = _("She died in the year %s") % date_text

                        self.doc.write_text(t)

                    if buried:
                        date = buried.get_date_object()
                        date_text = _dd.display(date)
                        place_handle = buried.get_place_handle()
                        if place_handle:
                            place = self.database.get_place_from_handle(place_handle).get_title()
                        else:
                            place = u''
                        if place[-1:] == '.':
                            place = place[:-1]
                        if date_text != "" or place_handle:
                            if date_text != "":
                                if date.get_day_valid() and date.get_month_valid():
                                    if place != "":
                                        t = _(", and was buried on %s in %s.") % \
                                            (date_text,place)
                                    else:
                                        t = _(", and was buried on %s.") % date_text
                                else:
                                    if place != "":
                                        t = _(", and was buried in the year %s in %s.") % \
                                            (date_text,place)
                                    else:
                                        t = _(", and was buried in the year %s.") % \
                                            date_text
                            else:
                                t = _(" and was buried in %s.") % place
                        self.doc.write_text(t)
                    else:
                        self.doc.write_text(".")
                        
            self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'max_gen'       : 10,
            'page_breaks'    : 0,
        }

    def make_default_style(self,default_style):
        """Make the default output style for the Ahnentafel report."""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set(pad=0.5)
        para.set_description(_('The style used for the title of the page.'))
        default_style.add_style("AHN-Title",para)
    
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_description(_('The style used for the generation header.'))
        default_style.add_style("AHN-Generation",para)
    
        para = BaseDoc.ParagraphStyle()
        para.set(first_indent=-1.0,lmargin=1.0,pad=0.25)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("AHN-Entry",para)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_report
register_report(
    name = 'ancestor_report',
    category = const.CATEGORY_TEXT,
    report_class = AncestorReport,
    options_class = AncestorOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("Ahnentafel Report"),
    status=(_("Beta")),
    description= _("Produces a textual ancestral report"),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )
