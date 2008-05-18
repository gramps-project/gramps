#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008 Brian G. Matherly
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

"""
Generate an hourglass graph using the GraphViz generator.
/Reports/GraphViz/Hourglass Graph
"""
#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import PluginManager, NumberOption, PersonOption, \
     EnumeratedListOption
from ReportBase import Report, ReportUtils, MenuReportOptions, \
    MODE_GUI, MODE_CLI, CATEGORY_GRAPHVIZ
from BasicUtils import name_displayer
import DateHandler

#------------------------------------------------------------------------
#
# Constant options items
#
#------------------------------------------------------------------------
_COLORS = [ { 'name' : _("B&W outline"),     'value' : "outline" },
            { 'name' : _("Colored outline"), 'value' : "colored" },
            { 'name' : _("Color fill"),      'value' : "filled"  }]


#------------------------------------------------------------------------
#
# HourGlassReport
#
#------------------------------------------------------------------------
class HourGlassReport(Report):
    """
    An hourglass report displays ancestors and descendants of a center person.
    """
    def __init__(self, database, options_class):
        """
        Create HourGlass object that produces the report.
        """
        Report.__init__(self, database, options_class)
        
        colored = {
            'male': 'dodgerblue4',
            'female': 'deeppink',
            'unknown': 'black',
            'family': 'darkgreen'
        }
        filled = {
            'male': 'lightblue',
            'female': 'lightpink',
            'unknown': 'lightgray',
            'family': 'lightyellow'
        }

        self.__db = database
        
        menu = options_class.menu
        self.max_descend = menu.get_option_by_name('maxdescend').get_value()
        self.max_ascend  = menu.get_option_by_name('maxascend').get_value()
        pid = menu.get_option_by_name('pid').get_value()
        self.center_person = database.get_person_from_gramps_id(pid)
        self.colorize = menu.get_option_by_name('color').get_value()
        if self.colorize == 'colored':
            self.colors = colored
        elif self.colorize == 'filled':
            self.colors = filled

    def write_report(self):
        """
        Generate the report.
        """
        self.add_person(self.center_person)
        self.traverse_up(self.center_person, 1)
        self.traverse_down(self.center_person, 1)
        
    def traverse_down(self, person, gen):
        """
        Resursively find the descendants of the given person.
        """
        if gen > self.max_descend:
            return
        for family_handle in person.get_family_handle_list():
            family = self.__db.get_family_from_handle(family_handle)
            self.add_family(family)
            self.doc.add_link( person.get_gramps_id(), family.get_gramps_id(), head='normal', tail='none' )
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.get_reference_handle()
                child = self.__db.get_person_from_handle(child_handle)
                self.add_person(child)
                self.doc.add_link(family.get_gramps_id(), child.get_gramps_id(), head='normal', tail='none' )
                self.traverse_down(child, gen+1)
                
    def traverse_up(self, person, gen):
        """
        Resursively find the ancestors of the given person.
        """
        if gen > self.max_ascend:
            return
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.__db.get_family_from_handle(family_handle)
            family_id = family.get_gramps_id()
            self.add_family(family)
            self.doc.add_link( family_id, person.get_gramps_id(), head='none', tail='normal' )
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.__db.get_person_from_handle(father_handle)
                self.add_person(father)
                self.doc.add_link( father.get_gramps_id(), family_id, head='none', tail='normal' )
                self.traverse_up(father, gen+1)
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.__db.get_person_from_handle( mother_handle )
                self.add_person( mother )
                self.doc.add_link( mother.get_gramps_id(), family_id, head='none', tail='normal' )
                self.traverse_up( mother, gen+1 )

    def add_person(self, person):
        """
        Add a person to the Graph. The node id will be the person's gramps id.
        """
        p_id = person.get_gramps_id()
        name = name_displayer.display_formal(person)
        
        birth_evt = ReportUtils.get_birth_or_fallback(self.__db, person)
        if birth_evt:
            birth = DateHandler.get_date(birth_evt)
        else:
            birth = ""
        
        death_evt = ReportUtils.get_death_or_fallback(self.__db, person)
        if death_evt:
            death = DateHandler.get_date(death_evt)
        else:
            death = ""

        label = "%s \\n(%s - %s)" % (name, birth, death)
            
        (shape, style, color, fill) = self.get_gender_style(person)
        self.doc.add_node(p_id, label, shape, color, style, fill)
        
    def add_family(self, family):
        """
        Add a family to the Graph. The node id will be the family's gramps id.
        """
        family_id = family.get_gramps_id()
        label = ""
        marriage = ReportUtils.find_marriage(self.__db, family)
        if marriage:
            label = DateHandler.get_date(marriage)
        color = ""
        fill = ""
        style = "solid"
        if self.colorize == 'colored':
            color = self.colors['family']
        elif self.colorize == 'filled':
            fill = self.colors['family']
            style = "filled"
        self.doc.add_node(family_id, label, "ellipse", color, style, fill)

    def get_gender_style(self, person):
        "return gender specific person style"
        gender = person.get_gender()
        shape = "box"
        style = ""
        color = ""
        fill = ""
        if gender == person.MALE:
            shape = "box"
            style = "solid"
        elif gender == person.FEMALE:
            shape = "box"
            style = "rounded"
        else:
            shape = "hexagon"
            style = "solid"
        if self.colorize == 'colored':
            if gender == person.MALE:
                color = self.colors['male']
            elif gender == person.FEMALE:
                color = self.colors['female']
            else:
                color = self.colors['unknown']
        elif self.colorize == 'filled':
            if style != "":
                style += ",filled"
            else:
                style = "filled"
            if gender == person.MALE:
                fill = self.colors['male']
            elif gender == person.FEMALE:
                fill = self.colors['female']
            else:
                fill = self.colors['unknown']
        return(shape, style, color, fill)


#------------------------------------------------------------------------
#
# HourGlassOptions
#
#------------------------------------------------------------------------
class HourGlassOptions(MenuReportOptions):
    """
    Defines options for the HourGlass report.
    """
    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """
        Create all the menu options for this report.
        """
        category_name = _("Options")
        
        pid = PersonOption(_("Center Person"))
        pid.set_help(_("The Center person for the graph"))
        menu.add_option(category_name, "pid", pid)
        
        max_gen = NumberOption(_('Max Descendant Generations'), 10, 1, 15)
        max_gen.set_help(_("The number of generations of descendants to " \
                           "include in the graph"))
        menu.add_option(category_name, "maxdescend", max_gen)
        
        max_gen = NumberOption(_('Max Ancestor Generations'), 10, 1, 15)
        max_gen.set_help(_("The number of generations of ancestors to " \
                           "include in the graph"))
        menu.add_option(category_name, "maxascend", max_gen)

        ################################
        category_name = _("Graph Style")
        ################################

        color = EnumeratedListOption(_("Graph coloring"), "filled")
        for i in range( 0, len(_COLORS) ):
            color.add_item(_COLORS[i]["value"], _COLORS[i]["name"])
        color.set_help(_("Males will be shown with blue, females "
                         "with red.  If the sex of an individual "
                         "is unknown it will be shown with gray."))
        menu.add_option(category_name, "color", color)
        

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name            = 'hourglass_graph',
    category        = CATEGORY_GRAPHVIZ,
    report_class    = HourGlassReport,
    options_class   = HourGlassOptions,
    modes           = MODE_GUI | MODE_CLI,
    translated_name = _("Hourglass Graph"),
    status          = _("Stable"),
    author_name     = "Brian G. Matherly",
    author_email    = "brian@gramps-project.org",
    description     = _("Produces an hourglass graph using Graphviz")
    )
