#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
from gettext import gettext as _
import cPickle as pickle
import urlparse

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
import os

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import RelLib
import Utils
import ImgManip
import Errors
import Mime
from DdTargets import DdTargets
from _ButtonTab import ButtonTab

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def make_launcher(prog, path):
    return lambda x: Utils.launch(prog, path)

#-------------------------------------------------------------------------
#
# GalleryTab
#
#-------------------------------------------------------------------------
class GalleryTab(ButtonTab):

    _DND_TYPE   = DdTargets.MEDIAREF
    _DND_EXTRA  = DdTargets.URI_LIST

    def __init__(self, dbstate, uistate, track,  media_list, update=None):
        ButtonTab.__init__(self, dbstate, uistate, track, _('Gallery'), True)
        self.media_list = media_list
        self.update = update

        self._set_dnd()

        self.rebuild()
        self.show_all()

    def double_click(self, obj, event):
        """
        Handles the double click on list. If the double click occurs, 
        the Edit button handler is called
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.edit_button_clicked(obj)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            reflist = self.iconlist.get_selected_items()
            if len(reflist) == 1:
                ref = self.media_list[reflist[0][0]]
                self.right_click(ref, event)

    def right_click(self, obj, event):
        itemlist = [
            (True, gtk.STOCK_ADD, self.add_button_clicked), 
            (False, _('Share'), self.edit_button_clicked), 
            (True, gtk.STOCK_EDIT, self.edit_button_clicked), 
            (True, gtk.STOCK_REMOVE, self.del_button_clicked), 
            ]

        menu = gtk.Menu()

        ref_obj = self.dbstate.db.get_object_from_handle(obj.ref)
        mime_type = ref_obj.get_mime_type()
        if mime_type:
            app = Mime.get_application(mime_type)
            if app:
                item = gtk.MenuItem(_('Open with %s') % app[1])
                item.connect('activate', make_launcher(app[0], 
                                                      ref_obj.get_path()))
                item.show()
                menu.append(item)
                item = gtk.SeparatorMenuItem()
                item.show()
                menu.append(item)
        
        for (image, title, func) in itemlist:
            if image:
                item = gtk.ImageMenuItem(stock_id=title)
            else:
                item = gtk.MenuItem(title)
            item.connect('activate', func)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, event.button, event.time)
        
    def get_icon_name(self):
        return 'gramps-media'

    def is_empty(self):
        return len(self.media_list)==0

    def _build_icon_model(self):
        self.iconmodel= gtk.ListStore(gtk.gdk.Pixbuf, str, object)

    def _connect_icon_model(self):
        self.iconlist.set_model(self.iconmodel)
        self.iconmodel.connect_after('row-inserted', self._update_internal_list)
        self.iconmodel.connect_after('row-deleted', self._update_internal_list)

    def build_interface(self):

        self._build_icon_model()
        # build the icon view
        self.iconlist = gtk.IconView()
        self.iconlist.set_pixbuf_column(0)
        self.iconlist.set_text_column(1)
        self.iconlist.set_margin(12)
        try:
            # This is only available for pygtk 2.8
            self.iconlist.set_reorderable(True)
        except AttributeError:
            pass
        self.iconlist.set_item_width(125)
        self.iconlist.set_spacing(24)
        self.iconlist.set_selection_mode(gtk.SELECTION_SINGLE)
        self.iconlist.connect('selection-changed', self._selection_changed)
        self.iconlist.connect('button_press_event', self.double_click)
        self._connect_icon_model()
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.iconlist)
        self.pack_start(scroll, True)

    def _update_internal_list(self, *obj):
        newlist = []
        node = self.iconmodel.get_iter_first()
        while node != None:
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
            pixbuf = ImgManip.get_thumbnail_image(obj.get_path(), 
                                                  obj.get_mime_type())
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
        import AddMedia

        am = AddMedia.AddMediaObject(self.dbstate, self.uistate, self.track)
        am.run()
        src = am.object

        if src:
            sref = RelLib.MediaRef()
            try:
                from Editors import EditMediaRef
                
                EditMediaRef(self.dbstate, self.uistate, self.track, 
                             src, sref, self.add_callback)
            except Errors.WindowActiveError:
                pass

    def add_callback(self, media_ref, media):
        media_ref.ref = media.handle
        self.get_data().append(media_ref)
        self.changed = True
        self.rebuild()

    def share_button_clicked(self, obj):
        """
        Function called with the Add button is clicked. This function
        should be overridden by the derived class.
        """
        from Selectors import selector_factory
        SelectObject = selector_factory('MediaObject')

        sel = SelectObject(self.dbstate,self.uistate,self.track)
        src = sel.run()
        if src:
            sref = RelLib.MediaRef()
            try:
                from Editors import EditMediaRef
                
                EditMediaRef(self.dbstate, self.uistate, self.track, 
                             src, sref, self.add_callback)
            except Errors.WindowActiveError:
                pass

    def del_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            self.media_list.remove(ref)
            self.rebuild()

    def edit_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            obj = self.dbstate.db.get_object_from_handle(ref.get_reference_handle())
            try:
                from Editors import EditMediaRef
                
                EditMediaRef(self.dbstate, self.uistate, self.track, 
                             obj, ref, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self, media_ref, ref):
        self.changed = True
        self.rebuild()

    def _set_dnd(self):
        """
        Sets up drag-n-drop. The source and destionation are set by calling .target()
        on the _DND_TYPE. Obviously, this means that there must be a _DND_TYPE
        variable defined that points to an entry in DdTargets.
        """

        dnd_types = [ self._DND_TYPE.target(), self._DND_EXTRA.target(),
                      DdTargets.MEDIAOBJ.target()]

        self.iconlist.drag_dest_set(gtk.DEST_DEFAULT_ALL, dnd_types,
                                    gtk.gdk.ACTION_COPY)
        self.iconlist.drag_source_set(gtk.gdk.BUTTON1_MASK,
                                      [self._DND_TYPE.target()],
                                      gtk.gdk.ACTION_COPY)
        self.iconlist.connect('drag_data_get', self.drag_data_get)
        self.iconlist.connect('drag_data_received', self.drag_data_received)
        
    def drag_data_get(self, widget, context, sel_data, info, time):
        """
        Provide the drag_data_get function, which passes a tuple consisting of:

           1) Drag type defined by the .drag_type field specfied by the value
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
            value = (self._DND_TYPE.drag_type, id(self), obj, self.find_index(obj))
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
                    data = self.iconlist.get_dest_item_at_pos(x,y)
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
                    oref = RelLib.MediaRef()
                    oref.set_reference_handle(obj)
                    self.get_data().append(oref)
                    self.changed = True
                    self.rebuild()
                elif self._DND_EXTRA and mytype == self._DND_EXTRA.drag_type:
                    self.handle_extra_type(mytype, obj)
            except pickle.UnpicklingError:
                d = Utils.fix_encoding(sel_data.data.replace('\0',' ').strip())
                protocol,site,mfile,j,k,l = urlparse.urlparse(d)
                if protocol == "file":
                    name = Utils.fix_encoding(mfile)
                    mime = Mime.get_type(name)
                    if not Mime.is_valid_type(mime):
                        return
                    photo = RelLib.MediaObject()
                    photo.set_path(name)
                    photo.set_mime_type(mime)
                    basename = os.path.basename(name)
                    (root,ext) = os.path.splitext(basename)
                    photo.set_description(root)
                    trans = self.dbstate.db.transaction_begin()
                    self.dbstate.db.add_object(photo, trans)
                    oref = RelLib.MediaRef()
                    oref.set_reference_handle(photo.get_handle())
                    self.get_data().append(oref)
                    self.changed = True
