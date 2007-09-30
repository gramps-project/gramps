#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Brian G. Matherly
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
# $Id:  $

"""
Generate an hourglass graph using the GraphViz generator.
"""

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, MenuOptions, NumberOption, \
     CATEGORY_GRAPHVIZ, MODE_GUI, MODE_CLI
from BasicUtils import name_displayer
import DateHandler

#------------------------------------------------------------------------
#
# AncestorChart
#
#------------------------------------------------------------------------
class HourGlassReport(Report):

    def __init__(self,database,person,options_class):
        """
        Creates HourGlass object that produces the report.
        """
        Report.__init__(self,database,person,options_class)
        self.person = person
        self.db = database
        self.max_descend = options_class.handler.options_dict['maxdescend']
        self.max_ascend  = options_class.handler.options_dict['maxascend']

    def write_report(self):
        self.add_person(self.person)
        self.traverse_up(self.person,1)
        self.traverse_down(self.person,1)
        
    def traverse_down(self,person,gen):
        """
        Resursively find the descendants of the given person.
        """
        if gen > self.max_descend:
            return
        for family_handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            self.add_family(family)
            self.doc.add_link( person.get_gramps_id(), family.get_gramps_id() )
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.get_reference_handle()
                child = self.db.get_person_from_handle(child_handle)
                self.add_person(child)
                self.doc.add_link(family.get_gramps_id() ,child.get_gramps_id())
                self.traverse_down(child,gen+1)
                
    def traverse_up(self,person,gen):
        """
        Resursively find the ancestors of the given person.
        """
        if gen > self.max_ascend:
            return
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.db.get_family_from_handle(family_handle)
            family_id = family.get_gramps_id()
            self.add_family(family)
            self.doc.add_link( family_id, person.get_gramps_id() )
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.db.get_person_from_handle(father_handle)
                self.add_person(father)
                self.doc.add_link( father.get_gramps_id(), family_id )
                self.traverse_up(father,gen+1)
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.db.get_person_from_handle( mother_handle )
                self.add_person( mother )
                self.doc.add_link( mother.get_gramps_id(), family_id )
                self.traverse_up( mother, gen+1 )

    def add_person(self,person):
        """
        Add a person to the Graph. The node id will be the person's gramps id.
        """
        p_id = person.get_gramps_id()
        name = name_displayer.display_formal(person)
        
        birth_evt = ReportUtils.get_birth_or_fallback(self.db,person)
        if birth_evt:
            birth = DateHandler.get_date(birth_evt)
        else:
            birth = ""
        
        death_evt = ReportUtils.get_death_or_fallback(self.db,person)
        if death_evt:
            death = DateHandler.get_date(death_evt)
        else:
            death = ""

        label = "%s \\n(%s - %s)" % (name,birth,death)
            
        gender = person.get_gender()
        if gender == person.MALE:
            color = 'lightblue'
        elif gender == person.FEMALE:
            color = 'lightpink'
        else:
            color = 'lightgray'
            
        self.doc.add_node(p_id,label,"box",color)
        
    def add_family(self,family):
        """
        Add a family to the Graph. The node id will be the family's gramps id.
        """
        family_id = family.get_gramps_id()
        label = ""
        marriage = ReportUtils.find_marriage(self.db,family)
        if marriage:
            label = DateHandler.get_date(marriage)
        self.doc.add_node(family_id,label,"ellipse","lightyellow")

#------------------------------------------------------------------------
#
# HourGlassOptions
#
#------------------------------------------------------------------------
class HourGlassOptions(MenuOptions):
    """
    Defines options for the HourGlass report.
    """
    def __init__(self,name,person_id=None):
        MenuOptions.__init__(self,name,person_id)
        
    def add_menu_options(self,menu):
        category_name = _("Report Options")
        
        max_gen = NumberOption(_('Max Descendant Generations'),10,1,15)
        max_gen.set_help(_("The number of generations of descendants to " \
                           "include in the report"))
        menu.add_option(category_name,"maxdescend",max_gen)
        
        max_gen = NumberOption(_('Max Ancestor Generations'),10,1,15)
        max_gen.set_help(_("The number of generations of ancestors to " \
                           "include in the report"))
        menu.add_option(category_name,"maxascend",max_gen)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name            = 'hourglass_graph',
    category        = CATEGORY_GRAPHVIZ,
    report_class    = HourGlassReport,
    options_class   = HourGlassOptions,
    modes           = MODE_GUI | MODE_CLI,
    translated_name = _("Hourglass Graph"),
    status          = _("Stable"),
    author_name     = "Brian G. Matherly",
    author_email    = "brian@gramps-project.org",
    description     = _("Produces an hourglass graph")
    )
