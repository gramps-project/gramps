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

"Generate files/Family Group Report"

import RelLib
import os
import intl
_ = intl.gettext

from Report import *
from TextDoc import *

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FamilyGroup:

    def __init__(self,database,family,output,doc):
        self.db = database
        self.family = family
        self.output = output
        self.doc = doc


        cell = TableCellStyle()
        cell.set_padding(0.2)
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('ParentHead',cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('TextContents',cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(0)
        cell.set_left_border(1)
        cell.set_padding(0.1)
        self.doc.add_cell_style('TextChild1',cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        cell.set_padding(0.1)
        self.doc.add_cell_style('TextChild2',cell)

        cell = TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('TextContentsEnd',cell)

        cell = TableCellStyle()
        cell.set_padding(0.2)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('ChildName',cell)

        table = TableStyle()
        table.set_width(100)
        table.set_columns(3)
        table.set_column_width(0,20)
        table.set_column_width(1,40)
        table.set_column_width(2,40)
        self.doc.add_table_style('ParentTable',table)

        table = TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0,7)
        table.set_column_width(1,18)
        table.set_column_width(2,35)
        table.set_column_width(3,40)
        self.doc.add_table_style('ChildTable',table)

    def setup(self):
        self.doc.open(self.output)
        self.doc.start_paragraph('Title')
        self.doc.write_text(_("Family Group Report"))
        self.doc.end_paragraph()
    
    def end(self):
        self.doc.close()
    
    def dump_parent(self,person):

        if not person:
            return
        
        if person.getGender() == RelLib.Person.male:
            id = _("Husband")
        else:
            id = _("Wife")
        
        self.doc.start_table(id,'ParentTable')
        self.doc.start_row()
        self.doc.start_cell('ParentHead',3)
        self.doc.start_paragraph('ParentName')
        self.doc.write_text(id + ': ')
        self.doc.write_text(person.getPrimaryName().getRegularName())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        birth = person.getBirth()
        death = person.getDeath()

        self.doc.start_row()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(_("Birth"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(birth.getDate())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContentsEnd")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(birth.getPlaceName())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(_("Death"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(death.getDate())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContentsEnd")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(death.getPlaceName())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        family = person.getMainParents()
        if family == None or family.getFather() == None:
            father_name = ""
        else:
            father_name = family.getFather().getPrimaryName().getRegularName()
        if family == None or family.getMother() == None:
            mother_name = ""
        else:
            mother_name = family.getMother().getPrimaryName().getRegularName()

        self.doc.start_row()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(_("Father"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContentsEnd",2)
        self.doc.start_paragraph('Normal')
        self.doc.write_text(father_name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell("TextContents")
        self.doc.start_paragraph('Normal')
        self.doc.write_text(_("Mother"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("TextContentsEnd",2)
        self.doc.start_paragraph('Normal')
        self.doc.write_text(mother_name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.end_table()

    def dump_child_event(self,text,name,event):
        if event:
            date = event.getDate()
            place = event.getPlaceName()
        else:
            date = ""
            place = ""
        self.doc.start_row()
        self.doc.start_cell(text)
        self.doc.start_paragraph('Normal')
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('TextContents')
        self.doc.start_paragraph('Normal')
        self.doc.write_text(name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('TextContents')
        self.doc.start_paragraph('Normal')
        self.doc.write_text(date)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('TextContentsEnd')
        self.doc.start_paragraph('Normal')
        self.doc.write_text(place)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
    def dump_child(self,index,person):

        self.doc.start_row()
        self.doc.start_cell('TextChild1')
        self.doc.start_paragraph('ChildText')
        if person.getGender() == RelLib.Person.male:
            self.doc.write_text("%dM" % index)
        else:
            self.doc.write_text("%dF" % index)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('ChildName',3)
        self.doc.start_paragraph('ChildText')
        self.doc.write_text(person.getPrimaryName().getRegularName())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        families = len(person.getFamilyList())
        self.dump_child_event('TextChild1','Birth',person.getBirth())
        if families == 0:
            self.dump_child_event('TextChild2','Death',person.getDeath())
        else:
            self.dump_child_event('TextChild1','Death',person.getDeath())
            
        index = 1
        for family in person.getFamilyList():
            m = family.getMarriage()
            if person == family.getFather():
                spouse = family.getMother()
            else:
                spouse = family.getFather()
            self.doc.start_row()
            self.doc.start_cell('TextChild1')
            self.doc.start_paragraph('Normal')
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell('TextContents')
            self.doc.start_paragraph('Normal')
            self.doc.write_text(_("Spouse"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell('TextContentsEnd',2)
            self.doc.start_paragraph('Normal')
            self.doc.write_text(spouse.getPrimaryName().getRegularName())
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()

            if index == families:
                self.dump_child_event('TextChild2',_("Married"),m)
            else:
                self.dump_child_event('TextChild1',_("Married"),m)
            
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):
        self.dump_parent(self.family.getFather())
        self.doc.start_paragraph("blank")
        self.doc.end_paragraph()
        self.dump_parent(self.family.getMother())

        length = len(self.family.getChildList())
        if length > 0:
            self.doc.start_paragraph("blank")
            self.doc.end_paragraph()
            self.doc.start_table('Children','ChildTable')
            self.doc.start_row()
            self.doc.start_cell('ParentHead',4)
            self.doc.start_paragraph('ParentName')
            self.doc.write_text(_("Children"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
            index = 1
            for child in self.family.getChildList():
                self.dump_child(index,child)
                index = index + 1
            self.doc.end_table()
        self.end()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FamilyGroupDialog(TextReportDialog):
    def __init__(self,database,person):
        TextReportDialog.__init__(self,database,person)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Family Group Report"),_("Text Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Family Group Report for %s") % name
    
    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Family Group Report")

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "family_group.xml"

    def doc_uses_tables(self):
        """This report requires table support."""
        return 1

    def get_report_generations(self):
        """No generation options."""
        return (0, 0)
    
    def get_report_extra_menu_info(self):
        """Create a mapping of all spouse names:families to be put
        into the 'extra' option menu in the report options box.  If
        the selected person has never been married then this routine
        will return a placebo label and disable the OK button."""
        mapping = {}
        family_list = self.person.getFamilyList()
#        if not family_list:
#            mapping[_("No known marriages")] = None
#            self.topDialog.get_widget("OK").set_sensitive(0)
        for family in family_list:
            if self.person == family.getFather():
                spouse = family.getMother()
            else:
                spouse = family.getFather()
            if spouse:
                name = spouse.getPrimaryName().getName()
            else:
                name= _("unknown")
            mapping[name] = family
        return (_("Spouse"), mapping, None, None)

    #------------------------------------------------------------------------
    #
    # Create output styles appropriate to this report.
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        """Make default output style for the Family Group Report."""
        para = ParagraphStyle()
        font = FontStyle()
        font.set_size(4)
        para.set_font(font)
        self.default_style.add_style('blank',para)
            
        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(16)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        self.default_style.add_style('Title',para)
    
        font = FontStyle()
        font.set_type_face(FONT_SERIF)
        font.set_size(10)
        font.set_bold(0)
        para = ParagraphStyle()
        para.set_font(font)
        self.default_style.add_style('Normal',para)
    
        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(10)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        self.default_style.add_style('ChildText',para)
    
        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        self.default_style.add_style('ParentName',para)

    #------------------------------------------------------------------------
    #
    # Create the contents of the report.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the object that will produce the Ancestor Chart.
        All user dialog has already been handled and the output file
        opened."""
        MyReport = FamilyGroup(self.db, self.report_menu, self.target_path, self.doc)
        MyReport.setup()
        MyReport.write_report()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    FamilyGroupDialog(database,person)
    
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
        "$	c #D2D2D2",
        "%	c #EDE2D2",
        "&	c #7A7262",
        "*	c #F1EADF",
        "=	c #867A6E",
        "-	c #56524E",
        ";	c #868686",
        ">	c #E2CAA2",
        ",	c #F2EEE2",
        "'	c #4E4E4E",
        ")	c #B2966E",
        "!	c #FAFAFA",
        "~	c #A29E96",
        "{	c #BEA27A",
        "]	c #CECABE",
        "^	c #968A76",
        "/	c #DAD2C6",
        "(	c #423E3E",
        "_	c #BA9E72",
        ":	c #B7AC9A",
        "<	c #E9DAC3",
        "[	c #E6E2E2",
        "}	c #322E2A",
        "|	c #9E9286",
        "1	c #E6D2B6",
        "2	c #F2EEE9",
        "3	c #5E5A56",
        "4	c #F6F2EE",
        "                                                ",
        "                                                ",
        "             ^=^=====&&&+&++++333+&             ",
        "             =##############:#:~;33&            ",
        "             =#!!!!!!!!!!!!!!*[$#;;|-           ",
        "             ;#!!!!!!!!!!!!!!!2[$@&]|(          ",
        "             =#!!!!!!!!!!!!!!!!2[$-[];}         ",
        "             =#!!!!@@@@@@@@!!!!![4'![];}        ",
        "             =#!!!!!!4!!4!!!!!!!!4'!![];}       ",
        "             =#!!!!!!!!!!!!!!!!!!!'*!![];(      ",
        "             =#!!!!!!!!!!!!!!!!!!!'[*!![]|-     ",
        "             &#!!!!@@~@@@~@@~@@@@@'][4!![#|+    ",
        "             &#!4!!!!!!!!!!!!!4!!!'..}('3&=+&   ",
        "             =#!!!!@@@@@@@@@@@@@@@@##@~;=+3(+   ",
        "             &#!!!!!!!!!!!!!!!!!!!![$##~;;='(   ",
        "             &#!!!!@@@@@~@@@~@@@@~@@@@@#~~;+(   ",
        "             &#!!!!!!!!!!!!!!!!!!!!444[]#@~&}   ",
        "             &#!!!!!!!!!!!!!!!!!!4442[[$]#@=}   ",
        "             &#!!!!!!!!!!!!!!!!!!4444[[$]]:;}   ",
        "             +#!!!!@~@@@@@@@@~@@@@@~~~|;]]];}   ",
        "             +#!!!!!!!!!!!!!!!!!44444,[$/]:^}   ",
        "             +#!!!!@@@~@@@@@@@@~@~~~~~~|1>$|}   ",
        "             +#!!!!!!!!!!!!!!!44442[*%[[<$]|}   ",
        "             +#!!!!@@@@~@@@@~~@~~~~~~~~|1/>~}   ",
        "             +#!!!!!!!!!!!!!!44444**[%%</1])}   ",
        "             +#!!!!!!!!!!!!!4422******%%<1/|}   ",
        "             +#!!!!!!!!!!!!!!4,*,**2***%<1/)}   ",
        "             3#!!!!@@@@@~,442,*,*,2**,,[<1/)}   ",
        "             +#!!!!!!4!!444444**[%%%%%%<<1>~}   ",
        "             3#!!!!@@4*@@@~~~~~~~~~~||||<11)}   ",
        "             +#4!!4444444,24[[*[<%<%<<<<<11|}   ",
        "             3#!!!44,,,@~~~~~~~~~|||||||111_}   ",
        "             3#!!!!!44444[4[[%%%%%<<<<11111)}   ",
        "             3#!!!!~@,*~~~~~~~~||||||^|^1>1_}   ",
        "             3#!!!444442%**[%<%%%<<<<11111>_}   ",
        "             3#!!!4***[~~~~~~|||||||^|^^1>>{}   ",
        "             -#!444444**[%<%%%<<<<11111>1>>_}   ",
        "             -#4444~~[[~~~|||||||^)^^^^^>>>_}   ",
        "             -#4444[**[%%%%%%<<<<11111>>>>>)}   ",
        "             '#4444****%%%%%<<<111<11>>>>>>_}   ",
        "             ':44****%%%%%<<<1<1<1>>1>>>>>>)}   ",
        "             -@4******%%%<%<1<<1111>>>>>>>>)}   ",
        "             '#****%%%%<%<<<<1<11>1>>>>>>>>)}   ",
        "             ':##:::::::{{{{{{__{___))^)))))}   ",
        "             }}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}   ",
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
    _("Family Group Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description=_("Creates a family group report, showing information on a set of parents and their children."),
    xpm=get_xpm_image()
    )

