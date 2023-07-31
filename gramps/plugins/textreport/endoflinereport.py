#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2012  Brian G. Matherly
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

"""Reports/Text Reports/End of Line Report"""

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
#
# gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.errors import ReportError
from gramps.gen.plug.docgen import (
    IndexMark,
    FontStyle,
    ParagraphStyle,
    TableStyle,
    TableCellStyle,
    FONT_SANS_SERIF,
    INDEX_TYPE_TOC,
    PARA_ALIGN_CENTER,
)
from gramps.gen.plug.menu import PersonOption
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.display.name import displayer as _nd


# ------------------------------------------------------------------------
#
# EndOfLineReport
#
# ------------------------------------------------------------------------
class EndOfLineReport(Report):
    """EndOfLine Report"""

    def __init__(self, database, options, user):
        """
        Create the EndOfLineReport object that produces the report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.
        name_format   - Preferred format to display names
        incl_private  - Whether to include private data
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """
        Report.__init__(self, database, options, user)

        menu = options.menu

        self.set_locale(menu.get_option_by_name("trans").get_value())

        stdoptions.run_date_format_option(self, menu)

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)

        pid = menu.get_option_by_name("pid").get_value()
        self.center_person = self.database.get_person_from_gramps_id(pid)
        if self.center_person is None:
            raise ReportError(_("Person %s is not in the Database") % pid)

        stdoptions.run_name_format_option(self, menu)

        # eol_map is a map whose:
        #   keys are the generations of the people
        #   values are a map whose:
        #      keys are person handles
        #      values are an array whose:
        #         elements are an array of ancestor person handles that link
        #         the eol person handle to the person or interest
        # eol_map[generation][person_handle][pedigree_idx][ancestor_handle_idx]
        #
        # There is an array of pedigrees because one person could show up twice
        # in one generation (descendants marrying). Most people only have one
        # pedigree.
        #
        # eol_map is populated by get_eol() which calls itself recursively.
        self.eol_map = {}
        self.get_eol(self.center_person, 1, [])

    def get_eol(self, person, gen, pedigree):
        """
        Recursively find the end of the line for each person
        """
        person_handle = person.get_handle()
        new_pedigree = list(pedigree) + [person_handle]
        person_is_eol = False
        families = person.get_parent_family_handle_list()

        if person_handle in pedigree:
            # This is a severe error!
            # It indicates a loop in ancestry: A -> B -> A
            person_is_eol = True
        elif not families:
            person_is_eol = True
        else:
            for family_handle in families:
                family = self.database.get_family_from_handle(family_handle)
                father_handle = family.get_father_handle()
                mother_handle = family.get_mother_handle()
                if father_handle:
                    father = self.database.get_person_from_handle(father_handle)
                    self.get_eol(father, gen + 1, new_pedigree)
                if mother_handle:
                    mother = self.database.get_person_from_handle(mother_handle)
                    self.get_eol(mother, gen + 1, new_pedigree)

                if not father_handle or not mother_handle:
                    person_is_eol = True

        if person_is_eol:
            # This person is the end of a line
            if gen not in self.eol_map:
                self.eol_map[gen] = {}
            if person_handle not in self.eol_map[gen]:
                self.eol_map[gen][person_handle] = []
            self.eol_map[gen][person_handle].append(new_pedigree)

    def write_report(self):
        """
        The routine that actually creates the report.
        At this point, the document is opened and ready for writing.
        """
        pname = self._name_display.display(self.center_person)

        self.doc.start_paragraph("EOL-Title")
        # feature request 2356: avoid genitive form
        title = self._("End of Line Report for %s") % pname
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()

        self.doc.start_paragraph("EOL-Subtitle")
        # feature request 2356: avoid genitive form
        title = self._("All the ancestors of %s who are missing a parent") % pname
        self.doc.write_text(title)
        self.doc.end_paragraph()

        self.doc.start_table("EolTable", "EOL-Table")
        for generation, handles in sorted(self.eol_map.items()):
            self.write_generation_row(generation)
            for person_handle, pedigrees in handles.items():
                self.write_person_row(person_handle)
                list(map(self.write_pedigree_row, pedigrees))
        self.doc.end_table()

    def write_generation_row(self, generation):
        """
        Write out a row in the table showing the generation.
        """
        self.doc.start_row()
        self.doc.start_cell("EOL_GenerationCell", 2)
        self.doc.start_paragraph("EOL-Generation")
        self.doc.write_text(self._("Generation %d") % generation)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

    def write_person_row(self, person_handle):
        """
        Write a row in the table with information about the given person.
        """
        person = self.database.get_person_from_handle(person_handle)

        name = self._name_display.display(person)
        mark = utils.get_person_mark(self.database, person)
        birth_date = ""
        birth_ref = person.get_birth_ref()
        if birth_ref:
            event = self.database.get_event_from_handle(birth_ref.ref)
            birth_date = self._get_date(event.get_date_object())
        death_date = ""
        death_ref = person.get_death_ref()
        if death_ref:
            event = self.database.get_event_from_handle(death_ref.ref)
            death_date = self._get_date(event.get_date_object())
        dates = ""
        if birth_date or death_date:
            dates = " (%(birth_date)s - %(death_date)s)" % {
                "birth_date": birth_date,
                "death_date": death_date,
            }

        self.doc.start_row()
        self.doc.start_cell("EOL-TableCell", 2)
        self.doc.start_paragraph("EOL-Normal")
        self.doc.write_text(name, mark)
        self.doc.write_text(dates)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

    def write_pedigree_row(self, pedigree):
        """
        Write a row in the table with with the person's family line.

        pedigree is an array containing the names of the people in the pedigree
        """
        names = []
        for person_handle in pedigree:
            person = self.database.get_person_from_handle(person_handle)
            names.append(self._name_display.display(person))
        text = " -- ".join(names)
        self.doc.start_row()
        self.doc.start_cell("EOL-TableCell")
        self.doc.end_cell()
        self.doc.start_cell("EOL-TableCell")
        self.doc.start_paragraph("EOL-Pedigree")
        self.doc.write_text(text)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()


