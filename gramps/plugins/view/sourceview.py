# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
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
Source View
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
import logging

LOG = logging.getLogger(".citation")

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Source
from gramps.gen.config import config
from gramps.gui.views.listview import ListView, TEXT, MARKUP, ICON
from gramps.gui.views.treemodels import SourceModel
from gramps.gui.views.bookmarks import SourceBookmarks
from gramps.gen.errors import WindowActiveError
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import ErrorDialog
from gramps.gui.editors import EditSource
from gramps.gui.filters.sidebar import SourceSidebarFilter
from gramps.gui.merge import MergeSource
from gramps.gen.plug import CATEGORY_QR_SOURCE
from gramps.plugins.lib.libsourceview import LibSourceView

# -------------------------------------------------------------------------
#
# internationalization
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# SourceView
#
# -------------------------------------------------------------------------
class SourceView(LibSourceView, ListView):
    """sources listview class"""

    COL_TITLE = 0
    COL_ID = 1
    COL_AUTH = 2
    COL_ABBR = 3
    COL_PINFO = 4
    COL_PRIV = 5
    COL_TAGS = 6
    COL_CHAN = 7

    # column definitions
    COLUMNS = [
        (_("Title"), TEXT, None),
        (_("ID"), TEXT, None),
        (_("Author"), TEXT, None),
        (_("Abbreviation"), TEXT, None),
        (_("Publication Information"), TEXT, None),
        (_("Private"), ICON, "gramps-lock"),
        (_("Tags"), TEXT, None),
        (_("Last Changed"), TEXT, None),
    ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ("columns.visible", [COL_TITLE, COL_ID, COL_AUTH, COL_PINFO]),
        (
            "columns.rank",
            [
                COL_TITLE,
                COL_ID,
                COL_AUTH,
                COL_ABBR,
                COL_PINFO,
                COL_PRIV,
                COL_TAGS,
                COL_CHAN,
            ],
        ),
        ("columns.size", [200, 75, 150, 100, 150, 40, 100, 100]),
    )
    ADD_MSG = _("Add a new source")
    EDIT_MSG = _("Edit the selected source")
    DEL_MSG = _("Delete the selected source")
    MERGE_MSG = _("Merge the selected sources")
    FILTER_TYPE = "Source"
    QR_CATEGORY = CATEGORY_QR_SOURCE

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        signal_map = {
            "source-add": self.row_add,
            "source-update": self.row_update,
            "source-delete": self.row_delete,
            "source-rebuild": self.object_build,
        }

        ListView.__init__(
            self,
            _("Sources"),
            pdata,
            dbstate,
            uistate,
            SourceModel,
            signal_map,
            SourceBookmarks,
            nav_group,
            multiple=True,
            filter_class=SourceSidebarFilter,
        )

        self.additional_uis.append(self.additional_ui)

    def navigation_type(self):
        return "Source"

    def drag_info(self):
        return DdTargets.SOURCE_LINK

    def get_stock(self):
        return "gramps-source"

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
        """Source Filter Editor</attribute>
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
    </menu>
    """
        % _("_Edit...", "action"),  # to use sgettext()
    ]

    def add(self, *obj):
        EditSource(self.dbstate, self.uistate, [], Source())

    def edit(self, *obj):
        for handle in self.selected_handles():
            source = self.dbstate.db.get_source_from_handle(handle)
            try:
                EditSource(self.dbstate, self.uistate, [], source)
            except WindowActiveError:
                pass

    def merge(self, *obj):
        """
        Merge the selected sources.
        """
        mlist = self.selected_handles()

        if len(mlist) != 2:
            msg = _("Cannot merge sources.")
            msg2 = _(
                "Exactly two sources must be selected to perform a merge. "
                "A second source can be selected by holding down the "
                "control key while clicking on the desired source."
            )
            ErrorDialog(msg, msg2, parent=self.uistate.window)
        else:
            MergeSource(self.dbstate, self.uistate, [], mlist[0], mlist[1])

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_source_from_gramps_id(gid)
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
                        tag_handle, include_classes="Source"
                    )
                ]
            )
            all_links = all_links.union(links)
        self.row_update(list(all_links))

    def add_tag(self, transaction, source_handle, tag_handle):
        """
        Add the given tag to the given source.
        """
        source = self.dbstate.db.get_source_from_handle(source_handle)
        source.add_tag(tag_handle)
        self.dbstate.db.commit_source(source, transaction)

    def remove_tag(self, transaction, source_handle, tag_handle):
        """
        Remove the given tag from the given source.
        """
        source = self.dbstate.db.get_source_from_handle(source_handle)
        source.remove_tag(tag_handle)
        self.dbstate.db.commit_source(source, transaction)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (
            ("Source Filter",),
            ("Source Gallery", "Source Notes", "Source Backlinks"),
        )

    def get_config_name(self):
        return __name__
