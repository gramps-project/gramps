#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

# $Id$

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import string
import urlparse
#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gnome
import gnome.ui
import gnome.canvas
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsCfg
import Plugins
import RelLib
import RelImage
import ListModel
import SelectObject
import grampslib

from QuestionDialog import ErrorDialog
from gettext import gettext as _

_IMAGEX = 140
_IMAGEY = 150
_PAD = 5

_last_path = ""
_iconlist_refs = []

#-------------------------------------------------------------------------
#
# ImageSelect class
#
#-------------------------------------------------------------------------
class ImageSelect:

    def __init__(self, path, db, parent, parent_window=None):
        """Creates an edit window.  Associates a person with the window."""
        self.path        = path;
        self.db          = db
        self.dataobj     = None
        self.parent      = parent
        self.parent_window = parent_window
        self.canvas_list = {}
        self.p_map       = {}
        self.canvas      = None
        
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
            
        self.glade       = gtk.glade.XML(const.imageselFile,"imageSelect","gramps")
        self.window      = self.glade.get_widget("imageSelect")

        self.fname       = self.glade.get_widget("fname")
        self.image       = self.glade.get_widget("image")
        self.description = self.glade.get_widget("photoDescription")
        self.external    = self.glade.get_widget("private")
        self.photosel    = self.glade.get_widget("photosel")
        self.temp_name   = ""

        Utils.set_titles(self.window,self.glade.get_widget('title'),
                         _('Select a media object'))
        
        self.glade.signal_autoconnect({
            "on_name_changed" : self.on_name_changed,
            "on_help_imagesel_clicked" : self.on_help_imagesel_clicked,
            })

        if os.path.isdir(_last_path):
            self.photosel.set_default_path(_last_path)
            self.photosel.set_filename(_last_path)
            self.photosel.gtk_entry().set_position(len(_last_path))

        if self.parent_window:
            self.window.set_transient_for(self.parent_window)
        self.window.show()
        self.val = self.window.run()
        if self.val == gtk.RESPONSE_OK:
            self.on_savephoto_clicked()
        self.window.destroy()

    def on_help_imagesel_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-quick')
        self.val = self.window.run()

    def on_name_changed(self, obj):
        """The filename has changed.  Verify it and load the picture."""
        filename = unicode(self.fname.get_text())

        basename = os.path.basename(filename)
        (root,ext) = os.path.splitext(basename)
        old_title  = unicode(self.description.get_text())

        if old_title == "" or old_title == self.temp_name:
            self.description.set_text(root)
        self.temp_name = root
        
        if os.path.isfile(filename):
            type = Utils.get_mime_type(filename)
            if type[0:5] == "image":
                image = RelImage.scale_image(filename,const.thumbScale)
                self.image.set_from_pixbuf(image)
            else:
                i = gtk.gdk.pixbuf_new_from_file(Utils.find_icon(type))
                self.image.set_from_pixbuf(i)

    def on_savephoto_clicked(self):
        """Save the photo in the dataobj object.  (Required function)"""
        global _last_path
        
        filename = self.photosel.get_full_path(0)
        _last_path = os.path.dirname(filename)
        
        description = unicode(self.description.get_text())

        if os.path.exists(filename) == 0:
            msgstr = _("Cannot import %s")
            msgstr2 = _("The filename supplied could not be found.")
            ErrorDialog(msgstr % filename, msgstr2)
            return

        already_imported = None
        for o in self.db.getObjectMap().values():
            if o.getPath() == filename:
                already_imported = o
                break

        if (already_imported):
            oref = RelLib.ObjectRef()
            oref.setReference(already_imported)
            self.dataobj.addPhoto(oref)
            self.add_thumbnail(oref)
        else:
            type = Utils.get_mime_type(filename)
            mobj = RelLib.Photo()
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
        self.load_images()

    def savephoto(self, photo):
        """Save the photo in the dataobj object - must be overridden"""
    	pass

_drag_targets = [
    ('STRING', 0, 0),
    ('text/plain',0,0),
    ('text/uri-list',0,2),
    ('application/x-rootwin-drop',0,1)]

