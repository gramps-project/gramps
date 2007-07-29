#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
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

"Generate files/Marker Report"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_TEXT, MODE_GUI, MODE_BKI, MODE_CLI
import BaseDoc
import Sort
from RelLib import MarkerType, FamilyRelType
from Filters import GenericFilter, GenericFilterFactory, Rules
from BasicUtils import name_displayer
import DateHandler

#------------------------------------------------------------------------
#
# GTK/GNOME modules
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# MarkerReport
#
#------------------------------------------------------------------------
class MarkerReport(Report):

    def __init__(self,database,person,options_class):
        """
        Creates the MarkerReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        marker       - The marker each object must match to be included.

        """

        Report.__init__(self,database,person,options_class)

        self.marker = options_class.handler.options_dict['marker']
        
        
    def write_report(self):
        self.doc.start_paragraph("MR-Title")
        title = _("Marker Report for %s Items") % self.marker
        mark = BaseDoc.IndexMark(title,BaseDoc.INDEX_TYPE_TOC,1)
        self.doc.write_text(title,mark)
        self.doc.end_paragraph()
        
        self.write_people()
        self.write_families()
        self.write_events()
        self.write_notes()
            
    def write_people(self):
        plist = self.database.get_person_handles(sort_handles=False)
        FilterClass = GenericFilterFactory('Person')
        filter = FilterClass()
        filter.add_rule(Rules.Person.HasMarkerOf([self.marker]))
        ind_list = filter.apply(self.database,plist)
        
        if not ind_list:
            return
        
        self.doc.start_paragraph("MR-Heading")
        header = _("People")
        mark = BaseDoc.IndexMark(header,BaseDoc.INDEX_TYPE_TOC,2)
        self.doc.write_text(header,mark)
        self.doc.end_paragraph()

        self.doc.start_table('PeopleTable','MR-Table')
        
        self.doc.start_row()
        
        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Id"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Name"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Birth"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Death"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()

        for person_handle in ind_list:
            person = self.database.get_person_from_handle(person_handle)

            self.doc.start_row()
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            self.doc.write_text(person.get_gramps_id())
            self.doc.end_paragraph()
            self.doc.end_cell()

            name = name_displayer.display(person)
            mark = ReportUtils.get_person_mark(self.database, person)
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            self.doc.write_text(name,mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            birth_ref = person.get_birth_ref()
            if birth_ref:
                event = self.database.get_event_from_handle(birth_ref.ref)
                self.doc.write_text(DateHandler.get_date( event ))
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            death_ref = person.get_death_ref()
            if death_ref:
                event = self.database.get_event_from_handle(death_ref.ref)
                self.doc.write_text(DateHandler.get_date( event ))
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.end_row()
            
        self.doc.end_table()
            
    def write_families(self):
        flist = self.database.get_family_handles()
        FilterClass = GenericFilterFactory('Family')
        filter = FilterClass()
        filter.add_rule(Rules.Family.HasMarkerOf([self.marker]))
        fam_list = filter.apply(self.database,flist)
        
        if not fam_list:
            return
        
        self.doc.start_paragraph("MR-Heading")
        header = _("Families")
        mark = BaseDoc.IndexMark(header,BaseDoc.INDEX_TYPE_TOC,2)
        self.doc.write_text(header,mark)
        self.doc.end_paragraph()

        self.doc.start_table('FamilyTable','MR-Table')
        
        self.doc.start_row()
        
        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Id"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Father"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Mother"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Relationship"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()

        for family_handle in fam_list:
            family = self.database.get_family_from_handle(family_handle)
            
            self.doc.start_row()
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            self.doc.write_text(family.get_gramps_id())
            self.doc.end_paragraph()
            self.doc.end_cell()

            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.database.get_person_from_handle(father_handle)
                mark = ReportUtils.get_person_mark(self.database, father)
                self.doc.write_text(name_displayer.display(father),mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                mark = ReportUtils.get_person_mark(self.database, mother)
                self.doc.write_text(name_displayer.display(mother),mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            relation = family.get_relationship()
            self.doc.write_text( str(FamilyRelType(relation)) )
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.end_row()
            
        self.doc.end_table()

    def write_events(self):
        # At the time of this writing, the GRAMPS UI does not allow the setting
        # of markers for events.
        elist = self.database.get_event_handles()
        FilterClass = GenericFilterFactory('Event')
        filter = FilterClass()
        filter.add_rule(Rules.Event.HasMarkerOf([self.marker]))
        event_list = filter.apply(self.database,elist)
        
        if not event_list:
            return
        
        self.doc.start_paragraph("MR-Heading")
        header = _("Events")
        mark = BaseDoc.IndexMark(header,BaseDoc.INDEX_TYPE_TOC,2)
        self.doc.write_text(header,mark)
        self.doc.end_paragraph()

        self.doc.start_table('EventTable','MR-Table')
        
        self.doc.start_row()
        
        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Id"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Date"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Place"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Description"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()

        for event_handle in event_list:
            event = self.database.get_event_from_handle(event_handle)
            
            self.doc.start_row()
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            self.doc.write_text(event.get_gramps_id())
            self.doc.end_paragraph()
            self.doc.end_cell()            
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            date = DateHandler.get_date(event)
            if date:
                self.doc.write_text(date)
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            place_handle = event.get_place_handle()
            place = ReportUtils.place_name(self.database,place_handle)
            if place:
                self.doc.write_text(place)
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            descr = event.get_description()
            if descr:
                self.doc.write_text( descr )
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.end_row()
            
        self.doc.end_table()
        
    def write_notes(self):
        nlist = self.database.get_note_handles()
        FilterClass = GenericFilterFactory('Note')
        filter = FilterClass()
        filter.add_rule(Rules.Note.HasMarkerOf([self.marker]))
        note_list = filter.apply(self.database,nlist)
        
        if not note_list:
            return
        
        self.doc.start_paragraph("MR-Heading")
        header = _("Notes")
        mark = BaseDoc.IndexMark(header,BaseDoc.INDEX_TYPE_TOC,2)
        self.doc.write_text(header,mark)
        self.doc.end_paragraph()

        self.doc.start_table('NoteTable','MR-Table')
        
        self.doc.start_row()
        
        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Id"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell('MR-TableCell')
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Type"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('MR-TableCell',2)
        self.doc.start_paragraph('MR-Normal-Bold')
        self.doc.write_text(_("Text"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()

        for note_handle in note_list:
            note = self.database.get_note_from_handle(note_handle)
            
            self.doc.start_row()
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            self.doc.write_text(note.get_gramps_id())
            self.doc.end_paragraph()
            self.doc.end_cell()            
            
            self.doc.start_cell('MR-TableCell')
            self.doc.start_paragraph('MR-Normal')
            type = note.get_type()
            self.doc.write_text(str(type))
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('MR-TableCell',2)
            self.doc.start_paragraph('MR-Normal')
            self.doc.write_text(note.get(True))
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.end_row()
            
        self.doc.end_table()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class MarkerOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'marker'       :  "",
        }
        self.options_help = {
            'marker'        : ("=str","Marker",
                            "The marker each item must match to be included",
                            True),
        }
        
    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add generations option
        """
        self.marker_menu = gtk.combo_box_new_text()
        index = 0
        marker_index = 0
        markers = []
        
        # Gather all the possible markers
        map = MarkerType().get_map()
        for key in map.keys():
            if key != MarkerType.CUSTOM and map[key] != "":
                markers.append( map[key] )
        markers += dialog.db.get_marker_types()
        
        # Add the markers to the menu
        for marker in markers:
            self.marker_menu.append_text(marker)
            if self.options_dict['marker'] == marker:
                marker_index = index
            index += 1
        self.marker_menu.set_active(marker_index)
        dialog.add_option('Marker',self.marker_menu)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added. Set the value in the
        options dictionary.
        """
        self.options_dict['marker'] = self.marker_menu.get_active_text()

    def make_default_style(self,default_style):
        """Make the default output style for the Marker Report."""
        # Paragraph Styles
        f = BaseDoc.FontStyle()
        f.set_size(16)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        f.set_bold(1)
        p = BaseDoc.ParagraphStyle()
        p.set_header_level(1)
        p.set_bottom_border(1)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_font(f)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_("The style used for the title of the page."))
        default_style.add_paragraph_style("MR-Title",p)
        
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for the section headers.'))
        default_style.add_paragraph_style("MR-Heading",para)
        
        font = BaseDoc.FontStyle()
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set(first_indent=-0.75,lmargin=.75)
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("MR-Normal",p)
        
        font = BaseDoc.FontStyle()
        font.set_size(12)
        font.set_bold(True)
        p = BaseDoc.ParagraphStyle()
        p.set(first_indent=-0.75,lmargin=.75)
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_('The basic style used for table headings.'))
        default_style.add_paragraph_style("MR-Normal-Bold",p)
        
        #Table Styles
        cell = BaseDoc.TableCellStyle()
        default_style.add_cell_style('MR-TableCell',cell)

        table = BaseDoc.TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0,10)
        table.set_column_width(1,30)
        table.set_column_width(2,30)
        table.set_column_width(3,30)
        default_style.add_table_style('MR-Table',table)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'marker_report',
    category = CATEGORY_TEXT,
    report_class = MarkerReport,
    options_class = MarkerOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Marker Report"),
    status=(_("Stable")),
    description=_("Generates a list of people with a specified marker"),
    author_name="Brian G. Matherly",
    author_email="brian@gramps-project.org"
    )
