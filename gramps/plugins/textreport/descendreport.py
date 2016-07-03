#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010       Craig J. Anderson
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Matt Keenan (matt.keenan@gmail.com)
# Copyright (C) 2013-2014  Paul Franklin
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Reports/Text Reports/Descendant Report.
"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                                    FONT_SANS_SERIF, INDEX_TYPE_TOC,
                                    PARA_ALIGN_CENTER)
from gramps.gen.plug.menu import (NumberOption, PersonOption, BooleanOption,
                                  EnumeratedListOption)
from gramps.gen.errors import ReportError
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.sort import Sort
from gramps.gen.utils.db import (get_birth_or_fallback, get_death_or_fallback,
                                 get_marriage_or_fallback,
                                 get_divorce_or_fallback)
from gramps.gen.display.place import displayer as _pd

#------------------------------------------------------------------------
#
# PrintSimple
#   Simple numbering system
#
#------------------------------------------------------------------------
class PrintSimple():
    def __init__(self, showdups):
        self.showdups = showdups
        self.num = {0:1}

    def number(self, level):
        if self.showdups:
            # Just show original simple numbering
            to_return = "%d." % level
        else:
            to_return = str(level)
            if level > 1:
                to_return += "-" + str(self.num[level-1])
            to_return += "."

            self.num[level] = 1
            self.num[level-1] = self.num[level-1] + 1

        return to_return
    
    
#------------------------------------------------------------------------
#
# PrintVlliers
#   de_Villiers_Pama numbering system
#
#------------------------------------------------------------------------
class PrintVilliers():
    def __init__(self):
        self.pama = 'abcdefghijklmnopqrstuvwxyz'
        self.num = {0:1}
    
    def number(self, level):
        to_return = self.pama[level-1]
        if level > 1:
            to_return += str(self.num[level-1])
        to_return += "."
        
        self.num[level] = 1
        self.num[level-1] = self.num[level-1] + 1

        return to_return
    

#------------------------------------------------------------------------
#
# class PrintMeurgey
#   Meurgey_de_Tupigny numbering system
#
#------------------------------------------------------------------------
class PrintMeurgey():
    def __init__(self):
        self.childnum = [""]
    
    def number(self, level):
        if level == 1:
            dash = ""
        else:
            dash = "-"
            if len(self.childnum) < level:
                self.childnum.append(1)
        
        to_return = (ReportUtils.roman(level) + dash +
                     str(self.childnum[level-1]) + ".")

        if level > 1:
            self.childnum[level-1] += 1
        
        return to_return
    

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
    def __init__(self, doc, database, numbering, showmarriage, showdivorce,\
                 name_display, rlocale):
        #classes
        self._name_display = name_display
        self.doc = doc
        self.database = database
        self.numbering = numbering
        #variables
        self.showmarriage = showmarriage
        self.showdivorce = showdivorce
        self._ = rlocale.translation.sgettext # needed for English
        self._get_date = rlocale.get_date

    def __date_place(self,event):
        if event:
            date = self._get_date(event.get_date_object())
            place_handle = event.get_place_handle()
            if place_handle:
                place = _pd.display_event(self.database, event)
                return("%(event_abbrev)s %(date)s - %(place)s" % {
                    'event_abbrev': event.type.get_abbreviation(self._),
                    'date' : date,
                    'place' : place,
                    })
            else:
                return("%(event_abbrev)s %(date)s" % {
                    'event_abbrev': event.type.get_abbreviation(self._),
                    'date' : date
                    })
        return ""

    def dump_string(self, person, family=None):
        string = self.__date_place(
                    get_birth_or_fallback(self.database, person)
                    )

        tmp = self.__date_place(get_death_or_fallback(self.database, person))
        if string and tmp:
            string += ", "
        string += tmp
        
        if string:
            string = " (" + string + ")"

        if family and self.showmarriage:
            tmp = self.__date_place(get_marriage_or_fallback(self.database,
                                                              family))
            if tmp:
                string += ", " + tmp

        if family and self.showdivorce:
            tmp = self.__date_place(get_divorce_or_fallback(self.database,
                                                              family))
            if tmp:
                string += ", " + tmp

        self.doc.write_text(string)

    def print_person(self, level, person):
        display_num = self.numbering.number(level)
        self.doc.start_paragraph("DR-Level%d" % min(level, 32), display_num)
        mark = ReportUtils.get_person_mark(self.database, person)
        self.doc.write_text(self._name_display.display(person), mark)
        self.dump_string(person)
        self.doc.end_paragraph()
        return display_num
    
    def print_spouse(self, level, spouse_handle, family_handle):
        #Currently print_spouses is the same for all numbering systems.
        if spouse_handle:
            spouse = self.database.get_person_from_handle(spouse_handle)
            mark = ReportUtils.get_person_mark(self.database, spouse)
            self.doc.start_paragraph("DR-Spouse%d" % min(level, 32))
            name = self._name_display.display(spouse)
            self.doc.write_text(
                    self._("sp. %(spouse)s") % {'spouse':name}, mark)
            self.dump_string(spouse, family_handle)
            self.doc.end_paragraph()
        else:
            self.doc.start_paragraph("DR-Spouse%d" % min(level, 32))
            self.doc.write_text(
                    self._("sp. %(spouse)s") % {'spouse':self._('Unknown')})
            self.doc.end_paragraph()

    def print_reference(self, level, person, display_num):
        #Person and their family have already been printed so
        #print reference here
        if person:
            mark = ReportUtils.get_person_mark(self.database, person)
            self.doc.start_paragraph("DR-Spouse%d" % min(level, 32))
            name = self._name_display.display(person)
            self.doc.write_text(
                    self._("sp. see  %(reference)s : %(spouse)s") %
                            {'reference':display_num, 'spouse':name}, mark)
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
    def __init__(self, max_generations, database, objPrint, showdups, rlocale):
        self.max_generations = max_generations
        self.database = database
        self.objPrint = objPrint
        self.showdups = showdups
        self.person_printed = {}
        self._ = rlocale.translation.sgettext # needed for English

    def recurse(self, level, person, curdepth):

        person_handle = person.get_handle()
        display_num = self.objPrint.print_person(level, person)

        if curdepth is None:
            ref_str = display_num
        else:
            ref_str = curdepth + " " + display_num

        if person_handle not in self.person_printed:
            self.person_printed[person_handle] = ref_str

        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)

            spouse_handle = ReportUtils.find_spouse(person, family)

            if not self.showdups and spouse_handle in self.person_printed:
                # Just print a reference
                spouse = self.database.get_person_from_handle(spouse_handle)
                self.objPrint.print_reference(level, spouse,
                        self.person_printed[spouse_handle])
            else:
                self.objPrint.print_spouse(level, spouse_handle, family)

                if spouse_handle:
                    spouse_num = self._("%s sp." % (ref_str))
                    self.person_printed[spouse_handle] = spouse_num

                if level >= self.max_generations:
                    continue

                childlist = family.get_child_ref_list()[:]
                for child_ref in childlist:
                    child = self.database.get_person_from_handle(child_ref.ref)
                    self.recurse(level+1, child, ref_str)


