#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

"Generate files/Descendant Report"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
import sort

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Report
import BaseDoc
import Errors

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
        
    def dump_dates(self, person):
        birth = person.get_birth().get_date_object().get_start_date()
        death = person.get_death().get_date_object().get_start_date()
        if birth.getYearValid() or death.getYearValid():
            self.doc.write_text(' (')
            if birth.getYearValid():
                self.doc.write_text("%s %d" % (_BORN,birth.getYear()))
            if death.getYearValid():
                if birth.getYearValid():
                    self.doc.write_text(', ')
                self.doc.write_text("%s %d" % (_DIED,death.getYear()))
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
        for family in person.get_family_id_list():
            for child in family.get_child_id_list():
                childlist.append(child)

        childlist.sort(sort.by_birthdate)
        for child in childlist:
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
def get_xpm_image():
    return [
        "48 48 33 1",
        " 	c None",
        ".	c #1A1A1A",
        "+	c #6A665E",
        "@	c #A6A6A6",
        "#	c #BABAB6",
        "$	c #E9D9C0",
        "%	c #E6E6E6",
        "&	c #7A7262",
        "*	c #867A6E",
        "=	c #C2C2BE",
        "-	c #5C5854",
        ";	c #898783",
        ">	c #EEEEEC",
        ",	c #B2966E",
        "'	c #4E4E4E",
        ")	c #BCA076",
        "!	c #FAFAFA",
        "~	c #CECBC1",
        "{	c #E2CBA5",
        "]	c #DAD6D1",
        "^	c #D2D1D0",
        "/	c #9E9286",
        "(	c #ECE1D1",
        "_	c #423E3E",
        ":	c #A29E96",
        "<	c #B7AC9A",
        "[	c #DAD2C6",
        "}	c #E6E2E2",
        "|	c #E1DFDC",
        "1	c #322E2A",
        "2	c #E6D2B6",
        "3	c #F5F2EF",
        "4	c #F1EADE",
        "                                                ",
        "                                                ",
        "             ;*;*****&&&+&++++---+&             ",
        "             *##############<#<:;--&            ",
        "             *#!!!!!!!!!!!!!!4}^#;;/'           ",
        "             ;#!!!!!!!!!!!!!!!3}^@&~/_          ",
        "             *#!!!!!!!!!!!!!!!!3}^-%~;1         ",
        "             *#!!!!@@@@@@@@@@@@@@@'!}~;1        ",
        "             *#!!!!!!!!!!!!!!!!3!3'!!}~;1       ",
        "             *#!!!!!!!!!!!!!!!!!!!'4!!|~;_      ",
        "             *#!!!!3!!!!!!!!!!!!!!'}4!!}~/'     ",
        "             &#!!!!@@:@:@:@:@@@!!3'~}3!!}#/+    ",
        "             &#!!!!!!!!!!!!!!!!!!!'..1_'-&*+&   ",
        "             *#!!!!!!!!@@@@@:@@@@%!3#@:;*+-_+   ",
        "             &#!!!!!!!!!!!!!!!!!!!!>|~=:;;*'_   ",
        "             &#!!!!!!!!@:@@@@:@@@^|>%^~#::;+_   ",
        "             &#!!!!!!!!!!!!!!!!!!!!3%>^~#@:&1   ",
        "             &#!!!!!!!!@@@@@@@@@@%>3%|~^~#@*1   ",
        "             &<!!!!!!!!!!!!!!!!!!33!3>>]=~<;1   ",
        "             +#!!!!@@@@@:@@@:@]%33>>>>>[~~~;1   ",
        "             +#!!!!!!!!!!!!!!!!!33333>}^[=#;1   ",
        "             +#!!!!!!!!@@@@@@:@@@]>>>44]2{[/1   ",
        "             +#!!!!!!!!!!!!!!!33333444}(([~/1   ",
        "             +#!!!!33!3@@@@@@:@::]}|}||[2^{:1   ",
        "             +#!!!!!!!!!!!!!!>3333>4}44$[2~,1   ",
        "             +#!!!!!!!!33!>@@@@@@@@@@^}|${[/1   ",
        "             +#!!!!!!!!!!!!33334444(((44$2[,1   ",
        "             -#!!!!3333333%:::::::::/]||$2^,1   ",
        "             +#!!!!!!!!!3333>>44|(((((4($2{:1   ",
        "             -#!!!!!!!!:@@:::::::~]}}|$$$22,1   ",
        "             +#!!!!!!!!33333(44}44(44((($22/1   ",
        "             -#!!!!@@@:@::::::]}|||$||$]222)1   ",
        "             -#!!!!!33333(>4}444((($$$22222,1   ",
        "             -#!!!!!!!!::::::/://]$$$$($2{2,1   ",
        "             -#!!!333333444|((((($$$$[2$22{)1   ",
        "             -#!!!33334::/:::////[[]$2$22{{)1   ",
        "             '#!33333334}(((((($$$2222$22{{,1   ",
        "             -#33333333:::///////{2[{2[{{{{)1   ",
        "             '#3333%44}4((4(($$$$2222222{{{,1   ",
        "             '#33334444(((((2$$222222{{{{{{,1   ",
        "             '<334444((((($$$2$222{{2{{{{{{,1   ",
        "             -@3444444((($4$$$$2222{{{{{{{{,1   ",
        "             '#4444(((4$($$$$2$2${2{{{{{{{{,1   ",
        "             '<##<<<<<<<)))<)))))),,,,,,,,,,1   ",
        "             11111111111111111111111111.11111   ",
        "                                                ",
        "                                                ",
        "                                                "]

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
    xpm=get_xpm_image(),
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
