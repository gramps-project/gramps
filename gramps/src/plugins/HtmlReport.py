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

"Generate files/Individual web pages"

from RelLib import *
import const
import utils

import os
import re
import sort
import string
import time

from gtk import *
from gnome.ui import *
from libglade import *

titleRe = re.compile(r"<TITLE>")
active_person = None
db = None
topDialog = None
glade_file = None
ind_list = []
restrict = 1
restrict_photos = 0
no_photos = 0

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def individual_filter(database,person,list):
    list.append(person)

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

    if person == None or person in list:
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
def an_des_of_gparents_filter(database,person,list):

    my_list = []

    family = person.getMainFamily()
    if family == None:
        return

    mother = family.getMother()
    father = family.getFather()
    if mother:
        mfamily = mother.getMainFamily()
        if mfamily:
            if mfamily.getFather():
                my_list.append(mfamily.getFather())
            if mfamily.getMother():
                my_list.append(mfamily.getMother())
    if father:
        ffamily = father.getMainFamily()
        if ffamily:
            if ffamily.getFather():
                my_list.append(ffamily.getFather())
            if ffamily.getMother():
                my_list.append(ffamily.getMother())

    for person in my_list:
        descendant_filter(database,person,list)
        ancestor_filter(database,person,list)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------

filter_map = {
    "Individual" : individual_filter,
    "Ancestors" : ancestor_filter,
    "Descendants" : descendant_filter,
    "Ancestors and descendants" : an_des_filter,
    "Grandparent's ancestors and descendants" : an_des_of_gparents_filter,
    "Entire database" : entire_db_filter
    }
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def probably_alive(person):

    if person == None:
        return 1

    if restrict == 0:
        return 0
    
    death = person.getDeath()
    birth = person.getBirth()

    if death.getDate() != "":
        return 0
    if birth.getDate() != "":
        year = birth.getDateObj().get_start_date().getYear()
        time_struct = time.localtime(time.time())
        current_year = time_struct[0]
        if year != -1 and current_year - year > 110:
            return 0
    return 1

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
    glade_file = base + os.sep + "htmlreport.glade"
    dic = {
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_nophotos_toggled" : on_nophotos_toggled,
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
def on_nophotos_toggled(obj):
    if obj.get_active():
        topDialog.get_widget("restrict_photos").set_sensitive(0)
    else:
        topDialog.get_widget("restrict_photos").set_sensitive(1)

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
    global restrict_photos
    global restrict
    global no_photos

    start = re.compile(r"<!-- START -->")
    stop = re.compile(r"<!-- STOP -->")
    top = []
    bottom = []
    
    filterName = topDialog.get_widget("filter").get_text()
    directoryName = topDialog.get_widget("targetDirectory").get_full_path(0)
    templateName = topDialog.get_widget("htmlTemplate").get_full_path(0)
    prefix = topDialog.get_widget("prefix").get_text()

    restrict = topDialog.get_widget("restrict").get_active()
    restrict_photos = topDialog.get_widget("restrict_photos").get_active()
    no_photos = topDialog.get_widget("nophotos").get_active()

    if directoryName == None:
        directoryName = os.getcwd()
    elif not os.path.isdir(directoryName):
        parent_dir = os.path.dirname(directoryName)
        if not os.path.isdir(parent_dir):
            GnomeErrorDialog("Neither " + directoryName + " nor " + \
                             parent_dir + " are directories")
            return
        else:
            try:
                print "trying to make",directoryName
                os.mkdir(directoryName)
            except IOError, value:
                GnomeErrorDialog("Could not create the directory " + directoryName + "\n" + \
                         value[1])
                return
            except:
                GnomeErrorDialog("Could not create the directory " + directoryName)
                return

    if templateName == None:
        templateName = const.dataDir + os.sep + "family.html"

    try:
        templateFile = open(templateName,"r")
    except IOError, value:
        GnomeErrorDialog("Could not open the template file (" + templateName + ")\n" + \
                         value[1])
        return
    except:
        GnomeErrorDialog("Could not open the template file (" + templateName + ")")
        return
        
    top_add = 1
    bottom_add = 0
    for line in templateFile.readlines():
        if top_add == 1:
            top.append(line)
            match = start.search(line)
            if match != None:
                top_add = 0
        elif bottom_add == 0:
            match = stop.search(line)
            if match != None:
                bottom_add = 1
                bottom.append(line)
        else:
            bottom.append(line)
    templateFile.close()

    if top_add == 1:
        GnomeErrorDialog("The HTML template (" + templateName + ")\n" + \
                         "did not have a '<!-- START -->' comment at the\n" + \
                         "beginning of a line.  The comment tells GRAMPS where\n" + \
                         "to insert the data in the template. Please fix the template\n" + \
                         "and try again.")
        return

    if bottom_add == 0 :
        GnomeErrorDialog("The HTML template (" + templateName + ")\n" + \
                         "did not have a '<!-- STOP -->' comment at the\n" + \
                         "beginning of a line.  The comment tells GRAMPS where\n" + \
                         "to resume the template. Please fix the template\n" + \
                         "and try again.")
        return
                         
    filter = filter_map[filterName]
    ind_list = []

    filter(db,active_person,ind_list)

    for person in ind_list:
        dump_person(person,prefix,top,bottom,directoryName)

    if len(ind_list) > 1:
        dump_index(ind_list,"index.html",prefix,top,bottom,directoryName)
        
    utils.destroy_passed_object(obj)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def print_event(html,name,event):
    if event == None:
        return
    
    date = event.getDate()
    place = event.getPlace()

    if date != "" or place != "":
        html.write("<H2>%s</H2>\n" % name)
        html.write("<UL>\n")
        if date != "":
            html.write("<LI>Date : %s</LI>\n" % date)
        if place != "":
            html.write("<LI>Place : %s</LI>\n" % place)
        html.write("</UL>\n")
            
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def name_or_link(individual, prefix):
    
    name = individual.getPrimaryName().getRegularName()
    if individual in ind_list:
        id = individual.getId()
        return "<A HREF=\"" + prefix + str(id) + ".html\">" + name + "</A>"
    else:
        return name

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def write_reference(html, parent, prefix):
    if parent != None and parent.getPrimaryName() != None:
        html.write("<LI>")
        html.write(name_or_link(parent,prefix))
        html.write("</LI>\n")

#########################################################################
#
# Write a web page for a specific person represented by the key
#
#########################################################################

def dump_person(person,prefix,templateTop,templateBottom,targetDir):

    filebase = "%s%d.html" % (prefix,person.getId())
    html = open(targetDir + os.sep + filebase,"w")

    name = person.getPrimaryName().getRegularName()

    alive = probably_alive(person)

    for line in templateTop:
        html.write(line)

        regex_match = titleRe.search(line)
        if regex_match != None:
            html.write("Family Tree - %s\n" % name )

    html.write("<H1>%s</H1>\n" % person.getPrimaryName().getRegularName())

    photo_list = person.getPhotoList()

    if no_photos or (alive and restrict_photos == 1):
        pass
    elif len(photo_list) > 0:
        import GdkImlib
        file = photo_list[0].getPath()
        image = GdkImlib.Image(file)
        width = int( (float(image.rgb_width) * 200.0) / float(image.rgb_height))
        base = os.path.basename(file)
        image_name = targetDir + os.sep + base
        cmd = const.convert + " -size " + str(width) + "x200 "\
              + file + " " + image_name
        os.system(cmd)
        html.write('<IMG SRC="' + base + '" ALT="')
        html.write(photo_list[0].getDescription())
        html.write('" WIDTH="' + str(width) + '" HEIGHT="200">\n')
        
    if not alive:
        print_event(html,"Birth",person.getBirth())
        print_event(html,"Death",person.getDeath())
    
    family = person.getMainFamily()
    if family != None:
        html.write("<H2>Parents</H2>\n")
        html.write("<UL>\n")
        write_reference(html,family.getFather(), prefix)
        write_reference(html,family.getMother(), prefix)
        html.write("</UL>\n")


    for family in person.getFamilyList():

        html.write("<H2>Spouse</H2>\n")
        html.write("<UL>\n")
        if person.getGender() == Person.male:
            spouse = family.getMother()
        else:    
            spouse = family.getFather()

        if spouse == None:
            name = None
            spouse_alive = 0
        else:    
            name = spouse.getPrimaryName()
            spouse_alive = probably_alive(spouse)
            
        if name == None or name.getRegularName() == "":
            html.write("<LI>Spouse's name is not known</LI>\n")
        else:
            write_reference(html,spouse,prefix)

        marriage = family.getMarriage()
        if marriage and not alive and not spouse_alive:
            place = marriage.getPlace()
            date = marriage.getDate()
            if place != "" and date != "":
                html.write("<LI>Married %s, %s</LI>\n" % (date, place))
            elif place == "":
                html.write("<LI>Marriage place :%s</LI>\n" % place)
            else:
                html.write("<LI>Marriage date :%s</LI>\n" % date)

        if spouse:
            sp_family = spouse.getMainFamily()
            if sp_family:
                sp_father = sp_family.getFather()
                sp_mother = sp_family.getMother()
                if sp_father and sp_mother:
                    html.write("<LI>Spouse's parents: ")
                    html.write(name_or_link(sp_father,prefix))
                    html.write(" and ")
                    html.write(name_or_link(sp_mother,prefix))
                    html.write("</LI>\n")
                elif sp_father:
                    html.write("<LI>Spouse's father: %s</LI>\n" %
                               name_or_link(sp_father,prefix))
                elif sp_mother:
                    html.write("<LI>Spouse's mother: %s</LI>\n" %
                               name_or_link(sp_mother,prefix))
            
        html.write("</UL>\n")

        childList = family.getChildList()
        if len(childList) > 0:
            html.write("<H3>Children</H3>\n")
            html.write("<UL>\n")
            for child in childList:
                write_reference(html,child,prefix)
            html.write("</UL>\n")


    note = person.getNote()
    if note != "":
        html.write("<H2>Notes</H2>\n")
        noteList = string.split(note,"\n")
        for text in noteList:
            html.write("<P>" + text + "</P>\n")

    for line in templateBottom:
        html.write(line)

    html.close()

#########################################################################
#
# Write a web page for a specific person represented by the key
#
#########################################################################

def dump_index(person_list,filename,prefix,templateTop,templateBottom,targetDir):

    html = open(targetDir + os.sep + filename,"w")

    for line in templateTop:
        html.write(line)

        regex_match = titleRe.search(line)
        if regex_match != None:
            html.write("Family Tree - Index\n")

    html.write("<H1>Family Tree Index</H1>\n")

    person_list.sort(sort.by_last_name)
    for person in person_list:
        name = person.getPrimaryName().getName()
        id = person.getId()
        html.write("<A HREF=\"%s%d.html\">%s</A><BR>\n" % (prefix,id,name))

    for line in templateBottom:
        html.write(line)

    html.close()
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return "Generates web (HTML) pages for individuals, or a set of " \
           "individuals."
    
