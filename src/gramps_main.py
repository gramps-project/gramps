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
import GDK
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
import Find
import VersionControl
import RelImage
import ImageSelect

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

id2col        = {}
alt2col       = {}

bookmarks     = None
topWindow     = None
statusbar     = None
gtop          = None
notebook      = None
person_list   = None
source_list   = None
place_list    = None
media_list    = None
mid           = None
mtype         = None
mdesc         = None
mpath         = None
mdetails      = None
preview       = None
database      = None
nameArrow     = None
deathArrow    = None
dateArrow     = None
canvas        = None
merge_button  = None
sort_column   = 5
sort_direct   = SORT_ASCENDING
DataFilter    = Filter.Filter("")
c_birth_order = 6
c_sort_column = c_birth_order
c_sort_direct = SORT_ASCENDING

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

NOTEBOOK    = "notebook1"
FILESEL     = "fileselection"
FILTERNAME  = "filter_list"
PAD         = 3
CANVASPAD   = 20

#-------------------------------------------------------------------------
#
# Find support
#
#-------------------------------------------------------------------------
def on_find_activate(obj):
    """Display the find box"""
    Find.Find(person_list,find_goto_to)

def find_goto_to(person):
    """Find callback to jump to the selected person"""
    change_active_person(person)
    goto_active_person()
    update_display(0)

#-------------------------------------------------------------------------
#
# Merge
#
#-------------------------------------------------------------------------
def on_merge_activate(obj):
    """Calls up the merge dialog for the selection"""

    page = notebook.get_current_page()
    if page == 0:
        if len(person_list.selection) != 2:
            msg = _("Exactly two people must be selected to perform a merge")
            GnomeErrorDialog()
        else:
            import MergeData
            p1 = person_list.get_row_data(person_list.selection[0])
            p2 = person_list.get_row_data(person_list.selection[1])
            MergeData.MergePeople(database,p1[0],p2[0],merge_update)
    elif page == 4:
        if len(place_list.selection) != 2:
            msg = _("Exactly two places must be selected to perform a merge")
            GnomeErrorDialog(msg)
        else:
            import MergeData
            p1 = place_list.get_row_data(place_list.selection[0])
            p2 = place_list.get_row_data(place_list.selection[1])
            MergeData.MergePlaces(database,p1,p2,load_places)

#-------------------------------------------------------------------------
#
# Exiting
#
#-------------------------------------------------------------------------
def delete_event(widget, event):
    """Catch the destruction of the top window, prompt to save if needed"""
    widget.hide()
    on_exit_activate(widget)
    return TRUE

def on_exit_activate(obj):
    """Prompt to save on exit if needed"""
    if utils.wasModified():
        question = _("Unsaved changes exist in the current database\n") + \
                   _("Do you wish to save the changes?")
        topWindow.question(question,save_query)
    else:    
        mainquit(obj)

def save_query(value):
    """Catch the reponse to the save on exit question"""
    if value == 0:
        on_save_activate_quit()
    else:
        mainquit(gtop)

#-------------------------------------------------------------------------
#
# Help
#
#-------------------------------------------------------------------------
def on_about_activate(obj):
    """Displays the about box.  Called from Help menu"""
    GnomeAbout(const.progName,const.version,const.copyright,
               const.authors,const.comments,const.logo).show()
    
def on_contents_activate(obj):
    """Display the Gramps manual"""
    import gnome.help
    gnome.help.display("gramps-manual","index.html")

def on_writing_extensions_activate(obj):
    """Display the Extending Gramps manual"""
    import gnome.help
    gnome.help.display("extending-gramps","index.html")
    
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
# Spouse editing callbacks 
#
#-------------------------------------------------------------------------
def on_add_sp_clicked(obj):
    """Add a new spouse to the current person"""
    import AddSpouse
    AddSpouse.AddSpouse(database,active_person,load_family,redisplay_person_list)

def on_edit_sp_clicked(obj):
    """Edit the marriage information for the current family"""
    Marriage.Marriage(active_family,database)

def on_delete_sp_clicked(obj):
    """Delete the currently selected spouse from the family"""
    
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
            load_family(active_person.getFamilyList()[0])
        else:
            load_family(None)
    else:
        load_family()
    utils.modified()

#-------------------------------------------------------------------------
#
# Selecting father, mother, or child from Family View
#
#-------------------------------------------------------------------------
def on_mother_next_clicked(obj):
    """Makes the current mother the active person"""
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

def on_father_next_clicked(obj):
    """Makes the current mother the active person"""
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

def on_fv_prev_clicked(obj):
    """makes the currently select child the active person"""
    if active_child:
        change_active_person(active_child)
        load_family()

#-------------------------------------------------------------------------
#
# Editing children of a marriage
#
#-------------------------------------------------------------------------
def on_add_child_clicked(obj):
    """Select an existing child to add to the active family"""
    import SelectChild
    SelectChild.SelectChild(database,active_family,active_person,load_family)

def on_add_new_child_clicked(obj):
    """Create a new child to add to the existing family"""
    import SelectChild
    SelectChild.NewChild(database,active_family,active_person,update_after_newchild)


#-------------------------------------------------------------------------
#
# Choosing Parents
#
#-------------------------------------------------------------------------
def on_choose_parents_clicked(obj):
    import ChooseParents
    ChooseParents.ChooseParents(database,active_person,active_parents,load_family)
    
