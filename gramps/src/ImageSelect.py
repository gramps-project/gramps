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
import Utils
import GrampsCfg
import Plugins
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

    last_path = ""

    def __init__(self, path, db, parent):
        """Creates an edit window.  Associates a person with the window."""
        self.path       = path;
        self.db         = db
        self.dataobj    = None
        self.icon_cache = []
        self.parent     =  parent

    def add_thumbnail(self, photo):
        "should be overrridden"
        pass

    def load_images(self):
        "should be overrridden"
        pass

    def create_add_dialog(self):
        """Create the gnome dialog for selecting a new photo and entering
        its description.""" 

        if self.path == '':
            return
            
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
            "destroy_passed_object" : Utils.destroy_passed_object
            })

        if ImageSelect.last_path != "":
            self.glade.get_widget("photosel").set_default_path(ImageSelect.last_path)
        window.editable_enters(self.description)
        window.show()

    def on_name_changed(self, obj):
        """The filename has changed.  Verify it and load the picture."""
        filename = self.fname.get_text()

        basename = os.path.basename(filename)
        (root,ext) = os.path.splitext(basename)
        old_title  = self.description.get_text()

        if old_title == "" or old_title == self.temp_name:
            self.description.set_text(root)
        self.temp_name = root
        
        if os.path.isfile(filename):
            type = Utils.get_mime_type(filename)
            if type[0:5] == "image":
                image = RelImage.scale_image(filename,const.thumbScale)
                self.image.load_imlib(image)
            else:
                self.image.load_file(Utils.find_icon(type))

    def on_savephoto_clicked(self, obj):
        """Save the photo in the dataobj object.  (Required function)"""
        filename = self.glade.get_widget("photosel").get_full_path(0)
        ImageSelect.last_path = os.path.dirname(filename)
        
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
            type = Utils.get_mime_type(filename)
            mobj = Photo()
            if description == "":
                description = os.path.basename(filename)
            mobj.setDescription(description)
            mobj.setMimeType(type)
            self.savephoto(mobj)

            if type[0:5] == "image":
                if self.external.get_active() == 0:
                    name = RelImage.import_media_object(filename,self.path,
                                                        mobj.getId())
                    mobj.setLocal(1)
                else:
                    name = filename
            else:
                if self.external.get_active() == 1:
                    name = filename
                else:
                    name = RelImage.import_media_object(filename,self.path,
                                                        mobj.getId())
                    mobj.setLocal(1)
            mobj.setPath(name)
            
        self.parent.lists_changed = 1
        Utils.destroy_passed_object(obj)
        self.load_images()

    def savephoto(self, photo):
        """Save the photo in the dataobj object - must be overridden"""
    	pass

