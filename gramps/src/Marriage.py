#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modiy
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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *
import GDK

import libglade
import os
import intl
import Sources
import AttrEdit
import EventEdit

_ = intl.gettext

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------

import const
import Config
import utils
from RelLib import *
import RelImage
import ImageSelect

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
MARRIAGE   = "m"

#-------------------------------------------------------------------------
#
# Marriage class
#
#-------------------------------------------------------------------------
class Marriage:

    #-------------------------------------------------------------------------
    #
    # Initializes the class, and displays the window
    #
    #-------------------------------------------------------------------------
    def __init__(self,family,db):
        self.family = family
        self.db = db
        self.path = db.getSavePath()

        self.top = libglade.GladeXML(const.marriageFile,"marriageEditor")
        top_window = self.get_widget("marriageEditor")
        fid = "f%s" % family.getId()
        plwidget = self.top.get_widget("photolist")
        self.gallery = ImageSelect.Gallery(family, self.path, fid, plwidget, db)
        self.top.signal_autoconnect({
            "destroy_passed_object" : on_cancel_edit,
            "on_add_attr_clicked" : on_add_attr_clicked,
            "on_addphoto_clicked" : self.gallery.on_add_photo_clicked,
            "on_attr_list_select_row" : on_attr_list_select_row,
            "on_close_marriage_editor" : on_close_marriage_editor,
            "on_delete_attr_clicked" : on_delete_attr_clicked,
            "on_delete_event" : on_delete_event,
            "on_deletephoto_clicked" : self.gallery.on_delete_photo_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_marriageAddBtn_clicked" : on_add_clicked,
            "on_marriageDeleteBtn_clicked" : on_delete_clicked,
            "on_marriageEventList_select_row" : on_select_row,
            "on_marriageUpdateBtn_clicked" : on_update_clicked,
            "on_photolist_button_press_event" : self.gallery.on_photolist_button_press_event,
            "on_photolist_select_icon" : self.gallery.on_photo_select_icon,
            "on_update_attr_clicked" : on_update_attr_clicked,
            })

        text_win = self.get_widget("marriageTitle")
        title = _("%s and %s") % (Config.nameof(family.getFather()),
                                  Config.nameof(family.getMother()))
        text_win.set_text(title)
        
        self.event_list = self.get_widget("marriageEventList")

        # widgets
        self.date_field  = self.get_widget("marriageDate")
        self.place_field = self.get_widget("marriagePlace")
        self.cause_field = self.get_widget("marriageCause")
        self.name_field  = self.get_widget("marriageEventName")
        self.descr_field = self.get_widget("marriageDescription")
        self.type_field  = self.get_widget("marriage_type")
        self.notes_field = self.get_widget("marriageNotes")
        self.gid = self.get_widget("gid")
        self.attr_list = self.get_widget("attr_list")
        self.attr_type = self.get_widget("attr_type")
        self.attr_value = self.get_widget("attr_value")
        self.event_details = self.get_widget("event_details")
        self.attr_details_field = self.get_widget("attr_details")

        self.event_list.set_column_visibility(3,Config.show_detail)
        self.attr_list.set_column_visibility(2,Config.show_detail)

        self.elist = family.getEventList()[:]
        self.alist = family.getAttributeList()[:]
        self.lists_changed = 0

        # set initial data
        self.gallery.load_images()

        self.type_field.set_popdown_strings(const.familyRelations)
        frel = const.display_frel(family.getRelationship())
        self.type_field.entry.set_text(frel)
        self.gid.set_text(family.getId())
        self.gid.set_editable(Config.id_edit)
        
        # stored object data
        top_window.set_data(MARRIAGE,self)
        self.event_list.set_data(MARRIAGE,self)
        self.attr_list.set_data(MARRIAGE,self)

        # set notes data
        self.notes_field.set_point(0)
        self.notes_field.insert_defaults(family.getNote())
        self.notes_field.set_word_wrap(1)

        # Typing CR selects OK button
        top_window.editable_enters(self.notes_field);
        top_window.editable_enters(self.get_widget("combo-entry1"));
        
        self.redraw_event_list()
        self.redraw_attr_list()
        top_window.show()

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def update_lists(self):
        self.family.setEventList(self.elist)
        self.family.setAttributeList(self.alist)

    #---------------------------------------------------------------------
    #
    # redraw_attr_list - redraws the attribute list for the person
    #
    #---------------------------------------------------------------------
    def redraw_attr_list(self):
        utils.redraw_list(self.alist,self.attr_list,disp_attr)

    #-------------------------------------------------------------------------
    #
    # redraw_events - redraws the event list by deleting all the entries and
    # reconstructing the list
    #
    #-------------------------------------------------------------------------
    def redraw_event_list(self):
        utils.redraw_list(self.elist,self.event_list,disp_event)

    #-------------------------------------------------------------------------
    #
    # get_widget - returns the widget associated with the specified name
    #
    #-------------------------------------------------------------------------
    def get_widget(self,name):
        return self.top.get_widget(name)


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def did_data_change(obj):
    family_obj = obj.get_data(MARRIAGE)

    changed = 0
    relation = family_obj.type_field.entry.get_text()
    if const.save_frel(relation) != family_obj.family.getRelationship():
        changed = 1

    text = family_obj.notes_field.get_chars(0,-1)
    if text != family_obj.family.getNote():
        changed = 1
        
    if family_obj.lists_changed:
        changed = 1

    idval = family_obj.gid.get_text()
    if family_obj.family.getId() != idval:
        changed = 1

    return changed

