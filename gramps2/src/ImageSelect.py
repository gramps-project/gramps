#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
import gc
import urlparse
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade

try:
    from gnomecanvas import CanvasGroup, CanvasRect, CanvasPixbuf, CanvasText
except:
    from gnome.canvas import CanvasGroup, CanvasRect, CanvasPixbuf, CanvasText

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsKeys
import NameDisplay
import PluginMgr
import RelLib
import RelImage
import ListModel
import SelectObject
import GrampsMime
import Sources
import DateEdit
import DateHandler
import Date
import ImgManip
import Spell
import GrampsDisplay

from QuestionDialog import ErrorDialog
from DdTargets import DdTargets
from WindowUtils import GladeIf

_IMAGEX = 140
_IMAGEY = 150
_PAD = 5

_last_path = ""
_iconlist_refs = []

_drag_targets = [
    ('STRING', 0, 0),
    ('text/plain',0,0),
    ('text/uri-list',0,2),
    ('application/x-rootwin-drop',0,1)]

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

    def internal_toggled(self, obj):
        self.fname.set_sensitive(not obj.get_active())

    def create_add_dialog(self):
        """Create the gnome dialog for selecting a new photo and entering
        its description.""" 

        if self.path == '':
            return

        self.glade       = gtk.glade.XML(const.imageselFile,"imageSelect","gramps")
        self.window      = self.glade.get_widget("imageSelect")

        self.fname       = self.glade.get_widget("fname")
        self.image       = self.glade.get_widget("image")
        self.internal    = self.glade.get_widget("internal")
        self.internal.connect('toggled',self.internal_toggled)
        self.description = self.glade.get_widget("photoDescription")
        self.temp_name   = ""

        Utils.set_titles(self.window,self.glade.get_widget('title'),
                         _('Select a media object'))
        

        self.gladeif = GladeIf(self.glade)
        self.gladeif.connect('fname', 'update_preview', self.on_name_changed)

        if os.path.isdir(_last_path):
            self.fname.set_current_folder(_last_path)

        if self.parent_window:
            self.window.set_transient_for(self.parent_window)
        self.window.show()
        self.val = self.window.run()
        if self.val == gtk.RESPONSE_OK:
            self.on_savephoto_clicked()
        self.window.destroy()
        gc.collect()

    def on_help_imagesel_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-edit-quick')
        self.val = self.window.run()

    def on_name_changed(self, obj):
        """The filename has changed.  Verify it and load the picture."""
        filename = unicode(self.fname.get_filename())

        basename = os.path.basename(filename)
        (root,ext) = os.path.splitext(basename)
        old_title  = unicode(self.description.get_text())

        if old_title == "" or old_title == self.temp_name:
            self.description.set_text(root)
        self.temp_name = root
        
        filename = Utils.find_file( filename)
        if filename:
            mtype = GrampsMime.get_type(filename)
            if not GrampsMime.is_valid_type(mtype):
                ErrorDialog(_('Invalid file type'),
                            _('An object of type %s cannot be added '
                              'to a gallery') % mtype)
                return
                
            if mtype and mtype.startswith("image"):
                image = RelImage.scale_image(filename,const.thumbScale)
                self.image.set_from_pixbuf(image)
            else:
                i = Utils.find_mime_type_pixbuf(mtype)
                self.image.set_from_pixbuf(i)

    def on_savephoto_clicked(self):
        """Save the photo in the dataobj object.  (Required function)"""
        global _last_path

        filename = self.fname.get_filename()
        _last_path = os.path.dirname(filename)
        
        description = unicode(self.description.get_text())

        internal = self.internal.get_active()

        if not internal:
            if os.path.exists(filename) == 0:
                msgstr = _("Cannot import %s")
                msgstr2 = _("The filename supplied could not be found.")
                ErrorDialog(msgstr % filename, msgstr2)
                return

            already_imported = None

            for o_id in self.db.get_media_object_handles():
                o = self.db.get_object_from_handle(o_id)
                if o.get_path() == filename:
                    already_imported = o
                    break

            if already_imported:
                oref = RelLib.MediaRef()
                oref.set_reference_handle(already_imported.get_handle())
                self.dataobj.add_media_reference(oref)
                self.add_thumbnail(oref)
            else:
                mtype = GrampsMime.get_type(filename)
                if GrampsMime.is_valid_type(mtype):
                    mobj = RelLib.MediaObject()
                    if description == "":
                        description = os.path.basename(filename)
                    mobj.set_description(description)
                    mobj.set_mime_type(mtype)
                    mobj.set_path(filename)
                else:
                    ErrorDialog(_('Invalid file type'),
                                _('An object of type %s cannot be added '
                                  'to a gallery') % mtype)
                    return
        else:
            mobj = RelLib.MediaObject()
            mobj.set_description(description)
            mobj.set_mime_type(None)

        if not already_imported:
            trans = self.db.transaction_begin()
            self.savephoto(mobj,trans)
            self.db.transaction_commit(trans,'Edit Media Objects')
            
        self.parent.lists_changed = 1
        self.load_images()

    def savephoto(self, photo, transaction):
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
    def __init__(self, dataobj, commit, path, icon_list, db, parent, parent_window=None):
        ImageSelect.__init__(self, path, db, parent, parent_window)

        self.commit = commit
        if path:
            icon_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                    [DdTargets.MEDIAOBJ.target()]+_drag_targets,
                                    gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
            icon_list.connect('event',self.item_event)
            if not db.readonly:
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
        self.old_media_list = [RelLib.MediaRef(ref) for ref in dataobj.get_media_list()]

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
        if self.canvas_list:
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
        pass

    def on_drag_begin(self,obj,context):
        if const.dnd_images:
            handle = self.sel_obj.get_reference_handle()
            media_obj = self.db.get_object_from_handle(handle)
            pix = ImgManip.get_thumbnail_image(media_obj.get_path(),
                                               media_obj.get_mime_type())
            context.set_icon_pixbuf(pix,0,0)

    def item_event(self, widget, event=None):

        if self.in_event:
            return False
        
        self.in_event = 1
        if self.button and event.type == gtk.gdk.MOTION_NOTIFY :
            if widget.drag_check_threshold(int(self.remember_x),int(self.remember_y),
                                           int(event.x),int(event.y)):
                self.drag_item = widget.get_item_at(self.remember_x,
                                                    self.remember_y)
                icon_index = self.get_index(widget,event.x,event.y)
                if icon_index == -1:
                    return
                for i in self.dataobj.get_media_list():
                    handle = i.get_reference_handle()
                    m = self.db.get_object_from_handle(handle)

                media_list = self.dataobj.get_media_list()

                if icon_index >= len(media_list):
                    return False
                self.sel_obj = media_list[icon_index]

                handle = self.sel_obj.get_reference_handle()
                media_obj = self.db.get_object_from_handle(handle)
                
                if self.drag_item:
                    widget.drag_begin([DdTargets.MEDIAOBJ.target()]+_drag_targets,
                                      gtk.gdk.ACTION_COPY|gtk.gdk.ACTION_MOVE,
                                      self.button, event)
                    
            self.in_event = 0
            return True

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
                return True

            elif event.button == 3:
                item = widget.get_item_at(event.x,event.y)
                if item:
                    (i,t,b,self.photo,oid) = self.p_map[item]
                    self.show_popup(self.photo,event)
                self.in_event = 0
                return True
        elif event.type == gtk.gdk.BUTTON_RELEASE:
            self.button = 0
        elif event.type == gtk.gdk.MOTION_NOTIFY:
            if event.state & gtk.gdk.BUTTON1_MASK:
                # Get the new position and move by the difference
                new_x = event.x
                new_y = event.y

                self.remember_x = new_x
                self.remember_y = new_y

                self.in_event = 0
                return True
            
        if event.type == gtk.gdk.EXPOSE:
            self.load_images()

        self.in_event = 0
        return False

    def savephoto(self,photo,transaction):
        """Save the photo in the dataobj object.  (Required function)"""
        self.db.add_object(photo,transaction)
        oref = RelLib.MediaRef()
        oref.set_reference_handle(photo.get_handle())
        self.dataobj.add_media_reference(oref)

    def add_thumbnail(self, photo):
        """Scale the image and add it to the IconList."""
        oid = photo.get_reference_handle()
        media_obj = self.db.get_object_from_handle(oid)
        if self.canvas_list.has_key(photo):
            (grp,item,text,x,y) = self.canvas_list[photo]
            if x != self.cx or y != self.cy:
                grp.move(self.cx-x,self.cy-y)
        else:
            description = media_obj.get_description()
            if len(description) > 20:
                description = "%s..." % description[0:20]

            try:
                mtype = media_obj.get_mime_type()
                image = ImgManip.get_thumbnail_image(media_obj.get_path(),mtype)
            except gobject.GError,msg:
                ErrorDialog(str(msg))
                image = gtk.gdk.pixbuf_new_from_file(const.icon)
            except:
                image = gtk.gdk.pixbuf_new_from_file(const.icon)

            x = image.get_width()
            y = image.get_height()

            grp = self.root.add(CanvasGroup,x=self.cx,y=self.cy)

            xloc = (_IMAGEX-x)/2
            yloc = (_IMAGEY-y)/2

            style = self.iconlist.get_style()

            box = grp.add(CanvasRect,x1=0,x2=_IMAGEX,y1=_IMAGEY-20,
                          y2=_IMAGEY, fill_color_gdk=style.bg[gtk.STATE_NORMAL])
            item = grp.add(CanvasPixbuf,
                           pixbuf=image,x=xloc, y=yloc)
            text = grp.add(CanvasText, x=_IMAGEX/2, 
                           anchor=gtk.ANCHOR_CENTER,
                           justification=gtk.JUSTIFY_CENTER,
                           y=_IMAGEY-10, text=description)

            # make sure that the text string doesn't exceed the size of the box

            bnds = text.get_bounds()
            while bnds[0] <0:
                description = description[0:-4] + "..."
                text.set(text=description)
                bnds = text.get_bounds()

            for i in [ item, text, box, grp ] :
                self.p_map[i] = (item,text,box,photo,oid)
                i.show()
            
        self.canvas_list[photo] = (grp,item,text,self.cx,self.cy)

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

        for photo in self.dataobj.get_media_list():
            self.add_thumbnail(photo)

        if self.cy > self.y:
            self.iconlist.set_scroll_region(0,0,self.x,self.cy)
        else:
            self.iconlist.set_scroll_region(0,0,self.x,self.y)
        
        if self.dataobj.get_media_list():
            Utils.bold_label(self.parent.gallery_label)
        else:
            Utils.unbold_label(self.parent.gallery_label)

    def get_index(self,obj,x,y):
        x_offset = int(x)/(_IMAGEX+_PAD)
        y_offset = int(y)/(_IMAGEY+_PAD)
        index = (y_offset*(self.max))+x_offset
        return min(index,len(self.dataobj.get_media_list()))

    def on_photolist_drag_data_received(self,w, context, x, y, data, info, time):
        if data and data.format == 8:
            icon_index = self.get_index(w,x,y)
            d = Utils.fix_encoding(data.data.replace('\0',' ').strip())
            protocol,site,mfile,j,k,l = urlparse.urlparse(d)
            if protocol == "file":
                name = Utils.fix_encoding(mfile)
                mime = GrampsMime.get_type(name)
                if not GrampsMime.is_valid_type(mime):
                    return
                photo = RelLib.MediaObject()
                photo.set_path(name)
                photo.set_mime_type(mime)
                basename = os.path.basename(name)
                (root,ext) = os.path.splitext(basename)
                photo.set_description(root)
                trans = self.db.transaction_begin()
                self.savephoto(photo,trans)
                if GrampsKeys.get_media_reference() == 0:
                    photo.set_path(name)
                self.db.transaction_commit(trans,_("Drag Media Object"))
                self.parent.lists_changed = 1
                if GrampsKeys.get_media_global():
                    GlobalMediaProperties(self.db,photo,
                                                self,self.parent_window)
            elif protocol != "":
                import urllib
                u = urllib.URLopener()
                try:
                    tfile,headers = u.retrieve(d)
                except (IOError,OSError), msg:
                    t = _("Could not import %s") % d
                    ErrorDialog(t,str(msg))
                    return
                tfile = Utils.fix_encoding(tfile)
                mime = GrampsMime.get_type(tfile)
                photo = RelLib.MediaObject()
                photo.set_mime_type(mime)
                photo.set_description(d)
                photo.set_path(tfile)
                trans = self.db.transaction_begin()
                self.db.add_object(photo,trans)
                self.db.transaction_commit(trans,_("Drag Media Object"))
                oref = RelLib.MediaRef()
                oref.set_reference_handle(photo.get_handle())
                self.dataobj.add_media_reference(oref)
