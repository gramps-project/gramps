#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2004  Donald N. Allingham
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
# standard python modules
#
#-------------------------------------------------------------------------
import string
import os

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import Utils
import GrampsGconfKeys
import const
import ImageSelect
import RelImage
import DisplayModels
import GrampsMime

from QuestionDialog import QuestionDialog, ErrorDialog, WarningDialog

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

column_names = [
    _('Title'),
    _('ID'),
    _('Type'),
    _('Path'),
    _('Last Changed'),
    ]

#-------------------------------------------------------------------------
#
# MediaView
#
#-------------------------------------------------------------------------
class MediaView:
    def __init__(self,parent,db,glade,update):
        self.parent = parent
        self.db = db
        self.list = glade.get_widget("media_list")
        #self.list.set_property('fixed-height-mode',True)
        self.mid = glade.get_widget("mid")
        self.mtype = glade.get_widget("mtype")
        self.mdesc = glade.get_widget("mdesc")
        self.mpath = glade.get_widget("mpath")
        self.mdetails = glade.get_widget("mdetails")
        self.preview = glade.get_widget("preview")
        self.topWindow = glade.get_widget("gramps")
        self.renderer = gtk.CellRendererText()

        # self.model = gtk.TreeModelSort(DisplayModels.MediaModel(self.db))
        self.model = DisplayModels.MediaModel(self.db)

        self.selection = self.list.get_selection()

        self.list.set_model(self.model)

        t = [ ('STRING', 0, 0),
              ('text/plain',0,0),
              ('text/uri-list',0,2),
              ('application/x-rootwin-drop',0,1)]

        self.list.drag_source_set(gtk.gdk.BUTTON1_MASK|gtk.gdk.BUTTON3_MASK,
                                  t,gtk.gdk.ACTION_COPY)
        self.list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                t,gtk.gdk.ACTION_COPY|gtk.gdk.ACTION_MOVE)


        self.list.connect("drag_data_received", self.on_drag_data_received)
        self.list.connect("drag_data_get", self.on_drag_data_get)
        self.list.connect("drag_begin", self.on_drag_begin)

        self.update = update
        self.list.connect('button-press-event',self.on_button_press_event)
        self.list.connect('key-press-event',self.key_press)
        self.selection.connect('changed',self.on_select_row)
        self.columns = []
        self.build_columns()
        self.build_tree()

    def build_columns(self):
        for column in self.columns:
            self.list.remove_column(column)
            
        column = gtk.TreeViewColumn(_('Title'), self.renderer,text=0)
        column.set_resizable(gtk.TRUE)

        column.set_min_width(225)
        self.list.append_column(column)
        self.columns = [column]

        index = 1
        for pair in self.parent.db.get_media_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = gtk.TreeViewColumn(name, self.renderer, text=pair[1])
            column.set_resizable(gtk.TRUE)
            column.set_min_width(75)
            self.columns.append(column)
            self.list.append_column(column)
            index += 1

    def change_db(self,db):
        self.db = db
        self.build_columns()
        self.build_tree()

    def build_tree(self):
        #self.model = gtk.TreeModelSort(DisplayModels.MediaModel(self.parent.db))
        self.model = DisplayModels.MediaModel(self.parent.db)
            
        self.list.set_model(self.model)
        self.selection = self.list.get_selection()

    def on_select_row(self,obj):
        fexists = 1

        store,node = self.selection.get_selected()
        if not node:
            return

        handle = store.get_value(node,5)
        
        mobj = self.db.get_object_from_handle(handle)
        mtype = mobj.get_mime_type()
        path = mobj.get_path()
        type_name = Utils.get_mime_description(mtype)
        image = self.db.get_thumbnail_image(mobj.get_handle())
        if image != None:
            self.preview.set_from_pixbuf(image)
        else:
            icon_image = gtk.gdk.pixbuf_new_from_file(Utils.find_icon(mtype))
            self.preview.set_from_pixbuf(icon_image)
        
        self.mid.set_text(mobj.get_gramps_id())
        self.mtype.set_text(type_name)
        self.mdesc.set_text(mobj.get_description())
        if len(path) == 0 or fexists == 0:
            self.mpath.set_text(_("The file no longer exists"))
        elif path[0] == "/":
            self.mpath.set_text(path)
        else:
            self.mpath.set_text(_("<local>"))
        self.mdetails.set_text(Utils.get_detail_text(mobj,0))

    def on_button_press_event(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_edit_clicked(obj)
            return 1
        elif event.button == 3:
            self.build_context_menu(event)
            return 1
        return 0

    def key_press(self,obj,event):
        if event.keyval == gtk.gdk.keyval_from_name("Return") \
                                        and not event.state:
            self.on_edit_clicked(obj)
            return 1
        return 0

    def build_context_menu(self,event):
        menu = gtk.Menu()
        menu.set_title(_("Media Object"))

        store,node = self.selection.get_selected()
        if node:
            handle = store.get_value(node,5)
            obj = self.db.get_object_from_handle(handle)
            self.obj = obj
            mime_type = obj.get_mime_type()
            
            Utils.add_menuitem(menu,_("View in the default viewer"),None,
                               self.popup_view_photo)
            
            if mime_type[0:5] == "image":
                Utils.add_menuitem(menu,_("Edit with the GIMP"),
                                   None,self.popup_edit_photo)
            item = gtk.MenuItem()
            item.show()
            menu.append(item)
            sel_sensitivity = 1
        else:
            sel_sensitivity = 0
        
        entries = [
            (gtk.STOCK_ADD, self.on_add_clicked,1),
            (gtk.STOCK_REMOVE, self.on_delete_clicked,sel_sensitivity),
            (_("Edit properties"), self.on_edit_clicked,sel_sensitivity),
        ]

        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def popup_view_photo(self, obj):
        Utils.view_photo(self.obj)
    
    def popup_edit_photo(self, obj):
        if os.fork() == 0:
            os.execvp(const.editor,[const.editor, self.obj.get_path()])
    
    def popup_convert_to_private(self, obj):
        path = self.db.get_save_path()
        handle = self.obj.get_handle()
        self.db.set_thumbnail_image(handle,path)
        if name:
            self.obj.set_path(name)

    def popup_change_description(self, obj):
        ImageSelect.GlobalMediaProperties(self.db,self.obj,
                                          self.update_display,
                                          self,self.topWindow)

    def on_add_clicked(self,obj):
        """Add a new media object to the media list"""
        import AddMedia
        am = AddMedia.AddMediaObject(self.db,self.add_object)
        am.run()

    def add_object(self,mobj_handle):
        self.model.add_row_by_handle(mobj_handle)

    def update_display(self,mobj):
        self.model.update_row_by_handle(mobj.get_handle())

    def on_edit_clicked(self,obj):
        """Edit the properties of an existing media object in the media list"""

        list_store, node = self.selection.get_selected()
        if node:
            handle = list_store.get_value(node,5)
            obj = self.db.get_object_from_handle(handle)
            ImageSelect.GlobalMediaProperties(self.db,obj,
                                              self.update_display,
                                              self,self.topWindow)

    def on_delete_clicked(self,obj):
        store,node = self.selection.get_selected()
        if not node:
            return

        handle = store.get_value(node,5)
        mobj = self.db.get_object_from_handle(handle)
        if self.is_object_used(mobj):
            ans = ImageSelect.DeleteMediaQuery(mobj,self.db,
                                               self.model.delete_row_by_handle)
            QuestionDialog(_('Delete Media Object?'),
                           _('This media object is currently being used. '
                             'If you delete this object, it will be removed '
                             'from the database and from all records that '
                             'reference it.'),
                           _('_Delete Media Object'),
                           ans.query_response)
        else:
            self.delete_object(mobj)

    def delete_object(self,media_obj):
        trans = self.parent.db.transaction_begin()
        mobj_handle = media_obj.get_handle()
        self.parent.db.remove_object(mobj_handle,trans)
        title_msg = _("Delete Media Object?")
        self.parent.db.transaction_commit(trans,title_msg)
        self.model.delete_row_by_handle(mobj_handle)

    def is_object_used(self,mobj):
        mhandle = mobj.get_handle()
        for family_handle in self.db.get_family_handles(sort_handles=False):
            p = self.db.get_family_from_handle(family_handle)
            for o in p.get_media_list():
                if o.get_reference_handle() == mhandle:
                    return True
        for key in self.db.get_person_handles(sort_handles=False):
            p = self.db.get_person_from_handle(key)
            for o in p.get_media_list():
                if o.get_reference_handle() == mhandle:
                    return True
        for key in self.db.get_source_handles(sort_handles=False):
            p = self.db.get_source_from_handle(key)
            for o in p.get_media_list():
                if o.get_reference_handle() == mhandle:
                    return True
        for key in self.db.get_place_handles(sort_handles=False):
            p = self.db.get_place_from_handle(key)
            for o in p.get_media_list():
                if o.get_reference_handle() == mhandle:
                    return True
        return False

    def on_drag_begin(self,obj,context):
        store,node = self.selection.get_selected()
        if not node:
            return
        if (const.dnd_images):
            handle = store.get_value(node,5)
            obj = self.db.get_object_from_handle(handle)
            image = self.db.get_thumbnail_image(obj.get_handle())
            context.set_icon_pixbuf(image,0,0)

    def on_drag_data_get(self,w, context, selection_data, info, time):
        if info == 1:
            return

        store,node = self.selection.get_selected()
        if not node:
            return
        handle = store.get_value(node,1)
        selection_data.set(selection_data.target, 8, handle)	

    def on_drag_data_received(self,w, context, x, y, data, info, time):
        print "on_drag_data_received"
        import urlparse
        if data and data.format == 8:
            d = string.strip(string.replace(data.data,'\0',' '))
            protocol,site,name, j,k,l = urlparse.urlparse(d)
            if protocol == "file":
                mime = GrampsMime.get_type(name)
                photo = RelLib.MediaObject()
                photo.set_path(name)
                photo.set_mime_type(mime)
                description = os.path.basename(name)
                photo.set_description(description)
                trans = self.db.transaction_begin()
                self.db.add_object(photo,trans)
                if GrampsGconfKeys.get_media_reference() == 0:
                    self.db.set_thumbnail_image(photo.get_handle(),name)

                self.db.commit_media_object(photo,trans)
                self.db.transaction_commit(trans,_("Add Media Object"))
                
                if GrampsGconfKeys.get_media_global():
                    ImageSelect.GlobalMediaProperties(self.db,photo,
                                                      self.update_display,
                                                      self,self.topWindow)
            elif protocol != "":
                import urllib
                u = urllib.URLopener()
                try:
                    tfile,headers = u.retrieve(d)
                except IOError, msg:
                    ErrorDialog(_('Image import failed'),str(msg))
                    return
                mime = GrampsMime.get_type(tfile)
                photo = RelLib.MediaObject()
                photo.set_mime_type(mime)
                photo.set_description(d)
                photo.set_path(tfile)
                trans = self.db.transaction_begin()
                self.db.add_object(photo,trans)
                oref = RelLib.MediaRef()
                oref.set_reference_handle(photo.get_handle())
                try:
                    handle = photo.get_handle()
                    path = self.db.get_save_path()
                    self.db.set_thumbnail_image(handle,path)
                except:
                    photo.set_path(tfile)
                    return

                self.db.commit_media_object(photo,trans)
                self.db.transaction_commit(trans,_("Add Media Object"))
                
                if GrampsGconfKeys.get_media_global():
                    ImageSelect.GlobalMediaProperties(self.db,photo,None,
                                                self,self.topWindow)

    