#-------------------------------------------------------------------------
#
# Gallery class - This class handles all the logic underlying a
# picture gallery.  This class does not load or contain the widget
# data structure to actually display the gallery.
#
#-------------------------------------------------------------------------
class Gallery(ImageSelect):
    def __init__(self, dataobj, path, icon_list, db, parent):
        ImageSelect.__init__(self, path, db, parent)

        t = [
            ('STRING', 0, 0),
            ('text/plain',0,0),
            ('text/uri-list',0,2),
            ('application/x-rootwin-drop',0,1)]

        if path:
            icon_list.drag_dest_set(GTK.DEST_DEFAULT_ALL, t,
                                    GDK.ACTION_COPY | GDK.ACTION_MOVE)
            icon_list.connect("drag_data_received",
                              self.on_photolist_drag_data_received)
            icon_list.drag_source_set(GDK.BUTTON1_MASK|GDK.BUTTON3_MASK,t,
                                      GDK.ACTION_COPY | GDK.ACTION_MOVE)
            icon_list.connect("drag_data_get",
                              self.on_photolist_drag_data_get)
        
        # Remember arguments
        self.path      = path;
        self.dataobj   = dataobj;
        self.icon_list = icon_list;

        # Local object variables
        self.selectedIcon = -1
        self.currentImages = []

    def savephoto(self, photo):
        """Save the photo in the dataobj object.  (Required function)"""
        self.db.addObject(photo)
        oref = ObjectRef()
        oref.setReference(photo)
        self.dataobj.addPhoto(oref)
        self.add_thumbnail(oref)

    def add_thumbnail(self, photo):
        """Scale the image and add it to the IconList."""
        object = photo.getReference()
        name = Utils.thumb_path(self.db.getSavePath(),object)
        description = object.getDescription()
        if len(description) > 50:
            description = "%s..." % description[0:50]
        self.icon_list.append(name,description)
        
    def load_images(self):
        """clears the currentImages list to free up any cached 
        Imlibs.  Then add each photo in the place's list of photos to the 
        photolist window."""
        self.icon_list.freeze()
        self.icon_list.clear()
        self.icon_cache = []
        for photo in self.dataobj.getPhotoList():
            self.add_thumbnail(photo)
        self.icon_list.thaw()

    def on_photo_select_icon(self, obj,iconNumber,event):
        """User clicked on a photo.  Remember which one."""
        self.selectedIcon = iconNumber

    def on_photolist_drag_data_received(self,w, context, x, y, data, info, time):
        import urlparse
	if data and data.format == 8:
            icon_index = w.get_icon_at(x,y)
            d = string.strip(string.replace(data.data,'\0',' '))
            protocol,site,file, j,k,l = urlparse.urlparse(d)
            if protocol == "file":
                name = file
                mime = Utils.get_mime_type(name)
                photo = Photo()
                photo.setPath(name)
                photo.setMimeType(mime)
                basename = os.path.basename(name)
                (root,ext) = os.path.splitext(basename)
                photo.setDescription(root)
                self.savephoto(photo)
                if GrampsCfg.mediaref == 0:
                    name = RelImage.import_media_object(name,self.path,photo.getId())
                    photo.setPath(name)
                    photo.setLocal(1)
                self.parent.lists_changed = 1
                if GrampsCfg.globalprop:
                    Utils.modified()
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
                mime = Utils.get_mime_type(tfile)
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
                    photo.setLocal(1)
                    photo.setPath(name)
                except:
                    photo.setPath(tfile)
                    w.drag_finish(context, 1, 0, time)
                    return
                self.add_thumbnail(oref)
                self.parent.lists_changed = 1
                if GrampsCfg.globalprop:
                    Utils.modified()
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
                                Utils.modified()
                                self.parent.lists_changed = 1
                                self.load_images()
                                return
                        index = index + 1
                    oref = ObjectRef()
                    oref.setReference(self.db.findObjectNoMap(data.data))
                    self.dataobj.addPhoto(oref)
                    self.add_thumbnail(oref)
                    self.parent.lists_changed = 1
                    if GrampsCfg.globalprop:
                        LocalMediaProperties(oref,self.path,self)
                    Utils.modified()
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

    def on_add_photo_clicked(self, obj):
        """User wants to add a new photo.  Create a dialog to find out
        which photo they want."""
        self.create_add_dialog()

    def on_delete_photo_clicked(self, obj):
        """User wants to delete a new photo. Remove it from the displayed
        thumbnails, and remove it from the dataobj photo list."""
        icon = self.selectedIcon
        if icon != -1:
            self.icon_list.remove(icon)
            list = self.dataobj.getPhotoList()
            del list[icon]
            self.dataobj.setPhotoList(list)
            self.parent.lists_changed = 1
            if len(self.dataobj.getPhotoList()) == 0:
                self.selectedIcon = -1
            else:
                self.selectedIcon = 0
                self.icon_list.select_icon(0)

    def on_button_press_event(self, obj, event):
        """Look for right-clicks on a picture and create a popup
        menu of the available actions."""
        icon = self.selectedIcon
        if icon == -1:
            return
    
        if event.button == 3:
            photo = self.dataobj.getPhotoList()[icon]
            menu = gtk.GtkMenu()
            item = gtk.GtkTearoffMenuItem()
            item.show()
            menu.append(item)
            Utils.add_menuitem(menu,_("View in the default viewer"),
                               None,self.popup_view_photo)
            object = photo.getReference()
            if object.getMimeType()[0:5] == "image":
                Utils.add_menuitem(menu,_("Edit with the GIMP"),
                                   None,self.popup_edit_photo)
            Utils.add_menuitem(menu,_("Edit Object Properties"),None,
                               self.popup_change_description)
            if object.getLocal() == 0:
                Utils.add_menuitem(menu,_("Convert to local copy"),None,
                                   self.popup_convert_to_private)
            menu.popup(None,None,None,0,0)

    def popup_view_photo(self, obj):
        """Open this picture in a picture viewer"""
        photo = self.dataobj.getPhotoList()[self.selectedIcon]
        Utils.view_photo(photo.getReference())
    
    def popup_edit_photo(self, obj):
        """Open this picture in a picture editor"""
        photo = self.dataobj.getPhotoList()[self.selectedIcon]
        if os.fork() == 0:
            os.execvp(const.editor,[const.editor,
                                    photo.getReference().getPath()])
    
    def popup_convert_to_private(self, obj):
        """Copy this picture into gramps private database instead of
        leaving it as an external data object."""
        photo = self.dataobj.getPhotoList()[self.selectedIcon]
        object = photo.getReference()
        name = RelImage.import_media_object(object.getPath(),self.path,
                                            object.getId())
        object.setPath(name)
        object.setLocal(1)

    def popup_change_description(self, obj):
        """Bring up a window allowing the user to edit the description
        of a picture."""
        if self.selectedIcon >=0:
            photo = self.dataobj.getPhotoList()[self.selectedIcon]
            LocalMediaProperties(photo,self.path,self)