#------------------------------------------------------------------------
#
# DescendantReport
#
#------------------------------------------------------------------------
class DescendantReport(Report):

    def __init__(self, database, options, user):
        """
        Create the DescendantReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen           - Maximum number of generations to include.
        name_format   - Preferred format to display names
        dups          - Whether to include duplicate descendant trees
        incl_private  - Whether to include private data
        """

        Report.__init__(self, database, options, user)

        menu = options.menu

        stdoptions.run_private_data_option(self, menu)

        self.max_generations = menu.get_option_by_name('gen').get_value()
        pid = menu.get_option_by_name('pid').get_value()
        self.center_person = self.database.get_person_from_gramps_id(pid)
        if (self.center_person == None) :
            raise ReportError(_("Person %s is not in the Database") % pid )
        
        sort = Sort(self.database)
    
        lang = menu.get_option_by_name('trans').get_value()
        self._locale = self.set_locale(lang)

        #Initialize the Printinfo class    
        self._showdups = menu.get_option_by_name('dups').get_value()
        numbering = menu.get_option_by_name('numbering').get_value()
        if numbering == "Simple":
            obj = PrintSimple(self._showdups)
        elif numbering == "de Villiers/Pama":
            obj = PrintVilliers()
        elif numbering == "Meurgey de Tupigny":
            obj = PrintMeurgey()
        else:
            raise AttributeError("no such numbering: '%s'" % self.numbering)

        marrs = menu.get_option_by_name('marrs').get_value()
        divs = menu.get_option_by_name('divs').get_value()

        stdoptions.run_name_format_option(self, menu)

        self.objPrint = Printinfo(self.doc, self.database, obj, marrs, divs,
                                  self._name_display, self._locale)
    
    def write_report(self):
        self.doc.start_paragraph("DR-Title")
        name = self._name_display.display(self.center_person)
        # feature request 2356: avoid genitive form
        title = self._("Descendants of %s") % name
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        
        recurse = RecurseDown(self.max_generations, self.database,
                              self.objPrint, self._showdups, self._locale)
        recurse.recurse(1, self.center_person, None)

#------------------------------------------------------------------------
#
# DescendantOptions
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
        
        stdoptions.add_name_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

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

        marrs = BooleanOption(_('Show marriage info'), False)
        marrs.set_help(_("Whether to show marriage information in the report."))
        menu.add_option(category_name, "marrs", marrs)

        divs = BooleanOption(_('Show divorce info'), False)
        divs.set_help(_("Whether to show divorce information in the report."))
        menu.add_option(category_name, "divs", divs)

        dups = BooleanOption(_('Show duplicate trees'), True)
        dups.set_help(
            _("Whether to show duplicate Family Trees in the report."))
        menu.add_option(category_name, "dups", dups)

        stdoptions.add_localization_option(menu, category_name)

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
