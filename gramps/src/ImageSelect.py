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
import GDK
import GTK
import gtk
import gnome.ui
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import utils
import Config
from RelLib import *
import RelImage

import EditPerson
import Marriage
import EditPlace
import EditSource

from intl import gettext
_ = gettext

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
        self.temp_name   = ""

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

        basename = os.path.basename(filename)
        (root,ext) = os.path.splitext(basename)
        old_title  = self.description.get_text()

        if old_title == "" or old_title == self.temp_name:
            self.description.set_text(root)
        self.temp_name = root
        
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
        description = self.description.get_text()

        if os.path.exists(filename) == 0:
            gnome.ui.GnomeErrorDialog(_("That is not a valid file name."));
            return

        already_imported = None
        for o in self.db.getObjectMap().values():
            if o.getPath() == filename:
                already_imported = o
                break

        if (already_imported):
            oref = ObjectRef()
            oref.setReference(already_imported)
            self.dataobj.addPhoto(oref)
            self.add_thumbnail(oref)
        else:
            type = utils.get_mime_type(filename)
            mobj = Photo()
            if description == "":
                description = os.path.basename(filename)
                mobj.setDescription(description)
            mobj.setMimeType(type)
            self.savephoto(mobj)

            if type[0:5] == "image":
                if self.external.get_active() == 0:
                    name = RelImage.import_media_object(filename,self.path,mobj.getId())
            else:
                if self.external.get_active() == 1:
                    name = filename
                    RelImage.mk_thumb(filename,self.path,mobj.getId())
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

        icon_list.drag_dest_set(GTK.DEST_DEFAULT_ALL, t, GDK.ACTION_COPY | GDK.ACTION_MOVE)
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
        thumb = utils.thumb_path(self.db.getSavePath(),object)
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
        import urlparse
	if data and data.format == 8:
            icon_index = w.get_icon_at(x,y)
            d = string.strip(string.replace(data.data,'\0',' '))
            protocol,site,file, j,k,l = urlparse.urlparse(d)
            if protocol == "file":
                name = file
                mime = utils.get_mime_type(name)
                photo = Photo()
                photo.setPath(name)
                photo.setMimeType(mime)
                basename = os.path.basename(name)
                (root,ext) = os.path.splitext(basename)
                photo.setDescription(root)
                self.savephoto(photo)
                if Config.mediaref == 0:
                    name = RelImage.import_media_object(name,
                                                        self.path,
                                                        photo.getId())
                    photo.setPath(name)
                    photo.setLocal(1)
                utils.modified()
                if Config.globalprop:
                    GlobalMediaProperties(self.db,photo,None)
            elif protocol != "":
                import urllib
                u = urllib.URLopener()
                try:
                    tfile,headers = u.retrieve(d)
                except IOError, msg:
                    t = _("Could not import %s") % d
                    
                    gnome.ui.GnomeErrorDialog("%s\n%s %d" % (t,msg[0],msg[1]))
                    return
                mime = utils.get_mime_type(tfile)
                photo = Photo()
                photo.setMimeType(mime)
                photo.setDescription(d)
                photo.setLocal(1)
                photo.setPath(tfile)
                self.db.addObject(photo)
                oref = ObjectRef()
                oref.setReference(photo)
                self.dataobj.addPhoto(oref)
                try:
                    id = photo.getId()
                    name = RelImage.import_media_object(tfile,self.path,id)
                    if name != None and name != "":
                        photo.setPath(name)
                except:
                    photo.setPath(tfile)
                    w.drag_finish(context, 1, 0, time)
                    return
                self.add_thumbnail(oref)
                utils.modified()
                if Config.globalprop:
                    GlobalMediaProperties(self.db,photo,None)
            else:
                if self.db.getObjectMap().has_key(data.data):
                    index = 0
                    for p in self.dataobj.getPhotoList():
                        if data.data == p.getReference().getId():
                            if index == icon_index or icon_index == -1:
                                w.drag_finish(context, 0, 0, time)
                                return
                            else:
                                w.drag_finish(context, 1, 0, time)
                                nl = self.dataobj.getPhotoList()
                                item = nl[index]
                                if icon_index == 0:
                                    del nl[index]
                                    nl = [item] + nl
                                else:
                                    del nl[index]
                                    nl = nl[0:icon_index] + [item] + nl[icon_index:]
                                self.dataobj.setPhotoList(nl)
                                utils.modified()
                                self.load_images()
                                return
                        index = index + 1
                    oref = ObjectRef()
                    oref.setReference(self.db.findObjectNoMap(data.data))
                    self.dataobj.addPhoto(oref)
                    self.add_thumbnail(oref)
                    if Config.globalprop:
                        LocalMediaProperties(oref,self.path)
                    utils.modified()
            w.drag_finish(context, 1, 0, time)
	else:
            w.drag_finish(context, 0, 0, time)
                
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
            menu = gtk.GtkMenu()
            item = gtk.GtkTearoffMenuItem()
            item.show()
            menu.append(item)
            utils.add_menuitem(menu,_("View in the default viewer"),None,self.popup_view_photo)
            object = photo.getReference()
            if object.getMimeType()[0:5] == "image":
                utils.add_menuitem(menu,_("Edit with the GIMP"),\
                                   None,self.popup_edit_photo)
            utils.add_menuitem(menu,_("Edit Object Properties"),None,
                               self.popup_change_description)
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
        name = RelImage.import_media_object(object.getPath(),self.path,object.getId())
    
        object.setPath(name)
        object.setLocal(1)

    #-------------------------------------------------------------------------
    #
    # popup_change_description - Bring up a window allowing the user
    # to edit the description of a picture.
    #
    #-------------------------------------------------------------------------
    def popup_change_description(self, obj):
        if self.selectedIcon >=0:
            photo = self.dataobj.getPhotoList()[self.selectedIcon]
            LocalMediaProperties(photo,self.path)

