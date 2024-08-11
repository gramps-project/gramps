#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2009       Gary Burton
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
# python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from .editsecondary import EditSecondary
from ..widgets import MonitoredEntry, PrivacyButton, MonitoredDataType
from ..glade import Glade
from gramps.gen.const import URL_MANUAL_SECT1

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT1
WIKI_HELP_SEC = _("Internet_Address_Editor", "manual")


# -------------------------------------------------------------------------
#
# EditUrl class
#
# -------------------------------------------------------------------------
class EditUrl(EditSecondary):
    def __init__(self, dbstate, uistate, track, name, url, callback):
        EditSecondary.__init__(self, dbstate, uistate, track, url, callback)

    def _local_init(self):
        self.top = Glade()
        self.jump = self.top.get_object("jump")

        self.set_window(
            self.top.toplevel,
            self.top.get_object("title"),
            _("Internet Address Editor"),
        )
        self.setup_configs("interface.url", 600, 150)

    def _connect_signals(self):
        self.jump.connect("clicked", self.jump_to)
        self.define_cancel_button(self.top.get_object("button125"))
        self.define_ok_button(self.top.get_object("button124"), self.save)
        # TODO help button (rename glade button name)
        self.define_help_button(
            self.top.get_object("button130"), WIKI_HELP_PAGE, WIKI_HELP_SEC
        )

    def jump_to(self, obj):
        if self.obj.get_path():
            from ..display import display_url

            display_url(self.obj.get_path())

    def _setup_fields(self):
        self.des = MonitoredEntry(
            self.top.get_object("url_des"),
            self.obj.set_description,
            self.obj.get_description,
            self.db.readonly,
        )

        self.addr = MonitoredEntry(
            self.top.get_object("url_addr"),
            self.obj.set_path,
            self.obj.get_path,
            self.db.readonly,
        )

        self.priv = PrivacyButton(
            self.top.get_object("priv"), self.obj, self.db.readonly
        )

        self.type_sel = MonitoredDataType(
            self.top.get_object("type"),
            self.obj.set_type,
            self.obj.get_type,
            self.db.readonly,
            self.db.get_url_types(),
        )

    def build_menu_names(self, obj):
        etitle = _("Internet Address Editor")
        return (etitle, etitle)

    def save(self, *obj):
        self.callback(self.obj)
        self.close()
