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
            "on_showsource_clicked" : on_showsource_clicked,
            "on_makeprimary_clicked" : on_primary_photo_clicked,
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

        # set initial data
        mevent_list = self.get_widget("marriageEvent")
        mevent_list.set_popdown_strings(const.marriageEvents)
        self.name_field.set_text("")
        self.load_images()

        self.type_field.set_popdown_strings(const.familyRelations)
        self.type_field.entry.set_text(family.getRelationship())
        
        # stored object data
        top_window.set_data(MARRIAGE,self)
        self.event_list.set_data(MARRIAGE,self)
        self.event_list.set_data(INDEX,-1)

        # set notes data
        self.notes_field.set_point(0)
        self.notes_field.insert_defaults(family.getNote())
        self.notes_field.set_word_wrap(1)

        self.redraw_events()
        top_window.show()

    #-------------------------------------------------------------------------
    #
    # add_event - adds the event to the window, attaching the event structure
    # to each row.
    #
    #-------------------------------------------------------------------------
    def add_event(self,text,event):
        if not event:
            return
        self.event_list.append([text,event.getQuoteDate(),event.getPlace()])
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

        self.add_event("Marriage",self.family.getMarriage())
        self.add_event("Divorce",self.family.getDivorce())
        for event in self.family.getEventList():
            self.add_event(event.getName(),event)

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
    if relation != family_obj.family.getRelationship():
        family_obj.family.setRelationship(relation)
        utils.modified()

    text = family_obj.notes_field.get_chars(0,-1)
    if text != family_obj.family.getNote():
        family_obj.family.setNote(text)
        utils.modified()

    utils.destroy_passed_object(family_obj.get_widget("marriageEditor"))

#-------------------------------------------------------------------------
#
# on_add_clicked - creates a new event from the data displayed in the
# window. Special care has to be take for the marriage and divorce
# events, since they are not stored in the event list. 
#
#-------------------------------------------------------------------------
def on_add_clicked(obj):

    family_obj = obj.get_data(MARRIAGE)
    
    date = family_obj.date_field.get_text()
    place= family_obj.place_field.get_text()
    name = family_obj.name_field.get_text()
    desc = family_obj.descr_field.get_text()

    if name == "Marriage":
        if family_obj.family.getMarriage() == None:
            event = Event()
            family_obj.family.setMarriage(event)
        else:
            event = family_obj.family.getMarriage()
    elif name == "Divorce":
        if family_obj.family.getDivorce() == None:
            event = Event()
            family_obj.family.setDivorce(event)
        else:
            event = family_obj.family.getDivorce()
    else:
        event = Event()
        family_obj.family.addEvent(event)

    event.set(name,date,place,desc)
    
    family_obj.redraw_events()
    utils.modified()

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

    date = family_obj.date_field.get_text()
    place= family_obj.place_field.get_text()
    name = family_obj.name_field.get_text()
    desc = family_obj.descr_field.get_text()

    update_event(event,name,date,place,desc)
    family_obj.redraw_events()

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
    
    active_event = obj.get_row_data(row)

    if active_event == family_obj.family.getMarriage():
        family_obj.family.setMarriage(None)
    elif active_event == family_obj.family.getDivorce():
        family_obj.family.setDivorce(None)
    else:
        count = 0
        list = family_obj.family.getEventList()
        for event in list:
            if event == active_event:
                del list[count]
                break
            count = count + 1

    if family_obj.lines == 1:
        obj.set_data(INDEX,None)
    elif row > family_obj.lines-1:
        obj.set_data(INDEX,row-1)
        
    family_obj.redraw_events()
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
    family_obj.name_field.set_text(event.getName())
    family_obj.descr_field.set_text(event.getDescription())

#-------------------------------------------------------------------------
#
# update_event
# 
# Updates the specified event with the specified date.  Compares against
# the previous value, so the that modified flag is not set if nothing has
# actually changed.
#
#-------------------------------------------------------------------------
def update_event(event,name,date,place,desc):
    if event.getPlace() != place:
        event.setPlace(place)
        utils.modified()
        
    if event.getName() != name:
        event.setName(name)
        utils.modified()
        
    if event.getDescription() != desc:
        event.setDescription(desc)
        utils.modified()

    if event.getDate() != date:
        event.setDate(date)
        utils.modified()
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
def on_primary_photo_clicked(obj):
    marriage_obj = obj.get_data(MARRIAGE)
    if marriage_obj.selectedIcon == None or \
       marriage_obj.selectedIcon == 0:
        return

    photolist = marriage.family.getPhotoList()
    savePhoto = photolist[selectedIcon]
    for i in range(0,selectedIcon):
        photolist[selectedIcon-i] = photolist[selectedIcon-i-1]
    photolist[0] = savePhoto
    marriage_obj.load_images()
    utils.modified()

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
        view = GtkMenuItem(_("View Photo"))
        view.set_data("m",myobj)
        view.connect("activate",on_view_photo)
        view.show()
        edit = GtkMenuItem(_("Edit Photo"))
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
    photo = myobj.person.getPhotoList()[myobj.selectedIcon]
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
    photo = myobj.person.getPhotoList()[myobj.selectedIcon]
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

    prefix = "f" + str(marriage_obj.family.getId())
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
    photo = myobj.person.getPhotoList()[myobj.selectedIcon]
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
