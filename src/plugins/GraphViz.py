#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

"Generate files/Relationship graph"

import os
import intl

_ = intl.gettext

import libglade
from Report import *

ind_list = []

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def ancestor_filter(database,person,list,generations):

    if person == None:
        return
    if person not in list:
        list.append(person)
    if generations <= 1:
        return
    
    family = person.getMainFamily()
    if family != None:
        ancestor_filter(database,family.getFather(),list,generations-1)
        ancestor_filter(database,family.getMother(),list,generations-1)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def descendant_filter(database,person,list,generations):

    if person == None:
        return
    if person not in list:
        list.append(person)
    if generations <= 1:
        return
    
    for family in person.getFamilyList():
        for child in family.getChildList():
            descendant_filter(database,child,list,generations-1)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def an_des_filter(database,person,list,generations):

    descendant_filter(database,person,list,generations)
    ancestor_filter(database,person,list,generations)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def entire_db_filter(database,person,list,generations):

    for entry in database.getPersonMap().values():
        list.append(entry)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------

filter_map = {
    _("Ancestors") : ancestor_filter,
    _("Descendants") : descendant_filter,
    _("Ancestors and Descendants") : an_des_filter,
    _("Entire Database") : entire_db_filter
    }
    
_scaled = 0
_single = 1
_multiple = 2

pagecount_map = {
    _("Single (scaled)") : _scaled,
    _("Single") : _single,
    _("Multiple") : _multiple,
    }
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class GraphVizDialog(ReportDialog):
    def __init__(self,database,person):
        ReportDialog.__init__(self,database,person)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return _("Gramps - Generate Relationship Graphs")

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Graphviz File")

    def get_print_pagecount_map(self):
        """Set up the list of possible page counts."""
        return (pagecount_map, _("Single (scaled)"))

    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (10, 0)

    def get_report_filter_strings(self):
        """Set up the list of possible content filters."""
        return filter_map.keys()

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self):
        """Build a one item menu of document types that are
        appropriate for this report."""
        map = {"Graphviz (dot)" : None}
        myMenu = utils.build_string_optmenu(map, None)
        self.format_menu.set_menu(myMenu)

    def make_document(self):
        """Do Nothing.  This document will be created in the
        make_report routine."""
        pass
    
    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window
    #
    #------------------------------------------------------------------------
    def setup_style_frame(self):
        """The style frame is not used in this dialog."""
        pass

    #------------------------------------------------------------------------
    #
    # Functions related to retrieving data from the dialog window
    #
    #------------------------------------------------------------------------
    def parse_style_frame(self):
        """The style frame is not used in this dialog."""
        pass

    #------------------------------------------------------------------------
    #
    # Functions related to creating the actual report document.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the object that will produce the GraphViz file."""
        width = self.paper.get_width_inches()
        height = self.paper.get_height_inches()

        file = open(self.target_path,"w")

        filter = filter_map[self.filter]
        ind_list = []

        filter(self.db,self.person,ind_list,self.max_gen)

        file.write("digraph g {\n")
        file.write("bgcolor=white;\n")
        file.write("rankdir=LR;\n")
        file.write("center=1;\n")

        if self.pagecount == _scaled:
            file.write("size=\"%3.1fin,%3.1fin\";\n" % (width-0.5,height-0.5))
            file.write("ratio=compress;\n")
        else:
            file.write("ratio=auto;\n")
        
        if self.pagecount == _multiple:
            file.write("page=\"%3.1f,%3.1f\";\n" % (width,height))
        
        if self.orien == PAPER_PORTRAIT:
            file.write("orientation=portrait;\n")
        else:
            file.write("orientation=landscape;\n")
        
        if len(ind_list) > 1:
            dump_index(ind_list,file)
            dump_person(ind_list,file)

        file.write("}\n")
        file.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    GraphVizDialog(database,person)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def dump_person(person_list,file):
    for person in person_list:
        family = person.getMainFamily()
        if family == None:
            continue
        father = family.getFather()
        if father and father in person_list:
            file.write('p%s -> p%s;\n' % (person.getId(), father.getId()))
        mother = family.getMother()
        if mother and mother in person_list:
            file.write('p%s -> p%s;\n' % (person.getId(), mother.getId()))


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def dump_index(person_list,file):

    for person in person_list:
        name = person.getPrimaryName().getName()
        id = person.getId()
        file.write('p%s [shape=box, ' % id)
        file.write('fontname="Arial", label="%s"];\n' % name)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return _("Generates relationship graphs, currently only in GraphViz format.") + \
           " " + \
           _("GraphViz (dot) can transform the graph into postscript, jpeg, png, vrml, svg, and many other formats.") + \
           " " + \
           _("For more information or to get a copy of GraphViz, goto http://www.graphviz.org")

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Relationship graph"),
    category=_("Graphical Reports"),
    description=get_description()
    )

