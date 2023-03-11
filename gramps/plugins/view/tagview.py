# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2022       Christopher Horn
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
Tag View.
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome Modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.datehandler import format_time
from gramps.gen.db import DbTxn
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Tag
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import QuestionDialog2
from gramps.gui.views.listview import ListView, TEXT
from gramps.gui.views.tags import EditTag, OrganizeTagsDialog
from gramps.gui.views.treemodels.flatbasemodel import FlatBaseModel
import gramps.gui.widgets.progressdialog as progressdlg

_ = glocale.translation.sgettext


(POS_HANDLE, POS_NAME, POS_COLOR, POS_PRIORITY, POS_CHANGE) = list(range(5))


# -------------------------------------------------------------------------
#
# TagModel
#
# -------------------------------------------------------------------------
class TagModel(FlatBaseModel):
    """
    Basic model for a Tag list
    """

    def __init__(
        self,
        db,
        uistate,
        scol=0,
        order=Gtk.SortType.ASCENDING,
        search=None,
        skip=None,
        sort_map=None,
    ):
        """Setup initial values for instance variables."""
        skip = skip or set()
        self.gen_cursor = db.get_tag_cursor
        self.map = db.get_raw_tag_data
        self.fmap = [
            self.column_name,
            self.column_color,
            self.column_priority,
            self.column_change,
            self.column_count,
        ]
        self.smap = [
            self.column_name,
            self.column_color,
            self.column_priority,
            self.sort_change,
            self.sort_count,
        ]
        FlatBaseModel.__init__(
            self,
            db,
            uistate,
            scol,
            order,
            search=search,
            skip=skip,
            sort_map=sort_map,
        )

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.map = None
        self.fmap = None
        self.smap = None
        FlatBaseModel.destroy(self)

    def color_column(self):
        """
        Return the color column.
        """
        return 1

    def on_get_n_columns(self):
        """
        Return the column number of the Tag tab.
        """
        return len(self.fmap) + 1

    def column_handle(self, data):
        """
        Return the handle of the Tag.
        """
        return data[POS_HANDLE]

    def column_name(self, data):
        """
        Return the name of the Tag in readable format.
        """
        return data[POS_NAME]

    def column_priority(self, data):
        """
        Return the priority of the Tag.
        """
        return "%03d" % data[POS_PRIORITY]

    def column_color(self, data):
        """
        Return the color.
        """
        return data[POS_COLOR]

    def sort_change(self, data):
        """
        Return sort value for change.
        """
        return "%012x" % data[POS_CHANGE]

    def column_change(self, data):
        """
        Return formatted change time.
        """
        return format_time(data[POS_CHANGE])

    def sort_count(self, data):
        """
        Return sort value for count of tagged items.
        """
        return "%012d" % len(
            list(self.db.find_backlink_handles(data[POS_HANDLE]))
        )

    def column_count(self, data):
        """
        Return count of tagged items.
        """
        return int(len(list(self.db.find_backlink_handles(data[POS_HANDLE]))))


# -------------------------------------------------------------------------
#
# TagView
#
# -------------------------------------------------------------------------
class TagView(ListView):
    """
    TagView, a normal flat listview for the tags
    """

    COL_NAME = 0
    COL_COLO = 1
    COL_PRIO = 2
    COL_CHAN = 3
    COL_COUNT = 4

    # column definitions
    COLUMNS = [
        (_("Name"), TEXT, None),
        (_("Color"), TEXT, None),
        (_("Priority"), TEXT, None),
        (_("Last Changed"), TEXT, None),
        (_("Tagged Items"), TEXT, None),
    ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        (
            "columns.visible",
            [COL_NAME, COL_COLO, COL_PRIO, COL_CHAN, COL_COUNT],
        ),
        ("columns.rank", [COL_NAME, COL_COLO, COL_PRIO, COL_CHAN, COL_COUNT]),
        ("columns.size", [330, 150, 70, 200, 50]),
    )

    ADD_MSG = _("Add a new tag")
    EDIT_MSG = _("Edit the selected tag")
    DEL_MSG = _("Delete the selected tag")
    ORGANIZE_MSG = _("Organize tags")

    FILTER_TYPE = "Tag"
    QR_CATEGORY = -1

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        signal_map = {
            "tag-add": self.row_add,
            "tag-update": self.row_update,
            "tag-delete": self.row_delete,
            "tag-rebuild": self.object_build,
        }

        # Work around for modify_statusbar issues
        if "Tag" not in uistate.NAV2MES:
            uistate.NAV2MES["Tag"] = ""

        ListView.__init__(
            self,
            _("Tags"),
            pdata,
            dbstate,
            uistate,
            TagModel,
            signal_map,
            None,
            nav_group,
            filter_class=None,
            multiple=False,
        )

        self.additional_uis.append(self.additional_ui)

    def navigation_type(self):
        """
        Return the navigation type.
        """
        return "Tag"

    def drag_info(self):
        """
        Return a drag type of TAG_LINK
        """
        return DdTargets.TAG_LINK

    def get_stock(self):
        """
        Return the gramps-tag stock icon
        """
        return "gramps-tag"

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
          <attribute name="action">win.Organize</attribute>
          <attribute name="label" translatable="yes">_Organize...</attribute>
        </item>
      </section>