# This code seems to be reproducing what is already done.
#                try:
#                    photo.set_path(name)
#                except:
#                    photo.set_path(tfile)
#                    return
                self.add_thumbnail(oref)
                self.parent.lists_changed = 1
                if GrampsKeys.get_media_global():
                    GlobalMediaProperties(self.db,photo,
                                                self,self.parent_window)
            else:
                if self.db.has_object_handle(data.data):
                    icon_index = self.get_index(w,x,y)
                    index = 0
                    for p in self.dataobj.get_media_list():
                        if data.data == p.get_reference_handle():
                            if index == icon_index or icon_index == -1:
                                return
                            else:
                                nl = self.dataobj.get_media_list()
                                item = nl[index]
                                if icon_index == 0:
                                    del nl[index]
                                    nl = [item] + nl
                                else:
                                    del nl[index]
                                    nl = nl[0:icon_index] + [item] + nl[icon_index:]
                                self.dataobj.set_media_list(nl)
                                self.parent.lists_changed = 1
                                self.load_images()
                                return
                        index = index + 1
                    oref = RelLib.MediaRef()
                    oref.set_reference_handle(data.data)
                    self.dataobj.add_media_reference(oref)
                    self.add_thumbnail(oref)
                    self.parent.lists_changed = 1
                    if GrampsKeys.get_media_global():
                        LocalMediaProperties(oref,self.path,self,self.parent_window)
                
    def on_photolist_drag_data_get(self,w, context, selection_data, info, time):
        if info == 1:
            return
        data = self.p_map[self.drag_item]
        selection_data.set(selection_data.target, 8, data[4])
        self.drag_item = None
        
    def on_add_media_clicked(self, obj):
        """User wants to add a new photo.  Create a dialog to find out
        which photo they want."""
        self.create_add_dialog()

    def on_select_media_clicked(self,obj):
        """User wants to add a new object that is already in a database.  
        Create a dialog to find out which object they want."""

        s_o = SelectObject.SelectObject(self.db,_("Select an Object"))
        obj = s_o.run()
        if not obj:
            return
        oref = RelLib.MediaRef()
        oref.set_reference_handle(obj.get_handle())
        self.dataobj.add_media_reference(oref)
        self.add_thumbnail(oref)

        self.parent.lists_changed = 1
        self.load_images()

    def on_delete_media_clicked(self, obj):
        """User wants to delete a new photo. Remove it from the displayed
        thumbnails, and remove it from the dataobj photo list."""

        if self.sel:
            (i,t,b,photo,oid) = self.p_map[self.sel]
            val = self.canvas_list[photo]
            val[0].hide()
            val[1].hide()
            val[2].hide()

            l = self.dataobj.get_media_list()
            l.remove(photo)
            self.dataobj.set_media_list(l)
            self.parent.lists_changed = 1
            self.load_images()

    def on_edit_media_clicked(self, obj):
        """User wants to delete a new photo. Remove it from the displayed
        thumbnails, and remove it from the dataobj photo list."""

        if self.sel:
            (i,t,b,photo,oid) = self.p_map[self.sel]
            base_obj = self.db.get_object_from_handle(photo.get_reference_handle())
            
            if base_obj.get_mime_type():
                LocalMediaProperties(photo,self.path,self,self.parent_window)
            else:
                import NoteEdit
                NoteEdit.NoteEditor(base_obj,self.parent,self.parent_window,
                                    self.note_callback)
        
    def note_callback(self,data):
        trans = self.db.transaction_begin()
        self.db.commit_media_object(data,trans)
        self.db.transaction_commit(trans,_("Edit Media Object"))

    def show_popup(self, photo, event):
        """Look for right-clicks on a picture and create a popup
        menu of the available actions."""
        
        menu = gtk.Menu()
        menu.set_title(_("Media Object"))
        obj = self.db.get_object_from_handle(photo.get_reference_handle())
        mtype = obj.get_mime_type()
        progname = GrampsMime.get_application(mtype)
        
        if progname and len(progname) > 1:
            Utils.add_menuitem(menu,_("Open in %s") % progname[1],
                               photo,self.popup_view_photo)
        if mtype and mtype.startswith("image"):
            Utils.add_menuitem(menu,_("Edit with the GIMP"),
                               photo,self.popup_edit_photo)
        Utils.add_menuitem(menu,_("Edit Object Properties"),photo,
                           self.popup_change_description)
        menu.popup(None,None,None,event.button,event.time)
            
    def popup_view_photo(self, obj):
        """Open this picture in a picture viewer"""
        photo = obj.get_data('o')
        Utils.view_photo(self.db.get_object_from_handle(photo.get_reference_handle()))
    
    def popup_edit_photo(self, obj):
        """Open this picture in a picture editor"""
        photo = obj.get_data('o')
        if os.fork() == 0:
            obj = self.db.get_object_from_handle(photo.get_reference_handle())
            os.execvp(const.editor,[const.editor, obj.get_path()])
    
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

    def __init__(self,photo,path,parent,parent_window=None):
        self.parent = parent
        if photo:
            if self.parent.parent.child_windows.has_key(photo):
                self.parent.parent.child_windows[photo].present(None)
                return
            else:
                self.win_key = photo
        else:
            self.win_key = self
        self.child_windows = {}
        self.photo = photo
        self.db = parent.db
        self.obj = self.db.get_object_from_handle(photo.get_reference_handle())
        self.alist = photo.get_attribute_list()[:]
        self.lists_changed = 0
        
        fname = self.obj.get_path()
        self.change_dialog = gtk.glade.XML(const.imageselFile,
                                           "change_description","gramps")

        title = _('Media Reference Editor')
        self.window = self.change_dialog.get_widget('change_description')
        Utils.set_titles(self.window,
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
        
        self.slist  = self.change_dialog.get_widget("src_list")
        self.sources_label = self.change_dialog.get_widget("source_label")
        if self.obj:
            self.srcreflist = [RelLib.SourceRef(ref)
                               for ref in self.photo.get_source_references()]
        else:
            self.srcreflist = []
    
        self.sourcetab = Sources.SourceTab(self.srcreflist,self,
                                 self.change_dialog,
                                 self.window, self.slist,
                                 self.change_dialog.get_widget('add_src'),
                                 self.change_dialog.get_widget('edit_src'),
                                 self.change_dialog.get_widget('del_src'))

        descr_window.set_text(self.obj.get_description())
        mtype = self.obj.get_mime_type()

        self.pix = ImgManip.get_thumbnail_image(self.obj.get_path(),mtype)
        self.pixmap.set_from_pixbuf(self.pix)

        self.change_dialog.get_widget("private").set_active(photo.get_privacy())
        coord = photo.get_rectangle()
        if coord and type(coord) == tuple:
            self.change_dialog.get_widget("upperx").set_value(coord[0])
            self.change_dialog.get_widget("uppery").set_value(coord[1])
            self.change_dialog.get_widget("lowerx").set_value(coord[2])
            self.change_dialog.get_widget("lowery").set_value(coord[3])
        
        self.change_dialog.get_widget("gid").set_text(self.obj.get_gramps_id())

        self.change_dialog.get_widget("path").set_text(fname)

        mt = Utils.get_mime_description(mtype)
        if mt:
            self.change_dialog.get_widget("type").set_text(mt)
        else:
            self.change_dialog.get_widget("type").set_text("")
        self.notes = self.change_dialog.get_widget("notes")
        self.spell = Spell.Spell(self.notes)
        if self.photo.get_note():
            self.notes.get_buffer().set_text(self.photo.get_note())
            Utils.bold_label(self.notes_label)
            if self.photo.get_note_format() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)

        self.gladeif = GladeIf(self.change_dialog)
        self.gladeif.connect('change_description','delete_event',self.on_delete_event)
        self.gladeif.connect('button84','clicked',self.close)
        self.gladeif.connect('button82','clicked',self.on_ok_clicked)
        self.gladeif.connect('button104','clicked',self.on_help_clicked)
        self.gladeif.connect('notebook1','switch_page',self.on_notebook_switch_page)
        self.gladeif.connect('button86','clicked',self.on_add_attr_clicked)
        self.gladeif.connect('button100','clicked',self.on_update_attr_clicked)
        self.gladeif.connect('button88','clicked',self.on_delete_attr_clicked)
            
        media_obj = self.db.get_object_from_handle(self.photo.get_reference_handle())
        gnote = self.change_dialog.get_widget('global_notes')
        spell = Spell.Spell(gnote)
        global_note = gnote.get_buffer()
        global_note.insert_at_cursor(media_obj.get_note())
        
        self.redraw_attr_list()
        if parent_window:
            self.window.set_transient_for(parent_window)
        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.gladeif.close()
        self.close_child_windows()
        self.remove_itself_from_menu()
        gc.collect()

    def close(self,obj=None):
        self.gladeif.close()
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.window.destroy()
        gc.collect()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.parent.child_windows[self.win_key] = self
        label = _('Media Reference')
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Reference Editor'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.parent.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def redraw_attr_list(self):
        self.atree.clear()
        self.amap = {}
        for attr in self.alist:
            d = [attr.get_type(),attr.get_value()]
            node = self.atree.add(d,attr)
            self.amap[str(attr)] = node
        if self.alist:
            Utils.bold_label(self.attr_label)
        else:
            Utils.unbold_label(self.attr_label)
        
    def on_notebook_switch_page(self,obj,junk,page):
        t = self.notes.get_buffer()
        text = unicode(t.get_text(t.get_start_iter(),t.get_end_iter(),False))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)
            
    def on_apply_clicked(self):
        priv = self.change_dialog.get_widget("private").get_active()

        coord = (
            self.change_dialog.get_widget("upperx").get_value_as_int(),
            self.change_dialog.get_widget("uppery").get_value_as_int(),
            self.change_dialog.get_widget("lowerx").get_value_as_int(),
            self.change_dialog.get_widget("lowery").get_value_as_int(),
            )
        if (coord[0] == None and coord[1] == None
            and coord[2] == None and coord[3] == None):
            coord = None

        t = self.notes.get_buffer()
        text = unicode(t.get_text(t.get_start_iter(),t.get_end_iter(),False))
        note = self.photo.get_note()
        format = self.preform.get_active()
        if text != note or priv != self.photo.get_privacy() \
               or coord != self.photo.get_rectangle() \
               or format != self.photo.get_note_format():
            self.photo.set_rectangle(coord)
            self.photo.set_note(text)
            self.photo.set_privacy(priv)
            self.photo.set_note_format(format)
            self.parent.lists_changed = 1
            self.parent.parent.lists_changed = 1
        if self.lists_changed:
            self.photo.set_attribute_list(self.alist)
            self.photo.set_source_reference_list(self.srcreflist)
            self.parent.lists_changed = 1
            self.parent.parent.lists_changed = 1

        trans = self.db.transaction_begin()
        self.db.commit_media_object(self.obj,trans)
        self.db.transaction_commit(trans,_("Edit Media Object"))

    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-edit-complete')
        
    def on_ok_clicked(self,obj):
        self.on_apply_clicked()
        self.close(obj)
        
    def on_attr_list_select_row(self,obj):
        store,node = self.atree.get_selected()
        if node:
            attr = self.atree.get_object(node)

            self.attr_type.set_label(attr.get_type())
            self.attr_value.set_text(attr.get_value())
        else:
            self.attr_type.set_label('')
            self.attr_value.set_text('')

    def attr_callback(self,attr):
        self.redraw_attr_list()
        self.atree.select_iter(self.amap[str(attr)])
        
    def on_update_attr_clicked(self,obj):
        import AttrEdit

        store,node = self.atree.get_selected()
        if node:
            attr = self.atree.get_object(node)
            AttrEdit.AttributeEditor(self,attr,"Media Object",
                                     PluginMgr.get_image_attributes(),
                                     self.attr_callback)

    def on_delete_attr_clicked(self,obj):
        if Utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        AttrEdit.AttributeEditor(self,None,"Media Object",
                                 PluginMgr.get_image_attributes(),
                                 self.attr_callback)

