#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010       Nick Hall
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

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from .editsecondary import EditSecondary
from ..glade import Glade
from ..widgets import MonitoredEntry
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# EditLocation class
#
# -------------------------------------------------------------------------
class EditLocation(EditSecondary):
    def __init__(self, dbstate, uistate, track, location, callback):
        EditSecondary.__init__(self, dbstate, uistate, track, location, callback)

    def _local_init(self):
        self.top = Glade()
        self.set_window(self.top.toplevel, None, _("Location Editor"))
        self.setup_configs("interface.location", 600, 250)

    def _setup_fields(self):
        self.street = MonitoredEntry(
            self.top.get_object("street"),
            self.obj.set_street,
            self.obj.get_street,
            self.db.readonly,
        )

        self.locality = MonitoredEntry(
            self.top.get_object("locality"),
            self.obj.set_locality,
            self.obj.get_locality,
            self.db.readonly,
        )

        self.city = MonitoredEntry(
            self.top.get_object("city"),
            self.obj.set_city,
            self.obj.get_city,
            self.db.readonly,
        )

        self.state = MonitoredEntry(
            self.top.get_object("state"),
            self.obj.set_state,
            self.obj.get_state,
            self.db.readonly,
        )

        self.postal = MonitoredEntry(
            self.top.get_object("postal"),
            self.obj.set_postal_code,
            self.obj.get_postal_code,
            self.db.readonly,
        )

        self.phone = MonitoredEntry(
            self.top.get_object("phone"),
            self.obj.set_phone,
            self.obj.get_phone,
            self.db.readonly,
        )

        self.parish = MonitoredEntry(
            self.top.get_object("parish"),
            self.obj.set_parish,
            self.obj.get_parish,
            self.db.readonly,
        )

        self.county = MonitoredEntry(
            self.top.get_object("county"),
            self.obj.set_county,
            self.obj.get_county,
            self.db.readonly,
        )

        self.country = MonitoredEntry(
            self.top.get_object("country"),
            self.obj.set_country,
            self.obj.get_country,
            self.db.readonly,
        )

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object("button119"))
        self.define_ok_button(self.top.get_object("button118"), self.save)
        self.define_help_button(self.top.get_object("button128"))

    def save(self, *obj):
        if self.callback:
            self.callback(self.obj)
        self.close()
