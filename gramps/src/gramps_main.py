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
import EditSource
import EditPerson
import Marriage

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
select_child_list = {}
bookmarks     = None

id2col        = {}

topWindow     = None
statusbar     = None
gtop          = None
person_list   = None
source_list   = None
database      = None
family_window = None
queryTop      = None
prefsTop      = None
pv            = {}
sortFunc      = sort.fast_name_sort
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
def delete_event(widget, event):
    widget.hide()
    if utils.wasModified():
        question = _("Unsaved changes exist in the current database\n") + \
                   _("Do you wish to save the changes?")
        topWindow.question(question,save_query)
    else:    
        mainquit(widget)
    return TRUE

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
    mainquit(gtop)

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
    
    GnomeOkDialog(_("Sorry.  Online help for gramps is currently under development.\nUnfortunately, it is not yet ready."))
    
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
# 
#
#-------------------------------------------------------------------------
def on_add_sp_clicked(obj):
    add_spouse()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_edit_sp_clicked(obj):
    marriage_edit(active_family)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_delete_sp_clicked(obj):
    delete_spouse()
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_add_child_clicked(obj):
    global addChildList
    global childWindow
    global select_child_list
    
    childWindow = libglade.GladeXML(const.gladeFile,"selectChild")
    
    childWindow.signal_autoconnect({
        "on_save_child_clicked" : on_save_child_clicked,
        "on_addChild_select_row" : on_addChild_select_row,
        "on_addChild_unselect_row" : on_addChild_unselect_row,
        "on_show_toggled" : on_show_toggled,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    select_child_list = {}
    selectChild = childWindow.get_widget("selectChild")
    addChildList = childWindow.get_widget("addChild")
    addChildList.set_column_visibility(1,Config.id_visible)

    father = active_family.getFather()
    if father != None:
        fname = father.getPrimaryName().getName()
        childWindow.get_widget("flabel").set_text(_("Relationship to %s") % fname)

    mother = active_family.getMother()
    if mother != None:
        mname = mother.getPrimaryName().getName()
        childWindow.get_widget("mlabel").set_text(_("Relationship to %s") % mname)

    childWindow.get_widget("mrel").set_text(_("Birth"))
    childWindow.get_widget("frel").set_text(_("Birth"))
    
    redraw_child_list(2)
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

    bday = active_person.getBirth().getDateObj()
    if  bday.getYear() != -1:
        bday_valid = 1
    else:
        bday_valid = 0
    dday = active_person.getDeath().getDateObj()
    if  dday.getYear() != -1:
        dday_valid = 1
    else:
        dday_valid = 0
    
    slist = []
    f = active_person.getMainFamily()
    if f:
        if f.getFather():
            slist.append(f.getFather())
        if f.getMother():
            slist.append(f.getFather())
            
    for f in active_person.getFamilyList():
        slist.append(f.getFather())
        slist.append(f.getMother())
        for c in f.getChildList():
            slist.append(c)
            
    for person in person_list:
        if person.getMainFamily() == active_person.getMainFamily():
            continue
        if person in slist:
            continue
        if filter:
            if person.getMainFamily() != None:
                continue
            
            pdday = person.getDeath().getDateObj()
            pbday = person.getBirth().getDateObj()

            if bday_valid:
                if pbday.getYear() != -1:

                    # reject if child birthdate < parents birthdate + 10
                    if pbday.getLowYear() < bday.getHighYear()+10:
                        continue

                    # reject if child birthdate > parents birthdate + 90
                    if pbday.getLowYear() > bday.getHighYear()+90:
                        continue

                if pdday.getYear() != -1:
                    # reject if child deathdate < parents birthdate+ 10
                    if pdday.getLowYear() < limit.getHighYear()+10:
                        continue
                
            if dday_valid:

                if pbday.getYear() != -1:
                    
                    # reject if childs birth date > parents deathday + 3
                    if pdday.getLowYear() > dday.getHighYear()+3:
                        continue

                if pdday.getYear() != -1:

                    # reject if childs death date > parents deathday + 150
                    if pbday.getLowYear() > dday.getHighYear() + 150:
                        continue
        
        addChildList.append([utils.phonebook_name(person),birthday(person),\
                             person.getId()])
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

    father = active_family.getFather()
    if father != None:
        fname = father.getPrimaryName().getName()
        newChildWindow.get_widget("flabel").set_text(_("Relationship to %s") % fname)

    mother = active_family.getMother()
    if mother != None:
        mname = mother.getPrimaryName().getName()
        newChildWindow.get_widget("mlabel").set_text(_("Relationship to %s") % mname)

    newChildWindow.get_widget("childSurname").set_text(surname)
    newChildWindow.get_widget("addChild").show()
    newChildWindow.get_widget("mrel").set_text(_("Birth"))
    newChildWindow.get_widget("frel").set_text(_("Birth"))

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

    mrel = const.childRelations[newChildWindow.get_widget("mrel").get_text()]
    frel = const.childRelations[newChildWindow.get_widget("frel").get_text()]

    if mrel == "Birth" and frel == "Birth":
        person.setMainFamily(active_family)
    else:
        person.addAltFamily(active_family,mrel,frel)

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

    for select_child in select_child_list.keys():

        if active_family == None:
            active_family = database.newFamily()
            active_person.addFamily(active_family)
            if active_person.getGender() == Person.male:
                active_family.setFather(active_person)
            else:	
                active_family.setMother(active_person)

        active_family.addChild(select_child)
		
        mrel = const.childRelations[childWindow.get_widget("mrel").get_text()]
        mother = active_family.getMother()
        if mother and mother.getGender() != Person.female:
            if mrel == "Birth":
                mrel = "Unknown"
                
        frel = const.childRelations[childWindow.get_widget("frel").get_text()]
        father = active_family.getFather()
        if father and father.getGender() != Person.male:
            if frel == "Birth":
                frel = "Unknown"

        if mrel == "Birth" and frel == "Birth":
            family = select_child.getMainFamily()
            if family != None and family != active_family:
                family.removeChild(select_child)

            select_child.setMainFamily(active_family)
        else:
            select_child.addAltFamily(active_family,mrel,frel)

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
def on_choose_parents_clicked(obj):
    global select_mother
    global select_father
    global family_window

    if active_parents:
        select_father = active_parents.getFather()
        select_mother = active_parents.getMother()
    else:
        select_mother = None
        select_father = None

    family_window = libglade.GladeXML(const.gladeFile,"familyDialog")
    familyDialog = family_window.get_widget("familyDialog")
	
    if active_parents and active_parents == active_person.getMainFamily():
        family_window.get_widget("mrel").set_text(_("Birth"))
        family_window.get_widget("frel").set_text(_("Birth"))
    else:
        for f in active_person.getAltFamilyList():
            if f[0] == active_parents:
                family_window.get_widget("mrel").set_text(_(f[1]))
                family_window.get_widget("frel").set_text(_(f[2]))
                break
        else:
            family_window.get_widget("mrel").set_text(_("Unknown"))
            family_window.get_widget("frel").set_text(_("Unknown"))

    fcombo = family_window.get_widget("prel_combo")
    prel = family_window.get_widget("prel")
            
    prel.set_data("o",family_window)
    fcombo.set_popdown_strings(const.familyRelations)

    family_window.signal_autoconnect({
        "on_motherList_select_row" : on_motherList_select_row,
        "on_fatherList_select_row" : on_fatherList_select_row,
        "on_save_parents_clicked" : on_save_parents_clicked,
        "on_prel_changed" : on_prel_changed,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    text = _("Choose the Parents of %s") % Config.nameof(active_person)
    family_window.get_widget("chooseTitle").set_text(text)
    if active_parents:
        prel.set_text(active_parents.getRelationship())
    familyDialog.show()
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_prel_changed(obj):

    family_window = obj.get_data("o")
    type = obj.get_text()

    fatherName = family_window.get_widget("fatherName")
    fatherName.set_text(Config.nameof(select_father))
    motherName = family_window.get_widget("motherName")
    motherName.set_text(Config.nameof(select_mother))

    fatherList = family_window.get_widget("fatherList")
    motherList = family_window.get_widget("motherList")

    fatherList.freeze()
    motherList.freeze()
    fatherList.clear()
    motherList.clear()

    fatherList.append(["Unknown",""])
    fatherList.set_row_data(0,None)
    fatherList.set_data("father_text",fatherName)

    motherList.append(["Unknown",""])
    motherList.set_row_data(0,None)
    motherList.set_data("mother_text",motherName)

    people = database.getPersonMap().values()
    people.sort(sort.by_last_name)
    father_index = 1
    mother_index = 1
    for person in people:
        if person == active_person:
            continue
        elif type == "Partners":
            fatherList.append([utils.phonebook_name(person),birthday(person)])
            fatherList.set_row_data(father_index,person)
            father_index = father_index + 1
            motherList.append([utils.phonebook_name(person),birthday(person)])
            motherList.set_row_data(mother_index,person)
            mother_index = mother_index + 1
        elif person.getGender() == Person.male:
            fatherList.append([utils.phonebook_name(person),birthday(person)])
            fatherList.set_row_data(father_index,person)
            father_index = father_index + 1
        else:
            motherList.append([utils.phonebook_name(person),birthday(person)])
            motherList.set_row_data(mother_index,person)
            mother_index = mother_index + 1

    if type == "Partners":
        family_window.get_widget("mlabel").set_text(_("Parent"))
        family_window.get_widget("flabel").set_text(_("Parent"))
    else:
        family_window.get_widget("mlabel").set_text(_("Mother"))
        family_window.get_widget("flabel").set_text(_("Father"))

    motherList.thaw()
    fatherList.thaw()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_new_clicked(obj):
    msg = _("Do you want to close the current database and create a new one?")
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

    const.personalEvents = const.initialize_personal_event_list()
    const.personalAttributes = const.initialize_personal_attribute_list()
    const.marriageEvents = const.initialize_marriage_event_list()
    const.familyAttributes = const.initialize_family_attribute_list()
    const.familyRelations = const.initialize_family_relation_list()
    const.places = []
    
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
    load_sources()
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def marriage_edit(family):
    Marriage.Marriage(family,database)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def full_update():
    gtop.get_widget(NOTEBOOK).set_show_tabs(Config.usetabs)
    clist = gtop.get_widget("child_list")
    clist.set_column_visibility(4,Config.show_detail)
    clist.set_column_visibility(1,Config.id_visible)
    apply_filter()
    load_family()
    load_sources()
    load_tree()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def update_display(changed):
    page = gtop.get_widget(NOTEBOOK).get_current_page()
    if page == 0:
        if changed:
            apply_filter()
        else:
            goto_active_person()
    elif page == 1:
        load_family()
    elif page == 3:
        load_sources()
    else:
        load_tree()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def load_sources():
    source_list.clear()
    source_list.freeze()

    color_clist = ListColors.ColorList(source_list,1)

    current_row = source_list.get_data("i")
    if current_row == None:
        current_row = -1

    index = 0
    for src in database.getSourceMap().values():
        source_list.append([src.getTitle(),src.getAuthor()])
        source_list.set_row_data(index,src)
        index = index + 1

    if index > 0:
        if current_row == -1:
            current_row = 0
        source_list.select_row(current_row,0)
        source_list.moveto(current_row,0)

    source_list.set_data("i",current_row)
    source_list.thaw()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_source_list_button_press_event(obj,event):
    if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
        index = obj.get_data("i")
        if index == -1:
            return

        source = obj.get_row_data(index)
        EditSource.EditSource(source,database,update_source_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_source_list_select_row(obj,a,b,c):
    obj.set_data("i",a)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_source_clicked(obj):
    EditSource.EditSource(Source(),database,new_source_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_source_clicked(obj):
    pass

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_source_clicked(obj):
    index = obj.get_data("i")
    if index == -1:
        return

    source = obj.get_row_data(index)
    EditSource.EditSource(source,database,update_source_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def new_source_after_edit(source):
    database.addSource(source)
    update_display(1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def update_source_after_edit(source):
    update_display(1)
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_tools_clicked(obj):
    if active_person:
        Plugins.ToolPlugins(database,active_person,update_display)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_reports_clicked(obj):
    if active_person:
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
        displayError(_("%s is not a directory") % filename)
        return

    statusbar.set_status(_("Loading %s ...") % filename)

    if load_database(filename) == 1:
        topWindow.set_title("%s - %s" % (_("Gramps"),filename))
    else:
        statusbar.set_status("")
        Config.save_last_file("")

    for person in database.getPersonMap().values():
        lastname = person.getPrimaryName().getSurname()
        if lastname and lastname not in const.surnames:
            const.surnames.append(lastname)
            
    full_update()
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

    filename = os.path.normpath(filename)
    
    if sbar_active:
        statusbar.set_status(_("Saving %s ...") % filename)

    if os.path.exists(filename):
        if os.path.isdir(filename) == 0:
            displayError(_("%s is not a directory") % filename)
            return
    else:
        try:
            os.mkdir(filename)
        except IOError, msg:
            GnomeErrorDialog(_("Could not create %s") % filename + "\n" + str(msg))
            return
        except OSError, msg:
            GnomeErrorDialog(_("Could not create %s") % filename + "\n" + str(msg))
            return
        except:
            GnomeErrorDialog(_("Could not create %s") % filename)
            return
        
    old_file = filename
    filename = filename + os.sep + const.indexFile
    try:
        WriteXML.exportData(database,filename,load_progress)
    except IOError, msg:
        GnomeErrorDialog(_("Could not create %s") % filename + "\n" + str(msg))
        return
    except OSError, msg:
        GnomeErrorDialog(_("Could not create %s") % filename + "\n" + str(msg))
        return
#    except:
#        GnomeErrorDialog(_("Could not create %s") % filename)
#        return

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
        elif family.getFather() == mother and family.getMother() == father:
            return family

    family = database.newFamily()
    family.setFather(father)
    family.setMother(mother)
    
    if father:
        father.addFamily(family)

    if mother:
        mother.addFamily(family)

    return family

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def change_family_type(family,mrel,frel):

    is_main = mrel == "Birth" and frel == "Birth"
    
    if not family:
        if is_main:
            main = active_person.getMainFamily()
            if main:
                main.removeChild(active_person)
            active_person.setMainFamily(None)
        else:
            for fam in active_person.getAltFamilyList():
                if is_main:
                    active_person.removeAltFamily(fam[0])
                    fam.removeChild(active_person)
                    return
    elif family == active_person.getMainFamily():
        if is_main:
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
                active_person.addAltFamily(family,mrel,frel)
    else:
        for fam in active_person.getAltFamilyList():
            if family == fam[0]:
                if is_main:
                    active_person.setMainFamily(family)
                    active_person.removeAltFamily(family)
                    utils.modified()
                    break
                if mrel == fam[1] and frel == fam[2]:
                    break
                if mrel != fam[1] or frel != fam[2]:
                    active_person.removeAltFamily(family)
                    active_person.addAltFamily(family,mrel,frel)
                    utils.modified()
                    break
        else:
            active_person.addAltFamily(family,mrel,frel)
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
    global select_mother
    global select_father

    mrel = family_window.get_widget("mrel").get_text()
    frel = family_window.get_widget("frel").get_text()
    type = family_window.get_widget("prel").get_text()

    mrel = const.childRelations[mrel]
    frel = const.childRelations[frel]
    type = save_frel(type)
    
    if select_father or select_mother:
        if select_mother.getGender() == Person.male and \
           select_father.getGender() == Person.female:
            family = find_family(select_father,select_mother)
            family.setFather(select_mother)
            family.setMother(select_father)
            x = select_father
            select_father = select_mother
            select_mother = x
        elif select_mother.getGender() != select_father.getGender():
            if type == "Partners":
                type = "Unknown"
            family = find_family(select_father,select_mother)
        else:
            type = "Partners"
            family = find_family(select_father,select_mother)
    else:    
        family = None

    family.setRelationship(type)

    change_family_type(family,mrel,frel)

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

    if active_person == Person.male:
        family.setMother(select_spouse)
        family.setFather(active_person)
    else:	
        family.setFather(select_spouse)
        family.setMother(active_person)

    family.setRelationship(const.save_frel(obj.get_data("d").get_text()))

    select_spouse = None
    utils.destroy_passed_object(obj)

    load_family()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_active_person(obj):
    if active_person:
        load_person(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_spouse_clicked(obj):
    if active_spouse:
        load_person(active_spouse)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_mother_clicked(obj):
    if active_mother:
        load_person(active_mother)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_father_clicked(obj):
    if active_father:
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

    topWindow.question(_("Do you really wish to delete %s?") % \
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
    spouseList = spouseDialog.get_widget("spouseList")
    spouseDialog.get_widget("rel_combo").set_popdown_strings(const.familyRelations)
    rel_type = spouseDialog.get_widget("rel_type")
    rel_type.set_data("d",spouseList)
    spouseDialog.get_widget("spouseDialog").set_data("d",rel_type)

    spouseDialog.signal_autoconnect({
        "on_spouseList_select_row" : on_spouseList_select_row,
        "on_select_spouse_clicked" : on_select_spouse_clicked,
        "on_rel_type_changed" : on_rel_type_changed,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    rel_type.set_text(_("Unknown"))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_rel_type_changed(obj):
	
    nameList = database.getPersonMap().values()
    nameList.sort(sort.by_last_name)
    spouse_list = obj.get_data("d")
    spouse_list.clear()
    spouse_list.freeze()
    text = obj.get_text()

    gender = active_person.getGender()
    if text == _("Partners"):
        if gender == Person.male:
            gender = Person.female
        else:
            gender = Person.male
	
    index = 0
    for person in nameList:
		
        if person.getGender() == gender:
            continue
        spouse_list.append([person.getPrimaryName().getName(),birthday(person)])
        spouse_list.set_row_data(index,person)
        index = index + 1
    spouse_list.thaw()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_parents_clicked(obj):
    if not active_parents:
        return

    active_parents.removeChild(active_person)
    
    if active_parents == active_person.getMainFamily():
        active_person.setMainFamily(None)
    else:
        active_person.removeAltFamily(active_parents)
    load_family()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def delete_spouse():
    import Check
    global active_family

    if active_person == active_family.getFather():
        person = active_family.getMother()
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
        active_family.setMother(None)

    load_family()
    utils.modified()

    checker = Check.CheckIntegrity(database)
    checker.cleanup_empty_families(1)
    checker.check_for_broken_family_links()
    
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

    nameArrow = gtop.get_widget("nameSort")
    dateArrow = gtop.get_widget("dateSort")
    deathArrow= gtop.get_widget("deathSort")
    
    if column == 0:
        dateArrow.hide()
        deathArrow.hide()
        nameArrow.show()
        if sortFunc != sort.fast_name_sort:
            sortFunc = sort.fast_name_sort
            nameArrow.set(GTK.ARROW_DOWN,2)
        else:
            sortFunc = sort.reverse_name_sort
            nameArrow.set(GTK.ARROW_UP,2)
    elif column == 3:
        nameArrow.hide()
        deathArrow.hide()
        dateArrow.show()
        if sortFunc != sort.fast_birth_sort:
            sortFunc = sort.fast_birth_sort
            dateArrow.set(GTK.ARROW_DOWN,2)
        else:
            sortFunc = sort.reverse_birth_sort
            dateArrow.set(GTK.ARROW_UP,2)
    elif column == 4:
        nameArrow.hide()
        deathArrow.show()
        dateArrow.hide()
        if sortFunc != sort.fast_death_sort:
            sortFunc = sort.fast_death_sort
            deathArrow.set(GTK.ARROW_DOWN,2)
        else:
            sortFunc = sort.reverse_death_sort
            deathArrow.set(GTK.ARROW_UP,2)
    else:
        return
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
    select_child_list[obj.get_row_data(a)] = 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_addChild_unselect_row(obj,a,b,c):
    del select_child_list[obj.get_row_data(a)]

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
    if active_person == None:
        statusbar.set_status("")
    else:
        pname = Config.nameof(active_person)
        if Config.status_bar == 1:
            name = "[%s] %s" % (active_person.getId(),pname)
        elif Config.status_bar == 2:
            name = pname
            for attr in active_person.getAttributeList():
                if attr.getType() == Config.attr_name:
                    name = "[%s] %s" % (attr.getValue(),pname)
                    break
        else:
            name = pname
        statusbar.set_status(name)
	
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
    fileSelector.set_filename(Config.db_dir)
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
        const.places = []
        const.personalEvents = const.initialize_personal_event_list()
        const.personalAttributes = const.initialize_personal_attribute_list()
        const.marriageEvents = const.initialize_marriage_event_list()
        const.familyAttributes = const.initialize_family_attribute_list()
        const.familyRelations = const.initialize_family_relation_list()

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
    notebk = gtop.get_widget(NOTEBOOK)
    notebk.set_page(0)

def on_family1_activate(obj):
    notebk = gtop.get_widget(NOTEBOOK)
    notebk.set_page(1)

def on_pedegree1_activate(obj):
    notebk = gtop.get_widget(NOTEBOOK)
    notebk.set_page(2)

def on_sources_activate(obj):
    notebk = gtop.get_widget(NOTEBOOK)
    notebk.set_page(3)

#-------------------------------------------------------------------------
#
# Load the appropriate page after a notebook switch
#
#-------------------------------------------------------------------------
def on_notebook1_switch_page(obj,junk,page):
    if not active_person:
        return
    if page == 0:
        if id2col.has_key(active_person):
            column = id2col[active_person]
            person_list.select_row(column,0)
            person_list.moveto(column,0)
    elif page == 1:
        load_family()
    elif page == 2:
        load_tree()
    elif page == 3:
        load_sources()
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_pv_button_press_event(obj,event):
    if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
        person = obj.get_data("p")
        if person == None:
            return
        load_person(person)

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
        spouse = gtop.get_widget("fv_spouse").get_menu().get_active().get_data("person")
    else:
        spouse = gtop.get_widget("fv_spouse1").get_data("person")

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

    invert_filter = gtop.get_widget("invert").get_active()
    qualifer = gtop.get_widget("filter").get_text()
    menu = gtop.get_widget(FILTERNAME).get_menu()
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
    gtop.get_widget("filter").set_sensitive(function())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_spouselist_changed(obj):
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
    if person == None:
        EditPerson.EditPerson(Person(),database,new_after_edit)
    else:
        EditPerson.EditPerson(person,database,update_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_family():
    global active_mother
    global active_parents
    global active_spouse
    
    family_types = []
    main_family = None

    gtop.get_widget("fv_person").set_text(Config.nameof(active_person))

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
            menuitem = GtkMenuItem("Birth")
            menuitem.set_data("parents",main_family)
            menuitem.connect("activate",on_current_type_changed)
            menuitem.show()
            typeMenu.append(menuitem)
        for fam in family_types:
            if active_person == fam[0].getFather():
                menuitem = GtkMenuItem("%s/%s" % (fam[1],fam[2]))
            else:
                menuitem = GtkMenuItem("%s/%s" % (fam[2],fam[1]))
            menuitem.set_data("parents",fam[0])
            menuitem.connect("activate",on_current_type_changed)
            menuitem.show()
            typeMenu.append(menuitem)
        gtop.get_widget("childtype").set_menu(typeMenu)
        gtop.get_widget("childtype").show()
    else:
        gtop.get_widget("childtype").hide()

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

                gtop.get_widget("fv_spouse").set_menu(myMenu)
            gtop.get_widget("lab_or_list").set_page(1)
            gtop.get_widget("edit_sp").set_sensitive(1)
            gtop.get_widget("delete_sp").set_sensitive(1)
        elif number_of_families == 1:
            gtop.get_widget("lab_or_list").set_page(0)
            family = active_person.getFamilyList()[0]
            if active_person != family.getFather():
                spouse = family.getFather()
            else:
                spouse = family.getMother()
            active_spouse = spouse
            fv_spouse1 = gtop.get_widget("fv_spouse1")
            fv_spouse1.set_text(Config.nameof(spouse))
            fv_spouse1.set_data("person",spouse)
            fv_spouse1.set_data("family",active_person.getFamilyList()[0])
            gtop.get_widget("edit_sp").set_sensitive(1)
            gtop.get_widget("delete_sp").set_sensitive(1)
        else:
            gtop.get_widget("lab_or_list").set_page(0)
            gtop.get_widget("fv_spouse1").set_text("")
            fv_spouse1 = gtop.get_widget("fv_spouse1")
            fv_spouse1.set_text("")
            fv_spouse1.set_data("person",None)
            fv_spouse1.set_data("family",None)
            active_spouse = None
            gtop.get_widget("edit_sp").set_sensitive(0)
            gtop.get_widget("delete_sp").set_sensitive(0)

        if number_of_families > 0:
            display_marriage(active_person.getFamilyList()[0])
        else:
            display_marriage(None)
    else:
        fv_spouse1 = gtop.get_widget("fv_spouse1").set_text("")
        display_marriage(None)
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def change_parents(family):
    global active_father
    global active_mother
    
    fn = _("Father")
    mn = _("Mother")

    if active_parents and active_parents.getRelationship() == "Partners":
        fn = _("Parent")
        mn = _("Parent")

    gtop.get_widget("editFather").children()[0].set_text(fn)
    gtop.get_widget("editMother").children()[0].set_text(mn)

    fv_father = gtop.get_widget("fv_father")
    fv_mother = gtop.get_widget("fv_mother")
    father_next = gtop.get_widget("father_next")
    mother_next = gtop.get_widget("mother_next")
    
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
        active_father = None
        active_mother = None
    else :
        fv_father.set_text("")
        fv_mother.set_text("")
        mother_next.set_sensitive(0)
        father_next.set_sensitive(0)
        active_father = None
        active_mother = None


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_tree():
    text = {}
    tip = {}
    for i in range(1,16):
        text[i] = ("",None)
        tip[i] = ""

    load_tree_values(active_person,1,16,text,tip)

    tips = GtkTooltips()
    for i in range(1,16):
        pv[i].set_text(text[i][0]) 
	pv[i].set_position(0)
        pv[i].set_data("p",text[i][1])
       
        if tip[i] != "":
            tips.set_tip(pv[i],tip[i])
        else:
            tips.set_tip(pv[i],None)

    if text[2] == "":
        gtop.get_widget("ped_father_next").set_sensitive(0)
    else:
        gtop.get_widget("ped_father_next").set_sensitive(1)

    if text[3] == "":
        gtop.get_widget("ped_mother_next").set_sensitive(0)
    else:
        gtop.get_widget("ped_mother_next").set_sensitive(1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_tree_values(person,index,max,pv_text,tip):
    if person == None:
        return
    msg = Config.nameof(person)
    
    bdate = person.getBirth().getDate()
    ddate = person.getDeath().getDate()
    if bdate and ddate:
        text = "%s\nb. %s\nd. %s" % (msg, bdate,ddate)
    elif bdate and not ddate:
        text = "%s\nb. %s" % (msg, bdate)
    elif not bdate and ddate:
        text = "%s\nb. %s" % (msg, ddate)
    else:
        text = msg
    tip[index] = text
    pv_text[index] = (msg,person)
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
    global active_spouse

    active_family = family
    clist = gtop.get_widget("child_list")
    fv_prev = gtop.get_widget("fv_prev")

    clist.clear()
    active_child = None
    active_fams = family

    i = 0
    if family != None:
        if active_person.getGender() == Person.male:
            active_spouse = family.getMother()
        else:
            active_spouse = family.getFather()
            
        child_list = family.getChildList()
        child_list.sort(sort.by_birthdate)
        attr = ""
        for child in child_list:
            status = _("Unknown")
            if child.getGender():
                gender = const.male
            else:
                gender = const.female
            if child.getMainFamily() == family:
                status = _("Birth")
            else:
                for fam in child.getAltFamilyList():
                    if fam[0] == family:
                        if active_person == family.getFather():
                            status = "%s/%s" % (_(fam[2]),_(fam[1]))
                        else:
                            status = "%s/%s" % (_(fam[1]),_(fam[2]))

            if Config.show_detail:
                attr = ""
                if child.getNote() != "":
                    attr = attr + "N"
                if len(child.getEventList())>0:
                    attr = attr + "E"
                if len(child.getAttributeList())>0:
                    attr = attr + "A"
                if len(child.getFamilyList()) > 0:
                    for f in child.getFamilyList():
                        if f.getFather() and f.getMother():
                            attr = attr + "M"
                            break
                if len(child.getPhotoList()) > 0:
                    attr = attr + "P"

            clist.append([Config.nameof(child),child.getId(),\
                          gender,birthday(child),status,attr])
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
        ntype = const.display_pevent(type)
        if ntype not in const.personalEvents:
            const.personalEvents.append(ntype)

    const.places = database.getPlaces()
    const.places.sort()
    
    mylist = database.getFamilyEventTypes()
    for type in mylist:
        ntype = const.display_fevent(type)
        if ntype not in const.marriageEvents:
            const.marriageEvents.append(ntype)

    mylist = database.getPersonAttributeTypes()
    for type in mylist:
        ntype = const.display_pattr(type)
        if ntype not in const.personalAttributes:
            const.personalAttributes.append(ntype)

    mylist = database.getFamilyAttributeTypes()
    for type in mylist:
        if type not in const.familyAttributes:
            const.familyAttributes.append(type)

    mylist = database.getFamilyRelationTypes()
    for type in mylist:
        if type not in const.familyRelations:
            const.familyRelations.append(type)

    Config.save_last_file(name)
    gtop.get_widget("filter").set_text("")
    active_person = database.getDefaultPerson()
    return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def setup_bookmarks():
    global bookmarks
    
    menu = gtop.get_widget("jump_to")
    person_map = database.getPersonMap()
    bookmarks = Bookmarks.Bookmarks(database.getBookmarks(),person_map,\
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
    altnames = []
    for person in people:
        names.append((person.getPrimaryName(),person,0))
        for name in person.getAlternateNames():
            altnames.append((name,person,1))

    if Config.hide_altnames == 0:
        names = names + altnames

    names = sortFunc(names)
    
    person_list.freeze()
    person_list.clear()

    color_clist = ListColors.ColorList(person_list,1)

    i=0

    datacomp = DataFilter.compare
    clistadd = color_clist.add_with_data
    gname = utils.phonebook_from_name

    person_list.set_column_visibility(1,Config.id_visible)
    
    for name_tuple in names:
        person = name_tuple[1]
        alt = name_tuple[2]
        name = name_tuple[0]
        
        if datacomp(person):
            if not alt:
                id2col[person] = i
            if person.getGender():
                gender = const.male
            else:
                gender = const.female
            bday = person.getBirth().getQuoteDate()
            dday = person.getDeath().getQuoteDate()
            clistadd([gname(name,alt),person.getId(), gender,bday, dday],\
                     person)
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
        topWindow.question(_("Do you wish to set %s as the home person?") % name, \
                           set_person)

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
    if active_person:
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
    global database, gtop
    global statusbar
    global person_list, source_list, pv
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

    gtop = libglade.GladeXML(const.gladeFile, "gramps")
    
    statusbar   = gtop.get_widget("statusbar")
    topWindow   = gtop.get_widget("gramps")
    person_list = gtop.get_widget("person_list")
    source_list = gtop.get_widget("source_list")
    filter_list = gtop.get_widget("filter_list")
    
    myMenu = GtkMenu()
    for filter in Filter.filterList:
        menuitem = GtkMenuItem(filter)
        myMenu.append(menuitem)
        menuitem.set_data("filter",Filter.filterMap[filter])
        menuitem.set_data("function",Filter.filterEnb[filter])
        menuitem.connect("activate",on_filter_name_changed)
        menuitem.show()
    filter_list.set_menu(myMenu)
    
    gtop.get_widget("filter").set_sensitive(0)

    # set the window icon 
    topWindow.set_icon(GtkPixmap(topWindow,const.logo))
    
    person_list.column_titles_active()

    for box in range(1,16):
        pv[box] = gtop.get_widget("pv%d" % box)

    gtop.signal_autoconnect({
        "on_about_activate": on_about_activate,
        "on_reports_clicked" : on_reports_clicked,
        "on_person_list1_activate": on_person_list1_activate,
        "on_family1_activate" : on_family1_activate,
        "on_sources_activate" : on_sources_activate,
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
        "on_delete_parents_clicked" : on_delete_parents_clicked,
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
        "on_edit_sp_clicked" : on_edit_sp_clicked,
        "on_add_sp_clicked" : on_add_sp_clicked,
        "on_delete_sp_clicked" : on_delete_sp_clicked,
        "on_remove_child_clicked" : on_remove_child_clicked,
        "on_new_clicked" : on_new_clicked,
        "on_add_bookmark_activate" : on_add_bookmark_activate,
        "on_arrow_left_clicked" : on_arrow_left_clicked,
        "on_addperson_clicked" : on_addperson_clicked,
        "on_delete_person_clicked" : on_delete_person_clicked,
        "on_preferences_activate" : on_preferences_activate,
        "on_pv_button_press_event" : on_pv_button_press_event,
        "on_edit_bookmarks_activate" : on_edit_bookmarks_activate,
        "on_edit_active_person" : on_edit_active_person,
        "on_edit_spouse_clicked" : on_edit_spouse_clicked,
        "on_edit_father_clicked" : on_edit_father_clicked,
        "on_edit_mother_clicked" : on_edit_mother_clicked,
        "on_exit_activate" : on_exit_activate,
        "on_statusbar_unmap" : on_statusbar_unmap,
        "on_add_source_clicked" : on_add_source_clicked,
        "on_source_list_button_press_event" : on_source_list_button_press_event,
        "on_source_list_select_row": on_source_list_select_row,
        "on_delete_source_clicked" : on_delete_source_clicked,
        "on_edit_source_clicked" : on_edit_source_clicked,
        "delete_event" : delete_event,
        "on_open_activate" : on_open_activate
        })	

    database = RelDataBase()
    Config.loadConfig(full_update)
    person_list.set_column_visibility(1,Config.id_visible)
    gtop.get_widget(NOTEBOOK).set_show_tabs(Config.usetabs)
    gtop.get_widget("child_list").set_column_visibility(4,Config.show_detail)
        
    if arg != None:
        read_file(arg)
    elif Config.lastfile != None and Config.lastfile != "" and Config.autoload:
        read_file(Config.lastfile)

    gtop.get_widget("export1").set_submenu(Plugins.export_menu(export_callback))
    gtop.get_widget("import1").set_submenu(Plugins.import_menu(import_callback))

    database.setResearcher(Config.owner)
    mainloop()

#-------------------------------------------------------------------------
#
# Start it all
#
#-------------------------------------------------------------------------
if __name__ == '__main__':
    main(None)
    
