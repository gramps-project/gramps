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
import string

import intl
import Utils

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
    
    family = person.getMainParents()
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
        return "%s - %s - GRAMPS" % (_("Relationship Graph"),_("Graphical Reports"))

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

    def add_user_options(self):
    
        self.arrowhead_optionmenu = GtkOptionMenu()
        menu = GtkMenu()
        
        menuitem = GtkMenuItem(_("Descendants <- Ancestors"))
        menuitem.set_data('i', '[arrowhead=none, arrowtail=normal]')
        menuitem.show()
        menu.append(menuitem)
        
        menuitem = GtkMenuItem(_("Descendants -> Ancestors"))
        menuitem.set_data('i', '[arrowhead=normal, arrowtail=none]')
        menuitem.show()
        menu.append(menuitem)

        menuitem = GtkMenuItem(_("Descendants <-> Ancestors"))
        menuitem.set_data('i', '[arrowhead=normal, arrowtail=normal]')
        menuitem.show()
        menu.append(menuitem)
        
        menu.set_active(0)
        self.arrowhead_optionmenu.set_menu(menu)
        tip = GtkTooltips()
        tip.set_tip(self.arrowhead_optionmenu, _("Choose the direction that the arrows point."))
        self.add_frame_option(_("GraphViz Options"), _("Arrowhead Options"), self.arrowhead_optionmenu)

        self.includedates_checkbutton = GtkCheckButton(_("Include Birth and Death Dates"))
        self.includedates_checkbutton.set_active(1)
        tip = GtkTooltips()
        tip.set_tip(self.includedates_checkbutton, _("Include the years that the individual was born and/or died in the graph node labels."))
        self.add_frame_option(_("GraphViz Options"), ' ', self.includedates_checkbutton)

        self.includeurl_checkbutton = GtkCheckButton(_("Include URLs"))
        self.includeurl_checkbutton.set_active(1)
        tip = GtkTooltips()
        tip.set_tip(self.includeurl_checkbutton, _("Include a URL in each graph node so that PDF and imagemap files can be generated that contain active links to the files generated by the 'Generate Web Site' report."))
        self.add_frame_option(_("GraphViz Options"), ' ', self.includeurl_checkbutton)

        self.tb_margin_adjustment = GtkAdjustment(value=0.5, lower=0.25, upper=100.0, step_incr=0.25)
        self.lr_margin_adjustment = GtkAdjustment(value=0.5, lower=0.25, upper=100.0, step_incr=0.25)

        self.tb_margin_spinbutton = GtkSpinButton(adj=self.tb_margin_adjustment, digits=2)
        self.lr_margin_spinbutton = GtkSpinButton(adj=self.lr_margin_adjustment, digits=2)

        self.add_frame_option(_("GraphViz Options"), _("Top & Bottom Margins"), self.tb_margin_spinbutton)
        self.add_frame_option(_("GraphViz Options"), _("Left & Right Margins"), self.lr_margin_spinbutton)
        
    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self):
        """Build a one item menu of document types that are
        appropriate for this report."""
        map = {"Graphviz (dot)" : None}
        myMenu = Utils.build_string_optmenu(map, None)
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

    def parse_other_frames(self):
        self.arrowhead_option = self.arrowhead_optionmenu.get_menu().get_active().get_data('i')
        self.includedates = self.includedates_checkbutton.get_active()
        self.includeurl = self.includeurl_checkbutton.get_active()
        self.tb_margin = self.tb_margin_spinbutton.get_value_as_float()
        self.lr_margin = self.lr_margin_spinbutton.get_value_as_float()
        
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
            file.write("ratio=compress;\n")
            file.write("size=\"%3.1f,%3.1f\";\n" % (width-(self.lr_margin * 2),
                                                    height-(self.tb_margin * 2)))
        else:
            file.write("ratio=auto;\n")
        
        file.write("page=\"%3.1f,%3.1f\";\n" % (width,height))
        
        if self.orien == PAPER_LANDSCAPE:
            file.write("rotate=90;\n")
        
        if len(ind_list) > 1:
            dump_index(ind_list,file,self.includedates,self.includeurl)
            dump_person(ind_list,file,self.arrowhead_option)

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
def dump_person(person_list,file,arrowhead_option):
    for person in person_list:
        pid = string.replace(person.getId(),'-','_')
        family = person.getMainParents()
        if family == None:
            continue
        father = family.getFather()
        if father and father in person_list:
            fid = string.replace(father.getId(),'-','_')
            file.write('p%s -> p%s %s;\n' % (pid, fid, arrowhead_option))
        mother = family.getMother()
        if mother and mother in person_list:
            mid = string.replace(mother.getId(),'-','_')
            file.write('p%s -> p%s %s;\n' % (pid, mid, arrowhead_option))

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def dump_index(person_list,file,includedates,includeurl):
    for person in person_list:
        label = person.getPrimaryName().getName()
        id = string.replace(person.getId(),'-','_')
        if includedates:
            if person.getBirth().getDateObj().getYearValid():
                birth = '%i' % person.getBirth().getDateObj().getYear()
            else:
                birth = ''
            if person.getDeath().getDateObj().getYearValid():
                death = '%i' % person.getDeath().getDateObj().getYear()
            else:
                death = ''
            label = label + '\\n(%s - %s)' % (birth, death)
        file.write('p%s [shape=box, ' % id)
        if includeurl:
            file.write('URL="%s.html", ' % id)
        file.write('fontname="Arial", label="%s"];\n' % label)

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
    _("Relationship Graph"),
    status=(_("Beta")),
    category=_("Graphical Reports"),
    description=get_description()
    )

