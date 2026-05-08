#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
DNA Matches list view.
"""

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".plugins.dnamatchview")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import DNAMatch
from gramps.gui.dialog import ErrorDialog
from gramps.gui.editors import EditDNAMatch
from gramps.gui.views.bookmarks import DNAMatchBookmarks
from gramps.gui.views.listview import ListView, TEXT, ICON
from gramps.gui.views.treemodels import DNAMatchModel


# -------------------------------------------------------------------------
#
# DNAMatchView
#
# -------------------------------------------------------------------------
class DNAMatchView(ListView):
    """
    A flat list view of all DNA match records in the database.
    """

    COL_ID = 0
    COL_SUBJECT_TEST = 1
    COL_MATCH_TEST = 2
    COL_SHARED_CM = 3
    COL_LARGEST_SEG = 4
    COL_SEG_COUNT = 5
    COL_PREDICTED_REL = 6
    COL_PRED_GEN = 7
    COL_SHARED_ANCS = 8
    COL_PRIV = 9
    COL_TAGS = 10
    COL_CHAN = 11

    COLUMNS = [
        (_("ID"), TEXT, None),
        (_("Subject test"), TEXT, None),
        (_("Match test"), TEXT, None),
        (_("Shared cM"), TEXT, None),
        (_("Largest segment cM"), TEXT, None),
        (_("Segment count"), TEXT, None),
        (_("Predicted relationship"), TEXT, None),
        (_("Predicted generations"), TEXT, None),
        (_("Shared ancestors"), TEXT, None),
        (_("Private"), ICON, "gramps-lock"),
        (_("Tags"), TEXT, None),
        (_("Last Changed"), TEXT, None),
    ]

    CONFIGSETTINGS = (
        (
            "columns.visible",
            [
                COL_SUBJECT_TEST,
                COL_MATCH_TEST,
                COL_SHARED_CM,
                COL_LARGEST_SEG,
                COL_PREDICTED_REL,
            ],
        ),
        (
            "columns.rank",
            [
                COL_ID,
                COL_SUBJECT_TEST,
                COL_MATCH_TEST,
                COL_SHARED_CM,
                COL_LARGEST_SEG,
                COL_SEG_COUNT,
                COL_PREDICTED_REL,
                COL_PRED_GEN,
                COL_SHARED_ANCS,
                COL_PRIV,
                COL_TAGS,
                COL_CHAN,
            ],
        ),
        ("columns.size", [75, 200, 200, 75, 75, 75, 120, 75, 75, 40, 100, 100]),
    )

    ADD_MSG = _("Add a new DNA match")
    EDIT_MSG = _("Edit the selected DNA match")
    DEL_MSG = _("Delete the selected DNA match")
    MERGE_MSG = _("Merge the selected DNA matches")
    FILTER_TYPE = "DNAMatch"

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        signal_map = {
            "dnamatch-add": self.row_add,
            "dnamatch-update": self.row_update,
            "dnamatch-delete": self.row_delete,
            "dnamatch-rebuild": self.object_build,
            "dnatest-update": self.object_build,
            "person-update": self.person_update,
            "person-add": self.person_update,
            "person-delete": self.object_build,
        }

        ListView.__init__(
            self,
            _("DNA Matches"),
            pdata,
            dbstate,
            uistate,
            DNAMatchModel,
            signal_map,
            DNAMatchBookmarks,
            nav_group,
            multiple=True,
        )

        self.additional_uis.append(self.additional_ui)

    def navigation_type(self):
        return "DNAMatch"

    def get_stock(self):
        return "gramps-dna-match"

    def person_update(self, handle_list):
        """
        Update rows whose person columns may have changed.
        """
        self.object_build()

    additional_ui = [
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
          <attribute name="label">%s...</attribute>
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
        % _("_Edit...", "action"),
        """
        <placeholder id='otheredit'>
        </placeholder>
""",
        """
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">Go to the previous object in the history</property>
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
        <property name="tooltip_text" translatable="yes">Go to the next object in the history</property>
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
        <placeholder id='WebConnect'>
        </placeholder>
      </section>
    </menu>
    """
        % _("_Edit...", "action"),
    ]

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_dnamatch_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        return None

    def add(self, *obj):
        try:
            EditDNAMatch(self.dbstate, self.uistate, [], DNAMatch())
        except WindowActiveError:
            pass

    def remove(self, *obj):
        handles = self.selected_handles()
        ht_list = [("DNAMatch", hndl) for hndl in handles]
        self.remove_selected_objects(ht_list)

    def edit(self, *obj):
        for handle in self.selected_handles():
            dnamatch = self.dbstate.db.get_dnamatch_from_handle(handle)
            try:
                EditDNAMatch(self.dbstate, self.uistate, [], dnamatch)
            except WindowActiveError:
                pass

    def merge(self, *obj):
        msg = _("Cannot merge DNA matches.")
        msg2 = _("Merge is not yet implemented for DNA matches.")
        ErrorDialog(msg, msg2, parent=self.uistate.window)

    def tag_updated(self, handle_list):
        """
        Update tagged rows when a tag color changes.
        """
        all_links = set()
        for tag_handle in handle_list:
            links = set(
                link[1]
                for link in self.dbstate.db.find_backlink_handles(
                    tag_handle, include_classes="DNAMatch"
                )
            )
            all_links = all_links.union(links)
        self.row_update(list(all_links))

    def add_tag(self, transaction, dnamatch_handle, tag_handle):
        """
        Add the given tag to the given DNA match.
        """
        dnamatch = self.dbstate.db.get_dnamatch_from_handle(dnamatch_handle)
        dnamatch.add_tag(tag_handle)
        self.dbstate.db.commit_dnamatch(dnamatch, transaction)

    def remove_tag(self, transaction, dnamatch_handle, tag_handle):
        """
        Remove the given tag from the given DNA match.
        """
        dnamatch = self.dbstate.db.get_dnamatch_from_handle(dnamatch_handle)
        dnamatch.remove_tag(tag_handle)
        self.dbstate.db.commit_dnamatch(dnamatch, transaction)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return ((), ())

    def get_config_name(self):
        return __name__
