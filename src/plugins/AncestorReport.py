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
from gettext import gettext as _

_dd = DateHandler.create_display()

#------------------------------------------------------------------------
#
# AncestorReport
#
#------------------------------------------------------------------------
class AncestorReport(Report.Report):

    def __init__(self,database,person,max,pgbrk,doc,output,newpage=0):
        self.map = {}
        self.database = database
        self.start = person
        self.max_generations = max
        self.pgbrk = pgbrk
        self.doc = doc
        self.newpage = newpage
        if output:
            self.standalone = 1
            self.doc.open(output)
            self.doc.init()
        else:
            self.standalone = 0
        
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

        if self.newpage:
            self.doc.page_break()

        self.filter(self.start.get_handle(),1)

        name = self.start.get_primary_name().get_regular_name()
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
        if self.standalone:
            self.doc.close()
 

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorReportDialog(Report.TextReportDialog):

    report_options = {}

    def __init__(self,database,person):
        Report.TextReportDialog.__init__(self,database,person,self.report_options)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Ahnentafel Report"),_("Text Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Ahnentafel Report for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Ahnentafel Report")

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "ancestor_report.xml"
    
    def make_default_style(self):
        _make_default_style(self.default_style)

    def make_report(self):
        """Create the object that will produce the Ahnentafel Report.
        All user dialog has already been handled and the output file
        opened."""
        try:
            MyReport = AncestorReport(self.db, self.person,
                self.max_gen, self.pg_brk, self.doc, self.target_path)
            MyReport.write_report()
        except Errors.ReportError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# Standalone report function
#
#------------------------------------------------------------------------
def report(database,person):
    AncestorReportDialog(database,person)


#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "ancestor_report.xml"
_style_name = "default" 

_person_handle = ""
_max_gen = 10
_pg_brk = 0
_options = ( _person_handle, _max_gen, _pg_brk )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class AncestorBareReportDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.get_person_from_handle(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)

        self.max_gen = int(self.options[1]) 
        self.pg_brk = int(self.options[2])
        self.new_person = None

        self.generations_spinbox.set_value(self.max_gen)
        self.pagebreak_checkbox.set_active(self.pg_brk)
        
        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        _make_default_style(self.default_style)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("Ahnentafel Report"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Ahnentafel Report for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def on_cancel(self, obj):
        pass

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        self.parse_report_options_frame()
        
        if self.new_person:
            self.person = self.new_person
        self.options = ( self.person.get_handle(), self.max_gen, self.pg_brk )
        self.style_name = self.selected_style.get_name() 

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Ahnentafel Report using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.get_person_from_handle(options[0])
        max_gen = int(options[1])
        pg_brk = int(options[2])
        return AncestorReport(database, person, max_gen, pg_brk, doc, None, newpage )
    except Errors.ReportError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except Errors.FilterError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def _make_default_style(default_style):
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
from Plugins import register_report, register_book_item

register_report(
    report,
    _("Ahnentafel Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description= _("Produces a textual ancestral report"),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Ahnentafel Report"), 
    _("Text"),
    AncestorBareReportDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
   )
