#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2008-2009  Stephane Charette <stephanecharette@gmail.com>
#               2009       Gary Burton
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
from gen.ggettext import sgettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gui.utils import open_file_with_default_application
import const
import Mime
import ThumbNails
import Utils
from gen.lib import NoteType
from glade import Glade
from displaytabs import (SourceEmbedList, AttrEmbedList, MediaBackRefList, 
                         NoteTab)
from gui.widgets import MonitoredSpinButton, MonitoredEntry, PrivacyButton
from editreference import RefTab, EditReference
from addmedia import AddMediaObject

#-------------------------------------------------------------------------
#
# EditMediaRef
#
#-------------------------------------------------------------------------
class EditMediaRef(EditReference):

    def __init__(self, state, uistate, track, media, media_ref, update):
        EditReference.__init__(self, state, uistate, track, media,
                               media_ref, update)
        if not self.source.get_handle():
            #show the addmedia dialog immediately, with track of parent.
            AddMediaObject(state, self.uistate, self.track, self.source, 
                           self._update_addmedia)

    def _local_init(self):
        self.width_key = 'interface.media-ref-width'
        self.height_key = 'interface.media-ref-height'
        self.top = Glade()

        self.set_window(self.top.toplevel,
                        self.top.get_object('title'),
                        _('Media Reference Editor'))
        self.define_warn_box(self.top.get_object("warn_box"))
        self.top.get_object("label427").set_text(_("Y coordinate|Y"))
        self.top.get_object("label428").set_text(_("Y coordinate|Y"))

        tblref =  self.top.get_object('table50')
        notebook = self.top.get_object('notebook_ref')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.reftab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('General'), tblref)
        tblref =  self.top.get_object('table2')
        notebook = self.top.get_object('notebook_shared')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.primtab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('_General'), tblref)

    def draw_preview(self):
        """
        Draw the two preview images. This method can be called on eg change of
        the path.
        """
        self.mtype = self.source.get_mime_type()
        fullpath = Utils.media_path_full(self.db, self.source.get_path())
        self.pix = ThumbNails.get_thumbnail_image(fullpath,
                                                  self.mtype)
        self.pixmap.set_from_pixbuf(self.pix)
        
        self.subpix = ThumbNails.get_thumbnail_image(fullpath,
                                                     self.mtype,
                                                     self.rectangle)
        self.subpixmap.set_from_pixbuf(self.subpix)

        mt = Mime.get_description(self.mtype)
        self.top.get_object("type").set_text(mt if mt else "")
        
    def _setup_fields(self):
        ebox_shared = self.top.get_object('eventbox')
        ebox_shared.connect('button-press-event', self.button_press_event)

        if not self.dbstate.db.readonly:
            self.button_press_coords = (0, 0)
            ebox_ref = self.top.get_object('eventbox1')
            ebox_ref.connect('button-press-event', self.button_press_event_ref)
            ebox_ref.connect('button-release-event', 
                                                 self.button_release_event_ref)
            ebox_ref.add_events(gtk.gdk.BUTTON_PRESS_MASK)
            ebox_ref.add_events(gtk.gdk.BUTTON_RELEASE_MASK)

        self.pixmap = self.top.get_object("pixmap")
        
        coord = self.source_ref.get_rectangle()
        #upgrade path: set invalid (from eg old db) to none

        if coord is not None and coord in (
                (None,)*4,  
                (0, 0, 100, 100),
                (coord[0], coord[1])*2
            ):
            coord = None

        self.rectangle = coord
        self.subpixmap = self.top.get_object("subpixmap")

        self.draw_preview()
        
        corners = ["corner1_x", "corner1_y", "corner2_x", "corner2_y"]

        if coord and isinstance(coord, tuple):
            for index, corner in enumerate(corners):
                self.top.get_object(corner).set_value(coord[index])
        else:
            for corner, value in zip(corners, [0, 0, 100, 100]):
                self.top.get_object(corner).set_value(value)
            
        if self.dbstate.db.readonly:
            for corner in corners:
                self.top.get_object(corner).set_sensitive(False)
        
        self.corner1_x_spinbutton = MonitoredSpinButton(
            self.top.get_object("corner1_x"),
            self.set_corner1_x,
            self.get_corner1_x,
            self.db.readonly)

        self.corner1_y_spinbutton = MonitoredSpinButton(
            self.top.get_object("corner1_y"),
            self.set_corner1_y,
            self.get_corner1_y,
            self.db.readonly)

        self.corner2_x_spinbutton = MonitoredSpinButton(
            self.top.get_object("corner2_x"),
            self.set_corner2_x,
            self.get_corner2_x,
            self.db.readonly)

        self.corner2_y_spinbutton = MonitoredSpinButton(
            self.top.get_object("corner2_y"),
            self.set_corner2_y,
            self.get_corner2_y,
            self.db.readonly)

        self.descr_window = MonitoredEntry(
            self.top.get_object("description"),
            self.source.set_description,
            self.source.get_description,
            self.db.readonly)

        self.ref_privacy = PrivacyButton(
            self.top.get_object("private"),
            self.source_ref,
            self.db.readonly)

        self.gid = MonitoredEntry(
            self.top.get_object("gid"),
            self.source.set_gramps_id,
            self.source.get_gramps_id,
            self.db.readonly)

        self.privacy = PrivacyButton(
            self.top.get_object("privacy"),
            self.source,
            self.db.readonly)

        self.path_obj = MonitoredEntry(
            self.top.get_object("path"),
            self.source.set_path,
            self.source.get_path,
            self.db.readonly)

    def set_corner1_x(self, value):
        """
        Callback for the signal handling of the spinbutton for the first
        corner x coordinate of the subsection.
        Updates the subsection thumbnail using the given value
        
        @param value: the first corner x coordinate of the subsection in int
        """
        
        if self.rectangle is None:
            self.rectangle = (0,0,100,100)
        self.rectangle = (value,) + self.rectangle[1:]
        self.update_subpixmap()

    def set_corner1_y(self, value):
        """
        Callback for the signal handling of the spinbutton for the first
        corner y coordinate of the subsection.
        Updates the subsection thumbnail using the given value
        
        @param value: the first corner y coordinate of the subsection in int
        """
        
        if self.rectangle is None:
            self.rectangle = (0,0,100,100)
        self.rectangle = self.rectangle[:1] + (value,) + self.rectangle[2:]
        self.update_subpixmap()

    def set_corner2_x(self, value):
        """
        Callback for the signal handling of the spinbutton for the second
        corner x coordinate of the subsection.
        Updates the subsection thumbnail using the given value
        
        @param value: the second corner x coordinate of the subsection in int
        """
        
        if self.rectangle is None:
            self.rectangle = (0,0,100,100)
        self.rectangle = self.rectangle[:2] + (value,) + self.rectangle[3:]
        self.update_subpixmap()

    def set_corner2_y(self, value):
        """
        Callback for the signal handling of the spinbutton for the second
        corner y coordinate of the subsection.
        Updates the subsection thumbnail using the given value
        
        @param value: the second corner y coordinate of the subsection in int
        """
        
        if self.rectangle is None:
            self.rectangle = (0,0,100,100)
        self.rectangle = self.rectangle[:3] + (value,)
        self.update_subpixmap()

    def get_corner1_x(self):
        """
        Callback for the signal handling of the spinbutton for the first corner 
        x coordinate of the subsection.
        
        @returns: the first corner x coordinate of the subsection or 0 if 
                  there is no selection
        """
        
        if self.rectangle is not None:
            return self.rectangle[0]
        else:
            return 0

    def get_corner1_y(self):
        """
        Callback for the signal handling of the spinbutton for the first corner 
        y coordinate of the subsection.
        
        @returns: the first corner y coordinate of the subsection or 0 if 
                  there is no selection
        """
         
        if self.rectangle is not None:
            return self.rectangle[1]
        else:
            return 0

    def get_corner2_x(self):
        """
        Callback for the signal handling of the spinbutton for the second
        corner x coordinate of the subsection.
        
        @returns: the second corner x coordinate of the subsection or 100 if 
                  there is no selection
        """
        
        if self.rectangle is not None:
            return self.rectangle[2]
        else:
            return 100

    def get_corner2_y(self):
        """
        Callback for the signal handling of the spinbutton for the second
        corner x coordinate of the subsection.
        
        @returns: the second corner x coordinate of the subsection or 100 if 
                  there is no selection
        """
        
        if self.rectangle is not None:
            return self.rectangle[3]
        else:
            return 100

    def update_subpixmap(self):
        """
        Updates the thumbnail of the specified subsection
        """
        
        path = self.source.get_path()
        if path is None:
            self.subpixmap.hide()
        else:
            try:
                fullpath = Utils.media_path_full(self.db, path)
                pixbuf = gtk.gdk.pixbuf_new_from_file(fullpath)
                width = pixbuf.get_width()
                height = pixbuf.get_height()
                upper_x = min(self.rectangle[0], self.rectangle[2])/100.
                lower_x = max(self.rectangle[0], self.rectangle[2])/100.
                upper_y = min(self.rectangle[1], self.rectangle[3])/100.
                lower_y = max(self.rectangle[1], self.rectangle[3])/100.
                sub_x = int(upper_x * width)
                sub_y = int(upper_y * height)
                sub_width = int((lower_x - upper_x) * width)
                sub_height = int((lower_y - upper_y) * height)
                if sub_width > 0 and sub_height > 0:
                    pixbuf = pixbuf.subpixbuf(sub_x, sub_y, sub_width, sub_height)
                    width = sub_width
                    height = sub_height
                ratio = float(max(height, width))
                scale = const.THUMBSCALE / ratio
                x = int(scale * width)
                y = int(scale * height)
                pixbuf = pixbuf.scale_simple(x, y, gtk.gdk.INTERP_BILINEAR)
                self.subpixmap.set_from_pixbuf(pixbuf)
                self.subpixmap.show()
            except:
                self.subpixmap.hide()

    def build_menu_names(self, person):
        """
        Provide the information needed by the base class to define the
        window management menu entries.
        """
        if self.source:
            submenu_label = _('Media: %s')  % self.source.get_gramps_id()
        else:
            submenu_label = _('New Media')
        return (_('Media Reference Editor'),submenu_label)
    
    def button_press_event(self, obj, event):
        if event.button==1 and event.type == gtk.gdk._2BUTTON_PRESS:
            photo_path = Utils.media_path_full(self.db, self.source.get_path())
            open_file_with_default_application(photo_path)

    def button_press_event_ref(self, widget, event):
        """
        Handle the button-press-event generated by the eventbox
        parent of the subpixmap.  Remember these coordinates
        so we can crop the picture when button-release-event
        is received.
        """
        self.button_press_coords = (event.x, event.y)

    def button_release_event_ref(self, widget, event):
        """
        Handle the button-release-event generated by the eventbox
        parent of the subpixmap.  Crop the picture accordingly.
        """

        # reset the crop on double-click or click+CTRL
        if (event.button==1 and event.type == gtk.gdk._2BUTTON_PRESS) or \
            (event.button==1 and (event.state & gtk.gdk.CONTROL_MASK) ):
            self.corner1_x_spinbutton.set_value(0)
            self.corner1_y_spinbutton.set_value(0)
            self.corner2_x_spinbutton.set_value(100)
            self.corner2_y_spinbutton.set_value(100)

        else:

            # ensure the clicks happened at least 5 pixels away from each other
            new_x1 = min(self.button_press_coords[0], event.x)
            new_y1 = min(self.button_press_coords[1], event.y)
            new_x2 = max(self.button_press_coords[0], event.x)
            new_y2 = max(self.button_press_coords[1], event.y)

            if new_x2 - new_x1 >= 5 and new_y2 - new_y1 >= 5:

                # get the image size and calculate the X and Y offsets
                # (image is centered when smaller than const.THUMBSCALE)
                pixbuf = self.subpixmap.get_pixbuf();
                w = pixbuf.get_width()
                h = pixbuf.get_height()
                x = (const.THUMBSCALE - w) / 2
                y = (const.THUMBSCALE - h) / 2

                # if the click was outside of the image,
                # bring it within the boundaries
                if new_x1 < x:
                    new_x1 = x
                if new_y1 < y:
                    new_y1 = y
                if new_x2 >= x + w:
                    new_x2 = x + w - 1
                if new_y2 >= y + h:
                    new_y2 = y + h - 1

                # get the old spinbutton % values
                old_x1 = self.corner1_x_spinbutton.get_value()
                old_y1 = self.corner1_y_spinbutton.get_value()
                old_x2 = self.corner2_x_spinbutton.get_value()
                old_y2 = self.corner2_y_spinbutton.get_value()
                delta_x = old_x2 - old_x1   # horizontal scale
                delta_y = old_y2 - old_y1   # vertical scale

                # Took a while to figure out the math here.
                #
                #   1)  figure out the current crop % values
                #       by doing the following:
                #
                #           xp = click_location_x / width * 100
                #           yp = click_location_y / height * 100
                #
                #       but remember that click_location_x and _y
                #       might not be zero-based for non-rectangular
                #       images, so subtract the pixbuf "x" and "y"
                #       to bring the values back to zero-based
                #
                #   2)  the minimum value cannot be less than the
                #       existing crop value, so add the current
                #       minimum to the new values

                new_x1 = old_x1 + delta_x * (new_x1 - x) / w
                new_y1 = old_y1 + delta_y * (new_y1 - y) / h
                new_x2 = old_x1 + delta_x * (new_x2 - x) / w
                new_y2 = old_y1 + delta_y * (new_y2 - y) / h

                # set the new values
                self.corner1_x_spinbutton.set_value(new_x1)
                self.corner1_y_spinbutton.set_value(new_y1)
                self.corner2_x_spinbutton.set_value(new_x2)
                self.corner2_y_spinbutton.set_value(new_y2)

    def _update_addmedia(self, obj):
        """
        Called when the add media dialog has been called.
        This allows us to update the main form in response to
        any changes: Redraw relevant fields: description, mimetype and path
        """
        for obj in (self.descr_window, self.path_obj):
            obj.update()
        self.draw_preview()

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object('button84'))
        self.define_ok_button(self.top.get_object('button82'),self.save)

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected. 
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('media-rebuild', self.close)
        self._add_db_signal('media-delete', self.check_for_close)

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.
        """
        notebook_ref = self.top.get_object('notebook_ref')
        notebook_src = self.top.get_object('notebook_shared')

        self._add_tab(notebook_src, self.primtab)
        self._add_tab(notebook_ref, self.reftab)

        self.srcref_list = self._add_tab(
            notebook_ref,
            SourceEmbedList(self.dbstate,self.uistate,self.track,
                            self.source_ref))

        self.attr_list = self._add_tab(
            notebook_ref,
            AttrEmbedList(self.dbstate,self.uistate,self.track,
                          self.source_ref.get_attribute_list()))

        self.backref_list = self._add_tab(
            notebook_src,
            MediaBackRefList(self.dbstate,self.uistate,self.track,
                             self.db.find_backlink_handles(self.source.handle),
                             self.enable_warnbox
                             ))

        self.note_ref_tab = self._add_tab(
            notebook_ref,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.source_ref.get_note_list(),
                    notetype=NoteType.MEDIAREF))

        self.src_srcref_list = self._add_tab(
            notebook_src,
            SourceEmbedList(self.dbstate,self.uistate,self.track,
                            self.source))

        self.src_attr_list = self._add_tab(
            notebook_src,
            AttrEmbedList(self.dbstate,self.uistate,self.track,
                          self.source.get_attribute_list()))

        self.src_note_ref_tab = self._add_tab(
            notebook_src,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.source.get_note_list(),
                    notetype=NoteType.MEDIA))

        self._setup_notebook_tabs(notebook_src)
        self._setup_notebook_tabs(notebook_ref)

    def save(self,*obj):
        #first save primary object
        trans = self.db.transaction_begin()
        if self.source.handle:
            self.db.commit_media_object(self.source, trans)
            self.db.transaction_commit(trans, _("Edit Media Object (%s)"
                                           ) % self.source.get_description())
        else:
            self.db.add_object(self.source, trans)
            self.db.transaction_commit(trans,_("Add Media Object (%s)"
                                           ) % self.source.get_description())

        #save reference object in memory
        coord = (
            self.top.get_object("corner1_x").get_value_as_int(),
            self.top.get_object("corner1_y").get_value_as_int(),
            self.top.get_object("corner2_x").get_value_as_int(),
            self.top.get_object("corner2_y").get_value_as_int(),
            )

        #do not set unset or invalid coord

        if coord is not None and coord in (
                (None,)*4,  
                (0, 0, 100, 100),
                (coord[0], coord[1])*2
            ):
            coord = None

        self.source_ref.set_rectangle(coord)

        #call callback if given
        if self.update:
            self.update(self.source_ref,self.source)

        self.close()
