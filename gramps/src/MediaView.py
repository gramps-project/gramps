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
import string
import ImageSelect

from RelLib import *
import utils
import os
import Config

from intl import gettext
_ = gettext

class MediaView:
    def __init__(self,db,glade,update):
        self.db = db
        self.media_list  = glade.get_widget("media_list")
        self.mid         = glade.get_widget("mid")
        self.mtype       = glade.get_widget("mtype")
        self.mdesc       = glade.get_widget("mdesc")
        self.mpath       = glade.get_widget("mpath")
        self.mdetails    = glade.get_widget("mdetails")
        self.mid_arrow   = glade.get_widget("mid_arrow")
        self.mdescr_arrow= glade.get_widget("mdescr_arrow")
        self.mtype_arrow = glade.get_widget("mtype_arrow")
        self.mpath_arrow = glade.get_widget("mpath_arrow")
        self.preview     = glade.get_widget("preview")

        self.sort_arrow = [self.mdescr_arrow, self.mid_arrow, 
                           self.mtype_arrow, self.mpath_arrow]
        self.sort_map   = [5,1,2,3,-1]
        self.media_list.connect('click-column',self.click_column)

        self.mid_arrow.hide()
        self.mtype_arrow.hide()
        self.mpath_arrow.hide()
        
        t = [ ('STRING', 0, 0),
              ('text/plain',0,0),
              ('text/uri-list',0,2),
              ('application/x-rootwin-drop',0,1)]

        self.media_list.drag_source_set(GDK.BUTTON1_MASK|GDK.BUTTON3_MASK,
                                        t,
                                        GDK.ACTION_COPY)
        self.media_list.drag_dest_set(GTK.DEST_DEFAULT_ALL,
                                      t,
                                      GDK.ACTION_COPY|GDK.ACTION_MOVE)

        self.update = update
        self.media_list.set_column_visibility(4,Config.show_detail)
        self.media_list.set_column_visibility(5,0)
        self.media_list.connect('button-press-event',self.on_button_press_event)

        # Restore the previous sort column
        
        self.sort_col,self.sort_dir = Config.get_sort_cols("media",0,GTK.SORT_ASCENDING)
        self.media_list.set_sort_type(self.sort_dir)
        self.media_list.set_sort_column(self.sort_map[self.sort_col])
        self.set_arrow(self.sort_col)

    def set_arrow(self,column):
        for a in self.sort_arrow:
            a.hide()

        a = self.sort_arrow[column]
        a.show()
        if self.sort_dir == GTK.SORT_ASCENDING:
            a.set(GTK.ARROW_DOWN,2)
        else:
            a.set(GTK.ARROW_UP,2)
        
    def click_column(self,obj,column):

        new_col = self.sort_map[column]
        if new_col == -1:
            return

        data = None
        if len(obj.selection) == 1:
            data = obj.get_row_data(obj.selection[0])
        
        obj.freeze()
        if new_col == self.sort_col:
            if self.sort_dir == GTK.SORT_ASCENDING:
                self.sort_dir = GTK.SORT_DESCENDING
            else:
                self.sort_dir = GTK.SORT_ASCENDING
        else:
            self.sort_dir = GTK.SORT_ASCENDING

        self.set_arrow(column)
        
        obj.set_sort_type(self.sort_dir)
        obj.set_sort_column(new_col)
        self.sort_col = column
        Config.save_sort_cols("media",self.sort_col,self.sort_dir)
        obj.sort()
        if data:
            row = obj.find_row_from_data(data)
            obj.moveto(row)
        obj.thaw()

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
        self.mdetails.set_text(utils.get_detail_text(mobj,0))

    def on_button_press_event(self,obj,event):
        if event.button != 1 or event.type != GDK._2BUTTON_PRESS:
            return
        if len(self.media_list.selection) <= 0:
            return
        object = self.media_list.get_row_data(self.media_list.selection[0])
        ImageSelect.GlobalMediaProperties(self.db,object,self.load_media)

    def load_media(self):

        if len(self.media_list.selection) == 0:
            current_row = 0
        else:
            current_row = self.media_list.selection[0]

        self.media_list.freeze()
        self.media_list.clear()
        self.media_list.set_column_visibility(1,Config.id_visible)
        self.media_list.set_column_visibility(4,Config.show_detail)
        
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
            details = utils.get_detail_flags(src,0)
            stitle = string.upper(title)
            self.media_list.append([title,id,type,path,details,stitle])
            self.media_list.set_row_data(index,src)
            index = index + 1

        self.media_list.sort()

        if index > 0:
            self.media_list.select_row(current_row,0)
            self.media_list.moveto(current_row)
            self.preview.show()
        else:
            self.mid.set_text("")
            self.mtype.set_text("")
            self.mdesc.set_text("")
            self.mpath.set_text("")
            self.mdetails.set_text("")
            self.preview.hide()

        if current_row < self.media_list.rows:
            self.media_list.moveto(current_row)
        else:
            self.media_list.moveto(0)
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

    
