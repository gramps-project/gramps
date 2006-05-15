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

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import RelLib
import Utils
import ImgManip
import Mime
import Errors
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

    def __init__(self, dbstate, uistate, track,  media_list, update=None):
        ButtonTab.__init__(self, dbstate, uistate, track, _('Gallery'), True)
        self.media_list = media_list
        self.update = update
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
        self.iconlist.set_reorderable(True)
        self.iconlist.set_item_width(125)
        self.iconlist.set_spacing(24)
        self.iconlist.set_selection_mode(gtk.SELECTION_SINGLE)
        self.iconlist.connect('selection-changed', self._selection_changed)
        self.iconlist.connect('button_press_event', self.double_click)
        self._connect_icon_model()
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.iconlist)
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

        sel = SelectObject(self.dbstate,self.uistate,self.track,
                                        _("Select media"))
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
