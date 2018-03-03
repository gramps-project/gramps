#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2012  Brian G. Matherly
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Matt Keenan (matt.keenan@gmail.com)
# Copyright (C) 2013-2014  Paul Franklin
# Copyright (C) 2010,2015  Craig J. Anderson
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
# Gramps modules
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
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.utils.db import (get_birth_or_fallback, get_death_or_fallback,
                                 get_marriage_or_fallback,
                                 get_divorce_or_fallback)
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.display.place import displayer as _pd
from gramps.gen.display.name import displayer as _nd

#------------------------------------------------------------------------
#
# PrintDAboville
#
#------------------------------------------------------------------------
class PrintDAboville():
    """
    d'Aboville numbering system

    (according to en.wikipedia.org/Genealogical_numbering_systems
    his name is spelled "d'Aboville" and not "D'Aboville" but I will
    leave this class name alone, mainly fixing the translated string,
    so that it is both accurate and also agrees with the DDR string)
    """

    def __init__(self):
        self.num = [0]

    def number(self, level):
        """ Make the current number based upon the current level """
        # Set up the array based on the current level
        while len(self.num) > level:  # We can go from a level 8 to level 2
            self.num.pop()
        if len(self.num) < level:
            self.num.append(0)

        # Increment the current level - initalized with 0
        self.num[-1] += 1

        # Display
        return ".".join(map(str, self.num))


#------------------------------------------------------------------------
#
# PrintHenry
#
#------------------------------------------------------------------------
class PrintHenry():
    """ Henry numbering system """

    def __init__(self, modified=False):
        self.henry = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.modified = modified
        self.num = [0]

    def number(self, level):
        """ Make the current number based upon the current level """
        # Set up the array based on the current level
        while len(self.num) > level:  # We can go from a level 8 to level 2
            self.num.pop()
        if len(self.num) < level:
            self.num.append(0)

        # Incriment the current level - initalized with 0
        self.num[-1] += 1

        def strd(inti):
            """ no change needed """
            return "(" + str(inti) + ")"

        # Display
        if self.modified is False:
            return "".join(map(
                lambda x: self.henry[x-1] if x <= len(self.henry) else strd(x)
                , self.num))
        else:
            return "".join(map(
                lambda x: str(x) if x < 10 else strd(x)
                , self.num))


#------------------------------------------------------------------------
#
# PrintSimple
#
#------------------------------------------------------------------------
class PrintSimple:
    """ Simple numbering system """

    def __init__(self, showdups):
        self.showdups = showdups
        self.num = {0:1}

    def number(self, level):
        """ the number of the person """
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
class PrintVilliers:
    """ de_Villiers_Pama numbering system """

    def __init__(self):
        self.pama = 'abcdefghijklmnopqrstuvwxyz'
        self.num = {0:1}

    def number(self, level):
        """ the number of the person """
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
class PrintMeurgey:
    """ Meurgey_de_Tupigny numbering system """

    def __init__(self):
        self.childnum = [""]

    def number(self, level):
        """ the number of the person """
        if level == 1:
            dash = ""
        else:
            dash = "-"
            if len(self.childnum) < level:
                self.childnum.append(1)

        to_return = (utils.roman(level) + dash +
                     str(self.childnum[level-1]) + ".")

        if level > 1:
            self.childnum[level-1] += 1

        return to_return


