#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2012  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2012-2014  Paul Franklin
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

"""Reports/Text Reports/Ahnentafel Report"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import math

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.errors import ReportError
from gramps.gen.lib import ChildRefType
from gramps.gen.plug.menu import (BooleanOption, NumberOption, PersonOption)
from gramps.gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                                    FONT_SANS_SERIF, INDEX_TYPE_TOC,
                                    PARA_ALIGN_CENTER)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.plugins.lib.libnarrate import Narrator
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.display.name import displayer as _nd

#------------------------------------------------------------------------
#
# log2val
#
#------------------------------------------------------------------------
def log2(val):
    """
    Calculate the log base 2 of a number
    """
    return int(math.log(val, 2))

#------------------------------------------------------------------------
#
# AncestorReport
#
#------------------------------------------------------------------------
class AncestorReport(Report):
    """
    Ancestor Report class
    """
    def __init__(self, database, options, user):
        """
        Create the AncestorReport object that produces the Ahnentafel report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.

        gen       - Maximum number of generations to include.
        pagebbg   - Whether to include page breaks between generations.
        name_format   - Preferred format to display names
        incl_private  - Whether to include private data
        namebrk       - Whether a line break should follow the name
        inc_id        - Whether to include Gramps IDs
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """
        Report.__init__(self, database, options, user)

        self.map = {}
        menu = options.menu

        self.set_locale(menu.get_option_by_name('trans').get_value())

        stdoptions.run_date_format_option(self, menu)

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)

        self.max_generations = menu.get_option_by_name('maxgen').get_value()
        self.pgbrk = menu.get_option_by_name('pagebbg').get_value()
        self.opt_namebrk = menu.get_option_by_name('namebrk').get_value()
        self.want_ids = menu.get_option_by_name('inc_id').get_value()

        pid = menu.get_option_by_name('pid').get_value()
        self.center_person = self.database.get_person_from_gramps_id(pid)
        if self.center_person is None:
            raise ReportError(_("Person %s is not in the Database") % pid)

        stdoptions.run_name_format_option(self, menu)

        self.__narrator = Narrator(self.database,  use_fulldate=True,
                                   nlocale=self._locale)

    def apply_filter(self, person_handle, index, generation=1):
        """
        Recursive function to walk back all parents of the current person.
        When max_generations are hit, we stop the traversal.
        """

        # check for end of the current recursion level. This happens
        # if the person handle is None, or if the max_generations is hit

        if not person_handle or generation > self.max_generations:
            return

        # store the person in the map based off their index number
        # which is passed to the routine.
        self.map[index] = person_handle

        # retrieve the Person instance from the database from the
        # passed person_handle and find the parents from the list.
        # Since this report is for natural parents (birth parents),
        # we have to handle that parents may not

        person = self.database.get_person_from_handle(person_handle)
        if person is None:
            return

        father_handle = None
        mother_handle = None
        for family_handle in person.get_parent_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)

            # filter the child_ref_list to find the reference that matches
            # the passed person. There should be exactly one, but there is
            # nothing that prevents the same child in the list multiple times.

            ref = [ c for c in family.get_child_ref_list()
                    if c.get_reference_handle() == person_handle]
            if ref:

                # If the father_handle is not defined and the relationship is
                # BIRTH, then we have found the birth father. Same applies to
                # the birth mother. If for some reason, the we have multiple
                # people defined as the birth parents, we will select based on
                # priority in the list

                if not father_handle and \
                   ref[0].get_father_relation() == ChildRefType.BIRTH:
                    father_handle = family.get_father_handle()
                if not mother_handle and \
                   ref[0].get_mother_relation() == ChildRefType.BIRTH:
                    mother_handle = family.get_mother_handle()

        # Recursively call the function. It is okay if the handle is None,
        # since routine handles a handle of None

        self.apply_filter(father_handle, index*2, generation+1)
        self.apply_filter(mother_handle, (index*2)+1, generation+1)

    def write_report(self):
        """
        The routine the actually creates the report. At this point, the document
        is opened and ready for writing.
        """

        # Call apply_filter to build the self.map array of people in the
        # database that match the ancestry.

        self.apply_filter(self.center_person.get_handle(), 1)

        # Write the title line. Set an INDEX mark so that this section will be
        # identified as a major category if this is included in a Book report.

        name = self._name_display.display_formal(self.center_person)
        # feature request 2356: avoid genitive form
        title = self._("Ahnentafel Report for %s") % name
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.start_paragraph("AHN-Title")
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()

        # get the entries out of the map, and sort them.

        generation = 0

        for key in sorted(self.map):

            # check the index number to see if we need to start a new generation
            if generation == log2(key):

                # generate a page break if requested
                if self.pgbrk and generation > 0:
                    self.doc.page_break()
                generation += 1

                # Create the Generation title, set an index marker
                gen_text = self._("Generation %d") % generation
                mark = None # don't need any with no page breaks
                if self.pgbrk:
                    mark = IndexMark(gen_text, INDEX_TYPE_TOC, 2)
                self.doc.start_paragraph("AHN-Generation")
                self.doc.write_text(gen_text, mark)
                self.doc.end_paragraph()

            # Build the entry

            self.doc.start_paragraph("AHN-Entry","%d." % key)
            person = self.database.get_person_from_handle(self.map[key])
            if person is None:
                continue
            name = self._name_display.display(person)
            mark = utils.get_person_mark(self.database, person)

            # write the name in bold
            self.doc.start_bold()
            self.doc.write_text(name.strip(), mark)
            self.doc.end_bold()
            if self.want_ids:
                self.doc.write_text(' (%s)' % person.get_gramps_id())

            # terminate with a period if it is not already terminated.
            # This can happen if the person's name ends with something 'Jr.'
            if name[-1:] == '.' and not self.want_ids:
                self.doc.write_text(" ")
            else:
                self.doc.write_text(". ")

            # Add a line break if requested
            if self.opt_namebrk:
                self.doc.write_text('\n')

            self.__narrator.set_subject(person)
            self.doc.write_text(self.__narrator.get_born_string())
            self.doc.write_text(self.__narrator.get_baptised_string())
            self.doc.write_text(self.__narrator.get_christened_string())
            self.doc.write_text(self.__narrator.get_died_string())
            self.doc.write_text(self.__narrator.get_buried_string())

            self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# AncestorOptions
#
#------------------------------------------------------------------------
class AncestorOptions(MenuReportOptions):

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
        """
        Add options to the menu for the ancestor report.
        """
        category_name = _("Report Options")

        self.__pid = PersonOption(_("Center Person"))
        self.__pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", self.__pid)

        maxgen = NumberOption(_("Generations"), 10, 1, 100)
        maxgen.set_help(
            _("The number of generations to include in the report"))
        menu.add_option(category_name, "maxgen", maxgen)

        stdoptions.add_gramps_id_option(menu, category_name)

        pagebbg = BooleanOption(_("Page break between generations"), False)
        pagebbg.set_help(
                     _("Whether to start a new page after each generation."))
        menu.add_option(category_name, "pagebbg", pagebbg)

        namebrk = BooleanOption(_("Add linebreak after each name"), False)
        namebrk.set_help(_("Whether a line break should follow the name."))
        menu.add_option(category_name, "namebrk", namebrk)

        category_name = _("Report Options (2)")

        stdoptions.add_name_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

    def make_default_style(self, default_style):
        """
        Make the default output style for the Ahnentafel report.

        There are 3 paragraph styles for this report.

        AHN_Title - The title for the report. The options are:

            Font      : Sans Serif
                        Bold
                        16pt
            Paragraph : First level header
                        0.25cm top and bottom margin
                        Centered

        AHN-Generation - Used for the generation header

            Font      : Sans Serif
                        Italic
                        14pt
            Paragraph : Second level header
                        0.125cm top and bottom margins

        AHN - Normal text display for each entry

            Font      : default
            Paragraph : 1cm margin, with first indent of -1cm
                        0.125cm top and bottom margins
        """

        #
        # AHN-Title
        #
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=16, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the title.'))
        default_style.add_paragraph_style("AHN-Title", para)

        #
        # AHN-Generation
        #
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=14, italic=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set_top_margin(0.125)
        para.set_bottom_margin(0.125)
        para.set_description(_('The style used for the generation header.'))
        default_style.add_paragraph_style("AHN-Generation", para)

        #
        # AHN-Entry
        #
        para = ParagraphStyle()
        para.set(first_indent=-1.0, lmargin=1.0)
        para.set_top_margin(0.125)
        para.set_bottom_margin(0.125)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("AHN-Entry", para)
