#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001       Jesper Zedlitz
# Copyright (C) 2004-2006  Donald Allingham
# Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
# Copyright (C) 2008       Brian G. Matherly
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

"""Reports/Text Reports /Number of Ancestors Report"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
from gettext import ngettext
import locale
import math

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import PluginManager
from gen.plug.menu import PersonOption
from ReportBase import Report, MenuReportOptions, ReportUtils, CATEGORY_TEXT
from BasicUtils import name_displayer
from gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                            FONT_SANS_SERIF, PARA_ALIGN_CENTER,
                            INDEX_TYPE_TOC)

#------------------------------------------------------------------------
#
# NumberOfAncestorsReport
#
#------------------------------------------------------------------------
class NumberOfAncestorsReport(Report):
    """
    This report counts all the ancestors of the specified person.
    """
    def __init__(self, database, options_class):
        """
        Create the NumberOfAncestorsReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report
        """
        Report.__init__(self, database, options_class)
        self.__db = database
        pid = options_class.menu.get_option_by_name('pid').get_value()
        self.__person = database.get_person_from_gramps_id(pid)

    def write_report(self):
        """
        The routine the actually creates the report. At this point, the document
        is opened and ready for writing.
        """
        thisgen = {}
        all_people = {}
        total_theoretical = 0
        thisgen[self.__person.get_handle()]=1
        
        self.doc.start_paragraph("NOA-Title")
        name = name_displayer.display(self.__person)
        title = _("Number of Ancestors for %s") % name
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
                theoretical = math.pow(2, ( gen - 1 ) )
                total_theoretical += theoretical
                percent = '(%s%%)' % locale.format('%3.2f', 
                    ((sum(thisgen.itervalues()) / theoretical ) * 100))
                
                # TC # English return something like:
                # Generation 3 has 2 individuals. (50.00%)
                text = ngettext(
                    "Generation %(generation)d has %(count)d individual. %(percent)s",
                    "Generation %(generation)d has %(count)d individuals. %(percent)s",
                    thisgensize) % {'generation': gen, 'count': thisgensize, 'percent': percent}
                            
                self.doc.start_paragraph('NOA-Normal')
                self.doc.write_text(text)
                self.doc.end_paragraph()
                
            temp = thisgen
            thisgen = {}
            for person_handle, person_data in temp.iteritems():
                person = self.__db.get_person_from_handle(person_handle)
                family_handle = person.get_main_parents_family_handle()
                if family_handle:
                    family = self.__db.get_family_from_handle(family_handle)
                    father_handle = family.get_father_handle()
                    mother_handle = family.get_mother_handle()
                    if father_handle:
                        thisgen[father_handle] = \
                            thisgen.get(father_handle, 0) + person_data
                        all_people[father_handle] = \
                                            all_people.get(father_handle, 0) + \
                                            person_data
                    if mother_handle:
                        thisgen[mother_handle] = \
                            thisgen.get(mother_handle, 0) + person_data
                        all_people[mother_handle] = \
                                            all_people.get(mother_handle, 0) + \
                                            person_data

        if( total_theoretical != 1 ):
            percent = '(%3.2f%%)' % (( sum(all_people.itervalues()) 
                                        / (total_theoretical-1) ) * 100)
        else:
            percent = 0

        # TC # English return something like:
        # Total ancestors in generations 2 to 3 is 4. (66.67%) 
        text = _("Total ancestors in generations %(second_generation)d to "
                 "%(last_generation)d is %(count)d. %(percent)s") % {
                 'second_generation' : 2,
                 'last_generation'   : gen,
                 'count'             : len(all_people),
                 'percent'           : percent}
                
        self.doc.start_paragraph('NOA-Normal')
        self.doc.write_text(text)
        self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# NumberOfAncestorsOptions
#
#------------------------------------------------------------------------
class NumberOfAncestorsOptions(MenuReportOptions):
    """
    Defines options for the NumberOfAncestorsReport.
    """
    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """
        Add options to the menu for the kinship report.
        """
        category_name = _("Report Options")
        
        pid = PersonOption(_("Center Person"))
        pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", pid)    

    def make_default_style(self, default_style):
        """Make the default output style for the Number of Ancestors Report."""
        font = FontStyle()
        font.set_size(16)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_header_level(1)
        para.set_bottom_border(1)
        para.set_bottom_margin(ReportUtils.pt2cm(8))
        para.set_font(font)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the title of the page."))
        default_style.add_paragraph_style("NOA-Title", para)
        
        font = FontStyle()
        font.set_size(12)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("NOA-Normal", para)

#-------------------------------------------------------------------------
#
# register_report
#
#-------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name = 'number_of_ancestors_report',
    category = CATEGORY_TEXT,
    report_class = NumberOfAncestorsReport,
    options_class = NumberOfAncestorsOptions,
    modes = PluginManager.REPORT_MODE_GUI | \
            PluginManager.REPORT_MODE_BKI | \
            PluginManager.REPORT_MODE_CLI,
    translated_name = _("Number of Ancestors Report"),
    status = _("Stable"),
    description = _("Counts number of ancestors of selected person"),
    author_name = "Brian G. Matherly",
    author_email = "brian@gramps-project.org"
    )
