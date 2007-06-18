#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"Text Reports/Ahnentafel Report"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import gtk
import math
from gettext import gettext as _

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_TEXT, MODE_GUI, MODE_BKI, MODE_CLI
import BaseDoc
import NameDisplay

from RelLib import ChildRefType

#------------------------------------------------------------------------
#
# log2val
#
#------------------------------------------------------------------------
def log2(val):
    return int(math.log10(val)/math.log10(2))

class AncestorReport(Report):

    def __init__(self, database, person, options_class):
        """
        Creates the AncestorReport object that produces the Ahnentafel report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen       - Maximum number of generations to include.
        pagebbg   - Whether to include page breaks between generations.

        """

        Report.__init__(self,database,person,options_class)

        self.map = {}
        (self.max_generations,self.pgbrk) \
                        = options_class.get_report_generations()
        self.opt_namebrk = options_class.handler.options_dict['namebrk']

    def apply_filter(self,person_handle,index,generation=1):
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

        # retreive the Person instance from the database from the
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

                if not father_handle and ref[0].get_father_relation() == ChildRefType.BIRTH:
                    father_handle = family.get_father_handle()
                if not mother_handle and ref[0].get_mother_relation() == ChildRefType.BIRTH:
                    mother_handle = family.get_mother_handle()

        # Recursively call the function. It is okay if the handle is None, since 
        # routine handles a handle of None

        self.apply_filter(father_handle, index*2, generation+1)
        self.apply_filter(mother_handle, (index*2)+1, generation+1)

    def write_report(self):
        """
        The routine the actually creates the report. At this point, the document is 
        opened and ready for writing.
        """

        # Call apply_filter to build the self.map array of people in the database that
        # match the ancestry.

        self.apply_filter(self.start_person.get_handle(),1)

        # Write the title line. Set in INDEX marker so that this section will be 
        # identified as a major category if this is included in a Book report.

        name = NameDisplay.displayer.display_formal(self.start_person)
        title = _("Ahnentafel Report for %s") % name
        mark = BaseDoc.IndexMark(title, BaseDoc.INDEX_TYPE_TOC,1 )        
        self.doc.start_paragraph("AHN-Title")
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
    
        # get the entries out of the map, and sort them.

        keys = self.map.keys()
        keys.sort()
        generation = 0

        for key in keys :

            # check the index number to see if we need to start a new generation
            if generation == log2(key):

                # generate a page break if requested
                if self.pgbrk and generation > 0:
                    self.doc.page_break()
                generation += 1

                # Create the Generation title, set an index marker
                mark =  BaseDoc.IndexMark(title,BaseDoc.INDEX_TYPE_TOC,2)  
                self.doc.start_paragraph("AHN-Generation")
                self.doc.write_text(_("Generation %d") % generation,mark)
                self.doc.end_paragraph()

            # Build the entry

            self.doc.start_paragraph("AHN-Entry","%d." % key)
            person = self.database.get_person_from_handle(self.map[key])
            name = NameDisplay.displayer.display(person)
            mark = ReportUtils.get_person_mark(self.database, person)
        
            # write the name in bold
            self.doc.start_bold()
            self.doc.write_text(name.strip(), mark)
            self.doc.end_bold()

            # terminate with a period if it is not already terminated. This can happen
            # if the person's name ends with something 'Jr.'
            if name[-1:] == '.':
                self.doc.write_text(" ")
            else:
                self.doc.write_text(". ")

            # Add a line break if requested (not implemented yet)
            if self.opt_namebrk:
                self.doc.write_text('\n')

            # Write the birth, death, and buried strings by calling the standard
            # functions in ReportUtils

            primary_name = person.get_primary_name()
            first = primary_name.get_first_name()

            self.doc.write_text(ReportUtils.born_str(self.database,person,first))
            self.doc.write_text(ReportUtils.died_str(self.database,person,0))
            self.doc.write_text(ReportUtils.buried_str(self.database,person,0))
                        
            self.doc.end_paragraph()

class AncestorOptions(ReportOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'gen'       : 10,
            'pagebbg'   : 0,
        }

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'namebrk'    : 0,
        }
        self.options_help = {
            'namebrk'    : ("=0/1","Indicates if a line break should follow the name.",
                            ["No line break", "Insert line break"],
                            False),
        }

    def make_default_style(self,default_style):
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
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)       
        para.set_description(_('The style used for the title of the page.'))
        default_style.add_style("AHN-Title",para)
    
        #
        # AHN-Generation
        #
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set_top_margin(0.125)
        para.set_bottom_margin(0.125)        
        para.set_description(_('The style used for the generation header.'))
        default_style.add_style("AHN-Generation",para)
    
        #
        # AHN-Entry
        #
        para = BaseDoc.ParagraphStyle()
        para.set(first_indent=-1.0,lmargin=1.0)
        para.set_top_margin(0.125)
        para.set_bottom_margin(0.125)        
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_style("AHN-Entry",para)

    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add a check box to 
        the dialog that for the LineBreak option.
        """
        self.cb_break = gtk.CheckButton (_("Add linebreak after each name"))
        self.cb_break.set_active (self.options_dict['namebrk'])
        dialog.add_option ('', self.cb_break)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added. Set the value in the
        options dictionary.
        """
        self.options_dict['namebrk'] = int(self.cb_break.get_active ())

#------------------------------------------------------------------------
#
# Register the plugin
#
#------------------------------------------------------------------------
register_report(
    name = 'ancestor_report',
    category = CATEGORY_TEXT,
    report_class = AncestorReport,
    options_class = AncestorOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Ahnentafel Report"),
    status=(_("Stable")),
    description= _("Produces a textual ancestral report"),
    author_name="Donald N. Allingham",
    author_email="don@gramps-project.org"
    )