#-------------------------------------------------------------------------
#
# LocalMediaProperties
#
#-------------------------------------------------------------------------
class LocalMediaProperties:

    def __init__(self,photo,path):
        self.photo = photo
        self.object = photo.getReference()
        self.alist = photo.getAttributeList()[:]
        self.lists_changed = 0
        
        fname = self.object.getPath()
        self.change_dialog = libglade.GladeXML(const.imageselFile,"change_description")
        descr_window = self.change_dialog.get_widget("description")
        pixmap = self.change_dialog.get_widget("pixmap")
        self.attr_type = self.change_dialog.get_widget("attr_type")
        self.attr_value = self.change_dialog.get_widget("attr_value")
        self.attr_details = self.change_dialog.get_widget("attr_details")
        self.attr_list = self.change_dialog.get_widget("attr_list")
        
        descr_window.set_text(self.object.getDescription())
        mtype = self.object.getMimeType()
        pixmap.load_file(utils.thumb_path(path,self.object))

        self.change_dialog.get_widget("private").set_active(photo.getPrivacy())
        self.change_dialog.get_widget("gid").set_text(self.object.getId())

        if self.object.getLocal():
            self.change_dialog.get_widget("path").set_text("<local>")
        else:
            self.change_dialog.get_widget("path").set_text(fname)
        self.change_dialog.get_widget("type").set_text(utils.get_mime_description(mtype))
        self.change_dialog.get_widget("notes").insert_defaults(photo.getNote())
        self.change_dialog.signal_autoconnect({
            "on_cancel_clicked" : utils.destroy_passed_object,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_apply_clicked" : self.on_apply_clicked,
            "on_attr_list_select_row" : self.on_attr_list_select_row,
            "on_add_attr_clicked": self.on_add_attr_clicked,
            "on_delete_attr_clicked" : self.on_delete_attr_clicked,
            "on_update_attr_clicked" : self.on_update_attr_clicked,
            })
        self.redraw_attr_list()

    def redraw_attr_list(self):
        utils.redraw_list(self.alist,self.attr_list,disp_attr)
        
    def on_apply_clicked(self, obj):
        priv = self.change_dialog.get_widget("private").get_active()
        text = self.change_dialog.get_widget("notes").get_chars(0,-1)
        note = self.photo.getNote()
        if text != note or priv != self.photo.getPrivacy():
            self.photo.setNote(text)
            self.photo.setPrivacy(priv)
            utils.modified()
        if self.lists_changed:
            self.photo.setAttributeList(self.alist)
            utils.modified()

    def on_ok_clicked(self, obj):
        self.on_apply_clicked(obj)
        utils.destroy_passed_object(obj)
        
    def on_attr_list_select_row(self,obj,row,b,c):
        attr = obj.get_row_data(row)

        self.attr_type.set_label(attr.getType())
        self.attr_value.set_text(attr.getValue())
        self.attr_details.set_text(utils.get_detail_text(attr))

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        if len(obj.selection) > 0:
            row = obj.selection[0]
            attr = obj.get_row_data(row)
            AttrEdit.AttributeEditor(self,attr,"Media Object",[])

    def on_delete_attr_clicked(self,obj):
        if utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        AttrEdit.AttributeEditor(self,None,"Media Object",[])

