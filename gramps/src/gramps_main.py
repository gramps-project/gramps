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
from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gnome.ui
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
import EditPerson
import Marriage
import Find
import VersionControl

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
source_view   = None
toolbar       = None

bookmarks     = None
topWindow     = None
statusbar     = None
gtop          = None
notebook      = None
person_list   = None
database      = None
nameArrow     = None
genderArrow   = None
idArrow       = None
deathArrow    = None
dateArrow     = None

merge_button  = None
sort_column   = 0
sort_direct   = GTK.SORT_ASCENDING
DataFilter    = Filter.Filter("")
c_birth_order = 0
c_name        = 1
c_id          = 2
c_gender      = 3
c_birth_date  = 4
c_details     = 6
c_sort_column = c_birth_order
c_sort_direct = GTK.SORT_ASCENDING
cNameArrow    = None
cGenderArrow  = None
cIDArrow      = None
cDateArrow    = None

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
    Find.Find(person_list,find_goto_to,database.getPersonMap().values())

def on_findname_activate(obj):
    """Display the find box"""
    pass

def find_goto_to(person):
    """Find callback to jump to the selected person"""
    change_active_person(person)
    goto_active_person()
    update_display(0)

def on_gramps_home_page_activate(obj):
    import gnome.url
    gnome.url.show("http://gramps.sourceforge.net")

def on_gramps_mailing_lists_activate(obj):
    import gnome.url
    gnome.url.show("http://sourceforge.net/mail/?group_id=25770")

def on_gramps_report_bug_activate(obj):
    import gnome.url
    gnome.url.show("http://sourceforge.net/tracker/?group_id=25770&atid=385137")
    
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
            gnome.ui.GnomeErrorDialog(msg)
        else:
            import MergeData
            (p1,x) = person_list.get_row_data(person_list.selection[0])
            (p2,x) = person_list.get_row_data(person_list.selection[1])
            MergeData.MergePeople(database,p1,p2,merge_update)
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
    return 1

def on_exit_activate(obj):
    """Prompt to save on exit if needed"""
    if utils.wasModified():
        question = _("Unsaved changes exist in the current database\n") + \
                   _("Do you wish to save the changes?")
        gnome.ui.GnomeQuestionDialog(question,save_query)
    else:    
        gtk.mainquit(obj)

def save_query(value):
    """Catch the reponse to the save on exit question"""
    if value == 0:
        on_save_activate_quit()
    gtk.mainquit(gtop)

