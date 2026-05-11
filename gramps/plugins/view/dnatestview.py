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
DNA Tests list view.
"""

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".plugins.dnatestview")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import DNATest
from gramps.gui.dialog import ErrorDialog
from gramps.gui.editors import EditDNATest
from gramps.gui.merge import MergeDNATest
from gramps.gui.views.bookmarks import DNATestBookmarks
from gramps.gui.views.listview import ListView, TEXT, ICON
from gramps.gui.views.treemodels import DNATestModel


# -------------------------------------------------------------------------
#
# DNATestView
#
# -------------------------------------------------------------------------
class DNATestView(ListView):
    """
    A flat list view of all DNA test records in the database.
    """

    COL_ID = 0
    COL_PERSON = 1
    COL_ACCOUNT = 2
    COL_PROVIDER = 3
    COL_KIT_ID = 4
    COL_TEST_TYPE = 5
    COL_HAPLOGROUP = 6
    COL_PRIV = 7
    COL_TAGS = 8
    COL_CHAN = 9

    COLUMNS = [
        (_("ID"), TEXT, None),
        (_("Person"), TEXT, None),
        (_("Account name"), TEXT, None),
        (_("Provider"), TEXT, None),
        (_("Kit ID"), TEXT, None),
        (_("Test type"), TEXT, None),
        (_("Haplogroup"), TEXT, None),
        (_("Private"), ICON, "gramps-lock"),
        (_("Tags"), TEXT, None),
        (_("Last Changed"), TEXT, None),
    ]

    CONFIGSETTINGS = (
        (
            "columns.visible",
            [COL_PERSON, COL_ACCOUNT, COL_PROVIDER, COL_TEST_TYPE, COL_HAPLOGROUP],
        ),
        (
            "columns.rank",
            [
                COL_ID,
                COL_PERSON,
                COL_ACCOUNT,
                COL_PROVIDER,
                COL_KIT_ID,
                COL_TEST_TYPE,
                COL_HAPLOGROUP,
                COL_PRIV,
                COL_TAGS,
                COL_CHAN,
            ],
        ),
        ("columns.size", [75, 200, 150, 100, 100, 100, 100, 40, 100, 100]),
    )

    ADD_MSG = _("Add a new DNA test")
    EDIT_MSG = _("Edit the selected DNA test")
    DEL_MSG = _("Delete the selected DNA test")
    MERGE_MSG = _("Merge the selected DNA tests")
    FILTER_TYPE = "DNATest"

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        signal_map = {
            "dnatest-add": self.row_add,
            "dnatest-update": self.row_update,
            "dnatest-delete": self.row_delete,
            "dnatest-rebuild": self.object_build,
            "person-update": self.person_update,
            "person-add": self.person_update,
            "person-delete": self.object_build,
        }

        ListView.__init__(
            self,
            _("DNA Tests"),
            pdata,
            dbstate,
            uistate,
            DNATestModel,
            signal_map,
            DNATestBookmarks,
            nav_group,
            multiple=True,
        )

        self.additional_uis.append(self.additional_ui)

    def navigation_type(self):
        return "DNATest"

    def get_stock(self):
        return "gramps-dna-test"

    def person_update(self, handle_list):
        """
        Update rows whose Person column may have changed.
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
""" % _("Organize Bookmarks"),
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
""" % _("_Edit...", "action"),
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
""" % (ADD_MSG, EDIT_MSG, DEL_MSG, MERGE_MSG),
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
        <item>
          <attribute name="action">win.SetActivePerson</attribute>
          <attribute name="label" translatable="yes">Set Active Person</attribute>
        </item>
      </section>
      <section>
        <placeholder id='QuickReport'>
        </placeholder>
        <placeholder id='WebConnect'>
        </placeholder>
      </section>
    </menu>
    """ % _("_Edit...", "action"),
    ]

    def define_actions(self):
        ListView.define_actions(self)
        self.action_list.extend(
            [
                ("SetActivePerson", self._set_active_person),
            ]
        )

    def _set_active_person(self, *obj):
        handle = self.first_selected()
        if handle:
            dnatest = self.dbstate.db.get_dnatest_from_handle(handle)
            if dnatest and dnatest.person_handle:
                self.uistate.set_active(dnatest.person_handle, "Person")

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_dnatest_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        return None

    def add(self, *obj):
        try:
            EditDNATest(self.dbstate, self.uistate, [], DNATest())
        except WindowActiveError:
            pass

    def remove(self, *obj):
        handles = self.selected_handles()
        ht_list = [("DNATest", hndl) for hndl in handles]
        self.remove_selected_objects(ht_list)

    def edit(self, *obj):
        for handle in self.selected_handles():
            dnatest = self.dbstate.db.get_dnatest_from_handle(handle)
            try:
                EditDNATest(self.dbstate, self.uistate, [], dnatest)
            except WindowActiveError:
                pass

    def merge(self, *obj):
        mlist = self.selected_handles()
        if len(mlist) != 2:
            msg = _("Cannot merge DNA tests.")
            msg2 = _(
                "Exactly two DNA tests must be selected to perform a merge. "
                "A second DNA test can be selected by holding down the "
                "control key while clicking on the desired DNA test."
            )
            ErrorDialog(msg, msg2, parent=self.uistate.window)
        else:
            MergeDNATest(self.dbstate, self.uistate, [], mlist[0], mlist[1])

    def tag_updated(self, handle_list):
        """
        Update tagged rows when a tag color changes.
        """
        all_links = set()
        for tag_handle in handle_list:
            links = set(
                link[1]
                for link in self.dbstate.db.find_backlink_handles(
                    tag_handle, include_classes="DNATest"
                )
            )
            all_links = all_links.union(links)
        self.row_update(list(all_links))

    def add_tag(self, transaction, dnatest_handle, tag_handle):
        """
        Add the given tag to the given DNA test.
        """
        dnatest = self.dbstate.db.get_dnatest_from_handle(dnatest_handle)
        dnatest.add_tag(tag_handle)
        self.dbstate.db.commit_dnatest(dnatest, transaction)

    def remove_tag(self, transaction, dnatest_handle, tag_handle):
        """
        Remove the given tag from the given DNA test.
        """
        dnatest = self.dbstate.db.get_dnatest_from_handle(dnatest_handle)
        dnatest.remove_tag(tag_handle)
        self.dbstate.db.commit_dnatest(dnatest, transaction)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return ((), ())

    def get_config_name(self):
        return __name__
