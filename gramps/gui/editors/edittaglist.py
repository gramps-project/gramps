#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010        Nick Hall
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
Tag editing module for Gramps.
"""
# -------------------------------------------------------------------------
#
# GNOME modules
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
from ..managedwindow import ManagedWindow
from gramps.gen.const import URL_MANUAL_PAGE
from ..display import display_help
from ..listmodel import ListModel, TOGGLE

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = "%s_-_Filters" % URL_MANUAL_PAGE
WIKI_HELP_SEC = _("Tag_selection_dialog", "manual")


# -------------------------------------------------------------------------
#
# EditTagList
#
# -------------------------------------------------------------------------
class EditTagList(ManagedWindow):
    """
    Dialog to allow the user to edit a list of tags.
    """

    def __init__(self, tag_list, full_list, uistate, track):
        """
        Initiate and display the dialog.
        """
        ManagedWindow.__init__(self, uistate, track, self, modal=True)
        # the self.window.run() below makes Gtk make it modal, so any change
        # to the previous line's "modal" would require that line to be changed

        self.namemodel = None
        top = self._create_dialog()
        self.set_window(top, None, _("Tag selection"))
        self.setup_configs("interface.edittaglist", 360, 400)

        for tag in full_list:
            self.namemodel.add([tag[0], tag in tag_list, tag[1]])
        self.namemodel.connect_model()

        # The dialog is modal.  We don't want to have several open dialogs of
        # this type, since then the user will loose track of which is which.
        self.return_list = None
        self.show()

        while True:
            # the self.window.run() makes Gtk make it modal, so any change to
            # that line means the ManagedWindow.__init__ must be changed also
            response = self.window.run()
            if response == Gtk.ResponseType.HELP:
                display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)
            elif response == Gtk.ResponseType.DELETE_EVENT:
                break
            else:
                if response == Gtk.ResponseType.OK:
                    self.return_list = [
                        (row[0], row[2]) for row in self.namemodel.model if row[1]
                    ]
                self.close()
                break

    def _create_dialog(self):
        """
        Create a dialog box to select tags.
        """
        # pylint: disable-msg=E1101
        top = Gtk.Dialog(transient_for=self.uistate.window)
        top.vbox.set_spacing(5)

        columns = [
            ("", -1, 300),
            (" ", -1, 25, TOGGLE, True, None),
            (_("Tag"), -1, 300),
        ]
        view = Gtk.TreeView()
        self.namemodel = ListModel(view, columns)

        slist = Gtk.ScrolledWindow()
        slist.add(view)
        slist.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        top.vbox.pack_start(slist, 1, 1, 5)

        top.add_button(_("_Help"), Gtk.ResponseType.HELP)
        top.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        top.add_button(_("_OK"), Gtk.ResponseType.OK)
        return top

    def build_menu_names(self, obj):  # meaningless while it's modal
        """
        Define the menu entry for the ManagedWindows.
        """
        return (_("Tag selection"), None)
