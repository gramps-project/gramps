# Gramps - a GTK+/GNOME based genealogy program
#
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
Citation View
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
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
import config
from gui.views.listview import ListView
from gui.views.treemodels import CitationListModel
import Utils
import Bookmarks
import Errors
from DdTargets import DdTargets
from gui.selectors import SelectorFactory
from QuestionDialog import ErrorDialog
from gui.editors import EditCitation, DeleteCitationQuery
from Filters.SideBar import SourceSidebarFilter
from gen.plug import CATEGORY_QR_SOURCE

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
class BaseCitationView(ListView):
    """ citation listview class 
    """
    # The data items here have to correspond, in order, to the items in
    # src/giu.views/treemodels/citationmodel.py
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
        _('Title/Page'),
        _('ID'),
        _('Date'),
        _('Confidence'),
        _('Last Changed'),
        _('Source: ID'),
        _('Source: Title'),
        _('Source: Author'),
        _('Source: Abbreviation'),
        _('Source: Publication Information'),
        _('Source: Last Changed'),
        ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_TITLE_PAGE, COL_ID, COL_DATE,
                             COL_CONFIDENCE]),
        ('columns.rank', [COL_TITLE_PAGE, COL_ID, COL_DATE, COL_CONFIDENCE,
                          COL_CHAN, COL_SRC_TITLE, COL_SRC_ID, COL_SRC_AUTH,
                          COL_SRC_ABBR, COL_SRC_PINFO, COL_SRC_CHAN]),
        ('columns.size', [200, 75, 100, 100, 100, 200, 75, 75, 100, 150, 100])
        )    
    ADD_MSG = _("Add a new citation")
    EDIT_MSG = _("Edit the selected citation")
    SHARE_MSG = _("Share the selected source")
    DEL_MSG = _("Delete the selected citation")
    MERGE_MSG = _("Merge the selected citations")
    FILTER_TYPE = "Citation"
    QR_CATEGORY = CATEGORY_QR_SOURCE

    def __init__(self, pdata, dbstate, uistate, title, model, nav_group=0):

        signal_map = {
            'citation-add'     : self.row_add,
            'citation-update'  : self.row_update,
            'citation-delete'  : self.row_delete,
            'citation-rebuild' : self.object_build,
            }

        ListView.__init__(
            self, title, pdata, dbstate, uistate, 
            BaseCitationView.COLUMN_NAMES, len(BaseCitationView.COLUMN_NAMES), 
            model, signal_map,
            dbstate.db.get_citation_bookmarks(),
            Bookmarks.CitationBookmarks, nav_group,
            multiple=True,
            filter_class=SourceSidebarFilter)

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
        return DdTargets.SOURCE_LINK
    
    def define_actions(self):
        ListView.define_actions(self)

#        self._add_action('Share', gtk.STOCK_EDIT, _("Share..."), 
#                         accel=None, 
#                         tip=self.SHARE_MSG, 
#                         callback=self.share)
#        
        self.all_action = gtk.ActionGroup(self.title + "/CitationAll")
        self.edit_action = gtk.ActionGroup(self.title + "/CitationEdit")

        self._add_action('FilterEdit', None, _('Citation Filter Editor'),
                         callback=self.filter_editor,)
        self._add_action('QuickReport', None, _("Quick View"), None, None, None)
        self._add_action('Dummy', None, '  ', None, None, self.dummy_report)

        self._add_action_group(self.edit_action)
        self._add_action_group(self.all_action)

    def get_stock(self):
        return 'gramps-citation'

    def additional_ui(self):
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
        SelectSource = SelectorFactory('Source')
        sel = SelectSource(self.dbstate,self.uistate)
        source = sel.run()
        if source:
            try:
                EditCitation(self.dbstate, self.uistate, [], gen.lib.Citation(),
                     source)
            except Errors.WindowActiveError:
                from QuestionDialog import WarningDialog
                WarningDialog(_("Cannot share this reference"),
                              self.__blocked_text())

    def remove(self, obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        the_lists = Utils.get_citation_referents(handle, self.dbstate.db)
        object = self.dbstate.db.get_citation_from_handle(handle)
        query = DeleteCitationQuery(self.dbstate, self.uistate, object, the_lists)
        is_used = any(the_lists)
        return (query, is_used, object)

    def edit(self, obj):
        for handle in self.selected_handles():
            citation = self.dbstate.db.get_citation_from_handle(handle)
            try:
                source = self.dbstate.db.get_source_from_handle(citation.ref)
                EditCitation(self.dbstate, self.uistate, [], citation, source)
            except Errors.WindowActiveError:
                pass
            except:
                LOG.warn("failed to find a Source for the selected Citation")

    def __blocked_text(self):
        """
        Return the common text used when mediaref cannot be edited
        """
        return _("This media reference cannot be edited at this time. "
                    "Either the associated media object is already being "
                    "edited or another media reference that is associated with "
                    "the same media object is being edited.\n\nTo edit this "
                    "media reference, you need to close the media object.")

#    def share(self, obj):
#        SelectSource = SelectorFactory('Source')
#        sel = SelectSource(self.dbstate,self.uistate)
#        source = sel.run()
#        if source:
#            try:
#                EditCitation(self.dbstate, self.uistate, [], gen.lib.Citation(),
#                     source)
#            except Errors.WindowActiveError:
#                from QuestionDialog import WarningDialog
#                WarningDialog(_("Cannot share this reference"),
#                              self.__blocked_text())
#    
    def merge(self, obj):
        """
        Merge the selected citations.
        """
        mlist = self.selected_handles()
        
        if len(mlist) != 2:
            msg = _("Cannot merge citations.")
            msg2 = _("Exactly two citations must be selected to perform a merge. "
                     "A second citation can be selected by holding down the "
                     "control key while clicking on the desired citation.")
            ErrorDialog(msg, msg2)
        else:
            import Merge
            Merge.MergeCitations(self.dbstate, self.uistate, mlist[0], mlist[1])

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_citation_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Source Filter",),
                ("Citation Gallery",
                 "Citation Notes",
                 "Citation Backlinks"))
