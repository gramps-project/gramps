#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021-      Serge Noiraud
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
# gui/columnorder.py

"""
Handle the csv format when exporting views
"""

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
import logging
import csv

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
#  -------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
__LOG = logging.getLogger(".CsvDialect")

CSV_DELIMITERS = {
    ",": ",",
    ";": ";",
    ":": ":",
    "|": "|",
    "\t": _("Tab", "character"),
}


class CsvDialect(Gtk.Box):
    """
    Use a custom format for csv export views
    """

    def __init__(self):
        """
        Used to set the csv dialect.
        We add the possibility to add a custom model where we
        can change the delimiter.
        """
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        hbox.set_spacing(10)
        hbox.pack_start(Gtk.Label(label=_("Choose your dialect")), False, False, 0)
        comment = Gtk.Label(
            label=_(
                "Changes are immediate.\n"
                "This is used when exporting views"
                " in CSV format."
            )
        )
        comment.set_justify(Gtk.Justification.LEFT)
        hbox.pack_start(comment, False, False, 0)
        hbox.pack_start(Gtk.Label(label=" "), False, True, 0)

        self.pack_start(hbox, True, True, 0)

        self.dialect = config.get("csv.dialect")
        self.delimiter = config.get("csv.delimiter")

        self.dialects = csv.list_dialects()
        self.dialects.append(_("Custom"))
        self.buttons = []
        button = None
        self.entry = Gtk.ComboBox()

        for dialect in self.dialects:
            title = dialect
            button = Gtk.RadioButton.new_with_mnemonic_from_widget(button, title)
            button.connect("toggled", self.on_toggled, self.entry)
            self.buttons.append(button)
            hbox.pack_start(button, False, True, 0)
            if dialect == self.dialect:
                button.set_active(True)

        lwidget = Gtk.Label(label=_("Delimiter:"))
        hbox.pack_start(lwidget, False, False, 0)

        store = Gtk.ListStore(str, str)
        default = 0
        for index, (key, value) in enumerate(CSV_DELIMITERS.items()):
            store.append((key, value))
            if key == self.delimiter:
                default = index
        self.entry.set_model(store)
        cell = Gtk.CellRendererText()
        self.entry.pack_start(cell, True)
        self.entry.add_attribute(cell, "text", 1)
        self.entry.set_active(default)
        self.entry.set_hexpand(False)
        self.entry.connect("changed", self.on_changed)
        hbox.pack_start(self.entry, False, True, 0)
        if self.dialect == _("Custom"):
            self.entry.set_sensitive(True)
        else:
            self.entry.set_sensitive(False)

    def on_changed(self, obj):
        """
        called when a button state change
        save is immediate
        """
        sep_iter = obj.get_active_iter()

        if sep_iter is not None:
            model = obj.get_model()
            sep = model[sep_iter][0]
            config.set("csv.delimiter", sep)

    def on_toggled(self, obj, entry):
        """
        called when a button state change
        save is immediate
        """
        if obj.get_active():
            button = obj.get_label()
            config.set("csv.dialect", button)
            if button == _("Custom"):
                entry.set_sensitive(True)
            else:
                entry.set_sensitive(False)
