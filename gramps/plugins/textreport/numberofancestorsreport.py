#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001       Jesper Zedlitz
# Copyright (C) 2004-2006  Donald Allingham
# Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
# Copyright (C) 2008,2012  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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

"""Reports/Text Reports /Number of Ancestors Report"""

# ------------------------------------------------------------------------
#
# standard python modules
#
# ------------------------------------------------------------------------
import math

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.errors import ReportError
from gramps.gen.plug.menu import PersonOption
from gramps.gen.plug.docgen import (
    IndexMark,
    FontStyle,
    ParagraphStyle,
    FONT_SANS_SERIF,
    PARA_ALIGN_CENTER,
    INDEX_TYPE_TOC,
)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.display.name import displayer as _nd


# ------------------------------------------------------------------------
#
# NumberOfAncestorsReport
#
# ------------------------------------------------------------------------
class NumberOfAncestorsReport(Report):
    """
    This report counts all the ancestors of the specified person.
    """

    def __init__(self, database, options, user):
        """
        Create the NumberOfAncestorsReport object that produces the report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        Menu options:
        name_format   - Preferred format to display names
        incl_private  - Whether to include private data
        """
        Report.__init__(self, database, options, user)

        stdoptions.run_private_data_option(self, options.menu)
        self.__db = self.database

        pid = options.menu.get_option_by_name("pid").get_value()
        self.__person = self.__db.get_person_from_gramps_id(pid)
        if self.__person is None:
            raise ReportError(_("Person %s is not in the Database") % pid)

        self.set_locale(options.menu.get_option_by_name("trans").get_value())

        stdoptions.run_name_format_option(self, options.menu)

    def write_report(self):
        """
        The routine that actually creates the report.
        At this point, the document is opened and ready for writing.
        """
        thisgen = {}
        all_people = {}
        total_theoretical = 0
        thisgen[self.__person.get_handle()] = 1
        ngettext = self._locale.translation.ngettext  # to see "nearby" comments

        self.doc.start_paragraph("NOA-Title")
        name = self._name_display.display(self.__person)
        # feature request 2356: avoid genitive form
        title = self._("Number of Ancestors for %s") % name
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()

        thisgensize = 1
        gen = 0
        while thisgensize > 0:
            thisgensize = 0
            if thisgen != {}:
                thisgensize = len(thisgen)
                gen += 1
                theoretical = math.pow(2, (gen - 1))
                total_theoretical += theoretical
                percent = "(%s%%)" % self._locale.format_string(
                    "%3.2f", ((sum(thisgen.values()) / theoretical) * 100)
                )

                # TC # English return something like:
                # Generation 3 has 2 individuals. (50.00%)
                # Translators: leave all/any {...} untranslated
                text = ngettext(
                    "Generation {number} has {count} individual. {percent}",
                    "Generation {number} has {count} individuals. {percent}",
                    thisgensize,
                ).format(number=gen, count=thisgensize, percent=percent)

                self.doc.start_paragraph("NOA-Normal")
                self.doc.write_text(text)
                self.doc.end_paragraph()

            temp = thisgen
            thisgen = {}
            for person_handle, person_data in temp.items():
                person = self.__db.get_person_from_handle(person_handle)
                family_handle = person.get_main_parents_family_handle()
                if family_handle:
                    family = self.__db.get_family_from_handle(family_handle)
                    father_handle = family.get_father_handle()
                    mother_handle = family.get_mother_handle()
                    if father_handle:
                        thisgen[father_handle] = (
                            thisgen.get(father_handle, 0) + person_data
                        )
                        all_people[father_handle] = (
                            all_people.get(father_handle, 0) + person_data
                        )
                    if mother_handle:
                        thisgen[mother_handle] = (
                            thisgen.get(mother_handle, 0) + person_data
                        )
                        all_people[mother_handle] = (
                            all_people.get(mother_handle, 0) + person_data
                        )

        if total_theoretical != 1:
            percent = "(%3.2f%%)" % (
                (sum(all_people.values()) / (total_theoretical - 1)) * 100
            )
        else:
            percent = 0

        # TC # English return something like:
        # Total ancestors in generations 2 to 3 is 4. (66.67%)
        text = self._(
            "Total ancestors in generations %(second_generation)d "
            "to %(last_generation)d is %(count)d. %(percent)s"
        ) % {
            "second_generation": 2,
            "last_generation": gen,
            "count": len(all_people),
            "percent": percent,
        }

        self.doc.start_paragraph("NOA-Normal")
        self.doc.write_text(text)
        self.doc.end_paragraph()


# ------------------------------------------------------------------------
#
# NumberOfAncestorsOptions
#
# ------------------------------------------------------------------------
class NumberOfAncestorsOptions(MenuReportOptions):
    """
    Defines options for the NumberOfAncestorsReport.
    """

    def __init__(self, name, dbase):
        self.__db = dbase
        self.__pid = None
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """Return a string that describes the subject of the report."""
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        return _nd.display(person)

    def add_menu_options(self, menu):
        """
        Add options to the menu for the Number of Ancestors report.
        """
        category_name = _("Report Options")

        self.__pid = PersonOption(_("Center Person"))
        self.__pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", self.__pid)

        stdoptions.add_name_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_localization_option(menu, category_name)

    def make_default_style(self, default_style):
        """Make the default output style for the Number of Ancestors Report."""
        font = FontStyle()
        font.set_size(16)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_header_level(1)
        para.set_bottom_border(1)
        para.set_bottom_margin(utils.pt2cm(8))
        para.set_font(font)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the title."))
        default_style.add_paragraph_style("NOA-Title", para)

        font = FontStyle()
        font.set_size(12)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(_("The basic style used for the text display."))
        default_style.add_paragraph_style("NOA-Normal", para)
