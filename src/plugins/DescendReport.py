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

"Generate files/Descendant Report"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Report
import BaseDoc
import Errors
import Date
import Sort
from QuestionDialog import ErrorDialog
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GTK/GNOME modules
#
#------------------------------------------------------------------------
import gtk

_BORN = _('b.')
_DIED = _('d.')

#------------------------------------------------------------------------
#
# DescendantReport
#
#------------------------------------------------------------------------
class DescendantReport:

    def __init__(self,database,person,max,pgbrk,doc,output,newpage=0):
        self.database = database
        self.creator = database.get_researcher().get_name()
        self.name = output
        self.person = person
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
        sort = Sort.Sort(self.database)
        self.by_birthdate = sort.by_birthdate
        
    def dump_dates(self, person):
        birth_id = person.get_birth_id()
        if birth_id:
            birth = self.database.find_event_from_id(birth_id).get_date_object().get_start_date()
            birth_year_valid = birth.get_year_valid()
        else:
            birth_year_valid = 0

        death_id = person.get_death_id()
        if death_id:
            death = self.database.find_event_from_id(death_id).get_date_object().get_start_date()
            death_year_valid = death.get_year_valid()
        else:
            death_year_valid = 0

        if birth_year_valid or death_year_valid:
            self.doc.write_text(' (')
            if birth_year_valid:
                self.doc.write_text("%s %d" % (_BORN,birth.get_year()))
            if death_year_valid:
                if birth_year_valid:
                    self.doc.write_text(', ')
                self.doc.write_text("%s %d" % (_DIED,death.get_year()))
            self.doc.write_text(')')
        
    def write_report(self):
        if self.newpage:
            self.doc.page_break()
        self.doc.start_paragraph("DR-Title")
        name = self.person.get_primary_name().get_regular_name()
        self.doc.write_text(_("Descendants of %s") % name)
        self.dump_dates(self.person)
        self.doc.end_paragraph()
        self.dump(0,self.person)
        if self.standalone:
            self.doc.close()

    def dump(self,level,person):

        if level != 0:
            self.doc.start_paragraph("DR-Level%d" % level)
            self.doc.write_text("%d." % level)
            self.doc.write_text(person.get_primary_name().get_regular_name())
            self.dump_dates(person)
            self.doc.end_paragraph()

        if level >= self.max_generations:
            return
        
        childlist = []
        for family_id in person.get_family_id_list():
            family = self.database.find_family_from_id(family_id)
            for child_id in family.get_child_id_list():
                childlist.append(child_id)

        childlist.sort(self.by_birthdate)
        for child_id in childlist:
            child = self.database.find_person_from_id(child_id)
            self.dump(level+1,child)

#------------------------------------------------------------------------
#
# DescendantReportDialog
#
#------------------------------------------------------------------------
class DescendantReportDialog(Report.TextReportDialog):
    def __init__(self,database,person):
        Report.TextReportDialog.__init__(self,database,person)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Descendant Report"),_("Text Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Descendant Report for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Descendant Report")

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "descend_report.xml"
    
    def make_default_style(self):
        _make_default_style(self.default_style)

    def make_report(self):
        """Create the object that will produce the Descendant Report.
        All user dialog has already been handled and the output file
        opened."""
        try:
            MyReport = DescendantReport(self.db, self.person,
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
    DescendantReportDialog(database,person)

#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "descend_report.xml"
_style_name = "default" 

_person_id = ""
_max_gen = 1
_pg_brk = 0
_options = ( _person_id, _max_gen, _pg_brk )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class DescendantBareReportDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.get_person(self.options[0])
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
        return "%s - GRAMPS Book" % (_("Descendant Report"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Descendant Report for GRAMPS Book") 

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
        self.options = ( self.person.get_id(), self.max_gen, self.pg_brk )
        self.style_name = self.selected_style.get_name()

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Descendant Report using the options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.get_person(options[0])
        max_gen = int(options[1])
        pg_brk = int(options[2])
        return DescendantReport(database, person, max_gen,
                                   pg_brk, doc, None, newpage )
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
    """Make the default output style for the Descendant Report."""
    f = BaseDoc.FontStyle()
    f.set_size(14)
    f.set_type_face(BaseDoc.FONT_SANS_SERIF)
    f.set_bold(1)
    p = BaseDoc.ParagraphStyle()
    p.set_header_level(1)
    p.set_font(f)
    p.set_description(_("The style used for the title of the page."))
    default_style.add_style("DR-Title",p)

    f = BaseDoc.FontStyle()
    for i in range(1,32):
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_left_margin(min(10.0,float(i-1)))
        p.set_description(_("The style used for the level %d display.") % i)
        default_style.add_style("DR-Level%d" % i,p)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_report, register_book_item

register_report(
    report,
    _("Descendant Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description=_("Generates a list of descendants of the active person"),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Descendant Report"), 
    _("Text"),
    DescendantBareReportDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
    )