#-------------------------------------------------------------------------
#
# GlobalMediaProperties
#
#-------------------------------------------------------------------------
class GlobalMediaProperties:

    def __init__(self,db,object,update):
        self.object = object
        self.alist = self.object.getAttributeList()[:]
        self.lists_changed = 0
        self.db = db
        self.update = update

        self.path = self.db.getSavePath()
        self.change_dialog = libglade.GladeXML(const.imageselFile,"change_global")
        self.descr_window = self.change_dialog.get_widget("description")
        self.notes = self.change_dialog.get_widget("notes")
        pixmap = self.change_dialog.get_widget("pixmap")
        self.attr_type = self.change_dialog.get_widget("attr_type")
        self.attr_value = self.change_dialog.get_widget("attr_value")
        self.attr_details = self.change_dialog.get_widget("attr_details")
        self.attr_list = self.change_dialog.get_widget("attr_list")
        
        self.descr_window.set_text(self.object.getDescription())
        mtype = self.object.getMimeType()
        pixmap.load_file(utils.thumb_path(self.path,self.object))

        self.change_dialog.get_widget("gid").set_text(self.object.getId())
        self.makelocal = self.change_dialog.get_widget("makelocal")

        self.update_info()
        
        self.change_dialog.get_widget("type").set_text(utils.get_mime_description(mtype))
        self.notes.insert_defaults(object.getNote())
        self.change_dialog.signal_autoconnect({
            "on_cancel_clicked"      : utils.destroy_passed_object,
            "on_ok_clicked"          : self.on_ok_clicked,
            "on_apply_clicked"       : self.on_apply_clicked,
            "on_attr_list_select_row": self.on_attr_list_select_row,
            "on_add_attr_clicked"    : self.on_add_attr_clicked,
            "on_notebook_switch_page": self.on_notebook_switch_page,
            "on_make_local_clicked"  : self.on_make_local_clicked,
            "on_delete_attr_clicked" : self.on_delete_attr_clicked,
            "on_update_attr_clicked" : self.on_update_attr_clicked,
            })
        self.redraw_attr_list()

    def update_info(self):
        fname = self.object.getPath()
        if self.object.getLocal():
            self.change_dialog.get_widget("path").set_text("<local>")
            self.makelocal.set_sensitive(0)
        else:
            self.change_dialog.get_widget("path").set_text(fname)
            self.makelocal.set_sensitive(1)

    def on_make_local_clicked(self, obj):
        name = RelImage.import_media_object(self.object.getPath(),
                                            self.path,
                                            self.object.getId())
        self.object.setPath(name)
        self.object.setLocal(1)
        self.update_info()
        if self.update != None:
            self.update()

    def redraw_attr_list(self):
        utils.redraw_list(self.alist,self.attr_list,disp_attr)

    def button_press(self,obj,event):
        if len(obj.selection) <= 0:
            return
        data = obj.get_row_data(obj.selection[0])
        if data != None:
            data[0](data[1],data[2])
        
    def display_refs(self):
        index = 0
        ref = self.change_dialog.get_widget("refinfo")
        ref.connect('button-press-event',self.button_press)
        for p in self.db.getPersonMap().values():
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    ref.append([_("Person"),p.getId(),Config.nameof(p)])
                    ref.set_row_data(index,(EditPerson.EditPerson,p,self.db))
                    index = index + 1
        for p in self.db.getFamilyMap().values():
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    ref.append([_("Family"),p.getId(),utils.family_name(p)])
                    ref.set_row_data(index,(Marriage.Marriage,p,self.db))
                    index = index + 1
        for p in self.db.getSourceMap().values():
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    ref.append([_("Source"),p.getId(),p.getTitle()])
                    ref.set_row_data(index,(EditSource.EditSource,p,self.db))
                    index = index + 1
        for p in self.db.getPlaceMap().values():
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    ref.append([_("Place"),p.getId(),p.get_title()])
                    ref.set_row_data(index,(EditPlace.EditPlace,p,self.db))
                    index = index + 1
        
    def on_notebook_switch_page(self,obj,junk,page):
        if page == 3:
            self.display_refs()
            
    def on_apply_clicked(self, obj):
        text = self.notes.get_chars(0,-1)
        desc = self.descr_window.get_text()
        note = self.object.getNote()
        if text != note or desc != self.object.getDescription():
            self.object.setNote(text)
            self.object.setDescription(desc)
            utils.modified()
        if self.lists_changed:
            self.object.setAttributeList(self.alist)
            utils.modified()
        if self.update != None:
            self.update()

    def on_ok_clicked(self, obj):
        self.on_apply_clicked(obj)
        utils.destroy_passed_object(obj)
        
    def on_attr_list_select_row(self,obj,row,b,c):
        attr = obj.get_row_data(row)

        self.attr_type.set_label(attr.getType())
        self.attr_value.set_text(attr.getValue())
        self.attr_details.set_text(utils.get_detail_text(attr))

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        if len(obj.selection) > 0:
            row = obj.selection[0]
            attr = obj.get_row_data(row)
            AttrEdit.AttributeEditor(self,attr,"Media Object",[])

    def on_delete_attr_clicked(self,obj):
        if utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        AttrEdit.AttributeEditor(self,None,"Media Object",[])

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_attr(attr):
    detail = utils.get_detail_flags(attr)
    return [const.display_pattr(attr.getType()),attr.getValue(),detail]


