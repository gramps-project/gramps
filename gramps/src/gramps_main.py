#! /usr/bin/python -O
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


#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import sys
import string
import re
import os

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
import intl,sys
_ = intl.gettext

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *

import GTK
import gnome.help
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *

import Filter
import const
import Plugins
import sort
import utils
import Bookmarks
import ListColors
import Config


#-------------------------------------------------------------------------
#
# Global variables.
#
# I'm not fond of global variables.  Howerver, I am fairly inexperienced
# with a GUI callback model, and I don't have another way of doing this
# yet.
#
#-------------------------------------------------------------------------

active_event  = None
active_person = None
active_father = None
active_family = None
active_parents= None
active_mother = None
active_child  = None
active_spouse = None

select_father = None
select_spouse = None
select_mother = None
select_child  = None
bookmarks     = None

id2col        = {}

surnameList   = []

topWindow     = None
statusbar     = None
Main          = None
person_list   = None
database      = None
family_window = None
queryTop      = None
prefsTop      = None
pv            = {}
sortFunc      = sort.by_last_name2
sbar_active   = 1
DataFilter    = Filter.create("")

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

NOTEBOOK   = "notebook1"
FILESEL    = "fileselection"
FILTERNAME = "filter_list"
ODDFGCOLOR = "oddForeground"
ODDBGCOLOR = "oddBackground"
EVENFGCOLOR= "evenForeground"
EVENBGCOLOR= "evenBackground"

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's birthday, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------
def birthday(person):
    if person:
        return person.getBirth().getQuoteDate()
    else:
        return ""

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's birthday, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------
def deathday(person):
    if person:
        return person.getDeath().getQuoteDate()
    else:
        return ""

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_exit_activate(obj):
    if utils.wasModified():
        question = _("Unsaved changes exist in the current database\n") + \
                   _("Do you wish to save the changes?")
        topWindow.question(question,save_query)
    else:    
        mainquit(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def save_query(value):
    if value == 0:
        on_save_activate(None)
    mainquit(Main)

#-------------------------------------------------------------------------
#
# Displays the about box.  Called from Help menu
#
#-------------------------------------------------------------------------
def on_about_activate(obj):
    GnomeAbout(const.progName,const.version,const.copyright,
               const.authors,const.comments,const.logo).show()
    
#-------------------------------------------------------------------------
#
# Display the help box
#
#-------------------------------------------------------------------------
def on_contents_activate(obj):
    gnome.help.display("gramps",const.helpMenu)
    
#-------------------------------------------------------------------------
#
# Called when the remove child button clicked on the family page.  If
# no active person is specified, or if no active child is specified,
# then the button press is meaningless, and should be ignored.  Otherwise,
# remove the child from the active family, and set the family the child
# belongs to to None.
#
#-------------------------------------------------------------------------
def on_remove_child_clicked(obj):
    if not active_family or not active_child:
        return

    active_family.removeChild(active_child)
    active_child.setMainFamily(None)
    utils.modified()
    load_family()

#-------------------------------------------------------------------------
#
# Called when the user selects the edit marriage button on the family
# page.
#
#-------------------------------------------------------------------------
def on_edit_marriage_clicked(obj):
    global queryTop
	
    if not active_family:
        add_spouse()
        return

    queryTop = libglade.GladeXML(const.gladeFile,"marriageQuery")
    queryTop.signal_autoconnect({
        "on_marriageQuery_clicked" : on_marriageQuery_clicked,
        "destroy_passed_object" : utils.destroy_passed_object
	})
    marriageQuery = queryTop.get_widget("marriageQuery")
    marriageQuery.show()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_marriageQuery_clicked(obj):
    if queryTop.get_widget("addSpouse").get_active():
        add_spouse()
    elif queryTop.get_widget("editMarriage").get_active():
        marriage_edit(active_family)
    else:
        delete_spouse()
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_add_child_clicked(obj):
    global select_child
    global addChildList
    
    select_child = None
	
    childWindow = libglade.GladeXML(const.gladeFile,"selectChild")
    childWindow.signal_autoconnect({
        "on_save_child_clicked" : on_save_child_clicked,
        "on_addChild_select_row" : on_addChild_select_row,
        "on_show_toggled" : on_show_toggled,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    selectChild = childWindow.get_widget("selectChild")
    addChildList = childWindow.get_widget("addChild")
    redraw_child_list(1)
    selectChild.show()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def redraw_child_list(filter):
    person_list = database.getPersonMap().values()
    person_list.sort(sort.by_last_name)
    addChildList.freeze()
    addChildList.clear()
    index = 0
    for person in person_list:
        if filter and person.getMainFamily() != None:
            continue
        addChildList.append([utils.phonebook_name(person),birthday(person)])
        addChildList.set_row_data(index,person)
        index = index + 1
        
    addChildList.thaw()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_show_toggled(obj):
    redraw_child_list(obj.get_active())
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_add_new_child_clicked(obj):
    global newChildWindow
    
    newChildWindow = libglade.GladeXML(const.gladeFile,"addChild")
    newChildWindow.signal_autoconnect({
        "on_addchild_ok_clicked" : on_addchild_ok_clicked,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    if active_person.getGender() == Person.male:
        surname = active_person.getPrimaryName().getSurname()
    elif active_spouse:
        surname = active_spouse.getPrimaryName().getSurname()
    else:
        surname = ""

    newChildWindow.get_widget("childSurname").set_text(surname)
    newChildWindow.get_widget("addChild").show()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_addchild_ok_clicked(obj):
    global active_family
    
    surname = newChildWindow.get_widget("childSurname").get_text()
    given = newChildWindow.get_widget("childGiven").get_text()
    
    person = Person()
    database.addPerson(person)

    name = Name()

    name.setSurname(surname)
    name.setFirstName(given)
    person.setPrimaryName(name)

    if newChildWindow.get_widget("childGender").get_active():
        person.setGender(Person.male)
    else:
        person.setGender(Person.female)
        
    if not active_family:
        active_family = database.newFamily()
        if active_person.getGender() == Person.male:
            active_family.setFather(active_person)
        else:
            active_family.setMother(active_person)
        active_person.addFamily(active_family)

    if newChildWindow.get_widget("childStatus").get_active():
        person.setMainFamily(active_family)
    else:
        person.addAltFamily(active_family,"Adopted")

    active_family.addChild(person)
        
    # must do an apply filter here to make sure the main window gets updated
    
    apply_filter()
    load_family()
    utils.modified()
    utils.destroy_passed_object(obj)
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_save_child_clicked(obj):
    global active_family
	
    if select_child == None:
        return

    if active_family == None:
        active_family = database.newFamily()
        active_person.addFamily(active_family)
        if active_person.getGender() == Person.male:
            active_family.setFather(active_person)
        else:	
            active_family.setMother(active_person)

    active_family.addChild(select_child)
    family = select_child.getMainFamily()

    if family != None:
        family.removeChild(select_child)
		
    select_child.setMainFamily(active_family)

    utils.modified()
    utils.destroy_passed_object(obj)
    load_family()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_option_index(obj):
    active_item  = obj.get_active()
    index = 0
    for item in obj.children():
        if item == active_item:
            break
        index = index + 1
    return index

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_rtype_clicked(obj,a):
    global family_window
    
    active_item  = obj.get_active()
    
    index = get_option_index(obj)
    type = const.childRelations[index]

    select_father = None
    select_mother = None

    if type == "Biological":
        fam = active_person.getMainFamily()
        if fam:
            select_father = fam.getFather()
            select_mother = fam.getMother()
    else:
        for fam in active_person.getAltFamilyList():
            if fam[1] == type:
                select_father = fam[0].getFather()
                select_mother = fam[0].getMother()

    family_window.get_widget("fatherName").set_text(Config.nameof(select_father))
    family_window.get_widget("motherName").set_text(Config.nameof(select_mother))

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------

def on_choose_parents_clicked(obj):
    global select_mother
    global select_father
    global family_window

#    select_father = active_father
#    select_mother = active_mother

    if active_parents:
        select_father = active_parents.getFather()
        select_mother = active_parents.getMother()
    else:
        select_mother = None
        select_father = None

    family_window = libglade.GladeXML(const.gladeFile,"familyDialog")
    family_window.signal_autoconnect({
        "on_motherList_select_row" : on_motherList_select_row,
        "on_fatherList_select_row" : on_fatherList_select_row,
        "on_rtype_clicked" : on_rtype_clicked,
        "on_save_parents_clicked" : on_save_parents_clicked,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    familyDialog = family_window.get_widget("familyDialog")
	
    fatherList = family_window.get_widget("fatherList")
    fatherList.append(["unknown",""])
    fatherList.set_row_data(0,None)

    fatherName = family_window.get_widget("fatherName")
    fatherName.set_text(Config.nameof(select_father))
    fatherList.set_data("father_text",fatherName)

    motherList = family_window.get_widget("motherList")
    motherList.append(["unknown",""])
    motherList.set_row_data(0,None)

    motherName = family_window.get_widget("motherName")
    motherName.set_text(Config.nameof(select_mother))
    motherList.set_data("mother_text",motherName)

    menu = family_window.get_widget("rtype")
    
    if active_parents == active_person.getMainFamily():
        menu.set_history(0)
    else:
        for fam in active_person.getAltFamilyList():
            if active_parents == fam[0]:
                type = fam[1]
                break
        if type == "Adopted":
            menu.set_history(1)
        else:
            menu.set_history(2)
    
    menu.get_menu().connect("deactivate",on_rtype_clicked,None)

    people = database.getPersonMap().values()
    people.sort(sort.by_last_name)
    father_index = 1
    mother_index = 1
    for person in people:
        if person == active_person:
            continue
        elif person.getGender() == Person.male:
            fatherList.append([utils.phonebook_name(person),birthday(person)])
            fatherList.set_row_data(father_index,person)
            father_index = father_index + 1
        else:
            motherList.append([utils.phonebook_name(person),birthday(person)])
            motherList.set_row_data(mother_index,person)
            mother_index = mother_index + 1

    familyDialog.show()
	
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_new_clicked(obj):
    msg = _("Do you wish to delete all entries and create a new database?")
    topWindow.question(msg,new_database_response)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def new_database_response(val):
    global active_person, active_father
    global active_family, active_mother
    global active_child, select_father, select_mother
    global id2col,person_list

    if val == 1:
        return

    const.personalEvents = const.personalConstantEvents.keys()
    const.personalEvents.sort()
    const.personalAttributes = const.personalConstantAttributes.keys()
    const.personalAttributes.sort()
    database.new()
    topWindow.set_title("Gramps")
    active_person = None
    active_father = None
    active_family = None
    active_mother = None
    active_child  = None
    select_father = None
    select_mother = None
    id2col        = {}

    utils.clearModified()
    change_active_person(None)
    person_list.clear()
    load_family()
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def marriage_edit(family):
    import Marriage

    Marriage.Marriage(family,database)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def full_update():
    Main.get_widget(NOTEBOOK).set_show_tabs(Config.usetabs)
    update_display(1)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def update_display(changed):
    page = Main.get_widget(NOTEBOOK).get_current_page()
    if page == 0:
        if changed:
            apply_filter()
        else:
            goto_active_person()
    elif page == 1:
        load_family()
    else:
        load_tree()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_tools_clicked(obj):
    Plugins.ToolPlugins(database,active_person,update_display)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_reports_clicked(obj):
    Plugins.ReportPlugins(database,active_person)

#-------------------------------------------------------------------------
#
# Called from the fileselector, when the OK button is pressed (Open
# command).  Currently loads a GEDCOM file and destroys the fileselector
# window, which is passed as "obj"
#
#-------------------------------------------------------------------------
def on_ok_button1_clicked(obj):
    new_database_response(0)
    filename = obj.get_filename()
    utils.destroy_passed_object(obj)

    if filename != "":
        read_file(filename)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def read_file(filename):
    base = os.path.basename(filename)
    if base == const.indexFile:
        filename = os.path.dirname(filename)
    elif not os.path.isdir(filename):
        displayError(filename + _(" is not a directory"))
        return

    statusbar.set_status(_("Loading ") +\
                         filename + "...")

    if load_database(filename) == 1:
        topWindow.set_title("Gramps - " + filename)
    else:
        statusbar.set_status("")
        Config.save_last_file("")

#    try:
#        if load_database(filename) == 1:
#            topWindow.set_title("Gramps - " + filename)
#        else:
#            statusbar.set_status("")
#            Config.save_last_file("")
#    except:
#        displayError(_("Failure reading ") + filename)

    statusbar.set_progress(0.0)

#-------------------------------------------------------------------------
#
# Called from the fileselector, when the OK button is pressed (Save
# command).  Currently saves a GEDCOM file and destroys the fileselector
# window, which is passed as "obj"
#
#-------------------------------------------------------------------------
def on_ok_button2_clicked(obj):
    filename = obj.get_filename()
    if filename:
        utils.destroy_passed_object(obj)
        save_file(filename)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def save_file(filename):        
    import WriteXML
    
    if sbar_active:
        statusbar.set_status(_("Saving ") \
                             + filename + "...")

    if os.path.exists(filename):
        if os.path.isdir(filename) == 0:
            displayError(filename + _(" is not a directory"))
            return
    else:
        try:
            os.mkdir(filename)
        except IOError, msg:
            GnomeErrorDialog(_("Could not create ") + \
                             os.path.normpath(filename) +\
                             "\n" + str(msg))
            return
        except OSError, msg:
            GnomeErrorDialog(_("Could not create ") + \
                             os.path.normpath(filename) +\
                             "\n" + str(msg))
            return
        except:
            GnomeErrorDialog(_("Could not create ") + \
                             os.path.normpath(filename))
            return
        
    old_file = filename
    filename = filename + os.sep + const.indexFile
    WriteXML.exportData(database,filename,load_progress)
    database.setSavePath(old_file)
    utils.clearModified()
    Config.save_last_file(old_file)
    if sbar_active:
        statusbar.set_status("")
        statusbar.set_progress(0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def find_family(father,mother):

    if not father and not mother:
        return None
	
    families = database.getFamilyMap().values()
    for family in families:
        if family.getFather() == father and family.getMother() == mother:
            return family

    family = database.newFamily()
    family.setFather(father)
    family.setMother(mother)
    father.addFamily(family)
    mother.addFamily(family)

    return family

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def change_family_type(family,type):

    if not family:
        if type == "Biological":
            main = active_person.getMainFamily()
            if main:
                main.removeChild(active_person)
            active_person.setMainFamily(None)
        else:
            for fam in active_person.getAltFamilyList():
                if fam[1] == type:
                    active_person.removeAltFamily(fam[0])
                    fam.removeChild(active_person)
                    return
    elif family == active_person.getMainFamily():
        if type != "Biological":
            utils.modified()
            active_person.setMainFamily(None)
            found = 0
            for fam in active_person.getAltFamilyList():
                if fam[0] == family:
                    fam[1] = type
                    found = 1
                elif fam[1] == type:
                    fam[0] = family
                    found = 1
            if found == 0:
                active_person.addAltFamily(family,type)
    else:
        for fam in active_person.getAltFamilyList():
            if family == fam[0]:
                if type == "Biological":
                    active_person.setMainFamily(family)
                    active_person.removeAltFamily(family)
                    utils.modified()
                    return
                if type != fam[1]:
                    fam[1] = type
                    utils.modified()
                    return
            if type == fam[1]:
                active_person.removeAltFamily(fam[0])
                fam[0].removeChild(active_person)
                active_person.addAltFamily(family,type)
                family.addChild(active_person)
                utils.modified()
                
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_save_parents_clicked(obj):
    global active_father
    global active_mother
    global active_family

    if select_father or select_mother:
        family = find_family(select_father,select_mother)
    else:    
        family = None

    index = get_option_index(family_window.get_widget("rtype").get_menu())
    type = const.childRelations[index]

    if family != active_family:
        utils.modified()
        if index == 0:
            active_person.setMainFamily(family)
            if family:
                family.addChild(active_person)
        else:
            active_person.addAltFamily(family,type)
            if family:
                family.addChild(active_person)
    else:
        change_family_type(family,type)

    active_mother = select_mother
    active_father = select_father
    active_family = family

    utils.destroy_passed_object(obj)
    load_family()
	
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_select_spouse_clicked(obj):
    global active_spouse
    global select_spouse
    global active_family

    # check to make sure that the person is not already listed as a
    # spouse
    
    for f in active_person.getFamilyList():
        if select_spouse == f.getMother() or select_spouse == f.getFather():
            utils.destroy_passed_object(obj)
            return

    utils.modified()
    active_spouse = select_spouse

    family = database.newFamily()
    active_family = family

    active_person.addFamily(family)
    select_spouse.addFamily(family)

    if active_person.getGender() == Person.male:
        family.setFather(active_person)
        family.setMother(select_spouse)
    else:	
        family.setFather(select_spouse)
        family.setMother(active_person)

    select_spouse = None
    utils.destroy_passed_object(obj)

    load_family()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_active_person(obj):
    load_person(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_spouse_clicked(obj):
    load_person(active_spouse)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_mother_clicked(obj):
    load_person(active_mother)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_father_clicked(obj):
    load_person(active_father)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_addperson_clicked(obj):
    load_person(None)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_person_clicked(obj):
    if not active_person:
        return

    topWindow.question(_("Do you really wish to delete ") + \
                       Config.nameof(active_person), delete_person_response)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def delete_person_response(val):
    if val == 1:
        return
    
    personmap = database.getPersonMap()
    familymap = database.getPersonMap()

    for family in active_person.getFamilyList():
        if active_person.getGender == Person.male:
            if family.getMother() == None:
                for child in family.getChildList():
                    child.setMainFamily(None)
                del familymap[family]
            else:
                family.setFather(None)
        else:
            if family.getFather() == None:
                for child in family.getChildList():
                    child.setMainFamily(None)
                del familymap[family]
            else:
                family.setMother(None)

    family = active_person.getMainFamily()
    if family:
        family.removeChild(active_person)
            
    del personmap[active_person.getId()]
    apply_filter()
    utils.modified()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_editperson_clicked(obj):
    load_person(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_spouse():

    spouseDialog = libglade.GladeXML(const.gladeFile, "spouseDialog")
    spouseDialog.signal_autoconnect({
        "on_spouseList_select_row" : on_spouseList_select_row,
        "on_select_spouse_clicked" : on_select_spouse_clicked,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    spouseList = spouseDialog.get_widget("spouseList")
	
    nameList = database.getPersonMap().values()
    nameList.sort(sort.by_last_name)
    gender = active_person.getGender()
	
    index = 0
    for person in nameList:
		
        if person.getGender() == gender:
            continue
        spouseList.append([Config.nameof(person),birthday(person)])
        spouseList.set_row_data(index,person)
        index = index + 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def delete_spouse():
    global active_family

    if active_person == active_family.getFather():
        person = active_family.getMother()
        if person:
            person.removeFamily(active_family)
        if len(active_family.getChildList()) == 0:
            active_person.removeFamily(active_family)
            database.deleteFamily(active_family)
            if len(active_person.getFamilyList()) > 0:
                active_family = active_person.getFamilyIndex(0)
            else:
                active_family = None
        else:	
            active_family.setMother(None)
    else:
        person = active_family.getFather()
        if person:
            person.removeFamily(active_family)
        if len(active_family.getChildList()) == 0:
            active_person.removeFamily(active_family)
            database.deleteFamily(active_family)
            if len(active_person.getFamilyList()) > 0:
                active_family = active_person.getFamilyIndex(0)
            else:
                active_family = None
        else:
            active_family.setFather(None)
    load_family()
    utils.modified()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_person_list_select_row(obj,a,b,c):
    person = obj.get_row_data(a)
    obj.set_data("a",person)
    change_active_person(person)

#-------------------------------------------------------------------------
#
# on_person_list_click_column
#
# Called when the user selects a column header on the person_list window.
# Change the sort function (column 0 is the name column, and column 2 is
# the birthdate column), set the arrows on the labels to the correct
# orientation, and then call apply_filter to redraw the list
#
#-------------------------------------------------------------------------
def on_person_list_click_column(obj,column):
    global sortFunc

    nameArrow = Main.get_widget("nameSort")
    dateArrow = Main.get_widget("dateSort")
    deathArrow= Main.get_widget("deathSort")
    
    if column == 0:
        dateArrow.hide()
        deathArrow.hide()
        nameArrow.show()
        if sortFunc != sort.by_last_name2:
            sortFunc = sort.by_last_name2
            nameArrow.set(GTK.ARROW_DOWN,2)
        else:
            sortFunc = sort.by_last_name_backwards2
            nameArrow.set(GTK.ARROW_UP,2)
    elif column == 2:
        nameArrow.hide()
        deathArrow.hide()
        dateArrow.show()
        if sortFunc != sort.by_birthdate2:
            sortFunc = sort.by_birthdate2
            dateArrow.set(GTK.ARROW_DOWN,2)
        else:
            sortFunc = sort.by_birthdate_backwards2
            dateArrow.set(GTK.ARROW_UP,2)
    elif column == 3:
        nameArrow.hide()
        deathArrow.show()
        dateArrow.hide()
        if sortFunc != sort.by_deathdate2:
            sortFunc = sort.by_deathdate2
            deathArrow.set(GTK.ARROW_DOWN,2)
        else:
            sortFunc = sort.by_deathdate_backwards2
            deathArrow.set(GTK.ARROW_UP,2)
    apply_filter()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_fatherList_select_row(obj,a,b,c):
    global select_father
	
    select_father = obj.get_row_data(a)
    obj.get_data("father_text").set_text(Config.nameof(select_father))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_addChild_select_row(obj,a,b,c):
    global select_child
	
    select_child = obj.get_row_data(a)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_motherList_select_row(obj,a,b,c):
    global select_mother

    select_mother = obj.get_row_data(a)
    obj.get_data("mother_text").set_text(Config.nameof(select_mother))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_child_list_button_press_event(obj,event):
    if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
        if active_child:
            load_person(active_child)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_person_list_button_press(obj,event):
    if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
        load_person(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def change_active_person(person):
    global active_person

    active_person = person
    modify_statusbar()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def modify_statusbar():
    statusbar.set_status(Config.nameof(active_person))
	
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_child_list_select_row(obj,a,b,c):
    global active_child

    active_child = obj.get_row_data(a)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_spouseList_select_row(obj,a,b,c):
    global select_spouse

    select_spouse = obj.get_row_data(a)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_new_person_activate(obj):
    load_person(None)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_open_activate(obj):
    wFs = libglade.GladeXML (const.gladeFile, FILESEL)
    wFs.signal_autoconnect({
        "on_ok_button1_clicked": on_ok_button1_clicked,
        "destroy_passed_object": utils.destroy_passed_object
        })

    fileSelector = wFs.get_widget(FILESEL)
    fileSelector.show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_revert_activate(obj):
    if database.getSavePath() != "":
        msg = _("Do you wish to abandon your changes and revert to the last saved database?")
        topWindow.question(msg,revert_query)
    else:
        msg = _("Cannot revert to a previous database, since one does not exist")
        topWindow.warning(msg)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def revert_query(value):
    if value == 0:
        const.personalEvents = const.personalConstantEvents.keys()
        const.personalEvents.sort()

        const.personalAttributes = const.personalConstantAttributes.keys()
        const.personalAttributes.sort()

        const.marriageEvents = const.familyConstantEvents.keys()
        const.marriageEvents.sort()
        file = database.getSavePath()
        database.new()
        read_file(file)
        utils.clearModified()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_save_as_activate(obj):
    wFs = libglade.GladeXML (const.gladeFile, FILESEL)
    wFs.signal_autoconnect({
        "on_ok_button1_clicked": on_ok_button2_clicked,
        "destroy_passed_object": utils.destroy_passed_object
        })
    fileSelector = wFs.get_widget(FILESEL)
    fileSelector.show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_save_activate(obj):
    if not database.getSavePath():
        on_save_as_activate(obj)
    else:
        save_file(database.getSavePath())

#-------------------------------------------------------------------------
#
# Switch notebook pages from menu
#
#-------------------------------------------------------------------------
def on_person_list1_activate(obj):
    notebk = Main.get_widget(NOTEBOOK)
    notebk.set_page(0)

def on_family1_activate(obj):
    notebk = Main.get_widget(NOTEBOOK)
    notebk.set_page(1)

def on_pedegree1_activate(obj):
    notebk = Main.get_widget(NOTEBOOK)
    notebk.set_page(2)

#-------------------------------------------------------------------------
#
# Load the appropriate page after a notebook switch
#
#-------------------------------------------------------------------------
def on_notebook1_switch_page(obj,junk,page):
    if not active_person:
        return
    if (page == 0):
        if id2col.has_key(active_person):
            column = id2col[active_person]
            person_list.select_row(column,0)
            person_list.moveto(column,0)
    elif (page == 1):
        load_family()
    elif (page == 2):
        load_tree()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_pv_n0_clicked(obj):
    family = active_person.getMainFamily()
    if family:
        father = family.getFather()
        if father:
            change_active_person(father)
            load_tree()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_pv_n1_clicked(obj):
    family = active_person.getMainFamily()
    if family:
        mother = family.getMother()
        if mother:
            change_active_person(mother)
            load_tree()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_arrow_left_clicked(obj):
    if active_person:
        myMenu = GtkMenu()
        for family in active_person.getFamilyList():
            for child in family.getChildList():
                menuitem = GtkMenuItem(Config.nameof(child))
                myMenu.append(menuitem)
                menuitem.set_data("person",child)
                menuitem.connect("activate",on_childmenu_changed)
                menuitem.show()
        myMenu.popup(None,None,None,0,0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_childmenu_changed(obj):
    person = obj.get_data("person")
    if person == None:
        return
    change_active_person(person)
    load_tree()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_mother_next_clicked(obj):
    if active_parents:
        mother = active_parents.getMother()
        if mother:
            change_active_person(mother)
            obj.set_sensitive(1)
            load_family()
        else:
            obj.set_sensitive(0)
    else:
        obj.set_sensitive(0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_father_next_clicked(obj):
    if active_parents:
        father = active_parents.getFather()
        if father:
            change_active_person(father)
            obj.set_sensitive(1)
            load_family()
        else:
            obj.set_sensitive(0)
    else:
        obj.set_sensitive(0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_fv_prev_clicked(obj):
    if active_child:
        change_active_person(active_child)
        load_family()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_swap_clicked(obj):
    if not active_person:
        return
    if len(active_person.getFamilyList()) > 1:
        spouse = Main.get_widget("fv_spouse").get_menu().get_active().get_data("person")
    else:
        spouse = Main.get_widget("fv_spouse1").get_data("person")

    if not spouse:
        return
    change_active_person(spouse)
    load_family()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_apply_filter_clicked(obj):
    global DataFilter

    invert_filter = Main.get_widget("invert").get_active()
    qualifer = Main.get_widget("filter").get_text()
    menu = Main.get_widget(FILTERNAME).get_menu()
    function = menu.get_active().get_data("filter")
    DataFilter = function(qualifer)
    DataFilter.set_invert(invert_filter)
    apply_filter()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_filter_name_changed(obj):
    function = obj.get_data("function")
    Main.get_widget("filter").set_sensitive(function())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_spouselist_changed(obj):
    global active_spouse
    
    if active_person == None :
        return

    display_marriage(obj.get_data("family"))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def new_after_edit(person):
    database.addPerson(person.person)
    update_display(1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def update_after_edit(person):
    update_display(1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_person(person):
    import EditPerson
    
    if person == None:
        EditPerson.EditPerson(Person(),database,surnameList,\
                              new_after_edit)
    else:
        EditPerson.EditPerson(person,database,surnameList,\
                              update_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_family():
    global active_mother
    global active_father
    global active_family
    global active_parents
    global active_spouse
    
    family_types = []
    main_family = None

    Main.get_widget("fv_person").set_text(Config.nameof(active_person))

    if active_person:
        main_family = active_person.getMainFamily()
        active_parents = main_family
        family_types = active_person.getAltFamilyList()

        if active_parents == None and len(family_types) > 0:
            fam = family_types[0]
            active_parents = fam[0]
    else:
        active_parents = None

    if len(family_types) > 0:
        typeMenu = GtkMenu()
        if main_family:
            menuitem = GtkMenuItem("Biological")
            menuitem.set_data("parents",main_family)
            menuitem.connect("activate",on_current_type_changed)
            menuitem.show()
            typeMenu.append(menuitem)
        for fam in family_types:
            menuitem = GtkMenuItem(fam[1])
            menuitem.set_data("parents",fam[0])
            menuitem.connect("activate",on_current_type_changed)
            menuitem.show()
            typeMenu.append(menuitem)
        Main.get_widget("childtype").set_menu(typeMenu)
        Main.get_widget("childtype").show()
    else:
        Main.get_widget("childtype").hide()

    change_parents(active_parents)

    if active_person:
        number_of_families = len(active_person.getFamilyList())
        if number_of_families > 1:
            myMenu = GtkMenu()
            if active_person != None:
                for family in active_person.getFamilyList():
                    person = None
                    if family.getMother() == active_person:
                        if family.getFather() != None:
                            person = family.getFather()
                    else:		
                        if family.getMother() != None:
                            person = family.getMother()

                    menuitem = GtkMenuItem(Config.nameof(person))
                    myMenu.append(menuitem)
                    menuitem.set_data("person",person)
                    menuitem.set_data("family",family)
                    menuitem.connect("activate",on_spouselist_changed)
                    menuitem.show()

                Main.get_widget("fv_spouse").set_menu(myMenu)
            Main.get_widget("lab_or_list").set_page(1)
        elif number_of_families == 1:
            Main.get_widget("lab_or_list").set_page(0)
            family = active_person.getFamilyList()[0]
            if active_person != family.getFather():
                spouse = family.getFather()
            else:
                spouse = family.getMother()
            active_spouse = spouse
            fv_spouse1 = Main.get_widget("fv_spouse1")
            fv_spouse1.set_text(Config.nameof(spouse))
            fv_spouse1.set_data("person",spouse)
            fv_spouse1.set_data("family",active_person.getFamilyList()[0])
        else:
            Main.get_widget("lab_or_list").set_page(0)
            Main.get_widget("fv_spouse1").set_text("")
            fv_spouse1 = Main.get_widget("fv_spouse1")
            fv_spouse1.set_text("")
            fv_spouse1.set_data("person",None)
            fv_spouse1.set_data("family",None)

        if number_of_families > 0:
            display_marriage(active_person.getFamilyList()[0])
        else:
            display_marriage(None)
    else:
        fv_spouse1 = Main.get_widget("fv_spouse1").set_text("")
        display_marriage(None)
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def change_parents(family):
    global active_father
    global active_mother
    
    fv_father = Main.get_widget("fv_father")
    fv_mother = Main.get_widget("fv_mother")
    father_next = Main.get_widget("father_next")
    mother_next = Main.get_widget("mother_next")
    
    if family != None :

        active_father = family.getFather()
        if active_father != None :
            fv_father.set_text(Config.nameof(active_father))
            father_next.set_sensitive(1)
        else :
            fv_father.set_text("")
            father_next.set_sensitive(0)

        active_mother = family.getMother()
        if active_mother != None :
            fv_mother.set_text(Config.nameof(active_mother))
            mother_next.set_sensitive(1)
        else :
            fv_mother.set_text("")
            mother_next.set_sensitive(0)
    elif active_person == None :
        fv_father.set_text("")
        fv_mother.set_text("")
        mother_next.set_sensitive(0)
        father_next.set_sensitive(0)
    else :
        fv_father.set_text("")
        fv_mother.set_text("")
        mother_next.set_sensitive(0)
        father_next.set_sensitive(0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_tree():
    text = {}
    tip = {}
    for i in range(1,16):
        text[i] = ""
        tip[i] = ""

    load_tree_values(active_person,1,16,text,tip)

    tips = GtkTooltips()
    for i in range(1,16):
        pv[i].set_text(text[i])
        if tip[i] != "":
            tips.set_tip(pv[i],tip[i])
        else:
            tips.set_tip(pv[i],None)

    if text[2] == "":
        Main.get_widget("ped_father_next").set_sensitive(0)
    else:
        Main.get_widget("ped_father_next").set_sensitive(1)

    if text[3] == "":
        Main.get_widget("ped_mother_next").set_sensitive(0)
    else:
        Main.get_widget("ped_mother_next").set_sensitive(1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_tree_values(person,index,max,pv_text,tip):
    if person == None:
        return
    pv_text[index] = Config.nameof(person)
    bdate = person.getBirth().getDate()
    ddate = person.getDeath().getDate()
    if bdate and ddate:
        text = pv_text[index] + "\nb. " + bdate + "\n" + "d. " +  ddate
    elif bdate and not ddate:
        text = pv_text[index] + "\nb. " + bdate
    elif not bdate and ddate:
        text = pv_text[index] + "\nd. " + ddate
    else:
        text = pv_text[index]
    tip[index] = text
    if 2*index+1 < max:
        family = person.getMainFamily()
        if family != None:
            load_tree_values(family.getFather(),2*index,max,pv_text,tip)
            load_tree_values(family.getMother(),(2*index)+1,max,pv_text,tip)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def display_marriage(family):
    global active_child
    global active_family

    active_family = family
    clist = Main.get_widget("child_list")
    fv_prev = Main.get_widget("fv_prev")

    clist.clear()
    active_child = None
    active_fams = family

    i = 0
    if family != None:
        child_list = family.getChildList()
        child_list.sort(sort.by_birthdate)
        for child in child_list:
            status = "unknown"
            if child.getGender():
                gender = const.male
            else:
                gender = const.female
            if child.getMainFamily() == family:
                status = "Natural"
            else:
                for fam in child.getAltFamilyList():
                    if fam[0] == family:
                        status = fam[1]
            clist.append([Config.nameof(child),gender,birthday(child),status])
            clist.set_row_data(i,child)
            i=i+1
            if i != 0:
                fv_prev.set_sensitive(1)
                clist.select_row(0,0)
            else:	
                fv_prev.set_sensitive(0)
    else:
        fv_prev.set_sensitive(0)
		
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_progress(value):
    if sbar_active:
        statusbar.set_progress(value)
        while events_pending():
            mainiteration()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_database(name):
    import ReadXML

    global active_person
	
    filename = name + os.sep + const.indexFile

    if ReadXML.loadData(database,filename,load_progress) == 0:
        return 0

    database.setSavePath(name)

    res = database.getResearcher()
    if res.getName() == "" and Config.owner.getName() != "":
        database.setResearcher(Config.owner)
        utils.modified()

    setup_bookmarks()

    mylist = database.getPersonEventTypes()
    for type in mylist:
        if type not in const.personalEvents:
            const.personalEvents.append(type)

    mylist = database.getPersonAttributeTypes()
    for type in mylist:
        if type not in const.personalAttributes:
            const.personalAttributes.append(type)

    Config.save_last_file(name)
    Main.get_widget("filter").set_text("")
    active_person = database.getDefaultPerson()
    update_display(1)
    return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def setup_bookmarks():
    global bookmarks
    
    menu = Main.get_widget("jump_to")
    person_map = database.getPersonMap()
    bookmarks = Bookmarks.Bookmarks(database.bookmarks,person_map,\
                                    menu,bookmark_callback)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def displayError(msg):
    topWindow.error(msg)
    statusbar.set_status("")
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def apply_filter():

    people = database.getPersonMap().values()

    names = []
    for person in people:
        names.append((person.getPrimaryName(),person,0))
        if Config.hide_altnames == 0:
            for name in person.getAlternateNames():
                names.append((name,person,1))
        
    names.sort(sortFunc)
    
    person_list.freeze()
    person_list.clear()

    color_clist = ListColors.ColorList(person_list,1)

    i=0
    for name_tuple in names:
        person = name_tuple[1]
        alt = name_tuple[2]
        name = name_tuple[0]
        
        pname = utils.phonebook_from_name(name,alt)

        lastname = name.getSurname()
        if lastname and lastname not in surnameList:
            surnameList.append(lastname)

        if DataFilter.compare(person):
            id2col[person] = i
            if person.getGender():
                gender = const.male
            else:
                gender = const.female
            data = [pname,gender,birthday(person),deathday(person)]
            color_clist.add_with_data(data,person)
        i = i + 1
        
    person_list.thaw()

    if i > 0:
        goto_active_person()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def goto_active_person():
    if id2col.has_key(active_person):
        column = id2col[active_person]
        person_list.select_row(column,0)
        person_list.moveto(column,0)
    else:
        person_list.select_row(0,0)
        person_list.moveto(0,0)
        person = person_list.get_row_data(0)
        change_active_person(person)	
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_home_clicked(obj):
    temp = database.getDefaultPerson()
    if temp:
        change_active_person(temp)
        update_display(0)
    else:
        topWindow.error(_("No default/home person has been set"))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_bookmark_activate(obj):
    bookmarks.add(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_bookmarks_activate(obj):
    bookmarks.edit()
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_default_person_activate(obj):
    if active_person:
        name = active_person.getPrimaryName().getRegularName()
        topWindow.question(_("Do you wish to set ") + name + \
                           _(" as the home person?"), set_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def set_person(value):
    if not value:
        database.setDefaultPerson(active_person)
        utils.modified()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_current_type_changed(obj):
    global active_parents
    
    active_parents = obj.get_data("parents")
    change_parents(active_parents)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_statusbar_unmap(obj):
    global sbar_active

    sbar_active = 0

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def export_callback(obj,plugin_function):
    plugin_function(database,active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def import_callback(obj,plugin_function):
    plugin_function(database,active_person,update_display)
    topWindow.set_title("Gramps - " + database.getSavePath())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def bookmark_callback(obj,person):
    change_active_person(person)
    update_display(0)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_preferences_activate(obj):
    Config.display_preferences_box()
    
#-------------------------------------------------------------------------
#
# Main program
#
#-------------------------------------------------------------------------

def main(arg):
    global database, Main
    global statusbar
    global person_list, pv
    global topWindow
    
    import ReadXML

    rc_parse(const.gtkrcFile)
    Plugins.load_plugins(const.pluginsDir)
    Filter.load_filters(const.filtersDir)
    path = os.path.expanduser("~/.gramps/plugins")
    if os.path.isdir(path):
        Plugins.load_plugins(path)
    path = os.path.expanduser("~/.gramps/filters")
    if os.path.isdir(path):
        Filter.load_filters(path)

    Main = libglade.GladeXML(const.gladeFile, "gramps")
    topWindow   = Main.get_widget("gramps")
    statusbar   = Main.get_widget("statusbar")
    person_list = Main.get_widget("person_list")
    filter_list = Main.get_widget("filter_list")
    
    myMenu = GtkMenu()
    for filter in Filter.filterList:
        menuitem = GtkMenuItem(filter)
        myMenu.append(menuitem)
        menuitem.set_data("filter",Filter.filterMap[filter])
        menuitem.set_data("function",Filter.filterEnb[filter])
        menuitem.connect("activate",on_filter_name_changed)
        menuitem.show()
    filter_list.set_menu(myMenu)
    
    Main.get_widget("filter").set_sensitive(0)

    # set the window icon 
    topWindow.set_icon(GtkPixmap(topWindow,const.logo))
    
    person_list.column_titles_active()

    for box in range(1,16):
        pv[box] = Main.get_widget("pv%d" % box)

    Main.signal_autoconnect({
        "on_about_activate": on_about_activate,
        "on_reports_clicked" : on_reports_clicked,
        "on_person_list1_activate": on_person_list1_activate,
        "on_family1_activate" : on_family1_activate,
        "on_pedegree1_activate" : on_pedegree1_activate,
        "on_notebook1_switch_page": on_notebook1_switch_page,
        "on_ok_button1_clicked": on_ok_button1_clicked,
        "on_father_next_clicked": on_father_next_clicked,
        "on_mother_next_clicked": on_mother_next_clicked,
        "on_person_list_select_row": on_person_list_select_row,
        "on_person_list_click_column": on_person_list_click_column,
        "on_person_list_button_press": on_person_list_button_press,
        "destroy_passed_object": utils.destroy_passed_object,
        "on_swap_clicked" : on_swap_clicked,
        "on_child_list_button_press_event" : on_child_list_button_press_event,
        "on_child_list_select_row" : on_child_list_select_row,
        "on_fv_prev_clicked" : on_fv_prev_clicked,
        "on_contents_activate" : on_contents_activate,
        "on_choose_parents_clicked" : on_choose_parents_clicked, 
        "on_spouselist_changed" : on_spouselist_changed,
        "on_home_clicked" : on_home_clicked,
        "on_default_person_activate" : on_default_person_activate,
        "on_pv_n0_clicked" : on_pv_n0_clicked,
        "on_pv_n1_clicked" : on_pv_n1_clicked,
        "on_apply_filter_clicked": on_apply_filter_clicked,
        "on_save_as_activate" : on_save_as_activate,
        "on_add_new_child_clicked" : on_add_new_child_clicked,
        "on_tools_clicked" : on_tools_clicked,
        "on_save_activate" : on_save_activate,
        "on_revert_activate" : on_revert_activate,
        "on_add_child_clicked" : on_add_child_clicked,
        "on_edit_marriage_clicked" : on_edit_marriage_clicked,
        "on_remove_child_clicked" : on_remove_child_clicked,
        "on_new_clicked" : on_new_clicked,
        "on_add_bookmark_activate" : on_add_bookmark_activate,
        "on_arrow_left_clicked" : on_arrow_left_clicked,
        "on_addperson_clicked" : on_addperson_clicked,
        "on_delete_person_clicked" : on_delete_person_clicked,
        "on_preferences_activate" : on_preferences_activate,
        "on_edit_bookmarks_activate" : on_edit_bookmarks_activate,
        "on_edit_active_person" : on_edit_active_person,
        "on_edit_spouse_clicked" : on_edit_spouse_clicked,
        "on_edit_father_clicked" : on_edit_father_clicked,
        "on_edit_mother_clicked" : on_edit_mother_clicked,
        "on_exit_activate" : on_exit_activate,
        "on_statusbar_unmap" : on_statusbar_unmap,
        "on_open_activate" : on_open_activate
        })	

    database = RelDataBase()
    Config.loadConfig(full_update)
    Main.get_widget(NOTEBOOK).set_show_tabs(Config.usetabs)

    if arg != None:
        read_file(arg)
    elif Config.lastfile != None and Config.lastfile != "" and Config.autoload:
        read_file(Config.lastfile)

    Main.get_widget("export1").set_submenu(Plugins.export_menu(export_callback))
    Main.get_widget("import1").set_submenu(Plugins.import_menu(import_callback))

    database.setResearcher(Config.owner)
    mainloop()

#-------------------------------------------------------------------------
#
# Start it all
#
#-------------------------------------------------------------------------
if __name__ == '__main__':
    main(None)
    