#------------------------------------------------------------------------
#
# Printinfo
#
#------------------------------------------------------------------------
class Printinfo:
    """
    A base class used to help make the individual numbering system classes.
    This class must first be initialized with set_class_vars
    """
    def __init__(self, doc, database, numbering, showmarriage, showdivorce,
                 name_display, rlocale, want_ids, pformat):
        #classes
        self._name_display = name_display
        self.doc = doc
        self.database = database
        self.numbering = numbering
        #variables
        self.showmarriage = showmarriage
        self.showdivorce = showdivorce
        self.want_ids = want_ids
        self._ = rlocale.translation.sgettext # needed for English
        self._get_date = rlocale.get_date
        self.pformat = pformat

    def __date_place(self, event):
        """ return the date and/or place an event happened """
        if event:
            date = self._get_date(event.get_date_object())
            place_handle = event.get_place_handle()
            if place_handle:
                place = _pd.display_event(self.database, event, self.pformat)
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
        """ generate a descriptive string for a person """
        string = self.__date_place(
            get_birth_or_fallback(self.database, person))

        tmp = self.__date_place(
            get_death_or_fallback(self.database, person))
        if string and tmp:
            string += self._(", ") # Arabic OK
        string += tmp

        if string:
            string = " (" + string + ")"

        if family and self.showmarriage:
            tmp = self.__date_place(
                get_marriage_or_fallback(self.database, family))
            if tmp:
                string += self._(", ") + tmp # Arabic OK

        if family and self.showdivorce:
            tmp = self.__date_place(
                get_divorce_or_fallback(self.database, family))
            if tmp:
                string += self._(", ") + tmp # Arabic OK

        if family and self.want_ids:
            string += ' (%s)' % family.get_gramps_id()

        self.doc.write_text(string)

    def print_person(self, level, person):
        """ print the person """
        display_num = self.numbering.number(level)
        self.doc.start_paragraph("DR-Level%d" % min(level, 32), display_num)
        mark = utils.get_person_mark(self.database, person)
        self.doc.write_text(self._name_display.display(person), mark)
        if self.want_ids:
            self.doc.write_text(' (%s)' % person.get_gramps_id())
        self.dump_string(person)
        self.doc.end_paragraph()
        return display_num

    def print_spouse(self, level, spouse_handle, family_handle):
        """ print the spouse """
        #Currently print_spouses is the same for all numbering systems.
        if spouse_handle:
            spouse = self.database.get_person_from_handle(spouse_handle)
            mark = utils.get_person_mark(self.database, spouse)
            self.doc.start_paragraph("DR-Spouse%d" % min(level, 32))
            name = self._name_display.display(spouse)
            self.doc.write_text(
                self._("sp. %(spouse)s") % {'spouse':name}, mark)
            if self.want_ids:
                self.doc.write_text(' (%s)' % spouse.get_gramps_id())
            self.dump_string(spouse, family_handle)
            self.doc.end_paragraph()
        else:
            self.doc.start_paragraph("DR-Spouse%d" % min(level, 32))
            self.doc.write_text(
                self._("sp. %(spouse)s") % {'spouse':self._('Unknown')})
            self.doc.end_paragraph()

    def print_reference(self, level, person, display_num):
        """ print the reference """
        #Person and their family have already been printed so
        #print reference here
        if person:
            mark = utils.get_person_mark(self.database, person)
            self.doc.start_paragraph("DR-Spouse%d" % min(level, 32))
            name = self._name_display.display(person)
            self.doc.write_text(self._("sp. see %(reference)s: %(spouse)s"
                                      ) % {'reference' : display_num,
                                           'spouse'    : name},
                                mark)
            self.doc.end_paragraph()


