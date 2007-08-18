#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
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

"Text Reports/Kinship Report"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
from string import capitalize

#------------------------------------------------------------------------
#
# GTK modules
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report, relationship_class
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_TEXT, MODE_GUI, MODE_BKI, MODE_CLI
import BaseDoc
from BasicUtils import name_displayer
import DateHandler

#------------------------------------------------------------------------
#
# KinshipReport
#
#------------------------------------------------------------------------
class KinshipReport(Report):

    def __init__(self, database, person, options_class):
        """
        Creates the KinshipReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        maxdescend    - Maximum generations of descendants to include.
        maxascend     - Maximum generations of ancestors to include.
        incspouses    - Whether to include spouses.
        inccousins    - Whether to include cousins.
        incaunts      - Whether to include aunts/uncles/nefews/nieces.
        """
        Report.__init__(self,database,person,options_class)

        self.max_descend = options_class.handler.options_dict['maxdescend']
        self.max_ascend  = options_class.handler.options_dict['maxascend']
        self.incSpouses  = options_class.handler.options_dict['incspouses']
        self.incCousins  = options_class.handler.options_dict['inccousins']
        self.incAunts   = options_class.handler.options_dict['incaunts']
        
        self.person = person
        self.db = database
        self.relCalc = relationship_class()
        self.kinship_map = {}
        self.spouse_map = {}

    def write_report(self):
        """
        The routine the actually creates the report. At this point, the document
        is opened and ready for writing.
        """
        pname = name_displayer.display(self.person)
        
        self.doc.start_paragraph("KIN-Title")
        title = _("Kinship Report for %s") % pname
        mark = BaseDoc.IndexMark(title,BaseDoc.INDEX_TYPE_TOC,1)
        self.doc.write_text(title,mark)
        self.doc.end_paragraph()

        if self.incSpouses:
            spouse_handles = self.get_spouse_handles(self.person.get_handle())
            if spouse_handles:
                self.write_people(_("Spouses"),spouse_handles)

        # Collect all descendants of the person
        self.traverse_down(self.person.get_handle(),0,1)
        
        # Collect all ancestors/aunts/uncles/nefews/cousins of the person
        self.traverse_up(self.person.get_handle(),1,0)
                
        # Write Ancestors
        for Ga in self.kinship_map.keys():
            for Gb in self.kinship_map[Ga]:
                # To understand these calculations, see: 
                # http://en.wikipedia.org/wiki/Cousin#Mathematical_definitions
                x = min (Ga,Gb)
                y = abs(Ga-Gb)
                # Skip unrequested people
                if x == 1 and y > 0 and not self.incAunts:
                    continue
                elif x > 1 and not self.incCousins:
                    continue
                
                title = self.relCalc.get_plural_relationship_string(Ga,Gb)
                self.write_people(title,self.kinship_map[Ga][Gb])
                
                if self.incSpouses and \
                   self.spouse_map.has_key(Ga) and \
                   self.spouse_map[Ga].has_key(Gb):
                    title = _("spouses of %s") % title
                    self.write_people(title,self.spouse_map[Ga][Gb])

    def traverse_down(self,person_handle,Ga,Gb,skip_handle=None):
        """
        Populate a map of arrays containing person handles for the descendants
        of the passed person. This function calls itself recursively until it
        reaches max_descend.
        
        Parameters:
        person_handle: the handle of the person to go to next
        Ga: The number of generations from the main person to the common 
           ancestor. This should be incremented when going up generations, and 
           left alone when going down generations.
        Gb: The number of generations from this person (person_handle) to the 
           common ancestor. This should be incremented when going down 
           generations and set back to zero when going up generations.
        skip_handle: an optional handle to skip when going down. This is useful
           to skip the descendant that brought you this generation in the first
           place.
        """
        for child_handle in self.get_children_handles(person_handle):
            if child_handle != skip_handle:
                self.add_kin(child_handle,Ga,Gb)
            
                if self.incSpouses:
                    for spouse_handle in self.get_spouse_handles(child_handle):
                        self.add_spouse(spouse_handle,Ga,Gb)
                    
                if Gb < self.max_descend:
                    self.traverse_down(child_handle,Ga,Gb+1)
                    
    def traverse_up(self,person_handle,Ga,Gb):
        """
        Populate a map of arrays containing person handles for the ancestors
        of the passed person. This function calls itself recursively until it
        reaches max_ascend.
        
        Parameters:
        person_handle: the handle of the person to go to next
        Ga: The number of generations from the main person to the common 
           ancestor. This should be incremented when going up generations, and 
           left alone when going down generations.
        Gb: The number of generations from this person (person_handle) to the 
           common ancestor. This should be incremented when going down 
           generations and set back to zero when going up generations.
        """
        parent_handles = self.get_parent_handles(person_handle)
        for parent_handle in parent_handles:
            self.add_kin(parent_handle,Ga,Gb)
            self.traverse_down(parent_handle,Ga,Gb+1,person_handle)
            if Ga < self.max_ascend:
                self.traverse_up(parent_handle,Ga+1,0)
                
    def add_kin(self,person_handle,Ga,Gb):
        """
        Add a person handle to the kin map.
        """
        if not self.kinship_map.has_key(Ga):
            self.kinship_map[Ga] = {}
        if not self.kinship_map[Ga].has_key(Gb):
            self.kinship_map[Ga][Gb] = []
        if person_handle not in self.kinship_map[Ga][Gb]:
            self.kinship_map[Ga][Gb].append(person_handle)
        
    def add_spouse(self,spouse_handle,Ga,Gb):
        """
        Add a person handle to the spouse map.
        """
        if not self.spouse_map.has_key(Ga):
            self.spouse_map[Ga] = {}
        if not self.spouse_map[Ga].has_key(Gb):
            self.spouse_map[Ga][Gb] = []
        if spouse_handle not in self.spouse_map[Ga][Gb]:
            self.spouse_map[Ga][Gb].append(spouse_handle)
                
    def get_parent_handles(self,person_handle):
        """
        Return an array of handles for all the parents of the 
        given person handle.
        """
        parent_handles = []
        person = self.db.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.db.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            if father_handle:
                parent_handles.append(father_handle)
            mother_handle = family.get_mother_handle()
            if mother_handle:
                parent_handles.append(mother_handle)
        return parent_handles
                
    def get_spouse_handles(self,person_handle):
        """
        Return an array of handles for all the spouses of the 
        given person handle.
        """
        spouses = []
        person = self.db.get_person_from_handle(person_handle)
        for family_handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            spouse_handle = None
            if mother_handle and father_handle == person_handle:
                spouse_handle = mother_handle
            elif father_handle and mother_handle == person_handle:
                spouse_handle = father_handle
            
            if spouse_handle and spouse_handle not in spouses:
                spouses.append(spouse_handle)
        return spouses
    
    def get_children_handles(self,person_handle):
        """
        Return an array of handles for all the children of the 
        given person handle.
        """
        children = []
        person = self.db.get_person_from_handle(person_handle)
        for family_handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            for child_ref in family.get_child_ref_list():
                children.append(child_ref.get_reference_handle())
        return children
    
    def get_sibling_handles(self,person_handle):
        """
        Return an array of handles for all the siblings of the 
        given person handle.
        """
        siblings = []
        person = self.db.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.db.get_family_from_handle(family_handle)
            for child_ref in family.get_child_ref_list():
                sibling_handle = child_ref.get_reference_handle()
                if sibling_handle != person_handle:
                    siblings.append(sibling_handle)
        return siblings
    
    def write_people(self,title,people_handles):
        """
        Write information about a group of people - including the title.
        """
        cap_title = capitalize(title)
        self.doc.start_paragraph("KIN-Subtitle")
        mark = BaseDoc.IndexMark(cap_title,BaseDoc.INDEX_TYPE_TOC,2)
        self.doc.write_text(cap_title,mark)
        self.doc.end_paragraph()
        for person_handle in people_handles:
            self.write_person(person_handle)

    def write_person(self,person_handle):
        """
        Write information about the given person.
        """
        person = self.database.get_person_from_handle(person_handle)

        name = name_displayer.display(person)
        mark = ReportUtils.get_person_mark(self.database, person)
        birth_date = ""
        birth_ref = person.get_birth_ref()
        if birth_ref:
            event = self.database.get_event_from_handle(birth_ref.ref)
            birth_date = DateHandler.get_date( event )
        
        death_date = ""
        death_ref = person.get_death_ref()
        if death_ref:
            event = self.database.get_event_from_handle(death_ref.ref)
            death_date = DateHandler.get_date( event )
        dates = _(" (%(birth_date)s - %(death_date)s)") % { 
                                            'birth_date' : birth_date,
                                            'death_date' : death_date }
        
        self.doc.start_paragraph('KIN-Normal')
        self.doc.write_text(name,mark)
        self.doc.write_text(dates)
        self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# KinshipOptions
