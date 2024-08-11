#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"""
Address List display tab.
"""

# -------------------------------------------------------------------------
#
# Python classes
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gi.repository import GObject, GLib

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Address
from gramps.gen.errors import WindowActiveError
from ...ddtargets import DdTargets
from .addressmodel import AddressModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
class AddrEmbedList(EmbeddedList):
    """
    Address List display tab for edit dialogs.

    Derives from the EmbeddedList class.
    """

    _HANDLE_COL = 10
    _DND_TYPE = DdTargets.ADDRESS

    _MSG = {
        "add": _("Create and add a new address"),
        "del": _("Remove the existing address"),
        "edit": _("Edit the selected address"),
        "up": _("Move the selected address upwards"),
        "down": _("Move the selected address downwards"),
    }

    # index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_("Date"), 0, 150, MARKUP_COL, -1, None),
        (_("Street"), 1, 225, TEXT_COL, -1, None),
        (_("Locality"), 2, 100, TEXT_COL, -1, None),
        (_("City"), 3, 100, TEXT_COL, -1, None),
        (_("State/County"), 4, 100, TEXT_COL, -1, None),
        (_("Country"), 5, 75, TEXT_COL, -1, None),
        (_("Postal"), 6, 75, TEXT_COL, -1, None),
        (_("Phone"), 7, 150, TEXT_COL, -1, None),
        (_("Source"), 8, 30, ICON_COL, -1, "gramps-source"),
        (_("Private"), 9, 30, ICON_COL, -1, "gramps-lock"),
    ]

    def __init__(self, dbstate, uistate, track, data, config_key):
        self.data = data
        EmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            _("_Addresses"),
            AddressModel,
            config_key,
            move_buttons=True,
        )

    def get_icon_name(self):
        """
        Return the stock-id icon name associated with the display tab
        """
        return "gramps-address"

    def get_data(self):
        """
        Return the data associated with display tab
        """
        return self.data

    def column_order(self):
        """
        Return the column order of the columns in the display tab.
        """
        return (
            (1, 8),
            (1, 9),
            (1, 0),
            (1, 1),
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5),
            (1, 6),
            (1, 7),
        )

    def add_button_clicked(self, obj):
        """
        Called when the Add button is clicked. Creates a new Address instance
        and calls the EditAddress editor with the new address. If the window
        already exists (WindowActiveError), we ignore it. This prevents
        the dialog from coming up twice on the same object.
        """
        addr = Address()
        try:
            from .. import EditAddress

            EditAddress(self.dbstate, self.uistate, self.track, addr, self.add_callback)
        except WindowActiveError:
            return

    def add_callback(self, name):
        """
        Called to update the screen when a new address is added
        """
        data = self.get_data()
        data.append(name)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        """
        Called with the Edit button is clicked. Gets the selected Address instance
        and calls the EditAddress editor with the address. If the window
        already exists (WindowActiveError), we ignore it. This prevents
        the dialog from coming up twice on the same object.
        """
        addr = self.get_selected()
        if addr:
            try:
                from .. import EditAddress

                EditAddress(
                    self.dbstate, self.uistate, self.track, addr, self.edit_callback
                )
            except WindowActiveError:
                return

    def edit_callback(self, name):
        """
        Called to update the screen when the address changes
        """
        self.rebuild()
