#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2014-2015  Nick Hall
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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .editsecondary import EditSecondary
from ..glade import Glade
from ..widgets import MonitoredDate, MonitoredEntry
from ..dialog import ErrorDialog
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# EditPlaceName class
#
#-------------------------------------------------------------------------
class EditPlaceName(EditSecondary):
    """
    Displays a dialog that allows the user to edit a place name.
    """
    def __init__(self, dbstate, uistate, track, pname, callback):
        EditSecondary.__init__(self, dbstate, uistate, track, pname, callback)

    def _local_init(self):
        self.width_key = 'interface.place-name-width'
        self.height_key = 'interface.place-name-height'

        self.top = Glade()
        self.set_window(self.top.toplevel,
                        self.top.get_object("title"),
                        _('Place Name Editor'))

    def _setup_fields(self):
        self.value = MonitoredEntry(
            self.top.get_object("value"), self.obj.set_value,
            self.obj.get_value, self.db.readonly)

        self.date = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_stat"),
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)

        self.language = MonitoredEntry(
            self.top.get_object("language"), self.obj.set_language,
            self.obj.get_language, self.db.readonly)

    def _connect_signals(self):
        self.define_help_button(self.top.get_object('help'))
        self.define_cancel_button(self.top.get_object('cancel'))
        self.define_ok_button(self.top.get_object('ok'),self.save)

    def build_menu_names(self, obj):
        return (_('Place Name'),_('Place Name Editor'))

    def save(self, *obj):
        if not self.obj.get_value():
            ErrorDialog(_("Cannot save place name"),
                _("The place name cannot be empty"),
                parent=self.window)
            return

        if self.callback:
            self.callback(self.obj)
        self.close()