class DeleteMediaQuery:

    def __init__(self,media,db,update):
        self.db = db
        self.media = media
        self.update = update
        
    def query_response(self,ans):
        if ans == 1:
            return
        del self.db.getObjectMap()[self.media.getId()]
        utils.modified()

        for p in self.db.getPersonMap().values():
            nl = []
            change = 0
            for photo in p.getPhotoList():
                if photo.getReference() != self.media:
                    nl.append(photo)
                else:
                    change = 1
            if change:
                p.setPhotoList(nl)

        for p in self.db.getFamilyMap().values():
            nl = []
            change = 0
            for photo in p.getPhotoList():
                if photo.getReference() != self.media:
                    nl.append(photo)
                else:
                    change = 1
            if change:
                p.setPhotoList(nl)

        for p in self.db.getSourceMap().values():
            nl = []
            change = 0
            for photo in p.getPhotoList():
                if photo.getReference() != self.media:
                    nl.append(photo)
                else:
                    change = 1
            if change:
                p.setPhotoList(nl)

        for p in self.db.getPlaceMap().values():
            nl = []
            change = 0
            for photo in p.getPhotoList():
                if photo.getReference() != self.media:
                    nl.append(photo)
                else:
                    change = 1
            if change:
                p.setPhotoList(nl)

        if self.update:
            self.update(0)


