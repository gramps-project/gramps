#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2005  Donald N. Allingham
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
import os
import gc
from gettext import gettext as _

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
import GrampsKeys
import const
import ImageSelect
import ImgManip
import RelImage
import DisplayModels
import GrampsMime
from QuestionDialog import QuestionDialog, ErrorDialog, WarningDialog

column_names = [
    _('Title'),
    _('ID'),
    _('Type'),
    _('Path'),
    _('Last Changed'),
    _('Date'),
    ]

_HANDLE_COL = len(column_names)
#-------------------------------------------------------------------------
#
# MediaView
#
#-------------------------------------------------------------------------
class MediaView:
    def __init__(self,parent,db,glade,update):
        self.parent = parent
        self.parent.connect('database-changed',self.change_db)
        self.db = db
        self.list = glade.get_widget("media_list")
        self.mid = glade.get_widget("mid")
        self.mtype = glade.get_widget("mtype")
        self.mdesc = glade.get_widget("mdesc")
        self.mpath = glade.get_widget("mpath")
        self.mdetails = glade.get_widget("mdetails")
        self.preview = glade.get_widget("preview")
        self.topWindow = glade.get_widget("gramps")
        self.renderer = gtk.CellRendererText()
        self.model = DisplayModels.MediaModel(self.db)
        self.sort_col = 0

        self.selection = self.list.get_selection()
        self.list.set_model(self.model)

        DND_TARGETS = [
            ('mediaobj', 0, 0),
            ('STRING', 0, 0),
            ('text/plain',0,0),
            ('text/uri-list',0,2),
            ('application/x-rootwin-drop',0,1)]

        self.list.enable_model_drag_source(
            gtk.gdk.BUTTON1_MASK,
            DND_TARGETS,
            gtk.gdk.ACTION_DEFAULT|gtk.gdk.ACTION_COPY
            )

        self.list.drag_source_set(
            gtk.gdk.BUTTON1_MASK|gtk.gdk.BUTTON3_MASK,
            DND_TARGETS,
            gtk.gdk.ACTION_COPY
            )

        self.list.enable_model_drag_dest(
            DND_TARGETS,
            gtk.gdk.ACTION_DEFAULT
            )
        self.list.drag_dest_set(
            gtk.DEST_DEFAULT_ALL,
            DND_TARGETS,
            gtk.gdk.ACTION_COPY|gtk.gdk.ACTION_MOVE
            )
        if not self.db.readonly:
            self.list.connect("drag-data-received", self.on_drag_data_received)
        self.list.connect("drag-data-get", self.on_drag_data_get)
        self.list.connect("drag-begin", self.on_drag_begin)
        self.list.connect("drag-drop", self.on_drag_drop)

        self.list.connect('button-press-event',self.on_button_press_event)
        self.list.connect('key-press-event',self.key_press)

        self.selection.connect('changed',self.on_select_row)
        self.update = update
        self.columns = []
        self.build_columns()
        self.build_tree()

    def column_clicked(self,obj,data):
        if self.sort_col != data:
            order = gtk.SORT_ASCENDING
        else:
            if (self.columns[data].get_sort_order() == gtk.SORT_DESCENDING
                or self.columns[data].get_sort_indicator() == False):
                order = gtk.SORT_ASCENDING
            else:
                order = gtk.SORT_DESCENDING
        self.sort_col = data
        handle = self.first_selected()
        self.model = DisplayModels.MediaModel(self.parent.db,
                                              self.sort_col,order)
        self.list.set_model(self.model)

        colmap = self.parent.db.get_place_column_order()
        
        if handle:
            path = self.model.on_get_path(handle)
            self.selection.select_path(path)
            self.list.scroll_to_cell(path,None,1,0.5,0)
        for i in range(0,len(self.columns)):
            self.columns[i].set_sort_indicator(i==colmap[data][1]-1)
        self.columns[self.sort_col].set_sort_order(order)

    def first_selected(self):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        if mlist:
            return mlist[0]
        else:
            return None

    def blist(self,store,path,iter,list):
        handle = store.get_value(iter,_HANDLE_COL)
        list.append(handle)

    def build_columns(self):
        for column in self.columns:
            self.list.remove_column(column)
            
        column = gtk.TreeViewColumn(_('Title'), self.renderer,text=0)
        column.set_resizable(True)
        column.connect('clicked',self.column_clicked,0)
        column.set_clickable(True)
        column.set_min_width(225)
        self.list.append_column(column)
        self.columns = [column]

        index = 1
        for pair in self.parent.db.get_media_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = gtk.TreeViewColumn(name, self.renderer, text=pair[1])
            column.set_resizable(True)
            column.set_min_width(75)
            column.set_clickable(True)
            column.connect('clicked',self.column_clicked,index)
            self.columns.append(column)
            self.list.append_column(column)
            index += 1

    def media_add(self,handle_list):
        for handle in handle_list:
            self.model.add_row_by_handle(handle)

    def media_update(self,handle_list):
        for handle in handle_list:
            self.model.update_row_by_handle(handle)
        self.on_select_row()

    def media_delete(self,handle_list):
        for handle in handle_list:
            self.model.delete_row_by_handle(handle)

    def change_db(self,db):
        db.connect('media-add',    self.media_add)
        db.connect('media-update', self.media_update)
        db.connect('media-delete', self.media_delete)
        db.connect('media-rebuild',self.build_tree)

        self.db = db
        self.build_columns()
        self.build_tree()

    def build_tree(self):
        self.model = DisplayModels.MediaModel(self.parent.db)
        self.list.set_model(self.model)
        self.selection = self.list.get_selection()

    def on_select_row(self,obj=None):
        fexists = 1

        store,node = self.selection.get_selected()
        if not node:
            self.preview.set_from_pixbuf(None)
            self.mid.set_text('')
            self.mdesc.set_text('')
            self.mpath.set_text('')
            self.mdetails.set_text('')
            self.mtype.set_text('')
        else:
            handle = store.get_value(node,_HANDLE_COL)
        
            mobj = self.db.get_object_from_handle(handle)
            mtype = mobj.get_mime_type()
            path = mobj.get_path()
            if mtype:
                type_name = Utils.get_mime_description(mtype)
                image = ImgManip.get_thumbnail_image(path,mtype)
            else:
                image = Utils.find_mime_type_pixbuf('text/plain')
                type_name = _('Note')
            self.preview.set_from_pixbuf(image)
            del image
            gc.collect()

            self.mid.set_text(mobj.get_gramps_id())
            if type_name:
                self.mtype.set_text(type_name)
            else:
                self.mtype.set_text(_('unknown'))
            self.mdesc.set_text(mobj.get_description())
            if type_name == _('Note'):
                self.mpath.set_text('')
            elif len(path) == 0 or fexists == 0:
                self.mpath.set_text(_("The file no longer exists"))
            else:
                self.mpath.set_text(path)
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
            handle = store.get_value(node,_HANDLE_COL)
            obj = self.db.get_object_from_handle(handle)
            self.obj = obj
            mime_type = obj.get_mime_type()
            
            Utils.add_menuitem(menu,_("View in the default viewer"),None,
                               self.popup_view_photo)
            
            if mime_type and mime_type[0:5] == "image":
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
    
    def popup_change_description(self, obj):
        ImageSelect.GlobalMediaProperties(self.db,self.obj,self,self.topWindow)

    def on_add_clicked(self,obj):
        """Add a new media object to the media list"""
        import AddMedia
        am = AddMedia.AddMediaObject(self.db)
        am.run()

    def on_edit_clicked(self,obj):
        """Edit the properties of an existing media object in the media list"""

        list_store, node = self.selection.get_selected()
        if node:
            handle = list_store.get_value(node,_HANDLE_COL)
            obj = self.db.get_object_from_handle(handle)
            if obj.get_mime_type():
                ImageSelect.GlobalMediaProperties(self.db,obj,self,self.topWindow)
            else:
                import NoteEdit
                NoteEdit.NoteEditor(obj,self.parent,self.topWindow,
                                    self.note_callback)

    def note_callback(self,data):
        trans = self.db.transaction_begin()
        self.db.commit_media_object(data,trans)
        self.db.transaction_commit(trans,_("Edit Media Object"))

    def on_delete_clicked(self,obj):
        store,node = self.selection.get_selected()
        if not node:
            return

        handle = store.get_value(node,_HANDLE_COL)
        the_lists = Utils.get_media_referents(handle,self.db)

        ans = ImageSelect.DeleteMediaQuery(handle,self.db,the_lists)
        if filter(None,the_lists): # quick test for non-emptiness
            msg = _('This media object is currently being used. '
                    'If you delete this object, it will be removed from '
                    'the database and from all records that reference it.')
        else:
            msg = _('Deleting media object will remove it from the database.')

        msg = "%s %s" % (msg,Utils.data_recover_msg)
        QuestionDialog(_('Delete Media Object?'),msg,
                      _('_Delete Media Object'),ans.query_response)

    def on_drag_drop(self, tree, context, x, y, time):
        self.list.emit_stop_by_name('drag-drop')
        return 1

    def on_drag_begin(self,obj,context):
        store,node = self.selection.get_selected()
        if not node:
            return
        if (const.dnd_images):
            handle = store.get_value(node,_HANDLE_COL)
            obj = self.db.get_object_from_handle(handle)
            if obj.get_path():
                image = ImgManip.get_thumbnail_image(obj.get_path(),
                                                     obj.get_mime_type())
                context.set_icon_pixbuf(image,0,0)

    def on_drag_data_get(self, w, context, selection_data, info, time):
        if info == 1:
            return

        store,node = self.selection.get_selected()
        if not node:
            return
        handle = store.get_value(node,_HANDLE_COL)
        selection_data.set(selection_data.target, 8, handle)

    def on_drag_data_received(self,w, context, x, y, data, info, time):
        import urlparse

        self.list.emit_stop_by_name('drag-data-received')
        if data and data.format == 8:
            d = data.data.replace('\0',' ').strip()
            protocol,site,name, j,k,l = urlparse.urlparse(d)
            if protocol == "file":
                mime = GrampsMime.get_type(name)
                if not GrampsMime.is_valid_type(mime):
                    ErrorDialog(_('Invalid file type'),
                                _('An object of type %s cannot be added '
                                  'to a gallery') % mime)
                    return
                photo = RelLib.MediaObject()
                photo.set_path(name)
                photo.set_mime_type(mime)
                description = os.path.basename(name)
                photo.set_description(description)
                trans = self.db.transaction_begin()
                self.db.add_object(photo,trans)

                self.db.commit_media_object(photo,trans)
                self.db.transaction_commit(trans,_("Add Media Object"))
                self.build_tree()
                if GrampsKeys.get_media_global():
                    ImageSelect.GlobalMediaProperties(self.db,photo,
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
                if not GrampsMime.is_valid_type(mime):
                    ErrorDialog(_('Invalid file type'),
                                _('An object of type %s cannot be added '
                                  'to a gallery') % mtype)
                    return
                photo = RelLib.MediaObject()
                photo.set_mime_type(mime)
                photo.set_description(d)
                photo.set_path(tfile)
                trans = self.db.transaction_begin()
                self.db.add_object(photo,trans)
                oref = RelLib.MediaRef()
                oref.set_reference_handle(photo.get_handle())

                self.db.commit_media_object(photo,trans)
                self.db.transaction_commit(trans,_("Add Media Object"))
                
                if GrampsKeys.get_media_global():
                    ImageSelect.GlobalMediaProperties(self.db,photo,
                                                self,self.topWindow)
