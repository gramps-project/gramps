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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *

import gnome.mime
import libglade
import os
import intl
import Sources

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

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
INDEX      = "i"
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

        self.selectedIcon = 0

        self.top = libglade.GladeXML(const.marriageFile,"marriageEditor")
        self.top.signal_autoconnect({
            "on_marriageAddBtn_clicked" : on_add_clicked,
            "on_marriageUpdateBtn_clicked" : on_update_clicked,
            "on_marriageDeleteBtn_clicked" : on_delete_clicked,
            "on_marriageEventList_select_row" : on_select_row,
            "on_attr_list_select_row" : on_attr_list_select_row,
            "on_add_attr_clicked" : on_add_attr_clicked,
            "on_update_attr_clicked" : on_update_attr_clicked,
            "on_delete_attr_clicked" : on_delete_attr_clicked,
            "on_showsource_clicked" : on_showsource_clicked,
            "on_photolist_select_icon" : on_photo_select_icon,
            "on_photolist_button_press_event" : on_photolist_button_press_event,
            "on_addphoto_clicked" : on_add_photo_clicked,
            "on_deletephoto_clicked" : on_delete_photo_clicked,
            "on_close_marriage_editor" : on_close_marriage_editor,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        top_window = self.get_widget("marriageEditor")
        text_win = self.get_widget("marriageTitle")
        text_win.set_text(Config.nameof(family.getFather()) + " and " + \
                          Config.nameof(family.getMother()))
        
        self.event_list = self.get_widget("marriageEventList")
        self.photo_list = self.get_widget("photolist")

        # widgets
        self.date_field  = self.get_widget("marriageDate")
        self.place_field = self.get_widget("marriagePlace")
        self.name_field  = self.get_widget("marriageEventName")
        self.descr_field = self.get_widget("marriageDescription")
        self.type_field  = self.get_widget("marriage_type")
        self.notes_field = self.get_widget("marriageNotes")
        self.attr_list = self.get_widget("attr_list")
        self.attr_type = self.get_widget("attr_type")
        self.attr_value = self.get_widget("attr_value")
        self.event_details = self.get_widget("event_details")
        self.attr_details_field = self.get_widget("attr_details")

        self.event_list.set_column_visibility(3,Config.show_detail)
        self.attr_list.set_column_visibility(2,Config.show_detail)

        self.elist = family.getEventList()[:]
        self.alist = family.getAttributeList()[:]
        self.events_changed = 0
        self.attr_changed = 0

        # set initial data
        mevent_list = self.get_widget("marriageEvent")
        self.load_images()

        self.type_field.set_popdown_strings(const.familyRelations)
        self.type_field.entry.set_text(const.display_frel(family.getRelationship()))
        
        # stored object data
        top_window.set_data(MARRIAGE,self)
        self.event_list.set_data(MARRIAGE,self)
        self.event_list.set_data(INDEX,-1)
        self.attr_list.set_data(MARRIAGE,self)
        self.attr_list.set_data(INDEX,-1)

        # set notes data
        self.notes_field.set_point(0)
        self.notes_field.insert_defaults(family.getNote())
        self.notes_field.set_word_wrap(1)

        self.redraw_events()
        self.redraw_attr_list()
        top_window.show()

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def update_events(self):
        self.family.setEventList(self.elist)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def update_attributes(self):
        self.family.setAttributeList(self.alist)

    #---------------------------------------------------------------------
    #
    # redraw_attr_list - redraws the attribute list for the person
    #
    #---------------------------------------------------------------------
    def redraw_attr_list(self):
        self.attr_list.freeze()
        self.attr_list.clear()

	self.attr_index = 0
        for attr in self.alist:
            details = get_detail_flags(attr)
            self.attr_list.append([const.display_fattr(attr.getType()),\
                                   attr.getValue(),details])
            self.attr_list.set_row_data(self.attr_index,attr)
            self.attr_index = self.attr_index + 1

        current_row = self.attr_list.get_data(INDEX)
        
        if self.attr_index > 0:
            if current_row <= 0:
                current_row = 0
            elif self.attr_index <= current_row:
                current_row = current_row - 1
            self.attr_list.select_row(current_row,0)
            self.attr_list.moveto(current_row,0)
        self.attr_list.set_data(INDEX,current_row)
        self.attr_list.thaw()

    #-------------------------------------------------------------------------
    #
    # add_event - adds the event to the window, attaching the event structure
    # to each row.
    #
    #-------------------------------------------------------------------------
    def add_event(self,text,event):
        if not event:
            return
        detail = get_detail_flags(event)
        self.event_list.append([text,event.getQuoteDate(),event.getPlace(),detail])
        self.event_list.set_row_data(self.lines,event)
        self.lines = self.lines + 1

    #-------------------------------------------------------------------------
    #
    # add_thumbnail - Scale the image and add it to the IconList.  Currently, 
    # there seems to be a problem with either GdkImlib. A reference has to be
    # kept to the image, or it gets lost.  This is supposed to be a known
    # imlib problem
    #
    #-------------------------------------------------------------------------
    def add_thumbnail(self,photo):

        src = photo.getPath()
        thumb = self.db.getSavePath() + os.sep + ".thumb" + os.sep + \
                os.path.basename(src)

        RelImage.check_thumb(src,thumb,const.thumbScale)

        self.photo_list.append(thumb,photo.getDescription())

    #-------------------------------------------------------------------------
    #
    # load_images - clears the currentImages list to free up any cached 
    # Imlibs.  Then add each photo in the person's list of photos to the 
    # photolist window.
    #
    #-------------------------------------------------------------------------
    def load_images(self):

        if len(self.family.getPhotoList()) == 0:
            return
        self.photo_list.freeze()
        self.photo_list.clear()
        for photo in self.family.getPhotoList():
            self.add_thumbnail(photo)
        self.photo_list.thaw()

    #-------------------------------------------------------------------------
    #
    # redraw_events - redraws the event list by deleting all the entries and
    # reconstructing the list
    #
    #-------------------------------------------------------------------------
    def redraw_events(self):
        self.lines = 0
        self.event_list.freeze()
        self.event_list.clear()

        for event in self.elist:
            self.add_event(const.display_fevent(event.getName()),event)

        current_row = self.event_list.get_data(INDEX)
        if current_row == None:
            current_row = -1
        
        if self.lines >= 0:
            if current_row < 0:
                current_row = 0
            elif self.lines < current_row:
                current_row = current_row - 1
            self.event_list.select_row(current_row,0)
            self.event_list.moveto(current_row,0)
        self.event_list.set_data(INDEX,current_row)
        self.event_list.thaw()

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
def on_close_marriage_editor(obj):
    family_obj = obj.get_data(MARRIAGE)

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
            family_obj.family.setRelationship(val)
        utils.modified()

    text = family_obj.notes_field.get_chars(0,-1)
    if text != family_obj.family.getNote():
        family_obj.family.setNote(text)
        utils.modified()

    utils.destroy_passed_object(family_obj.get_widget("marriageEditor"))

    family_obj.update_events()
    if family_obj.events_changed:
        utils.modified()

    family_obj.update_events()
    if family_obj.events_changed:
        utils.modified()

#-------------------------------------------------------------------------
#
# on_add_clicked - creates a new event from the data displayed in the
# window. Special care has to be take for the marriage and divorce
# events, since they are not stored in the event list. 
#
#-------------------------------------------------------------------------
def on_add_clicked(obj):
    editor = EventEditor(obj.get_data(MARRIAGE),None)

#-------------------------------------------------------------------------
#
# on_update_clicked - updates the selected event with the values in the
# current display
#
#-------------------------------------------------------------------------
def on_update_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return

    family_obj = obj.get_data(MARRIAGE)
    event = obj.get_row_data(row)
    editor = EventEditor(family_obj,event)

#-------------------------------------------------------------------------
#
# on_delete_clicked - deletes the currently displayed event from the
# marriage event list.  Special care needs to be taken for the Marriage
# and Divorce events, since they are not stored in the event list
#
#-------------------------------------------------------------------------
def on_delete_clicked(obj):
    family_obj = obj.get_data(MARRIAGE)
    row = obj.get_data(INDEX)
    if row < 0:
        return
    
    del family_obj.elist[row]

    if row > len(family_obj.elist)-1:
        obj.set_data(INDEX,row-1)
        
    family_obj.redraw_events()
    family_obj.events_changed = 1
    utils.modified()

#-------------------------------------------------------------------------
#
# on_select_row - updates the internal data attached to the passed object,
# then updates the display.
#
#-------------------------------------------------------------------------
def on_select_row(obj,row,b,c):
    obj.set_data(INDEX,row)
    family_obj = obj.get_data(MARRIAGE)
    event = obj.get_row_data(row)
    
    family_obj.date_field.set_text(event.getDate())
    family_obj.place_field.set_text(event.getPlace())
    family_obj.name_field.set_label(const.display_fevent(event.getName()))
    family_obj.event_details.set_text(get_detail_text(event))
    family_obj.descr_field.set_text(event.getDescription())

#-------------------------------------------------------------------------
#
# update_attrib
# 
# Updates the specified event with the specified date.  Compares against
# the previous value, so the that modified flag is not set if nothing has
# actually changed.
#
#-------------------------------------------------------------------------
def update_attrib(attr,type,value,note,priv,conf):
    changed = 0
        
    if attr.getType() != const.save_pattr(type):
        attr.setType(const.save_pattr(type))
        changed = 1
        
    if attr.getValue() != value:
        attr.setValue(value)
        changed = 1

    if attr.getNote() != note:
        attr.setNote(note)
        changed = 1

    if attr.getPrivacy() != priv:
        attr.setPrivacy(priv)
        changed = 1

    if attr.getConfidence() != conf:
        attr.setConfidence(conf)
        changed = 1

    return changed

#-------------------------------------------------------------------------
#
# update_event
# 
# Updates the specified event with the specified date.  Compares against
# the previous value, so the that modified flag is not set if nothing has
# actually changed.
#
#-------------------------------------------------------------------------
def update_event(event,name,date,place,desc,note,priv,conf):
    changed = 0
    if event.getPlace() != place:
        event.setPlace(place)
        changed = 1
        
    if event.getName() != const.save_pevent(name):
        event.setName(const.save_pevent(name))
        changed = 1
        
    if event.getDescription() != desc:
        event.setDescription(desc)
        changed = 1

    if event.getNote() != note:
        event.setNote(note)
        changed = 1

    if event.getDate() != date:
        event.setDate(date)
        changed = 1

    if event.getPrivacy() != priv:
        event.setPrivacy(priv)
        changed = 1

    if event.getConfidence() != conf:
        event.setConfidence(conf)
        changed = 1
        
    return changed
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_showsource_clicked(obj):
    import Sources

    row = obj.get_data(INDEX)
    family_obj = obj.get_data(MARRIAGE)
    if row >= 0:
        Sources.SourceEditor(obj.get_row_data(row),family_obj.db)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_photolist_button_press_event(obj,event):
    if event.button == 3:
        myobj = obj.get_data(MARRIAGE)
        menu = GtkMenu()
        item = GtkTearoffMenuItem()
        item.show()
        view = GtkMenuItem(_("View Image"))
        view.set_data("m",myobj)
        view.connect("activate",on_view_photo)
        view.show()
        edit = GtkMenuItem(_("Edit Image"))
        edit.set_data("m",myobj)
        edit.connect("activate",on_edit_photo)
        edit.show()
        change = GtkMenuItem(_("Edit Description"))
        change.set_data("m",myobj)
        change.connect("activate",on_change_description)
        change.show()
        menu.append(item)
        menu.append(view)
        menu.append(edit)
        menu.append(change)
        menu.popup(None,None,None,0,0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_view_photo(obj):
    myobj = obj.get_data("m")
    photo = myobj.family.getPhotoList()[myobj.selectedIcon]
    type = gnome.mime.type(photo.getPath())
    
    prog = string.split(gnome.mime.get_value(type,'view'))
    args = []
    for val in prog:
        if val == "%f":
            args.append(photo.getPath())
        else:
            args.append(val)
    
    if os.fork() == 0:
        os.execvp(args[0],args)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_photo(obj):
    myobj = obj.get_data("m")
    photo = myobj.family.getPhotoList()[myobj.selectedIcon]
    if os.fork() == 0:
        os.execvp(const.editor,[const.editor, photo.getPath()])

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_photo_select_icon(obj,iconNumber,event):
    obj.get_data(MARRIAGE).selectedIcon = iconNumber

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_photo_clicked(obj):
    marriage_obj = obj.get_data(MARRIAGE)

    photolist = marriage_obj.family.getPhotoList()
    marriage_obj.photo_list.remove(marriage_obj.selectedIcon)
    del photolist[marriage_obj.selectedIcon]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_photo_clicked(obj):

    marriage_obj = obj.get_data(MARRIAGE)
    
    imageSelect = libglade.GladeXML(const.imageselFile,"imageSelect")
    imageSelect.signal_autoconnect({
        "on_savephoto_clicked" : on_savephoto_clicked,
        "destroy_passed_object" : utils.destroy_passed_object
        })
    imageSelect.get_widget("imageSelect").set_data(MARRIAGE,marriage_obj)
    imageSelect.get_widget("imageSelect").show()

    marriage_obj.imageSelect = imageSelect

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_savephoto_clicked(obj):
    marriage_obj = obj.get_data(MARRIAGE)

    photo_name_obj = marriage_obj.imageSelect.get_widget("photosel")
    description_obj = marriage_obj.imageSelect.get_widget("photoDescription")
    filename = photo_name_obj.get_full_path(0)
    description = description_obj.get_text()

    if os.path.exists(filename) == 0:
        return

    prefix = "f%s" % marriage_obj.family.getId()
    name = RelImage.import_photo(filename,marriage_obj.path,prefix)
    if name == None:
        return
        
    photo = Photo()
    photo.setPath(name)
    photo.setDescription(description)
    
    marriage_obj.family.addPhoto(photo)
    marriage_obj.add_thumbnail(photo)

    utils.modified()
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_change_description(obj):
    
    myobj = obj.get_data("m")
    photo = myobj.family.getPhotoList()[myobj.selectedIcon]
    window = libglade.GladeXML(const.imageselFile,"dialog1")
    text = window.get_widget("text")
    text.set_text(photo.getDescription())

    image2 = RelImage.scale_image(photo.getPath(),200.0)

    window.get_widget("photo").load_imlib(image2)
    window.get_widget("dialog1").set_data("p",photo)
    window.get_widget("dialog1").set_data("t",text)
    window.get_widget("dialog1").set_data("m",obj.get_data("m"))
    window.signal_autoconnect({
        "on_cancel_clicked" : utils.destroy_passed_object,
        "on_ok_clicked" : on_ok_clicked,
        "on_apply_clicked" : on_apply_clicked
        })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_apply_clicked(obj):
    photo = obj.get_data("p")
    text = obj.get_data("t").get_text()
    if text != photo.getDescription():
        photo.setDescription(text)
        edit_window = obj.get_data("m")
        edit_window.load_images()
        utils.modified()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    on_apply_clicked(obj)
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
# on_attr_list_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_attr_list_select_row(obj,row,b,c):
    obj.set_data(INDEX,row)

    family_obj = obj.get_data(MARRIAGE)
    attr = obj.get_row_data(row)

    family_obj.attr_type.set_label(const.display_fattr(attr.getType()))
    family_obj.attr_value.set_text(attr.getValue())
    family_obj.attr_details_field.set_text(get_detail_text(attr))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_attr_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return
    AttributeEditor(obj.get_data(MARRIAGE),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_attr_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return

    family_obj = obj.get_data(MARRIAGE)
    del family_obj.alist[row]

    if row > len(family_obj.alist)-1:
        obj.set_data(INDEX,row-1)

    family_obj.redraw_attr_list()
    utils.modified()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_attr_clicked(obj):
    AttributeEditor(obj.get_data(MARRIAGE),None)

#-------------------------------------------------------------------------
#
# EventEditor class
#
#-------------------------------------------------------------------------
class EventEditor:

    def __init__(self,parent,event):
        self.parent = parent
        self.event = event
        self.top = libglade.GladeXML(const.dialogFile, "event_edit")
        self.window = self.top.get_widget("event_edit")
        self.name_field  = self.top.get_widget("eventName")
        self.place_field = self.top.get_widget("eventPlace")
        self.date_field  = self.top.get_widget("eventDate")
        self.descr_field = self.top.get_widget("eventDescription")
        self.note_field = self.top.get_widget("eventNote")
        self.event_menu = self.top.get_widget("personalEvents")
        self.source_field = self.top.get_widget("event_source")
        self.conf_menu = self.top.get_widget("conf")
        self.priv = self.top.get_widget("priv")

        father = parent.family.getFather()
        mother = parent.family.getMother()
        if father and mother:
            name = _("%s and %s") % (father.getPrimaryName().getName(),
                                     mother.getPrimaryName().getName())
        elif father:
            name = father.getPrimaryName().getName()
        else:
            name = mother.getPrimaryName().getName()
            
        self.top.get_widget("eventTitle").set_text(name) 
        self.event_menu.set_popdown_strings(const.marriageEvents)

        myMenu = GtkMenu()
        index = 0
        for name in const.confidence:
            item = GtkMenuItem(name)
            item.set_data("a",index)
            item.show()
            myMenu.append(item)
            index = index + 1

        self.conf_menu.set_menu(myMenu)

        if event != None:
            self.name_field.set_text(event.getName())
            self.place_field.set_text(event.getPlace())
            self.date_field.set_text(event.getDate())
            self.descr_field.set_text(event.getDescription())
            self.conf_menu.set_history(event.getConfidence())

            self.priv.set_active(event.getPrivacy())
            
            srcref_base = self.event.getSourceRef().getBase()
            if srcref_base:
                self.source_field.set_text(srcref_base.getTitle())
            else:
                self.source_field.set_text("")
                 
            self.note_field.set_point(0)
            self.note_field.insert_defaults(event.getNote())
            self.note_field.set_word_wrap(1)
        else:
            self.conf_menu.set_history(2)

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_event_edit_ok_clicked" : on_event_edit_ok_clicked,
            "on_source_clicked" : on_edit_source_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_source_clicked(obj):
    ee = obj.get_data("o")
    Sources.SourceEditor(ee.event,ee.parent.db,ee.source_field)
            
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_event_edit_ok_clicked(obj):
    ee = obj.get_data("o")
    event = ee.event

    ename = ee.name_field.get_text()
    edate = ee.date_field.get_text()
    eplace = ee.place_field.get_text()
    enote = ee.note_field.get_chars(0,-1)
    edesc = ee.descr_field.get_text()
    epriv = ee.priv.get_active()
    econf = ee.conf_menu.get_menu().get_active().get_data("a")

    if event == None:
        event = Event()
        ee.parent.elist.append(event)
        
    if update_event(event,ename,edate,eplace,edesc,enote,epriv,econf):
        ee.parent.events_changed = 1
        
    ee.parent.redraw_events()
    utils.destroy_passed_object(obj)


#-------------------------------------------------------------------------
#
# AttributeEditor class
#
#-------------------------------------------------------------------------
class AttributeEditor:

    def __init__(self,parent,attrib):
        self.parent = parent
        self.attrib = attrib
        self.top = libglade.GladeXML(const.dialogFile, "attr_edit")
        self.window = self.top.get_widget("attr_edit")
        self.type_field  = self.top.get_widget("attr_type")
        self.value_field = self.top.get_widget("attr_value")
        self.note_field = self.top.get_widget("attr_note")
        self.attrib_menu = self.top.get_widget("attr_menu")
        self.source_field = self.top.get_widget("attr_source")
        self.conf_menu = self.top.get_widget("conf")
        self.priv = self.top.get_widget("priv")

        father = parent.family.getFather()
        mother = parent.family.getMother()
        if father and mother:
            name = _("%s and %s") % (father.getPrimaryName().getName(),
                                     mother.getPrimaryName().getName())
        elif father:
            name = father.getPrimaryName().getName()
        else:
            name = mother.getPrimaryName().getName()
        
        self.top.get_widget("attrTitle").set_text(_("Attribute Editor for %s") % name)
        if len(const.familyAttributes) > 0:
            self.attrib_menu.set_popdown_strings(const.familyAttributes)

        myMenu = GtkMenu()
        index = 0
        for name in const.confidence:
            item = GtkMenuItem(name)
            item.set_data("a",index)
            item.show()
            myMenu.append(item)
            index = index + 1
        self.conf_menu.set_menu(myMenu)

        if attrib != None:
            self.type_field.set_text(attrib.getType())
            self.value_field.set_text(attrib.getValue())
            srcref_base = self.attrib.getSourceRef().getBase()
            if srcref_base:
                self.source_field.set_text(srcref_base.getTitle())
            else:
                self.source_field.set_text("")
                 
            self.conf_menu.set_history(attrib.getConfidence())

            self.priv.set_active(attrib.getPrivacy())

            self.note_field.set_point(0)
            self.note_field.insert_defaults(attrib.getNote())
            self.note_field.set_word_wrap(1)
        else:
            self.conf_menu.set_history(2)

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_attr_edit_ok_clicked" : on_attrib_edit_ok_clicked,
            "on_source_clicked" : on_attrib_source_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_attrib_source_clicked(obj):
    ee = obj.get_data("o")
    Sources.SourceEditor(ee.attrib,ee.parent.db,ee.source_field)
            
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_attrib_edit_ok_clicked(obj):
    ee = obj.get_data("o")
    attrib = ee.attrib

    type = ee.type_field.get_text()
    value = ee.value_field.get_text()
    note = ee.note_field.get_chars(0,-1)
    priv = ee.priv.get_active()
    conf = ee.conf_menu.get_menu().get_active().get_data("a")

    if attrib == None:
        attrib = Attribute()
        ee.parent.alist.append(attrib)
        
    if update_attrib(attrib,type,value,note,priv,conf):
        ee.parent.attr_changed = 1
        
    ee.parent.redraw_attr_list()
    utils.destroy_passed_object(obj)

#
#
#
#-------------------------------------------------------------------------
def get_detail_flags(obj):
    detail = ""
    if Config.show_detail:
        if obj.getNote() != "":
            detail = "N"
        if obj.getSourceRef().getBase():
            detail = detail + "S"
        if obj.getPrivacy():
            detail = detail + "P"
    return detail

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_detail_text(obj):
    if obj.getNote() != "":
        details = _("Note")
    else:
        details = ""
    if obj.getSourceRef().getBase() != None:
        if details == "":
            details = _("Source")
        else:
            details = "%s, %s" % (details,_("Source"))
    if obj.getPrivacy() == 1:
        if details == "":
            details = _("Private")
        else:
            details = "%s, %s" % (details,_("Private"))
    return details
