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
Citation List View
"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gui.views.treemodels.citationlistmodel import CitationListModel
from gramps.gen.plug import CATEGORY_QR_CITATION
from gramps.gen.lib import Citation, Source
from gramps.gui.views.listview import ListView, TEXT, MARKUP, ICON
from gramps.gen.utils.db import get_citation_referents
from gramps.gui.views.bookmarks import CitationBookmarks
from gramps.gen.errors import WindowActiveError
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import ErrorDialog
from gramps.gui.editors import EditCitation, DeleteCitationQuery
from gramps.gui.filters.sidebar import CitationSidebarFilter
from gramps.gui.merge import MergeCitation

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext


#-------------------------------------------------------------------------
#
# CitationView
#
#-------------------------------------------------------------------------
class CitationListView(ListView):
    """
    A list view of citations.

    The citation list view only shows the citations (it does not show
    sources as separate list entries).
    """
    # The data items here have to correspond, in order, to the items in
    # src/giu/views/treemodels/citationlismodel.py
    COL_TITLE_PAGE = 0
    COL_ID = 1
    COL_DATE = 2
    COL_CONFIDENCE = 3
    COL_PRIV = 4
    COL_TAGS = 5
    COL_CHAN = 6
    COL_SRC_TITLE = 7
    COL_SRC_ID = 8
    COL_SRC_AUTH = 9
    COL_SRC_ABBR = 10
    COL_SRC_PINFO = 11
    COL_SRC_PRIV = 12
    COL_SRC_CHAN = 13
    # column definitions
    COLUMNS = [
        (_('Volume/Page'), TEXT, None),
        (_('ID'), TEXT, None),
        (_('Date'), MARKUP, None),
        (_('Confidence'), TEXT, None),
        (_('Private'), ICON, 'gramps-lock'),
        (_('Tags'), TEXT, None),
        (_('Last Changed'), TEXT, None),
        (_('Source: Title'), TEXT, None),
        (_('Source: ID'), TEXT, None),
        (_('Source: Author'), TEXT, None),
        (_('Source: Abbreviation'), TEXT, None),
        (_('Source: Publication Information'), TEXT, None),
        (_('Source: Private'), ICON, 'gramps-lock'),
        (_('Source: Last Changed'), TEXT, None),
        ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_TITLE_PAGE, COL_ID, COL_DATE,
                             COL_CONFIDENCE]),
        ('columns.rank', [COL_TITLE_PAGE, COL_ID, COL_DATE, COL_CONFIDENCE,
                          COL_PRIV, COL_TAGS, COL_CHAN, COL_SRC_TITLE,
                          COL_SRC_ID, COL_SRC_AUTH, COL_SRC_ABBR, COL_SRC_PINFO,
                          COL_SRC_PRIV, COL_SRC_CHAN]),
        ('columns.size', [200, 75, 100, 100, 40, 100, 100, 200, 75, 75, 100,
                          150, 40, 100])
        )
    ADD_MSG = _("Add a new citation and a new source")
    ADD_SOURCE_MSG = _("Add a new source")
    ADD_CITATION_MSG = _("Add a new citation to an existing source")
    EDIT_MSG = _("Edit the selected citation")
    DEL_MSG = _("Delete the selected citation")
    MERGE_MSG = _("Merge the selected citations")
    FILTER_TYPE = "Citation"
    QR_CATEGORY = CATEGORY_QR_CITATION

    def __init__(self, pdata, dbstate, uistate, nav_group=0):

        signal_map = {
            'citation-add'     : self.row_add,
            'citation-update'  : self.row_update,
            'citation-delete'  : self.row_delete,
            'citation-rebuild' : self.object_build,
            }

        ListView.__init__(
            self, _('Citation View'), pdata, dbstate, uistate,
            CitationListModel, signal_map,
            CitationBookmarks, nav_group,
            multiple=True,
            filter_class=CitationSidebarFilter)

        self.additional_uis.append(self.additional_ui)

    def navigation_type(self):
        return 'Citation'

    def drag_info(self):
        return DdTargets.CITATION_LINK

    def get_stock(self):
        return 'gramps-citation'

    additional_ui = [
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
        '''Citation Filter Editor</attribute>
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
        <property name="tooltip_text" >%s</property>
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
        <placeholder id='QuickReport'>
        </placeholder>
      </section>
    </menu>
''' % _('_Edit...', 'action')  # to use sgettext()
]

    def add(self, *obj):
        """
        add:        Add a new citation and a new source (this can also be done
                      by source view add a source, then citation view add a new
                      citation to an existing source)

        Create a new Source instance and Citation instance and call the
        EditCitation editor with the new source and new citation.

        Called when the Add button is clicked.
        If the window already exists (WindowActiveError), we ignore it.
        This prevents the dialog from coming up twice on the same object.

        However, since the window is identified by the Source object, and
        we have just created a new one, it seems to be impossible for the
        window to already exist, so this is just an extra safety measure.
        """
        try:
            EditCitation(self.dbstate, self.uistate, [], Citation(),
                         Source())
        except WindowActiveError:
            pass

    def remove(self, *obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        the_lists = get_citation_referents(handle, self.dbstate.db)
        object = self.dbstate.db.get_citation_from_handle(handle)
        query = DeleteCitationQuery(self.dbstate, self.uistate, object,
                                    the_lists)
        is_used = any(the_lists)
        return (query, is_used, object)

    def edit(self, *obj):
        """
        Edit a Citation
        """
        for handle in self.selected_handles():
            citation = self.dbstate.db.get_citation_from_handle(handle)
            try:
                EditCitation(self.dbstate, self.uistate, [], citation)
            except WindowActiveError:
                pass

    def __blocked_text(self):
        """
        Return the common text used when citation cannot be edited
        """
        return _("This citation cannot be edited at this time. "
                    "Either the associated citation is already being "
                    "edited or another object that is associated with "
                    "the same citation is being edited.\n\nTo edit this "
                    "citation, you need to close the object.")

    def merge(self, *obj):
        """
        Merge the selected citations.
        """
        mlist = self.selected_handles()

        if len(mlist) != 2:
            msg = _("Cannot merge citations.")
            msg2 = _("Exactly two citations must be selected to perform a "
                     "merge. A second citation can be selected by holding "
                     "down the control key while clicking on the desired "
                     "citation.")
            ErrorDialog(msg, msg2, parent=self.uistate.window)
        else:
            citation1 = self.dbstate.db.get_citation_from_handle(mlist[0])
            citation2 = self.dbstate.db.get_citation_from_handle(mlist[1])
            if not citation1.get_reference_handle()  == \
                            citation2.get_reference_handle():
                msg = _("Cannot merge citations.")
                msg2 = _("The two selected citations must have the same "
                         "source to perform a merge. If you want to merge "
                         "these two citations, then you must merge the "
                         "sources first.")
                ErrorDialog(msg, msg2, parent=self.uistate.window)
            else:
                MergeCitation(self.dbstate, self.uistate, [], mlist[0],
                              mlist[1])

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_citation_from_gramps_id(gid)
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
            links = set([link[1] for link in
                         self.dbstate.db.find_backlink_handles(tag_handle,
                                                include_classes='Citation')])
            all_links = all_links.union(links)
        self.row_update(list(all_links))

    def add_tag(self, transaction, citation_handle, tag_handle):
        """
        Add the given tag to the given citation.
        """
        citation = self.dbstate.db.get_citation_from_handle(citation_handle)
        citation.add_tag(tag_handle)
        self.dbstate.db.commit_citation(citation, transaction)

    def remove_tag(self, transaction, citation_handle, tag_handle):
        """
        Remove the given tag from the given citation.
        """
        citation = self.dbstate.db.get_citation_from_handle(citation_handle)
        citation.remove_tag(tag_handle)
        self.dbstate.db.commit_citation(citation, transaction)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        This is overridden for the tree view to give 'Source Filter'
        """
        return (("Citation Filter",),
                ("Citation Gallery",
                 "Citation Notes",
                 "Citation Backlinks"))
