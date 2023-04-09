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

"""AttrEmbedList"""

# -------------------------------------------------------------------------
#
# GTK classes
#
# -------------------------------------------------------------------------
from gi.repository import GLib

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Attribute
from gramps.gui.ddtargets import DdTargets
from .attrmodel import AttrModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# AttrEmbedList
#
# -------------------------------------------------------------------------
class AttrEmbedList(EmbeddedList):
    """
    Class to handle embedded attribute lists.
    """

    _HANDLE_COL = 6
    _DND_TYPE = DdTargets.ATTRIBUTE

    _MSG = {
        "add": _("Create and add a new attribute"),
        "del": _("Remove the existing attribute"),
        "edit": _("Edit the selected attribute"),
        "up": _("Move the selected attribute upwards"),
        "down": _("Move the selected attribute downwards"),
    }

    # index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_("Type"), 0, 250, TEXT_COL, -1, None),
        (_("Value"), 1, 200, TEXT_COL, -1, None),
        (_("Date"), 5, 180, MARKUP_COL, -1, None),
        (_("Source"), 3, 30, ICON_COL, -1, "gramps-source"),
        (_("Private"), 4, 30, ICON_COL, -1, "gramps-lock"),
        (_("Sorted date"), 5, 80, TEXT_COL, -1, None),
    ]

    def __init__(self, dbstate, uistate, track, data):
        """
        Initialize the displaytab. The dbstate and uistate is needed
        track is the list of parent windows
        data is an attribute_list (as obtained by AttributeBase) to display and
            edit
        """
        self.data = data
        EmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            _("_Attributes"),
            AttrModel,
            move_buttons=True,
        )

    def get_editor(self):
        """
        Return editor.
        """
        from .. import EditAttribute
        return EditAttribute

    def get_user_values(self):
        """
        Return custom types.
        """
        return self.dbstate.db.get_person_attribute_types()

    def get_icon_name(self):
        """
        Return icon name.
        """
        return "gramps-attribute"

    def get_data(self):
        """
        Return data.
        """
        return self.data

    def column_order(self):
        """
        Return column display order.
        """
        return ((1, 3), (1, 4), (1, 0), (1, 1), (1, 2))

    def add_button_clicked(self, obj):
        """
        Handle add button click.
        """
        pname = ""
        attr = Attribute()
        try:
            self.get_editor()(
                self.dbstate,
                self.uistate,
                self.track,
                attr,
                pname,
                self.get_user_values(),
                self.add_callback,
            )
        except WindowActiveError:
            pass

    def add_callback(self, name):
        """
        Post add handler.
        """
        data = self.get_data()
        data.append(name)
        self.changed = True
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        """
        Handle edit button click.
        """
        attr = self.get_selected()
        if attr:
            pname = ""
            try:
                self.get_editor()(
                    self.dbstate,
                    self.uistate,
                    self.track,
                    attr,
                    pname,
                    self.get_user_values(),
                    self.edit_callback,
                )
            except WindowActiveError:
                pass

    def edit_callback(self, _cb_name):
        """
        Post edit handler.
        """
        self.changed = True
        self.rebuild()