#-------------------------------------------------------------------------
#
# Help
#
#-------------------------------------------------------------------------
def on_about_activate(obj):
    """Displays the about box.  Called from Help menu"""
    gnome.ui.GnomeAbout(const.progName,const.version,const.copyright,
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
        SelectChild.NewChild(database,active_family,active_person,
                             update_after_newchild,Config.lastnamegen)

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
    gnome.ui.GnomeQuestionDialog(msg,new_database_response)

def new_database_response(val):
    if val == 1:
        return
    clear_database()
    DbPrompter(database,1)
    
def clear_database():
    """Clear out the database if permission was granted"""
    global active_person, active_father
    global active_family, active_mother
    global active_child, active_spouse
    global id2col,alt2col,person_list

    const.personalEvents = const.initialize_personal_event_list()
    const.personalAttributes = const.initialize_personal_attribute_list()
    const.marriageEvents = const.initialize_marriage_event_list()
    const.familyAttributes = const.initialize_family_attribute_list()
    const.familyRelations = const.initialize_family_relation_list()
    
    database.new()
    topWindow.set_title("GRAMPS")
    active_person = None
    active_father = None
    active_family = None
    active_mother = None
    active_child  = None
    active_spouse = None
    id2col        = {}
    alt2col       = {}

    utils.clearModified()
    utils.clear_timer()
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
    toolbar.set_style(Config.toolbar)

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
    global yname
    global nname
    
    dbname = obj.get_data("dbname")
    getoldrev = obj.get_data("getoldrev")
    filename = dbname.get_full_path(0)
    utils.destroy_passed_object(obj)

    if filename == "" or filename == None:
        return

    clear_database()
    
    if getoldrev.get_active():
        vc = VersionControl.RcsVersionControl(filename)
        VersionControl.RevisionSelect(database,filename,vc,load_revision)
    else:
        auto_save_load(filename)

def auto_save_load(filename):
    global yname, nname
    
    if os.path.isdir(filename):
        dirname = filename
    else:
        dirname = os.path.dirname(filename)
    autosave = "%s/autosave.gramps" % dirname

    if os.path.isfile(autosave):
        q = _("An autosave file exists for %s.\nShould this be loaded instead of the last saved version?") % dirname
        yname = autosave
        nname = filename
        gnome.ui.GnomeQuestionDialog(q,autosave_query)
    else:
        read_file(filename)

def autosave_query(value):
    if value == 0:
        read_file(yname)
    else:
        read_file(nname)
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def read_file(filename):
    base = os.path.basename(filename)
    if base == const.indexFile:
        filename = os.path.dirname(filename)
    elif base == "autosave.gramps":
        filename = os.path.dirname(filename)
    elif not os.path.isdir(filename):
        displayError(_("%s is not a directory") % filename)
        return

    statusbar.set_status(_("Loading %s ...") % filename)

    if load_database(filename) == 1:
        if filename[-1] == '/':
            filename = filename[:-1]
        name = os.path.basename(filename)
        topWindow.set_title("%s - %s" % (name,_("GRAMPS")))
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

    path = filename
    filename = os.path.normpath(filename)
    autosave = "%s/autosave.gramps" % filename
    
    statusbar.set_status(_("Saving %s ...") % filename)

    utils.clearModified()
    utils.clear_timer()

    if os.path.exists(filename):
        if os.path.isdir(filename) == 0:
            displayError(_("%s is not a directory") % filename)
            return
    else:
        try:
            os.mkdir(filename)
        except IOError, msg:
            gnome.ui.GnomeErrorDialog(_("Could not create %s") % filename + "\n" + str(msg))
            return
        except OSError, msg:
            gnome.ui.GnomeErrorDialog(_("Could not create %s") % filename + "\n" + str(msg))
            return
        except:
            gnome.ui.GnomeErrorDialog(_("Could not create %s") % filename)
            return
        
    old_file = filename
    filename = filename + os.sep + const.indexFile
    try:
        WriteXML.exportData(database,filename,load_progress)
    except IOError, msg:
        gnome.ui.GnomeErrorDialog(_("Could not create %s") % filename + "\n" + str(msg))
        return
    except OSError, msg:
        gnome.ui.GnomeErrorDialog(_("Could not create %s") % filename + "\n" + str(msg))
        return

    database.setSavePath(old_file)
    Config.save_last_file(old_file)

    if Config.usevc:
        vc = VersionControl.RcsVersionControl(path)
        vc.checkin(filename,comment,not Config.uncompress)
               
    topWindow.set_title("Gramps - " + database.getSavePath())
    statusbar.set_status("")
    statusbar.set_progress(0)
    if os.path.exists(autosave):
        try:
            os.remove(autosave)
        except:
            pass

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def autosave_database():
    import WriteXML

    path = database.getSavePath()
    filename = os.path.normpath(path)
    utils.clear_timer()

    filename = "%s/autosave.gramps" % (database.getSavePath())
    
    statusbar.set_status(_("autosaving..."));
    try:
        WriteXML.quick_write(database,filename,quick_progress)
        statusbar.set_status(_("autosave complete"));
    except (IOError,OSError):
        statusbar.set_status(_("autosave failed"));
    except:
        import traceback
        traceback.print_exc()

    return 0

#-------------------------------------------------------------------------
#
# Edit Person window for specified people
#
#-------------------------------------------------------------------------
def load_selected_people(obj):
    """Display the selected people in the EditPerson display"""
    if len(person_list.selection) > 5:
        msg = _("You requested too many people to edit at the same time")
        gnome.ui.GnomeErrorDialog(msg)
    else:
        for p in person_list.selection:
            (person,x) = person_list.get_row_data(p)
            load_person(person)

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
        gnome.ui.GnomeQuestionDialog( msg, delete_person_response)
    elif len(person_list.selection) > 1:
        gnome.ui.GnomeErrorDialog(_("Currently, you can only delete one person at a time"))

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
            (active_person,x) = person_list.get_row_data(row)
    person_list.thaw()
    
def merge_update(p1,p2):
    remove_from_person_list(p1)
    remove_from_person_list(p2)
    redisplay_person_list(p1)
    
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
        (person,x) = obj.get_row_data(row)
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
    change_sort(column)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
col_map = [ 5, 1, 2, 6, 7 ]

def set_sort_arrow(column,direct):
    col_arr = [ nameArrow, idArrow, genderArrow, dateArrow, deathArrow]

    arrow = col_arr[column]
    for a in col_arr:
        if arrow != a:
            a.hide()
    arrow.show()
    if direct == GTK.SORT_ASCENDING:
        arrow.set(GTK.ARROW_DOWN,2)
    else:
        arrow.set(GTK.ARROW_UP,2)
    
def change_sort(column,change=1):
    global sort_direct
    global sort_column

    col_arr = [ nameArrow, idArrow, genderArrow, dateArrow, deathArrow]

    arrow = col_arr[column]
    for a in col_arr:
        if arrow != a:
            a.hide()
    arrow.show()

    person_list.set_sort_column(col_map[column])
    person_list.set_sort_type(sort_direct)

    sort_person_list()

    if change:
        if sort_column == column:
            if sort_direct == GTK.SORT_DESCENDING:
                sort_direct = GTK.SORT_ASCENDING
                arrow.set(GTK.ARROW_DOWN,2)
            else:
                sort_direct = GTK.SORT_DESCENDING
                arrow.set(GTK.ARROW_UP,2)
        else:
            sort_direct = GTK.SORT_ASCENDING
            arrow.set(GTK.ARROW_DOWN,2)
    sort_column = column

    if id2col.has_key(active_person):
        row = person_list.find_row_from_data(id2col[active_person])
        person_list.moveto(row)
    Config.save_sort_cols("person",sort_column,sort_direct)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def sort_person_list():
    person_list.freeze()
    person_list.sort()
    person_list.sort()
    if ListColors.get_enable():
        try:
            oddbg = gtk.GdkColor(ListColors.oddbg[0],ListColors.oddbg[1],ListColors.oddbg[2])
            oddfg = gtk.GdkColor(ListColors.oddfg[0],ListColors.oddfg[1],ListColors.oddfg[2])
            evenbg = gtk.GdkColor(ListColors.evenbg[0],ListColors.evenbg[1],ListColors.evenbg[2])
            evenfg = gtk.GdkColor(ListColors.evenfg[0],ListColors.evenfg[1],ListColors.evenfg[2])
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
            person_list.unselect_all()
            person_list.select_row(column,0)
            person_list.moveto(column)
    else:
        if person_list.rows > 0:
            person_list.unselect_all()
            person_list.select_row(0,0)
            person_list.moveto(0)
            (person,x) = person_list.get_row_data(0)
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
    return 0
	
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
        child_change_sort(clist,c_name,cNameArrow)
    elif column == c_gender:
        child_change_sort(clist,c_gender,cGenderArrow)
    elif column == c_id:
        child_change_sort(clist,c_id,cIDArrow)
    elif (column == c_birth_order) or (column == c_birth_date):
        child_change_sort(clist,c_birth_order,cDateArrow)
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
    cIDArrow.hide()
    cGenderArrow.hide()
    arrow.show()
    
    if c_sort_column == column:
        if c_sort_direct == GTK.SORT_DESCENDING:
            c_sort_direct = GTK.SORT_ASCENDING
            arrow.set(GTK.ARROW_DOWN,2)
        else:
            c_sort_direct = GTK.SORT_DESCENDING
            arrow.set(GTK.ARROW_UP,2)
    else:
        c_sort_direct = GTK.SORT_ASCENDING
    c_sort_column = column
    clist.set_sort_type(c_sort_direct)
    clist.set_sort_column(c_sort_column)
    clist.set_reorderable(c_sort_column == c_birth_order)

def sort_child_list(clist):
    clist.freeze()
    clist.sort()
    clist.sort()
    if ListColors.get_enable():
        try:
            oddbg = gtk.GdkColor(ListColors.oddbg[0],ListColors.oddbg[1],ListColors.oddbg[2])
            oddfg = gtk.GdkColor(ListColors.oddfg[0],ListColors.oddfg[1],ListColors.oddfg[2])
            evenbg = gtk.GdkColor(ListColors.evenbg[0],ListColors.evenbg[1],ListColors.evenbg[2])
            evenfg = gtk.GdkColor(ListColors.evenfg[0],ListColors.evenfg[1],ListColors.evenfg[2])
            ancestorfg = gtk.GdkColor(ListColors.ancestorfg[0],ListColors.ancestorfg[1],ListColors.ancestorfg[2])
            rows = clist.rows
            for i in range(0,rows):
                clist.set_background(i,(evenbg,oddbg)[i%2])
                person = clist.get_row_data(i)
                if (person.getAncestor()):
                    clist.set_foreground(i,ancestorfg)
                else:
                    clist.set_foreground(i,(evenfg,oddfg)[i%2])
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
    if (c_sort_direct == GTK.SORT_DESCENDING):
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
        gnome.ui.GnomeWarningDialog(_("Invalid move.  Children must be ordered by birth date."))
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
    if (c_sort_direct == GTK.SORT_DESCENDING):
        clist_order.reverse()

    # Update the clist indices so any change of sorting works
    i = 0
    for tmp in clist_order:
    	clist.set_text(i, c_birth_order, "%2d"%(new_order[tmp]+1))
        i = i + 1

    # Need to save the changed order
    utils.modified()

def on_open_activate(obj):
    wFs = libglade.GladeXML(const.revisionFile, "dbopen")
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
        gnome.ui.GnomeQuestionDialog(msg,revert_query)
    else:
        msg = _("Cannot revert to a previous database, since one does not exist")
        gnome.ui.GnomeWarningDialog(msg)

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
        utils.clear_timer()

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
        on_save_as_activate(None)
    else:
        if Config.usevc and Config.vc_comment:
            display_comment_box(database.getSavePath())
        else:
            save_file(database.getSavePath(),_("No Comment Provided"))

def display_comment_box(filename):
    """Displays a dialog box, prompting for a revison control comment"""
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
                              sort.build_sort_date(bday),
                              sort.build_sort_date(dday)])

        person_list.set_row_data(0,pos)

        if Config.hide_altnames == 0:
            for name in person.getAlternateNames():
                pos2 = (person,0)
                alt2col[person].append(pos2)
                person_list.insert(0,[gname(name,1),person.getId(),
                                      gender,bday.getQuoteDate(),
                                      dday.getQuoteDate(),
                                      sort.build_sort_name(name),
                                      sort.build_sort_date(bday),
                                      sort.build_sort_date(dday)])

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
        typeMenu = gtk.GtkMenu()
        if main_family:
            menuitem = gtk.GtkMenuItem(_("Birth"))
            menuitem.set_data("parents",main_family)
            menuitem.connect("activate",on_current_type_changed)
            menuitem.show()
            typeMenu.append(menuitem)
        for fam in family_types:
            if active_person == fam[0].getFather():
                menuitem = gtk.GtkMenuItem("%s/%s" % (fam[1],fam[2]))
            else:
                menuitem = gtk.GtkMenuItem("%s/%s" % (fam[2],fam[1]))
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
            myMenu = gtk.GtkMenu()
            index = 0
            opt_index = 0
            for f in active_person.getFamilyList():
                person = None
                if f.getMother() == active_person:
                    if f.getFather() != None:
                        person = f.getFather()
                else:		
                    if f.getMother() != None:
                        person = f.getMother()

                menuitem = gtk.GtkMenuItem(Config.nameof(person))
                myMenu.append(menuitem)
                menuitem.set_data("person",person)
                menuitem.set_data("family",f)
                menuitem.connect("activate",on_spouselist_changed)
                menuitem.show()
                if family and f == family:
                    opt_index = index
                index = index + 1
            gtop.get_widget("fv_spouse").set_menu(myMenu)
            gtop.get_widget("fv_spouse").set_history(opt_index)
            gtop.get_widget("lab_or_list").set_page(1)
            gtop.get_widget("edit_sp").set_sensitive(1)
            gtop.get_widget("delete_sp").set_sensitive(1)
        elif number_of_families == 1:
            gtop.get_widget("lab_or_list").set_page(0)
            f = active_person.getFamilyList()[0]
            if active_person != f.getFather():
                spouse = f.getFather()
            else:
                spouse = f.getMother()
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
            if family:
                display_marriage(family)
            else:
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
        child_list.sort(sort.by_birthdate)

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
    while gtk.events_pending():
        gtk.mainiteration()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def quick_progress(value):
    gtk.threads_enter()
    statusbar.set_progress(value)
    while gtk.events_pending():
        gtk.mainiteration()
    gtk.threads_leave()

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
    gnome.ui.GnomeErrorDialog(msg)
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
    
    bsn = sort.build_sort_name
    bsd = sort.build_sort_date
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

            name = person.getPrimaryName()
            bday = person.getBirth().getDateObj()
            dday = person.getDeath().getDateObj()
            sort_bday = bsd(bday)
            sort_dday = bsd(dday)
            qbday = bday.getQuoteDate()
            qdday = dday.getQuoteDate()
            pid = person.getId()

            values = [gname(name,0), pid, gender, qbday, qdday,
                      bsn(name), sort_bday, sort_dday ]
            person_list.insert(0,values)
            person_list.set_row_data(0,pos)

            if Config.hide_altnames:
                continue

            for name in person.getAlternateNames():
                pos = (person,0)
                new_alt2col[person].append(pos)

                values = [gname(name,1), pid, gender, qbday, qdday,
                          bsn(name), sort_bday, sort_dday]
                person_list.insert(0,values)
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
        gnome.ui.GnomeErrorDialog(_("No default/home person has been set"))