#-------------------------------------------------------------------------
#
# GlobalMediaProperties
#
#-------------------------------------------------------------------------
class GlobalMediaProperties:

    def __init__(self,db,obj,parent,parent_window=None):
        self.parent = parent
        self.dp = DateHandler.parser
        self.dd = DateHandler.displayer
        if obj:
            if self.parent.parent.child_windows.has_key(obj.get_handle()):
                self.parent.parent.child_windows[obj.get_handle()].present(None)
                return
            else:
                self.win_key = obj.get_handle()
        else:
            self.win_key = self
        self.pdmap = {}
        self.child_windows = {}
        self.obj = obj
        self.lists_changed = 0
        self.db = db
        self.idle = None
        if obj:
            self.date_object = Date.Date(self.obj.get_date_object())
            self.alist = self.obj.get_attribute_list()[:]
            self.refs = 0
        else:
            self.date_object = Date.Date()
            self.alist = []
            self.refs = 1
            
        self.path = self.db.get_save_path()
        self.change_dialog = gtk.glade.XML(const.imageselFile,
                                           "change_global","gramps")
        self.gladeif = GladeIf(self.change_dialog)

        mode = not self.db.readonly
        
        title = _('Media Properties Editor')

        self.window = self.change_dialog.get_widget('change_global')
        self.date_entry = self.change_dialog.get_widget('date')
        self.date_entry.set_editable(mode)
        
        if self.obj:
            self.date_entry.set_text(self.dd.display(self.date_object))
        
        Utils.set_titles(self.window,
                         self.change_dialog.get_widget('title'),title)
        
        self.descr_window = self.change_dialog.get_widget("description")
        self.descr_window.set_editable(mode)
        
        self.notes = self.change_dialog.get_widget("notes")
        self.notes.set_editable(mode)
        self.spell = Spell.Spell(self.notes)
        
        self.date_edit = self.change_dialog.get_widget("date_edit")
        self.date_edit.set_sensitive(mode)
        
        self.date_check = DateEdit.DateEdit(
            self.date_object, self.date_entry,
            self.date_edit, self.window)
        
        self.pixmap = self.change_dialog.get_widget("pixmap")
        self.attr_type = self.change_dialog.get_widget("attr_type")
        self.attr_value = self.change_dialog.get_widget("attr_value")
        self.attr_details = self.change_dialog.get_widget("attr_details")

        self.attr_list = self.change_dialog.get_widget("attr_list")

        self.attr_label = self.change_dialog.get_widget("attrGlobal")
        self.notes_label = self.change_dialog.get_widget("notesGlobal")
        self.refs_label = self.change_dialog.get_widget("refsGlobal")
        self.flowed = self.change_dialog.get_widget("global_flowed")
        self.flowed.set_sensitive(mode)
        self.preform = self.change_dialog.get_widget("global_preform")
        self.preform.set_sensitive(mode)

        titles = [(_('Attribute'),0,150),(_('Value'),1,100)]

        self.atree = ListModel.ListModel(self.attr_list,titles,
                                         self.on_attr_list_select_row,
                                         self.on_update_attr_clicked)
        
        self.slist  = self.change_dialog.get_widget("src_list")
        self.sources_label = self.change_dialog.get_widget("sourcesGlobal")
        if self.obj:
            self.srcreflist = [RelLib.SourceRef(ref)
                               for ref in self.obj.get_source_references()]
        else:
            self.srcreflist = []
    
        self.sourcetab = Sources.SourceTab(
            self.srcreflist,self,
            self.change_dialog,
            self.window, self.slist,
            self.change_dialog.get_widget('gl_add_src'),
            self.change_dialog.get_widget('gl_edit_src'),
            self.change_dialog.get_widget('gl_del_src'))
        
        self.descr_window.set_text(self.obj.get_description())
        mtype = self.obj.get_mime_type()
        if mtype:
            pb = ImgManip.get_thumbnail_image(self.obj.get_path(),mtype)
            self.pixmap.set_from_pixbuf(pb)
            descr = Utils.get_mime_description(mtype)
            if descr:
                self.change_dialog.get_widget("type").set_text(descr)
        else:
            self.change_dialog.get_widget("type").set_text(_('Note'))
            self.pixmap.hide()

        self.change_dialog.get_widget("gid").set_text(self.obj.get_gramps_id())

        self.update_info()
        
        if self.obj.get_note():
            self.notes.get_buffer().set_text(self.obj.get_note())
            Utils.bold_label(self.notes_label)
            if self.obj.get_note_format() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)

        self.gladeif.connect('change_global','delete_event',
                             self.on_delete_event)
        self.gladeif.connect('button91','clicked',self.close)
        self.gladeif.connect('ok','clicked',self.on_ok_clicked)
        self.gladeif.connect('button102','clicked',self.on_help_clicked)
        self.gladeif.connect('notebook2','switch_page',
                             self.on_notebook_switch_page)
        self.gladeif.connect('add_attr','clicked',self.on_add_attr_clicked)
        self.gladeif.connect('button101','clicked',self.on_update_attr_clicked)
        self.gladeif.connect('del_attr','clicked',self.on_delete_attr_clicked)

        for name in ['gl_del_src','gl_add_src','add_attr','del_attr','ok']:
            self.change_dialog.get_widget(name).set_sensitive(mode)

        self.redraw_attr_list()
        if parent_window:
            self.window.set_transient_for(parent_window)
        self.add_itself_to_menu()
        self.window.show()
        if not self.refs:
            Utils.temp_label(self.refs_label,self.window)
            self.cursor_type = None
            self.idle = gobject.idle_add(self.display_refs)

    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()
        gc.collect()

    def close(self,obj=None):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.window.destroy()
        if self.idle != None:
            gobject.source_remove(self.idle)
        gc.collect()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.parent.child_windows[self.win_key] = self
        label = _('Media Object')
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Properties Editor'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.parent.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_up_clicked(self,obj):
        store,node = self.atree.get_selected()
        if node:
            row = self.atree.get_row(node)
            if row != 0:
                self.atree.select_row(row-1)

    def on_down_clicked(self,obj):
        model,node = self.atree.get_selected()
        if not node:
            return
        row = self.atree.get_row(node)
        self.atree.select_row(row+1)

    def update_info(self):
        fname = self.obj.get_path()
        self.change_dialog.get_widget("path").set_text(fname)

    def redraw_attr_list(self):
        self.atree.clear()
        self.amap = {}
        for attr in self.alist:
            d = [attr.get_type(),attr.get_value()]
            node = self.atree.add(d,attr)
            self.amap[str(attr)] = node
        if self.alist:
            Utils.bold_label(self.attr_label)
        else:
            Utils.unbold_label(self.attr_label)

    def button_press(self,obj):
        data = self.refmodel.get_selected_objects()
        if not data:
            return
        (data_type,handle) = data[0]
        if data_type == 0:
            import EditPerson
            person = self.db.get_person_from_handle(handle)
            EditPerson.EditPerson(self.parent.parent,person,self.db)
        elif data_type == 1:
            import Marriage
            family = self.db.get_family_from_handle(handle)
            Marriage.Marriage(self.parent.parent,family,self.db)
        elif data_type == 2:
            import EventEdit
            event = self.db.get_event_from_handle(handle)
            event_name = event.get_name()
            if const.family_events.has_key(event_name):
                EventEdit.FamilyEventEditor(
                    self,", ", event, None, 0, None, None, self.db.readonly)
            elif const.personal_events.has_key(event_name):
                EventEdit.PersonEventEditor(
                    self,", ", event, None, 0, None, None, self.db.readonly)
            elif event_name in ["Birth","Death"]:
                EventEdit.PersonEventEditor(
                    self,", ", event, None, 1, None, None, self.db.readonly)
        elif data_type == 3:
            import EditPlace
            place = self.db.get_place_from_handle(handle)
            EditPlace.EditPlace(self.parent.parent,place)
        elif data_type == 4:
            source = self.db.get_source_from_handle(handle)
            import EditSource
            EditSource.EditSource(source,self.db,self.parent.parent,
                                  None,self.db.readonly)
            
    def display_refs(self):
        media_handle = self.obj.get_handle()
        self.refs = 1

        # Initialize things if we're entering this functioin
        # for the first time
        if not self.cursor_type:
            self.cursor_type = 'Person'
            self.cursor = self.db.get_person_cursor()
            self.data = self.cursor.first()

            self.any_refs = False
            titles = [(_('Type'),0,150),(_('ID'),1,75),(_('Name'),2,150)]
            self.refmodel = ListModel.ListModel(
                self.change_dialog.get_widget("refinfo"),
                titles,
                event_func=self.button_press)

        if self.cursor_type == 'Person':
            while self.data:
                handle,val = self.data
                person = RelLib.Person()
                person.unserialize(val)
                if person.has_media_reference(media_handle):
                    name = NameDisplay.displayer.display(person)
                    gramps_id = person.get_gramps_id()
                    self.refmodel.add([_("Person"),gramps_id,name],
                                      (0,handle))
                    self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()
            
            self.cursor_type = 'Family'
            self.cursor = self.db.get_family_cursor()
            self.data = self.cursor.first()

        if self.cursor_type == 'Family':
            while self.data:
                handle,val = self.data
                family = RelLib.Family()
                family.unserialize(val)
                if family.has_media_reference(media_handle):
                    name = Utils.family_name(family,self.db)
                    gramps_id = family.get_gramps_id()
                    self.refmodel.add([_("Family"),gramps_id,name],
                                      (1,handle))
                    self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()
            
            self.cursor_type = 'Event'
            self.cursor = self.db.get_event_cursor()
            self.data = self.cursor.first()

        if self.cursor_type == 'Event':
            while self.data:
                handle,val = self.data
                event = RelLib.Event()
                event.unserialize(val)
                if event.has_media_reference(media_handle):
                    name = event.get_name()
                    gramps_id = event.get_gramps_id()
                    self.refmodel.add([_("Event"),gramps_id,name],
                                      (2,handle))
                    self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()
            
            self.cursor_type = 'Place'
            self.cursor = self.db.get_place_cursor()
            self.data = self.cursor.first()

        if self.cursor_type == 'Place':
            while self.data:
                handle,val = self.data
                place = RelLib.Place()
                place.unserialize(val)
                if place.has_media_reference(media_handle):
                    name = place.get_title()
                    gramps_id = place.get_gramps_id()
                    self.refmodel.add([_("Place"),gramps_id,name],
                                      (3,handle))
                    self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()
            
            self.cursor_type = 'Source'
            self.cursor = self.db.get_source_cursor()
            self.data = self.cursor.first()

        if self.cursor_type == 'Source':
            while self.data:
                handle,val = self.data
                source = RelLib.Source()
                source.unserialize(val)
                if source.has_media_reference(media_handle):
                    name = source.get_title()
                    gramps_id = source.get_gramps_id()
                    self.refmodel.add([_("Source"),gramps_id,name],
                                      (4,handle))
                    self.any_refs = True
                self.data = self.cursor.next()
                if gtk.events_pending():
                    return True
            self.cursor.close()

        if self.any_refs:
            Utils.bold_label(self.refs_label,self.window)
        else:
            Utils.unbold_label(self.refs_label,self.window)

        self.cursor_type = None
        return False
        
    def on_notebook_switch_page(self,obj,junk,page):
        if page == 3 and not self.refs:
            Utils.temp_label(self.refs_label,self.window)
            self.idle = gobject.idle_add(self.display_refs)
        t = self.notes.get_buffer()
        text = unicode(t.get_text(t.get_start_iter(),t.get_end_iter(),False))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)
            
    def get_place(self,field,makenew=0):
        text = unicode(field.get_text().strip())
        if text:
            if self.pdmap.has_key(text):
                return self.pdmap[text]
            elif makenew:
                place = RelLib.Place()
                place.set_title(text)
                trans = self.db.transaction_begin()
                self.db.add_place(place,trans)
                self.db.transaction_commit(trans,_('Add Place (%s)' % text))
                self.pdmap[text] = place.get_handle()
                return place.get_handle()
            else:
                return None
        else:
            return None

    def on_apply_clicked(self, obj):
        t = self.notes.get_buffer()
        text = unicode(t.get_text(t.get_start_iter(),t.get_end_iter(),False))
        desc = unicode(self.descr_window.get_text())
        note = self.obj.get_note()
        path = self.change_dialog.get_widget('path').get_text()
        if path != self.obj.get_path():
            mime = GrampsMime.get_type(path)
            self.obj.set_mime_type(mime)
        self.obj.set_path(path)

        if not self.date_object.is_equal(self.obj.get_date_object()):
            self.obj.set_date_object(self.date_object)

        format = self.preform.get_active()
        if text != note or desc != self.obj.get_description():
            self.obj.set_note(text)
            self.obj.set_description(desc)
        if format != self.obj.get_note_format():
            self.obj.set_note_format(format)
        if self.lists_changed:
            self.obj.set_attribute_list(self.alist)
            self.obj.set_source_reference_list(self.srcreflist)
        trans = self.db.transaction_begin()
        self.db.commit_media_object(self.obj,trans)
        self.db.transaction_commit(trans,_("Edit Media Object"))

    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-media')
        
    def on_ok_clicked(self, obj):
        self.on_apply_clicked(obj)
        self.close(obj)

    def on_attr_list_select_row(self,obj):
        store,node = self.atree.get_selected()
        if node:
            attr = self.atree.get_object(node)

            self.attr_type.set_label(attr.get_type())
            self.attr_value.set_text(attr.get_value())
        else:
            self.attr_type.set_label('')
            self.attr_value.set_text('')

    def attr_callback(self,attr):
        self.redraw_attr_list()
        self.atree.select_iter(self.amap[str(attr)])

    def on_update_attr_clicked(self,obj):
        import AttrEdit

        store,node = self.atree.get_selected()
        if node:
            attr = self.atree.get_object(node)
            AttrEdit.AttributeEditor(self,attr,"Media Object",
                                     PluginMgr.get_image_attributes(),
                                     self.attr_callback)

    def on_delete_attr_clicked(self,obj):
        if Utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        AttrEdit.AttributeEditor(self,None,"Media Object",
                                 PluginMgr.get_image_attributes(),
                                 self.attr_callback)

