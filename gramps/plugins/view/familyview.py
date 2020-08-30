# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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
Family View.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
import logging
_LOG = logging.getLogger(".plugins.eventview")
#-------------------------------------------------------------------------
#
# GNOME/GTK+ modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import Family
from gramps.gui.views.listview import ListView, TEXT, MARKUP, ICON
from gramps.gui.views.treemodels import FamilyModel
from gramps.gui.editors import EditFamily
from gramps.gui.views.bookmarks import FamilyBookmarks
from gramps.gen.errors import WindowActiveError
from gramps.gen.config import config
from gramps.gui.dialog import ErrorDialog
from gramps.gui.filters.sidebar import FamilySidebarFilter
from gramps.gui.merge import MergeFamily
from gramps.gen.plug import CATEGORY_QR_FAMILY
from gramps.gui.ddtargets import DdTargets

#-------------------------------------------------------------------------
#
# FamilyView
#
#-------------------------------------------------------------------------
class FamilyView(ListView):
    """ FamilyView class, derived from the ListView
    """
    # columns in the model used in view
    COL_ID = 0
    COL_FATHER = 1
    COL_MOTHER = 2
    COL_REL = 3
    COL_MARDATE = 4
    COL_PRIV = 5
    COL_TAGS = 6
    COL_CHAN = 7
    # column definitions
    COLUMNS = [
        (_('ID'), TEXT, None),
        (_('Father'), TEXT, None),
        (_('Mother'), TEXT, None),
        (_('Relationship'), TEXT, None),
        (_('Marriage Date'), MARKUP, None),
        (_('Private'), ICON, 'gramps-lock'),
        (_('Tags'), TEXT, None),
        (_('Last Changed'), TEXT, None),
        ]
    #default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_ID, COL_FATHER, COL_MOTHER, COL_REL,
                             COL_MARDATE]),
        ('columns.rank', [COL_ID, COL_FATHER, COL_MOTHER, COL_REL,
                           COL_MARDATE, COL_PRIV, COL_TAGS, COL_CHAN]),
        ('columns.size', [75, 200, 200, 100, 100, 40, 100, 100])
        )

    ADD_MSG = _("Add a new family")
    EDIT_MSG = _("Edit the selected family")
    DEL_MSG = _("Delete the selected family")
    MERGE_MSG = _("Merge the selected families")
    FILTER_TYPE = "Family"
    QR_CATEGORY = CATEGORY_QR_FAMILY

    def __init__(self, pdata, dbstate, uistate, nav_group=0):

        signal_map = {
            'family-add'     : self.row_add,
            'family-update'  : self.row_update,
            'family-delete'  : self.row_delete,
            'family-rebuild' : self.object_build,
            'event-update'   : self.related_update,
            'person-update'  : self.related_update,
            }

        ListView.__init__(
            self, _('Families'), pdata, dbstate, uistate,
            FamilyModel,
            signal_map,
            FamilyBookmarks, nav_group,
            multiple=True,
            filter_class=FamilySidebarFilter)

        uistate.connect('nameformat-changed', self.build_tree)

        self.additional_uis.append(self.additional_ui)

    def navigation_type(self):
        return 'Family'

    def get_stock(self):
        return 'gramps-family'

    additional_ui = [  # Defines the UI string for UIManager
        '''
      <placeholder id="LocalExport">
        <item>
          <attribute name="action">win.ExportTab</attribute>
          <attribute name="label" translatable="yes">Export View...</attribute>
        </item>
      </placeholder>
''',
        '''
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
''' % _('Organize Bookmarks'),
        '''
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
''',
        '''
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
''' % _("_Edit...", "action"),  # to use sgettext()
        '''
        <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.FilterEdit</attribute>
          <attribute name="label" translatable="yes">'''
        '''Family Filter Editor</attribute>
        </item>
        </placeholder>
''',  # Following are the Toolbar items
        '''
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the previous object in the history</property>
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
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
''',
        '''
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
''' % (ADD_MSG, EDIT_MSG, DEL_MSG, MERGE_MSG),
        '''
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
          <attribute name="action">win.MakeFatherActive</attribute>
          <attribute name="label" translatable="yes">'''
        '''Make Father Active Person</attribute>
        </item>
        <item>
          <attribute name="action">win.MakeMotherActive</attribute>
          <attribute name="label" translatable="yes">'''
        '''Make Mother Active Person</attribute>
        </item>
      </section>
      <section>
        <placeholder id='QuickReport'>
        </placeholder>
      </section>
    </menu>
''' % _('_Edit...', 'action')  # to use sgettext()
    ]

    def define_actions(self):
        """Add the Forward action group to handle the Forward button."""

        ListView.define_actions(self)

        self.action_list.extend([
            ('MakeFatherActive', self._make_father_active),
            ('MakeMotherActive', self._make_mother_active), ])

    def add_bookmark(self, *obj):
        mlist = self.selected_handles()
        if mlist:
            self.bookmarks.add(mlist[0])
        else:
            from gramps.gui.dialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"),
                _("A bookmark could not be set because "
                  "no one was selected."), parent=self.uistate.window)

    def add(self, *obj):
        family = Family()
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass

    def remove(self, *obj):
        """
        Method called when deleting a family from a family view.
        """
        from gramps.gui.dialog import QuestionDialog, MultiSelectDialog
        from gramps.gen.utils.string import data_recover_msg
        handles = self.selected_handles()
        if len(handles) == 1:
            family = self.dbstate.db.get_family_from_handle(handles[0])
            msg1 = self._message1_format(family)
            msg2 = self._message2_format(family)
            msg2 = "%s %s" % (msg2, data_recover_msg)
            QuestionDialog(msg1,
                           msg2,
                           _('_Delete Family'),
                           lambda: self.delete_family_response(family),
                           parent=self.uistate.window)
        else:
            MultiSelectDialog(self._message1_format,
                              self._message2_format,
                              handles,
                              self.dbstate.db.get_family_from_handle,
                              yes_func=self.delete_family_response,
                              parent=self.uistate.window)

    def _message1_format(self, family):
        """
        Header format for remove dialogs.
        """
        return _('Delete %s?') % (_('family') +
                                  (" [%s]" % family.gramps_id))

    def _message2_format(self, family):
        """
        Detailed message format for the remove dialogs.
        """
        return _('Deleting item will remove it from the database.')

    def delete_family_response(self, family):
        """
        Deletes the family from the database. Callback to remove
        dialogs.
        """
        from gramps.gen.db import DbTxn
        # set the busy cursor, so the user knows that we are working
        self.uistate.set_busy_cursor(True)
        # create the transaction
        with DbTxn('', self.dbstate.db) as trans:
            gramps_id = family.gramps_id
            self.dbstate.db.remove_family_relationships(family.handle, trans)
            trans.set_description(_("Family [%s]") % gramps_id)
        self.uistate.set_busy_cursor(False)

    def remove_object_from_handle(self, handle):
        """
        The remove_selected_objects method is not called in this view.
        """
        pass

    def edit(self, *obj):
        for handle in self.selected_handles():
            family = self.dbstate.db.get_family_from_handle(handle)
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except WindowActiveError:
                pass

    def merge(self, *obj):
        """
        Merge the selected families.
        """
        mlist = self.selected_handles()

        if len(mlist) != 2:
            msg = _("Cannot merge families.")
            msg2 = _("Exactly two families must be selected to perform a merge."
                     " A second family can be selected by holding down the "
                     "control key while clicking on the desired family.")
            ErrorDialog(msg, msg2, parent=self.uistate.window)
        else:
            MergeFamily(self.dbstate, self.uistate, [], mlist[0], mlist[1])

    def _make_father_active(self, *obj):
        """
        Make the father of the family the active person.
        """
        fhandle = self.first_selected()
        if fhandle:
            family = self.dbstate.db.get_family_from_handle(fhandle)
            if family:
                self.uistate.set_active(family.father_handle, 'Person')

    def _make_mother_active(self, *obj):
        """
        Make the mother of the family the active person.
        """
        fhandle = self.first_selected()
        if fhandle:
            family = self.dbstate.db.get_family_from_handle(fhandle)
            if family:
                self.uistate.set_active(family.mother_handle, 'Person')

    def drag_info(self):
        """
        Indicate that the drag type is a FAMILY_LINK
        """
        return DdTargets.FAMILY_LINK

    def tag_updated(self, handle_list):
        """
        Update tagged rows when a tag color changes.
        """
        all_links = set([])
        for tag_handle in handle_list:
            links = set([link[1] for link in
                         self.dbstate.db.find_backlink_handles(tag_handle,
                                                    include_classes='Family')])
            all_links = all_links.union(links)
        self.row_update(list(all_links))

    def add_tag(self, transaction, family_handle, tag_handle):
        """
        Add the given tag to the given family.
        """
        family = self.dbstate.db.get_family_from_handle(family_handle)
        family.add_tag(tag_handle)
        self.dbstate.db.commit_family(family, transaction)

    def remove_tag(self, transaction, family_handle, tag_handle):
        """
        Remove the given tag from the given family.
        """
        family = self.dbstate.db.get_family_from_handle(family_handle)
        family.remove_tag(tag_handle)
        self.dbstate.db.commit_family(family, transaction)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Family Filter",),
                ("Family Gallery",
                 "Family Events",
                 "Family Children",
                 "Family Citations",
                 "Family Notes",
                 "Family Attributes",
                 "Family Backlinks"))