#-------------------------------------------------------------------------
#
# Creating a new database
#
#-------------------------------------------------------------------------
def on_new_clicked(obj):
    """Prompt for permission to close the current database"""
    msg = _("Do you want to close the current database and create a new one?")
    topWindow.question(msg,new_database_response)

def new_database_response(val):
    """Clear out the database if permission was granted"""
    global active_person, active_father
    global active_family, active_mother
    global active_child
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
    id2col        = {}
    alt2col       = {}

    utils.clearModified()
    change_active_person(None)
    person_list.clear()
    load_family()
    load_sources()
    load_places()
    load_media()
    
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
# Update the display
#
#-------------------------------------------------------------------------
def full_update():
    """Brute force display update, updating all the pages"""
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
    load_canvas()
    load_media()

def update_display(changed):
    """Incremental display update, update only the displayed page"""
    page = notebook.get_current_page()
    if page == 0:
        if changed:
            apply_filter()
        else:
            goto_active_person()
    elif page == 1:
        load_family()
    elif page == 2:
        load_canvas()
    elif page == 3:
        load_sources()
    elif page == 4:
        load_places()
    else:
        load_media()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def load_sources():
    source_list.clear()
    source_list.freeze()

    if len(source_list.selection) > 0:
        current_row = source_list.selection[0]
    else:
        current_row = 0

    index = 0
    for src in database.getSourceMap().values():
        source_list.append([src.getTitle(),src.getAuthor()])
        source_list.set_row_data(index,src)
        index = index + 1

    if index > 0:
        source_list.select_row(current_row,0)
        source_list.moveto(current_row)

    source_list.thaw()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_src_list_button_press_event(obj,event):
    if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
        if len(obj.selection) > 0:
            index = obj.selection[0]
            source = obj.get_row_data(index)
            EditSource.EditSource(source,database,update_display_after_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_place_list_button_press_event(obj,event):
    if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
        if len(obj.selection) > 0:
            index = obj.selection[0]
            place = obj.get_row_data(index)
            EditPlace.EditPlace(place,database,update_display_after_edit)

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
def on_delete_place_clicked(obj):
    if len(obj.selection) == 0:
        return
    elif len(obj.selection) > 1:
        msg = _("Currently, you can only delete on place at a time")
        topWindow.error(msg)
        return
    else:
        index = obj.selection[0]

    used = 0
    place = obj.get_row_data(index)
    for p in database.getPersonMap().values():
        for event in [p.getBirth(), p.getDeath()] + p.getEventList():
            if event.getPlace() == place:
                used = 1
    for f in database.getFamilyMap().values():
        for event in f.getEventList():
            if event.getPlace() == place:
                used = 1

    if used == 1:
        import EditPlace
        ans = EditPlace.DeletePlaceQuery(place,database,update_display)
        msg = _("This place is currently being used. Delete anyway?")
        GnomeQuestionDialog(msg,ans.query_response)
    else:
        map = database.getPlaceMap()
        del map[place.getId()]
        utils.modified()
        update_display(0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_source_clicked(obj):
    import EditSource
    
    if len(obj.selection) == 0:
        return
    else:
        index = obj.selection[0]

    source = obj.get_row_data(index)


    if is_source_used(source):
        msg = _("This source is currently being used. Delete anyway?")
        ans = EditSource.DelSrcQuery(source,database,update_display)
        GnomeQuestionDialog(msg,ans.query_response)
    else:
        map = database.getSourceMap()
        del map[source.getId()]
        utils.modified()
        update_display(0)

def is_source_used(source):
    for p in database.getPlaceMap().values():
        for sref in p.getSourceRefList():
            if sref.getBase() == source:
                return 1
    for p in database.getPersonMap().values():
        for v in p.getEventList() + [p.getBirth(), p.getDeath()]:
            for sref in v.getSourceRefList():
                if sref.getBase() == source:
                    return 1
        for v in p.getAttributeList():
            for sref in v.getSourceRefList():
                if sref.getBase() == source:
                    return 1
        for v in p.getAlternateNames() + [p.getPrimaryName()]:
            for sref in v.getSourceRefList():
                if sref.getBase() == source:
                    return 1
        for v in p.getAddressList():
            for sref in v.getSourceRefList():
                if sref.getBase() == source:
                    return 1
    for p in database.getObjectMap().values():
        for sref in p.getSourceRefList():
            if sref.getBase() == source:
                return 1
    for p in database.getFamilyMap().values():
        for v in p.getEventList():
            for sref in v.getSourceRefList():
                if sref.getBase() == source:
                    return 1
        for v in p.getAttributeList():
            for sref in v.getSourceRefList():
                if sref.getBase() == source:
                    return 1
    return 0

#-------------------------------------------------------------------------
#
# Edit callbacks
#
#-------------------------------------------------------------------------
def on_edit_source_clicked(obj):
    if len(obj.selection) > 0:
        index = obj.selection[0]
        source = obj.get_row_data(index)
        EditSource.EditSource(source,database,update_display_after_edit)

def on_edit_place_clicked(obj):
    """Display the selected places in the EditPlace display"""
    if len(obj.selection) > 5:
        msg = _("You requested too many places to edit at the same time")
        GnomeErrorDialog(msg)
    else:
        for p in obj.selection:
            place = obj.get_row_data(p)
            EditPlace.EditPlace(place,database,update_display_after_edit)

def new_source_after_edit(source):
    database.addSource(source)
    update_display(0)

def new_place_after_edit(place):
    database.addPlace(place)
    update_display(0)

def update_display_after_edit(place):
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
    dbname = obj.get_data("dbname")
    getoldrev = obj.get_data("getoldrev")
    filename = dbname.get_full_path(1)
    utils.destroy_passed_object(obj)

    if getoldrev.get_active():
        vc = VersionControl.RcsVersionControl(filename)
        VersionControl.RevisionSelect(database,filename,vc,load_revision)
    else:
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
        if Config.usevc and Config.vc_comment:
            display_comment_box(filename)
        else:
            save_file(filename,_("No Comment Provided"))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def save_file(filename,comment):        
    import WriteXML
    import VersionControl

    path = filename
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

    if Config.usevc:
        vc = VersionControl.RcsVersionControl(path)
        vc.checkin(filename,comment,not Config.uncompress)
               
    statusbar.set_status("")
    statusbar.set_progress(0)

#-------------------------------------------------------------------------
#
# Edit Person window for specified people
#
#-------------------------------------------------------------------------
def load_active_person(obj):
    """Display the selected people in the EditPerson display"""
    if len(person_list.selection) > 5:
        msg = _("You requested too many people to edit at the same time")
        GnomeErrorDialog(msg)
    else:
        for p in person_list.selection:
            person = person_list.get_row_data(p)
            load_person(person[0])

def on_edit_spouse_clicked(obj):
    """Display the active spouse in the EditPerson display"""
    load_person(active_spouse)

def on_edit_mother_clicked(obj):
    """Display the active mother in the EditPerson display"""
    load_person(active_mother)

def on_edit_father_clicked(obj):
    """Display the active father in the EditPerson display"""
    load_person(active_father)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_new_person(obj):
    global active_person
    active_person = Person()
    EditPerson.EditPerson(active_person,database,new_after_edit)

#-------------------------------------------------------------------------
#
# Deleting a person
#
#-------------------------------------------------------------------------
def on_delete_person_clicked(obj):
    if len(person_list.selection) == 1:
        msg = _("Do you really wish to delete %s?") % Config.nameof(active_person)
        topWindow.question( msg, delete_person_response)
    elif len(person_list.selection) > 1:
        topWindow.error(_("Currently, you can only delete one person at a time"))

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
    global active_person
    
    person_list.freeze()
    if id2col.has_key(person):
        for id in [id2col[person]] + alt2col[person]:
            row = person_list.find_row_from_data(id)
            person_list.remove(row)

        del id2col[person]
        del alt2col[person]

        if row > person_list.rows:
            (active_person,alt) = person_list.get_row_data(row)
    person_list.thaw()
    
def merge_update(p1,p2):
    remove_from_person_list(p2)

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
def on_person_list_select_row(obj,row,b,c):
    if row == obj.selection[0]:
        person,alt = obj.get_row_data(row)
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
# on_child_list_click_column
# 
# Called when the user selects a column header on the person_list window.
# Change the sort function (column 0 is the name column, and column 2 is
# the birthdate column), set the arrows on the labels to the correct
# orientation, and then call apply_filter to redraw the list
#
#-------------------------------------------------------------------------
def on_child_list_click_column(clist,column):
    if column == 0:
        child_change_sort(clist,0,gtop.get_widget("cNameSort"))
    elif (column == 3) or (column == 6):
        child_change_sort(clist,6,gtop.get_widget("cDateSort"))
    else:
        return

    sort_child_list(clist)
    if id2col.has_key(active_child):
        row = clist.find_row_from_data(id2col[active_child])
        clist.moveto(row)

#-------------------------------------------------------------------------
# 
# 
# 
#-------------------------------------------------------------------------
def child_change_sort(clist,column,arrow):
    global c_sort_direct
    global c_sort_column

    cNameArrow.hide()
    cDateArrow.hide()
    arrow.show()
    
    if c_sort_column == column:
        if c_sort_direct == SORT_DESCENDING:
            c_sort_direct = SORT_ASCENDING
            arrow.set(GTK.ARROW_DOWN,2)
        else:
            c_sort_direct = SORT_DESCENDING
            arrow.set(GTK.ARROW_UP,2)
    else:
        c_sort_direct = SORT_ASCENDING
    c_sort_column = column
    clist.set_sort_type(c_sort_direct)
    clist.set_sort_column(c_sort_column)
    clist.set_reorderable(c_sort_column == c_birth_order)
    

def sort_child_list(clist):
    clist.freeze()
    clist.sort()
    clist.thaw()

#-------------------------------------------------------------------------
# 
# on_child_list_row_move
# 
# Validate whether or not this child can be moved within the clist.
# This routine is called in the middle of the clist's callbacks, so
# the state can be confusing.  If the code is being debugged, the
# display at this point shows that the list has been reordered when in
# actuality it hasn't.  All accesses to the clist data structure
# reference the state just prior to the "move".
#
# This routine must keep/compute its own list indices as the functions
# list.remove(), list.insert(), list.reverse() etc. do not affect the
# values returned from the list.index() routine.
#
#-------------------------------------------------------------------------
def on_child_list_row_move(clist,fm,to):
    family = clist.get_data("f")

    # Create a list based upon the current order of the clist
    clist_order = []
    for i in range(clist.rows):
        clist_order = clist_order + [clist.get_row_data(i)]
    child = clist_order[fm]

    # This function deals with ascending order lists.  Convert if
    # necessary.
    if (c_sort_direct == SORT_DESCENDING):
        clist_order.reverse()
        max_index = len(clist_order) - 1
        fm = max_index - fm
        to = max_index - to
        
    # Create a new list to match the requested order
    desired_order = clist_order[:fm] + clist_order[fm+1:]
    desired_order = desired_order[:to] + [child] + desired_order[to:]

    # Check birth date order in the new list
    if (EditPerson.birth_dates_in_order(desired_order) == 0):
        clist.emit_stop_by_name("row_move")
        GnomeWarningDialog(_("Invalid move.  Children must be ordered by birth date."))
        return
           
    # OK, this birth order works too.  Update the family data structures.
    family.setChildList(desired_order)

    # Build a mapping of child item to list position.  This would not
    # be necessary if indices worked properly
    i = 0
    new_order = {}
    for tmp in desired_order:
        new_order[tmp] = i
        i = i + 1

    # Convert the original list back to whatever ordering is being
    # used by the clist itself.
    if (c_sort_direct == SORT_DESCENDING):
        clist_order.reverse()

    # Update the clist indices so any change of sorting works
    i = 0
    for tmp in clist_order:
    	clist.set_text(i, c_birth_order, "%2d"%new_order[tmp])
        i = i + 1

    # Need to save the changed order
    utils.modified()

def on_open_activate(obj):
    wFs = libglade.GladeXML(const.gladeFile, "dbopen")
    wFs.signal_autoconnect({
        "on_ok_button1_clicked": on_ok_button1_clicked,
        "destroy_passed_object": utils.destroy_passed_object
        })

    fileSelector = wFs.get_widget("dbopen")
    dbname = wFs.get_widget("dbname")
    getoldrev = wFs.get_widget("getoldrev")
    fileSelector.set_data("dbname",dbname)
    dbname.set_default_path(Config.db_dir)
    fileSelector.set_data("getoldrev",getoldrev)
    getoldrev.set_sensitive(Config.usevc)
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
# Save the file
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

def on_save_activate(obj):
    """Saves the file, first prompting for a comment if revision control needs it"""
    if not database.getSavePath():
        on_save_as_activate(obj)
    else:
        if Config.usevc and Config.vc_comment:
            display_comment_box(database.getSavePath())
        else:
            save_file(database.getSavePath(),_("No Comment Provided"))

def on_save_activate_quit():
    """Saves the file, first prompting for a comment if revision control needs it"""
    if not database.getSavePath():
        on_save_as_activate(obj)
    else:
        if Config.usevc and Config.vc_comment:
            display_comment_box(database.getSavePath())
        else:
            save_file(database.getSavePath(),_("No Comment Provided"))

def display_comment_box(filename):
    """Displays a dialog box, prompting for a revison control comment"""
    import VersionControl
    VersionControl.RevisionComment(filename,save_file)
    
#-------------------------------------------------------------------------
#
# Callbacks for the menu selections to change the view
# 
#-------------------------------------------------------------------------
def on_person_list1_activate(obj):
    """Switches to the person list view"""
    notebook.set_page(0)
    merge_button.set_sensitive(1)

def on_family1_activate(obj):
    """Switches to the family view"""
    notebook.set_page(1)
    merge_button.set_sensitive(0)

def on_pedegree1_activate(obj):
    """Switches to the pedigree view"""
    notebook.set_page(2)
    merge_button.set_sensitive(0)

def on_sources_activate(obj):
    """Switches to the sources view"""
    notebook.set_page(3)
    merge_button.set_sensitive(0)

def on_places_activate(obj):
    """Switches to the places view"""
    notebook.set_page(4)
    merge_button.set_sensitive(1)

def on_media_activate(obj):
    """Switches to the media view"""
    notebook.set_page(5)
    merge_button.set_sensitive(0)

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
        load_canvas()
    elif page == 3:
        load_sources()
    elif page == 4:
        load_places()
    elif page == 5:
        load_media()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_places():
    place_list.freeze()
    place_list.clear()

    if len(place_list.selection) == 0:
        current_row = 0
    else:
        current_row = place_list.selection[0]

    index = 0
    places = database.getPlaceMap().values()

    nlist = map(lambda x: (string.upper(x.get_title()),x),places)
    nlist.sort()
    places = map(lambda(key,x): x, nlist)
    
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
        place_list.select_row(current_row,0)
        place_list.moveto(current_row)

    place_list.thaw()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_media_list_select_row(obj,row,b,c):
    mobj = obj.get_row_data(row)
    type = mobj.getMimeType()
    type_name = utils.get_mime_description(type)
    path = mobj.getPath()
    preview.load_file(utils.thumb_path(database.getSavePath(),mobj))
                          
    mid.set_text(mobj.getId())
    mtype.set_text(type_name)
    mdesc.set_text(mobj.getDescription())
    if path[0] == "/":
        mpath.set_text(path)
    else:
        mpath.set_text("<local>")
    mdetails.set_text("")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_media():
    media_list.freeze()
    media_list.clear()

    if len(media_list.selection) == 0:
        current_row = 0
    else:
        current_row = media_list.selection[0]

    index = 0
    objects = database.getObjectMap().values()

    for src in objects:
        title = src.getDescription()
        id = src.getId()
        type = utils.get_mime_description(src.getMimeType())
        if src.getLocal():
            path = "<local copy>"
        else:
            path = src.getPath()
        media_list.append([id,title,type,path,""])
        media_list.set_row_data(index,src)
        index = index + 1

    media_list.sort()

    if index > 0:
        media_list.select_row(current_row,0)
        media_list.moveto(current_row)

    media_list.thaw()

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
    class_init = menu.get_active().get_data("function")
    DataFilter = class_init(qualifer)
    DataFilter.set_invert(invert_filter)
    apply_filter()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_filter_name_changed(obj):
    filter = obj.get_data("filter")
    filter.set_sensitive(obj.get_data("qual"))

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
    if epo.person.getId() == "":
        database.addPerson(epo.person)
    else:
        database.addPersonNoMap(epo.person,epo.person.getId())
    change_active_person(epo.person)
    redisplay_person_list(epo.person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def update_after_newchild(family,person):
    load_family(family)
    redisplay_person_list(person)

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
        if person.getGender() == Person.male:
            gender = const.male
        elif person.getGender() == Person.female:
            gender = const.female
        else:
            gender = const.unknown
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
def load_family(family=None):
    global active_mother
    global active_parents
    global active_spouse
    global active_family

    if family != None:
        active_family = family
    
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
    
    if active_parents and active_parents.getRelationship() == "Partners":
        fn = _("Parent")
        mn = _("Parent")
    else:
        fn = _("Father")
        mn = _("Mother")

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
    elif active_person == None:
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
def display_marriage(family):
    global active_child
    global active_family
    global active_spouse

    active_family = family
    clist = gtop.get_widget("child_list")
    fv_prev = gtop.get_widget("fv_prev")

    clist.clear()
    active_child = None

    i = 0
    clist.set_sort_type(c_sort_direct)
    clist.set_sort_column(c_sort_column)
    clist.set_reorderable(c_sort_column == c_birth_order)

    if family != None:
        if active_person.getGender() == Person.male:
            active_spouse = family.getMother()
        else:
            active_spouse = family.getFather()
            
        child_list = family.getChildList()
        # List is already sorted by birth date
        attr = ""
        for child in child_list:
            status = _("Unknown")
            if child.getGender() == Person.male:
                gender = const.male
            elif child.getGender() == Person.female:
                gender = const.female
            else:
                gender = const.unknown
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
                          gender,utils.birthday(child),status,attr,"%2d"%i])
            clist.set_row_data(i,child)
            i=i+1
            if i != 0:
                fv_prev.set_sensitive(1)
                clist.select_row(0,0)
            else:	
                fv_prev.set_sensitive(0)
        clist.set_data("f",family)
        clist.sort()
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
def post_load(name):
    global active_person

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
    for person in database.getPersonMap().values():
        if active_person == None:
            active_person = person
        lastname = person.getPrimaryName().getSurname()
        if lastname and lastname not in const.surnames:
            const.surnames.append(lastname)

    statusbar.set_progress(1.0)
    full_update()
    statusbar.set_progress(0.0)
    return 1
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_database(name):
    filename = "%s/%s" % (name,const.indexFile)
    if ReadXML.loadData(database,filename,load_progress) == 0:
        return 0
    return post_load(name)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def load_revision(f,name,revision):
    filename = "%s/%s" % (name,const.indexFile)
    if ReadXML.loadRevision(database,f,filename,revision,load_progress) == 0:
        return 0
    return post_load(name)

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

            if person.getGender() == Person.male:
                gender = const.male
            elif person.getGender() == Person.female:
                gender = const.female
            else:
                gender = const.unknown

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
def on_home_clicked(obj):
    temp = database.getDefaultPerson()
    if temp:
        change_active_person(temp)
        update_display(0)
    else:
        topWindow.error(_("No default/home person has been set"))

#-------------------------------------------------------------------------
#
# Bookmark interface
#
#-------------------------------------------------------------------------
def on_add_bookmark_activate(obj):
    bookmarks.add(active_person)

def on_edit_bookmarks_activate(obj):
    bookmarks.edit()
        
def bookmark_callback(obj,person):
    change_active_person(person)
    update_display(0)
    
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
# Import/Export function callbacks
#
#-------------------------------------------------------------------------
def export_callback(obj,plugin_function):
    """Call the export plugin, with the active person and database"""
    if active_person:
        plugin_function(database,active_person)

def import_callback(obj,plugin_function):
    """Call the import plugin"""
    plugin_function(database,active_person,tool_callback)
    topWindow.set_title("Gramps - " + database.getSavePath())

#-------------------------------------------------------------------------
#
# Call up the preferences dialog box
#
#-------------------------------------------------------------------------
def on_preferences_activate(obj):
    Config.display_preferences_box(database)
    
#-------------------------------------------------------------------------
#
# Report and tool callbacks from pull down menus
#
#-------------------------------------------------------------------------
def menu_report(obj,task):
    """Call the report plugin selected from the menus"""
    if active_person:
        task(database,active_person)

def menu_tools(obj,task):
    """Call the tool plugin selected from the menus"""
    if active_person:
        task(database,active_person,tool_callback)
    
#-------------------------------------------------------------------------
#
# Person list keypress events
#
#-------------------------------------------------------------------------
def on_main_key_release_event(obj,event):
    """Respond to the insert and delete buttons in the person list"""
    if event.keyval == GDK.Delete:
        on_delete_person_clicked(obj)
    elif event.keyval == GDK.Insert:
        load_new_person(obj)
    
#-------------------------------------------------------------------------
#
# Basic media list callbacks
#
#-------------------------------------------------------------------------
def create_add_dialog(obj):
    """Add a new media object to the media list"""
    import AddMedia
    AddMedia.AddMediaObject(database,load_media)

def on_edit_media_clicked(obj):
    """Edit the properties of an existing media object in the media list"""
    if len(media_list.selection) <= 0:
        return
    object = media_list.get_row_data(media_list.selection[0])
    ImageSelect.GlobalMediaProperties(database,object)

def on_delete_media_clicked(obj):
    if len(media_list.selection) <= 0:
        return
    else:
        index = media_list.selection[0]
    mobj = media_list.get_row_data(index)
    if is_media_object_used(mobj):
        import ImageSelect
        ans = ImageSelect.DeleteMediaQuery(mobj,database,update_display)
        msg = _("This media object is currently being used. Delete anyway?")
        GnomeQuestionDialog(msg,ans.query_response)
    else:
        map = database.getObjectMap()
        del map[mobj.getId()]
        utils.modified()
        update_display(0)

def is_media_object_used(mobj):
    for p in database.getFamilyMap().values():
        for o in p.getPhotoList():
            if o.getReference() == mobj:
                return 1
    for p in database.getPersonMap().values():
        for o in p.getPhotoList():
            if o.getReference() == mobj:
                return 1
    for p in database.getSourceMap().values():
        for o in p.getPhotoList():
            if o.getReference() == mobj:
                return 1
    for p in database.getPlaceMap().values():
        for o in p.getPhotoList():
            if o.getReference() == mobj:
                return 1
    
#-------------------------------------------------------------------------
#
# Drag and drop media list callbacks
#
#-------------------------------------------------------------------------
def on_media_list_drag_data_get(w, context, selection_data, info, time):
    if info == 1:
        return
    if len(w.selection) > 0:
        row = w.selection[0]
        d = w.get_row_data(row)
        id = d.getId()
        selection_data.set(selection_data.target, 8, id)	

def on_media_list_drag_data_received(w, context, x, y, data, info, time):
    if data and data.format == 8:
        d = string.strip(string.replace(data.data,'\0',' '))
        if d[0:5] == "file:":
            name = d[5:]
            mime = utils.get_mime_type(name)
            photo = Photo()
            photo.setPath(name)
            photo.setMimeType(mime)
            description = os.path.basename(name)
            photo.setDescription(description)
            database.addObject(photo)
            utils.modified()
            w.drag_finish(context, TRUE, FALSE, time)
            load_media()
        else:
            w.drag_finish(context, FALSE, FALSE, time)

#-------------------------------------------------------------------------
#
# Create the list of ancestors for the pedigree chart
#
#-------------------------------------------------------------------------
def find_tree(person,index,depth,list,val=0):

    if depth > 5 or person == None:
        return
    family = person.getMainFamily()
    frel = 0
    mrel = 0
    if family == None:
        l = person.getAltFamilyList()
        if len(l) > 0:
            (family,m,f) = l[0]
            mrel = (m != "Birth")
            frel = (f != "Birth")
            
    list[index] = (person,val)
    if family != None:
        father = family.getFather()
        if father != None:
            find_tree(father,(2*index)+1,depth+1,list,frel)
        mother = family.getMother()
        if mother != None:
            find_tree(mother,(2*index)+2,depth+1,list,mrel)

#-------------------------------------------------------------------------
#
# Draw the pedigree chart
#
#-------------------------------------------------------------------------
canvas_items = []

def load_canvas():
    global canvas_items 
    
    if active_person == None:
        return

    h = 0
    w = 0

    cx1,cy1,cx2,cy2 = canvas.get_allocation()
    canvas.set_scroll_region(cx1,cy1,cx2,cy2)
    root = canvas.root()

    for i in canvas_items:
        i.destroy()
        
    style = canvas['style']
    font = style.font

    list = [None]*31
    find_tree(active_person,0,1,list)
    for t in list:
        if t:
            n = t[0].getPrimaryName().getName()
            h = max(h,font.height(n)+2*PAD)
            w = max(w,font.width(n)+2*PAD)
            w = max(w,font.width("d. %s" % t[0].getDeath().getDate())+2*PAD)
            w = max(w,font.width("b. %s" % t[0].getBirth().getDate())+2*PAD)

    cpad = max(h+4,CANVASPAD)
    cw = (cx2-cx1-(2*cpad))
    ch = (cy2-cy1-(2*cpad))

    if 5*w < cw and 24*h < ch:
        gen = 31
        xdiv = 5.0
    elif 4*w < cw and 12*h < ch:
        gen = 15
        xdiv = 4.0
    else:
        gen = 7
        xdiv = 3.0

    for c in canvas_items:
        c.destroy()

    xpts = build_x_coords(cw/xdiv,cpad)
    ypts = build_y_coords(ch/32.0)

    childcnt = 0
    for family in active_person.getFamilyList():
        if len(family.getChildList()) > 0:
            a = GtkArrow(at=GTK.ARROW_LEFT)
            cnv_button = GtkButton()
            cnv_button.add(a)
            a.show()
            cnv_button.connect("clicked",on_arrow_left_clicked)

            cnv_button.show()
            item = root.add("widget",
                            widget=cnv_button,
                            x=cx1,
                            y=ypts[0]+(h/2.0), 
                            height=h,
                            width=h,
                            size_pixels=1,
                            anchor=GTK.ANCHOR_WEST)
            canvas_items = [item, cnv_button, a]
            break
    else:
        canvas_items = []

    if list[1]:
        p = list[1]
        add_parent_button(root,canvas_items,p[0],cx2-PAD,ypts[1],h)
        
    if list[2]:
        p = list[2]
        add_parent_button(root,canvas_items,p[0],cx2-PAD,ypts[2],h)

    for i in range(gen):
        if list[i]:
            if i < int(gen/2):
                findex = (2*i)+1 
                mindex = findex+1
                if list[findex]:
                    p = list[findex]
                    draw_canvas_line(root, xpts[i], ypts[i], xpts[findex],
                                     ypts[findex], h, w, p[0], style, p[1])
                if list[mindex]:
                    p = list[mindex]
                    draw_canvas_line(root,xpts[i],ypts[i], xpts[mindex],
                                     ypts[mindex], h, w, p[0], style, p[1])
            p = list[i]
            add_box(root,xpts[i],ypts[i],w,h,p[0],style)


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
        load_canvas()
    return 1
    
def add_parent_button(root,item_list,parent,x,y,h):
    a = GtkArrow(at=GTK.ARROW_RIGHT)
    cnv_button = GtkButton()
    cnv_button.add(a)
    a.show()
    cnv_button.connect("clicked",change_to_parent)
    cnv_button.set_data("p",parent)

    cnv_button.show()
    item = root.add("widget", widget=cnv_button, x=x, y=y+(h/2), height=h,
                    width=h, size_pixels=1, anchor=GTK.ANCHOR_EAST)
    item_list.append(a)
    item_list.append(item)
    item_list.append(cnv_button)

def change_to_parent(obj):
    person = obj.get_data("p")
    change_active_person(person)
    load_canvas()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def draw_canvas_line(root,x1,y1,x2,y2,h,w,data,style,ls):
    startx = x1+(w/2.0)
    pts = [startx,y1, startx,y2+(h/2.0), x2,y2+(h/2.0)]
    item = root.add("line",
                    width_pixels=2,
                    points=pts,
                    line_style=ls,
                    fill_color_gdk=style.black)
    item.set_data("p",data)
    item.connect("event",line_event)
    canvas_items.append(item)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def build_x_coords(xincr,cpad):

    return [cpad] + [xincr+cpad]*2 + [xincr*2+cpad]*4 +\
           [xincr*3+cpad]*8 + [xincr*4+cpad]*16

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def build_y_coords(yincr):
    return [ yincr*16, yincr*8,  yincr*24, yincr*4,  yincr*12,
             yincr*20, yincr*28, yincr*2,  yincr*6,  yincr*10,
             yincr*14, yincr*18, yincr*22, yincr*26, yincr*30,
             yincr,    yincr*3,  yincr*5,  yincr*7,  yincr*9,
             yincr*11, yincr*13, yincr*15, yincr*17, yincr*19,
             yincr*21, yincr*23, yincr*25, yincr*27, yincr*29, yincr*31]
    
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
                     outline_color_gdk=style.bg[STATE_NORMAL],
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
        if event.button == 1:
            if (event.state & GDK.SHIFT_MASK) or (event.state & GDK.CONTROL_MASK):
                change_active_person(obj.get_data("p"))
                load_canvas()
            else:
                load_person(obj.get_data('p'))
            return 1
    elif event.type == GDK.ENTER_NOTIFY:
        obj.raise_to_top()
        box = obj.children()[1]
        x,y,w,h = box.get_bounds()
        box.set(x1=x,y1=y,x2=w,y2=h*3)
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
        statusbar.set_status(_("Doubleclick to edit, Shift-Doubleclick to make the active person"))
    elif event.type == GDK.LEAVE_NOTIFY:
        ch = obj.children()
        length = len(ch)
        if length <= 3:
            return 1
        box = obj.children()[1]
        x,y,w,h = box.get_bounds()
        box.set(x1=x,y1=y,x2=w,y2=h/3)
        box2 = obj.children()[0]
        x,y,w,h1 = box2.get_bounds()
        box2.set(x1=x,y1=y,x2=w,y2=(h/3)+PAD)
        if length > 4:
            ch[4].destroy()
        if length > 3:
            ch[3].destroy()
        modify_statusbar()
        canvas.update_now()
        
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
        obj.set(fill_color_gdk=canvas['style'].bg[STATE_SELECTED],
                width_pixels=4)
        name = Config.nameof(obj.get_data("p"))
        msg = _("Double clicking will make %s the active person") % name
        statusbar.set_status(msg)
    elif event.type == GDK.LEAVE_NOTIFY:
        obj.set(fill_color_gdk=canvas['style'].black, width_pixels=2)
        modify_statusbar()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
ox1 = 0
ox2 = 0
oy1 = 0
oy2 = 0

def on_canvas1_event(obj,event):
    global ox1,ox2,oy1,oy2

    if event.type == GDK.EXPOSE:
        cx1,cy1,cx2,cy2 = canvas.get_allocation()
        if ox1 != cx1 or ox2 != cx2 or oy1 != cy1 or oy2 != cy2:
            ox1 = cx1
            ox2 = cx2
            oy1 = cy1
            oy2 = cy2
            load_canvas()
    return 0

#-------------------------------------------------------------------------
#
# Main program
#
#-------------------------------------------------------------------------

def main(arg):
    global database, gtop
    global statusbar,notebook
    global person_list, source_list, place_list, canvas, media_list
    global topWindow, preview, merge_button
    global nameArrow, dateArrow, deathArrow
    global cNameArrow, cDateArrow
    global mid, mtype, mdesc, mpath, mdetails
    
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
    canvas      = gtop.get_widget("canvas1")
    source_list = gtop.get_widget("source_list")
    place_list  = gtop.get_widget("place_list")
    media_list  = gtop.get_widget("media_list")
    mid         = gtop.get_widget("mid")
    mtype       = gtop.get_widget("mtype")
    mdesc       = gtop.get_widget("mdesc")
    mpath       = gtop.get_widget("mpath")
    mdetails    = gtop.get_widget("mdetails")
    preview     = gtop.get_widget("preview")
    filter_list = gtop.get_widget("filter_list")
    notebook    = gtop.get_widget(NOTEBOOK)
    nameArrow   = gtop.get_widget("nameSort")
    dateArrow   = gtop.get_widget("dateSort")
    deathArrow  = gtop.get_widget("deathSort")
    merge_button= gtop.get_widget("merge")
    
    t = [ ('STRING', 0, 0),
          ('text/plain',0,0),
          ('text/uri-list',0,2),
          ('application/x-rootwin-drop',0,1)]
    media_list.drag_source_set(GDK.BUTTON1_MASK|GDK.BUTTON3_MASK,t,GDK.ACTION_COPY)
    media_list.drag_dest_set(DEST_DEFAULT_ALL,t,GDK.ACTION_COPY|GDK.ACTION_MOVE)
    cNameArrow  = gtop.get_widget("cNameSort")
    cDateArrow  = gtop.get_widget("cDateSort")
    person_list.set_column_visibility(5,0)
    person_list.set_column_visibility(6,0)
    person_list.set_column_visibility(7,0)
    person_list.set_sort_column(sort_column)
    person_list.set_sort_type(sort_direct)

    fw = gtop.get_widget('filter')
    filter_list.set_menu(Filter.build_filter_menu(on_filter_name_changed,fw))
    
    fw.set_sensitive(0)

    # set the window icon 
    topWindow.set_icon(GtkPixmap(topWindow,const.logo))
    
    person_list.column_titles_active()

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
        "on_canvas1_event"                  : on_canvas1_event,
        "on_child_list_button_press_event"  : on_child_list_button_press_event,
        "on_child_list_select_row"          : on_child_list_select_row,
        "on_child_list_click_column"        : on_child_list_click_column,
        "on_child_list_row_move"            : on_child_list_row_move,
        "on_choose_parents_clicked"         : on_choose_parents_clicked, 
        "on_contents_activate"              : on_contents_activate,
        "on_default_person_activate"        : on_default_person_activate,
        "on_delete_parents_clicked"         : on_delete_parents_clicked,
        "on_delete_person_clicked"          : on_delete_person_clicked,
        "on_delete_place_clicked"           : on_delete_place_clicked,
        "on_delete_source_clicked"          : on_delete_source_clicked,
        "on_delete_media_clicked"           : on_delete_media_clicked,
        "on_delete_sp_clicked"              : on_delete_sp_clicked,
        "on_edit_active_person"             : load_active_person,
        "on_edit_bookmarks_activate"        : on_edit_bookmarks_activate,
        "on_edit_father_clicked"            : on_edit_father_clicked,
        "on_edit_media_clicked"             : on_edit_media_clicked,
        "on_edit_mother_clicked"            : on_edit_mother_clicked,
        "on_edit_place_clicked"             : on_edit_place_clicked,
        "on_edit_source_clicked"            : on_edit_source_clicked,
        "on_edit_sp_clicked"                : on_edit_sp_clicked,
        "on_edit_spouse_clicked"            : on_edit_spouse_clicked,
        "on_exit_activate"                  : on_exit_activate,
        "on_family1_activate"               : on_family1_activate,
        "on_father_next_clicked"            : on_father_next_clicked,
        "on_find_activate"                  : on_find_activate,
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
        "on_main_key_release_event"         : on_main_key_release_event,
        "on_add_media_clicked"              : create_add_dialog,
        "on_media_activate"                 : on_media_activate,
        "on_media_list_select_row"          : on_media_list_select_row,
        "on_media_list_drag_data_get"       : on_media_list_drag_data_get,
        "on_media_list_drag_data_received"  : on_media_list_drag_data_received,
        "on_merge_activate"                 : on_merge_activate,
        "on_places_activate"                : on_places_activate,
        "on_preferences_activate"           : on_preferences_activate,
        "on_remove_child_clicked"           : on_remove_child_clicked,
        "on_reports_clicked"                : on_reports_clicked,
        "on_revert_activate"                : on_revert_activate,
        "on_save_activate"                  : on_save_activate,
        "on_save_as_activate"               : on_save_as_activate,
        "on_source_list_button_press_event" : on_src_list_button_press_event,
        "on_sources_activate"               : on_sources_activate,
        "on_spouselist_changed"             : on_spouselist_changed,
        "on_swap_clicked"                   : on_swap_clicked,
        "on_tools_clicked"                  : on_tools_clicked,
        "on_writing_extensions_activate"    : on_writing_extensions_activate,
        })	

    database = RelDataBase()
    Config.loadConfig(full_update)
    person_list.set_column_visibility(1,Config.id_visible)

    notebook.set_show_tabs(Config.usetabs)
    database.set_iprefix(Config.iprefix)
    database.set_oprefix(Config.oprefix)
    database.set_fprefix(Config.fprefix)
    database.set_sprefix(Config.sprefix)
    database.set_pprefix(Config.pprefix)
    child_list = gtop.get_widget("child_list")
    child_list.set_column_visibility(4,Config.show_detail)
    child_list.set_column_visibility(6,0)
    child_list.set_column_visibility(7,0)
        
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
if __name__ == '__main__':
    main(None)
