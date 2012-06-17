# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
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
Provide the event view.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _
import logging
_LOG = logging.getLogger(".plugins.eventview")

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
import gen.lib
from gui.views.listview import ListView
from gui.views.treemodels import EventModel
import Utils
from gen.errors import WindowActiveError
from gui.views.bookmarks import EventBookmarks
from gen.config import config
from gui.ddtargets import DdTargets
from gui.dialog import ErrorDialog
from gui.editors import EditEvent, DeleteEventQuery
from gui.filters.sidebar import EventSidebarFilter
from gui.merge import MergeEvent
from gen.plug import CATEGORY_QR_EVENT

#-------------------------------------------------------------------------
#
# EventView
#
#-------------------------------------------------------------------------
class EventView(ListView):
    """
    EventView class, derived from the ListView
    """
    # columns in the model used in view
    COL_DESCR = 0
    COL_ID = 1
    COL_TYPE = 2
    COL_DATE = 3
    COL_PLACE = 4
    COL_CHAN = 5
    COL_PARTIC = 6
    # name of the columns
    COLUMN_NAMES = [
        _('Description'),
        _('ID'),
        _('Type'),
        _('Date'),
        _('Place'),
        _('Last Changed'),
        _('Main Participants'),
        ]
    # columns that contain markup
    MARKUP_COLS = [COL_DATE]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_DESCR, COL_ID, COL_TYPE, COL_DATE, COL_PLACE]),
        ('columns.rank', [COL_DESCR, COL_ID, COL_TYPE, COL_PARTIC, COL_DATE,
                           COL_PLACE, COL_CHAN]),
        ('columns.size', [200, 75, 100, 230, 150, 200, 100])
        )    
    ADD_MSG     = _("Add a new event")
    EDIT_MSG    = _("Edit the selected event")
    DEL_MSG     = _("Delete the selected event")
    MERGE_MSG   = _("Merge the selected events")
    FILTER_TYPE = "Event"
    QR_CATEGORY = CATEGORY_QR_EVENT

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        """
        Create the Event View
        """
        signal_map = {
            'event-add'     : self.row_add,
            'event-update'  : self.row_update,
            'event-delete'  : self.row_delete,
            'event-rebuild' : self.object_build,
            }

        ListView.__init__(
            self, _('Events'), pdata, dbstate, uistate,
            EventView.COLUMN_NAMES, len(EventView.COLUMN_NAMES), 
            EventModel,
            signal_map, dbstate.db.get_event_bookmarks(),
            EventBookmarks, nav_group,
            multiple=True,
            filter_class=EventSidebarFilter,
            markup = EventView.MARKUP_COLS)
            
        self.func_list.update({
            '<CONTROL>J' : self.jump,
            '<CONTROL>BackSpace' : self.key_delete,
            })

        uistate.connect('nameformat-changed', self.build_tree)

        self.additional_uis.append(self.additional_ui())

    def navigation_type(self):
        return 'Event'

    def get_bookmarks(self):
        """
        Return the bookmark object
        """
        return self.dbstate.db.get_event_bookmarks()

    def drag_info(self):
        """
        Indicate that the drag type is an EVENT
        """
        return DdTargets.EVENT

    def get_stock(self):
        """
        Use the gramps-event stock icon
        """
        return 'gramps-event'

    def additional_ui(self):
        """
        Defines the UI string for UIManager
        """
        return '''<ui>
          <menubar name="MenuBar">
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
            <menu action="FileMenu">
              <placeholder name="LocalExport">
                <menuitem action="ExportTab"/>
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

    def define_actions(self):
        ListView.define_actions(self)
        self._add_action('FilterEdit', None, _('Event Filter Editor'),
                        callback=self.filter_editor,)
        self._add_action('QuickReport', None, 
                         _("Quick View"), None, None, None)
        self._add_action('Dummy', None, 
                         '  ', None, None, self.dummy_report)

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_event_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def add(self, obj):
        try:
            EditEvent(self.dbstate, self.uistate, [], gen.lib.Event())
        except WindowActiveError:
            pass

    def remove(self, obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        person_list = [
            item[1] for item in
            self.dbstate.db.find_backlink_handles(handle,['Person']) ]

        family_list = [ 
            item[1] for item in
            self.dbstate.db.find_backlink_handles(handle,['Family']) ]
        
        object = self.dbstate.db.get_event_from_handle(handle)

        query = DeleteEventQuery(self.dbstate, self.uistate, object, 
                                 person_list, family_list)
        is_used = len(person_list) + len(family_list) > 0
        return (query, is_used, object)

    def edit(self, obj):
        for handle in self.selected_handles():
            event = self.dbstate.db.get_event_from_handle(handle)
            try:
                EditEvent(self.dbstate, self.uistate, [], event)
            except WindowActiveError:
                pass

    def merge(self, obj):
        """
        Merge the selected events.
        """
        mlist = self.selected_handles()

        if len(mlist) != 2:
            msg = _("Cannot merge event objects.")
            msg2 = _("Exactly two events must be selected to perform a merge. "
                     "A second object can be selected by holding down the "
                     "control key while clicking on the desired event.")
            ErrorDialog(msg, msg2)
        else:
            MergeEvent(self.dbstate, self.uistate, mlist[0], mlist[1])

    def dummy_report(self, obj):
        """ For the xml UI definition of popup to work, the submenu 
            Quick Report must have an entry in the xml
            As this submenu will be dynamically built, we offer a dummy action
        """
        pass

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Event Filter",),
                ("Event Gallery",
                 "Event Citations",
                 "Event Notes",
                 "Event Attributes",
                 "Event Backlinks"))
