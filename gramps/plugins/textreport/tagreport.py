#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008 Brian G. Matherly
# Copyright (C) 2009      Gary Burton
# Copyright (C) 2010      Jakim Friant
# Copyright (C) 2010      Nick Hall
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

"""Reports/Text Reports/Tag Report"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gramps.gen.plug.menu import EnumeratedListOption
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                        TableStyle, TableCellStyle, FONT_SANS_SERIF, 
                        INDEX_TYPE_TOC, PARA_ALIGN_CENTER)
from gramps.gen.lib import NoteType
from gramps.gen.filters import GenericFilterFactory, rules
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import ReportError
from gramps.gen.datehandler import get_date

#------------------------------------------------------------------------
#
# TagReport
#
#------------------------------------------------------------------------
class TagReport(Report):

    def __init__(self, database, options, user):
        """
        Create the TagReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.
        
        tag             - The tag each object must match to be included.
        """
        Report.__init__(self, database, options, user)
        menu = options.menu
        self.tag = menu.get_option_by_name('tag').get_value()
        if not self.tag:
            raise ReportError(_('Tag Report'),
                _('You must first create a tag before running this report.'))
       
    def write_report(self):
        self.doc.start_paragraph("TR-Title")
        # feature request 2356: avoid genitive form
        title = _("Tag Report for %s Items") % self.tag
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        
        self.write_people()
        self.write_families()
        #self.write_events()
        self.write_notes()
        self.write_media()
            
    def write_people(self):
        plist = self.database.iter_person_handles()
        FilterClass = GenericFilterFactory('Person')
        filter = FilterClass()
        filter.add_rule(rules.person.HasTag([self.tag]))
        ind_list = filter.apply(self.database, plist)
        
        if not ind_list:
            return
        
        self.doc.start_paragraph("TR-Heading")
        header = _("People")
        mark = IndexMark(header, INDEX_TYPE_TOC, 2)
        self.doc.write_text(header, mark)
        self.doc.end_paragraph()

        self.doc.start_table('PeopleTable','TR-Table')
        
        self.doc.start_row()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Id"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Name"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Birth"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Death"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()

        for person_handle in ind_list:
            person = self.database.get_person_from_handle(person_handle)

            self.doc.start_row()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            self.doc.write_text(person.get_gramps_id())
            self.doc.end_paragraph()
            self.doc.end_cell()

            name = name_displayer.display(person)
            mark = ReportUtils.get_person_mark(self.database, person)
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            self.doc.write_text(name, mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            birth_ref = person.get_birth_ref()
            if birth_ref:
                event = self.database.get_event_from_handle(birth_ref.ref)
                self.doc.write_text(get_date( event ))
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            death_ref = person.get_death_ref()
            if death_ref:
                event = self.database.get_event_from_handle(death_ref.ref)
                self.doc.write_text(get_date( event ))
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.end_row()
            
        self.doc.end_table()
            
    def write_families(self):
        flist = self.database.iter_family_handles()
        FilterClass = GenericFilterFactory('Family')
        filter = FilterClass()
        filter.add_rule(rules.family.HasTag([self.tag]))
        fam_list = filter.apply(self.database, flist)
        
        if not fam_list:
            return
        
        self.doc.start_paragraph("TR-Heading")
        header = _("Families")
        mark = IndexMark(header,INDEX_TYPE_TOC, 2)
        self.doc.write_text(header, mark)
        self.doc.end_paragraph()

        self.doc.start_table('FamilyTable','TR-Table')
        
        self.doc.start_row()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Id"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Father"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Mother"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Relationship"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()

        for family_handle in fam_list:
            family = self.database.get_family_from_handle(family_handle)
            
            self.doc.start_row()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            self.doc.write_text(family.get_gramps_id())
            self.doc.end_paragraph()
            self.doc.end_cell()

            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.database.get_person_from_handle(father_handle)
                mark = ReportUtils.get_person_mark(self.database, father)
                self.doc.write_text(name_displayer.display(father), mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                mark = ReportUtils.get_person_mark(self.database, mother)
                self.doc.write_text(name_displayer.display(mother), mark)
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            relation = family.get_relationship()
            self.doc.write_text(str(relation) )
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.end_row()
            
        self.doc.end_table()

    def write_events(self):
        # At the time of this writing, the GRAMPS UI does not allow the setting
        # of tags for events.
        elist = self.database.get_event_handles()
        FilterClass = GenericFilterFactory('Event')
        filter = FilterClass()
        filter.add_rule(rules.event.HasTag([self.tag]))
        event_list = filter.apply(self.database, elist)
        
        if not event_list:
            return
        
        self.doc.start_paragraph("TR-Heading")
        header = _("Events")
        mark = IndexMark(header, INDEX_TYPE_TOC, 2)
        self.doc.write_text(header, mark)
        self.doc.end_paragraph()

        self.doc.start_table('EventTable','TR-Table')
        
        self.doc.start_row()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Id"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Date"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Place"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Description"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()

        for event_handle in event_list:
            event = self.database.get_event_from_handle(event_handle)
            
            self.doc.start_row()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            self.doc.write_text(event.get_gramps_id())
            self.doc.end_paragraph()
            self.doc.end_cell()            
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            date = get_date(event)
            if date:
                self.doc.write_text(date)
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            place_handle = event.get_place_handle()
            place = ReportUtils.place_name(self.database, place_handle)
            if place:
                self.doc.write_text(place)
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
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
        filter.add_rule(rules.note.HasTag([self.tag]))
        note_list = filter.apply(self.database, nlist)
        
        if not note_list:
            return
        
        self.doc.start_paragraph("TR-Heading")
        header = _("Notes")
        mark = IndexMark(header, INDEX_TYPE_TOC, 2)
        self.doc.write_text(header ,mark)
        self.doc.end_paragraph()

        self.doc.start_table('NoteTable','TR-Table')
        
        self.doc.start_row()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Id"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Type"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('TR-TableCell', 2)
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Text"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()

        for note_handle in note_list:
            note = self.database.get_note_from_handle(note_handle)
            
            self.doc.start_row()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            self.doc.write_text(note.get_gramps_id())
            self.doc.end_paragraph()
            self.doc.end_cell()            
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            type = note.get_type()
            self.doc.write_text(str(type))
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('TR-TableCell', 2)
            self.doc.write_styled_note(note.get_styledtext(),
                                       note.get_format(), 'TR-Note',
                                       contains_html = (note.get_type()
                                                        == NoteType.HTML_CODE)
                                      )
            self.doc.end_cell()
            
            self.doc.end_row()
            
        self.doc.end_table()

    def write_media(self):
        mlist = self.database.get_media_object_handles(sort_handles=True)
        FilterClass = GenericFilterFactory('Media')
        filter = FilterClass()
        filter.add_rule(rules.media.HasTag([self.tag]))
        media_list = filter.apply(self.database, mlist)
        
        if not media_list:
            return
        
        self.doc.start_paragraph("TR-Heading")
        header = _("Media")
        mark = IndexMark(header, INDEX_TYPE_TOC, 2)
        self.doc.write_text(header ,mark)
        self.doc.end_paragraph()

        self.doc.start_table('MediaTable','TR-Table')
        
        self.doc.start_row()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Id"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Title"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Type"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('TR-TableCell')
        self.doc.start_paragraph('TR-Normal-Bold')
        self.doc.write_text(_("Date"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()

        for media_handle in media_list:
            media = self.database.get_object_from_handle(media_handle)

            self.doc.start_row()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            self.doc.write_text(media.get_gramps_id())
            self.doc.end_paragraph()
            self.doc.end_cell()            
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            title = media.get_description()
            self.doc.write_text(str(title))
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            mime_type = media.get_mime_type()
            self.doc.write_text(str(mime_type))
            self.doc.end_paragraph()
            self.doc.end_cell()
            
            self.doc.start_cell('TR-TableCell')
            self.doc.start_paragraph('TR-Normal')
            date = get_date(media)
            if date:
                self.doc.write_text(date)
            self.doc.end_paragraph()
            self.doc.end_cell()

            self.doc.end_row()
            
        self.doc.end_table()

#------------------------------------------------------------------------
#
# TagOptions
#
#------------------------------------------------------------------------
class TagOptions(MenuReportOptions):

    def __init__(self, name, dbase):
        self.__db = dbase
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """
        Add options to the menu for the tag report.
        """
        category_name = _("Report Options")

        all_tags = []
        for handle in self.__db.get_tag_handles(sort_handles=True):
            tag = self.__db.get_tag_from_handle(handle)
            all_tags.append(tag.get_name())

        if len(all_tags) > 0:
            tag_option = EnumeratedListOption(_('Tag'), all_tags[0])
            for tag_name in all_tags:
                tag_option.add_item(tag_name, tag_name)
        else:
            tag_option = EnumeratedListOption(_('Tag'), '')
            tag_option.add_item('', '')

        tag_option.set_help( _("The tag to use for the report"))
        menu.add_option(category_name, "tag", tag_option)

    def make_default_style(self,default_style):
        """Make the default output style for the Tag Report."""
        # Paragraph Styles
        f = FontStyle()
        f.set_size(16)
        f.set_type_face(FONT_SANS_SERIF)
        f.set_bold(1)
        p = ParagraphStyle()
        p.set_header_level(1)
        p.set_bottom_border(1)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_font(f)
        p.set_alignment(PARA_ALIGN_CENTER)
        p.set_description(_("The style used for the title of the page."))
        default_style.add_paragraph_style("TR-Title", p)
        
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=14, italic=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for the section headers.'))
        default_style.add_paragraph_style("TR-Heading", para)
        
        font = FontStyle()
        font.set_size(12)
        p = ParagraphStyle()
        p.set(first_indent=-0.75, lmargin=.75)
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("TR-Normal", p)
        
        font = FontStyle()
        font.set_size(12)
        font.set_bold(True)
        p = ParagraphStyle()
        p.set(first_indent=-0.75, lmargin=.75)
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_('The basic style used for table headings.'))
        default_style.add_paragraph_style("TR-Normal-Bold", p)
        
        para = ParagraphStyle()
        p.set(first_indent=-0.75, lmargin=.75)
        para.set_top_margin(ReportUtils.pt2cm(3))
        para.set_bottom_margin(ReportUtils.pt2cm(3))
        para.set_description(_('The basic style used for the note display.'))
        default_style.add_paragraph_style("TR-Note",para)
 
        #Table Styles
        cell = TableCellStyle()
        default_style.add_cell_style('TR-TableCell', cell)

        table = TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0, 10)
        table.set_column_width(1, 30)
        table.set_column_width(2, 30)
        table.set_column_width(3, 30)
        default_style.add_table_style('TR-Table',table)