#-------------------------------------------------------------------------
#
# Bookmark interface
#
#-------------------------------------------------------------------------
def on_add_bookmark_activate(obj):
    bookmarks.add(active_person)
    name = Config.nameof(active_person)
    statusbar.set_status(_("%s has been bookmarked") % name)
    gtk.timeout_add(5000,modify_statusbar)

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
        gnome.ui.GnomeQuestionDialog(msg,set_person)

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
    global person_list
    global topWindow, preview, merge_button
    global nameArrow, dateArrow, deathArrow, idArrow, genderArrow
    global cNameArrow, cDateArrow, cIDArrow, cGenderArrow, toolbar
    global sort_column, sort_direct

    gtk.rc_parse(const.gtkrcFile)

    if os.getuid() == 0:
        msg = _("You are running GRAMPS as the 'root' user.\nThis account is not meant for normal application use.")
        gnome.ui.GnomeWarningDialog(msg)

    database = RelDataBase()

    Plugins.load_plugins(const.pluginsDir)
    Plugins.load_plugins(os.path.expanduser("~/.gramps/plugins"))
    Filter.load_filters(const.filtersDir)
    Filter.load_filters(os.path.expanduser("~/.gramps/filters"))

    (sort_column,sort_direct) = Config.get_sort_cols("person",sort_column,sort_direct)

    Config.loadConfig(full_update)

    gtop = libglade.GladeXML(const.gladeFile, "gramps")
    toolbar = gtop.get_widget("toolbar1")
    toolbar.set_style(Config.toolbar)

    statusbar   = gtop.get_widget("statusbar")
    topWindow   = gtop.get_widget("gramps")
    person_list = gtop.get_widget("person_list")
    filter_list = gtop.get_widget("filter_list")
    notebook    = gtop.get_widget(NOTEBOOK)
    nameArrow   = gtop.get_widget("nameSort")
    genderArrow = gtop.get_widget("genderSort")
    idArrow     = gtop.get_widget("idSort")
    dateArrow   = gtop.get_widget("dateSort")
    deathArrow  = gtop.get_widget("deathSort")
    merge_button= gtop.get_widget("merge")

    Plugins.build_report_menu(gtop.get_widget("reports_menu"),menu_report)
    Plugins.build_tools_menu(gtop.get_widget("tools_menu"),menu_tools)
    Plugins.build_export_menu(gtop.get_widget("export1"),export_callback)
    Plugins.build_import_menu(gtop.get_widget("import1"),import_callback)
    
    canvas = gtop.get_widget("canvas1")
    pedigree_view = PedigreeView(canvas,modify_statusbar,\
                                 statusbar,change_active_person,\
                                 load_person)
    place_view  = PlaceView(database,gtop,update_display)
    source_view = SourceView(database,gtop,update_display)
    media_view  = MediaView(database,gtop,update_display)

    cNameArrow  = gtop.get_widget("cNameSort")
    cGenderArrow= gtop.get_widget("cGenderSort")
    cIDArrow    = gtop.get_widget("cIDSort")
    cDateArrow  = gtop.get_widget("cDateSort")
    person_list.set_column_visibility(5,0)
    person_list.set_column_visibility(6,0)
    person_list.set_column_visibility(7,0)
    fw = gtop.get_widget('filter')
    filter_list.set_menu(Filter.build_filter_menu(on_filter_name_changed,fw))
    
    fw.set_sensitive(0)

    # set the window icon 
    topWindow.set_icon(gtk.GtkPixmap(topWindow,const.icon))
    
    person_list.column_titles_active()

    change_sort(sort_column,sort_direct==GTK.SORT_DESCENDING)
    set_sort_arrow(sort_column,sort_direct)

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
        "on_findname_activate"              : on_findname_activate,
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
        "on_gramps_home_page_activate"      : on_gramps_home_page_activate,
        "on_gramps_report_bug_activate"     : on_gramps_report_bug_activate,
        "on_gramps_mailing_lists_activate"  : on_gramps_mailing_lists_activate,
        "on_writing_extensions_activate"    : on_writing_extensions_activate,
        })	

    person_list.set_column_visibility(1,Config.id_visible)

    notebook.set_show_tabs(Config.usetabs)
    database.set_iprefix(Config.iprefix)
    database.set_oprefix(Config.oprefix)
    database.set_fprefix(Config.fprefix)
    database.set_sprefix(Config.sprefix)
    database.set_pprefix(Config.pprefix)
    child_list = gtop.get_widget("child_list")
    child_list.set_column_visibility(c_details,Config.show_detail)
    child_list.set_column_justification(c_birth_order,GTK.JUSTIFY_RIGHT)
        
    if arg != None:
        read_file(arg)
    elif Config.lastfile != None and Config.lastfile != "" and Config.autoload:
        auto_save_load(Config.lastfile)
    else:
        DbPrompter(database,0)

    if Config.autosave_int != 0:
        utils.enable_autosave(autosave_database,Config.autosave_int)

    database.setResearcher(Config.owner)
    gtk.mainloop()

