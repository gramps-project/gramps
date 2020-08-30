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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
import os
import pickle
from urllib.parse import urlparse
from urllib.request import url2pathname

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import GLib

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from ...utils import is_right_click, open_file_with_default_application
from ...dbguielement import DbGUIElement
from ...selectors import SelectorFactory
from gramps.gen.lib import Media, MediaRef
from gramps.gen.db import DbTxn
from gramps.gen.utils.file import (media_path_full, media_path, relative_path,
                                   create_checksum)
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gen.errors import WindowActiveError
from gramps.gen.mime import get_type, is_valid_type
from ...ddtargets import DdTargets
from .buttontab import ButtonTab
from gramps.gen.const import THUMBSCALE
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def make_launcher(path, uistate):
    return lambda x: open_file_with_default_application(path, uistate)
#-------------------------------------------------------------------------
#
# GalleryTab
#
#-------------------------------------------------------------------------
class GalleryTab(ButtonTab, DbGUIElement):

    _DND_TYPE = DdTargets.MEDIAREF
    _DND_EXTRA = DdTargets.URI_LIST

    def __init__(self, dbstate, uistate, track,  media_list, update=None):
        self.iconlist = Gtk.IconView()
        ButtonTab.__init__(self, dbstate, uistate, track, _('_Gallery'), True,
                           move_buttons=ButtonTab.L_R)
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
           {'media-delete': self.media_delete,  # delete a media we track
            'media-update': self.media_update,  # change a media we track
           })
        self.callman.connect_all(keys=['media'])

    def double_click(self, obj, event):
        """
        Handle the button press event: double click or right click on iconlist.
        If the double click occurs, the Edit button handler is called.
        """
        if (event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS
                and event.button == 1):
            self.edit_button_clicked(obj)
            return True
        elif is_right_click(event):
            reflist = self.iconlist.get_selected_items()
            if len(reflist) == 1:
                path = reflist[0].get_indices()
                ref = self.media_list[path[0]]
                self.right_click(ref, event)
                return True
        return

    def right_click(self, obj, event):
        itemlist = [
            (True, _('_Add'), self.add_button_clicked),
            (True, _('Share'), self.share_button_clicked),
            (False, _('_Edit'), self.edit_button_clicked),
            (True, _('_Remove'), self.del_button_clicked),
            ]

        self.menu = Gtk.Menu()
        self.menu.set_reserve_toggle_size(False)

        ref_obj = self.dbstate.db.get_media_from_handle(obj.ref)
        media_path = media_path_full(self.dbstate.db, ref_obj.get_path())
        if media_path:
            # Translators: _View means "to look at this"
            item = Gtk.MenuItem.new_with_mnemonic(_('_View', 'verb:look at this'))
            item.connect('activate', make_launcher(media_path, self.uistate))
            item.show()
            self.menu.append(item)
            mfolder, mfile = os.path.split(media_path)
            item = Gtk.MenuItem.new_with_mnemonic(_('Open Containing _Folder'))
            item.connect('activate', make_launcher(mfolder, self.uistate))
            item.show()
            self.menu.append(item)
            item = Gtk.SeparatorMenuItem()
            item.show()
            self.menu.append(item)

            item = Gtk.MenuItem.new_with_mnemonic(_('_Make Active Media'))
            item.connect('activate', lambda obj: self.uistate.set_active(ref_obj.handle, "Media"))
            item.show()
            self.menu.append(item)
            item = Gtk.SeparatorMenuItem()
            item.show()
            self.menu.append(item)

        for (needs_write_access, title, func) in itemlist:
            item = Gtk.MenuItem.new_with_mnemonic(title)
            item.connect('activate', func)
            if needs_write_access and self.dbstate.db.readonly:
                item.set_sensitive(False)
            item.show()
            self.menu.append(item)
        self.menu.popup(None, None, None, None, event.button, event.time)

    def get_icon_name(self):
        return 'gramps-media'

    def is_empty(self):
        return len(self.media_list)==0

    def _build_icon_model(self):
        self.iconmodel = Gtk.ListStore(GdkPixbuf.Pixbuf, GObject.TYPE_STRING,
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
        text_renderer = Gtk.CellRendererText()
        text_renderer.set_property('wrap-mode', Pango.WrapMode.WORD_CHAR)
        text_renderer.set_property('wrap-width', THUMBSCALE)
        text_renderer.set_property('alignment', Pango.Alignment.CENTER)
        self.iconlist.pack_end(text_renderer, True)
        self.iconlist.add_attribute(text_renderer, "text", 1)

        # set basic properties of the icon view
        self.iconlist.set_margin(padding)
        self.iconlist.set_column_spacing(padding)
        self.iconlist.set_reorderable(True)
        self.iconlist.set_selection_mode(Gtk.SelectionMode.SINGLE)

        # connect the signals
        self.__id_connect_sel = self.iconlist.connect('selection-changed', self._selection_changed)
        self.iconlist.connect('button_press_event', self.double_click)
        self.iconlist.connect('key_press_event', self.key_pressed)
        self._connect_icon_model()

        # create the scrolled window
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # put everything together
        scroll.add(self.iconlist)
        self.pack_end(scroll, True, True, 0)

    def _update_internal_list(self, *obj):
        newlist = []
        node = self.iconmodel.get_iter_first()
        while node is not None:
            newlist.append(self.iconmodel.get_value(node, 2))
            node = self.iconmodel.iter_next(node)
        for i in range(len(self.media_list)):
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
            obj = self.dbstate.db.get_media_from_handle(handle)
            if obj is None :
                #notify user of error
                from ...dialog import RunDatabaseRepair
                RunDatabaseRepair(
                    _('Non existing media found in the Gallery'),
                    parent=self.uistate.window)
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
            path = node[0].get_indices()
            return self.media_list[path[0]]
        return None

    def add_button_clicked(self, obj):
        try:
            from .. import EditMediaRef
            EditMediaRef(self.dbstate, self.uistate, self.track,
                         Media(), MediaRef(),
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
                GLib.idle_add(self.iconlist.scroll_to_path, path, False,
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
        SelectObject = SelectorFactory('Media')

        sel = SelectObject(self.dbstate, self.uistate, self.track)
        src = sel.run()
        if src:
            sref = MediaRef()
            try:
                from .. import EditMediaRef
                EditMediaRef(self.dbstate, self.uistate, self.track,
                             src, sref, self.add_callback)
            except WindowActiveError:
                from ...dialog import WarningDialog
                WarningDialog(_("Cannot share this reference"),
                              self.__blocked_text(),
                              parent=self.uistate.window)

    def del_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            self.media_list.remove(ref)
            self.rebuild()

    def edit_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            obj = self.dbstate.db.get_media_from_handle(
                                                ref.get_reference_handle())
            try:
                from .. import EditMediaRef
                EditMediaRef(self.dbstate, self.uistate, self.track,
                             obj, ref, self.edit_callback)
            except WindowActiveError:
                from ...dialog import WarningDialog
                WarningDialog(_("Cannot edit this reference"),
                              self.__blocked_text(),
                              parent=self.uistate.window)

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

    def up_button_clicked(self, obj):
        """ Deal with up button """
        ref = self.get_selected()
        if ref:
            pos = self.find_index(ref)
            if pos > 0 :
                self._move_up(pos, ref)

    def down_button_clicked(self, obj):
        """ Deal with down button """
        ref = self.get_selected()
        if ref:
            pos = self.find_index(ref)
            if pos >= 0 and pos < len(self.get_data()) - 1:
                self._move_down(pos, ref)

    def _move_up(self, row_from, obj):
        """
        Move the item a position up in the EmbeddedList.
        Eg: 0,1,2,3 needs to become 0,2,1,3, here row_from = 2
        """
        dlist = self.get_data()
        del dlist[row_from]
        dlist.insert(row_from - 1, obj)
        self.changed = True
        self.rebuild()
        #select the row
        path = Gtk.TreePath.new_from_string(str(row_from - 1))
        self.iconlist.select_path(path)

    def _move_down(self, row_from, obj):
        """
        Move the item a position down in the EmbeddedList.
        Eg: 0,1,2,3 needs to become 0,2,1,3, here row_from = 1
        """
        dlist = self.get_data()
        del dlist[row_from]
        dlist.insert(row_from + 1, obj)
        self.changed = True
        self.rebuild()
        #select the row
        path = Gtk.TreePath.new_from_string(str(row_from + 1))
        self.iconlist.select_path(path)

    def _set_dnd(self):
        """
        Set up drag-n-drop. The source and destination are set by calling .target()
        on the _DND_TYPE. Obviously, this means that there must be a _DND_TYPE
        variable defined that points to an entry in DdTargets.
        """

        dnd_types = [self._DND_TYPE.target(), self._DND_EXTRA.target(),
                     DdTargets.MEDIAOBJ.target()]

        self.iconlist.enable_model_drag_dest(
            dnd_types, Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
        self.iconlist.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                                               [self._DND_TYPE.target()],
                                               Gdk.DragAction.COPY)
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
            path = reflist[0].get_indices()
            obj = self.media_list[path[0]]

            if not obj:
                return

            # pickle the data, and build the tuple to be passed
            value = (self._DND_TYPE.drag_type, id(self), obj,
                     self.find_index(obj))
            data = pickle.dumps(value)

            # pass as a string (8 bits)
            sel_data.set(self._DND_TYPE.atom_drag_type, 8, data)
        except IndexError:
            return

    def drag_data_received(self, widget, context, x, y, sel_data, info, time):
        """
        Handle the standard gtk interface for drag_data_received.

        If the selection data is define, extract the value from sel_data.data,
        and decide if this is a move or a reorder.
        """
        if sel_data and sel_data.get_data():
            sel_list = []
            try:
                rets = pickle.loads(sel_data.get_data())

                # single dnd item
                if isinstance(rets, tuple):
                    sel_list.append(rets)

                # multiple dnd items
                elif isinstance(rets, list):
                    for ret in rets:
                        sel_list.append(pickle.loads(ret))

                for sel in sel_list:
                    (mytype, selfid, obj, row_from) = sel

                    # make sure this is the correct DND type for this object
                    if mytype == self._DND_TYPE.drag_type:

                        # determine the destination row
                        data = self.iconlist.get_dest_item_at_pos(x, y)
                        if data:
                            (path, pos) = data
                            row = path.get_indices()[0]
                            if pos ==  Gtk.IconViewDropPosition.DROP_LEFT:
                                row = max(row, 0)
                            elif pos == Gtk.IconViewDropPosition.DROP_RIGHT:
                                row = min(row, len(self.get_data()))
                            elif pos == Gtk.IconViewDropPosition.DROP_INTO:
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
                        oref = MediaRef()
                        oref.set_reference_handle(obj)
                        self.get_data().append(oref)
                        self.changed = True
                        self.rebuild()
                    elif self._DND_EXTRA and mytype == self._DND_EXTRA.drag_type:
                        self.handle_extra_type(mytype, obj)
            except pickle.UnpicklingError:
                files = sel_data.get_uris()
                for file in files:
                    protocol, site, mfile, j, k, l = urlparse(file)
                    if protocol == "file":
                        name = url2pathname(mfile)
                        mime = get_type(name)
                        if not is_valid_type(mime):
                            return
                        photo = Media()
                        self.uistate.set_busy_cursor(True)
                        photo.set_checksum(create_checksum(name))
                        self.uistate.set_busy_cursor(False)
                        base_dir = str(media_path(self.dbstate.db))
                        if os.path.exists(base_dir):
                            name = relative_path(name, base_dir)
                        photo.set_path(name)
                        photo.set_mime_type(mime)
                        basename = os.path.basename(name)
                        (root, ext) = os.path.splitext(basename)
                        photo.set_description(root)
                        with DbTxn(_("Drag Media Object"),
                                   self.dbstate.db) as trans:
                            self.dbstate.db.add_media(photo, trans)
                            oref = MediaRef()
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

    def clean_up(self):
        self.iconlist.disconnect(self.__id_connect_sel)
        super(ButtonTab, self).clean_up()
