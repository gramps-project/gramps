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
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Report
import BaseDoc
import Errors
import Sort
from QuestionDialog import ErrorDialog
import ReportOptions
import const

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
        
        max_gen   - Maximum number of generations to include.
        pg_breaks - Whether to include page breaks between generations.
        document  - BaseDoc instance for the output file. Any class derived
                    from BaseDoc may be used
        output    - name of the output file. 
                    None if report is not a standalone, in which case
                    somebody must take care of opening and initializing report
                    prior to writing.
        newpage   - if True, newpage is made before writing a report

        """

        Report.Report.__init__(self,database,person,options_class)

        (self.max_generations,self.pgbrk) \
                        = options_class.get_report_generations()
        sort = Sort.Sort(self.database)
        self.by_birthdate = sort.by_birthdate
        
    def dump_dates(self, person):
        birth_handle = person.get_birth_handle()
        if birth_handle:
            birth = self.database.get_event_from_handle(birth_handle).get_date_object()
            birth_year_valid = birth.get_year_valid()
        else:
            birth_year_valid = 0

        death_handle = person.get_death_handle()
        if death_handle:
            death = self.database.get_event_from_handle(death_handle).get_date_object()
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
        self.doc.start_paragraph("DR-Title")
        name = self.start_person.get_primary_name().get_regular_name()
        self.doc.write_text(_("Descendants of %s") % name)
        self.dump_dates(self.start_person)
        self.doc.end_paragraph()
        self.dump(0,self.start_person)

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
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            for child_handle in family.get_child_handle_list():
                childlist.append(child_handle)

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
from Plugins import register_report
register_report(
    name = 'descend_report',
    category = const.CATEGORY_TEXT,
    report_class = DescendantReport,
    options_class = DescendantOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("Descendant Report"),
    status=(_("Beta")),
    description=_("Generates a list of descendants of the active person"),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )
