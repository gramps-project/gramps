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
import string
import os

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
import intl
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

import ReadXML
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
import EditPlace
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
childWindow   = None
new_child_win = None
add_child_win = None
bookmarks     = None

id2col        = {}
alt2col       = {}

topWindow     = None
statusbar     = None
gtop          = None
notebook      = None
person_list   = None
source_list   = None
place_list    = None
database      = None
family_window = None
pv            = {}
sort_column   = 5
sort_direct   = SORT_ASCENDING
DataFilter    = Filter.Filter("")

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

NOTEBOOK    = "notebook1"
FILESEL     = "fileselection"
FILTERNAME  = "filter_list"
ODDFGCOLOR  = "oddForeground"
ODDBGCOLOR  = "oddBackground"
EVENFGCOLOR = "evenForeground"
EVENBGCOLOR = "evenBackground"
GIVEN       = "g"
SURNAME     = "s"
RELTYPE     = "d"
PAD         = 3

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
    if len(active_family.getChildList()) == 0:
        if active_family.getFather() == None:
            delete_family_from(active_family.getMother())
        elif active_family.getMother() == None:
            delete_family_from(active_family.getFather())

    utils.modified()
    load_family()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def delete_family_from(person):
    global active_family

    person.removeFamily(active_family)
    database.deleteFamily(active_family)
    flist = active_person.getFamilyList()
    if len(flist) > 0:
        active_family = flist[0]
    else:
        active_family = None

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_add_sp_clicked(obj):
    dialog = libglade.GladeXML(const.gladeFile, "spouseDialog")
    dialog.get_widget("rel_combo").set_popdown_strings(const.familyRelations)

    rel_type = dialog.get_widget("rel_type")
    rel_type.set_data("d", dialog.get_widget("spouseList"))
    rel_type.set_data("x", dialog.get_widget("reldef"))

    top = dialog.get_widget("spouseDialog")
    top.set_data(RELTYPE,rel_type)
    top.set_data(GIVEN,dialog.get_widget("given"))
    top.set_data(SURNAME,dialog.get_widget("surname"))

    dialog.signal_autoconnect({
        "on_spouseList_select_row" : on_spouse_list_select_row,
        "on_select_spouse_clicked" : on_select_spouse_clicked,
        "on_new_spouse_clicked"    : on_new_spouse_clicked,
        "on_rel_type_changed"      : on_rel_type_changed,
        "destroy_passed_object"    : utils.destroy_passed_object
        })

    rel_type.set_text(_("Married"))

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_edit_sp_clicked(obj):
    Marriage.Marriage(active_family,database)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_delete_sp_clicked(obj):
    global active_family

    if active_person == active_family.getFather():
        person = active_family.getMother()
        active_family.setMother(None)
    else:
        person = active_family.getFather()
        active_family.setFather(None)

    if person:
        person.removeFamily(active_family)
    
    if len(active_family.getChildList()) == 0:
        active_person.removeFamily(active_family)
        database.deleteFamily(active_family)
        if len(active_person.getFamilyList()) > 0:
            active_family = active_person.getFamilyIndex(0)
        else:
            active_family = None

    load_family()
    utils.modified()
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_add_child_clicked(obj):
    global add_child_win
    global childWindow
    global select_child_list
    
    childWindow = libglade.GladeXML(const.gladeFile,"selectChild")
    
    childWindow.signal_autoconnect({
        "on_save_child_clicked"    : on_save_child_clicked,
        "on_addChild_select_row"   : on_add_child_select_row,
        "on_addChild_unselect_row" : on_add_child_unselect_row,
        "on_show_toggled"          : on_show_toggled,
        "destroy_passed_object"    : utils.destroy_passed_object
        })

    select_child_list = {}
    selectChild = childWindow.get_widget("selectChild")
    add_child_win = childWindow.get_widget("addChild")
    add_child_win.set_column_visibility(1,Config.id_visible)

    father = active_family.getFather()
    if father != None:
        fname = father.getPrimaryName().getName()
        ftitle = _("Relationship to %s") % fname
        childWindow.get_widget("flabel").set_text(ftitle)

    mother = active_family.getMother()
    if mother != None:
        mname = mother.getPrimaryName().getName()
        mtitle = _("Relationship to %s") % mname
        childWindow.get_widget("mlabel").set_text(mtitle)

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
    add_child_win.freeze()
    add_child_win.clear()
    index = 0

    bday = active_person.getBirth().getDateObj()
    dday = active_person.getDeath().getDateObj()

    bday_valid = (bday.getYear() != -1)
    dday_valid = (dday.getYear() != -1)
    
    slist = []
    for f in [active_person.getMainFamily()] + active_person.getFamilyList():
        if f:
            if f.getFather():
                slist.append(f.getFather())
            elif f.getMother():
                slist.append(f.getMother())
            for c in f.getChildList():
                slist.append(c)
            
    for person in person_list:
        if filter:
            if person in slist:
                continue
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
                    if pdday.getLowYear() < bday.getHighYear()+10:
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
        
        add_child_win.append([utils.phonebook_name(person),birthday(person),\
                              person.getId()])
        add_child_win.set_row_data(index,person)
        index = index + 1
    add_child_win.thaw()

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
    global new_child_win
    
    new_child_win = libglade.GladeXML(const.gladeFile,"addChild")
    new_child_win.signal_autoconnect({
        "on_addchild_ok_clicked" : on_addchild_ok_clicked,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    if active_person.getGender() == Person.male:
        surname = active_person.getPrimaryName().getSurname()
    elif active_spouse:
        surname = active_spouse.getPrimaryName().getSurname()
    else:
        surname = ""

    if active_family:
        father = active_family.getFather()
        if father != None:
            fname = father.getPrimaryName().getName()
            label = _("Relationship to %s") % fname
            new_child_win.get_widget("flabel").set_text(label)

        mother = active_family.getMother()
        if mother != None:
            mname = mother.getPrimaryName().getName()
            label = _("Relationship to %s") % mname
            new_child_win.get_widget("mlabel").set_text(label)
    else:
        fname = active_person.getPrimaryName().getName()
        label = _("Relationship to %s") % fname
        if active_person.getGender() == Person.male:
            new_child_win.get_widget("flabel").set_text(label)
            new_child_win.get_widget("mcombo").set_sensitive(0)
        else:
            new_child_win.get_widget("mlabel").set_text(label)
            new_child_win.get_widget("fcombo").set_sensitive(0)

    new_child_win.get_widget("childSurname").set_text(surname)
    new_child_win.get_widget("addChild").show()
    new_child_win.get_widget("mrel").set_text(_("Birth"))
    new_child_win.get_widget("frel").set_text(_("Birth"))

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_addchild_ok_clicked(obj):
    global active_family
    
    surname = new_child_win.get_widget("childSurname").get_text()
    given = new_child_win.get_widget("childGiven").get_text()
    
    person = Person()
    database.addPerson(person)

    name = Name()
    name.setSurname(surname)
    name.setFirstName(given)
    person.setPrimaryName(name)

    if new_child_win.get_widget("childGender").get_active():
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

    mrel = const.childRelations[new_child_win.get_widget("mrel").get_text()]
    frel = const.childRelations[new_child_win.get_widget("frel").get_text()]

    if mrel == "Birth" and frel == "Birth":
        person.setMainFamily(active_family)
    else:
        person.addAltFamily(active_family,mrel,frel)

    active_family.addChild(person)
        
    # must do an apply filter here to make sure the main window gets updated
    
    redisplay_person_list(person)
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
            family_window.get_widget("mrel").set_text(_("Birth"))
            family_window.get_widget("frel").set_text(_("Birth"))

    fcombo = family_window.get_widget("prel_combo")
    prel = family_window.get_widget("prel")
            
    prel.set_data("o",family_window)
    fcombo.set_popdown_strings(const.familyRelations)

    family_window.signal_autoconnect({
        "on_motherList_select_row" : on_mother_list_select_row,
        "on_fatherList_select_row" : on_father_list_select_row,
        "on_save_parents_clicked" : on_save_parents_clicked,
        "on_prel_changed" : on_prel_changed,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    text = _("Choose the Parents of %s") % Config.nameof(active_person)
    family_window.get_widget("chooseTitle").set_text(text)
    if active_parents:
        prel.set_text(active_parents.getRelationship())
    else:
        on_prel_changed(prel)
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

    father_list = family_window.get_widget("fatherList")
    mother_list = family_window.get_widget("motherList")

    father_list.freeze()
    mother_list.freeze()
    father_list.clear()
    mother_list.clear()

    father_list.append(["Unknown",""])
    father_list.set_row_data(0,None)
    father_list.set_data("father_text",fatherName)

    mother_list.append(["Unknown",""])
    mother_list.set_row_data(0,None)
    mother_list.set_data("mother_text",motherName)

    people = database.getPersonMap().values()
    people.sort(sort.by_last_name)
    father_index = 1
    mother_index = 1
    for person in people:
        if person == active_person:
            continue
        elif type == "Partners":
            father_list.append([utils.phonebook_name(person),birthday(person)])
            father_list.set_row_data(father_index,person)
            father_index = father_index + 1
            mother_list.append([utils.phonebook_name(person),birthday(person)])
            mother_list.set_row_data(mother_index,person)
            mother_index = mother_index + 1
        elif person.getGender() == Person.male:
            father_list.append([utils.phonebook_name(person),birthday(person)])
            father_list.set_row_data(father_index,person)
            father_index = father_index + 1
        else:
            mother_list.append([utils.phonebook_name(person),birthday(person)])
            mother_list.set_row_data(mother_index,person)
            mother_index = mother_index + 1

    if type == "Partners":
        family_window.get_widget("mlabel").set_text(_("Parent"))
        family_window.get_widget("flabel").set_text(_("Parent"))
    else:
        family_window.get_widget("mlabel").set_text(_("Mother"))
        family_window.get_widget("flabel").set_text(_("Father"))

    mother_list.thaw()
    father_list.thaw()

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
    global id2col,alt2col,person_list

    if val == 1:
        return

    const.personalEvents = const.initialize_personal_event_list()
    const.personalAttributes = const.initialize_personal_attribute_list()
    const.marriageEvents = const.initialize_marriage_event_list()
    const.familyAttributes = const.initialize_family_attribute_list()
    const.familyRelations = const.initialize_family_relation_list()
    
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
    alt2col       = {}

    utils.clearModified()
    change_active_person(None)
    person_list.clear()
    load_family()
    load_sources()
    load_places()
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def tool_callback(val):
    if val:
        utils.modified()
        full_update()
        
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def full_update():
    global id2col
    global alt2col
    
    id2col = {}
    alt2col = {}
    person_list.clear()
    notebook.set_show_tabs(Config.usetabs)
    clist = gtop.get_widget("child_list")
    clist.set_column_visibility(4,Config.show_detail)
    clist.set_column_visibility(1,Config.id_visible)
    apply_filter()
    load_family()
    load_sources()
    load_places()
    load_tree()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def update_display(changed):
    page = notebook.get_current_page()
    if page == 0:
        if changed:
            apply_filter()
        else:
            goto_active_person()
    elif page == 1:
        load_family()
    elif page == 2:
        load_sources()
    elif page == 3:
        load_tree()
    else:
        load_places()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def load_sources():
    source_list.clear()
    source_list.freeze()

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
        source_list.moveto(current_row)

    source_list.set_data("i",current_row)
    source_list.thaw()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_src_list_button_press_event(obj,event):
    if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
        index = obj.get_data("i")
        if index >= 0:
            source = obj.get_row_data(index)
            EditSource.EditSource(source,database,update_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_place_list_button_press_event(obj,event):
    if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
        index = obj.get_data("i")
        if index >= 0:
            place = obj.get_row_data(index)
            EditPlace.EditPlace(place,database,update_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_list_select_row(obj,a,b,c):
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
def on_add_place_clicked(obj):
    EditPlace.EditPlace(Place(),database,new_place_after_edit)

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
def on_delete_place_clicked(obj):
    global pevent
    global fevent
    
    index = obj.get_data("i")
    if index == -1:
        return

    pevent = []
    fevent = []
    place = obj.get_row_data(index)
    for p in database.getPersonMap().values():
        for event in [p.getBirth(), p.getDeath()] + p.getEventList():
            if event.getPlace() == place:
                pevent.append(p,event)
    for f in database.getFamilyMap().values():
        for event in f.getEventList():
            if event.getPlace() == place:
                fevent.append(f,event)

    if len(pevent) > 0 or len(fevent) > 0:
        msg = []
        ptop = libglade.GladeXML(const.gladeFile,"place_query")
        ptop.signal_autoconnect({
            'on_force_delete_clicked': on_force_delete_clicked,
            'destroy_passed_object' : utils.destroy_passed_object}) 
        
        fd = ptop.get_widget("place_query")
        fd.set_data("p",pevent)
        fd.set_data("f",fevent)
        fd.set_data("place",place)
        
        textbox = ptop.get_widget("text")
        textbox.set_point(0)
        textbox.set_word_wrap(1)

        if len(pevent) > 0:
            textbox.insert_defaults(_("People") + "\n")
            textbox.insert_defaults("_________________________\n\n")
            t = _("%s [%s]: event %s\n")

            for e in pevent:
                msg = t % (Config.nameof(e[0]),e[0].getId(),e[1].getName())
                textbox.insert_defaults(msg)

        if len(fevent) > 0:
            textbox.insert_defaults("\n%s\n" % _("Families"))
            textbox.insert_defaults("_________________________\n\n")
            t = _("%s [%s]: event %s\n")

            for e in fevent:
                father = e[0].getFather()
                mother = e[0].getMother()
                if father and mother:
                    fname = "%s and %s" % (Config.nameof(father),Config.nameof(mother))
                elif father:
                    fname = "%s" % Config.nameof(father)
                else:
                    fname = "%s" % Config.nameof(mother)

                msg = t % (fname,e[0].getId(),e[1].getName())
                textbox.insert_defaults(msg)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_force_delete_clicked(obj):
    place = obj.get_data('place')
    plist = obj.get_data('p')
    flist = obj.get_data('f')

    for event in plist + flist:
        event[1].setPlace(None)
    map = database.getPlaceMap()
    del map[place.getId()]
    utils.modified()
    utils.destroy_passed_object(obj)
    update_display(0)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_source_clicked(obj):
    index = obj.get_data("i")
    if index != -1:
        source = obj.get_row_data(index)
        EditSource.EditSource(source,database,update_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_place_clicked(obj):
    index = obj.get_data("i")
    if index != -1:
        place = obj.get_row_data(index)
        EditPlace.EditPlace(place,database,update_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def new_source_after_edit(source):
    database.addSource(source)
    update_display(0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def new_place_after_edit(place):
    database.addPlace(place)
    update_display(0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def update_after_edit(source):
    update_display(0)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_tools_clicked(obj):
    if active_person:
        Plugins.ToolPlugins(database,active_person,tool_callback)

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

    active_person = None
    for person in database.getPersonMap().values():
        if active_person == None:
            active_person = person
        lastname = person.getPrimaryName().getSurname()
        if lastname and lastname not in const.surnames:
            const.surnames.append(lastname)
            
    statusbar.set_progress(1.0)
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

    database.setSavePath(old_file)
    utils.clearModified()
    Config.save_last_file(old_file)
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

    is_main = (mrel == "Birth") and (frel == "Birth")
    
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
        family.addChild(active_person)
        if not is_main:
            utils.modified()
            active_person.setMainFamily(None)
            for fam in active_person.getAltFamilyList():
                if fam[0] == family:
                    fam[1] = type
                    break
                elif fam[1] == type:
                    fam[0] = family
                    break
            else:
                active_person.addAltFamily(family,mrel,frel)
    else:
        family.addChild(active_person)
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
            if is_main:
                active_person.setMainFamily(family)
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
    type = const.save_frel(type)
    
    if select_father or select_mother:
        if select_mother and not select_father:
            if select_mother.getGender() == Person.male:
                select_father = select_mother
                select_mother = None
            family = find_family(select_father,select_mother)
        elif select_father and not select_mother: 
            if select_father.getGender() == Person.female:
                select_mother = select_father
                select_father = None
            family = find_family(select_father,select_mother)
        elif select_mother.getGender() != select_father.getGender():
            if type == "Partners":
                type = "Unknown"
            if select_father.getGender() == Person.female:
                x = select_father
                select_father = select_mother
                select_mother = x
            family = find_family(select_father,select_mother)
        else:
            type = "Partners"
            family = find_family(select_father,select_mother)
    else:    
        family = None

    active_mother = select_mother
    active_father = select_father
    active_family = family

    utils.destroy_passed_object(obj)
    if family:
        family.setRelationship(type)

    change_family_type(family,mrel,frel)
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
def on_new_spouse_clicked(obj):
    global active_spouse
    global select_spouse
    global active_family

    select_spouse = Person()
    database.addPerson(select_spouse)
    name = Name()
    select_spouse.setPrimaryName(name)
    name.setSurname(string.strip(obj.get_data(SURNAME).get_text()))
    name.setFirstName(string.strip(obj.get_data(GIVEN).get_text()))

    reltype = const.save_frel(obj.get_data(RELTYPE).get_text())
    if reltype == "Partners":
        select_spouse.setGender(active_person.getGender())
    else:
        if active_person.getGender() == Person.male:
            select_spouse.setGender(Person.female)
        else:
            select_spouse.setGender(Person.male)

    utils.modified()
    active_spouse = select_spouse

    family = database.newFamily()
    active_family = family

    active_person.addFamily(family)
    select_spouse.addFamily(family)

    if active_person.getGender() == Person.male:
        family.setMother(select_spouse)
        family.setFather(active_person)
    else:	
        family.setFather(select_spouse)
        family.setMother(active_person)

    family.setRelationship(const.save_frel(obj.get_data("d").get_text()))

    select_spouse = None
    utils.destroy_passed_object(obj)

    redisplay_person_list(active_spouse)
    load_family()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_active_person(obj):
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
def load_new_person(obj):
    EditPerson.EditPerson(Person(),database,new_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_person_clicked(obj):
    if active_person:
        msg = _("Do you really wish to delete %s?") % Config.nameof(active_person)
        topWindow.question( msg, delete_person_response)

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
    remove_from_person_list(active_person)
    person_list.sort()
    update_display(0)
    utils.modified()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def remove_from_person_list(person):
    person_list.freeze()
    if id2col.has_key(person):
        for id in [id2col[person]] + alt2col[person]:
            row = person_list.find_row_from_data(id)
            person_list.remove(row)

        del id2col[person]
        del alt2col[person]
    person_list.thaw()
    
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
    deftxt = obj.get_data("x")
    text = obj.get_text()

    deftxt.set_text(const.relationship_def(text))
    
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
def on_person_list_select_row(obj,a,b,c):
    person,alt = obj.get_row_data(a)
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
    if column == 0:
        change_sort(5,gtop.get_widget("nameSort"))
    elif column == 3:
        change_sort(6,gtop.get_widget("dateSort"))
    elif column == 4:
        change_sort(7,gtop.get_widget("deathSort"))
    else:
        return

    sort_person_list()
    if id2col.has_key(active_person):
        row = person_list.find_row_from_data(id2col[active_person])
        person_list.moveto(row)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def change_sort(column,arrow):
    global sort_direct
    global sort_column

    nameArrow.hide()
    deathArrow.hide()
    dateArrow.hide()
    arrow.show()
    
    if sort_column == column:
        if sort_direct == SORT_DESCENDING:
            sort_direct = SORT_ASCENDING
            arrow.set(GTK.ARROW_DOWN,2)
        else:
            sort_direct = SORT_DESCENDING
            arrow.set(GTK.ARROW_UP,2)
    else:
        sort_direct = SORT_ASCENDING
    sort_column = column
    person_list.set_sort_type(sort_direct)
    person_list.set_sort_column(sort_column)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def sort_person_list():
    person_list.freeze()
    person_list.sort()
    if ListColors.get_enable():
        try:
            oddbg = GdkColor(ListColors.oddbg[0],ListColors.oddbg[1],ListColors.oddbg[2])
            oddfg = GdkColor(ListColors.oddfg[0],ListColors.oddfg[1],ListColors.oddfg[2])
            evenbg = GdkColor(ListColors.evenbg[0],ListColors.evenbg[1],ListColors.evenbg[2])
            evenfg = GdkColor(ListColors.evenfg[0],ListColors.evenfg[1],ListColors.evenfg[2])
            rows = person_list.rows
            for i in range(0,rows,2):
                person_list.set_background(i,oddbg)
                person_list.set_foreground(i,oddfg)
                if i != rows:
                    person_list.set_background(i+1,evenbg)
                    person_list.set_foreground(i+1,evenfg)
        except OverflowError:
            pass
    goto_active_person()
    person_list.thaw()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_father_list_select_row(obj,a,b,c):
    global select_father
	
    select_father = obj.get_row_data(a)
    obj.get_data("father_text").set_text(Config.nameof(select_father))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_child_select_row(obj,row,b,c):
    select_child_list[obj.get_row_data(row)] = 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_child_unselect_row(obj,row,b,c):
    del select_child_list[obj.get_row_data(row)]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_mother_list_select_row(obj,a,b,c):
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
def on_child_list_select_row(obj,row,b,c):
    global active_child
    active_child = obj.get_row_data(row)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_spouse_list_select_row(obj,row,b,c):
    global select_spouse
    select_spouse = obj.get_row_data(row)

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
    notebook.set_page(0)

def on_family1_activate(obj):
    notebook.set_page(1)

def on_pedegree1_activate(obj):
    notebook.set_page(2)

def on_sources_activate(obj):
    notebook.set_page(3)

def on_places_activate(obj):
    notebook.set_page(4)

#-------------------------------------------------------------------------
#
# Load the appropriate page after a notebook switch
#
#-------------------------------------------------------------------------
def on_notebook1_switch_page(obj,junk,page):
    if not active_person:
        return
    if page == 0:
        goto_active_person()
    elif page == 1:
        load_family()
    elif page == 2:
        load_tree()
    elif page == 3:
        load_sources()
    elif page == 4:
        load_places()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_places():
    place_list.freeze()
    place_list.clear()

    current_row = place_list.get_data("i")
    if current_row == None:
        current_row = -1

    index = 0
    places = database.getPlaceMap().values()
    
    for src in places:
        title = src.get_title()
        id = src.getId()
        mloc = src.get_main_location()
        city = mloc.get_city()
        county = mloc.get_county()
        state = mloc.get_state()
        country = mloc.get_country()
        place_list.append([title,id,city,county,state,country])
        place_list.set_row_data(index,src)
        index = index + 1

    place_list.sort()

    if index > 0:
        if current_row == -1:
            current_row = 0
        place_list.select_row(current_row,0)
        place_list.moveto(current_row)

    place_list.set_data("i",current_row)
    place_list.thaw()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_pv_button_press_event(obj,event):
    if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
        load_person(obj.get_data("p"))

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
def childmenu (obj,event):
    if not active_person:
        return 1
    
    if event.type == GDK.BUTTON_PRESS and event.button == 3:
        myMenu = GtkMenu()
        for family in active_person.getFamilyList():
            for child in family.getChildList():
                menuitem = GtkMenuItem(Config.nameof(child))
                myMenu.append(menuitem)
                menuitem.set_data("person",child)
                menuitem.connect("activate",on_childmenu_changed)
                menuitem.show()
        myMenu.popup(None,None,None,0,0)
    elif event.type == GDK.ENTER_NOTIFY:
        statusbar.set_status(_("Right clicking will allow you to choose a child"))
        style = gtop.get_widget("canvas1")['style']
        obj.set(fill_color=style.fg[STATE_SELECTED])
    elif event.type == GDK.LEAVE_NOTIFY:
        style = gtop.get_widget("canvas1")['style']
        obj.set(fill_color=style.black)
        modify_statusbar()
    return 1

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
    return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_childmenu_changed(obj):
    person = obj.get_data("person")
    if person:
        change_active_person(person)
        load_tree()
    return 1
    
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

    if spouse:
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
    class_init = menu.get_active().get_data("filter")
    DataFilter = class_init(qualifer)
    DataFilter.set_invert(invert_filter)
    apply_filter()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_filter_name_changed(obj):
    gtop.get_widget("filter").set_sensitive(obj.get_data("qual"))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_spouselist_changed(obj):
    if active_person:
        display_marriage(obj.get_data("family"))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def new_after_edit(epo):
    database.addPerson(epo.person)
    redisplay_person_list(epo.person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def update_after_edit(epo):
    remove_from_person_list(epo.person)
    redisplay_person_list(epo.person)
    update_display(0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def redisplay_person_list(person):
    pos = (person,0)
    id2col[person] = pos
    alt2col[person] = []
    gname = utils.phonebook_from_name
    if DataFilter.compare(person):
        if person.getGender():
            gender = const.male
        else:
            gender = const.female
        bday = person.getBirth().getDateObj()
        dday = person.getDeath().getDateObj()
        name = person.getPrimaryName()
        person_list.insert(0,[gname(name,0),person.getId(),
                              gender,bday.getQuoteDate(),
                              dday.getQuoteDate(),
                              sort.build_sort_name(name),
                              sort.build_sort_birth(bday),
                              sort.build_sort_death(dday)])

        person_list.set_row_data(0,pos)

        if Config.hide_altnames == 0:
            for name in person.getAlternateNames():
                pos2 = (person,1)
                alt2col[person].append(pos2)
                person_list.insert(0,[gname(name,1),person.getId(),
                                      gender,bday.getQuoteDate(),
                                      dday.getQuoteDate(),
                                      sort.build_sort_name(name),
                                      sort.build_sort_birth(bday),
                                      sort.build_sort_death(dday)])

                person_list.set_row_data(0,pos2)

        sort_person_list()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_person(person):
    if person:
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

def find_tree(person,index,depth,list):

    if depth > 5 or person == None:
        return
    family = person.getMainFamily()
    list[index] = person
    if family != None:
        father = family.getFather()
        if father != None:
            find_tree(father,(2*index)+1,depth+1,list)
        mother = family.getMother()
        if mother != None:
            find_tree(mother,(2*index)+2,depth+1,list)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
canvas_items = []
old_gen = 0
old_h = 0
old_w = 0

def load_canvas():
    global canvas_items
    global old_gen,old_h,old_w

    if active_person == None:
        return
    
    h = 0
    w = 0
    xpad = 15

    canvas = gtop.get_widget("canvas1")
    cx1,cy1,cx2,cy2 = canvas.get_allocation()
    root = canvas.root()

    cw = (cx2-cx1-(2*xpad))

    style = canvas['style']
    font = style.font

    list = [None]*31
    find_tree(active_person,0,1,list)
    for t in list:
        if t:
            n = t.getPrimaryName().getName()
            h = max(h,font.height(n)+2*PAD)
            w = max(w,font.width(n)+2*PAD)
            w = max(w,font.width("d. %s" % t.getDeath().getDate())+2*PAD)
            w = max(w,font.width("b. %s" % t.getBirth().getDate())+2*PAD)

    if 5*w < cw and 24*h < cy2:
        gen = 31
        xdiv = 5.0
    elif 4*w < cw and 12*h < cy2:
        gen = 15
        xdiv = 4.0
    else:
        gen = 7
        xdiv = 3.0

    for c in canvas_items:
        c.destroy()
    canvas.set_scroll_region(cx1,cy1,cx2,cy2)

    xincr = cw/xdiv
    yincr = cy2/32

    xfactor = [xpad] + [xincr+xpad]*2 + [xincr*2+xpad]*4 + [xincr*3+xpad]*8 + [xincr*4+xpad]*16
    yfactor = [ yincr*16, yincr*8,yincr*24,yincr*4,yincr*12,yincr*20, yincr*28,
                yincr*2, yincr*6,yincr*10,yincr*14,yincr*18,yincr*22,yincr*26,
                yincr*30, yincr, yincr*3, yincr*5, yincr*7, yincr*9, yincr*11,
                yincr*13, yincr*15, yincr*17, yincr*19, yincr*21, yincr*23,
                yincr*25, yincr*27, yincr*29, yincr*31]


    if len(active_person.getFamilyList()) > 0:
        ypos = yfactor[0]+h/2.0
        item = root.add("line",
                        points=[xpad,ypos,xpad/4.0,ypos],
                        fill_color_gdk=style.black,
                        width_pixels=3,
                        arrow_shape_a=6,
                        arrow_shape_b=6,
                        arrow_shape_c=4,
                        last_arrowhead=1
                        )
        item.connect('event',childmenu)
        canvas_items = [item]
    else:
        canvas_items = []

    for i in range(gen):
        if list[i]:
            if i < int(gen/2):
                startx = xfactor[i]+(w/2)
                if list[(2*i)+1]:
                    pts = [startx,yfactor[i],
                           startx,yfactor[(i*2)+1]+(h/2),
                           xfactor[(i*2)+1],yfactor[(i*2)+1]+(h/2)]
                    item = root.add("line",
                                    width_pixels=2,
                                    points=pts,
                                    fill_color_gdk=style.black)
                    item.set_data("p",list[(2*i)+1])
                    item.connect("event",line_event)
                    canvas_items.append(item)
                if list[(2*i)+2]:
                    pts = [startx,yfactor[i]+h,
                           startx,yfactor[(i*2)+2]+(h/2),
                           xfactor[(i*2)+2],yfactor[(i*2)+2]+(h/2)]
                    item = root.add("line",
                                    points=pts,
                                    width_pixels=2,
                                    fill_color_gdk=style.black)
                    item.set_data("p",list[(2*i)+2])
                    item.connect("event",line_event)
                    canvas_items.append(item)
            add_box(root,xfactor[i],yfactor[i],w,h,list[i],style)
                    
    old_gen = gen
    old_h = h
    old_w = w

    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_box(root,x,y,bwidth,bheight,person,style):
    shadow = PAD
    xpad = PAD

    name = person.getPrimaryName().getName()
    group = root.add("group",x=x,y=y)
    canvas_items.append(group)
    item = group.add("rect",
                     x1=shadow,
                     y1=shadow,
                     x2=bwidth+shadow,
                     y2=bheight+shadow,
                     outline_color_gdk=style.dark[STATE_NORMAL],
                     fill_color_gdk=style.dark[STATE_NORMAL])
    canvas_items.append(item)
    item = group.add("rect",
                     x1=0,
                     y1=0,
                     x2=bwidth,
                     y2=bheight,
                     outline_color_gdk=style.fg[STATE_NORMAL],
                     fill_color_gdk=style.white)
    canvas_items.append(item)
    item = group.add("text",
                     x=xpad,
                     y=bheight/2.0,
                     fill_color_gdk=style.text[STATE_NORMAL],
                     font_gdk=style.font,
                     text=name,
                     anchor=ANCHOR_WEST)
    canvas_items.append(item)
    group.connect('event',box_event)
    group.set_data('p',person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def box_event(obj,event):
    if event.type == GDK._2BUTTON_PRESS:
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            load_person(obj.get_data('p'))
    elif event.type == GDK.ENTER_NOTIFY:
        canvas = gtop.get_widget("canvas1")
        obj.raise_to_top()
        box = obj.children()[1]
        x,y,w,h = box.get_bounds()
        box.set(x1=x,y1=y,x2=w,y2=h*3,
                outline_color_gdk=canvas['style'].black)
        box2 = obj.children()[0]
        x,y,w,h1 = box2.get_bounds()
        box2.set(x1=x,y1=y,x2=w,y2=(3*h)+PAD)
        person = obj.get_data('p')
        obj.add("text",
                font_gdk=canvas['style'].font,
                fill_color_gdk=canvas['style'].text[STATE_NORMAL],
                text="b. %s" % person.getBirth().getDate(),
                anchor=ANCHOR_WEST,
                x=PAD,
                y=h+(h/2))
        obj.add("text",
                font_gdk=canvas['style'].font,
                fill_color_gdk=canvas['style'].text[STATE_NORMAL],
                text="d. %s" % person.getDeath().getDate(),
                anchor=ANCHOR_WEST,
                x=PAD,
                y=2*h+(h/2))
    elif event.type == GDK.LEAVE_NOTIFY:
        canvas = gtop.get_widget("canvas1")
        box = obj.children()[1]
        x,y,w,h = box.get_bounds()
        box.set(x1=x,y1=y,x2=w,y2=h/3,
                outline_color_gdk=canvas['style'].fg[STATE_NORMAL])
        box2 = obj.children()[0]
        x,y,w,h1 = box2.get_bounds()
        box2.set(x1=x,y1=y,x2=w,y2=(h/3)+PAD)
        obj.children()[4].destroy()
        obj.children()[3].destroy()
        canvas.update_now()
    return 1
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def line_event(obj,event):
    if event.type == GDK._2BUTTON_PRESS:
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            change_active_person(obj.get_data("p"))
            load_canvas()
    elif event.type == GDK.ENTER_NOTIFY:
        canvas = gtop.get_widget("canvas1")
        obj.set(fill_color_gdk=canvas['style'].bg[STATE_SELECTED])
        name = Config.nameof(obj.get_data("p"))
        msg = _("Double clicking will make %s the active person") % name
        statusbar.set_status(msg)
    elif event.type == GDK.LEAVE_NOTIFY:
        canvas = gtop.get_widget("canvas1")
        obj.set(fill_color_gdk=canvas['style'].black)
        modify_statusbar()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_tree():

    load_canvas()
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
    statusbar.set_progress(value)
    while events_pending():
        mainiteration()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_database(name):
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
    
    person = database.getDefaultPerson()
    if person:
        active_person = person
    return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def setup_bookmarks():
    global bookmarks
    bookmarks = Bookmarks.Bookmarks(database.getBookmarks(),
                                    gtop.get_widget("jump_to"),
                                    bookmark_callback)

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
    global id2col
    global alt2col
    
    person_list.freeze()
    datacomp = DataFilter.compare
    gname = utils.phonebook_from_name

    person_list.set_column_visibility(1,Config.id_visible)
    new_alt2col = {}
    
    for person in database.getPersonMap().values():
        if datacomp(person):
            if id2col.has_key(person):
                new_alt2col[person] = alt2col[person]
                continue
            pos = (person,0)
            id2col[person] = pos
            new_alt2col[person] = []

            if person.getGender():
                gender = const.male
            else:
                gender = const.female

            bday = person.getBirth().getDateObj()
            dday = person.getDeath().getDateObj()
            sort_bday = sort.build_sort_birth(bday)
            sort_dday = sort.build_sort_death(dday)
            qbday = bday.getQuoteDate()
            qdday = dday.getQuoteDate()
            pid = person.getId()
            bsn = sort.build_sort_name

            name = person.getPrimaryName()
            person_list.insert(0,[gname(name,0), pid, gender, qbday, qdday,
                                  bsn(name), sort_bday, sort_dday])
            person_list.set_row_data(0,pos)

            if Config.hide_altnames:
                continue
                
            for name in person.getAlternateNames():
                pos = (person,1)
                new_alt2col[person].append(pos)

                person_list.insert(0,[gname(name,1), pid, gender, qbday, qdday,
                                      bsn(name), sort_bday, sort_dday])
                person_list.set_row_data(0,pos)
                    
        else:
            if id2col.has_key(person):
                pid = id2col[person]
                del id2col[person]

                for id in [pid] + alt2col[person]:
                    row = person_list.find_row_from_data(id)
                    person_list.remove(row)

    alt2col = new_alt2col
    person_list.thaw()
    sort_person_list()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def goto_active_person():
    if id2col.has_key(active_person):
        pos = id2col[active_person]
        column = person_list.find_row_from_data(pos)
        if column != -1:
            person_list.select_row(column,0)
            person_list.moveto(column)
    else:
        if person_list.rows > 0:
            person_list.select_row(0,0)
            person_list.moveto(0)
            person,alt = person_list.get_row_data(0)
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
        msg = _("Do you wish to set %s as the home person?") % name
        topWindow.question(msg,set_person)

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
#
#
#-------------------------------------------------------------------------
def menu_report(obj,task):
    if active_person:
        task(database,active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def menu_tools(obj,task):
    if active_person:
        task(database,active_person,update_display)
    
#-------------------------------------------------------------------------
#
# Main program
#
#-------------------------------------------------------------------------

def main(arg):
    global database, gtop
    global statusbar,notebook
    global person_list, source_list, place_list,pv
    global topWindow
    
    rc_parse(const.gtkrcFile)

    Plugins.load_plugins(const.pluginsDir)
    Plugins.load_plugins(os.path.expanduser("~/.gramps/plugins"))
    Filter.load_filters(const.filtersDir)
    Filter.load_filters(os.path.expanduser("~/.gramps/filters"))

    gtop = libglade.GladeXML(const.gladeFile, "gramps")

    Plugins.build_report_menu(gtop.get_widget("reports_menu"),menu_report)
    Plugins.build_tools_menu(gtop.get_widget("tools_menu"),menu_tools)
    Plugins.build_export_menu(gtop.get_widget("export1"),export_callback)
    Plugins.build_import_menu(gtop.get_widget("import1"),import_callback)
    
    statusbar   = gtop.get_widget("statusbar")
    topWindow   = gtop.get_widget("gramps")
    person_list = gtop.get_widget("person_list")
    source_list = gtop.get_widget("source_list")
    place_list  = gtop.get_widget("place_list")
    filter_list = gtop.get_widget("filter_list")
    notebook    = gtop.get_widget(NOTEBOOK)

    person_list.set_column_visibility(5,0)
    person_list.set_column_visibility(6,0)
    person_list.set_column_visibility(7,0)
    person_list.set_sort_column(sort_column)
    person_list.set_sort_type(sort_direct)

    filter_list.set_menu(Filter.build_filter_menu(on_filter_name_changed))
    
    gtop.get_widget("filter").set_sensitive(0)

    # set the window icon 
    topWindow.set_icon(GtkPixmap(topWindow,const.logo))
    
    person_list.column_titles_active()

    for box in range(1,16):
        pv[box] = gtop.get_widget("pv%d" % box)

    gtop.signal_autoconnect({
        "delete_event"                      : delete_event,
        "destroy_passed_object"             : utils.destroy_passed_object,
        "on_about_activate"                 : on_about_activate,
        "on_add_bookmark_activate"          : on_add_bookmark_activate,
        "on_add_child_clicked"              : on_add_child_clicked,
        "on_add_new_child_clicked"          : on_add_new_child_clicked,
        "on_add_place_clicked"              : on_add_place_clicked,
        "on_add_source_clicked"             : on_add_source_clicked,
        "on_add_sp_clicked"                 : on_add_sp_clicked,
        "on_addperson_clicked"              : load_new_person,
        "on_apply_filter_clicked"           : on_apply_filter_clicked,
        "on_arrow_left_clicked"             : on_arrow_left_clicked,
        "on_canvas1_size_request"           : on_canvas1_size_request,
        "on_child_list_button_press_event"  : on_child_list_button_press_event,
        "on_child_list_select_row"          : on_child_list_select_row,
        "on_choose_parents_clicked"         : on_choose_parents_clicked, 
        "on_contents_activate"              : on_contents_activate,
        "on_default_person_activate"        : on_default_person_activate,
        "on_delete_parents_clicked"         : on_delete_parents_clicked,
        "on_delete_person_clicked"          : on_delete_person_clicked,
        "on_delete_place_clicked"           : on_delete_place_clicked,
        "on_delete_source_clicked"          : on_delete_source_clicked,
        "on_delete_sp_clicked"              : on_delete_sp_clicked,
        "on_edit_active_person"             : load_active_person,
        "on_edit_bookmarks_activate"        : on_edit_bookmarks_activate,
        "on_edit_father_clicked"            : on_edit_father_clicked,
        "on_edit_mother_clicked"            : on_edit_mother_clicked,
        "on_edit_place_clicked"             : on_edit_place_clicked,
        "on_edit_source_clicked"            : on_edit_source_clicked,
        "on_edit_sp_clicked"                : on_edit_sp_clicked,
        "on_edit_spouse_clicked"            : on_edit_spouse_clicked,
        "on_exit_activate"                  : on_exit_activate,
        "on_family1_activate"               : on_family1_activate,
        "on_father_next_clicked"            : on_father_next_clicked,
        "on_fv_prev_clicked"                : on_fv_prev_clicked,
        "on_home_clicked"                   : on_home_clicked,
        "on_mother_next_clicked"            : on_mother_next_clicked,
        "on_new_clicked"                    : on_new_clicked,
        "on_notebook1_switch_page"          : on_notebook1_switch_page,
        "on_ok_button1_clicked"             : on_ok_button1_clicked,
        "on_open_activate"                  : on_open_activate,
        "on_pedegree1_activate"             : on_pedegree1_activate,
        "on_person_list1_activate"          : on_person_list1_activate,
        "on_person_list_button_press"       : on_person_list_button_press,
        "on_person_list_click_column"       : on_person_list_click_column,
        "on_person_list_select_row"         : on_person_list_select_row,
        "on_place_list_button_press_event"  : on_place_list_button_press_event,
        "on_place_list_select_row"          : on_list_select_row,
        "on_places_activate"                : on_places_activate,
        "on_preferences_activate"           : on_preferences_activate,
        "on_pv_button_press_event"          : on_pv_button_press_event,
        "on_pv_n0_clicked"                  : on_pv_n0_clicked,
        "on_pv_n1_clicked"                  : on_pv_n1_clicked,
        "on_remove_child_clicked"           : on_remove_child_clicked,
        "on_reports_clicked"                : on_reports_clicked,
        "on_revert_activate"                : on_revert_activate,
        "on_save_activate"                  : on_save_activate,
        "on_save_as_activate"               : on_save_as_activate,
        "on_source_list_button_press_event" : on_src_list_button_press_event,
        "on_source_list_select_row"         : on_list_select_row,
        "on_sources_activate"               : on_sources_activate,
        "on_spouselist_changed"             : on_spouselist_changed,
        "on_swap_clicked"                   : on_swap_clicked,
        "on_tools_clicked"                  : on_tools_clicked,
        })	

    database = RelDataBase()
    Config.loadConfig(full_update)
    person_list.set_column_visibility(1,Config.id_visible)

    notebook.set_show_tabs(Config.usetabs)
    gtop.get_widget("child_list").set_column_visibility(4,Config.show_detail)
        
    if arg != None:
        read_file(arg)
    elif Config.lastfile != None and Config.lastfile != "" and Config.autoload:
        read_file(Config.lastfile)

    database.setResearcher(Config.owner)
    mainloop()

#-------------------------------------------------------------------------
#
# Start it all
#
#-------------------------------------------------------------------------
def on_canvas1_size_request(obj,a):
    load_canvas()

#-------------------------------------------------------------------------
#
# Start it all
#
#-------------------------------------------------------------------------
if __name__ == '__main__':
    main(None)
    
