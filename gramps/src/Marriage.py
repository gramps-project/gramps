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
            "destroy_passed_object" : on_cancel_edit,
            "on_add_attr_clicked" : on_add_attr_clicked,
            "on_addphoto_clicked" : on_add_photo_clicked,
            "on_attr_list_select_row" : on_attr_list_select_row,
            "on_close_marriage_editor" : on_close_marriage_editor,
            "on_delete_attr_clicked" : on_delete_attr_clicked,
            "on_delete_event" : on_delete_event,
            "on_deletephoto_clicked" : on_delete_photo_clicked,
            "on_marriageAddBtn_clicked" : on_add_clicked,
            "on_marriageDeleteBtn_clicked" : on_delete_clicked,
            "on_marriageEventList_select_row" : on_select_row,
            "on_marriageUpdateBtn_clicked" : on_update_clicked,
            "on_photolist_button_press_event" : on_photolist_button_press_event,
            "on_photolist_select_icon" : on_photo_select_icon,
            "on_update_attr_clicked" : on_update_attr_clicked,
            })

        top_window = self.get_widget("marriageEditor")
        text_win = self.get_widget("marriageTitle")
        title = _("%s and %s") % (Config.nameof(family.getFather()),
                                  Config.nameof(family.getMother()))
        text_win.set_text(title)
        
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
        self.lists_changed = 0

        # set initial data
        self.load_images()

        self.type_field.set_popdown_strings(const.familyRelations)
        frel = const.display_frel(family.getRelationship())
        self.type_field.entry.set_text(frel)
        
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

        # Typing CR selects OK button
        top_window.editable_enters(self.notes_field);
        top_window.editable_enters(self.get_widget("combo-entry1"));
        
        self.redraw_events()
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
    # add_thumbnail - Scale the image and add it to the IconList.  Currently, 
    # there seems to be a problem with either GdkImlib. A reference has to be
    # kept to the image, or it gets lost.  This is supposed to be a known
    # imlib problem
    #
    #-------------------------------------------------------------------------
    def add_thumbnail(self,photo):
        src = os.path.basename(photo.getPath())
        if photo.getPrivate():
            thumb = "%s%s.thumb%s%s" % (self.path,os.sep,os.sep,src)
        else:
            thumb = "%s%s.thumb%s%s.jpg" % (self.path,os.sep,os.sep,os.path.basename(src))
        RelImage.check_thumb(photo.getPath(),thumb,const.thumbScale)
        self.photo_list.append(thumb,photo.getDescription())

    #-------------------------------------------------------------------------
    #
    # load_images - clears the currentImages list to free up any cached 
    # Imlibs.  Then add each photo in the person's list of photos to the 
    # photolist window.
    #
    #-------------------------------------------------------------------------
    def load_images(self):
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
    EventEditor(obj.get_data(MARRIAGE),None)

