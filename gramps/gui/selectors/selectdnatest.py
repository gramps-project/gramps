#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Selector dialog for DNATest objects.
"""

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gi.repository import Gtk

from gramps.gen.display.name import displayer as name_displayer


# -------------------------------------------------------------------------
#
# SelectDNATest
#
# -------------------------------------------------------------------------
class SelectDNATest:
    """
    Dialog for selecting an existing DNATest record.

    Returns the selected DNATest object from run(), or None if cancelled.
    This is a standalone implementation because the tree model needed by
    BaseSelector does not exist until Milestone 4.
    """

    def __init__(self, dbstate, uistate, track, **kwargs):
        self.dbstate = dbstate
        self.uistate = uistate
        self.track = track

    def run(self):
        """Show the selector dialog and return the chosen DNATest or None."""
        db = self.dbstate.db
        parent = self.uistate.window if self.uistate else None

        dialog = Gtk.Dialog(
            title=_("Select DNA Test"),
            transient_for=parent,
            flags=0,
        )
        dialog.add_buttons(
            _("_Cancel"),
            Gtk.ResponseType.CANCEL,
            _("_Select"),
            Gtk.ResponseType.OK,
        )
        dialog.set_default_size(600, 400)
        dialog.set_default_response(Gtk.ResponseType.OK)

        # TreeView with columns: Person, Account name, Provider, Test type, ID
        store = Gtk.ListStore(str, str, str, str, str, object)

        for test in db.iter_dnatests():
            if test.get_person_handle():
                person = db.get_person_from_handle(test.get_person_handle())
                person_name = name_displayer.display(person) if person else _("Unknown")
            else:
                person_name = _("(unidentified)")
            store.append(
                [
                    person_name,
                    test.get_account_name(),
                    str(test.get_provider()),
                    str(test.get_test_type()),
                    test.gramps_id or "",
                    test,
                ]
            )

        treeview = Gtk.TreeView(model=store)
        treeview.set_search_column(1)

        for idx, title in enumerate(
            [_("Person"), _("Account name"), _("Provider"), _("Test type"), _("ID")]
        ):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=idx)
            col.set_resizable(True)
            col.set_sort_column_id(idx)
            treeview.append_column(col)

        treeview.connect("row-activated", lambda tv, path, col: dialog.response(Gtk.ResponseType.OK))

        selection = treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.SINGLE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(treeview)

        dialog.get_content_area().pack_start(scroll, True, True, 6)
        dialog.show_all()

        result = None
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            model, tree_iter = selection.get_selected()
            if tree_iter:
                result = model[tree_iter][5]

        dialog.destroy()
        return result
