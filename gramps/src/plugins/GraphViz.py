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

from RelLib import *
import os
import re
import sort
import string
import utils
import intl

_ = intl.gettext

from gtk import *
from gnome.ui import *
from libglade import *

active_person = None
db = None
topDialog = None
glade_file = None
ind_list = []

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def ancestor_filter(database,person,list):

    if person == None:
        return
    if person not in list:
        list.append(person)
    family = person.getMainFamily()
    if family != None:
        ancestor_filter(database,family.getFather(),list)
        ancestor_filter(database,family.getMother(),list)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def descendant_filter(database,person,list):

    if person == None:
        return
    if person not in list:
        list.append(person)
        
    for family in person.getFamilyList():
        for child in family.getChildList():
            descendant_filter(database,child,list)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def an_des_filter(database,person,list):

    descendant_filter(database,person,list)
    ancestor_filter(database,person,list)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def entire_db_filter(database,person,list):

    for entry in database.getPersonMap().values():
        list.append(entry)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------

filter_map = {
    "Ancestors" : ancestor_filter,
    "Descendants" : descendant_filter,
    "Ancestors and Descendants" : an_des_filter,
    "Entire Database" : entire_db_filter
    }
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    global active_person
    global topDialog
    global glade_file
    global db
    
    active_person = person
    db = database

    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "graphviz.glade"
    dic = {
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_ok_clicked" : on_ok_clicked,
        }

    topDialog = GladeXML(glade_file,"top")
    topDialog.signal_autoconnect(dic)
    
    top = topDialog.get_widget("top")
    topDialog.get_widget("targetDirectory").set_default_path(os.getcwd())
    filterName = topDialog.get_widget("filterName")
    popdown_strings = filter_map.keys()
    popdown_strings.sort()
    filterName.set_popdown_strings(popdown_strings)

    name = person.getPrimaryName().getName()
    topDialog.get_widget("personName").set_text(name)

    top.show()
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_ok_clicked(obj):
    global active_person
    global filter_map
    global db
    global glade_file
    global ind_list

    filterName = topDialog.get_widget("filter").get_text()
    file_name = topDialog.get_widget("filename").get_text()
    if file_name == "":
        return

    paper = topDialog.get_widget("paper")
    multi = topDialog.get_widget("multi").get_active()
    scaled = topDialog.get_widget("scaled").get_active()
    portrait = topDialog.get_widget("portrait").get_active()
    
    width = paper.get_width()/72.0
    height = paper.get_height()/72.0

    file = open(file_name,"w")

    filter = filter_map[filterName]
    ind_list = []

    filter(db,active_person,ind_list)

    file.write("digraph g {\n")
    file.write("bgcolor=white;\n")
    file.write("rankdir=LR;\n")
    file.write("center=1;\n")

    if scaled == 1:
        file.write("size=\"%3.1fin,%3.1fin\";\n" % (width-0.5,height-0.5))
        file.write("ratio=compress;\n")
    else:
        file.write("ratio=auto;\n")
        
    if multi == 1:
        file.write("page=\"%3.1f,%3.1f\";\n" % (width,height))
        
    if portrait == 1:
        file.write("orientation=portrait;\n")
    else:
        file.write("orientation=landscape;\n")
        
    if len(ind_list) > 1:
        dump_index(ind_list,file)
        dump_person(ind_list,file)

    file.write("}\n")
    file.close()
    utils.destroy_passed_object(obj)
    
#########################################################################
#
# Write a web page for a specific person represented by the key
#
#########################################################################

def dump_person(person_list,file):
    for person in person_list:
        family = person.getMainFamily()
        if family == None:
            continue
        father = family.getFather()
        if father and father in person_list:
            file.write('p' + str(person.getId()) + ' -> p')
            file.write(str(father.getId()) + ';\n')
        mother = family.getMother()
        if mother and mother in person_list:
            file.write('p' + str(person.getId()) + ' -> p')
            file.write(str(mother.getId()) + ';\n')

#########################################################################
#
# Write a web page for a specific person represented by the key
#
#########################################################################

def dump_index(person_list,file):

    for person in person_list:
        name = person.getPrimaryName().getName()
        id = person.getId()
#        file.write('p' + str(id) + ' [shape=box, fontsize=11, ')
        file.write('p' + str(id) + ' [shape=box, ')
        file.write('fontname="Arial", label="' + name + '"];\n')

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return _("Generates relationship graphs, currently only in GraphVis format.") + \
           " " + \
           _("GraphViz (dot) will transform the graph into postscript, jpeg, png, vrml, svg, and many other formats.") + \
           " " + \
           _("For more information or to get a copy of GraphViz, goto http://www.graphviz.org")

def get_name():
    return _("Generate files/Relationship graph")
