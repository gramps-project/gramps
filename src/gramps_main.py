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
from PedView import PedigreeView
from PlaceView import PlaceView
from SourceView import SourceView
from MediaView import MediaView

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

pedigree_view = None
place_view    = None
media_view    = None

bookmarks     = None
topWindow     = None
statusbar     = None
gtop          = None
notebook      = None
person_list   = None
database      = None
nameArrow     = None
idArrow       = None
deathArrow    = None
dateArrow     = None

merge_button  = None
sort_column   = 5
sort_direct   = SORT_ASCENDING
p_sort_column = 0
p_sort_direct = SORT_ASCENDING
DataFilter    = Filter.Filter("")
c_birth_order = 0
c_name        = 1
c_id          = 2
c_birth_date  = 4
c_details     = 6
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
            GnomeErrorDialog(msg)
        else:
            import MergeData
            p1 = person_list.get_row_data(person_list.selection[0])
            p2 = person_list.get_row_data(person_list.selection[1])
            MergeData.MergePeople(database,p1[0],p2[0],merge_update)
    elif page == 4:
        place_view.merge()

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
    if not active_family or not active_child or not active_person:
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
    if active_person:
        AddSpouse.AddSpouse(database,active_person,load_family,redisplay_person_list)

def on_edit_sp_clicked(obj):
    """Edit the marriage information for the current family"""
    if active_person:
        Marriage.Marriage(active_family,database)

def on_delete_sp_clicked(obj):
    """Delete the currently selected spouse from the family"""
    
    if active_person == None:
        return
    elif active_person == active_family.getFather():
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
    if active_person:
        SelectChild.SelectChild(database,active_family,active_person,load_family)

def on_add_new_child_clicked(obj):
    """Create a new child to add to the existing family"""
    import SelectChild
    if active_person:
        SelectChild.NewChild(database,active_family,active_person,update_after_newchild)


#-------------------------------------------------------------------------
#
# Choosing Parents
#
#-------------------------------------------------------------------------
def on_choose_parents_clicked(obj):
    import ChooseParents
    if active_person:
        ChooseParents.ChooseParents(database,active_person,active_parents,load_family,full_update)
    
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
    global active_child, active_spouse
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
    active_spouse = None
    id2col        = {}
    alt2col       = {}

    utils.clearModified()
    change_active_person(None)
    person_list.clear()
    load_family()
    source_view.load_sources()
    place_view.load_places()
    media_view.load_media()
    
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
    clist.set_column_visibility(c_details,Config.show_detail)
    clist.set_column_visibility(c_id,Config.id_visible)
    clist.set_column_visibility(c_birth_order,Config.index_visible)
    apply_filter()
    load_family()
    source_view.load_sources()
    place_view.load_places()
    pedigree_view.load_canvas(active_person)
    media_view.load_media()

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
        pedigree_view.load_canvas(active_person)
    elif page == 3:
        source_view.load_sources()
    elif page == 4:
        place_view.load_places()
    else:
        media_view.load_media()

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
def load_selected_people(obj):
    """Display the selected people in the EditPerson display"""
    if len(person_list.selection) > 5:
        msg = _("You requested too many people to edit at the same time")
        GnomeErrorDialog(msg)
    else:
        for p in person_list.selection:
            person = person_list.get_row_data(p)
            load_person(person[0])