#------------------------------------------------------------------------
#
# RecurseDown
#
#------------------------------------------------------------------------
class RecurseDown:
    """
    A simple object to recurse from a person down through their descendants

    The arguments are:

    max_generations: The max number of generations
    database:  The database object
    obj_print: A Printinfo derived class that prints person
               information on the report
    """
    def __init__(self, max_generations, database,
                 obj_print, showdups, rlocale):
        self.max_generations = max_generations
        self.database = database
        self.obj_print = obj_print
        self.showdups = showdups
        self.person_printed = {}
        self._ = rlocale.translation.sgettext # needed for English

    def recurse(self, level, person, curdepth):
        """ recurse """

        person_handle = person.get_handle()
        display_num = self.obj_print.print_person(level, person)

        if curdepth is None:
            ref_str = display_num
        else:
            ref_str = curdepth + " " + display_num

        if person_handle not in self.person_printed:
            self.person_printed[person_handle] = ref_str

        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)

            spouse_handle = utils.find_spouse(person, family)

            if not self.showdups and spouse_handle in self.person_printed:
                # Just print a reference
                spouse = self.database.get_person_from_handle(spouse_handle)
                self.obj_print.print_reference(
                    level, spouse, self.person_printed[spouse_handle])
            else:
                self.obj_print.print_spouse(level, spouse_handle, family)

                if spouse_handle:
                    spouse_num = self._("%s sp.") % ref_str
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
    """ Descendant report """

    def __init__(self, database, options, user):
        """
        Create the DescendantReport object that produces the report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.

        gen           - Maximum number of generations to include.
        name_format   - Preferred format to display names
        dups          - Whether to include duplicate descendant trees
        incl_private  - Whether to include private data
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        inc_id        - Whether to include Gramps IDs
        """

        Report.__init__(self, database, options, user)

        menu = options.menu

        self.set_locale(menu.get_option_by_name('trans').get_value())

        stdoptions.run_date_format_option(self, menu)

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)

        self.max_generations = menu.get_option_by_name('gen').get_value()
        self.want_ids = menu.get_option_by_name('inc_id').get_value()

        pid = menu.get_option_by_name('pid').get_value()
        self.center_person = self.database.get_person_from_gramps_id(pid)
        if self.center_person is None:
            raise ReportError(_("Person %s is not in the Database") % pid)

        #Initialize the Printinfo class
        self._showdups = menu.get_option_by_name('dups').get_value()
        numbering = menu.get_option_by_name('numbering').get_value()
        if numbering == "Simple":
            obj = PrintSimple(self._showdups)
        elif numbering == "Henry":
            obj = PrintHenry()
        elif numbering == "Modified Henry":
            obj = PrintHenry(modified=True)
        elif numbering == "d'Aboville":
            obj = PrintDAboville()
        elif numbering == "de Villiers/Pama":
            obj = PrintVilliers()
        elif numbering == "Meurgey de Tupigny":
            obj = PrintMeurgey()
        else:
            raise AttributeError("no such numbering: '%s'" % numbering)

        marrs = menu.get_option_by_name('marrs').get_value()
        divs = menu.get_option_by_name('divs').get_value()

        stdoptions.run_name_format_option(self, menu)

        pformat = menu.get_option_by_name("place_format").get_value()

        self.obj_print = Printinfo(self.doc, self.database, obj, marrs, divs,
                                   self._name_display, self._locale,
                                   self.want_ids, pformat)

    def write_report(self):
        self.doc.start_paragraph("DR-Title")
        name = self._name_display.display(self.center_person)
        # feature request 2356: avoid genitive form
        title = self._("Descendants of %s") % name
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()

        recurse = RecurseDown(self.max_generations, self.database,
                              self.obj_print, self._showdups, self._locale)
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
        self.__db = dbase
        self.__pid = None
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """ Return a string that describes the subject of the report. """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        return _nd.display(person)

    def add_menu_options(self, menu):
        category_name = _("Report Options")

        self.__pid = PersonOption(_("Center Person"))
        self.__pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", self.__pid)

        numbering = EnumeratedListOption(_("Numbering system"), "Simple")
        numbering.set_items([
            ("Simple", _("Simple numbering")),
            ("d'Aboville", _("d'Aboville numbering")),
            ("Henry", _("Henry numbering")),
            ("Modified Henry", _("Modified Henry numbering")),
            ("de Villiers/Pama", _("de Villiers/Pama numbering")),
            ("Meurgey de Tupigny", _("Meurgey de Tupigny numbering"))])
        numbering.set_help(_("The numbering system to be used"))
        menu.add_option(category_name, "numbering", numbering)

        gen = NumberOption(_("Generations"), 10, 1, 15)
        gen.set_help(_("The number of generations to include in the report"))
        menu.add_option(category_name, "gen", gen)

        stdoptions.add_gramps_id_option(menu, category_name)

        marrs = BooleanOption(_('Show marriage info'), False)
        marrs.set_help(
            _("Whether to show marriage information in the report."))
        menu.add_option(category_name, "marrs", marrs)

        divs = BooleanOption(_('Show divorce info'), False)
        divs.set_help(_("Whether to show divorce information in the report."))
        menu.add_option(category_name, "divs", divs)

        dups = BooleanOption(_('Show duplicate trees'), True)
        dups.set_help(
            _("Whether to show duplicate Family Trees in the report."))
        menu.add_option(category_name, "dups", dups)

        category_name = _("Report Options (2)")

        stdoptions.add_name_format_option(menu, category_name)

        stdoptions.add_place_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

    def make_default_style(self, default_style):
        """Make the default output style for the Descendant Report."""
        fstyle = FontStyle()
        fstyle.set_size(12)
        fstyle.set_type_face(FONT_SANS_SERIF)
        fstyle.set_bold(1)
        pstyle = ParagraphStyle()
        pstyle.set_header_level(1)
        pstyle.set_bottom_border(1)
        pstyle.set_top_margin(utils.pt2cm(3))
        pstyle.set_bottom_margin(utils.pt2cm(3))
        pstyle.set_font(fstyle)
        pstyle.set_alignment(PARA_ALIGN_CENTER)
        pstyle.set_description(_("The style used for the title."))
        default_style.add_paragraph_style("DR-Title", pstyle)

        fstyle = FontStyle()
        fstyle.set_size(10)
        for i in range(1, 33):
            pstyle = ParagraphStyle()
            pstyle.set_font(fstyle)
            pstyle.set_top_margin(utils.pt2cm(fstyle.get_size()*0.125))
            pstyle.set_bottom_margin(
                utils.pt2cm(fstyle.get_size()*0.125))
            pstyle.set_first_indent(-0.5)
            pstyle.set_left_margin(min(10.0, float(i-0.5)))
            pstyle.set_description(
                _("The style used for the level %d display.") % i)
            default_style.add_paragraph_style("DR-Level%d" % min(i, 32),
                                              pstyle)

            pstyle = ParagraphStyle()
            pstyle.set_font(fstyle)
            pstyle.set_top_margin(utils.pt2cm(fstyle.get_size()*0.125))
            pstyle.set_bottom_margin(
                utils.pt2cm(fstyle.get_size()*0.125))
            pstyle.set_left_margin(min(10.0, float(i-0.5)))
            pstyle.set_description(
                _("The style used for the spouse level %d display.") % i)
            default_style.add_paragraph_style("DR-Spouse%d" % min(i, 32),
                                              pstyle)
