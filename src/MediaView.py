#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  Donald N. Allingham
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

import GTK
import GDK
import gnome.ui
import gtk
import string
import ImageSelect

from RelLib import *
import intl
import utils
import const
import os

_ = intl.gettext

class MediaView:
    def __init__(self,db,glade,update):
        self.db = db
        self.media_list = glade.get_widget("media_list")
        self.mid        = glade.get_widget("mid")
        self.mtype      = glade.get_widget("mtype")
        self.mdesc      = glade.get_widget("mdesc")
        self.mpath      = glade.get_widget("mpath")
        self.mdetails   = glade.get_widget("mdetails")
        self.preview    = glade.get_widget("preview")
        
        t = [ ('STRING', 0, 0),
              ('text/plain',0,0),
              ('text/uri-list',0,2),
              ('application/x-rootwin-drop',0,1)]

        self.media_list.drag_source_set(GDK.BUTTON1_MASK|GDK.BUTTON3_MASK,t,GDK.ACTION_COPY)
        self.media_list.drag_dest_set(GTK.DEST_DEFAULT_ALL,t,GDK.ACTION_COPY|GDK.ACTION_MOVE)

        self.update = update

    def on_select_row(self,obj,row,b,c):
        mobj = obj.get_row_data(row)
        type = mobj.getMimeType()
        type_name = utils.get_mime_description(type)
        path = mobj.getPath()
        self.preview.load_file(utils.thumb_path(self.db.getSavePath(),mobj))
        
        self.mid.set_text(mobj.getId())
        self.mtype.set_text(type_name)
        self.mdesc.set_text(mobj.getDescription())
        if path[0] == "/":
            self.mpath.set_text(path)
        else:
            self.mpath.set_text("<local>")
        self.mdetails.set_text("")

    def load_media(self):
        self.media_list.freeze()
        self.media_list.clear()

        if len(self.media_list.selection) == 0:
            current_row = 0
        else:
            current_row = self.media_list.selection[0]

        index = 0
        objects = self.db.getObjectMap().values()

        for src in objects:
            title = src.getDescription()
            id = src.getId()
            type = utils.get_mime_description(src.getMimeType())
            if src.getLocal():
                path = "<local copy>"
            else:
                path = src.getPath()
            self.media_list.append([id,title,type,path,""])
            self.media_list.set_row_data(index,src)
            index = index + 1

        self.media_list.sort()

        if index > 0:
            self.media_list.select_row(current_row,0)
            self.media_list.moveto(current_row)
        else:
            self.mid.set_text("")
            self.mtype.set_text("")
            self.mdesc.set_text("")
            self.mpath.set_text("")
            self.mdetails.set_text("")
            self.preview.load_imlib(const.empty_image)

        self.media_list.thaw()

    def create_add_dialog(self,obj):
        """Add a new media object to the media list"""
        import AddMedia
        AddMedia.AddMediaObject(self.db,self.load_media)

    def on_edit_media_clicked(self,obj):
        """Edit the properties of an existing media object in the media list"""
        if len(self.media_list.selection) <= 0:
            return
        object = self.media_list.get_row_data(self.media_list.selection[0])
        ImageSelect.GlobalMediaProperties(self.db,object,self.load_media)

    def on_delete_media_clicked(self,obj):
        if len(self.media_list.selection) <= 0:
            return
        else:
            index = self.media_list.selection[0]
        mobj = self.media_list.get_row_data(index)
        if self.is_media_object_used(mobj):
            ans = ImageSelect.DeleteMediaQuery(mobj,self.db,self.update)
            msg = _("This media object is currently being used. Delete anyway?")
            gnome.ui.GnomeQuestionDialog(msg,ans.query_response)
        else:
            map = self.db.getObjectMap()
            del map[mobj.getId()]
            utils.modified()
            self.update(0)

    def is_media_object_used(self,mobj):
        for p in self.db.getFamilyMap().values():
            for o in p.getPhotoList():
                if o.getReference() == mobj:
                    return 1
        for p in self.db.getPersonMap().values():
            for o in p.getPhotoList():
                if o.getReference() == mobj:
                    return 1
        for p in self.db.getSourceMap().values():
            for o in p.getPhotoList():
                if o.getReference() == mobj:
                    return 1
        for p in self.db.getPlaceMap().values():
            for o in p.getPhotoList():
                if o.getReference() == mobj:
                    return 1
    
    def on_drag_data_get(self,w, context, selection_data, info, time):
        if info == 1:
            return
        if len(w.selection) > 0:
            row = w.selection[0]
            d = w.get_row_data(row)
            id = d.getId()
            selection_data.set(selection_data.target, 8, id)	

    def on_drag_data_received(self,w, context, x, y, data, info, time):
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
                self.db.addObject(photo)
                utils.modified()
                w.drag_finish(context, 1, 0, time)
                self.load_media()
            else:
                w.drag_finish(context, 0, 0, time)

    