#-------------------------------------------------------------------------
#
# on_cancel_edit
#
#-------------------------------------------------------------------------
def on_cancel_edit(obj):

    if did_data_change(obj):
        global quit
        q = _("Data was modified. Are you sure you want to abandon your changes?")
        quit = obj
        GnomeQuestionDialog(q,cancel_callback)
    else:
        utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def cancel_callback(a):
    if a==0:
        utils.destroy_passed_object(quit)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_delete_event(obj,b):
    global quit

    if did_data_change(obj):
        q = _("Data was modified. Are you sure you want to abandon your changes?")
        quit = obj
        GnomeQuestionDialog(q,cancel_callback)
        return 1
    else:
        utils.destroy_passed_object(obj)
        return 0

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_close_marriage_editor(obj):
    family_obj = obj.get_data(MARRIAGE)

    idval = family_obj.gid.get_text()
    family = family_obj.family
    if idval != family.getId():
        m = family_obj.db.getFamilyMap() 
        if not m.has_key(idval):
            if m.has_key(family.getId()):
                del m[family.getId()]
                m[idval] = family
            family.setId(idval)
            utils.modified()
        else:
            msg1 = _("GRAMPS ID value was not changed.")
            GnomeWarningDialog("%s" % msg1)

    relation = family_obj.type_field.entry.get_text()
    if const.save_frel(relation) != family_obj.family.getRelationship():
        father = family_obj.family.getFather()
        mother = family_obj.family.getMother()
        if father.getGender() == mother.getGender():
            family_obj.family.setRelationship("Partners")
        else:
            val = const.save_frel(relation)
            if val == "Partners":
                val = "Unknown"
            if father.getGender() == Person.female or \
               mother.getGender() == Person.male:
                family_obj.family.setFather(mother)
                family_obj.family.setMother(father)
            family_obj.family.setRelationship(val)
        utils.modified()

    text = family_obj.notes_field.get_chars(0,-1)
    if text != family_obj.family.getNote():
        family_obj.family.setNote(text)
        utils.modified()

    utils.destroy_passed_object(family_obj.get_widget("marriageEditor"))

    family_obj.update_lists()
    if family_obj.lists_changed:
        utils.modified()

#-------------------------------------------------------------------------
#
# on_add_clicked - creates a new event from the data displayed in the
# window. Special care has to be take for the marriage and divorce
# events, since they are not stored in the event list. 
#
#-------------------------------------------------------------------------
def on_add_clicked(obj):
    mobj = obj.get_data(MARRIAGE)
    father = mobj.family.getFather()
    mother = mobj.family.getMother()
    if father and mother:
        name = _("%s and %s") % (father.getPrimaryName().getName(),
                                 mother.getPrimaryName().getName())
    elif father:
        name = father.getPrimaryName().getName()
    else:
        name = mother.getPrimaryName().getName()
    EventEdit.EventEditor(mobj,name,const.marriageEvents,const.save_pevent,None,0)

