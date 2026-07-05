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
# GTK libraries
#
# -------------------------------------------------------------------------
from gi.repository import Gtk


# -------------------------------------------------------------------------
#
# SuperEventModel
#
# -------------------------------------------------------------------------
class SuperEventModel(Gtk.ListStore):
    """
    Model backing the "Part of" list on the event editor.

    Each row shows the Gramps ID, type, and description of a super-event
    referenced by handle in the event's super_event_list.
    """

    def __init__(self, handle_list, db):
        Gtk.ListStore.__init__(self, str, str, str, str)
        self.db = db
        for handle in handle_list:
            event = self.db.get_event_from_handle(handle)
            self.append(
                row=[
                    event.get_gramps_id(),
                    str(event.get_type()),
                    event.get_description(),
                    handle,
                ]
            )
