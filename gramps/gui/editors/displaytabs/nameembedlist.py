#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2009       Benny Malengier
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
# Python classes
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib

# -------------------------------------------------------------------------
#
# Python classes
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Name, Surname
from gramps.gen.errors import WindowActiveError
from ...ddtargets import DdTargets
from .namemodel import NameModel
from .embeddedlist import TEXT_COL, MARKUP_COL, ICON_COL
from .groupembeddedlist import GroupEmbeddedList


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
class NameEmbedList(GroupEmbeddedList):
    _HANDLE_COL = 2
    _DND_TYPE = DdTargets.NAME
    _WORKGROUP = NameModel.ALTINDEX

    _MSG = {
        "add": _("Create and add a new name"),
        "del": _("Remove the existing name"),
        "edit": _("Edit the selected name"),
        "up": _("Move the selected name upwards"),
        "down": _("Move the selected name downwards"),
    }

    # index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_("Name"), -1, 250, TEXT_COL, NameModel.COL_FONTWEIGHT[0], None),
        (_("Type"), NameModel.COL_TYPE[0], 100, TEXT_COL, -1, None),
        None,
        None,
        (_("Group As"), NameModel.COL_GROUPAS[0], 100, TEXT_COL, -1, None),
        (_("Source"), NameModel.COL_HASSOURCE[0], 30, ICON_COL, -1, "gramps-source"),
        (_("Notes Preview"), NameModel.COL_NOTEPREVIEW[0], 250, TEXT_COL, -1, None),
        (_("Private"), NameModel.COL_PRIVATE[0], 30, ICON_COL, -1, "gramps-lock"),
    ]

    def __init__(self, dbstate, uistate, track, data, person, config_key, callback):
        """callback is the function to call when preferred name changes
        on the namelist"""
        self.data = data
        self.person = person
        self.callback = callback

        GroupEmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            _("_Names"),
            NameModel,
            config_key,
            move_buttons=True,
        )
        self.tree.expand_all()

    def _cleanup_on_exit(self):
        """Unset all things that can block garbage collection.
        Finalize rest
        """
        self.person = None
        self.callback = None
        self.data = None

    def get_data(self):
        return ([self.person.get_primary_name()], self.data)

    def groups(self):
        """
        Return the (group key, group name)s in the order as given by get_data()
        """
        return ((None, NameModel.DEFNAME), (None, NameModel.ALTNAME))

    def column_order(self):
        """
        The columns to show as a tuple of tuples containing
        tuples (show/noshow, model column)
        """
        return ((1, 0), (1, 5), (1, 7), (1, 1), (1, 4), (1, 6))

    def get_popup_menu_items(self):
        if self._tmpgroup == self._WORKGROUP:
            return [
                (True, _("_Add"), self.add_button_clicked),
                (False, _("_Edit"), self.edit_button_clicked),
                (True, _("_Remove"), self.del_button_clicked),
                (True, _("Set as default name"), self.name_button_clicked),
            ]
        else:
            return [
                (True, _("_Add"), self.add_button_clicked),
                (False, _("_Edit"), self.edit_button_clicked),
            ]

    def name_button_clicked(self, obj):
        name = self.get_selected()
        if name and name[1]:
            self.set_default_name(name[1])

    def set_default_name(self, name):
        pname = self.person.get_primary_name()
        self.person.set_primary_name(name)
        remove = [altname for altname in self.data if altname.is_equal(name)]
        list(map(self.data.remove, remove))
        # only non empty name should move to alternative names
        if not name.is_equal(Name()):
            self.data.append(pname)
        self.rebuild()
        self.callback()

    def update_defname(self):
        """
        callback from person editor if change to the preferred name happens
        """
        self.model.update_defname(self.person.get_primary_name())
        self.tree.expand_all()

    def add_button_clicked(self, obj):
        name = Name()
        # the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        try:
            from .. import EditName

            EditName(self.dbstate, self.uistate, self.track, name, self.add_callback)
        except WindowActiveError:
            pass

    def add_callback(self, name):
        data = self.get_data()[self._WORKGROUP]
        data.append(name)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, (self._WORKGROUP, len(data) - 1))

    def edit_button_clicked(self, obj):
        name = self.get_selected()
        if name and name[1] is not None:
            try:
                from .. import EditName

                if name[0] == NameModel.ALTINDEX:
                    EditName(
                        self.dbstate,
                        self.uistate,
                        self.track,
                        name[1],
                        self.edit_callback,
                    )
                elif name[0] == NameModel.DEFINDEX:
                    EditName(
                        self.dbstate,
                        self.uistate,
                        self.track,
                        name[1],
                        self.editdef_callback,
                    )
            except WindowActiveError:
                pass

    def edit_callback(self, name):
        self.rebuild()

    def editdef_callback(self, name):
        """
        callback after default name has changed
        """
        self.rebuild()
        self.callback()

    def dropnotworkgroup(self, row, obj):
        """
        Drop of obj on row that is not WORKGROUP
        """
        if row[0] == NameModel.DEFINDEX:
            # drop on default name
            self.set_default_name(obj)

    def move_away_work(self, row_from, row_to, obj):
        """
        move from the workgroup to a not workgroup
        we allow to change the default name like this
        """
        if row_from[0] == self._WORKGROUP and row_to[0] == NameModel.DEFINDEX:
            self.set_default_name(obj)

    def post_rebuild(self, prebuildpath):
        """
        Allow post rebuild specific handling.
        @param prebuildpath: path selected before rebuild, None if none
        @type prebuildpath: tree path
        """
        self.tree.expand_all()
        if prebuildpath is not None:
            self.selection.select_path(prebuildpath)
