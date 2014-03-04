#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2014       Nick Hall
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
from ..managedwindow import ManagedWindow
from ..dialog import ErrorDialog
from ..display import display_help
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# EditPlaceName class
#
#-------------------------------------------------------------------------
class EditPlaceName(ManagedWindow):

    def __init__(self, dbstate, uistate, track, data, index, callback):
        ManagedWindow.__init__(self, uistate, track, self.__class__)

        self.data = data
        self.index = index
        self.callback = callback

        self.width_key = 'interface.place-name-width'
        self.height_key = 'interface.place-name-height'

        window = Gtk.Dialog('', uistate.window,
                            Gtk.DialogFlags.DESTROY_WITH_PARENT, None)

        self.cancel_button = window.add_button(Gtk.STOCK_CANCEL,
                                              Gtk.ResponseType.CANCEL)
        self.ok_button = window.add_button(Gtk.STOCK_OK,
                                             Gtk.ResponseType.ACCEPT)
        self.help_button = window.add_button(Gtk.STOCK_HELP,
                                              Gtk.ResponseType.HELP)

        window.connect('response', self.response)
        self.set_window(window, None, _('Place Name Editor'))

        hbox = Gtk.HBox()
        label = Gtk.Label(_('Place Name:'))
        self.entry = Gtk.Entry()
        if index >= 0:
            self.entry.set_text(data[index])
        hbox.pack_start(label, False, False, 4)
        hbox.pack_start(self.entry, True, True, 4)
        hbox.show_all()
        window.vbox.pack_start(hbox, False, False, 4)

        self._set_size()
        self.show()

    def response(self, obj, response_id):
        if response_id == Gtk.ResponseType.CANCEL:
            self.close()
        if response_id == Gtk.ResponseType.ACCEPT:
            self.save()
        if response_id == Gtk.ResponseType.HELP:
            display_help('', '')

    def save(self, *obj):
        place_name = self.entry.get_text()
        if not place_name:
            ErrorDialog(_("Cannot save place name"),
                _("The place name cannot be empty"))
            return
        if self.index >= 0:
            self.data[self.index] = place_name
        else:
            self.data.append(place_name)
        if self.callback:
            self.callback(place_name)
        self.close()
