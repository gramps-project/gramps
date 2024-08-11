#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013-2014  Nick Hall
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

"""Ancestors Gramplet"""

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.listmodel import ListModel, NOSORT
from gramps.gui.editors import EditPerson
from gramps.gen.errors import WindowActiveError
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.datehandler import get_date
from gramps.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gramps.gen.config import config
from gramps.gui.utils import model_to_text, text_to_clipboard

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


class Ancestor(Gramplet):
    """
    Gramplet to display ancestors of the active person.
    """

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.view = Gtk.TreeView()
        self.view.set_tooltip_column(3)
        titles = [
            (_("Name"), 0, 230),
            (_("Birth"), 2, 100),
            ("", NOSORT, 1),
            ("", NOSORT, 1),  # tooltip
            ("", NOSORT, 100),
        ]  # handle
        self.model = ListModel(
            self.view,
            titles,
            list_mode="tree",
            event_func=self.cb_double_click,
            right_click=self.cb_right_click,
        )
        return self.view

    def get_has_data(self, active_handle):
        """
        Return True if the gramplet has data, else return False.
        """
        if active_handle:
            person = self.dbstate.db.get_person_from_handle(active_handle)
            family_handle = person.get_main_parents_family_handle()
            if family_handle:
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family and (
                    family.get_father_handle() or family.get_mother_handle()
                ):
                    return True
        return False

    def cb_double_click(self, treeview):
        """
        Handle double click on treeview.
        """
        (model, iter_) = treeview.get_selection().get_selected()
        if not iter_:
            return

        try:
            handle = model.get_value(iter_, 4)
            person = self.dbstate.db.get_person_from_handle(handle)
            EditPerson(self.dbstate, self.uistate, [], person)
        except WindowActiveError:
            pass

    def cb_right_click(self, treeview, event):
        """
        Handle right click on treeview.
        """
        (model, iter_) = treeview.get_selection().get_selected()
        sensitivity = 1 if iter_ else 0
        menu = Gtk.Menu()
        menu.set_reserve_toggle_size(False)
        entries = [
            (_("Edit"), lambda obj: self.cb_double_click(treeview), sensitivity),
            (None, None, 0),
            (_("Copy all"), lambda obj: self.on_copy_all(treeview), 1),
        ]
        for title, callback, sensitivity in entries:
            item = Gtk.MenuItem(label=title)
            if callback:
                item.connect("activate", callback)
            else:
                item = Gtk.SeparatorMenuItem()
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        self.menu = menu
        self.menu.popup_at_pointer(event)

    def on_copy_all(self, treeview):
        """
        Copy tree to clipboard.
        """
        model = treeview.get_model()
        text = model_to_text(model, [0, 1], level=1)
        text_to_clipboard(text)

    def db_changed(self):
        self.update()

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active("Person")
        if active_handle:
            self.set_has_data(self.get_has_data(active_handle))
        else:
            self.set_has_data(False)

    def main(self):
        active_handle = self.get_active("Person")
        self.model.clear()
        if active_handle:
            self.add_to_tree(1, None, active_handle)
            self.view.expand_all()
            self.set_has_data(self.get_has_data(active_handle))
        else:
            self.set_has_data(False)

    def add_to_tree(self, depth, parent_id, person_handle):
        """
        Add a person to the tree.
        """
        if depth > config.get("behavior.generation-depth"):
            return

        person = self.dbstate.db.get_person_from_handle(person_handle)
        name = name_displayer.display(person)

        birth = get_birth_or_fallback(self.dbstate.db, person)
        death = get_death_or_fallback(self.dbstate.db, person)

        birth_text = birth_date = birth_sort = ""
        if birth:
            birth_date = get_date(birth)
            birth_sort = "%012d" % birth.get_date_object().get_sort_value()
            birth_text = _("%(abbr)s %(date)s") % {
                "abbr": birth.type.get_abbreviation(),
                "date": birth_date,
            }

        death_date = death_sort = death_text = ""
        if death:
            death_date = get_date(death)
            death_sort = "%012d" % death.get_date_object().get_sort_value()
            death_text = _("%(abbr)s %(date)s") % {
                "abbr": death.type.get_abbreviation(),
                "date": death_date,
            }

        tooltip = name + "\n" + birth_text + "\n" + death_text

        label = _("%(depth)s. %(name)s") % {"depth": depth, "name": name}
        item_id = self.model.add(
            [label, birth_date, birth_sort, tooltip, person_handle], node=parent_id
        )

        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.dbstate.db.get_family_from_handle(family_handle)
            if family:
                father_handle = family.get_father_handle()
                if father_handle:
                    self.add_to_tree(depth + 1, item_id, father_handle)
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    self.add_to_tree(depth + 1, item_id, mother_handle)

        return item_id