#
#------------------------------------------------------------------------
class KinshipOptions(ReportOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)
        
    def set_new_options(self):
        self.options_dict = {
            'maxdescend'    : 2,
            'maxascend'     : 2,
            'incspouses'    : 1,
            'inccousins'    : 1,
            'incsiblings'   : 1,
            'incaunts' : 1,
        }
        self.options_help = {
            'maxdescend'   : ("=int","Max Descendants",
                           "The number of generations of descendants to " \
                           "include in the report",
                           True),
            'maxascend'    : ("=int","Max Ancestors",
                           "The number of generations of ancestors to " \
                           "include in the report",
                           True),
            'incspouses'   : ("=0/1","Whether to include spouses",
                           ["Do not include spouses","Include spouses"],
                           True),
            'inccousins'   : ("=0/1","Whether to include cousins",
                           ["Do not include cousins","Include cousins"],
                           True),
            'incaunts': ("=0/1","Whether to include aunts/uncles/nefews/nieces",
                           ["Do not include aunts","Include aunts"],
                           True),
        }
        
    def add_user_options(self,dialog):
        self.maxdescend = gtk.SpinButton(gtk.Adjustment(1,1,20,1))
        self.maxdescend.set_value(self.options_dict['maxdescend'])
        
        self.maxascend = gtk.SpinButton(gtk.Adjustment(1,1,20,1))
        self.maxascend.set_value(self.options_dict['maxascend'])
        
        self.incspouses = gtk.CheckButton(_("Include spouses"))
        self.incspouses.set_active(self.options_dict['incspouses'])
        
        self.inccousins = gtk.CheckButton(_("Include cousins"))
        self.inccousins.set_active(self.options_dict['inccousins'])
        
        self.incaunts = gtk.CheckButton(_("Include aunts/uncles/nefews/nieces"))
        self.incaunts.set_active(self.options_dict['incaunts'])

        dialog.add_option (_('Max Descendant Generations'), self.maxdescend)
        dialog.add_option (_('Max Ancestor Generations'), self.maxascend)
        dialog.add_option ('', self.incspouses)
        dialog.add_option ('', self.inccousins)
        dialog.add_option ('', self.incaunts)

    def parse_user_options(self,dialog):
        self.options_dict['maxdescend']  = self.maxdescend.get_value_as_int()
        self.options_dict['maxascend']   = self.maxascend.get_value_as_int()
        self.options_dict['incspouses']  = int(self.incspouses.get_active ())
        self.options_dict['inccousins']  = int(self.inccousins.get_active())
        self.options_dict['incaunts']    = int(self.incaunts.get_active())

    def make_default_style(self,default_style):
        """Make the default output style for the Kinship Report."""
        f = BaseDoc.FontStyle()
        f.set_size(16)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        f.set_bold(1)
        p = BaseDoc.ParagraphStyle()
        p.set_header_level(1)
        p.set_bottom_border(1)
        p.set_bottom_margin(ReportUtils.pt2cm(8))
        p.set_font(f)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_("The style used for the title of the page."))
        default_style.add_paragraph_style("KIN-Title",p)
        
        font = BaseDoc.FontStyle()
        font.set_size(12)
        font.set_bold(True)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(6))
        p.set_description(_('The basic style used for sub-headings.'))
        default_style.add_paragraph_style("KIN-Subtitle",p)
        
        font = BaseDoc.FontStyle()
        font.set_size(10)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_left_margin(0.5)
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("KIN-Normal",p)

#------------------------------------------------------------------------
#
# Register the plugin
#
#------------------------------------------------------------------------
register_report(
    name = 'kinship_report',
    category = CATEGORY_TEXT,
    report_class = KinshipReport,
    options_class = KinshipOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Kinship Report"),
    status=(_("Stable")),
    description= _("Produces a textual report of kinship for a given person"),
    author_name="Brian G. Matherly",
    author_email="brian@gramps-project.org"
    )
