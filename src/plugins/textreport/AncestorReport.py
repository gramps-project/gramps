#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
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

"""Reports/Text Reports/Ahnentafel Report"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import math
from gettext import gettext as _

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from BasicUtils import name_displayer
from Errors import ReportError
from gen.lib import ChildRefType
from gen.plug.menu import BooleanOption, NumberOption, PersonOption, \
                          EnumeratedListOption
from gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                             FONT_SANS_SERIF, INDEX_TYPE_TOC, 
                             PARA_ALIGN_CENTER)
from ReportBase import Report, ReportUtils, MenuReportOptions
import TransUtils
from libnarrate import Narrator
from libtranslate import Translator

#------------------------------------------------------------------------
#
# log2val
#
#------------------------------------------------------------------------
def log2(val):
    """
    Calculate the log base 2 of a number
    """
    return int(math.log10(val)/math.log10(2))

#------------------------------------------------------------------------
#
# AncestorReport
#
#------------------------------------------------------------------------
class AncestorReport(Report):
    """
    Ancestor Report class
    """
    def __init__(self, database, options_class):
        """
        Create the AncestorReport object that produces the Ahnentafel report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen       - Maximum number of generations to include.
        pagebbg   - Whether to include page breaks between generations.

        """

        Report.__init__(self, database, options_class)

        self.map = {}
        
        menu = options_class.menu
        self.max_generations = menu.get_option_by_name('maxgen').get_value()
        self.pgbrk = menu.get_option_by_name('pagebbg').get_value()
        self.opt_namebrk = menu.get_option_by_name('namebrk').get_value()
        pid = menu.get_option_by_name('pid').get_value()
        self.center_person = database.get_person_from_gramps_id(pid)
        if (self.center_person == None) :
            raise ReportError(_("Person %s is not in the Database") % pid )
        language = menu.get_option_by_name('trans').get_value()
        translator = Translator(language)
        self._ = translator.get_text
        self.__narrator = Narrator(self.database, 
                                   translator=translator)

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

        # Write the title line. Set in INDEX marker so that this section will be
        # identified as a major category if this is included in a Book report.

        name = name_displayer.display_formal(self.center_person)
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
                mark =  IndexMark(title, INDEX_TYPE_TOC, 2)  
                self.doc.start_paragraph("AHN-Generation")
                self.doc.write_text(self._("Generation %d") % generation, mark)
                self.doc.end_paragraph()

            # Build the entry

            self.doc.start_paragraph("AHN-Entry","%d." % key)
            person = self.database.get_person_from_handle(self.map[key])
            name = name_displayer.display(person)
            mark = ReportUtils.get_person_mark(self.database, person)
        
            # write the name in bold
            self.doc.start_bold()
            self.doc.write_text(name.strip(), mark)
            self.doc.end_bold()

            # terminate with a period if it is not already terminated. 
            # This can happen if the person's name ends with something 'Jr.'
            if name[-1:] == '.':
                self.doc.write_text(" ")
            else:
                self.doc.write_text(". ")

            # Add a line break if requested (not implemented yet)
            if self.opt_namebrk:
                self.doc.write_text('\n')

            self.__narrator.set_subject(person)
            self.doc.write_text(self.__narrator.get_born_string())
            self.doc.write_text(self.__narrator.get_baptized_string())
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
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """
        Add options to the menu for the ancestor report.
        """
        category_name = _("Report Options")
        
        pid = PersonOption(_("Center Person"))
        pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", pid)
        
        maxgen = NumberOption(_("Generations"), 10, 1, 15)
        maxgen.set_help(_("The number of generations to include in the report"))
        menu.add_option(category_name, "maxgen", maxgen)
        
        pagebbg = BooleanOption(_("Page break between generations"), False)
        pagebbg.set_help(
                     _("Whether to start a new page after each generation."))
        menu.add_option(category_name, "pagebbg", pagebbg)
        
        namebrk = BooleanOption(_("Add linebreak after each name"), False)
        namebrk.set_help(_("Indicates if a line break should follow the name."))
        menu.add_option(category_name, "namebrk", namebrk)
        
        trans = EnumeratedListOption(_("Translation"), 
                                      Translator.DEFAULT_TRANSLATION_STR)
        trans.add_item(Translator.DEFAULT_TRANSLATION_STR, _("default"))
        for language in TransUtils.get_available_translations():
            trans.add_item(language, language)
        trans.set_help(_("The translation to be used for the report."))
        menu.add_option(category_name, "trans", trans)

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
        para.set_description(_('The style used for the title of the page.'))
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
