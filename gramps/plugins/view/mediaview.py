# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2010       Nick Hall
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Media View.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
import os
from urllib.parse import urlparse
from urllib.request import url2pathname
import pickle

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gui.utils import open_file_with_default_application
from gramps.gui.views.listview import ListView, TEXT, MARKUP, ICON
from gramps.gui.views.treemodels import MediaModel
from gramps.gen.config import config
from gramps.gen.utils.file import (
    media_path,
    relative_path,
    media_path_full,
    create_checksum,
)
from gramps.gui.views.bookmarks import MediaBookmarks
from gramps.gen.mime import get_type, is_valid_type
from gramps.gen.lib import Media
from gramps.gen.db import DbTxn
from gramps.gui.editors import EditMedia
from gramps.gen.errors import WindowActiveError
from gramps.gui.filters.sidebar import MediaSidebarFilter
from gramps.gui.merge import MergeMedia
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import ErrorDialog
from gramps.gen.plug import CATEGORY_QR_MEDIA


# -------------------------------------------------------------------------
#
# MediaView
#
# -------------------------------------------------------------------------
class MediaView(ListView):
    """
    Provide the Media View interface on the Gramps main window. This allows
    people to manage all media items in their database. This is very similar
    to the other list based views, with the exception that it also has a
    thumbnail image at the top of the view that must be updated when the
    selection changes or when the selected media object changes.
    """

    COL_TITLE = 0
    COL_ID = 1
    COL_TYPE = 2
    COL_PATH = 3
    COL_DATE = 4
    COL_PRIV = 5
    COL_TAGS = 6
    COL_CHAN = 7

    # column definitions
    COLUMNS = [
        (_("Title"), TEXT, None),
        (_("ID"), TEXT, None),
        (_("Type"), TEXT, None),
        (_("Path"), TEXT, None),
        (_("Date"), TEXT, None),
        (_("Private"), ICON, "gramps-lock"),
        (_("Tags"), TEXT, None),
        (_("Last Changed"), TEXT, None),
    ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ("columns.visible", [COL_TITLE, COL_ID, COL_TYPE, COL_PATH, COL_DATE]),
        (
            "columns.rank",
            [
                COL_TITLE,
                COL_ID,
                COL_TYPE,
                COL_PATH,
                COL_DATE,
                COL_PRIV,
                COL_TAGS,
                COL_CHAN,
            ],
        ),
        ("columns.size", [200, 75, 100, 200, 150, 40, 100, 150]),
    )

    ADD_MSG = _("Add a new media object")
    EDIT_MSG = _("Edit the selected media object")
    DEL_MSG = _("Delete the selected media object")
    MERGE_MSG = _("Merge the selected media objects")
    FILTER_TYPE = "Media"
    QR_CATEGORY = CATEGORY_QR_MEDIA

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        signal_map = {
            "media-add": self.row_add,
            "media-update": self.row_update,
            "media-delete": self.row_delete,
            "media-rebuild": self.object_build,
        }

        ListView.__init__(
            self,
            _("Media"),
            pdata,
            dbstate,
            uistate,
            MediaModel,
            signal_map,
            MediaBookmarks,
            nav_group,
            filter_class=MediaSidebarFilter,
            multiple=True,
        )

        self.additional_uis.append(self.additional_ui)
        self.uistate = uistate

    def navigation_type(self):
        return "Media"

    def drag_info(self):
        """
        Return the type of DND targets that this view will accept. For Media
        View, we will accept media objects.
        """
        return DdTargets.MEDIAOBJ

    def drag_dest_info(self):
        """
        Specify the drag type for objects dropped on the view
        """
        return DdTargets.URI_LIST

    def find_index(self, obj):
        """
        returns the index of the object within the associated data
        """
        return self.model.indexlist[obj]

    def drag_data_received(self, widget, context, x, y, sel_data, info, time):
        """
        Handle the standard gtk interface for drag_data_received.

        If the selection data is define, extract the value from sel_data.data,
        and decide if this is a move or a reorder.
        The only data we accept on mediaview is dropping a file, so URI_LIST.
        We assume this is what we obtain
        """
        if not sel_data:
            return

        files = sel_data.get_uris()
        photo = None

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
                with DbTxn(_("Drag Media Object"), self.dbstate.db) as trans:
                    self.dbstate.db.add_media(photo, trans)

        if photo:
            self.uistate.set_active(photo.handle, "Media")

        widget.emit_stop_by_name("drag_data_received")

    def define_actions(self):
        """
        Defines the UIManager actions specific to Media View. We need to make
        sure that the common List View actions are defined as well, so we
        call the parent function.
        """
        ListView.define_actions(self)

        self._add_action("OpenMedia", self.view_media)
        self._add_action("OpenContainingFolder", self.open_containing_folder)

    def view_media(self, *obj):
        """
        Launch external viewers for the selected objects.
        """
        for handle in self.selected_handles():
            ref_obj = self.dbstate.db.get_media_from_handle(handle)
            mpath = media_path_full(self.dbstate.db, ref_obj.get_path())
            open_file_with_default_application(mpath, self.uistate)

    def open_containing_folder(self, *obj):
        """
        Launch external viewers for the selected objects.
        """
        for handle in self.selected_handles():
            ref_obj = self.dbstate.db.get_media_from_handle(handle)
            mpath = media_path_full(self.dbstate.db, ref_obj.get_path())
            if mpath:
                mfolder, mfile = os.path.split(mpath)
                open_file_with_default_application(mfolder, self.uistate)

    def get_stock(self):
        """
        Return the icon for this view
        """
        return "gramps-media"

    additional_ui = [  # Defines the UI string for UIManager
        """
      <placeholder id="LocalExport">
        <item>
          <attribute name="action">win.ExportTab</attribute>
          <attribute name="label" translatable="yes">Export View...</attribute>
        </item>
      </placeholder>
""",
        """
      <section id="AddEditBook">
        <item>
          <attribute name="action">win.AddBook</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.EditBook</attribute>
          <attribute name="label" translatable="no">%s...</attribute>
        </item>
      </section>
"""
        % _("Organize Bookmarks"),
        """
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">_Forward</attribute>
        </item>
      </section>
      </placeholder>
""",
        """
      <section id='CommonEdit' groups='RW'>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label">%s</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
        <item>
          <attribute name="action">win.Merge</attribute>
          <attribute name="label" translatable="yes">_Merge...</attribute>
        </item>
      </section>
"""
        % _("_Edit...", "action"),  # to use sgettext()
        """
        <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.FilterEdit</attribute>
          <attribute name="label" translatable="yes">"""
        """Media Filter Editor</attribute>
        </item>
        </placeholder>
""",  # Following are the Toolbar items
        """
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">"""
        """Go to the previous object in the history</property>
        <property name="label" translatable="yes">_Back</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-next</property>
        <property name="action-name">win.Forward</property>
        <property name="tooltip_text" translatable="yes">"""
        """Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
""",
        """
    <placeholder id='BarCommonEdit'>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">list-add</property>
        <property name="action-name">win.Add</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Add...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gtk-edit</property>
        <property name="action-name">win.Edit</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">Edit...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">list-remove</property>
        <property name="action-name">win.Remove</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Delete</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-merge</property>
        <property name="action-name">win.Merge</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Merge...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
"""
        % (ADD_MSG, EDIT_MSG, DEL_MSG, MERGE_MSG),
        """
    <placeholder id='MoreButtons'>
    <child>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-viewmedia</property>
        <property name="action-name">win.OpenMedia</property>
        <property name="tooltip_text" translatable="yes">"""
        """View in the default viewer</property>
        <property name="label" translatable="yes">View</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
""",
        """
    <menu id="Popup">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">Forward</attribute>
        </item>
      </section>
      <section id="PopUpTree">
        <item>
          <attribute name="action">win.OpenMedia</attribute>
          <attribute name="label" translatable="yes">View</attribute>
        </item>
        <item>
          <attribute name="action">win.OpenContainingFolder</attribute>
          <attribute name="label" translatable="yes">"""
        """Open Containing _Folder</attribute>
        </item>
      </section>
      <section>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label">%s</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
        <item>
          <attribute name="action">win.Merge</attribute>
          <attribute name="label" translatable="yes">_Merge...</attribute>
        </item>
      </section>
      <section>
        <placeholder id='QuickReport'>
        </placeholder>
      </section>
      <section>
        <placeholder id='AfterTools'>
        </placeholder>
      </section>
    </menu>
"""
        % _("_Edit...", "action"),  # to use sgettext()
    ]

    def add(self, *obj):
        """Add a new media object to the media list"""
        try:
            EditMedia(self.dbstate, self.uistate, [], Media())
        except WindowActiveError:
            pass

    def remove(self, *obj):
        handles = self.selected_handles()
        ht_list = [("Media", hndl) for hndl in handles]
        self.remove_selected_objects(ht_list)

    def edit(self, *obj):
        """
        Edit the selected objects in the EditMedia dialog
        """
        for handle in self.selected_handles():
            object = self.dbstate.db.get_media_from_handle(handle)
            try:
                EditMedia(self.dbstate, self.uistate, [], object)
            except WindowActiveError:
                pass

    def merge(self, *obj):
        """
        Merge the selected objects.
        """
        mlist = self.selected_handles()

        if len(mlist) != 2:
            msg = _("Cannot merge media objects.")
            msg2 = _(
                "Exactly two media objects must be selected to perform a "
                "merge. A second object can be selected by holding down the "
                "control key while clicking on the desired object."
            )
            ErrorDialog(msg, msg2, parent=self.uistate.window)
        else:
            MergeMedia(self.dbstate, self.uistate, [], mlist[0], mlist[1])

    def get_handle_from_gramps_id(self, gid):
        """
        returns the handle of the specified object
        """
        obj = self.dbstate.db.get_media_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def tag_updated(self, handle_list):
        """
        Update tagged rows when a tag color changes.
        """
        all_links = set([])
        for tag_handle in handle_list:
            links = set(
                [
                    link[1]
                    for link in self.dbstate.db.find_backlink_handles(
                        tag_handle, include_classes="Media"
                    )
                ]
            )
            all_links = all_links.union(links)
        self.row_update(list(all_links))

    def add_tag(self, transaction, media_handle, tag_handle):
        """
        Add the given tag to the given media object.
        """
        media = self.dbstate.db.get_media_from_handle(media_handle)
        media.add_tag(tag_handle)
        self.dbstate.db.commit_media(media, transaction)

    def remove_tag(self, transaction, media_handle, tag_handle):
        """
        Remove the given tag from the given media object.
        """
        media = self.dbstate.db.get_media_from_handle(media_handle)
        media.remove_tag(tag_handle)
        self.dbstate.db.commit_media(media, transaction)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (
            ("Media Filter",),
            (
                "Media Preview",
                "Media Citations",
                "Media Notes",
                "Media Attributes",
                "Metadata Viewer",
                "Media Backlinks",
            ),
        )

    def get_config_name(self):
        return __name__