#-------------------------------------------------------------------------
#
# Make sure a database is opened
#
#-------------------------------------------------------------------------
class DbPrompter:
    def __init__(self,db,want_new):
        self.db = db
        self.want_new = want_new
        self.show()

    def show(self):
        opendb = libglade.GladeXML(const.gladeFile, "opendb")
        opendb.signal_autoconnect({
            "on_open_ok_clicked" : self.open_ok_clicked,
            "on_open_cancel_clicked" : self.open_cancel_clicked,
            "on_opendb_delete_event": self.open_delete_event,
            })
        self.new = opendb.get_widget("new")
        if self.want_new:
            self.new.set_active(1)

    def open_ok_clicked(self,obj):
        if self.new.get_active():
            self.save_as_activate()
        else:
            self.open_activate()
        utils.destroy_passed_object(obj)

    def save_as_activate(self):
        wFs = libglade.GladeXML (const.gladeFile, FILESEL)
        wFs.signal_autoconnect({
            "on_ok_button1_clicked": self.save_ok_button_clicked,
            "destroy_passed_object": self.cancel_button_clicked,
            })

    def save_ok_button_clicked(self,obj):
        filename = obj.get_filename()
        if filename:
            utils.destroy_passed_object(obj)
            if Config.usevc and Config.vc_comment:
                display_comment_box(filename)
            else:
                save_file(filename,_("No Comment Provided"))

    def open_activate(self):
        wFs = libglade.GladeXML(const.revisionFile, "dbopen")
        wFs.signal_autoconnect({
            "on_ok_button1_clicked": self.ok_button_clicked,
            "destroy_passed_object": self.cancel_button_clicked,
            })

        self.fileSelector = wFs.get_widget("dbopen")
        self.dbname = wFs.get_widget("dbname")
        self.getoldrev = wFs.get_widget("getoldrev")
        self.dbname.set_default_path(Config.db_dir)
        self.getoldrev.set_sensitive(Config.usevc)

    def cancel_button_clicked(self,obj):
        utils.destroy_passed_object(obj)
        self.show()
        
    def ok_button_clicked(self,obj):
        filename = self.dbname.get_full_path(0)

        if not filename:
            return

        utils.destroy_passed_object(obj)
        clear_database()
    
        if self.getoldrev.get_active():
            vc = VersionControl.RcsVersionControl(filename)
            VersionControl.RevisionSelect(self.db,filename,vc,load_revision,self.show)
        else:
            read_file(filename)

    def open_delete_event(self,obj,event):
        gtk.mainquit()

    def open_cancel_clicked(self,obj):
        gtk.mainquit()


#-------------------------------------------------------------------------
#
# Start it all
#
#-------------------------------------------------------------------------
if __name__ == '__main__':
    main(None)

