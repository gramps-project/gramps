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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

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
from gui.views.treemodels.citationlistmodel import CitationListModel
from gen.plug import CATEGORY_QR_CITATION
import gen.lib
from gui.views.listview import ListView
from gen.utils.referent import get_citation_referents
from gui.views.bookmarks import CitationBookmarks
from gen.errors import WindowActiveError
from gui.ddtargets import DdTargets
from gui.dialog import ErrorDialog
from gui.editors import EditCitation, DeleteCitationQuery
from gui.filters.sidebar import CitationSidebarFilter
from gui.merge import MergeCitation

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _


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
    # src/giu.views/treemodels/citationlismodel.py
    COL_TITLE_PAGE     =  0
    COL_ID             =  1
    COL_DATE           =  2
    COL_CONFIDENCE     =  3
    COL_CHAN           =  4    
    COL_SRC_TITLE      =  5
    COL_SRC_ID         =  6
    COL_SRC_AUTH       =  7
    COL_SRC_ABBR       =  8
    COL_SRC_PINFO      =  9
    COL_SRC_CHAN       = 10
    # name of the columns
    COLUMN_NAMES = [
        _('Volume/Page'),
        _('ID'),
        _('Date'),
        _('Confidence'),
        _('Last Changed'),
        _('Source: Title'),
        _('Source: ID'),
        _('Source: Author'),
        _('Source: Abbreviation'),
        _('Source: Publication Information'),
        _('Source: Last Changed'),
        ]
    # columns that contain markup
    MARKUP_COLS = [COL_DATE]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_TITLE_PAGE, COL_ID, COL_DATE,
                             COL_CONFIDENCE]),
        ('columns.rank', [COL_TITLE_PAGE, COL_ID, COL_DATE, COL_CONFIDENCE,
                          COL_CHAN, COL_SRC_TITLE, COL_SRC_ID, COL_SRC_AUTH,
                          COL_SRC_ABBR, COL_SRC_PINFO, COL_SRC_CHAN]),
        ('columns.size', [200, 75, 100, 100, 100, 200, 75, 75, 100, 150, 100])
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
            self.COLUMN_NAMES, len(self.COLUMN_NAMES), 
            CitationListModel, signal_map,
            dbstate.db.get_citation_bookmarks(),
            CitationBookmarks, nav_group,
            multiple=True,
            filter_class=CitationSidebarFilter,
            markup = CitationListView.MARKUP_COLS)

        self.func_list.update({
            '<CONTROL>J' : self.jump,
            '<CONTROL>BackSpace' : self.key_delete,
            })

        self.additional_uis.append(self.additional_ui())

    def navigation_type(self):
        return 'Citation'

    def get_bookmarks(self):
        return self.dbstate.db.get_citation_bookmarks()

    def drag_info(self):
        return DdTargets.CITATION_LINK
    
    def define_actions(self):
        """
        This defines the possible actions for the citation views.
        Possible actions are:
        add:        Add a new citation and a new source (this can also be done 
                      by source view add a source, then citation view add a new 
                      citation to an existing source)
        edit:       Edit a citation.
        merge:      Merge the selected citations.
        remove:     Delete the selected citations.
        
        
        """
        ListView.define_actions(self)

        self.all_action = Gtk.ActionGroup(self.title + "/CitationAll")
        self.edit_action = Gtk.ActionGroup(self.title + "/CitationEdit")

        self._add_action('FilterEdit', None, _('Citation Filter Editor'),
                         callback=self.filter_editor,)
        self._add_action('QuickReport', None, _("Quick View"), None, None, None)
        self._add_action('Dummy', None, '  ', None, None, self.dummy_report)

        self._add_action_group(self.edit_action)
        self._add_action_group(self.all_action)

    def get_stock(self):
        return 'gramps-citation'

    def additional_ui(self):
        """
        Defines the UI string for UIManager
        """
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="FileMenu">
              <placeholder name="LocalExport">
                <menuitem action="ExportTab"/>
              </placeholder>
            </menu>
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
                <menuitem action="Merge"/>
              </placeholder>
              <menuitem action="FilterEdit"/>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
              <toolitem action="Merge"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Back"/>
            <menuitem action="Forward"/>
            <separator/>
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
            <menuitem action="Merge"/>
            <separator/>
            <menu name="QuickReport" action="QuickReport">
              <menuitem action="Dummy"/>
            </menu>
          </popup>
        </ui>'''

    def dummy_report(self, obj):
        """ For the xml UI definition of popup to work, the submenu 
            Quick Report must have an entry in the xml
            As this submenu will be dynamically built, we offer a dummy action
        """
        pass

    def add(self, obj):
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
            EditCitation(self.dbstate, self.uistate, [], gen.lib.Citation(),
                         gen.lib.Source())
        except WindowActiveError:
            pass

    def remove(self, obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        the_lists = get_citation_referents(handle, self.dbstate.db)
        object = self.dbstate.db.get_citation_from_handle(handle)
        query = DeleteCitationQuery(self.dbstate, self.uistate, object, 
                                    the_lists)
        is_used = any(the_lists)
        return (query, is_used, object)

    def edit(self, obj):
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

    def merge(self, obj):
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
            ErrorDialog(msg, msg2)
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
                ErrorDialog(msg, msg2)
            else:
                MergeCitation(self.dbstate, self.uistate, mlist[0], mlist[1])

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_citation_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        This is overridden for the tree view to give 'Source Filter'
        """
        return (("Citation Filter",),
                ("Citation Gallery",
                 "Citation Notes",
                 "Citation Backlinks"))
