#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import Report, ReportOptions, ReportUtils, register_report
import BaseDoc
import Errors
import Sort
from QuestionDialog import ErrorDialog
import NameDisplay

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
class DescendantReport(Report.Report):

    def __init__(self,database,person,options_class):
        """
        Creates the DescendantReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen       - Maximum number of generations to include.
        pagebbg   - Whether to include page breaks between generations.

        """

        Report.Report.__init__(self,database,person,options_class)

        (self.max_generations,self.pgbrk) \
                        = options_class.get_report_generations()
        sort = Sort.Sort(self.database)
        self.by_birthdate = sort.by_birthdate
        
    def dump_dates(self, person):
        birth_handle = person.get_birth_handle()
        if birth_handle:
            birth = self.database.get_event_from_handle(birth_handle)
            birth_date = birth.get_date_object()
            birth_year_valid = birth_date.get_year_valid()
        else:
            birth_year_valid = 0
            birth = None

        death_handle = person.get_death_handle()
        if death_handle:
            death = self.database.get_event_from_handle(death_handle)
            death_date = death.get_date_object()
            death_year_valid = death_date.get_year_valid()
        else:
            death = None
            death_year_valid = 0

        if birth_year_valid or death_year_valid:
            self.doc.write_text(' (')

            birth_place = ""
            if birth:
                bplace_handle = birth.get_place_handle()
                if bplace_handle:
                    birth_place = self.database.get_place_from_handle(
                        bplace_handle).get_title()

            death_place = ""
            if death:
                dplace_handle = death.get_place_handle()
                if dplace_handle:
                    death_place = self.database.get_place_from_handle(
                        dplace_handle).get_title()

            if birth_year_valid:
                if birth_place:
                    self.doc.write_text(_("b. %(birth_year)d - %(place)s") % {
                        'birth_year' : birth_date.get_year(),
                        'place' : birth_place,
                        })
                else:
                    self.doc.write_text(_("b. %(birth_year)d") % {
                        'birth_year' : birth_date.get_year()
                        })

            if death_year_valid:
                if birth_year_valid:
                    self.doc.write_text(', ')
                if death_place:
                    self.doc.write_text(_("d. %(death_year)d - %(place)s") % {
                        'death_year' : death_date.get_year(),
                        'place' : death_place,
                        })
                else:
                    self.doc.write_text(_("d. %(death_year)d") % {
                        'death_year' : death_date.get_year()
                        })

            self.doc.write_text(')')
        
    def write_report(self):
        self.doc.start_paragraph("DR-Title")
        name = NameDisplay.displayer.display(self.start_person)
        self.doc.write_text(_("Descendants of %s") % name)
        self.doc.end_paragraph()
        self.dump(1,self.start_person)

    def dump(self,level,person):

        self.doc.start_paragraph("DR-Level%d" % level,"%d." % level)
        self.doc.write_text(NameDisplay.displayer.display(person))
        self.dump_dates(person)
        self.doc.end_paragraph()

        if level >= self.max_generations:
            return
        
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)

            spouse_handle = ReportUtils.find_spouse(person,family)
            if spouse_handle:
                spouse = self.database.get_person_from_handle(spouse_handle)
                self.doc.start_paragraph("DR-Spouse%d" % level)
                name = NameDisplay.displayer.display(spouse)
                self.doc.write_text(_("sp. %(spouse)s") % {'spouse':name})
                self.dump_dates(spouse)
                self.doc.end_paragraph()

            childlist = family.get_child_handle_list()[:]
            childlist.sort(self.by_birthdate)

            for child_handle in childlist:
                child = self.database.get_person_from_handle(child_handle)
                self.dump(level+1,child)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DescendantOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'gen'       : 10,
            'pagebbg'   : 0,
        }

    def make_default_style(self,default_style):
        """Make the default output style for the Descendant Report."""
        f = BaseDoc.FontStyle()
        f.set_size(12)
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
        default_style.add_style("DR-Title",p)

        f = BaseDoc.FontStyle()
        f.set_size(10)
        for i in range(1,32):
            p = BaseDoc.ParagraphStyle()
            p.set_font(f)
            p.set_top_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_bottom_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_first_indent(-0.5)
            p.set_left_margin(min(10.0,float(i-0.5)))
            p.set_description(_("The style used for the "
                                "level %d display.") % i)
            default_style.add_style("DR-Level%d" % i,p)

            p = BaseDoc.ParagraphStyle()
            p.set_font(f)
            p.set_top_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_bottom_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_left_margin(min(10.0,float(i-0.5)))
            p.set_description(_("The style used for the "
                                "spouse level %d display.") % i)
            default_style.add_style("DR-Spouse%d" % i,p)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'descend_report',
    category = Report.CATEGORY_TEXT,
    report_class = DescendantReport,
    options_class = DescendantOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("Descendant Report"),
    status=(_("Stable")),
    description=_("Generates a list of descendants of the active person"),
    author_name="Donald N. Allingham",
    author_email="don@gramps-project.org"
    )