def load_active_person(obj):
    load_person(active_person)
    
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
        change_sort(5,nameArrow)
    elif column == 1:
        change_sort(1,idArrow)
    elif column == 3:
        change_sort(6,dateArrow)
    elif column == 4:
        change_sort(7,deathArrow)
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

    for a in [ nameArrow, deathArrow, dateArrow, idArrow ]:
        if arrow != a:
            a.hide()
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
        arrow.set(GTK.ARROW_DOWN,2)
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
    if column == c_name:
        child_change_sort(clist,c_name,gtop.get_widget("cNameSort"))
    elif (column == c_birth_order) or (column == c_birth_date):
        child_change_sort(clist,c_birth_order,gtop.get_widget("cDateSort"))
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
    if ListColors.get_enable():
        try:
            oddbg = GdkColor(ListColors.oddbg[0],ListColors.oddbg[1],ListColors.oddbg[2])
            oddfg = GdkColor(ListColors.oddfg[0],ListColors.oddfg[1],ListColors.oddfg[2])
            evenbg = GdkColor(ListColors.evenbg[0],ListColors.evenbg[1],ListColors.evenbg[2])
            evenfg = GdkColor(ListColors.evenfg[0],ListColors.evenfg[1],ListColors.evenfg[2])
            rows = clist.rows
            for i in range(0,rows,2):
                clist.set_background(i,oddbg)
                clist.set_foreground(i,oddfg)
                if i != rows:
                    clist.set_background(i+1,evenbg)
                    clist.set_foreground(i+1,evenfg)
        except OverflowError:
            pass
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
    	clist.set_text(i, c_birth_order, "%2d"%(new_order[tmp]+1))
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

def on_family1_activate(obj):
    """Switches to the family view"""
    notebook.set_page(1)

def on_pedegree1_activate(obj):
    """Switches to the pedigree view"""
    notebook.set_page(2)

def on_sources_activate(obj):
    """Switches to the sources view"""
    notebook.set_page(3)

def on_places_activate(obj):
    """Switches to the places view"""
    notebook.set_page(4)

def on_media_activate(obj):
    """Switches to the media view"""
    notebook.set_page(5)

#-------------------------------------------------------------------------
#
# Load the appropriate page after a notebook switch
#
#-------------------------------------------------------------------------
def on_notebook1_switch_page(obj,junk,page):
    if page == 0:
        goto_active_person()
        merge_button.set_sensitive(1)
    elif page == 1:
        merge_button.set_sensitive(0)
        load_family()
    elif page == 2:
        merge_button.set_sensitive(0)
        pedigree_view.load_canvas(active_person)
    elif page == 3:
        merge_button.set_sensitive(0)
        source_view.load_sources()
    elif page == 4:
        merge_button.set_sensitive(1)
        place_view.load_places()
    elif page == 5:
        merge_button.set_sensitive(0)
        media_view.load_media()

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

            clist.append(["%2d"%(i+1),Config.nameof(child),child.getId(),\
                          gender,utils.birthday(child),status,attr])
            clist.set_row_data(i,child)
            i=i+1
            if i != 0:
                fv_prev.set_sensitive(1)
                clist.select_row(0,0)
            else:	
                fv_prev.set_sensitive(0)
        clist.set_data("f",family)
        sort_child_list(clist)
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
            const.surnames.sort()

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
# Main program
#
#-------------------------------------------------------------------------

def main(arg):
    global pedigree_view, place_view, source_view, media_view
    global database, gtop
    global statusbar,notebook
    global person_list, source_list, canvas
    global topWindow, preview, merge_button
    global nameArrow, dateArrow, deathArrow, idArrow
    global cNameArrow, cDateArrow