class DeleteMediaQuery:

    def __init__(self,media_handle,db,the_lists):
        self.db = db
        self.media_handle = media_handle
        self.the_lists = the_lists
        
    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        (person_list,family_list,event_list,
                place_list,source_list) = self.the_lists

        for handle in person_list:
            person = self.db.get_person_from_handle(handle)
            new_list = [ photo for photo in person.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            person.set_media_list(new_list)
            self.db.commit_person(person,trans)

        for handle in family_list:
            family = self.db.get_family_from_handle(handle)
            new_list = [ photo for photo in family.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            family.set_media_list(new_list)
            self.db.commit_family(family,trans)

        for handle in event_list:
            event = self.db.get_event_from_handle(handle)
            new_list = [ photo for photo in event.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            event.set_media_list(new_list)
            self.db.commit_event(event,trans)

        for handle in place_list:
            place = self.db.get_place_from_handle(handle)
            new_list = [ photo for photo in place.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            place.set_media_list(new_list)
            self.db.commit_place(place,trans)

        for handle in source_list:
            source = self.db.get_source_from_handle(handle)
            new_list = [ photo for photo in source.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            source.set_media_list(new_list)
            self.db.commit_source(source,trans)

        self.db.enable_signals()
        self.db.remove_object(self.media_handle,trans)
        self.db.transaction_commit(trans,_("Remove Media Object"))

def build_dropdown(entry,strings):
    store = gtk.ListStore(str)
    for value in strings:
        node = store.append()
        store.set(node,0,value)
    completion = gtk.EntryCompletion()
    completion.set_text_column(0)
    completion.set_model(store)
    entry.set_completion(completion)