#                    self.dataobj.add_media_reference(oref)
                    self.dbstate.db.transaction_commit(trans,
                                                       _("Drag Media Object"))
                    self.rebuild()
#                 elif protocol != "":
#                     import urllib
#                     u = urllib.URLopener()
#                     try:
#                         tfile,headers = u.retrieve(d)
#                     except (IOError,OSError), msg:
#                         t = _("Could not import %s") % d
#                         ErrorDialog(t,str(msg))
#                         return
#                     tfile = Utils.fix_encoding(tfile)
#                     mime = GrampsMime.get_type(tfile)
#                     photo = RelLib.MediaObject()
#                     photo.set_mime_type(mime)
#                     photo.set_description(d)
#                     photo.set_path(tfile)
#                     trans = self.db.transaction_begin()
#                     self.db.add_object(photo,trans)
#                     self.db.transaction_commit(trans,_("Drag Media Object"))
#                     oref = RelLib.MediaRef()
#                     oref.set_reference_handle(photo.get_handle())
#                     self.dataobj.add_media_reference(oref)
#                     self.add_thumbnail(oref)

    def handle_extra_type(self, objtype, obj):
        pass

    def _handle_drag(self, row, obj):
        self.get_data().insert(row, obj)
        self.changed = True
        self.rebuild()

    def _move(self, row_from, row_to, obj):
        dlist = self.get_data()
        if row_from < row_to:
            dlist.insert(row_to, obj)
            del dlist[row_from]
        else:
            del dlist[row_from]
            dlist.insert(row_to-1, obj)
        self.changed = True
        self.rebuild()

    def find_index(self, obj):
        """
        returns the index of the object within the associated data
        """
        return self.get_data().index(obj)

