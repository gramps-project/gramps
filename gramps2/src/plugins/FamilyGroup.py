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
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Gnome/GTK modules
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS 
#
#------------------------------------------------------------------------
import RelLib
import Report
import BaseDoc
import ReportOptions
import const
from DateHandler import displayer as _dd

#------------------------------------------------------------------------
#
# FamilyGroup
#
#------------------------------------------------------------------------
class FamilyGroup(Report.Report):

    def __init__(self,database,person,options_class):
        #,family_handle,doc,output,newpage=0):
        """
        Creates the DetAncestorReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        family_handle - Handle of the family to write report on.
        """
        Report.Report.__init__(self,database,person,options_class)

        spouse_id = options_class.handler.options_dict['spouse_id']
        if spouse_id:
            family_list = person.get_family_handle_list()
            for family_handle in family_list:
                family = database.get_family_from_handle(family_handle)
                if person.get_handle() == family.get_father_handle():
                    this_spouse_id = family.get_mother_handle()
                else:
                    this_spouse_id = family.get_father_handle()
                if spouse_id == this_spouse_id:
                    self.family = family
                    break
        else:
            self.family = None

        self.setup()

    def setup(self):
        """
        Define the table  styles used by the report. 
        """
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

    def dump_parent(self,person_handle):

        if not person_handle:
            return
        
        person = self.database.get_person_from_handle(person_handle)
        
        if person.get_gender() == RelLib.Person.male:
            id = _("Husband")
        else:
            id = _("Wife")
        
        self.doc.start_table(id,'FGR-ParentTable')
        self.doc.start_row()
        self.doc.start_cell('FGR-ParentHead',3)
        self.doc.start_paragraph('FGR-ParentName')
        self.doc.write_text(id + ': ')
        self.doc.write_text(person.get_primary_name().get_regular_name())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
        birth_handle = person.get_birth_handle()
        bdate = ""
        bplace = ""
        if birth_handle:
            birth = self.database.get_event_from_handle(birth_handle)
            bdate = birth.get_date()
            bplace_handle = birth.get_place_handle()
            if bplace_handle:
                bplace = self.database.get_place_from_handle(bplace_handle).get_title()
        
        death_handle = person.get_death_handle()
        ddate = ""
        dplace = ""
        if death_handle:
            death = self.database.get_event_from_handle(death_handle)
            ddate = death.get_date()
            dplace_handle = death.get_place_handle()
            if dplace_handle:
                dplace = self.database.get_place_from_handle(dplace_handle).get_title()

        self.doc.start_row()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(_("Birth"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContents")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(bdate)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(bplace)
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
        self.doc.write_text(ddate)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell("FGR-TextContentsEnd")
        self.doc.start_paragraph('FGR-Normal')
        self.doc.write_text(dplace)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        family_handle = person.get_main_parents_family_handle()
        father_name = ""
        mother_name = ""
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle() 
            if father_handle:
                father_name = self.database.get_person_from_handle(father_handle).get_primary_name().get_regular_name()
            mother_handle = family.get_mother_handle() 
            if mother_handle:
                mother_name = self.database.get_person_from_handle(mother_handle).get_primary_name().get_regular_name()

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
        date = ""
        place = ""
        if event:
            date = event.get_date()
            place_handle = event.get_place_handle()
            if place_handle:
                place = self.database.get_place_from_handle(place_handle).get_title()

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
        
    def dump_child(self,index,person_handle):

        person = self.database.get_person_from_handle(person_handle)
        self.doc.start_row()
        self.doc.start_cell('FGR-TextChild1')
        self.doc.start_paragraph('FGR-ChildText')
        if person.get_gender() == RelLib.Person.male:
            self.doc.write_text("%dM" % index)
        else:
            self.doc.write_text("%dF" % index)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.start_cell('FGR-ChildName',3)
        self.doc.start_paragraph('FGR-ChildText')
        self.doc.write_text(person.get_primary_name().get_regular_name())
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

        families = len(person.get_family_handle_list())
        birth_handle = person.get_birth_handle()
        if birth_handle:
            birth = self.database.get_event_from_handle(birth_handle)
        else:
            birth = None
        death_handle = person.get_death_handle()
        if death_handle:
            death = self.database.get_event_from_handle(death_handle)
        else:
            death = None
        self.dump_child_event('FGR-TextChild1',_('Birth'),birth)
        if families == 0:
            self.dump_child_event('FGR-TextChild2',_('Death'),death)
        else:
            self.dump_child_event('FGR-TextChild1',_('Death'),death)
            
        index = 1
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            for event_handle in family.get_event_list():
                if event_handle:
                    event = self.database.get_event_from_handle(event_handle)
                    if event.get_name() == "Marriage":
                        m = event
                        break
            else:
                m = None

            if person_handle == family.get_father_handle():
                spouse_id = family.get_mother_handle()
            else:
                spouse_id = family.get_father_handle()
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
            if spouse_id:
                spouse = self.database.get_person_from_handle(spouse_id)
                self.doc.write_text(spouse.get_primary_name().get_regular_name())
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()

            if index == families:
                self.dump_child_event('FGR-TextChild2',_("Married"),m)
            else:
                self.dump_child_event('FGR-TextChild1',_("Married"),m)
            

    def write_report(self):
        self.doc.start_paragraph('FGR-Title')
        self.doc.write_text(_("Family Group Report"))
        self.doc.end_paragraph()

        if self.family:
            self.dump_parent(self.family.get_father_handle())
            self.doc.start_paragraph("FGR-blank")
            self.doc.end_paragraph()
            self.dump_parent(self.family.get_mother_handle())

            length = len(self.family.get_child_handle_list())
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
                for child_handle in self.family.get_child_handle_list():
                    self.dump_child(index,child_handle)
                    index = index + 1
                self.doc.end_table()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FamilyGroupOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'spouse_id'    : '',
        }

        self.options_help = {
            'spouse_id'    : ("=ID","Gramps ID of the person's spouse.",
                            "Use show=id to get ID list.",
                            #[item[0] for item in self.get_spouses(None,None)],
                            #False
                            ),
        }

    def get_spouses(self,database,person):
        """
        Create a mapping of all spouse names:families to be put
        into the 'extra' option menu in the report options box.  If
        the selected person has never been married then this routine
        will return a placebo label and disable the OK button.
        """
        spouses = []
        family_list = person.get_family_handle_list()
        for family_handle in family_list:
            family = database.get_family_from_handle(family_handle)
            if person.get_handle() == family.get_father_handle():
                spouse_id = family.get_mother_handle()
            else:
                spouse_id = family.get_father_handle()
            if spouse_id:
                spouse = database.get_person_from_handle(spouse_id)
                name = spouse.get_primary_name().get_name()
            else:
                name = _("unknown")
            spouses.append((spouse_id,name))
        return spouses

    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add a menu that allows
        the user to select the sort method.
        """
        
        spouses = self.get_spouses(dialog.db,dialog.person)
        spouse_id = self.options_dict['spouse_id']

        self.spouse_menu = gtk.combo_box_new_text()
        index = 0
        spouse_index = 0
        for item in spouses:
            self.spouse_menu.append_text(item[1])
            if item[0] == spouse_id:
                spouse_index = index
            index = index + 1
        self.spouse_menu.set_active(spouse_index)

        dialog.add_option(_("Spouse"),self.spouse_menu)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added.
        """
        spouses = self.get_spouses(dialog.db,dialog.person)
        spouse_index = self.spouse_menu.get_active()
        self.options_dict['spouse_id'] = spouses[spouse_index][0]

    def make_default_style(self,default_style):
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

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
from Plugins import register_report
register_report(
    name = 'family_group',
    category = const.CATEGORY_TEXT,
    report_class = FamilyGroup,
    options_class = FamilyGroupOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("Family Group Report"),
    status = _("Beta"),
    author_name = "Donald N. Allingham",
    author_email = "dallingham@users.sourceforge.net",
    description=_("Creates a family group report, showing information on a set of parents and their children."),
    )
