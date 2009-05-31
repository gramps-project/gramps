#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

"""Reports/Text Reports/Summary of the Database"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import posixpath
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import gen.lib
from gen.plug import PluginManager
from ReportBase import Report, ReportUtils, MenuReportOptions, CATEGORY_TEXT
from gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                    FONT_SANS_SERIF, INDEX_TYPE_TOC, PARA_ALIGN_CENTER)
from Utils import media_path_full
import DateHandler


#------------------------------------------------------------------------
#
# SummaryReport
#
#------------------------------------------------------------------------
class SummaryReport(Report):
    """
    This report produces a summary of the objects in the database.
    """
    def __init__(self, database, options_class):
        """
        Create the SummaryReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        """
        Report.__init__(self, database, options_class)
        self.__db = database
        
    def write_report(self):
        """
        Overridden function to generate the report.
        """
        self.doc.start_paragraph("SR-Title")
        title = _("Database Summary Report")
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        
        self.summarize_people()
        self.summarize_families()
        self.summarize_media()
            
    def summarize_people(self):
        """
        Write a summary of all the people in the database.
        """
        with_media = 0
        incomp_names = 0
        disconnected = 0
        missing_bday = 0
        males = 0
        females = 0
        unknowns = 0
        namelist = []
        
        self.doc.start_paragraph("SR-Heading")
        self.doc.write_text(_("Individuals"))
        self.doc.end_paragraph()
        
        person_list = self.__db.get_person_handles(sort_handles=False)
        for person_handle in person_list:
            person = self.__db.get_person_from_handle(person_handle)
            if not person:
                continue
            
            # Count people with media.
            length = len(person.get_media_list())
            if length > 0:
                with_media = with_media + 1
            
            # Count people with incomplete names.
            name = person.get_primary_name()
            if name.get_first_name() == "" or name.get_surname() == "":
                incomp_names = incomp_names + 1
                
            # Count people without families.
            if (not person.get_main_parents_family_handle()) and \
               (not len(person.get_family_handle_list())):
                disconnected = disconnected + 1
            
            # Count missing birthdays.
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = self.__db.get_event_from_handle(birth_ref.ref)
                if not DateHandler.get_date(birth):
                    missing_bday = missing_bday + 1
            else:
                missing_bday = missing_bday + 1
                
            # Count genders.
            if person.get_gender() == gen.lib.Person.FEMALE:
                females = females + 1
            elif person.get_gender() == gen.lib.Person.MALE:
                males = males + 1
            else:
                unknowns += 1
                
            # Count unique surnames
            if name.get_surname() not in namelist:
                namelist.append(name.get_surname())
        
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Number of individuals: %d") % len(person_list))
        self.doc.end_paragraph()
        
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Males: %d") % males)
        self.doc.end_paragraph()
        
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Females: %d") % females)
        self.doc.end_paragraph()
        
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Individuals with unknown gender: %d") % unknowns)
        self.doc.end_paragraph()
                            
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Individuals with incomplete names: %d") % 
                            incomp_names)
        self.doc.end_paragraph()
        
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Individuals missing birth dates: %d") % 
                            missing_bday)
        self.doc.end_paragraph()

        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Disconnected individuals: %d") % disconnected)
        self.doc.end_paragraph()
                            
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Unique surnames: %d") % len(namelist))
        self.doc.end_paragraph()
        
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Individuals with media objects: %d") % 
                            with_media)
        self.doc.end_paragraph()

    def summarize_families(self):
        """
        Write a summary of all the families in the database.
        """
        self.doc.start_paragraph("SR-Heading")
        self.doc.write_text(_("Family Information"))
        self.doc.end_paragraph()
        
        family_list = self.__db.get_family_handles()
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Number of families: %d") % len(family_list))
        self.doc.end_paragraph()

    def summarize_media(self):
        """
        Write a summary of all the media in the database.
        """
        total_media = 0
        bytes = 0
        notfound = []
        
        self.doc.start_paragraph("SR-Heading")
        self.doc.write_text(_("Media Objects"))
        self.doc.end_paragraph()
        
        total_media = len(self.__db.get_media_object_handles())
        for media_id in self.__db.get_media_object_handles():
            media = self.__db.get_object_from_handle(media_id)
            try:
                bytes = bytes + posixpath.getsize(media_path_full(self.__db, 
                                                            media.get_path()))
            except:
                notfound.append(media.get_path())
                
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Number of unique media objects: %d") % 
                            total_media)
        self.doc.end_paragraph()
        
        self.doc.start_paragraph("SR-Normal")
        self.doc.write_text(_("Total size of media objects: %d bytes") % bytes)
        self.doc.end_paragraph()
    
        if len(notfound) > 0:
            self.doc.start_paragraph("SR-Heading")
            self.doc.write_text(_("Missing Media Objects"))
            self.doc.end_paragraph()

            for media_path in notfound:
                self.doc.start_paragraph("SR-Normal")
                self.doc.write_text(media_path)
                self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# SummaryOptions
#
#------------------------------------------------------------------------
class SummaryOptions(MenuReportOptions):
    """
    SummaryOptions provides the options for the SummaryReport.
    """
    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """
        Add options to the menu for the marker report.
        """
        pass

    def make_default_style(self, default_style):
        """Make the default output style for the Summary Report."""
        font = FontStyle()
        font.set_size(16)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_header_level(1)
        para.set_bottom_border(1)
        para.set_top_margin(ReportUtils.pt2cm(3))
        para.set_bottom_margin(ReportUtils.pt2cm(3))
        para.set_font(font)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the title of the page."))
        default_style.add_paragraph_style("SR-Title", para)
        
        font = FontStyle()
        font.set_size(12)
        font.set_bold(True)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(0)
        para.set_description(_('The basic style used for sub-headings.'))
        default_style.add_paragraph_style("SR-Heading", para)
        
        font = FontStyle()
        font.set_size(12)
        para = ParagraphStyle()
        para.set(first_indent=-0.75, lmargin=.75)
        para.set_font(font)
        para.set_top_margin(ReportUtils.pt2cm(3))
        para.set_bottom_margin(ReportUtils.pt2cm(3))
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("SR-Normal", para)

#-------------------------------------------------------------------------
#
# register_report
#
#-------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name = 'summary',
    category = CATEGORY_TEXT,
    report_class = SummaryReport,
    options_class = SummaryOptions,
    modes = PluginManager.REPORT_MODE_GUI | \
            PluginManager.REPORT_MODE_BKI | \
            PluginManager.REPORT_MODE_CLI,
    translated_name = _("Database Summary Report"),
    status = _("Stable"),
    description = _("Provides a summary of the current database"),
    author_name = "Brian G. Matherly",
    author_email = "brian@gramps-project.org",
    require_active = False
    )