#    global mid, mtype, mdesc, mpath, mdetails
    
    rc_parse(const.gtkrcFile)
    database = RelDataBase()

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
    filter_list = gtop.get_widget("filter_list")
    notebook    = gtop.get_widget(NOTEBOOK)
    nameArrow   = gtop.get_widget("nameSort")
    idArrow     = gtop.get_widget("idSort")
    dateArrow   = gtop.get_widget("dateSort")
    deathArrow  = gtop.get_widget("deathSort")
    merge_button= gtop.get_widget("merge")

    canvas = gtop.get_widget("canvas1")
    pedigree_view = PedigreeView(canvas,modify_statusbar,\
                                 statusbar,change_active_person,\
                                 load_person)
    place_view  = PlaceView(database,gtop,update_display)
    source_view = SourceView(database,source_list,update_display)
    media_view  = MediaView(database,gtop,update_display)

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
    topWindow.set_icon(GtkPixmap(topWindow,const.icon))
    
    person_list.column_titles_active()

    gtop.signal_autoconnect({
        "delete_event"                      : delete_event,
        "destroy_passed_object"             : utils.destroy_passed_object,
        "on_about_activate"                 : on_about_activate,
        "on_add_bookmark_activate"          : on_add_bookmark_activate,
        "on_add_child_clicked"              : on_add_child_clicked,
        "on_add_new_child_clicked"          : on_add_new_child_clicked,
        "on_add_place_clicked"              : place_view.on_add_place_clicked,
        "on_add_source_clicked"             : source_view.on_add_source_clicked,
        "on_add_sp_clicked"                 : on_add_sp_clicked,
        "on_addperson_clicked"              : load_new_person,
        "on_apply_filter_clicked"           : on_apply_filter_clicked,
        "on_arrow_left_clicked"             : pedigree_view.on_show_child_menu,
        "on_canvas1_event"                  : pedigree_view.on_canvas1_event,
        "on_child_list_button_press_event"  : on_child_list_button_press_event,
        "on_child_list_select_row"          : on_child_list_select_row,
        "on_child_list_click_column"        : on_child_list_click_column,
        "on_child_list_row_move"            : on_child_list_row_move,
        "on_choose_parents_clicked"         : on_choose_parents_clicked, 
        "on_contents_activate"              : on_contents_activate,
        "on_default_person_activate"        : on_default_person_activate,
        "on_delete_parents_clicked"         : on_delete_parents_clicked,
        "on_delete_person_clicked"          : on_delete_person_clicked,
        "on_delete_place_clicked"           : place_view.on_delete_place_clicked,
        "on_delete_source_clicked"          : source_view.on_delete_source_clicked,
        "on_delete_media_clicked"           : media_view.on_delete_media_clicked,
        "on_delete_sp_clicked"              : on_delete_sp_clicked,
        "on_edit_active_person"             : load_active_person,
        "on_edit_selected_people"           : load_selected_people,
        "on_edit_bookmarks_activate"        : on_edit_bookmarks_activate,
        "on_edit_father_clicked"            : on_edit_father_clicked,
        "on_edit_media_clicked"             : media_view.on_edit_media_clicked,
        "on_edit_mother_clicked"            : on_edit_mother_clicked,
        "on_edit_place_clicked"             : place_view.on_edit_place_clicked,
        "on_edit_source_clicked"            : source_view.on_edit_source_clicked,
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
        "on_place_list_button_press_event"  : place_view.on_button_press_event,
        "on_place_list_click_column"        : place_view.on_click_column,
        "on_main_key_release_event"         : on_main_key_release_event,
        "on_add_media_clicked"              : media_view.create_add_dialog,
        "on_media_activate"                 : on_media_activate,
        "on_media_list_select_row"          : media_view.on_select_row,
        "on_media_list_drag_data_get"       : media_view.on_drag_data_get,
        "on_media_list_drag_data_received"  : media_view.on_drag_data_received,
        "on_merge_activate"                 : on_merge_activate,
        "on_places_activate"                : on_places_activate,
        "on_preferences_activate"           : on_preferences_activate,
        "on_reload_plugins_activate"        : Plugins.reload_plugins,
        "on_remove_child_clicked"           : on_remove_child_clicked,
        "on_reports_clicked"                : on_reports_clicked,
        "on_revert_activate"                : on_revert_activate,
        "on_save_activate"                  : on_save_activate,
        "on_save_as_activate"               : on_save_as_activate,
        "on_source_list_button_press_event" : source_view.on_button_press_event,
        "on_sources_activate"               : on_sources_activate,
        "on_spouselist_changed"             : on_spouselist_changed,
        "on_swap_clicked"                   : on_swap_clicked,
        "on_tools_clicked"                  : on_tools_clicked,
        "on_writing_extensions_activate"    : on_writing_extensions_activate,
        })	

    Config.loadConfig(full_update)
    person_list.set_column_visibility(1,Config.id_visible)

    notebook.set_show_tabs(Config.usetabs)
    database.set_iprefix(Config.iprefix)
    database.set_oprefix(Config.oprefix)
    database.set_fprefix(Config.fprefix)
    database.set_sprefix(Config.sprefix)
    database.set_pprefix(Config.pprefix)
    child_list = gtop.get_widget("child_list")
    child_list.set_column_visibility(c_details,Config.show_detail)
    child_list.set_column_justification(c_birth_order,JUSTIFY_RIGHT)
        
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
