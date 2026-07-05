#
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

# -------------------------------------------------------------------------
#
# Python classes
#
# -------------------------------------------------------------------------
from gi.repository import GLib

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.lib import Event
from gramps.gen.errors import WindowActiveError
from .embeddedlist import EmbeddedList, TEXT_COL
from .supereventmodel import SuperEventModel
from ...selectors import SelectorFactory
from ...dbguielement import DbGUIElement


# -------------------------------------------------------------------------
#
# SuperEventEmbedList
#
# -------------------------------------------------------------------------
class SuperEventEmbedList(DbGUIElement, EmbeddedList):
    """
    Displays the "Part of" list: the super-events of the event being
    edited, i.e. the events this one is a sub-event of.
    """

    _HANDLE_COL = 3
    _DND_TYPE = None

    _column_names = [
        (_("ID"), 0, 75, TEXT_COL, -1, None),
        (_("Type"), 1, 100, TEXT_COL, -1, None),
        (_("Description"), 2, 250, TEXT_COL, -1, None),
    ]

    def __init__(self, dbstate, uistate, track, data, config_key, handle, callback):
        self.data = data
        self.handle = handle
        self.callback = callback
        DbGUIElement.__init__(self, dbstate.db)
        EmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            _("Part of"),
            SuperEventModel,
            config_key,
            share_button=True,
            move_buttons=True,
        )

    def _connect_db_signals(self):
        """
        called on init of DbGUIElement, connect to db as required.
        """
        # note: event-rebuild closes the editors, so no need to connect to it
        self.callman.register_callbacks(
            {
                "event-update": self.event_change,  # change to event we track
                "event-delete": self.event_delete,  # delete of event we track
            }
        )
        self.callman.connect_all(keys=["event"])

    def event_change(self, *obj):
        """
        Callback method called when a tracked super-event changes (type,
        description, ...).
        """
        self.rebuild()

    def event_delete(self, hndls):
        """
        Callback method called when a tracked super-event is deleted.
        Remove it from the list so no dangling reference is shown.
        """
        for handle in hndls:
            if handle in self.data:
                self.data.remove(handle)
        self.rebuild()

    def get_data(self):
        self.callman.register_handles({"event": list(self.data)})
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2))

    def get_icon_name(self):
        return "gramps-event"

    def get_skip_list(self, handle):
        """
        Return the handles that must not be offered as a super-event for
        handle: itself, its own (recursive) sub-events -- selecting one of
        those would close a cycle -- and events already in the list.
        """
        todo = [handle]
        skip = [handle]
        while todo:
            current = todo.pop()
            for _cls, child in self.dbstate.db.find_backlink_handles(
                current, ["Event"]
            ):
                if child not in skip:
                    todo.append(child)
                    skip.append(child)
        for existing in self.data:
            if existing not in skip:
                skip.append(existing)
        return skip

    def add_button_clicked(self, obj):
        event = Event()
        try:
            from .. import EditEvent

            EditEvent(self.dbstate, self.uistate, self.track, event, self.add_callback)
        except WindowActiveError:
            pass

    def add_callback(self, event):
        self._add_super_event(event.get_handle())

    def share_button_clicked(self, obj):
        SelectEvent = SelectorFactory("Event")

        sel = SelectEvent(
            self.dbstate, self.uistate, self.track, skip=self.get_skip_list(self.handle)
        )
        event = sel.run()
        if event:
            self._add_super_event(event.get_handle())

    def _add_super_event(self, handle):
        data = self.get_data()
        if handle in data:
            return
        data.append(handle)
        self.changed = True
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        handle = self.get_selected()
        if handle:
            event = self.dbstate.db.get_event_from_handle(handle)
            try:
                from .. import EditEvent

                EditEvent(self.dbstate, self.uistate, self.track, event)
            except WindowActiveError:
                pass

    def post_rebuild(self, prebuildpath):
        self.callback()
