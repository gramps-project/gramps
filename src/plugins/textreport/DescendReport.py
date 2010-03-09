#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010       Craig J. Anderson

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

"""
Reports/Text Reports/Descendant Report.
"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gen.ggettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                            FONT_SANS_SERIF, INDEX_TYPE_TOC, PARA_ALIGN_CENTER)
from gen.plug.menu import NumberOption, PersonOption, BooleanOption, EnumeratedListOption
from gen.display.name import displayer as name_displayer
from Errors import ReportError
from ReportBase import Report, ReportUtils, MenuReportOptions
import DateHandler
import Sort
from gen.utils import get_birth_or_fallback, get_death_or_fallback


#------------------------------------------------------------------------
#
# Printinfo
#
#------------------------------------------------------------------------
class Printinfo():
    """
    A base class used to help make the individual numbering system classes.
    This class must first be initialized with set_class_vars
    """
    doc = None
    database = None
    
    def set_class_vars(self, doc, database, showspouse):
        Printinfo.doc = doc
        Printinfo.database = database
        Printinfo.showspouse = showspouse
    
    def dump_dates(self, person):
        birth = get_birth_or_fallback(Printinfo.database, person)
        death = get_death_or_fallback(Printinfo.database, person)

        if birth or death:
            Printinfo.doc.write_text(' (')

        if birth:
            birth_date = DateHandler.get_date(birth)
            bplace_handle = birth.get_place_handle()
            if bplace_handle:
                birth_place = Printinfo.database.get_place_from_handle(
                    bplace_handle).get_title()
                Printinfo.doc.write_text("%(event_abbrev)s %(birth_date)s - %(place)s" % {
                    'event_abbrev': birth.type.get_abbreviation(),
                    'birth_date' : birth_date,
                    'place' : birth_place,
                    })
            else:
                Printinfo.doc.write_text("%(event_abbrev)s %(birth_date)s" % {
                    'event_abbrev': birth.type.get_abbreviation(),
                    'birth_date' : birth_date
                    })

        if death:
            death_date = DateHandler.get_date(death)
            dplace_handle = death.get_place_handle()
            if birth:
                Printinfo.doc.write_text(', ')
            if dplace_handle:
                death_place = Printinfo.database.get_place_from_handle(
                    dplace_handle).get_title()
                Printinfo.doc.write_text("%(event_abbrev)s %(death_date)s - %(place)s" % {
                    'event_abbrev': death.type.get_abbreviation(),
                    'death_date' : death_date,
                    'place' : death_place,
                    })
            else:
                Printinfo.doc.write_text("%(event_abbrev)s %(death_date)s" % {
                    'event_abbrev': death.type.get_abbreviation(),
                    'death_date' : death_date
                    })

        if birth or death:
            Printinfo.doc.write_text(')')
            
    def print_person(level, person):
        pass
    
    def print_spouse(self, level, spouse_handle):
        #Currently print_spouses is the same for all numbering systems.
        if spouse_handle and Printinfo.showspouse:
            spouse = self.database.get_person_from_handle(spouse_handle)
            mark = ReportUtils.get_person_mark(self.database, spouse)
            self.doc.start_paragraph("DR-Spouse%d" % min(level, 32))
            name = name_displayer.display(spouse)
            self.doc.write_text(_("sp. %(spouse)s") % {'spouse':name}, mark)
            self.dump_dates(spouse)
            self.doc.end_paragraph()


#------------------------------------------------------------------------
#
# PrintSimple
#   Simple numbering system
#
#------------------------------------------------------------------------
class PrintSimple(Printinfo):
    def print_person(self, level, person):
        self.doc.start_paragraph("DR-Level%d" % min(level, 32), "%d." % level)
        mark = ReportUtils.get_person_mark(self.database, person)
        self.doc.write_text(name_displayer.display(person), mark)
        self.dump_dates(person)
        self.doc.end_paragraph()
    
    
#------------------------------------------------------------------------
#
# PrintVlliers
#   de_Villiers_Pama numbering system
#
#------------------------------------------------------------------------
class PrintVlliers(Printinfo):
    def __init__(self):
        self.pama = 'abcdefghijklmnopqrstuvwxyz'
        self.num = {0:1}
    
    def print_person(self, level, person):
        self.doc.start_paragraph("DR-Level%d" % min(level, 32),
                                 self.pama[level-1] +
                                 str(self.num[level-1]) + ".")
        mark = ReportUtils.get_person_mark(self.database, person)
        self.doc.write_text(name_displayer.display(person), mark)
        self.dump_dates(person)
        self.doc.end_paragraph()
        
        self.num[level] = 1
        self.num[level-1] = self.num[level-1] + 1
        


#------------------------------------------------------------------------
#
# class PrintMeurgey
#   Meurgey_de_Tupigny numbering system
#
#------------------------------------------------------------------------
class PrintMeurgey(Printinfo):
    def __init__(self):
        self.childnum = [""]
    
    def print_person(self, level, person):
        if level == 1:
            dash = ""
        else:
            dash = "-"
            if len(self.childnum) < level:
                self.childnum.append(1)

        self.doc.start_paragraph("DR-Level%d" % min(level, 32),
                                 ReportUtils.roman(level)
                                 + dash + str(self.childnum[level-1]) + ".")
        if level > 1:
            self.childnum[level-1] += 1
        mark = ReportUtils.get_person_mark(self.database, person)
        self.doc.write_text(name_displayer.display(person), mark)
        self.dump_dates(person)
        self.doc.end_paragraph()
        

#------------------------------------------------------------------------
#
# RecurseDown
#
#------------------------------------------------------------------------
class RecurseDown():
    """
    A simple object to recurse from a person down through their descendants
    
    The arguments are:
    
    max_generations: The max number of generations
    database:  The database object
    objPrint:  A Printinfo derived class that prints person
               information on the report
    """
    def __init__(self, max_generations, database, objPrint):
        self.max_generations = max_generations
        self.database = database
        self.objPrint = objPrint
    
    def recurse(self, level, person):

        self.objPrint.print_person(level, person)

        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)

            spouse_handle = ReportUtils.find_spouse(person, family)
            self.objPrint.print_spouse(level, spouse_handle)

            if level >= self.max_generations:
                continue

            childlist = family.get_child_ref_list()[:]
            for child_ref in childlist:
                child = self.database.get_person_from_handle(child_ref.ref)
                self.recurse(level+1, child)

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
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen       - Maximum number of generations to include.
        """

        Report.__init__(self, database, options_class)

        menu = options_class.menu
        self.max_generations = menu.get_option_by_name('gen').get_value()
        self.numbering     = menu.get_option_by_name('numbering').get_value()
        pid = menu.get_option_by_name('pid').get_value()
        self.center_person = database.get_person_from_gramps_id(pid)
        if (self.center_person == None) :
            raise ReportError(_("Person %s is not in the Database") % pid )
        
        sort = Sort.Sort(self.database)
        self.by_birthdate = sort.by_birthdate
    
        #Initialize the Printinfo class    
        p = Printinfo()
        p.set_class_vars(self.doc, database,
                         menu.get_option_by_name('shows').get_value())
    
    
    def write_report(self):
        self.doc.start_paragraph("DR-Title")
        name = name_displayer.display(self.center_person)
        title = _("Descendants of %s") % name
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        
        if self.numbering == "Simple":
            obj = PrintSimple()
        elif self.numbering == "de Villiers/Pama":
            obj = PrintVlliers()
        elif self.numbering == "Meurgey de Tupigny":
            obj = PrintMeurgey()
        else:
            raise AttributeError("no such numbering: '%s'" % self.numbering)

        recurse = RecurseDown(self.max_generations, self.database, obj)
        recurse.recurse(1, self.center_person)

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
        
        numbering = EnumeratedListOption(_("Numbering system"), "Simple")
        numbering.set_items([
                ("Simple",      _("Simple numbering")), 
                ("de Villiers/Pama", _("de Villiers/Pama numbering")), 
                ("Meurgey de Tupigny", _("Meurgey de Tupigny numbering"))])
        numbering.set_help(_("The numbering system to be used"))
        menu.add_option(category_name, "numbering", numbering)
        
        gen = NumberOption(_("Generations"), 10, 1, 15)
        gen.set_help(_("The number of generations to include in the report"))
        menu.add_option(category_name, "gen", gen)

        shows = BooleanOption(_('Show Sp_ouses'), True)
        shows.set_help(_("Whether to show spouses in the report."))
        menu.add_option(category_name, "shows", shows)

    def make_default_style(self, default_style):
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
        default_style.add_paragraph_style("DR-Title", p)

        f = FontStyle()
        f.set_size(10)
        for i in range(1, 33):
            p = ParagraphStyle()
            p.set_font(f)
            p.set_top_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_bottom_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_first_indent(-0.5)
            p.set_left_margin(min(10.0, float(i-0.5)))
            p.set_description(_("The style used for the "
                                "level %d display.") % i)
            default_style.add_paragraph_style("DR-Level%d" % min(i, 32), p)

            p = ParagraphStyle()
            p.set_font(f)
            p.set_top_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_bottom_margin(ReportUtils.pt2cm(f.get_size()*0.125))
            p.set_left_margin(min(10.0, float(i-0.5)))
            p.set_description(_("The style used for the "
                                "spouse level %d display.") % i)
            default_style.add_paragraph_style("DR-Spouse%d" % min(i, 32), p)