#-------------------------------------------------------------------------
#
# on_update_clicked - updates the selected event with the values in the
# current display
#
#-------------------------------------------------------------------------
def on_update_clicked(obj):
    row = obj.get_data(INDEX)
    if row >= 0:
        EventEditor(obj.get_data(MARRIAGE),obj.get_row_data(row))

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
        family_obj.redraw_events()

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
    family_obj.place_field.set_text(event.getPlaceName())
    family_obj.name_field.set_label(const.display_fevent(event.getName()))
    family_obj.event_details.set_text(utils.get_detail_text(event))
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
def on_photolist_button_press_event(obj,event):
    myobj = obj.get_data(MARRIAGE)
    icon = myobj.selectedIcon
    if icon == -1:
        return

    if event.button == 3:
        photo = myobj.family.getPhotoList()[icon]
        menu = GtkMenu()
        item = GtkTearoffMenuItem()
        item.show()
        menu.append(item)
        utils.add_menuitem(menu,_("View Image"),myobj,on_view_photo)
        utils.add_menuitem(menu,_("Edit Image"),myobj,on_edit_photo)
        utils.add_menuitem(menu,_("Edit Description"),myobj,
                           on_change_description)
        if photo.getPrivate() == 0:
            utils.add_menuitem(menu,_("Convert to private copy"),myobj,
                               on_convert_to_private)
        menu.popup(None,None,None,0,0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_convert_to_private(obj):
    epo = obj.get_data(OBJECT)
    photo = epo.family.getPhotoList()[epo.selected_icon]

    prefix = "f%s" % epo.person.getId()
    name = RelImage.import_photo(photo.getPath(),epo.path,prefix)

    photo.setPath(name)
    photo.setPrivate(1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_view_photo(obj):
    myobj = obj.get_data("m")
    photo = myobj.family.getPhotoList()[myobj.selectedIcon]
    utils.view_photo(photo)

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
    icon = marriage_obj.selectedIcon

    if icon != -1:
        marriage_obj.photo_list.remove(icon)
        del marriage_obj.family.getPhotoList()[icon]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_photo_clicked(obj):

    marriage_obj = obj.get_data(MARRIAGE)
    imageSelect = libglade.GladeXML(const.imageselFile,"imageSelect")
    marriage_obj.imageSelect = imageSelect
    
    imageSelect.signal_autoconnect({
        "on_savephoto_clicked" : on_savephoto_clicked,
        "on_name_changed" : on_name_changed,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    marriage_obj.fname = image_select.get_widget("fname")
    marriage_obj.add_image = image_select.get_widget("image")
    marriage_obj.external = image_select.get_widget("private")
    window = imageSelect.get_widget("imageSelect")
    window.editable_enters(image_select.get_widget("photoDescription"))
    window.set_data(MARRIAGE,marriage_obj)
    window.show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_name_changed(obj):
    edit_person = obj.get_data(MARRIAGE_OBJ)
    file = edit_person.fname.get_text()
    if os.path.isfile(file):
        image = RelImage.scale_image(file,const.thumbScale)
        edit_person.add_image.load_imlib(image)

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

    if marriage_obj.external.get_active() == 1:
        if os.path.isfile(filename):
            name = filename
            thumb = "%s%s.thumb.jpg" % (path,os.sep,os.path.basename(filename))
            RelImage.mk_thumb(filename,thumb,const.thumbScale)
        else:
            return
    else:
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
    window.get_widget("dialog1").editable_enters(text)
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
    family_obj.attr_details_field.set_text(utils.get_detail_text(attr))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_attr_clicked(obj):
    row = obj.get_data(INDEX)
    if row >= 0:
        AttributeEditor(obj.get_data(MARRIAGE),obj.get_row_data(row))

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
        if self.event:
            self.srcref = SourceRef(self.event.getSourceRef())
        else:
            self.srcref = SourceRef()
        self.top = libglade.GladeXML(const.dialogFile, "event_edit")
        self.window = self.top.get_widget("event_edit")
        self.name_field  = self.top.get_widget("eventName")
        self.place_field = self.top.get_widget("eventPlace")
        self.place_combo = self.top.get_widget("eventPlace_combo")
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

        # Typing CR selects OK button
        self.window.editable_enters(self.name_field);
        self.window.editable_enters(self.place_field);
        self.window.editable_enters(self.date_field);
        self.window.editable_enters(self.descr_field);

        utils.build_confidence_menu(self.conf_menu)

        values = self.parent.db.getPlaceMap().values()
        if event != None:
            self.name_field.set_text(event.getName())

            utils.attach_places(values,self.place_combo,event.getPlace())
            self.place_field.set_text(event.getPlaceName())
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
            utils.attach_places(values,self.place_combo,None)
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
    Sources.SourceEditor(ee.srcref,ee.parent.db,ee.source_field)
            
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
    eplace = string.strip(ee.place_field.get_text())
    eplace_obj = utils.get_place_from_list(ee.place_combo)
    enote = ee.note_field.get_chars(0,-1)
    edesc = ee.descr_field.get_text()
    epriv = ee.priv.get_active()
    econf = ee.conf_menu.get_menu().get_active().get_data("a")

    if event == None:
        event = Event()
        ee.parent.elist.append(event)
        
    if eplace_obj == None and eplace != "":
        eplace_obj = Place()
        eplace_obj.set_title(eplace)
        ee.parent.db.addPlace(eplace_obj)

    if update_event(event,ename,edate,eplace_obj,edesc,enote,epriv,econf):
        ee.parent.lists_changed = 1
        
    if not source_refs_equal(event.getSourceRef(),ee.srcref):
        event.setSourceRef(ee.srcref)
        ee.parent.lists_changed = 1

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
        if self.attrib:
            self.srcref = SourceRef(self.attrib.getSourceRef())
        else:
            self.srcref = SourceRef()
        
        # Typing CR selects OK button
        self.window.editable_enters(self.type_field);
        self.window.editable_enters(self.value_field);

        father = parent.family.getFather()
        mother = parent.family.getMother()
        if father and mother:
            name = _("%s and %s") % (father.getPrimaryName().getName(),
                                     mother.getPrimaryName().getName())
        elif father:
            name = father.getPrimaryName().getName()
        else:
            name = mother.getPrimaryName().getName()

        title = _("Attribute Editor for %s") % name
        self.top.get_widget("attrTitle").set_text(title)
        if len(const.familyAttributes) > 0:
            self.attrib_menu.set_popdown_strings(const.familyAttributes)

        utils.build_confidence_menu(self.conf_menu)

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
    Sources.SourceEditor(ee.srcref,ee.parent.db,ee.source_field)
            
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
        ee.parent.lists_changed = 1
        
    if not source_refs_equal(attrib.getSourceRef(),ee.srcref):
        attrib.setSourceRef(ee.srcref)
        ee.parent.lists_changed = 1

    ee.parent.redraw_attr_list()
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def source_refs_equal(one,two):
    if not one or not two:
        return 0
    if one.ref != two.ref:
        return 0
    if one.page != two.page:
        return 0
    if one.date != two.date:
        return 0
    if one.comments != two.comments:
        return 0
    if one.text != two.text:
        return 0
    return 1

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_attr(attr):
    detail = utils.get_detail_flags(attr)
    return [const.display_pattr(attr.getType()),attr.getValue(),detail]

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_event(event):
    return [const.display_fevent(event.getName()), event.getQuoteDate(),
            event.getPlaceName(), utils.get_detail_flags(event)]
