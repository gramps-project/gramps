#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017       Nick Hall
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
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..managedwindow import ManagedWindow
from ..glade import Glade
from ..listmodel import ListModel
from gramps.gen.errors import ValidationError
from gramps.gen.display.place import displayer as _pd
from gramps.gen.display.place import PlaceFormat
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# EditPlaceFormat
#
# -------------------------------------------------------------------------
class EditPlaceFormat(ManagedWindow):
    def __init__(self, uistate, dbstate, track, callback):
        self.title = _("Place Format Editor")
        ManagedWindow.__init__(self, uistate, track, EditPlaceFormat)
        self.callback = callback
        self.top = Glade()
        self.set_window(self.top.toplevel, None, self.title, None)
        self.setup_configs("interface.editplaceformat", 600, 400)
        self.top.get_object("add").connect("clicked", self.__add)
        self.top.get_object("remove").connect("clicked", self.__remove)
        self.top.get_object("name").connect("changed", self.__name_changed)
        self.top.get_object("levels").connect("validate", self._validate)
        self.window.connect("response", self.__close)
        self.model = None
        self.formats = _pd.get_formats()
        self.current_format = None
        self.__populate_format_list()
        self.show()

    def build_menu_names(self, obj):
        return (self.title, None)

    def __populate_format_list(self):
        flist = self.top.get_object("format_list")
        self.model = ListModel(
            flist, [(_("Format"), -1, 100)], select_func=self.__format_changed
        )
        for fmt in self.formats:
            self.model.add([fmt.name])
        self.model.select_row(0)

    def __format_changed(self, selection):
        if self.current_format is not None:
            fmt = self.formats[self.current_format]
            self.__save_format(fmt)
        row = self.model.get_selected_row()
        if row != -1:
            fmt = self.formats[row]
            self.__load_format(fmt)
            self.current_format = row
        if row == 0:
            self.top.get_object("remove").set_sensitive(False)
            self.top.get_object("name").set_sensitive(False)
            self.top.get_object("levels").set_sensitive(False)
            self.top.get_object("street").set_sensitive(False)
            self.top.get_object("language").set_sensitive(False)
            self.top.get_object("reverse").set_sensitive(False)
        else:
            self.top.get_object("remove").set_sensitive(True)
            self.top.get_object("name").set_sensitive(True)
            self.top.get_object("levels").set_sensitive(True)
            self.top.get_object("street").set_sensitive(True)
            self.top.get_object("language").set_sensitive(True)
            self.top.get_object("reverse").set_sensitive(True)
        self.top.get_object("levels").validate(force=True)

    def __name_changed(self, entry):
        store, iter_ = self.model.get_selected()
        self.model.set(iter_, [entry.get_text()])

    def _validate(self, widget, text):
        for level in text.split(","):
            parts = level.split(":")
            if len(parts) < 1:
                return ValidationError("Empty level")
            if len(parts) > 2:
                return ValidationError("Invalid slice")
            for part in parts:
                integer_str = part.replace("p", "")
                if integer_str != "":
                    try:
                        integer = int(integer_str)
                    except ValueError:
                        return ValidationError("Invalid format string")

    def __load_format(self, fmt):
        self.top.get_object("name").set_text(fmt.name)
        self.top.get_object("levels").set_text(fmt.levels)
        self.top.get_object("street").set_active(fmt.street)
        self.top.get_object("language").set_text(fmt.language)
        self.top.get_object("reverse").set_active(fmt.reverse)

    def __save_format(self, fmt):
        fmt.name = self.top.get_object("name").get_text()
        fmt.levels = self.top.get_object("levels").get_text()
        fmt.street = self.top.get_object("street").get_active()
        fmt.language = self.top.get_object("language").get_text()
        fmt.reverse = self.top.get_object("reverse").get_active()

    def __add(self, button):
        name = _("New")
        self.formats.append(PlaceFormat(name, ":", "", 0, False))
        self.model.add([name])
        self.model.select_row(len(self.formats) - 1)

    def __remove(self, button):
        store, iter_ = self.model.get_selected()
        if iter_:
            self.current_format = None
            del self.formats[self.model.get_selected_row()]
            self.model.remove(iter_)
        if self.model.get_selected_row() == -1:
            self.model.select_row(len(self.formats) - 1)

    def __close(self, *obj):
        row = self.model.get_selected_row()
        fmt = self.formats[self.current_format]
        self.__save_format(fmt)
        _pd.save_formats()
        self.callback()
        self.close()
