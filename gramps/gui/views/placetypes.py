# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010    Nick Hall
#               2020    Paul Culley
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
Provide PlaceType editing functionality.
"""
# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------

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
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.lib import PlaceType
from gramps.gen.db import DbTxn
from gramps.gen.const import URL_MANUAL_PAGE
from ..display import display_help
import gramps.gui.widgets.progressdialog as progressdlg
from gramps.gui.widgets.placetypeselector import PlaceTypeSelector
from gramps.gui.widgets.monitoredwidgets import MonitoredDataType
from ..uimanager import ActionGroup
from ..managedwindow import ManagedWindow


WIKI_HELP_PAGE = "%s_-_Filters" % URL_MANUAL_PAGE
WIKI_HELP_SEC2 = _("manual|Replace_PlaceType_dialog")
WIKI_HELP_SEC3 = _("manual|Assign_PlaceGroup_dialog")


# -------------------------------------------------------------------------
#
# ReplacePlaceType dialog
#
# -------------------------------------------------------------------------
class ReplacePlaceType(ManagedWindow):
    """
    A dialog to enable the user to replace a place type.
    """

    def __init__(self, dbstate, uistate):
        view = uistate.viewmanager.active_page
        self.selected = view.selected_handles()
        if not self.selected:
            return
        self.db = dbstate.db
        place = self.db.get_place_from_handle(self.selected[0])
        self.title = _("Replace Place Type")
        ManagedWindow.__init__(self, uistate, [], self.__class__, modal=True)
        # the self.top.run() below makes Gtk make it modal, so any change to
        # the previous line's "modal" would require that line to be changed
        self.top = Gtk.Dialog(transient_for=self.parent_window)
        self.top.vbox.set_spacing(5)

        grid = Gtk.Grid()
        self.top.vbox.pack_start(grid, True, True, 10)

        # Original type
        cbe_o = Gtk.ComboBox(has_entry=True)
        self.o_ptype = place.get_type()
        self.orig = PlaceTypeSelector(dbstate, cbe_o, self.o_ptype)
        label = Gtk.Label(label=_("Original Place Type:"))
        grid.attach(label, 0, 0, 1, 1)
        grid.attach(cbe_o, 1, 0, 1, 1)

        # replacement type
        cbe_n = Gtk.ComboBox(has_entry=True)
        self.ptype_n = PlaceType("")

        self.sel = PlaceTypeSelector(dbstate, cbe_n, self.ptype_n)
        label = Gtk.Label(label=_("Replacement Place Type:"))
        grid.attach(label, 0, 1, 1, 1)
        grid.attach(cbe_n, 1, 1, 1, 1)

        self.top.add_button(_("_Help"), Gtk.ResponseType.HELP)
        self.top.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.top.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.set_window(self.top, None, self.title)
        self.show()
        self.run()

    def build_menu_names(self, _obj):  # this is meaningless while it's modal
        return (self.title, None)

    def run(self):
        """
        Run the dialog and return the result.
        """
        while True:
            # the self.top.run() makes Gtk make it modal, so any change to that
            # line would require the ManagedWindow.__init__ to be changed also
            response = self.top.run()
            if response == Gtk.ResponseType.HELP:
                display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC2)
            else:
                break

        if response == Gtk.ResponseType.OK:
            self._save()
        if response != Gtk.ResponseType.DELETE_EVENT:
            self.close()

    def _save(self):
        """
        start the process of replacing place types
        """
        # Make the dialog modal so that the user can't start another
        # database transaction while we are still running.
        pmon = progressdlg.ProgressMonitor(
            progressdlg.GtkProgressDialog,
            ("", self.uistate.window, Gtk.DialogFlags.MODAL),
            popup_time=2,
        )
        status = progressdlg.LongOpStatus(
            msg=_("Replacing place types"),
            total_steps=len(self.selected),
            interval=len(self.selected) // 20,
        )
        pmon.add_op(status)
        msg = _("Replace Place Type: (%s)") % str(self.o_ptype)
        with DbTxn(msg, self.db) as trans:
            for handle in self.selected:
                status.heartbeat()
                place = self.db.get_place_from_handle(handle)
                commit = False
                for ptype in place.get_types():
                    if ptype.is_same(self.o_ptype):
                        ptype.pt_id = self.ptype_n.pt_id
                        ptype.name = self.ptype_n.name
                        commit = True
                if commit:
                    self.db.commit_place(place, trans)
        status.end()


# -------------------------------------------------------------------------
#
# AssignPlaceGroup dialog
#
# -------------------------------------------------------------------------
class AssignPlaceGroup(ManagedWindow):
    """
    A dialog to enable the user to assign a place group.
    """

    def __init__(self, dbstate, uistate):
        view = uistate.viewmanager.active_page
        self.selected = view.selected_handles()
        if not self.selected:
            return
        self.db = dbstate.db
        self.place = self.db.get_place_from_handle(self.selected[0])
        self.title = _("Assign Place Group")
        ManagedWindow.__init__(self, uistate, [], self.__class__, modal=True)
        # the self.top.run() below makes Gtk make it modal, so any change to
        # the previous line's "modal" would require that line to be changed
        self.top = Gtk.Dialog(transient_for=self.parent_window)
        self.top.vbox.set_spacing(5)

        grid = Gtk.Grid()
        self.top.vbox.pack_start(grid, True, True, 10)

        #  Group
        cbe = Gtk.ComboBox(has_entry=True)

        custom_placegroup_types = sorted(
            self.db.get_placegroup_types(), key=lambda s: s.lower()
        )
        self.place_group = MonitoredDataType(
            cbe, self.place.set_group, self.place.get_group, custom_placegroup_types
        )
        label = Gtk.Label(label=_("Place Group:"))
        grid.attach(label, 0, 0, 1, 1)
        grid.attach(cbe, 1, 0, 1, 1)

        self.top.add_button(_("_Help"), Gtk.ResponseType.HELP)
        self.top.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.top.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.set_window(self.top, None, self.title)
        self.show()
        self.run()

    def build_menu_names(self, _obj):  # this is meaningless while it's modal
        return (self.title, None)

    def run(self):
        """
        Run the dialog and return the result.
        """
        while True:
            # the self.top.run() makes Gtk make it modal, so any change to that
            # line would require the ManagedWindow.__init__ to be changed also
            response = self.top.run()
            if response == Gtk.ResponseType.HELP:
                display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC3)
            else:
                break

        if response == Gtk.ResponseType.OK:
            self._save()
        if response != Gtk.ResponseType.DELETE_EVENT:
            self.close()

    def _save(self):
        """
        start the process of replacing place types
        """
        # get group
        group = self.place.group

        # Make the dialog modal so that the user can't start another
        # database transaction while we are still running.
        pmon = progressdlg.ProgressMonitor(
            progressdlg.GtkProgressDialog,
            ("", self.uistate.window, Gtk.DialogFlags.MODAL),
            popup_time=2,
        )
        status = progressdlg.LongOpStatus(
            msg=_("Assigning place Groups"),
            total_steps=len(self.selected),
            interval=len(self.selected) // 20,
        )
        pmon.add_op(status)
        msg = _("Assign Place Group: (%s)") % str(group)
        with DbTxn(msg, self.db) as trans:
            for handle in self.selected:
                status.heartbeat()
                place = self.db.get_place_from_handle(handle)
                place.group = group
                self.db.commit_place(place, trans)
        status.end()