# ------------------------------------------------------------------------
#
# EndOfLineOptions
#
# ------------------------------------------------------------------------
class EndOfLineOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
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
        Add options to the menu for the End of Line report.
        """
        category_name = _("Report Options")

        self.__pid = PersonOption(_("Center Person"))
        self.__pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", self.__pid)

        stdoptions.add_name_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

    def make_default_style(self, default_style):
        """Make the default output style for the End of Line Report."""
        # Paragraph Styles
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
        default_style.add_paragraph_style("EOL-Title", para)

        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=12, italic=1)
        para = ParagraphStyle()
        para.set_bottom_margin(utils.pt2cm(6))
        para.set_font(font)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the subtitle."))
        default_style.add_paragraph_style("EOL-Subtitle", para)

        font = FontStyle()
        font.set_size(10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(utils.pt2cm(6))
        para.set_bottom_margin(utils.pt2cm(6))
        para.set_description(_("The basic style used for the text display."))
        default_style.add_paragraph_style("EOL-Normal", para)

        font = FontStyle()
        font.set_size(12)
        font.set_italic(True)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(utils.pt2cm(6))
        para.set_description(_("The style used for the generation header."))
        default_style.add_paragraph_style("EOL-Generation", para)

        font = FontStyle()
        font.set_size(8)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(0)
        para.set_bottom_margin(utils.pt2cm(6))
        para.set_description(_("The style used for details."))
        default_style.add_paragraph_style("EOL-Pedigree", para)

        # Table Styles
        cell = TableCellStyle()
        default_style.add_cell_style("EOL-TableCell", cell)

        cell = TableCellStyle()
        cell.set_bottom_border(1)
        default_style.add_cell_style("EOL_GenerationCell", cell)

        table = TableStyle()
        table.set_width(100)
        table.set_columns(2)
        table.set_column_width(0, 10)
        table.set_column_width(1, 90)
        default_style.add_table_style("EOL-Table", table)
