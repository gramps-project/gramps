#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2008-2009  Stephane Charette <stephanecharette@gmail.com>
#               2009       Gary Burton
#               2011       Robert Cheramy <robert@cheramy.net>
# Copyright (C) 2011       Tim G L Lyons
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
from gramps.gen.ggettext import sgettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GdkPixbuf
from gi.repository import Gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gui.utils import open_file_with_default_application
from gramps.gen.const import THUMBSCALE
from gramps.gen.mime import get_description, get_type
from gramps.gui.thumbnails import get_thumbnail_image, find_mime_type_pixbuf
from gramps.gen.utils.file import (media_path_full, find_file, 
                            get_unicode_path_from_file_chooser)
from gramps.gen.lib import NoteType
from gramps.gen.db import DbTxn
from gramps.gui.glade import Glade
from displaytabs import (CitationEmbedList, AttrEmbedList, MediaBackRefList, 
                         NoteTab)
from gramps.gui.widgets import (MonitoredSpinButton, MonitoredEntry, PrivacyButton,
                         MonitoredDate, MonitoredTagList)
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
        self.notebook_ref = self.top.get_object('notebook_ref')
        self.track_ref_for_deletion("notebook_ref")
        #recreate start page as GrampsTab
        self.notebook_ref.remove_page(0)
        self.reftab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('General'), tblref)
        self.track_ref_for_deletion("reftab")
        tblref =  self.top.get_object('table2')
        self.notebook_shared = self.top.get_object('notebook_shared')
        #recreate start page as GrampsTab
        self.notebook_shared.remove_page(0)
        self.track_ref_for_deletion("notebook_shared")
        self.primtab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('_General'), tblref)
        self.track_ref_for_deletion("primtab")
        self.rect_pixbuf = None

    def setup_filepath(self):
        self.select = self.top.get_object('file_select')
        self.track_ref_for_deletion("select")
        self.file_path = self.top.get_object("path")
        self.track_ref_for_deletion("file_path")

        self.file_path.set_text(self.source.get_path())
        self.select.connect('clicked', self.select_file)

    def determine_mime(self):
        descr = get_description(self.source.get_mime_type())
        if descr:
            self.mimetext.set_text(descr)

        path = self.file_path.get_text()
        path_full = media_path_full(self.db, path)
        if path != self.source.get_path() and path_full != self.source.get_path():
            #redetermine mime
            mime = get_type(find_file(path_full))
            self.source.set_mime_type(mime)
            descr = get_description(mime)
            if descr:
                self.mimetext.set_text(descr)
            else:
                self.mimetext.set_text(_('Unknown'))
        #if mime type not set, is note
        if not self.source.get_mime_type():
            self.mimetext.set_text(_('Note'))

    def draw_preview(self):
        """
        Draw the two preview images. This method can be called on eg change of
        the path.
        """
        mtype = self.source.get_mime_type()
        if mtype:
            fullpath = media_path_full(self.db, self.source.get_path())
            pb = get_thumbnail_image(fullpath, mtype)
            self.pixmap.set_from_pixbuf(pb)
            subpix = get_thumbnail_image(fullpath, mtype,
                                                    self.rectangle)
            self.subpixmap.set_from_pixbuf(subpix)
        else:
            pb = find_mime_type_pixbuf('text/plain')
            self.pixmap.set_from_pixbuf(pb)
            self.subpixmap.set_from_pixbuf(pb)

    def _setup_fields(self):
        
        ebox_shared = self.top.get_object('eventbox')
        ebox_shared.connect('button-press-event', self.button_press_event)

        if not self.dbstate.db.readonly:
            self.button_press_coords = (0, 0)
            ebox_ref = self.top.get_object('eventbox1')
            ebox_ref.connect('button-press-event', self.button_press_event_ref)
            ebox_ref.connect('button-release-event', 
                                                 self.button_release_event_ref)
            ebox_ref.connect('motion-notify-event', self.motion_notify_event_ref)
            ebox_ref.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            ebox_ref.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)

        self.pixmap = self.top.get_object("pixmap")
        self.mimetext = self.top.get_object("type")
        self.track_ref_for_deletion("mimetext")
        
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
        self.track_ref_for_deletion("subpixmap")

        self.setup_filepath()
        self.determine_mime()
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
        self.track_ref_for_deletion("corner1_x_spinbutton")

        self.corner1_y_spinbutton = MonitoredSpinButton(
            self.top.get_object("corner1_y"),
            self.set_corner1_y,
            self.get_corner1_y,
            self.db.readonly)
        self.track_ref_for_deletion("corner1_y_spinbutton")

        self.corner2_x_spinbutton = MonitoredSpinButton(
            self.top.get_object("corner2_x"),
            self.set_corner2_x,
            self.get_corner2_x,
            self.db.readonly)
        self.track_ref_for_deletion("corner2_x_spinbutton")

        self.corner2_y_spinbutton = MonitoredSpinButton(
            self.top.get_object("corner2_y"),
            self.set_corner2_y,
            self.get_corner2_y,
            self.db.readonly)
        self.track_ref_for_deletion("corner2_y_spinbutton")

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
            
        self.date_field = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_edit"),
            self.source.get_date_object(),
            self.uistate, self.track,
            self.db.readonly)
            
        self.tags = MonitoredTagList(
            self.top.get_object("tag_label"), 
            self.top.get_object("tag_button"), 
            self.source.set_tag_list, 
            self.source.get_tag_list,
            self.db,
            self.uistate, self.track,
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
                fullpath = media_path_full(self.db, path)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(fullpath)
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
                scale = THUMBSCALE / ratio
                x = int(scale * width)
                y = int(scale * height)
                pixbuf = pixbuf.scale_simple(x, y, GdkPixbuf.InterpType.BILINEAR)
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
        if event.button==1 and event.type == Gdk.EventType._2BUTTON_PRESS:
            photo_path = media_path_full(self.db, self.source.get_path())
            open_file_with_default_application(photo_path)

    def button_press_event_ref(self, widget, event):
        """
        Handle the button-press-event generated by the eventbox
        parent of the subpixmap.  Remember these coordinates
        so we can crop the picture when button-release-event
        is received.
        """
        self.button_press_coords = (event.x, event.y)
        # prepare drawing of a feedback rectangle
        self.rect_pixbuf = self.subpixmap.get_pixbuf()
        w,h = self.rect_pixbuf.get_width(), self.rect_pixbuf.get_height()
        self.rect_pixbuf_render = GdkPixbuf.Pixbuf(GdkPixbuf.Colorspace.RGB, False, 8, w, h)
        cm = Gdk.colormap_get_system()
        color = cm.alloc_color(Gdk.Color("blue"))
        self.rect_pixmap = Gdk.Pixmap(None, w, h, cm.get_visual().depth)
        self.rect_pixmap.set_colormap(cm)
        self.rect_gc = self.rect_pixmap.new_gc()
        self.rect_gc.set_foreground(color)
 
    def motion_notify_event_ref(self, widget, event):
        # get the image size and calculate the X and Y offsets
        # (image is centered *horizontally* when smaller than THUMBSCALE)
        w, h = self.rect_pixbuf.get_width(), self.rect_pixbuf.get_height()
        offset_x = (THUMBSCALE - w) / 2
        offset_y = 0

        self.rect_pixmap.draw_pixbuf(self.rect_gc, self.rect_pixbuf, 0, 0, 0, 0)
        
        # get coordinates of the rectangle, so that x1 < x2 and y1 < y2
        x1 = min(self.button_press_coords[0], event.x)
        x2 = max(self.button_press_coords[0], event.x)
        y1 = min(self.button_press_coords[1], event.y)
        y2 = max(self.button_press_coords[1], event.y)

        width = int(x2 - x1)
        height = int(y2 - y1)
        x1 = int(x1 - offset_x)
        y1 = int(y1 - offset_y)
        
        self.rect_pixmap.draw_rectangle(self.rect_gc, False,
                    x1, y1, width, height)
                    
        self.rect_pixbuf_render.get_from_drawable(self.rect_pixmap,
                                Gdk.colormap_get_system(),
                                0,0,0,0, w, h)
        self.subpixmap.set_from_pixbuf(self.rect_pixbuf_render)

    def button_release_event_ref(self, widget, event):
        """
        Handle the button-release-event generated by the eventbox
        parent of the subpixmap.  Crop the picture accordingly.
        """

        # reset the crop on double-click or click+CTRL
        if (event.button==1 and event.type == Gdk.EventType._2BUTTON_PRESS) or \
            (event.button==1 and (event.get_state() & Gdk.ModifierType.CONTROL_MASK) ):
            self.corner1_x_spinbutton.set_value(0)
            self.corner1_y_spinbutton.set_value(0)
            self.corner2_x_spinbutton.set_value(100)
            self.corner2_y_spinbutton.set_value(100)

        else:
            if (self.rect_pixbuf == None):
                return
            self.subpixmap.set_from_pixbuf(self.rect_pixbuf)

            # ensure the clicks happened at least 5 pixels away from each other
            new_x1 = min(self.button_press_coords[0], event.x)
            new_y1 = min(self.button_press_coords[1], event.y)
            new_x2 = max(self.button_press_coords[0], event.x)
            new_y2 = max(self.button_press_coords[1], event.y)

            if new_x2 - new_x1 >= 5 and new_y2 - new_y1 >= 5:

                # get the image size and calculate the X and Y offsets
                # (image is centered *horizontally* when smaller than THUMBSCALE)
                w = self.rect_pixbuf.get_width()
                h = self.rect_pixbuf.get_height()
                x = (THUMBSCALE - w) / 2
                y = 0

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

                # Free the pixbuf as it is not needed anymore
                self.rect_pixbuf = None

    def _update_addmedia(self, obj):
        """
        Called when the add media dialog has been called.
        This allows us to update the main form in response to
        any changes: Redraw relevant fields: description, mimetype and path
        """
        for obj in (self.descr_window, self.path_obj):
            obj.update()
        self.determine_mime()
        self.draw_preview()

    def select_file(self, val):
        self.determine_mime()
        path = self.file_path.get_text()
        self.source.set_path(get_unicode_path_from_file_chooser(path))
        AddMediaObject(self.dbstate, self.uistate, self.track, self.source, 
                       self._update_addmedia)

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

        self.srcref_list = CitationEmbedList(self.dbstate,
                                         self.uistate,
                                         self.track,
                                         self.source_ref.get_citation_list())
        self._add_tab(notebook_ref, self.srcref_list)
        self.track_ref_for_deletion("srcref_list")

        self.attr_list = AttrEmbedList(self.dbstate,self.uistate,self.track,
                                       self.source_ref.get_attribute_list())
        self._add_tab(notebook_ref, self.attr_list)
        self.track_ref_for_deletion("attr_list")

        self.backref_list = MediaBackRefList(self.dbstate,self.uistate,self.track,
                             self.db.find_backlink_handles(self.source.handle),
                             self.enable_warnbox
                             )
        self._add_tab(notebook_src, self.backref_list)
        self.track_ref_for_deletion("backref_list")

        self.note_ref_tab = NoteTab(self.dbstate, self.uistate, self.track,
                                    self.source_ref.get_note_list(),
                                    notetype=NoteType.MEDIAREF)
        self._add_tab(notebook_ref, self.note_ref_tab)
        self.track_ref_for_deletion("note_ref_tab")

        self.src_srcref_list = CitationEmbedList(self.dbstate,
                                             self.uistate,
                                             self.track, 
                                             self.source.get_citation_list())
        self._add_tab(notebook_src, self.src_srcref_list)
        self.track_ref_for_deletion("src_srcref_list")

        self.src_attr_list = AttrEmbedList(self.dbstate,self.uistate,self.track,
                                           self.source.get_attribute_list())
        self._add_tab(notebook_src, self.src_attr_list)
        self.track_ref_for_deletion("src_attr_list")

        self.src_note_ref_tab = NoteTab(self.dbstate, self.uistate, self.track,
                                        self.source.get_note_list(),
                                        notetype=NoteType.MEDIA)
        self._add_tab(notebook_src, self.src_note_ref_tab)
        self.track_ref_for_deletion("src_note_ref_tab")

        self._setup_notebook_tabs(notebook_src)
        self._setup_notebook_tabs(notebook_ref)

    def save(self,*obj):
        #first save primary object
        if self.source.handle:
            with DbTxn(_("Edit Media Object (%s)") %
                       self.source.get_description(), self.db) as trans:
                self.db.commit_media_object(self.source, trans)
        else:
            with DbTxn(_("Add Media Object (%s)") % 
                       self.source.get_description(), self.db) as trans:
                self.db.add_object(self.source, trans)

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
            self.update = None
        self.close()