#-------------------------------------------------------------------------
#
# Gallery class - This class handles all the logic underlying a
# picture gallery.  This class does not load or contain the widget
# data structure to actually display the gallery.
#
#-------------------------------------------------------------------------
class Gallery(ImageSelect):
    def __init__(self, dataobj, path, icon_list, db, parent, parent_window=None):
        ImageSelect.__init__(self, path, db, parent, parent_window)

        if path:
            icon_list.drag_dest_set(gtk.DEST_DEFAULT_ALL, _drag_targets,
                                    gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
            icon_list.connect('event',self.item_event)
            icon_list.connect("drag_data_received",
                              self.on_photolist_drag_data_received)
            icon_list.connect("drag_data_get",
                              self.on_photolist_drag_data_get)
            icon_list.connect("drag_begin", self.on_drag_begin)

        _iconlist_refs.append(icon_list)
        self.in_event = 0
        
        # Remember arguments
        self.path      = path;
        self.dataobj   = dataobj;
        self.iconlist = icon_list;
        self.root = self.iconlist.root()

        # Local object variables
        self.y = 0
        self.remember_x = -1
        self.remember_y = -1
        self.button = None
        self.drag_item = None
        self.sel = None
        self.photo = None

    def close(self):
        self.iconlist.hide()
        for a in self.canvas_list.values():
            a[0].destroy()
            a[1].destroy()
            a[2].destroy()
        self.p_map = None
        self.canvas_list = None
        
    def on_canvas1_event(self,obj,event):
        """
        Handle resize events over the canvas, redrawing if the size changes
        """

    def on_drag_begin(self,obj,context):
        if const.dnd_images:
            mtype = self.sel_obj.getReference().getMimeType()
            name = Utils.thumb_path(self.db.getSavePath(),self.sel_obj.getReference())
            pix = gtk.gdk.pixbuf_new_from_file(name)
            context.set_icon_pixbuf(pix,0,0)

    def item_event(self, widget, event=None):

        if self.in_event:
            return
        self.in_event = 1
        if self.button and event.type == gtk.gdk.MOTION_NOTIFY :
            if widget.drag_check_threshold(self.remember_x,self.remember_y,
                                           event.x,event.y):
                self.drag_item = widget.get_item_at(self.remember_x,
                                                    self.remember_y)
                icon_index = self.get_index(widget,event.x,event.y)-1
                self.sel_obj = self.dataobj.getPhotoList()[icon_index]
                if self.drag_item:
                    widget.drag_begin(_drag_targets,
                                      gtk.gdk.ACTION_COPY|gtk.gdk.ACTION_MOVE,
                                      self.button, event)
                    
            self.in_event = 0
            return gtk.TRUE

        style = self.iconlist.get_style()
        
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 1:
                # Remember starting position.

                item = widget.get_item_at(event.x,event.y)
                if item:
                    (i,t,b,self.photo,oid) = self.p_map[item]
                    t.set(fill_color_gdk=style.fg[gtk.STATE_SELECTED])
                    b.set(fill_color_gdk=style.bg[gtk.STATE_SELECTED])
                    if self.sel:
                        (i,t,b,photo,oid) = self.p_map[self.sel]
                        t.set(fill_color_gdk=style.fg[gtk.STATE_NORMAL])
                        b.set(fill_color_gdk=style.bg[gtk.STATE_NORMAL])
                        
                    self.sel = item

                self.remember_x = event.x
                self.remember_y = event.y
                self.button = event.button
                self.in_event = 0
                return gtk.TRUE

            elif event.button == 3:
                item = widget.get_item_at(event.x,event.y)
                if item:
                    (i,t,b,self.photo,oid) = self.p_map[item]
                    self.show_popup(self.photo,event)
                self.in_event = 0
                return gtk.TRUE
        elif event.type == gtk.gdk.BUTTON_RELEASE:
            self.button = 0
        elif event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            item = widget.get_item_at(event.x,event.y)
            if item:
                (i,t,b,self.photo,oid) = self.p_map[item]
                LocalMediaProperties(self.photo,self.path,self)
            self.in_event = 0
            return gtk.TRUE
        elif event.type == gtk.gdk.MOTION_NOTIFY:
            if event.state & gtk.gdk.BUTTON1_MASK:
                # Get the new position and move by the difference
                new_x = event.x
                new_y = event.y

                self.remember_x = new_x
                self.remember_y = new_y

                self.in_event = 0
                return gtk.TRUE
            
        if event.type == gtk.gdk.EXPOSE:
            self.load_images()

        self.in_event = 0
        return gtk.FALSE

    def savephoto(self, photo):
        """Save the photo in the dataobj object.  (Required function)"""
        self.db.addObject(photo)
        oref = RelLib.ObjectRef()
        oref.setReference(photo)
        self.dataobj.addPhoto(oref)

    def add_thumbnail(self, photo):
        """Scale the image and add it to the IconList."""
        object = photo.getReference()
        oid = object.getId()

        if self.canvas_list.has_key(oid):
            (grp,item,text,x,y) = self.canvas_list[oid]
            if x != self.cx or y != self.cy:
                grp.move(self.cx-x,self.cy-y)
        else:
            import gobject
            
            name = Utils.thumb_path(self.db.getSavePath(),object)

            description = object.getDescription()
            if len(description) > 20:
                description = "%s..." % description[0:20]

            try:
                image = gtk.gdk.pixbuf_new_from_file(name)
            except gobject.GError,msg:
                ErrorDialog(str(msg))
                image = gtk.gdk.pixbuf_new_from_file(const.icon)
            except:
                ErrorDialog(_("Thumbnail %s could not be found") % name)
                image = gtk.gdk.pixbuf_new_from_file(const.icon)
            
            x = image.get_width()
            y = image.get_height()

            grp = self.root.add(gnome.canvas.CanvasGroup,x=self.cx,y=self.cy)

            xloc = (_IMAGEX-x)/2
            yloc = (_IMAGEY-y)/2

            style = self.iconlist.get_style()

            box = grp.add(gnome.canvas.CanvasRect,x1=0,x2=_IMAGEX,y1=_IMAGEY-20,
                          y2=_IMAGEY, fill_color_gdk=style.bg[gtk.STATE_NORMAL])
            item = grp.add(gnome.canvas.CanvasPixbuf,
                           pixbuf=image,x=xloc, y=yloc)
            text = grp.add(gnome.canvas.CanvasText, x=_IMAGEX/2, 
                           anchor=gtk.ANCHOR_CENTER,
                           justification=gtk.JUSTIFY_CENTER,
                           y=_IMAGEY-10, text=description)

            bnds = text.get_bounds()
            print bnds
            while bnds[0] <0:
                description = description[0:-4] + "..."
                text.set(text=description)
                bnds = text.get_bounds()
                print bnds

            for i in [ item, text, box, grp ] :
                self.p_map[i] = (item,text,box,photo,oid)
                i.show()
            
        self.canvas_list[oid] = (grp,item,text,self.cx,self.cy)

        self.cx += _PAD + _IMAGEX
        
        if self.cx + _PAD + _IMAGEX > self.x:
            self.cx = _PAD
            self.cy += _PAD + _IMAGEY
        
    def load_images(self):
        """clears the currentImages list to free up any cached 
        Imlibs.  Then add each photo in the place's list of photos to the 
        photolist window."""

        self.pos = 0
        self.cx = _PAD
        self.cy = _PAD
        
        (self.x,self.y) = self.iconlist.get_size()

        self.max = (self.x)/(_IMAGEX+_PAD)

        for photo in self.dataobj.getPhotoList():
            self.add_thumbnail(photo)

        if self.cy > self.y:
            self.iconlist.set_scroll_region(0,0,self.x,self.cy)
        else:
            self.iconlist.set_scroll_region(0,0,self.x,self.y)
        
        if self.dataobj.getPhotoList():
            Utils.bold_label(self.parent.gallery_label)
        else:
            Utils.unbold_label(self.parent.gallery_label)

    def get_index(self,obj,x,y):
        x_offset = x/(_IMAGEX+_PAD)
        y_offset = y/(_IMAGEY+_PAD)
        index = (y_offset*(1+self.max))+x_offset
        return min(index,len(self.dataobj.getPhotoList()))

    def on_photolist_drag_data_received(self,w, context, x, y, data, info, time):
	if data and data.format == 8:
            icon_index = self.get_index(w,x,y)
            d = string.strip(string.replace(data.data,'\0',' '))
            protocol,site,file, j,k,l = urlparse.urlparse(d)
            if protocol == "file":
                name = file
                mime = Utils.get_mime_type(name)
                photo = RelLib.Photo()
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
                    ErrorDialog(t,str(msg))
                    return
                mime = Utils.get_mime_type(tfile)
                photo = RelLib.Photo()
                photo.setMimeType(mime)
                photo.setDescription(d)
                photo.setLocal(1)
                photo.setPath(tfile)
                self.db.addObject(photo)
                oref = RelLib.ObjectRef()
                oref.setReference(photo)
                self.dataobj.addPhoto(oref)
                try:
                    id = photo.getId()
                    name = RelImage.import_media_object(tfile,self.path,id)
                    photo.setLocal(1)
                    photo.setPath(name)
                except:
                    photo.setPath(tfile)
                    return
                self.add_thumbnail(oref)
                self.parent.lists_changed = 1
                if GrampsCfg.globalprop:
                    Utils.modified()
                    GlobalMediaProperties(self.db,photo,None)
            else:
                if self.db.getObjectMap().has_key(data.data):
                    icon_index = self.get_index(w,x,y)
                    index = 0
                    for p in self.dataobj.getPhotoList():
                        if data.data == p.getReference().getId():
                            if index == icon_index or icon_index == -1:
                                return
                            else:
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
                    oref = RelLib.ObjectRef()
                    oref.setReference(self.db.findObjectNoMap(data.data))
                    self.dataobj.addPhoto(oref)
                    self.add_thumbnail(oref)
                    self.parent.lists_changed = 1
                    if GrampsCfg.globalprop:
                        LocalMediaProperties(oref,self.path,self)
                    Utils.modified()
                
    def on_photolist_drag_data_get(self,w, context, selection_data, info, time):
        if info == 1:
            return
        id = self.p_map[self.drag_item]
        selection_data.set(selection_data.target, 8, id[4])
        self.drag_item = None
        
    def on_add_photo_clicked(self, obj):
        """User wants to add a new photo.  Create a dialog to find out
        which photo they want."""
        self.create_add_dialog()

    def on_select_photo_clicked(self,obj):
        """User wants to add a new object that is already in a database.  
        Create a dialog to find out which object they want."""

        s_o = SelectObject.SelectObject(self.db,_("Select an Object"))
        object = s_o.run()
        if not object:
            return
        oref = RelLib.ObjectRef()
        oref.setReference(object)
        self.dataobj.addPhoto(oref)
        self.add_thumbnail(oref)

        self.parent.lists_changed = 1
        self.load_images()

    def on_delete_photo_clicked(self, obj):
        """User wants to delete a new photo. Remove it from the displayed
        thumbnails, and remove it from the dataobj photo list."""

        if self.sel:
            (i,t,b,photo,oid) = self.p_map[self.sel]
            val = self.canvas_list[photo.getReference().getId()]
            val[0].hide()
            val[1].hide()
            val[2].hide()

            l = self.dataobj.getPhotoList()
            l.remove(photo)
            self.dataobj.setPhotoList(l)
            self.parent.lists_changed = 1
            self.load_images()

    def on_edit_photo_clicked(self, obj):
        """User wants to delete a new photo. Remove it from the displayed
        thumbnails, and remove it from the dataobj photo list."""

        if self.sel:
            (i,t,b,photo,oid) = self.p_map[self.sel]
            LocalMediaProperties(photo,self.path,self)
        
    def show_popup(self, photo, event):
        """Look for right-clicks on a picture and create a popup
        menu of the available actions."""
        
        menu = gtk.Menu()
        menu.set_title(_("Media Object"))
        object = photo.getReference()
        mtype = object.getMimeType()
        progname = grampslib.default_application_name(mtype)
        
        Utils.add_menuitem(menu,_("Open in %s") % progname,
                           photo,self.popup_view_photo)
        if mtype[0:5] == "image":
            Utils.add_menuitem(menu,_("Edit with the GIMP"),
                               photo,self.popup_edit_photo)
        Utils.add_menuitem(menu,_("Edit Object Properties"),photo,
                           self.popup_change_description)
        if object.getLocal() == 0:
            Utils.add_menuitem(menu,_("Convert to local copy"),photo,
                               self.popup_convert_to_private)
        menu.popup(None,None,None,event.button,event.time)
            
    def popup_view_photo(self, obj):
        """Open this picture in a picture viewer"""
        photo = obj.get_data('o')
        Utils.view_photo(photo.getReference())
    
    def popup_edit_photo(self, obj):
        """Open this picture in a picture editor"""
        photo = obj.get_data('o')
        if os.fork() == 0:
            os.execvp(const.editor,[const.editor,
                                    photo.getReference().getPath()])
    
    def popup_convert_to_private(self, obj):
        """Copy this picture into gramps private database instead of
        leaving it as an external data object."""
        photo = obj.get_data('o')
        object = photo.getReference()
        name = RelImage.import_media_object(object.getPath(),self.path,
                                            object.getId())
        object.setPath(name)
        object.setLocal(1)

    def popup_change_description(self, obj):
        """Bring up a window allowing the user to edit the description
        of a picture."""
        photo = obj.get_data('o')
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
        self.db = parent.db
        
        fname = self.object.getPath()
        self.change_dialog = gtk.glade.XML(const.imageselFile,"change_description","gramps")

        title = _('Change local media object properties')
        Utils.set_titles(self.change_dialog.get_widget('change_description'),
                         self.change_dialog.get_widget('title'), title)
        
        descr_window = self.change_dialog.get_widget("description")
        self.pixmap = self.change_dialog.get_widget("pixmap")
        self.attr_type = self.change_dialog.get_widget("attr_type")
        self.attr_value = self.change_dialog.get_widget("attr_value")
        self.attr_details = self.change_dialog.get_widget("attr_details")

        self.attr_list = self.change_dialog.get_widget("attr_list")
        titles = [(_('Attribute'),0,150),(_('Value'),0,100)]

        self.attr_label = self.change_dialog.get_widget("attr_local")
        self.notes_label = self.change_dialog.get_widget("notes_local")
        self.flowed = self.change_dialog.get_widget("flowed")
        self.preform = self.change_dialog.get_widget("preform")

        self.atree = ListModel.ListModel(self.attr_list,titles,
                                         self.on_attr_list_select_row,
                                         self.on_update_attr_clicked)
        
        descr_window.set_text(self.object.getDescription())
        mtype = self.object.getMimeType()

        thumb = Utils.thumb_path(path,self.object)
        if os.path.isfile(thumb):
            self.pix = gtk.gdk.pixbuf_new_from_file(thumb)
            self.pixmap.set_from_pixbuf(self.pix)

        self.change_dialog.get_widget("private").set_active(photo.getPrivacy())
        self.change_dialog.get_widget("gid").set_text(self.object.getId())

        if self.object.getLocal():
            self.change_dialog.get_widget("path").set_text("<local>")
        else:
            self.change_dialog.get_widget("path").set_text(fname)

        mt = Utils.get_mime_description(mtype)
        self.change_dialog.get_widget("type").set_text(mt)
        self.notes = self.change_dialog.get_widget("notes")
        if self.photo.getNote():
            self.notes.get_buffer().set_text(self.photo.getNote())
            Utils.bold_label(self.notes_label)
            if self.photo.getNoteFormat() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)

        self.change_dialog.signal_autoconnect({
            "on_cancel_clicked" : Utils.destroy_passed_object,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_apply_clicked" : self.on_apply_clicked,
            "on_add_attr_clicked": self.on_add_attr_clicked,
            "on_notebook_switch_page": self.on_notebook_switch_page,
            "on_update_attr_clicked": self.on_update_attr_clicked,
            "on_delete_attr_clicked" : self.on_delete_attr_clicked,
            "on_help_clicked" : self.on_help_clicked,
            })
        self.redraw_attr_list()

    def redraw_attr_list(self):
        self.atree.clear()
        self.amap = {}
        for attr in self.alist:
            d = [attr.getType(),attr.getValue()]
            iter = self.atree.add(d,attr)
            self.amap[str(attr)] = iter
        if self.alist:
            Utils.bold_label(self.attr_label)
        else:
            Utils.unbold_label(self.attr_label)
        
    def on_notebook_switch_page(self,obj,junk,page):
        t = self.notes.get_buffer()
        text = unicode(t.get_text(t.get_start_iter(),t.get_end_iter(),gtk.FALSE))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)
            
    def on_apply_clicked(self, obj):
        priv = self.change_dialog.get_widget("private").get_active()

        t = self.notes.get_buffer()
        text = unicode(t.get_text(t.get_start_iter(),t.get_end_iter(),gtk.FALSE))
        note = self.photo.getNote()
        format = self.preform.get_active()
        if text != note or priv != self.photo.getPrivacy():
            self.photo.setNote(text)
            self.photo.setPrivacy(priv)
            self.parent.lists_changed = 1
            Utils.modified()
        if format != self.photo.getNoteFormat():
            self.photo.setNoteFormat(format)
            Utils.modified()
        if self.lists_changed:
            self.photo.setAttributeList(self.alist)
            self.parent.lists_changed = 1
            Utils.modified()

    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')
        
    def on_ok_clicked(self, obj):
        self.on_apply_clicked(obj)
        Utils.destroy_passed_object(obj)
        
    def on_attr_list_select_row(self,obj):
        store,iter = self.atree.get_selected()
        if iter:
            attr = self.atree.get_object(iter)

            self.attr_type.set_label(attr.getType())
            self.attr_value.set_text(attr.getValue())
        else:
            self.attr_type.set_label('')
            self.attr_value.set_text('')

    def attr_callback(self,attr):
        self.redraw_attr_list()
        self.atree.select_iter(self.amap[str(attr)])
        
    def on_update_attr_clicked(self,obj):
        import AttrEdit

        store,iter = self.atree.get_selected()
        if iter:
            attr = self.atree.get_object(iter)
            AttrEdit.AttributeEditor(self,attr,"Media Object",
                                     Plugins.get_image_attributes(),
                                     self.attr_callback)

    def on_delete_attr_clicked(self,obj):
        if Utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        AttrEdit.AttributeEditor(self,None,"Media Object",
                                 Plugins.get_image_attributes(),
                                 self.attr_callback)

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
        self.change_dialog = gtk.glade.XML(const.imageselFile,"change_global","gramps")

        title = _('Change global media object properties')

        Utils.set_titles(self.change_dialog.get_widget('change_global'),
                         self.change_dialog.get_widget('title'),title)
        
        self.descr_window = self.change_dialog.get_widget("description")
        self.notes = self.change_dialog.get_widget("notes")
        self.pixmap = self.change_dialog.get_widget("pixmap")
        self.attr_type = self.change_dialog.get_widget("attr_type")
        self.attr_value = self.change_dialog.get_widget("attr_value")
        self.attr_details = self.change_dialog.get_widget("attr_details")

        self.attr_list = self.change_dialog.get_widget("attr_list")

        self.attr_label = self.change_dialog.get_widget("attrGlobal")
        self.notes_label = self.change_dialog.get_widget("notesGlobal")
        self.refs_label = self.change_dialog.get_widget("refsGlobal")
        self.flowed = self.change_dialog.get_widget("global_flowed")
        self.preform = self.change_dialog.get_widget("global_preform")

        titles = [(_('Attribute'),0,150),(_('Value'),1,100)]

        self.atree = ListModel.ListModel(self.attr_list,titles,
                                         self.on_attr_list_select_row,
                                         self.on_update_attr_clicked)
        
        self.descr_window.set_text(self.object.getDescription())
        mtype = self.object.getMimeType()
        pb = gtk.gdk.pixbuf_new_from_file(Utils.thumb_path(self.path,self.object))
        self.pixmap.set_from_pixbuf(pb)

        self.change_dialog.get_widget("gid").set_text(self.object.getId())
        self.makelocal = self.change_dialog.get_widget("makelocal")

        self.update_info()
        
        self.change_dialog.get_widget("type").set_text(Utils.get_mime_description(mtype))
        if self.object.getNote():
            self.notes.get_buffer().set_text(self.object.getNote())
            Utils.bold_label(self.notes_label)
            if self.object.getNoteFormat() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)

        self.change_dialog.signal_autoconnect({
            "on_cancel_clicked"      : Utils.destroy_passed_object,
            "on_up_clicked"          : self.on_up_clicked,
            "on_down_clicked"        : self.on_down_clicked,
            "on_ok_clicked"          : self.on_ok_clicked,
            "on_apply_clicked"       : self.on_apply_clicked,
            "on_add_attr_clicked"    : self.on_add_attr_clicked,
            "on_notebook_switch_page": self.on_notebook_switch_page,
            "on_make_local_clicked"  : self.on_make_local_clicked,
            "on_delete_attr_clicked" : self.on_delete_attr_clicked,
            "on_update_attr_clicked" : self.on_update_attr_clicked,
            "on_help_clicked" : self.on_help_clicked,
            })
        self.redraw_attr_list()
        self.display_refs()

    def on_up_clicked(self,obj):
        store,iter = self.atree.get_selected()
        if iter:
            row = self.atree.get_row(iter)
            if row != 0:
                self.atree.select_row(row-1)

    def on_down_clicked(self,obj):
        model,iter = self.atree.get_selected()
        if not iter:
            return
        row = self.atree.get_row(iter)
        self.atree.select_row(row+1)

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
        self.atree.clear()
        self.amap = {}
        for attr in self.alist:
            d = [attr.getType(),attr.getValue()]
            iter = self.atree.add(d,attr)
            self.amap[str(attr)] = iter
        if self.alist:
            Utils.bold_label(self.attr_label)
        else:
            Utils.unbold_label(self.attr_label)

    def button_press(self,obj):
        store,iter = self.refmodel.selection.get_selected()
        if not iter:
            return
            
    def display_refs(self):
        if self.refs == 1:
            return
        self.refs = 1

        titles = [(_('Type'),0,150),(_('ID'),1,75),(_('Value'),2,100)]
        self.refmodel = ListModel.ListModel(self.change_dialog.get_widget("refinfo"),
                                            titles,event_func=self.button_press)
        any = 0
        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    self.refmodel.add([_("Person"),p.getId(),GrampsCfg.nameof(p)])
                    any = 1
        for p in self.db.getFamilyMap().values():
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    self.refmodel.add([_("Family"),p.getId(),Utils.family_name(p)])
                    any = 1
        for key in self.db.getSourceKeys():
            p = self.db.getSource(key)
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    self.refmodel.add([_("Source"),p.getId(),p.getTitle()])
                    any = 1
        for key in self.db.getPlaceKeys():
            p = self.db.getPlace(key)
            for o in p.getPhotoList():
                if o.getReference() == self.object:
                    self.refmodel.add([_("Place"),p.getId(),p.get_title()])
                    any = 1
        if any:
            Utils.bold_label(self.refs_label)
        else:
            Utils.unbold_label(self.refs_label)
        
    def on_notebook_switch_page(self,obj,junk,page):
        if page == 3:
            self.display_refs()
        t = self.notes.get_buffer()
        text = unicode(t.get_text(t.get_start_iter(),t.get_end_iter(),gtk.FALSE))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)
            
    def on_apply_clicked(self, obj):
        t = self.notes.get_buffer()
        text = unicode(t.get_text(t.get_start_iter(),t.get_end_iter(),gtk.FALSE))
        desc = unicode(self.descr_window.get_text())
        note = self.object.getNote()
        format = self.preform.get_active()
        if text != note or desc != self.object.getDescription():
            self.object.setNote(text)
            self.object.setDescription(desc)
            Utils.modified()
        if format != self.object.getNoteFormat():
            self.object.setNoteFormat(format)
            Utils.modified()
        if self.lists_changed:
            self.object.setAttributeList(self.alist)
            Utils.modified()
        if self.update != None:
            self.update()

    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')
        
    def on_ok_clicked(self, obj):
        self.on_apply_clicked(obj)
        Utils.destroy_passed_object(obj)

    def on_attr_list_select_row(self,obj):
        store,iter = self.atree.get_selected()
        if iter:
            attr = self.atree.get_object(iter)

            self.attr_type.set_label(attr.getType())
            self.attr_value.set_text(attr.getValue())
        else:
            self.attr_type.set_label('')
            self.attr_value.set_text('')

    def attr_callback(self,attr):
        self.redraw_attr_list()
        self.atree.select_iter(self.amap[str(attr)])

    def on_update_attr_clicked(self,obj):
        import AttrEdit

        store,iter = self.atree.get_selected()
        if iter:
            attr = self.atree.get_object(iter)
            AttrEdit.AttributeEditor(self,attr,"Media Object",
                                     Plugins.get_image_attributes(),
                                     self.attr_callback)

    def on_delete_attr_clicked(self,obj):
        if Utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        AttrEdit.AttributeEditor(self,None,"Media Object",
                                 Plugins.get_image_attributes(),
                                 self.attr_callback)

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
