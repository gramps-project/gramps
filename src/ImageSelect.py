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
import os
import string

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *
import GDK
import libglade
import GdkImlib

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import intl
import const
import utils
import Config
from RelLib import *
import RelImage
import Sources

_ = intl.gettext

#-------------------------------------------------------------------------
#
# ImageSelect class
#
#-------------------------------------------------------------------------
class ImageSelect:

    #---------------------------------------------------------------------
    #
    # __init__ - Creates an edit window.  Associates a person with the 
    # window.
    #
    #---------------------------------------------------------------------
    def __init__(self, path, prefix, db):
        self.path        = path;
        self.db          = db
        self.prefix      = prefix;

    #-------------------------------------------------------------------------
    #
    # create_add_dialog - Create the gnome dialog for selecting a new
    # photo and entering its description.
    #
    #-------------------------------------------------------------------------
    def create_add_dialog(self):
        self.glade       = libglade.GladeXML(const.imageselFile,"imageSelect")
        window           = self.glade.get_widget("imageSelect")
        self.fname       = self.glade.get_widget("fname")
        self.image       = self.glade.get_widget("image")
        self.description = self.glade.get_widget("photoDescription")
        self.external    = self.glade.get_widget("private")

        self.glade.signal_autoconnect({
            "on_savephoto_clicked" : self.on_savephoto_clicked,
            "on_name_changed" : self.on_name_changed,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        window.editable_enters(self.description)
        window.show()

    #-------------------------------------------------------------------------
    #
    # on_name_changed - The filename has changed.  Verify it and load
    # the picture.
    #
    #-------------------------------------------------------------------------
    def on_name_changed(self, obj):
        filename = self.fname.get_text()
        if os.path.isfile(filename):
            type = utils.get_mime_type(filename)
            if type[0:5] == "image":
                image = RelImage.scale_image(filename,const.thumbScale)
                self.image.load_imlib(image)
            else:
                self.image.load_file(utils.find_icon(type))

    #-------------------------------------------------------------------------
    #
    # savephoto - Save the photo in the dataobj object.  (Required function)
    #
    #-------------------------------------------------------------------------
    def on_savephoto_clicked(self, obj):
        filename = self.glade.get_widget("photosel").get_full_path(0)
        description = self.glade.get_widget("photoDescription").get_text()

        if os.path.exists(filename) == 0:
            GnomeErrorDialog(_("That is not a valid file name."));
            return

        type = utils.get_mime_type(filename)
        mobj = Photo()
        if description == "":
            description = os.path.basename(name)
        mobj.setDescription(description)
        mobj.setMimeType(type)
        self.savephoto(mobj)

        if type[0:5] == "image":
            if self.external.get_active() == 1:
                if os.path.isfile(filename):
                    name = filename
                    thumb = "%s/.thumb/%s.jpg" % (self.path,mobj.getId())
                    RelImage.mk_thumb(filename,thumb,const.thumbScale)
                else:
                    return
            else:
                name = RelImage.import_media_object(filename,self.path,mobj.getId())
        else:
            if self.external.get_active() == 1:
                name = filename
            else:
                name = RelImage.import_media_object(filename,self.path,mobj.getId())

        mobj.setPath(name)

        utils.modified()
        utils.destroy_passed_object(obj)

    #-------------------------------------------------------------------------
    #
    # savephoto - Save the photo in the dataobj object.  (Placeholder)
    #
    #-------------------------------------------------------------------------
    def savephoto(self, photo):
    	assert 0, "The savephoto function must be subclassed"

#-------------------------------------------------------------------------
#
# Gallery class - This class handles all the logic underlying a
# picture gallery.  This class does not load or contain the widget
# data structure to actually display the gallery.
#
#-------------------------------------------------------------------------
class Gallery(ImageSelect):
    def __init__(self, dataobj, path, prefix, icon_list, db):
        ImageSelect.__init__(self, path, prefix, db)

        t = [
            ('STRING', 0, 0),
            ('text/plain',0,0),
            ('text/uri-list',0,2),
            ('application/x-rootwin-drop',0,1)]

        icon_list.drag_dest_set(DEST_DEFAULT_ALL, t, GDK.ACTION_COPY | GDK.ACTION_MOVE)
        icon_list.connect("drag_data_received", self.on_photolist_drag_data_received)

        icon_list.drag_source_set(GDK.BUTTON1_MASK|GDK.BUTTON3_MASK,t,\
                                   GDK.ACTION_COPY | GDK.ACTION_MOVE)
        icon_list.connect("drag_data_get", self.on_photolist_drag_data_get)
        

        # Be paranoid - development only error messages
        assert dataobj.addPhoto, "Gallery data object must contain an addPhoto routine."
        assert dataobj.getPhotoList, "Gallery data object must contain an getPhotoList routine."

        # Remember arguments
        self.path      = path;
        self.prefix    = prefix;
        self.dataobj   = dataobj;
        self.icon_list = icon_list;

        # Local object variables
        self.selectedIcon = -1
        self.currentImages = []

    #-------------------------------------------------------------------------
    #
    # savephoto - Save the photo in the dataobj object.  (Required function)
    #
    #-------------------------------------------------------------------------
    def savephoto(self, photo):

        self.db.addObject(photo)
        oref = ObjectRef()
        oref.setReference(photo)
        self.dataobj.addPhoto(oref)
        self.add_thumbnail(oref)

    #-------------------------------------------------------------------------
    #
    # add_thumbnail - Scale the image and add it to the IconList. 
    #
    #-------------------------------------------------------------------------
    def add_thumbnail(self, photo):
        object = photo.getReference()
        path = object.getPath()
        src = os.path.basename(path)
        if object.getMimeType()[0:5] == "image":
            thumb = "%s/.thumb/%s.jpg" % (self.path,object.getId())
            RelImage.check_thumb(path,thumb,const.thumbScale)
        else:
            thumb = utils.find_icon(object.getMimeType())
        self.icon_list.append(thumb,object.getDescription())
        
    #-------------------------------------------------------------------------
    #
    # load_images - clears the currentImages list to free up any cached 
    # Imlibs.  Then add each photo in the place's list of photos to the 
    # photolist window.
    #
    #-------------------------------------------------------------------------
    def load_images(self):
        self.icon_list.freeze()
        self.icon_list.clear()
        for photo in self.dataobj.getPhotoList():
            self.add_thumbnail(photo)
        self.icon_list.thaw()

    #-------------------------------------------------------------------------
    #
    # on_photo_select_icon - User clicked on a photo.  Remember which one.
    #
    #-------------------------------------------------------------------------
    def on_photo_select_icon(self, obj,iconNumber,event):
        self.selectedIcon = iconNumber

    def on_photolist_drag_data_received(self,w, context, x, y, data, info, time):
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
                self.savephoto(photo)
            else:
                if self.db.getObjectMap().has_key(data.data):
                    for p in self.dataobj.getPhotoList():
                        if data.data == p.getReference().getId():
                            w.drag_finish(context, TRUE, FALSE, time)
                            return
                    oref = ObjectRef()
                    oref.setReference(self.db.findObjectNoMap(data.data))
                    self.dataobj.addPhoto(oref)
                    self.add_thumbnail(oref)
                    utils.modified()
            w.drag_finish(context, TRUE, FALSE, time)
	else:
            w.drag_finish(context, FALSE, FALSE, time)
                
    def on_photolist_drag_data_get(self,w, context, selection_data, info, time):
        if info == 1:
            return
        if self.selectedIcon != -1:
            ref = self.dataobj.getPhotoList()[self.selectedIcon]
            id = ref.getReference().getId()
            selection_data.set(selection_data.target, 8, id)	

    #-------------------------------------------------------------------------
    #
    # on_add_photo_clicked - User wants to add a new photo.  Create a
    # dialog to find out which photo they want.
    #
    #-------------------------------------------------------------------------
    def on_add_photo_clicked(self, obj):
        self.create_add_dialog()

    #-------------------------------------------------------------------------
    #
    # on_delete_photo_clicked - User wants to delete a new photo.
    # Remove it from the displayed thumbnails, and remove it from the
    # dataobj photo list.
    #
    #-------------------------------------------------------------------------
    def on_delete_photo_clicked(self, obj):
        icon = self.selectedIcon
        if icon != -1:
            self.icon_list.remove(icon)
            del self.dataobj.getPhotoList()[icon]
            if len(self.dataobj.getPhotoList()) == 0:
                self.selectedIcon = -1
            else:
                self.selectedIcon = 0
                self.icon_list.select_icon(0)

    #-------------------------------------------------------------------------
    #
    # on_photolist_button_press_event - Look for right-clicks on a
    # picture and create a popup menu of the available actions.
    #
    #-------------------------------------------------------------------------
    def on_photolist_button_press_event(self, obj, event):
        icon = self.selectedIcon
        if icon == -1:
            return
    
        if event.button == 3:
            photo = self.dataobj.getPhotoList()[icon]
            menu = GtkMenu()
            item = GtkTearoffMenuItem()
            item.show()
            menu.append(item)
            utils.add_menuitem(menu,_("View in the default viewer"),None,self.popup_view_photo)
            utils.add_menuitem(menu,_("Edit in the default editor"),None,self.popup_edit_photo)
            utils.add_menuitem(menu,_("Edit Object Properties"),None,
                               self.popup_change_description)
            object = photo.getReference()
            if object.getLocal() == 0:
                utils.add_menuitem(menu,_("Convert to local copy"),None,
                                   self.popup_convert_to_private)
            menu.popup(None,None,None,0,0)

    #-------------------------------------------------------------------------
    #
    # popup_view_photo - Open this picture in a picture viewer
    #
    #-------------------------------------------------------------------------
    def popup_view_photo(self, obj):
        photo = self.dataobj.getPhotoList()[self.selectedIcon]
        utils.view_photo(photo.getReference())
    
    #-------------------------------------------------------------------------
    #
    # popup_edit_photo - Open this picture in a picture editor
    #
    #-------------------------------------------------------------------------
    def popup_edit_photo(self, obj):
        photo = self.dataobj.getPhotoList()[self.selectedIcon]
        if os.fork() == 0:
            os.execvp(const.editor,[const.editor, photo.getReference().getPath()])
    
    #-------------------------------------------------------------------------
    #
    # popup_convert_to_private - Copy this picture into gramps private
    # database instead of leaving it as an external data object.
    #
    #-------------------------------------------------------------------------
    def popup_convert_to_private(self, obj):
        photo = self.dataobj.getPhotoList()[self.selectedIcon]
        object = photo.getReference()
        name = RelImage.import_photo(object.getPath(),self.path,self.prefix)
    
        object.setPath(name)
        object.setLocal(1)

    #-------------------------------------------------------------------------
    #
    # popup_change_description - Bring up a window allowing the user
    # to edit the description of a picture.
    #
    #-------------------------------------------------------------------------
    def popup_change_description(self, obj):
        photo = self.dataobj.getPhotoList()[self.selectedIcon]
        object = photo.getReference()
        path = object.getPath()
        src = os.path.basename(path)
    
        self.change_dialog = libglade.GladeXML(const.imageselFile,"change_description")
        window = self.change_dialog.get_widget("change_description")
        self.change_dialog.get_widget("description").set_text(object.getDescription())
        pixmap = self.change_dialog.get_widget("pixmap")
        mtype = object.getMimeType()
        if mtype[0:5] == "image":
            thumb = "%s/.thumb/%s" % (self.path,object.getId())
            RelImage.check_thumb(path,thumb,const.thumbScale)
            pixmap.load_file(thumb)
        else:
            pixmap.load_file(utils.find_icon(mtype))

        self.change_dialog.get_widget("gid").set_text(object.getId())
        self.change_dialog.get_widget("description").set_text(object.getDescription())
        if object.getLocal():
            self.change_dialog.get_widget("path").set_text("<local>")
        else:
            self.change_dialog.get_widget("path").set_text(path)
        self.change_dialog.get_widget("type").set_text(utils.get_mime_description(mtype))
        self.change_dialog.get_widget("notes").insert_defaults(photo.getNote())
        window.set_data("p",photo)
        window.set_data("t",self.change_dialog)
        self.change_dialog.signal_autoconnect({
            "on_cancel_clicked" : utils.destroy_passed_object,
            "on_ok_clicked" : self.new_desc_ok_clicked,
            "on_apply_clicked" : self.new_desc_apply_clicked
            })

    #-------------------------------------------------------------------------
    #
    # new_desc_apply_clicked - Apply the new description.
    #
    #-------------------------------------------------------------------------
    def new_desc_apply_clicked(self, obj):
        photo = obj.get_data("p")
        top = obj.get_data('t')
        text = top.get_widget("notes").get_chars(0,-1)
        note = photo.getNote()
        if text != note:
            photo.setNote(text)
            utils.modified()

    #-------------------------------------------------------------------------
    #
    # new_desc_ok_clicked - Apply the new description and close the dialog.
    #
    #-------------------------------------------------------------------------
    def new_desc_ok_clicked(self, obj):
        self.new_desc_apply_clicked(obj)
        utils.destroy_passed_object(obj)
    



