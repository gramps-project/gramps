#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2008-2009  Stephane Charette <stephanecharette@gmail.com>
#               2009       Gary Burton
#               2011       Robert Cheramy <robert@cheramy.net>
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013       Nick Hall
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
# Standard python modules
#
#-------------------------------------------------------------------------
import os
from copy import deepcopy

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
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from ..utils import open_file_with_default_application
from gramps.gen.const import THUMBSCALE
from gramps.gen.mime import get_description, get_type
from gramps.gen.utils.thumbnails import get_thumbnail_image, find_mime_type_pixbuf
from gramps.gen.utils.file import (media_path_full, find_file, create_checksum)
from gramps.gen.lib import NoteType
from gramps.gen.db import DbTxn
from ..glade import Glade
from .displaytabs import (CitationEmbedList, MediaAttrEmbedList, MediaBackRefList,
                         NoteTab)
from ..widgets import (MonitoredSpinButton, MonitoredEntry, PrivacyButton,
                       MonitoredDate, MonitoredTagList, SelectionWidget, Region)
from .editreference import RefTab, EditReference
from .addmedia import AddMedia
from gramps.gen.const import URL_MANUAL_SECT2

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT2
WIKI_HELP_SEC = _('Media_Reference_Editor_dialog', 'manual')

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
            AddMedia(state, self.uistate, self.track, self.source,
                     self._update_addmedia)
        else:
            self.original = deepcopy(self.source.serialize())

    def _local_init(self):

        self.top = Glade()
        self.set_window(self.top.toplevel,
                        self.top.get_object('title'),
                        _('Media Reference Editor'))
        self.setup_configs('interface.media-ref', 600, 450)

        self.define_warn_box(self.top.get_object("warn_box"))
        self.top.get_object("label427").set_text(_("Y", "Y coordinate"))
        self.top.get_object("label428").set_text(_("Y", "Y coordinate"))

        tblref = self.top.get_object('table50')
        self.notebook_ref = self.top.get_object('notebook_ref')
        self.track_ref_for_deletion("notebook_ref")
        self.expander = self.top.get_object('expander1')
        #recreate start page as GrampsTab
        self.notebook_ref.remove_page(0)
        self.reftab = RefTab(self.dbstate, self.uistate, self.track,
                              _('General'), tblref)
        self.track_ref_for_deletion("reftab")
        tblref = self.top.get_object('table2')
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
            self.selection.load_image(fullpath)
        else:
            pb = find_mime_type_pixbuf('text/plain')
            self.pixmap.set_from_pixbuf(pb)
            self.selection.load_image('')

    def _setup_fields(self):

        ebox_shared = self.top.get_object('eventbox')
        ebox_shared.connect('button-press-event', self.button_press_event)
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

        if coord is not None:
            self.rectangle = coord
        else:
            self.rectangle = (0, 0, 100, 100)

        self.selection = SelectionWidget()
        self.selection.set_multiple_selection(False)
        self.selection.connect("region-modified", self.region_modified)
        self.selection.connect("region-created", self.region_modified)
        self.expander.connect("activate", self.selection.expander)
        frame = self.top.get_object("frame9")
        frame.add(self.selection)
        self.track_ref_for_deletion("selection")
        self.selection.show()

        self.setup_filepath()
        self.determine_mime()

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

    def _post_init(self):
        """
        Initialization that must happen after the window is shown.
        """
        self.draw_preview()
        self.update_region()

    def set_corner1_x(self, value):
        """
        Callback for the signal handling of the spinbutton for the first
        corner x coordinate of the subsection.
        Updates the subsection thumbnail using the given value

        @param value: the first corner x coordinate of the subsection in int
        """

        self.rectangle = (value,) + self.rectangle[1:]
        self.update_region()

    def set_corner1_y(self, value):
        """
        Callback for the signal handling of the spinbutton for the first
        corner y coordinate of the subsection.
        Updates the subsection thumbnail using the given value

        @param value: the first corner y coordinate of the subsection in int
        """

        self.rectangle = self.rectangle[:1] + (value,) + self.rectangle[2:]
        self.update_region()

    def set_corner2_x(self, value):
        """
        Callback for the signal handling of the spinbutton for the second
        corner x coordinate of the subsection.
        Updates the subsection thumbnail using the given value

        @param value: the second corner x coordinate of the subsection in int
        """

        self.rectangle = self.rectangle[:2] + (value,) + self.rectangle[3:]
        self.update_region()

    def set_corner2_y(self, value):
        """
        Callback for the signal handling of the spinbutton for the second
        corner y coordinate of the subsection.
        Updates the subsection thumbnail using the given value

        @param value: the second corner y coordinate of the subsection in int
        """

        self.rectangle = self.rectangle[:3] + (value,)
        self.update_region()

    def get_corner1_x(self):
        """
        Callback for the signal handling of the spinbutton for the first corner
        x coordinate of the subsection.

        @returns: the first corner x coordinate of the subsection or 0 if
                  there is no selection
        """
        return self.rectangle[0]

    def get_corner1_y(self):
        """
        Callback for the signal handling of the spinbutton for the first corner
        y coordinate of the subsection.

        @returns: the first corner y coordinate of the subsection or 0 if
                  there is no selection
        """
        return self.rectangle[1]

    def get_corner2_x(self):
        """
        Callback for the signal handling of the spinbutton for the second
        corner x coordinate of the subsection.

        @returns: the second corner x coordinate of the subsection or 100 if
                  there is no selection
        """
        return self.rectangle[2]

    def get_corner2_y(self):
        """
        Callback for the signal handling of the spinbutton for the second
        corner x coordinate of the subsection.

        @returns: the second corner x coordinate of the subsection or 100 if
                  there is no selection
        """
        return self.rectangle[3]

    def update_region(self):
        """
        Updates the thumbnail of the specified subsection.
        """
        if not self.selection.is_image_loaded():
            return
        real = self.selection.proportional_to_real_rect(self.rectangle)
        region = Region(real[0], real[1], real[2], real[3])
        self.selection.set_regions([region])
        self.selection.select(region)  # update the selection box shown
        self.selection.refresh()

    def region_modified(self, widget):
        """
        Update new values when the selection is changed.
        """
        real = self.selection.get_selection()
        coords = self.selection.real_to_proportional_rect(real)
        self.corner1_x_spinbutton.set_value(coords[0])
        self.corner1_y_spinbutton.set_value(coords[1])
        self.corner2_x_spinbutton.set_value(coords[2])
        self.corner2_y_spinbutton.set_value(coords[3])

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
        if (event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS
                and event.button == 1):
            photo_path = media_path_full(self.db, self.source.get_path())
            open_file_with_default_application(photo_path, self.uistate)

    def _update_addmedia(self, obj):
        """
        Called when the add media dialog has been called.
        This allows us to update the main form in response to
        any changes: Redraw relevant fields: description, mimetype and path
        """
        for obj in (self.descr_window, self.path_obj):
            obj.update()
        self.determine_mime()
        self.update_checksum()
        self.draw_preview()

    def update_checksum(self):
        self.uistate.set_busy_cursor(True)
        media_path = media_path_full(self.dbstate.db, self.source.get_path())
        self.source.set_checksum(create_checksum(os.path.normpath(media_path)))
        self.uistate.set_busy_cursor(False)

    def select_file(self, val):
        self.determine_mime()
        path = self.file_path.get_text()
        self.source.set_path(path)
        AddMedia(self.dbstate, self.uistate, self.track, self.source,
                       self._update_addmedia)

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object('button84'))
        self.define_ok_button(self.top.get_object('button82'),self.save)
        # TODO help button (rename glade button name)
        self.define_help_button(self.top.get_object('button104'),
                WIKI_HELP_PAGE, WIKI_HELP_SEC)

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

        self.attr_list = MediaAttrEmbedList(self.dbstate,self.uistate,self.track,
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

        self.src_attr_list = MediaAttrEmbedList(self.dbstate,self.uistate,self.track,
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
            # only commit if it has changed
            if self.source.serialize() != self.original:
                with DbTxn(_("Edit Media Object (%s)") %
                           self.source.get_description(), self.db) as trans:
                    self.db.commit_media(self.source, trans)
        else:
            if self.check_for_duplicate_id('Media'):
                return
            with DbTxn(_("Add Media Object (%s)") %
                       self.source.get_description(), self.db) as trans:
                self.db.add_media(self.source, trans)

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
