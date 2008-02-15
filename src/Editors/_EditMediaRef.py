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
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

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
import const
import Config
import Mime
import ThumbNails
from gen.lib import NoteType

from DisplayTabs import \
     SourceEmbedList,AttrEmbedList,MediaBackRefList,NoteTab
from GrampsWidgets import *
from _EditReference import RefTab, EditReference
from AddMedia import AddMediaObject

#-------------------------------------------------------------------------
#
# EditMediaRef
#
#-------------------------------------------------------------------------
class EditMediaRef(EditReference):

    WIDTH_KEY = Config.MEDIA_REF_WIDTH
    HEIGHT_KEY = Config.MEDIA_REF_HEIGHT

    def __init__(self, state, uistate, track, media, media_ref, update):
        EditReference.__init__(self, state, uistate, track, media,
                               media_ref, update)
        if not self.source.get_handle():
            #show the addmedia dialog immediately, with track of parent.
            AddMediaObject(state, self.uistate, self.track, self.source, 
                           self._update_addmedia)

    def _local_init(self):

        self.top = gtk.glade.XML(const.GLADE_FILE,
                                 "change_description","gramps")

        self.set_window(self.top.get_widget('change_description'),
                        self.top.get_widget('title'),
                        _('Media Reference Editor'))
        self.define_warn_box(self.top.get_widget("warn_box"))

        tblref =  self.top.get_widget('table50')
        notebook = self.top.get_widget('notebook_ref')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.reftab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('General'), tblref)
        tblref =  self.top.get_widget('table2')
        notebook = self.top.get_widget('notebook_shared')
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
        self.pix = ThumbNails.get_thumbnail_image(self.source.get_path(),
                                                  self.mtype)
        self.pixmap.set_from_pixbuf(self.pix)
        
        self.subpix = ThumbNails.get_thumbnail_image(self.source.get_path(),
                                                     self.mtype,
                                                     self.rectangle)
        self.subpixmap.set_from_pixbuf(self.subpix)

        mt = Mime.get_description(self.mtype)
        if mt:
            self.top.get_widget("type").set_text(mt)
        else:
            self.top.get_widget("type").set_text("")

    def _setup_fields(self):
        ebox = self.top.get_widget('eventbox')
        ebox.connect('button-press-event', self.button_press_event)
        
        self.pixmap = self.top.get_widget("pixmap")
        
        coord = self.source_ref.get_rectangle()
        #upgrade path: set invalid (from eg old db) to none
        if coord is not None and ((coord[0] == None and coord[1] == None
                and coord[2] == None and coord[3] == None) or (
            coord[0] == 0 and coord[1] == 0
                and coord[2] == 100 and coord[3] == 100) or (
            coord[0] == coord[2] and coord[1] == coord[3]
           )):
            coord = None
        self.rectangle = coord
        self.subpixmap = self.top.get_widget("subpixmap")

        self.draw_preview()

        if coord and type(coord) == tuple:
            self.top.get_widget("corner1_x").set_value(coord[0])
            self.top.get_widget("corner1_y").set_value(coord[1])
            self.top.get_widget("corner2_x").set_value(coord[2])
            self.top.get_widget("corner2_y").set_value(coord[3])
        else:
            self.top.get_widget("corner1_x").set_value(0)
            self.top.get_widget("corner1_y").set_value(0)
            self.top.get_widget("corner2_x").set_value(100)
            self.top.get_widget("corner2_y").set_value(100)
            
        if self.dbstate.db.readonly:
            self.top.get_widget("corner1_x").set_sensitive(False)
            self.top.get_widget("corner1_y").set_sensitive(False)
            self.top.get_widget("corner2_x").set_sensitive(False)
            self.top.get_widget("corner2_y").set_sensitive(False)
        
        self.corner1_x_spinbutton = MonitoredSpinButton(
            self.top.get_widget("corner1_x"),
            self.set_corner1_x,
            self.get_corner1_x,
            self.db.readonly)

        self.corner1_y_spinbutton = MonitoredSpinButton(
            self.top.get_widget("corner1_y"),
            self.set_corner1_y,
            self.get_corner1_y,
            self.db.readonly)

        self.corner2_x_spinbutton = MonitoredSpinButton(
            self.top.get_widget("corner2_x"),
            self.set_corner2_x,
            self.get_corner2_x,
            self.db.readonly)

        self.corner2_y_spinbutton = MonitoredSpinButton(
            self.top.get_widget("corner2_y"),
            self.set_corner2_y,
            self.get_corner2_y,
            self.db.readonly)

        self.descr_window = MonitoredEntry(
            self.top.get_widget("description"),
            self.source.set_description,
            self.source.get_description,
            self.db.readonly)

        self.ref_privacy = PrivacyButton(
            self.top.get_widget("private"),
            self.source_ref,
            self.db.readonly)

        self.gid = MonitoredEntry(
            self.top.get_widget("gid"),
            self.source.set_gramps_id,
            self.source.get_gramps_id,
            self.db.readonly)

        self.privacy = PrivacyButton(
            self.top.get_widget("privacy"),
            self.source,
            self.db.readonly)

        self.path_obj = MonitoredEntry(
            self.top.get_widget("path"),
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
        
        if self.rectangle == None:
            self.rectangle = (0,0,100,100)
        self.rectangle = (value,
                          self.rectangle[1],
                          self.rectangle[2],
                          self.rectangle[3])
        self.update_subpixmap()

    def set_corner1_y(self, value):
        """
        Callback for the signal handling of the spinbutton for the first
        corner y coordinate of the subsection.
        Updates the subsection thumbnail using the given value
        
        @param value: the first corner y coordinate of the subsection in int
        """
        
        if self.rectangle == None:
            self.rectangle = (0,0,100,100)
        self.rectangle = (self.rectangle[0],
                          value,
                          self.rectangle[2],
                          self.rectangle[3])
        self.update_subpixmap()

    def set_corner2_x(self, value):
        """
        Callback for the signal handling of the spinbutton for the second
        corner x coordinate of the subsection.
        Updates the subsection thumbnail using the given value
        
        @param value: the second corner x coordinate of the subsection in int
        """
        
        if self.rectangle == None:
            self.rectangle = (0,0,100,100)
        self.rectangle = (self.rectangle[0],
                          self.rectangle[1],
                          value,
                          self.rectangle[3])
        self.update_subpixmap()

    def set_corner2_y(self, value):
        """
        Callback for the signal handling of the spinbutton for the second
        corner y coordinate of the subsection.
        Updates the subsection thumbnail using the given value
        
        @param value: the second corner y coordinate of the subsection in int
        """
        
        if self.rectangle == None:
            self.rectangle = (0,0,100,100)
        self.rectangle = (self.rectangle[0],
                          self.rectangle[1],
                          self.rectangle[2],
                          value)
        self.update_subpixmap()

    def get_corner1_x(self):
        """
        Callback for the signal handling of the spinbutton for the first corner 
        x coordinate of the subsection.
        
        @returns: the first corner x coordinate of the subsection or 0 if 
                  there is no selection
        """
        
        if self.rectangle != None:
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
         
        if self.rectangle != None:
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
        
        if self.rectangle != None:
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
        
        if self.rectangle != None:
            return self.rectangle[3]
        else:
            return 100

    def update_subpixmap(self):
        """
        Updates the thumbnail of the specified subsection
        """
        
        path = self.source.get_path()
        if path == None:
            self.subpixmap.hide()
        else:
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file(path)
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
        Provides the information needed by the base class to define the
        window management menu entries.
        """
        if self.source:
            submenu_label = _('Media: %s')  % self.source.get_gramps_id()
        else:
            submenu_label = _('New Media')
        return (_('Media Reference Editor'),submenu_label)
    
    def button_press_event(self, obj, event):
        if event.button==1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.view_media(obj)

    def _update_addmedia(self, obj):
        """
        Called when the add media dialog has been called.
        This allows us to update the main form in response to
        any changes: Redraw relevant fields: description, mimetype and path
        """
        for obj in (self.descr_window, self.path_obj):
            obj.update()
        self.draw_preview()

    def view_media(self, obj):
        mime_type = self.source.get_mime_type()
        app = Mime.get_application(mime_type)
        if app:
            import Utils
            Utils.launch(app[0],self.source.get_path())

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_widget('button84'))
        self.define_ok_button(self.top.get_widget('button82'),self.save)

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        """
        notebook_ref = self.top.get_widget('notebook_ref')
        notebook_src = self.top.get_widget('notebook_shared')

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
            self.top.get_widget("corner1_x").get_value_as_int(),
            self.top.get_widget("corner1_y").get_value_as_int(),
            self.top.get_widget("corner2_x").get_value_as_int(),
            self.top.get_widget("corner2_y").get_value_as_int(),
            )
        #do not set unset or invalid coord
        if (coord[0] == None and coord[1] == None
                and coord[2] == None and coord[3] == None) or (
            coord[0] == 0 and coord[1] == 0
                and coord[2] == 100 and coord[3] == 100) or (
            coord[0] == coord[2] and coord[1] == coord[3]
           ):
            coord = None
        self.source_ref.set_rectangle(coord)

        #call callback if given
        if self.update:
            self.update(self.source_ref,self.source)

        self.close()
