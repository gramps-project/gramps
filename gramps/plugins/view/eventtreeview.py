# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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
Event Tree View
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Event
from gramps.gui.editors import EditEvent
from gramps.gui.views.treemodels import EventTreeModel
from .eventview import EventView


# -------------------------------------------------------------------------
#
# EventTreeView
#
# -------------------------------------------------------------------------
class EventTreeView(EventView):
    """
    A hierarchical view of events, showing sub-events under their
    super-event.
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        EventView.__init__(
            self, pdata, dbstate, uistate, nav_group, model_class=EventTreeModel
        )

    def get_viewtype_stock(self):
        """
        Override the default icon. Set for hierarchical view.
        """
        return "gramps-tree-group"

    def define_actions(self):
        """
        Define actions for the popup menu specific to the tree view.
        """
        EventView.define_actions(self)

        self._add_action("OpenBranch", self.open_branch)
        self._add_action("CloseBranch", self.close_branch)
        self._add_action("OpenAllNodes", self.open_all_nodes)
        self._add_action("CloseAllNodes", self.close_all_nodes)

    additional_ui = EventView.additional_ui[:]
    additional_ui.append(
        """
        <section id="PopUpTree">
          <item>
            <attribute name="action">win.OpenBranch</attribute>
            <attribute name="label" translatable="yes">"""
        """Expand this Entire Group</attribute>
          </item>
          <item>
            <attribute name="action">win.CloseBranch</attribute>
            <attribute name="label" translatable="yes">"""
        """Collapse this Entire Group</attribute>
          </item>
          <item>
            <attribute name="action">win.OpenAllNodes</attribute>
            <attribute name="label" translatable="yes">"""
        """Expand all Nodes</attribute>
          </item>
          <item>
            <attribute name="action">win.CloseAllNodes</attribute>
            <attribute name="label" translatable="yes">"""
        """Collapse all Nodes</attribute>
          </item>
        </section>
        """
    )

    def add(self, *obj):
        """
        Add a new event. If a single event is selected, use it as the new
        event's super-event (the "Part of" tab lets the user add further
        super-events or remove this one).
        """
        event = Event()
        selected = self.selected_handles()
        if len(selected) == 1:
            event.add_super_event(selected[0])

        try:
            EditEvent(self.dbstate, self.uistate, [], event)
        except WindowActiveError:
            pass

    def row_update(self, handle_list):
        """
        Called when an event is updated.
        """
        EventView.row_update(self, handle_list)

        for handle in handle_list:
            # Rebuild the model if the primary super-event has changed.
            if self._significant_change(handle):
                self.build_tree()
                break

    def _significant_change(self, handle):
        """
        Return True if the primary super-event is different from the
        parent displayed in the tree, or if there are children.
        The first occurs if a change moves a sub-event to a different
        super-event, the second if a change to a super-event occurs (a
        description change might shift position in the tree).
        """
        new_handle = None
        event = self.dbstate.db.get_event_from_handle(handle)
        super_event_list = event.get_super_event_list()
        if len(super_event_list) > 0:
            new_handle = super_event_list[0]

        old_handle = None
        children = False
        iter_ = self.model.get_iter_from_handle(handle)
        if iter_:
            parent_iter = self.model.iter_parent(iter_)
            if parent_iter:
                old_handle = self.model.get_handle_from_iter(parent_iter)
            children = self.model.get_node_from_iter(iter_).children
        return new_handle != old_handle or children

    def get_config_name(self):
        return __name__
