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

"Generate files/Family Group Report"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os

import gtk
#------------------------------------------------------------------------
#
# GRAMPS 
#
#------------------------------------------------------------------------
import RelLib
import Report
import BaseDoc
import Errors
import Utils
from gettext import gettext as _
from QuestionDialog import ErrorDialog

#------------------------------------------------------------------------
#
# FamilyGroup
#
#------------------------------------------------------------------------
class FamilyGroup:

    def __init__(self,database,family,doc,output,newpage=0):
        self.db = database
        self.family = family
        self.output = output
        self.doc = doc
        self.newpage = newpage
        if output:
            self.standalone = 1
            self.doc.open(output)
            self.doc.init()
        else:
            self.standalone = 0

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.2)
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('FGR-ParentHead',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('FGR-TextContents',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(0)
        cell.set_left_border(1)
        cell.set_padding(0.1)
        self.doc.add_cell_style('FGR-TextChild1',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_left_border(1)
        cell.set_padding(0.1)
        self.doc.add_cell_style('FGR-TextChild2',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.1)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('FGR-TextContentsEnd',cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.2)
        cell.set_bottom_border(1)
        cell.set_right_border(1)
        cell.set_left_border(1)
        self.doc.add_cell_style('FGR-ChildName',cell)

        table = BaseDoc.TableStyle()
        table.set_width(100)
        table.set_columns(3)
        table.set_column_width(0,20)
        table.set_column_width(1,40)
        table.set_column_width(2,40)
        self.doc.add_table_style('FGR-ParentTable',table)

        table = BaseDoc.TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0,7)
        table.set_column_width(1,18)
        table.set_column_width(2,35)
        table.set_column_width(3,40)
        self.doc.add_table_style('FGR-ChildTable',table)

    def end(self):
        if self.standalone:
            self.doc.close()
    
    def dump_parent(self,person):

        if not person:
            return
        
        if person.getGender() == RelLib.Person.male:
            id = _("Husband")
        else:
            id = _("Wife")
        
        self.doc.start_table(id,'FGR-ParentTable')
        self.doc.start_row()
        self.doc.start_cell('FGR-ParentHead',3)
        self.doc.start_paragraph('FGR-ParentName')
        self.doc.write_text(id + ': ')
        self.doc.write_text(person.getPrimaryName().getRegularName())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        birth = person.getBirth()
        death = person.getDeath()

        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(_("Birth"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(birth.getDate())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(birth.getPlaceName())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(_("Death"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(death.getDate())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd")
        self.doc.start_paragraph('FGR-Normal')
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
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(_("Father"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd",2)
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(father_name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(_("Mother"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd",2)
        self.doc.start_paragraph('FGR-Normal')
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
        self.doc.start_paragraph('FGR-Normal')
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('FGR-TextContents')
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(name)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('FGR-TextContents')
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(date)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('FGR-TextContentsEnd')
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(place)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
    def dump_child(self,index,person):

        self.doc.start_row()
        self.doc.start_cell('FGR-TextChild1')
        self.doc.start_paragraph('FGR-ChildText')
        if person.getGender() == RelLib.Person.male:
            self.doc.write_text("%dM" % index)
        else:
            self.doc.write_text("%dF" % index)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('FGR-ChildName',3)
        self.doc.start_paragraph('FGR-ChildText')
        self.doc.write_text(person.getPrimaryName().getRegularName())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        families = len(person.getFamilyList())
        self.dump_child_event('FGR-TextChild1','Birth',person.getBirth())
        if families == 0:
            self.dump_child_event('FGR-TextChild2',_('Death'),person.getDeath())
        else:
            self.dump_child_event('FGR-TextChild1',_('Death'),person.getDeath())
            
        index = 1
        for family in person.getFamilyList():
            m = family.getMarriage()
            if person == family.getFather():
                spouse = family.getMother()
            else:
                spouse = family.getFather()
            self.doc.start_row()
            self.doc.start_cell('FGR-TextChild1')
            self.doc.start_paragraph('FGR-Normal')
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell('FGR-TextContents')
            self.doc.start_paragraph('FGR-Normal')
            self.doc.write_text(_("Spouse"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.start_cell('FGR-TextContentsEnd',2)
            self.doc.start_paragraph('FGR-Normal')
            if spouse:
                self.doc.write_text(spouse.getPrimaryName().getRegularName())
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()

            if index == families:
                self.dump_child_event('FGR-TextChild2',_("Married"),m)
            else:
                self.dump_child_event('FGR-TextChild1',_("Married"),m)
            
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):
        if self.newpage:
            self.doc.page_break()

        self.doc.start_paragraph('FGR-Title')
        self.doc.write_text(_("Family Group Report"))
        self.doc.end_paragraph()

        if self.family:
            self.dump_parent(self.family.getFather())
            self.doc.start_paragraph("FGR-blank")
            self.doc.end_paragraph()
            self.dump_parent(self.family.getMother())

            length = len(self.family.getChildList())
            if length > 0:
                self.doc.start_paragraph("FGR-blank")
                self.doc.end_paragraph()
                self.doc.start_table('FGR-Children','FGR-ChildTable')
                self.doc.start_row()
                self.doc.start_cell('FGR-ParentHead',4)
                self.doc.start_paragraph('FGR-ParentName')
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
# FamilyGroupDialog
#
#------------------------------------------------------------------------
class FamilyGroupDialog(Report.TextReportDialog):

    report_options = {}

    def __init__(self,database,person):
        Report.TextReportDialog.__init__(self,database,person,self.report_options)

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
        spouse_map = _build_spouse_map(self.person)
        return (_("Spouse"), spouse_map, None, None)

    #------------------------------------------------------------------------
    #
    # Create output styles appropriate to this report.
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        _make_default_style(self.default_style)

    #------------------------------------------------------------------------
    #
    # Create the contents of the report.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the object that will produce the Ancestor Chart.
        All user dialog has already been handled and the output file
        opened."""
        try:
            MyReport = FamilyGroup(self.db, self.report_menu, 
                self.doc, self.target_path)
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
    FamilyGroupDialog(database,person)
    
#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "family_group.xml"
_style_name = "default" 

_person_id = ""
_spouse_name = ""
_options = ( _person_id, _spouse_name )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class FamilyGroupBareDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.getPerson(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)

        self.spouse_name = self.options[1]

        self.new_person = None

        self.spouse_map = _build_spouse_map(self.person)
        if self.extra_menu:
            myMenu = Utils.build_string_optmenu(self.spouse_map,self.spouse_name)
            self.extra_menu.set_menu(myMenu)
            self.extra_menu.set_sensitive(len(self.spouse_map) > 1)
        
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
        return "%s - GRAMPS Book" % (_("Family Group Report"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Family Group Report for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def get_report_generations(self):
        """No generation options."""
        return (0, 0)

    def doc_uses_tables(self):
        """This report requires table support."""
        return 1

    def get_report_extra_menu_info(self):
        self.spouse_map = _build_spouse_map(self.person)
        return (_("Spouse"), self.spouse_map, None, None)

    def on_center_person_change_clicked(self,obj):
        import SelectPerson
        sel_person = SelectPerson.SelectPerson(self.db,_('Select Person'))
        new_person = sel_person.run()
        if new_person:
            self.new_person = new_person
            self.new_spouse_map = _build_spouse_map(self.new_person)

            if self.new_spouse_map:
                if not self.extra_menu:
                    old_person = self.person
                    self.person = self.new_person
                    self.setup_report_options_frame()
                    self.window.show_all()
                    self.person = old_person
                myMenu = Utils.build_string_optmenu(self.new_spouse_map,None)
                self.extra_menu.set_menu(myMenu)
                self.extra_menu.set_sensitive(len(self.new_spouse_map) > 1)
            else:
                if self.extra_menu:
                    myMenu = Utils.build_string_optmenu(self.new_spouse_map,None)
                    self.extra_menu.set_menu(myMenu)
                    self.extra_menu.set_sensitive(gtk.FALSE)
                    self.window.show_all()
                    self.extra_menu = None

            new_name = new_person.getPrimaryName().getRegularName()
	    if new_name:
                self.person_label.set_text( "<i>%s</i>" % new_name )
                self.person_label.set_use_markup(gtk.TRUE)

            
    def on_cancel(self, obj):
        pass

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        if self.new_person:
            self.person = self.new_person
            self.spouse_map = self.new_spouse_map

        self.parse_style_frame()
        self.parse_report_options_frame()
        
        if self.spouse_map:
            spouse_number = self.extra_menu.get_history()
            spouse_names = self.spouse_map.keys()
            spouse_names.sort()
            self.spouse_name = spouse_names[spouse_number]
        else:
            self.spouse_name = ""
            
        self.options = ( self.person.getId(), self.spouse_name )
        self.style_name = self.selected_style.get_name()

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Family Group Report using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.getPerson(options[0])
        spouse_name = options[1]
        spouse_map = _build_spouse_map(person)
        if spouse_map:
            if spouse_map.has_key(spouse_name):
                family = spouse_map[spouse_name]
            else:
                spouse_names = spouse_map.keys()
                spouse_names.sort()
                family = spouse_map[spouse_names[0]]
        else:
            family = None
        return FamilyGroup(database, family, doc, None, newpage )
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
# Functions shared between the dialogs
#
#------------------------------------------------------------------------
def _make_default_style(default_style):
    """Make default output style for the Family Group Report."""
    para = BaseDoc.ParagraphStyle()
    font = BaseDoc.FontStyle()
    font.set_size(4)
    para.set_font(font)
    default_style.add_style('FGR-blank',para)
            
    font = BaseDoc.FontStyle()
    font.set_type_face(BaseDoc.FONT_SANS_SERIF)
    font.set_size(16)
    font.set_bold(1)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_description(_("The style used for the title of the page."))
    default_style.add_style('FGR-Title',para)
    
    font = BaseDoc.FontStyle()
    font.set_type_face(BaseDoc.FONT_SERIF)
    font.set_size(10)
    font.set_bold(0)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_description(_('The basic style used for the text display.'))
    default_style.add_style('FGR-Normal',para)
    
    font = BaseDoc.FontStyle()
    font.set_type_face(BaseDoc.FONT_SANS_SERIF)
    font.set_size(10)
    font.set_bold(1)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_description(_('The style used for the text related to the children.'))
    default_style.add_style('FGR-ChildText',para)
    
    font = BaseDoc.FontStyle()
    font.set_type_face(BaseDoc.FONT_SANS_SERIF)
    font.set_size(12)
    font.set_bold(1)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_description(_("The style used for the parent's name"))
    default_style.add_style('FGR-ParentName',para)

def _build_spouse_map(person):
    """Create a mapping of all spouse names:families to be put
    into the 'extra' option menu in the report options box.  If
    the selected person has never been married then this routine
    will return a placebo label and disable the OK button."""
    spouse_map = {}
    family_list = person.getFamilyList()
    for family in family_list:
        if person == family.getFather():
            spouse = family.getMother()
        else:
            spouse = family.getFather()
        if spouse:
            name = spouse.getPrimaryName().getName()
        else:
            name= _("unknown")
        spouse_map[name] = family
    return spouse_map

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
from Plugins import register_report, register_book_item

register_report(
    report,
    _("Family Group Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description=_("Creates a family group report, showing information on a set of parents and their children."),
    xpm=get_xpm_image()
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Family Group Report"), 
    _("Text"),
    FamilyGroupBareDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
    )
