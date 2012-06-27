#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009-2011  Gary Burton
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
# Python classes
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _
import cPickle as pickle
import urlparse

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
import pango
import os
import sys
import urllib
import gobject

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import gui.utils
from gui.dbguielement import DbGUIElement
from gui.selectors import SelectorFactory
import gen.lib
from gen.db import DbTxn
from gen.utils.file import (media_path_full, media_path, relative_path,
                            fix_encoding)
from gui.thumbnails import get_thumbnail_image
from gen.errors import WindowActiveError
import gen.mime
from gui.ddtargets import DdTargets
from buttontab import ButtonTab
from gen.constfunc import win
from gen.const import THUMBSCALE
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def make_launcher(path):
    return lambda x: gui.utils.open_file_with_default_application(path)

#-------------------------------------------------------------------------
#
# GalleryTab
#
#-------------------------------------------------------------------------
class GalleryTab(ButtonTab, DbGUIElement):

    _DND_TYPE   = DdTargets.MEDIAREF
    _DND_EXTRA  = DdTargets.URI_LIST

    def __init__(self, dbstate, uistate, track,  media_list, update=None):
        self.iconlist = gtk.IconView()
        ButtonTab.__init__(self, dbstate, uistate, track, _('_Gallery'), True)
        DbGUIElement.__init__(self, dbstate.db)
        self.track_ref_for_deletion("iconlist")
        self.media_list = media_list
        self.callman.register_handles({'media': [mref.ref for mref 
                                                          in self.media_list]})
        self.update = update

        self._set_dnd()

        self.rebuild()
        self.show_all()
    
    def _connect_db_signals(self):
        """
        Implement base class DbGUIElement method
        """
        #note: media-rebuild closes the editors, so no need to connect to it
        self.callman.register_callbacks(
           {'media-delete': self.media_delete,  # delete a mediaobj we track
            'media-update': self.media_update,  # change a mediaobj we track
           })
        self.callman.connect_all(keys=['media'])

    def double_click(self, obj, event):
        """
        Handle the button press event: double click or right click on iconlist. 
        If the double click occurs, the Edit button handler is called.
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.edit_button_clicked(obj)
            return True
        elif gui.utils.is_right_click(event):
            reflist = self.iconlist.get_selected_items()
            if len(reflist) == 1:
                ref = self.media_list[reflist[0][0]]
                self.right_click(ref, event)
                return True
        return

    def right_click(self, obj, event):
        itemlist = [
            (True, True, gtk.STOCK_ADD, self.add_button_clicked), 
            (True, False, _('Share'), self.share_button_clicked), 
            (False,True, gtk.STOCK_EDIT, self.edit_button_clicked), 
            (True, True, gtk.STOCK_REMOVE, self.del_button_clicked), 
            ]

        menu = gtk.Menu()

        ref_obj = self.dbstate.db.get_object_from_handle(obj.ref)
        media_path = media_path_full(self.dbstate.db, ref_obj.get_path())
        if media_path:
            item = gtk.ImageMenuItem(_('View'))
            img = gtk.Image()
            img.set_from_stock("gramps-viewmedia", gtk.ICON_SIZE_MENU)
            item.set_image(img)
            item.connect('activate', make_launcher(media_path))
            item.show()
            menu.append(item)
            mfolder, mfile = os.path.split(media_path)
            item = gtk.MenuItem(_('Open Containing _Folder'))
            item.connect('activate', make_launcher(mfolder))
            item.show()
            menu.append(item)
            item = gtk.SeparatorMenuItem()
            item.show()
            menu.append(item)
        
        for (needs_write_access, image, title, func) in itemlist:
            if image:
                item = gtk.ImageMenuItem(stock_id=title)
            else:
                item = gtk.MenuItem(title)
            item.connect('activate', func)
            if needs_write_access and self.dbstate.db.readonly:
                item.set_sensitive(False)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, event.button, event.time)
        
    def get_icon_name(self):
        return 'gramps-media'

    def is_empty(self):
        return len(self.media_list)==0

    def _build_icon_model(self):
        self.iconmodel = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING, 
                                      object)
        self.track_ref_for_deletion("iconmodel")

    def _connect_icon_model(self):
        self.iconlist.set_model(self.iconmodel)
        self.iconmodel.connect_after('row-inserted', self._update_internal_list)
        self.iconmodel.connect_after('row-deleted', self._update_internal_list)

    def build_interface(self):
        """Setup the GUI.
        
        It includes an IconView placed inside of a ScrolledWindow.
        
        """
        # create the model used with the icon view
        self._build_icon_model()

        # pixels to pad the image
        padding = 6
        
        # build the icon view
        self.iconlist.set_pixbuf_column(0)
        self.iconlist.set_item_width(int(THUMBSCALE) + padding * 2)
        # set custom text cell renderer for better control
        text_renderer = gtk.CellRendererText()
        text_renderer.set_property('wrap-mode', pango.WRAP_WORD_CHAR)
        text_renderer.set_property('wrap-width', THUMBSCALE)
        text_renderer.set_property('alignment', pango.ALIGN_CENTER)
        self.iconlist.pack_end(text_renderer)
        self.iconlist.set_attributes(text_renderer, text=1)
        
        # set basic properties of the icon view
        self.iconlist.set_margin(padding)
        self.iconlist.set_column_spacing(padding)
        self.iconlist.set_reorderable(True)
        self.iconlist.set_selection_mode(gtk.SELECTION_SINGLE)
        
        # connect the signals
        self.iconlist.connect('selection-changed', self._selection_changed)
        self.iconlist.connect('button_press_event', self.double_click)
        self.iconlist.connect('key_press_event', self.key_pressed)
        self._connect_icon_model()
        
        # create the scrolled window
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        # put everything together
        scroll.add(self.iconlist)
        self.pack_end(scroll, True)

    def _update_internal_list(self, *obj):
        newlist = []
        node = self.iconmodel.get_iter_first()
        while node is not None:
            newlist.append(self.iconmodel.get_value(node, 2))
            node = self.iconmodel.iter_next(node)
        for i in xrange(len(self.media_list)):
            self.media_list.pop()
        for i in newlist:
            if i:
                self.media_list.append(i)

        if self.update:
            self.update()
        self.changed = True

    def get_data(self):
        return self.media_list

    def rebuild(self):
        self._build_icon_model()
        for ref in self.media_list:
            handle = ref.get_reference_handle()
            obj = self.dbstate.db.get_object_from_handle(handle)
            if obj is None :
                #notify user of error
                from gui.dialog import RunDatabaseRepair
                RunDatabaseRepair(
                            _('Non existing media found in the Gallery'))
            else :
                pixbuf = get_thumbnail_image(
                                media_path_full(self.dbstate.db, 
                                                      obj.get_path()), 
                                obj.get_mime_type(),
                                ref.get_rectangle())
                self.iconmodel.append(row=[pixbuf, obj.get_description(), ref])
        self._connect_icon_model()
        self._set_label()
        self._selection_changed()
        if self.update:
            self.update()
        
    def get_selected(self):
        node = self.iconlist.get_selected_items()
        if len(node) > 0:
            return self.media_list[node[0][0]]
        return None

    def add_button_clicked(self, obj):
        try:
            from gui.editors import EditMediaRef
            EditMediaRef(self.dbstate, self.uistate, self.track, 
                         gen.lib.MediaObject(), gen.lib.MediaRef(),
                         self.add_callback)
        except WindowActiveError:
            pass

    def add_callback(self, media_ref, media):
        media_ref.ref = media.handle
        data = self.get_data()
        data.append(media_ref)
        self.callman.register_handles({'media': [media.handle]})
        self.changed = True
        self.rebuild()
        model = self.iconlist.get_model()
        if model:
            itr_last = model.iter_nth_child(None, len(data) - 1)
            if itr_last:
                path = model.get_path(itr_last)
                gobject.idle_add(self.iconlist.scroll_to_path, path, False,
                                                                     0.0, 0.0)

    def __blocked_text(self):
        """
        Return the common text used when mediaref cannot be edited
        """
        return _("This media reference cannot be edited at this time. "
                    "Either the associated media object is already being "
                    "edited or another media reference that is associated with "
                    "the same media object is being edited.\n\nTo edit this "
                    "media reference, you need to close the media object.")

    def share_button_clicked(self, obj):
        """
        Function called when the Share button is clicked. 
        
        This function should be overridden by the derived class.
        
        """
        SelectObject = SelectorFactory('MediaObject')

        sel = SelectObject(self.dbstate, self.uistate, self.track)
        src = sel.run()
        if src:
            sref = gen.lib.MediaRef()
            try:
                from gui.editors import EditMediaRef
                EditMediaRef(self.dbstate, self.uistate, self.track, 
                             src, sref, self.add_callback)
            except WindowActiveError:
                from gui.dialog import WarningDialog
                WarningDialog(_("Cannot share this reference"),
                              self.__blocked_text())

    def del_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            self.media_list.remove(ref)
            self.rebuild()

    def edit_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            obj = self.dbstate.db.get_object_from_handle(
                                                ref.get_reference_handle())
            try:
                from gui.editors import EditMediaRef
                EditMediaRef(self.dbstate, self.uistate, self.track, 
                             obj, ref, self.edit_callback)
            except WindowActiveError:
                from gui.dialog import WarningDialog
                WarningDialog(_("Cannot edit this reference"),
                              self.__blocked_text())

    def edit_callback(self, media_ref, media):
        """
        Rebuild the gallery after a media reference is edited in case the
        image rectangle has changed.
        """
        self.rebuild()

    def media_delete(self, del_media_handle_list):
        """
        Outside of this tab media objects have been deleted. Check if tab
        and object must be changed.
        Note: delete of object will cause reference on database to be removed,
              so this method need not do this
        """
        rebuild = False
        ref_handles = [x.ref for x in self.media_list]
        for handle in del_media_handle_list :
            while 1:
                pos = None
                try :
                    pos = ref_handles.index(handle)
                except ValueError :
                    break
            
                if pos is not None:
                    #oeps, we need to remove this reference, and rebuild tab
                    del self.media_list[pos]
                    del ref_handles[pos]
                    rebuild = True
        if rebuild:
            self.rebuild()

    def media_update(self, upd_media_handle_list):
        """
        Outside of this tab media objects have been changed. Check if tab
        and object must be changed.
        """
        ref_handles = [x.ref for x in self.media_list]
        for handle in upd_media_handle_list :
            if handle in ref_handles:
                self.rebuild()
                break

    def _set_dnd(self):
        """
        Set up drag-n-drop. The source and destination are set by calling .target()
        on the _DND_TYPE. Obviously, this means that there must be a _DND_TYPE
        variable defined that points to an entry in DdTargets.
        """

        dnd_types = [ self._DND_TYPE.target(), self._DND_EXTRA.target(),
                      DdTargets.MEDIAOBJ.target()]

        self.iconlist.enable_model_drag_dest(dnd_types,
                                    gtk.gdk.ACTION_MOVE|gtk.gdk.ACTION_COPY)
        self.iconlist.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                                  [self._DND_TYPE.target()],
                                  gtk.gdk.ACTION_COPY)
        self.iconlist.connect('drag_data_get', self.drag_data_get)
        if not self.dbstate.db.readonly:
            self.iconlist.connect('drag_data_received', self.drag_data_received)
        
    def drag_data_get(self, widget, context, sel_data, info, time):
        """
        Provide the drag_data_get function, which passes a tuple consisting of:

           1) Drag type defined by the .drag_type field specified by the value
              assigned to _DND_TYPE
           2) The id value of this object, used for the purpose of determining
              the source of the object. If the source of the object is the same
              as the object, we are doing a reorder instead of a normal drag
              and drop
           3) Pickled data. The pickled version of the selected object
           4) Source row. Used for a reorder to determine the original position
              of the object
        """

        # get the selected object, returning if not is defined

        try:
            reflist = self.iconlist.get_selected_items()
            obj = self.media_list[reflist[0][0]]

            if not obj:
                return
            
            # pickle the data, and build the tuple to be passed
            value = (self._DND_TYPE.drag_type, id(self), obj, 
                     self.find_index(obj))
            data = pickle.dumps(value)

            # pass as a string (8 bits)
            sel_data.set(sel_data.target, 8, data)
        except IndexError:
            return

    def drag_data_received(self, widget, context, x, y, sel_data, info, time):
        """
        Handle the standard gtk interface for drag_data_received.

        If the selection data is define, extract the value from sel_data.data,
        and decide if this is a move or a reorder.
        """
        if sel_data and sel_data.data:
            try:
                (mytype, selfid, obj, row_from) = pickle.loads(sel_data.data)

                # make sure this is the correct DND type for this object
                if mytype == self._DND_TYPE.drag_type:
                    
                    # determine the destination row
                    data = self.iconlist.get_dest_item_at_pos(x, y)
                    if data:
                        (path, pos) = data
                        row = path[0]

                        if pos ==  gtk.ICON_VIEW_DROP_LEFT:
                            row = max(row, 0)
                        elif pos == gtk.ICON_VIEW_DROP_RIGHT:
                            row = min(row, len(self.get_data()))
                        elif pos == gtk.ICON_VIEW_DROP_INTO:
                            row = min(row+1, len(self.get_data()))
                    else:
                        row = len(self.get_data())
                    
                    # if the is same object, we have a move, otherwise,
                    # it is a standard drag-n-drop
                    
                    if id(self) == selfid:
                        self._move(row_from, row, obj)
                    else:
                        self._handle_drag(row, obj)
                    self.rebuild()
                elif mytype == DdTargets.MEDIAOBJ.drag_type:
                    oref = gen.lib.MediaRef()
                    oref.set_reference_handle(obj)
                    self.get_data().append(oref)
                    self.changed = True
                    self.rebuild()
                elif self._DND_EXTRA and mytype == self._DND_EXTRA.drag_type:
                    self.handle_extra_type(mytype, obj)
            except pickle.UnpicklingError:
        #modern file managers provide URI_LIST. For Windows split sel_data.data
                if win():
                    files = sel_data.data.split('\n')
                else:
                    files =  sel_data.get_uris()
                for file in files:
                    d = fix_encoding(file.replace('\0',' ').strip())
                    protocol, site, mfile, j, k, l = urlparse.urlparse(d)
                    if protocol == "file":
                        name = fix_encoding(mfile)
                        name = unicode(urllib.url2pathname(
                                    name.encode(sys.getfilesystemencoding())))
                        mime = gen.mime.get_type(name)
                        if not gen.mime.is_valid_type(mime):
                            return
                        photo = gen.lib.MediaObject()
                        base_dir = unicode(media_path(self.dbstate.db))
                        if os.path.exists(base_dir):
                            name = relative_path(name, base_dir)
                        photo.set_path(name)
                        photo.set_mime_type(mime)
                        basename = os.path.basename(name)
                        (root, ext) = os.path.splitext(basename)
                        photo.set_description(root)
                        with DbTxn(_("Drag Media Object"),
                                   self.dbstate.db) as trans:
                            self.dbstate.db.add_object(photo, trans)
                            oref = gen.lib.MediaRef()
                            oref.set_reference_handle(photo.get_handle())
                            self.get_data().append(oref)
                            self.changed = True
                    self.rebuild()

    def handle_extra_type(self, objtype, obj):
        pass

    def _handle_drag(self, row, obj):
        self.get_data().insert(row, obj)
        self.changed = True

    def _move(self, row_from, row_to, obj):
        dlist = self.get_data()
        if row_from < row_to:
            dlist.insert(row_to, obj)
            del dlist[row_from]
        else:
            del dlist[row_from]
            dlist.insert(row_to, obj)
        self.changed = True

    def find_index(self, obj):
        """
        returns the index of the object within the associated data
        """
        return self.get_data().index(obj)