"""
        % _(
            "_Edit...", "action"
        ),  # to use sgettext() # Following are the Toolbar items
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
        <property name="icon-name">view-sort-descending</property>
        <property name="action-name">win.Organize</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Organize</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
"""
        % (ADD_MSG, EDIT_MSG, DEL_MSG, ORGANIZE_MSG),
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
          <attribute name="action">win.Organize</attribute>
          <attribute name="label" translatable="yes">_Organize...</attribute>
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
    # Leave QuickReport as placeholder

    def define_actions(self):
        """
        Define actions for the view.
        """
        ListView.define_actions(self)
        self.edit_action.add_actions(
            [("Organize", self.organize, "<PRIMARY>Home")]
        )

    def set_active(self):
        """
        Set view active.
        """
        ListView.set_active(self)
        self.uistate.viewmanager.tags.tag_disable()

    def set_inactive(self):
        """
        Set view inactive.
        """
        ListView.set_inactive(self)
        self.uistate.viewmanager.tags.tag_enable(update_menu=False)

    def get_handle_from_gramps_id(self, gid):
        """
        Not applicable.
        """
        return None

    def add(self, *obj):
        """
        Add new tag.
        """
        try:
            EditTag(self.dbstate.db, self.uistate, [], Tag())
        except WindowActiveError:
            pass

    def remove(self, *obj):
        """
        Remove selected tag.
        """
        handles = self.selected_handles()
        if handles:
            tag = self.dbstate.db.get_tag_from_handle(handles[0])
            delete_tag(self.uistate.window, self.dbstate.db, tag)

    def edit(self, *obj):
        """
        Edit selected tag.
        """
        for handle in self.selected_handles():
            tag = self.dbstate.db.get_tag_from_handle(handle)
            try:
                EditTag(self.dbstate.db, self.uistate, [], tag)
            except WindowActiveError:
                pass

    def organize(self, *_dummy_obj):
        """
        Launch organize tool.
        """
        try:
            OrganizeTagsDialog(self.dbstate.db, self.uistate, [])
        except WindowActiveError:
            pass

    def merge(self, *obj):
        """
        Not supported for now.
        """

    def tag_updated(self, handle_list):
        """
        Not applicable.
        """

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return ((), ())

    def remove_object_from_handle(self, *args, **kwargs):
        """
        Not applicable.
        """


def delete_tag(window, db, tag):
    """
    Handle tag deletion, extracted from OrganizeTagsDialog.
    """
    yes_no = QuestionDialog2(
        _("Remove tag '%s'?") % tag.name,
        _(
            "The tag definition will be removed.  The tag will be also "
            "removed from all objects in the database."
        ),
        _("Yes"),
        _("No"),
        parent=window,
    )
    prompt = yes_no.run()
    if prompt:
        fnc = {
            "Person": (db.get_person_from_handle, db.commit_person),
            "Family": (db.get_family_from_handle, db.commit_family),
            "Event": (db.get_event_from_handle, db.commit_event),
            "Place": (db.get_place_from_handle, db.commit_place),
            "Source": (db.get_source_from_handle, db.commit_source),
            "Citation": (db.get_citation_from_handle, db.commit_citation),
            "Repository": (
                db.get_repository_from_handle,
                db.commit_repository,
            ),
            "Media": (db.get_media_from_handle, db.commit_media),
            "Note": (db.get_note_from_handle, db.commit_note),
        }

        links = list(db.find_backlink_handles(tag.handle))
        # Make the dialog modal so that the user can't start another
        # database transaction while the one removing tags is still running.
        pmon = progressdlg.ProgressMonitor(
            progressdlg.GtkProgressDialog,
            ("", window, Gtk.DialogFlags.MODAL),
            popup_time=2,
        )
        status = progressdlg.LongOpStatus(
            msg=_("Removing Tags"),
            total_steps=len(links),
            interval=len(links) // 20,
        )
        pmon.add_op(status)

        msg = _("Delete Tag (%s)") % tag.name
        with DbTxn(msg, db) as trans:
            for classname, handle in links:
                status.heartbeat()
                obj = fnc[classname][0](handle)  # get from handle
                obj.remove_tag(tag.handle)
                fnc[classname][1](obj, trans)  # commit

            db.remove_tag(tag.handle, trans)
        status.end()