#-------------------------------------------------------------------------
#
# on_update_clicked - updates the selected event with the values in the
# current display
#
#-------------------------------------------------------------------------
def on_update_clicked(obj):
    if len(obj.selection) <= 0:
        return

    mobj = obj.get_data(MARRIAGE)
    event = obj.get_row_data(obj.selection[0])
    father = mobj.family.getFather()
    mother = mobj.family.getMother()
    if father and mother:
        name = _("%s and %s") % (father.getPrimaryName().getName(),
                                 mother.getPrimaryName().getName())
    elif father:
        name = father.getPrimaryName().getName()
    else:
        name = mother.getPrimaryName().getName()
    EventEdit.EventEditor(mobj,name,const.marriageEvents,const.save_pevent,event,0)

#-------------------------------------------------------------------------
#
# on_delete_clicked - deletes the currently displayed event from the
# marriage event list.  Special care needs to be taken for the Marriage
# and Divorce events, since they are not stored in the event list
#
#-------------------------------------------------------------------------
def on_delete_clicked(obj):
    family_obj = obj.get_data(MARRIAGE)
    if utils.delete_selected(obj,family_obj.elist):
        family_obj.lists_changed = 1
        family_obj.redraw_event_list()

#-------------------------------------------------------------------------
#
# on_select_row - updates the internal data attached to the passed object,
# then updates the display.
#
#-------------------------------------------------------------------------
def on_select_row(obj,row,b,c):
    family_obj = obj.get_data(MARRIAGE)
    event = obj.get_row_data(row)
    
    family_obj.date_field.set_text(event.getDate())
    family_obj.place_field.set_text(event.getPlaceName())
    family_obj.cause_field.set_text(event.getCause())
    family_obj.name_field.set_label(const.display_fevent(event.getName()))
    family_obj.event_details.set_text(utils.get_detail_text(event))
    family_obj.descr_field.set_text(event.getDescription())


#-------------------------------------------------------------------------
#
# on_attr_list_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_attr_list_select_row(obj,row,b,c):
    family_obj = obj.get_data(MARRIAGE)
    attr = obj.get_row_data(row)

    family_obj.attr_type.set_label(const.display_fattr(attr.getType()))
    family_obj.attr_value.set_text(attr.getValue())
    family_obj.attr_details_field.set_text(utils.get_detail_text(attr))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_attr_clicked(obj):
    if len(obj.selection) > 0:
        row = obj.selection[0]
        mobj = obj.get_data(MARRIAGE)
        attr = obj.get_row_data(row)
        father = mobj.family.getFather()
        mother = mobj.family.getMother()
        if father and mother:
            name = _("%s and %s") % (father.getPrimaryName().getName(),
                                     mother.getPrimaryName().getName())
        elif father:
            name = father.getPrimaryName().getName()
        else:
            name = mother.getPrimaryName().getName()
        AttrEdit.AttributeEditor(mobj,attr,name,const.familyAttributes)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_attr_clicked(obj):
    family_obj = obj.get_data(MARRIAGE)
    if utils.delete_selected(obj,family_obj.alist):
        family_obj.lists_changed = 1
        family_obj.redraw_attr_list()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_attr_clicked(obj):
    mobj = obj.get_data(MARRIAGE)
    father = mobj.family.getFather()
    mother = mobj.family.getMother()
    if father and mother:
        name = _("%s and %s") % (father.getPrimaryName().getName(),
                                 mother.getPrimaryName().getName())
    elif father:
        name = father.getPrimaryName().getName()
    else:
        name = mother.getPrimaryName().getName()
    AttrEdit.AttributeEditor(mobj,None,name,const.familyAttributes)


#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_attr(attr):
    detail = utils.get_detail_flags(attr)
    return [const.display_fattr(attr.getType()),attr.getValue(),detail]

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_event(event):
    return [const.display_fevent(event.getName()), event.getQuoteDate(),
            event.getPlaceName(), utils.get_detail_flags(event)]
