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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
import logging
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import Source
from gramps.gen.config import config
from gramps.gui.views.listview import ListView, TEXT, MARKUP, ICON
from gramps.gui.views.treemodels import SourceModel
from gramps.gen.utils.db import get_source_and_citation_referents
from gramps.gui.views.bookmarks import SourceBookmarks
from gramps.gen.errors import WindowActiveError
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import ErrorDialog
from gramps.gui.editors import EditSource, DeleteSrcQuery
from gramps.gui.filters.sidebar import SourceSidebarFilter
from gramps.gui.merge import MergeSource
from gramps.gen.plug import CATEGORY_QR_SOURCE

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


#-------------------------------------------------------------------------
#
# SourceView
#
#-------------------------------------------------------------------------
class SourceView(ListView):
    """ sources listview class
    """
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
        (_('Title'), TEXT, None),
        (_('ID'), TEXT, None),
        (_('Author'), TEXT, None),
        (_('Abbreviation'), TEXT, None),
        (_('Publication Information'), TEXT, None),
        (_('Private'), ICON, 'gramps-lock'),
        (_('Tags'), TEXT, None),
        (_('Last Changed'), TEXT, None),
        ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_TITLE, COL_ID, COL_AUTH, COL_PINFO]),
        ('columns.rank', [COL_TITLE, COL_ID, COL_AUTH, COL_ABBR, COL_PINFO,
                          COL_PRIV, COL_TAGS, COL_CHAN]),
        ('columns.size', [200, 75, 150, 100, 150, 40, 100, 100])
        )
    ADD_MSG = _("Add a new source")
    EDIT_MSG = _("Edit the selected source")
    DEL_MSG = _("Delete the selected source")
    MERGE_MSG = _("Merge the selected sources")
    FILTER_TYPE = "Source"
    QR_CATEGORY = CATEGORY_QR_SOURCE

    def __init__(self, pdata, dbstate, uistate, nav_group=0):

        signal_map = {
            'source-add'     : self.row_add,
            'source-update'  : self.row_update,
            'source-delete'  : self.row_delete,
            'source-rebuild' : self.object_build,
            }

        ListView.__init__(
            self, _('Sources'), pdata, dbstate, uistate,
            SourceModel, signal_map,
            SourceBookmarks, nav_group,
            multiple=True,
            filter_class=SourceSidebarFilter)

        self.func_list.update({
            '<PRIMARY>J' : self.jump,
            '<PRIMARY>BackSpace' : self.key_delete,
            })

        self.additional_uis.append(self.additional_ui())

    def navigation_type(self):
        return 'Source'

    def drag_info(self):
        return DdTargets.SOURCE_LINK

    def define_actions(self):
        ListView.define_actions(self)
        self._add_action('FilterEdit', None, _('Source Filter Editor'),
                         callback=self.filter_editor,)
        self._add_action('QuickReport', None, _("Quick View"), None, None, None)

    def get_stock(self):
        return 'gramps-source'

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
            <menu name="QuickReport" action="QuickReport"/>
          </popup>
        </ui>'''

    def add(self, obj):
        EditSource(self.dbstate, self.uistate, [], Source())

    def remove(self, obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        the_lists = get_source_and_citation_referents(handle, self.dbstate.db)
        LOG.debug('the_lists %s' % [the_lists])

        object = self.dbstate.db.get_source_from_handle(handle)
        query = DeleteSrcQuery(self.dbstate, self.uistate, object, the_lists)
        is_used = any(the_lists)
        return (query, is_used, object)

    def edit(self, obj):
        for handle in self.selected_handles():
            source = self.dbstate.db.get_source_from_handle(handle)
            try:
                EditSource(self.dbstate, self.uistate, [], source)
            except WindowActiveError:
                pass

    def merge(self, obj):
        """
        Merge the selected sources.
        """
        mlist = self.selected_handles()

        if len(mlist) != 2:
            msg = _("Cannot merge sources.")
            msg2 = _("Exactly two sources must be selected to perform a merge. "
                     "A second source can be selected by holding down the "
                     "control key while clicking on the desired source.")
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
            links = set([link[1] for link in
                         self.dbstate.db.find_backlink_handles(tag_handle,
                                                include_classes='Source')])
            all_links = all_links.union(links)
        self.row_update(list(all_links))

    def add_tag(self, transaction, source_handle, tag_handle):
        """
        Add the given tag to the given source.
        """
        source = self.dbstate.db.get_source_from_handle(source_handle)
        source.add_tag(tag_handle)
        self.dbstate.db.commit_source(source, transaction)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Source Filter",),
                ("Source Gallery",
                 "Source Notes",
                 "Source Backlinks"))