#-------------------------------------------------------------------------
#
# LocalMediaProperties
#
#-------------------------------------------------------------------------
class LocalMediaProperties:

    def __init__(self,photo,path,parent):
        self.photo = photo
        self.object = photo.getReference()
        self.alist = photo.getAttributeList()[:]
        self.lists_changed = 0
        self.parent = parent
        
        fname = self.object.getPath()
        self.change_dialog = libglade.GladeXML(const.imageselFile,
                                               "change_description")
        descr_window = self.change_dialog.get_widget("description")
        pixmap = self.change_dialog.get_widget("pixmap")
        self.attr_type = self.change_dialog.get_widget("attr_type")
        self.attr_value = self.change_dialog.get_widget("attr_value")
        self.attr_details = self.change_dialog.get_widget("attr_details")
        self.attr_list = self.change_dialog.get_widget("attr_list")
        
        descr_window.set_text(self.object.getDescription())
        mtype = self.object.getMimeType()
        pixmap.load_file(Utils.thumb_path(path,self.object))

        self.change_dialog.get_widget("private").set_active(photo.getPrivacy())
        self.change_dialog.get_widget("gid").set_text(self.object.getId())

        if self.object.getLocal():
            self.change_dialog.get_widget("path").set_text("<local>")
        else:
            self.change_dialog.get_widget("path").set_text(fname)

        mt = Utils.get_mime_description(mtype)
        self.change_dialog.get_widget("type").set_text(mt)
        self.change_dialog.get_widget("notes").insert_defaults(photo.getNote())
        self.change_dialog.signal_autoconnect({
            "on_cancel_clicked" : Utils.destroy_passed_object,
            "on_up_clicked" : self.on_up_clicked,
            "on_down_clicked" : self.on_down_clicked,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_apply_clicked" : self.on_apply_clicked,
            "on_attr_list_select_row" : self.on_attr_list_select_row,
            "on_add_attr_clicked": self.on_add_attr_clicked,
            "on_delete_attr_clicked" : self.on_delete_attr_clicked,
            "on_update_attr_clicked" : self.on_update_attr_clicked,
            })
        self.redraw_attr_list()

    def on_up_clicked(self,obj):
        if len(obj.selection) == 0:
            return
        row = obj.selection[0]
        if row != 0:
            obj.select_row(row-1,0)

    def on_down_clicked(self,obj):
        if len(obj.selection) == 0:
            return
        row = obj.selection[0]
        if row != obj.rows-1:
            obj.select_row(row+1,0)

    def redraw_attr_list(self):
        Utils.redraw_list(self.alist,self.attr_list,disp_attr)
        
    def on_apply_clicked(self, obj):
        priv = self.change_dialog.get_widget("private").get_active()
        text = self.change_dialog.get_widget("notes").get_chars(0,-1)
        note = self.photo.getNote()
        if text != note or priv != self.photo.getPrivacy():
            self.photo.setNote(text)
            self.photo.setPrivacy(priv)
            self.parent.lists_changed = 1
            Utils.modified()
        if self.lists_changed:
            self.photo.setAttributeList(self.alist)
            self.parent.lists_changed = 1
            Utils.modified()

    def on_ok_clicked(self, obj):
        self.on_apply_clicked(obj)
        Utils.destroy_passed_object(obj)
        
    def on_attr_list_select_row(self,obj,row,b,c):
        attr = obj.get_row_data(row)

        self.attr_type.set_label(attr.getType())
        self.attr_value.set_text(attr.getValue())
        self.attr_details.set_text(Utils.get_detail_text(attr))

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        if len(obj.selection) > 0:
            row = obj.selection[0]
            attr = obj.get_row_data(row)
            AttrEdit.AttributeEditor(self,attr,"Media Object",
                                     Plugins.get_image_attributes())

    def on_delete_attr_clicked(self,obj):
        if Utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        AttrEdit.AttributeEditor(self,None,"Media Object",
                                 Plugins.get_image_attributes())

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
        self.refs = 0

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
        pixmap.load_file(Utils.thumb_path(self.path,self.object))

        self.change_dialog.get_widget("gid").set_text(self.object.getId())
        self.makelocal = self.change_dialog.get_widget("makelocal")

        self.update_info()
        
        self.change_dialog.get_widget("type").set_text(Utils.get_mime_description(mtype))
        self.notes.insert_defaults(object.getNote())
        self.change_dialog.signal_autoconnect({
            "on_cancel_clicked"      : Utils.destroy_passed_object,
            "on_up_clicked"          : self.on_up_clicked,
            "on_down_clicked"        : self.on_down_clicked,
            "on_ok_clicked"          : self.on_ok_clicked,
            "on_apply_clicked"       : self.on_apply_clicked,
            "on_attr_list_select_row": self.on_attr_list_select_row,
            "on_add_attr_clicked"    : self.on_add_attr_clicked,
            "on_attr_button_press"   : self.attr_double_click,
            "on_notebook_switch_page": self.on_notebook_switch_page,
            "on_make_local_clicked"  : self.on_make_local_clicked,
            "on_delete_attr_clicked" : self.on_delete_attr_clicked,
            "on_update_attr_clicked" : self.on_update_attr_clicked,
            })
        self.redraw_attr_list()

    def attr_double_click(self,obj,event):
         if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
             self.on_update_attr_clicked(obj)

    def on_up_clicked(self,obj):
        if len(obj.selection) == 0:
            return
        row = obj.selection[0]
        if row != 0:
            obj.select_row(row-1,0)

    def on_down_clicked(self,obj):
        if len(obj.selection) == 0:
            return
        row = obj.selection[0]
        if row != obj.rows-1:
            obj.select_row(row+1,0)

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
        Utils.redraw_list(self.alist,self.attr_list,disp_attr)

    def button_press(self,obj,event):
        if len(obj.selection) <= 0:
            return
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            data = obj.get_row_data(obj.selection[0])
            if data != None:
                data[0](data[1],data[2])
        
    def display_refs(self):
        if self.refs == 1:
            return
        self.refs = 1
        index = 0
        ref = self.change_dialog.get_widget("refinfo")
        ref.connect('button-press-event',self.button_press)
        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    ref.append([_("Person"),p.getId(),GrampsCfg.nameof(p)])
                    ref.set_row_data(index,(EditPerson.EditPerson,p,self.db))
                    index = index + 1
        for p in self.db.getFamilyMap().values():
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    ref.append([_("Family"),p.getId(),Utils.family_name(p)])
                    ref.set_row_data(index,(Marriage.Marriage,p,self.db))
                    index = index + 1
        for key in self.db.getSourceKeys():
            p = self.db.getSource(key)
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    ref.append([_("Source"),p.getId(),p.getTitle()])
                    ref.set_row_data(index,(EditSource.EditSource,p,self.db))
                    index = index + 1
        for key in self.db.getPlaceKeys():
            p = self.db.getPlace(key)
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
            Utils.modified()
        if self.lists_changed:
            self.object.setAttributeList(self.alist)
            Utils.modified()
        if self.update != None:
            self.update()

    def on_ok_clicked(self, obj):
        self.on_apply_clicked(obj)
        Utils.destroy_passed_object(obj)
        
    def on_attr_list_select_row(self,obj,row,b,c):
        attr = obj.get_row_data(row)

        self.attr_type.set_label(attr.getType())
        self.attr_value.set_text(attr.getValue())
        self.attr_details.set_text(Utils.get_detail_text(attr))

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        if len(obj.selection) > 0:
            row = obj.selection[0]
            attr = obj.get_row_data(row)
            AttrEdit.AttributeEditor(self,attr,"Media Object",
                                     Plugins.get_image_attributes())

    def on_delete_attr_clicked(self,obj):
        if Utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        AttrEdit.AttributeEditor(self,None,"Media Object",
                                 Plugins.get_image_attributes())

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_attr(attr):
    detail = Utils.get_detail_flags(attr)
    return [const.display_pattr(attr.getType()),attr.getValue(),detail]


class DeleteMediaQuery:

    def __init__(self,media,db,update):
        self.db = db
        self.media = media
        self.update = update
        
    def query_response(self):
        del self.db.getObjectMap()[self.media.getId()]
        Utils.modified()

        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
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

        for key in self.db.getSourceKeys():
            p = self.db.getSource(key)
            nl = []
            change = 0
            for photo in p.getPhotoList():
                if photo.getReference() != self.media:
                    nl.append(photo)
                else:
                    change = 1
            if change:
                p.setPhotoList(nl)

        for key in self.db.getPlaceKeys():
            p = self.db.getPlace(key)
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


