#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2009       Gary Burton
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

"""Reports/Text Reports/Descendant Report"""

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
from gen.plug import PluginManager
from gen.plug.menu import NumberOption, PersonOption
from ReportBase import Report, ReportUtils, MenuReportOptions, CATEGORY_TEXT
from gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                            FONT_SANS_SERIF, 
                            INDEX_TYPE_TOC, PARA_ALIGN_CENTER)
import Sort
from BasicUtils import name_displayer
import DateHandler

_BORN = _('b.')
_DIED = _('d.')

#------------------------------------------------------------------------
#
# DescendantReport
#
#------------------------------------------------------------------------
class DescendantReport(Report):

    def __init__(self, database, options_class):
        """
        Create the DescendantReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen       - Maximum number of generations to include.

        """

        Report.__init__(self, database, options_class)

        menu = options_class.menu
        self.max_generations = menu.get_option_by_name('gen').get_value()
        pid = menu.get_option_by_name('pid').get_value()
        self.center_person = database.get_person_from_gramps_id(pid)
        sort = Sort.Sort(self.database)
        self.by_birthdate = sort.by_birthdate
        
    def dump_dates(self, person):
        birth = ReportUtils.get_birth_or_fallback(self.database, person)
        death = ReportUtils.get_death_or_fallback(self.database, person)

        if birth or death:
            self.doc.write_text(' (')

        if birth:
            birth_date = DateHandler.get_date(birth)
            bplace_handle = birth.get_place_handle()
            if bplace_handle:
                birth_place = self.database.get_place_from_handle(
                    bplace_handle).get_title()
                self.doc.write_text(_("b. %(birth_date)s - %(place)s") % {
                    'birth_date' : birth_date,
                    'place' : birth_place,
                    })
            else:
                self.doc.write_text(_("b. %(birth_date)s") % {
                    'birth_date' : birth_date
                    })

        if death:
            death_date = DateHandler.get_date(death)
            dplace_handle = death.get_place_handle()
            if birth:
                self.doc.write_text(', ')
            if dplace_handle:
                death_place = self.database.get_place_from_handle(
                    dplace_handle).get_title()
                self.doc.write_text(_("d. %(death_date)s - %(place)s") % {
                    'death_date' : death_date,
                    'place' : death_place,
                    })
            else:
                self.doc.write_text(_("d. %(death_date)s") % {
                    'death_date' : death_date
                    })

        self.doc.write_text(')')
        
    def write_report(self):
        self.doc.start_paragraph("DR-Title")
        name = name_displayer.display(self.center_person)
        title = _("Descendants of %s") % name
        mark = IndexMark(title,INDEX_TYPE_TOC,1)
        self.doc.write_text(title,mark)
        self.doc.end_paragraph()
        self.dump(1,self.center_person)

    def dump(self,level,person):

        self.doc.start_paragraph("DR-Level%d" % min(level,32),"%d." % level)
        mark = ReportUtils.get_person_mark(self.database,person)
        self.doc.write_text(name_displayer.display(person),mark)
        self.dump_dates(person)
        self.doc.end_paragraph()

        if level >= self.max_generations:
            return
        
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)

            spouse_handle = ReportUtils.find_spouse(person,family)
            if spouse_handle:
                spouse = self.database.get_person_from_handle(spouse_handle)
                mark = ReportUtils.get_person_mark(self.database,person)
                self.doc.start_paragraph("DR-Spouse%d" % min(level,32))
                name = name_displayer.display(spouse)
                self.doc.write_text(_("sp. %(spouse)s") % {'spouse':name},mark)
                self.dump_dates(spouse)
                self.doc.end_paragraph()

            childlist = family.get_child_ref_list()[:]
            for child_ref in childlist:
                child = self.database.get_person_from_handle(child_ref.ref)
                self.dump(level+1,child)

#------------------------------------------------------------------------
#
# AncestorOptions
#
#------------------------------------------------------------------------
class DescendantOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        category_name = _("Report Options")
        
        pid = PersonOption(_("Center Person"))
        pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", pid)
        
        gen = NumberOption(_("Generations"),10,1,15)
        gen.set_help(_("The number of generations to include in the report"))
        menu.add_option(category_name,"gen",gen)

    def make_default_style(self,default_style):
        """Make the default output style for the Descendant Report."""
        f = FontStyle()
        f.set_size(12)
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
        default_style.add_paragraph_style("DR-Title",p)

        f = FontStyle()
        f.set_size(10)
        for i in range(1,33):
            p = ParagraphStyle()
            p.set_font(f)
            p.set_top_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_bottom_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_first_indent(-0.5)
            p.set_left_margin(min(10.0,float(i-0.5)))
            p.set_description(_("The style used for the "
                                "level %d display.") % i)
            default_style.add_paragraph_style("DR-Level%d" % min(i,32), p)

            p = ParagraphStyle()
            p.set_font(f)
            p.set_top_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_bottom_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_left_margin(min(10.0,float(i-0.5)))
            p.set_description(_("The style used for the "
                                "spouse level %d display.") % i)
            default_style.add_paragraph_style("DR-Spouse%d" % min(i,32), p)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name = 'descend_report',
    category = CATEGORY_TEXT,
    report_class = DescendantReport,
    options_class = DescendantOptions,
    modes = PluginManager.REPORT_MODE_GUI | \
            PluginManager.REPORT_MODE_BKI | \
            PluginManager.REPORT_MODE_CLI,
    translated_name = _("Descendant Report"),
    status = _("Stable"),
    description = _("Produces a list of descendants of the active person"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org"
    )
