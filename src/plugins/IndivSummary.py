#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

"Generate files/Individual Summary"

import RelLib
import const
import os
import string
import intl

_ = intl.gettext

from TextDoc import *
from StyleEditor import *
from Report import *

import gtk
import libglade

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndivSummary:

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,database,person,output,document):
        self.d = document
        
        c = database.getResearcher().getName()
        self.d.creator(c)
        self.map = {}
        self.database = database
        self.person = person
        self.output = output
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0,20)
        tbl.set_column_width(1,80)
        self.d.add_table_style("IndTable",tbl)

        cell = TableCellStyle()
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        self.d.add_cell_style("TableHead",cell)

        cell = TableCellStyle()
        self.d.add_cell_style("NormalCell",cell)

        cell = TableCellStyle()
	cell.set_longlist(1)
        self.d.add_cell_style("ListCell",cell)

        self.d.open(self.output)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        self.d.close()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_fact(self,event):
        if event == None:
            return
        name = event.getName()
        date = event.getDate()
        place = event.getPlaceName()
        description = event.getDescription()
        if date == "":
            if place == "":
                return
            else:
                val = place + ". " + description
        else:
            if place == "":
                val = date + ". " + description
            else:
                val = date + " in " + place + ". " +  description

        self.d.start_row()
        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text(name)
        self.d.end_paragraph()
        self.d.end_cell()

        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text(val)
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_families(self):

        self.d.start_paragraph("Normal")
        self.d.end_paragraph()
        self.d.start_table("three","IndTable")
        self.d.start_row()
        self.d.start_cell("TableHead",2)
        self.d.start_paragraph("TableTitle")
        self.d.write_text(_("Marriages/Children"))
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()
        
        for family in self.person.getFamilyList():
            if self.person == family.getFather():
                spouse = family.getMother()
            else:
                spouse = family.getFather()
            self.d.start_row()
            self.d.start_cell("NormalCell",2)
            self.d.start_paragraph("Spouse")
            if spouse:
                self.d.write_text(spouse.getPrimaryName().getRegularName())
            else:
                self.d.write_text(_("unknown"))
            self.d.end_paragraph()
            self.d.end_cell()
            self.d.end_row()
            
            for event in family.getEventList():
                self.write_fact(event)

            child_list = family.getChildList()
            if len(child_list) > 0:
                self.d.start_row()
                self.d.start_cell("NormalCell")
                self.d.start_paragraph("Normal")
                self.d.write_text(_("Children"))
                self.d.end_paragraph()
                self.d.end_cell()

                self.d.start_cell("ListCell")
                self.d.start_paragraph("Normal")
                
                first = 1
                for child in family.getChildList():
                    if first == 1:
                        first = 0
                    else:
                        self.d.write_text('\n')
                    self.d.write_text(child.getPrimaryName().getRegularName())
                self.d.end_paragraph()
                self.d.end_cell()
                self.d.end_row()
        self.d.end_table()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):
        photo_list = self.person.getPhotoList()

        name = self.person.getPrimaryName().getRegularName()
        self.d.start_paragraph("Title")
        self.d.write_text(_("Summary of %s") % name)
        self.d.end_paragraph()

        self.d.start_paragraph("Normal")
        self.d.end_paragraph()

        if len(photo_list) > 0:
            object = photo_list[0].getReference()
            if object.getMimeType()[0:5] == "image":
                file = object.getPath()
                self.d.start_paragraph("Normal")
                self.d.add_photo(file,"row",4.0,4.0)
                self.d.end_paragraph()

        self.d.start_table("one","IndTable")

        self.d.start_row()
        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text("%s:" % _("Name"))
        self.d.end_paragraph()
        self.d.end_cell()

        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text(self.person.getPrimaryName().getRegularName())
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()

        self.d.start_row()
        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text("%s:" % _("Gender"))
        self.d.end_paragraph()
        self.d.end_cell()

        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        if self.person.getGender() == RelLib.Person.male:
            self.d.write_text(_("Male"))
        else:
            self.d.write_text(_("Female"))
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()

        family = self.person.getMainParents()
        if family:
            father_inst = family.getFather()
            if father_inst:
                father = father_inst.getPrimaryName().getRegularName()
            else:
                father = ""
            mother_inst = family.getMother()
            if mother_inst:
                mother = mother_inst.getPrimaryName().getRegularName()
            else:
                mother = ""
        else:
            father = ""
            mother = ""

        self.d.start_row()
        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text("%s:" % _("Father"))
        self.d.end_paragraph()
        self.d.end_cell()

        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text(father)
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()

        self.d.start_row()
        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text("%s:" % _("Mother"))
        self.d.end_paragraph()
        self.d.end_cell()

        self.d.start_cell("NormalCell")
        self.d.start_paragraph("Normal")
        self.d.write_text(mother)
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()
        self.d.end_table()

        self.d.start_paragraph("Normal")
        self.d.end_paragraph()
        
        self.d.start_table("two","IndTable")
        self.d.start_row()
        self.d.start_cell("TableHead",2)
        self.d.start_paragraph("TableTitle")
        self.d.write_text(_("Individual Facts"))
        self.d.end_paragraph()
        self.d.end_cell()
        self.d.end_row()

        event_list = [ self.person.getBirth(), self.person.getDeath() ]
        event_list = event_list + self.person.getEventList()
        for event in event_list:
            self.write_fact(event)
        self.d.end_table()

        self.write_families()
        self.end()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndivSummaryDialog(TextReportDialog):
    def __init__(self,database,person):
        TextReportDialog.__init__(self,database,person)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" %(_("Individual Summary"),_("Text Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Individual Summary for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Individual Summary")
    
    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "family_group.xml"
    
    def doc_uses_tables(self):
        """This report requires table support."""
        return 1

    #------------------------------------------------------------------------
    #
    # Create output styles appropriate to this report.
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        """Make the default output style for the Individual Summary Report."""
        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(16)
        p = ParagraphStyle()
        p.set_alignment(PARA_ALIGN_CENTER)
        p.set_font(font)
        self.default_style.add_style("Title",p)
        
        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        font.set_italic(1)
        p = ParagraphStyle()
        p.set_font(font)
        self.default_style.add_style("TableTitle",p)
        
        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        p = ParagraphStyle()
        p.set_font(font)
        self.default_style.add_style("Spouse",p)
    
        font = FontStyle()
        font.set_size(12)
        p = ParagraphStyle()
        p.set_font(font)
        self.default_style.add_style("Normal",p)
    

    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window
    #
    #------------------------------------------------------------------------
    def setup_report_options(self):
        """The 'Report Options' frame is not used in this dialog."""
        pass

    #------------------------------------------------------------------------
    #
    # Create the contents of the report.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the object that will produce the Ancestor Chart.
        All user dialog has already been handled and the output file
        opened."""
        MyReport = IndivSummary(self.db, self.person, self.target_path, self.doc)
        MyReport.setup()
        MyReport.write_report()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    IndivSummaryDialog(database,person)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_xpm_image():
    return [
        "48 48 33 1",
        " 	c None",
        ".	c #312D2A",
        "+	c #4773AA",
        "@	c #A8A7A5",
        "#	c #BABAB6",
        "$	c #CECECE",
        "%	c #ECDECB",
        "&	c #5C5C60",
        "*	c #7C7262",
        "=	c #F2EADE",
        "-	c #867A6F",
        ";	c #8E887E",
        ">	c #E2CAA2",
        ",	c #565354",
        "'	c #4C4E51",
        ")	c #6D655E",
        "!	c #B69970",
        "~	c #F6F2EE",
        "{	c #9E9286",
        "]	c #416CA3",
        "^	c #3D4557",
        "/	c #A29E96",
        "(	c #FAFAFA",
        "_	c #BA7458",
        ":	c #C67C5E",
        "<	c #BDA37E",
        "[	c #CECABE",
        "}	c #A26E62",
        "|	c #E6E2E2",
        "1	c #423E43",
        "2	c #966A60",
        "3	c #D2D2D2",
        "4	c #E5D2B8",
        "                                                ",
        "                                                ",
        "             ;-;-----***)*))))&,&)*             ",
        "             -##############@#@/;&,*            ",
        "             -#((((((((((((((=|$#;;{,           ",
        "             ;#(((((((((((((((~|3/*[{1          ",
        "             -#((((((((((((((((~|3,|[;.         ",
        "             -#((((((((@/@@@@@@/@/'(|[;.        ",
        "             -#((((((((((((((((((~'((|[;.       ",
        "             -#(((((((((((]+]+]]+('=((|[;1      ",
        "             -#(((((((((((]+]}2&+('|=((|[{,     ",
        "             *#(((((((((((]+}<:-+('[|~((|#{)    ",
        "             *#(((((((((((+]2_:)+('...1'&*-)*   ",
        "             -#(((((((((((]&1(_&+(3@#//--)&1)   ",
        "             *#~((((((((((+]1}/^]((|$##/;--'1   ",
        "             *#(((((((((((]]^)11,(((|$[#@/;)1   ",
        "             *#(((((((((((]^.^^&&((~=|$[#@/*.   ",
        "             *#(((((((((((((~(((((((|$[$[#/-.   ",
        "             *#~(((((((((((((((((~~~~||$[[@;.   ",
        "             )#((((@@@@@@/@@/@/@@@@///{;[[[;.   ",
        "             )#(((((((((((((((((~~~~==|$$[#;.   ",
        "             )#((((@/@@/@@@@@@@@@//////{4>3{.   ",
        "             )#(((((((((((((((~~~~==|=||%$[{.   ",
        "             )#((((@@@@@/@@@///////////{43>/.   ",
        "             )#((((((((((((((~~~~~==|||%>4[!.   ",
        "             )#((((@/@@@@@//~~~~======%%%43{.   ",
        "             )#((((((((((((~~~~=|==||=%%%44!.   ",
        "             ,#((((@@/@@/@/@////////{/{{%4$!.   ",
        "             )#~((((((((~~~~~~==||%=%=%%44>/.   ",
        "             ,#((((/@@//@///////////{{{{%4>!.   ",
        "             )#((((((((~~~=~||=|%%%%%4%%%44{.   ",
        "             ,#((((@@@/@/////////{{{{{{{444!.   ",
        "             &#(((((~~~~~|~|||%%|%%%%44444%!.   ",
        "             ,#(((~/@//////////{{{{{{;{;4>4!.   ",
        "             ,#(((~~~~=~|==|%|=%%%4%%44444>!.   ",
        "             &#(((~//////////{{{{{{{;{;{4>><.   ",
        "             ,#(~~~~~~==||%|%%%%%%44444>4>>!.   ",
        "             '#~~~~///////{{{{{{{;!;{;;;>>>!.   ",
        "             ,#~~~~||=||%|%=%%4%444>44>>>>>!.   ",
        "             '#~~~~====%=%=%4%%444444>>>>>>!.   ",
        "             '@~~====|%=%%%%%4%444>>4>>>>>>!.   ",
        "             ,@~======%%%%%%>%%4444>>>>>>>>!.   ",
        "             '#====||=%%%%4%44444>4>>>>>>>>!.   ",
        "             ,@##@<#<<#@<<<<<<<<<<!<!!:!!!!!.   ",
        "             ................................   ",
        "                                                ",
        "                                                ",
        "                                                "]

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Individual Summary"),
    status=(_("Beta")),
    category=_("Text Reports"),
    description=_("Produces a detailed report on the selected person."),
    xpm=get_xpm_image()
    )








