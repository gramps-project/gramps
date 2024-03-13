#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021    Matthias Kemmer
# Copyright (C) 2024-   Serge Noiraud
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
"""Collection of classes creating a multi-select listbox for menu options."""


# -------------------------------------------------------------------------
#
# GTK Modules
#
# -------------------------------------------------------------------------
from collections import defaultdict
from gi.repository import Gtk  # type: ignore
from gramps.plugins.webreport.common import get_surname_from_person

# ------------------------------------------------------------------------
#
# GRAMPS modules
#
# ------------------------------------------------------------------------
from gramps.gen.lib import EventType  # type: ignore
from gramps.gen.plug.menu import Option as PlugOption  # type: ignore
from gramps.gui.widgets.multitreeview import MultiTreeView
from gramps.gen.const import GRAMPS_LOCALE as glocale

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# MultiSelectOption Class for events
#
# ------------------------------------------------------------------------
class MultiSelectEvents(PlugOption):
    """Extending gramps.gen.plug.menu._option.Option"""

    def __init__(self, label, value):
        PlugOption.__init__(self, label, value)


# ------------------------------------------------------------------------
#
# MultiSelectOption Class for surnames
#
# ------------------------------------------------------------------------
class MultiSelectSurnames(PlugOption):
    """Extending gramps.gen.plug.menu._option.Option"""

    def __init__(self, label, value):
        PlugOption.__init__(self, label, value)


# ------------------------------------------------------------------------
#
# MultiSelectOption Class for tags
#
# ------------------------------------------------------------------------
class MultiSelectTags(PlugOption):
    """Extending gramps.gen.plug.menu._option.Option"""

    def __init__(self, label, value):
        PlugOption.__init__(self, label, value)


# ------------------------------------------------------------------------
#
# HeatmapScrolled Class for events
#
# ------------------------------------------------------------------------
class HeatmapEventsScrolled(Gtk.ScrolledWindow):
    """Extending Gtk.ScrolledWindow."""

    def __init__(self, option, dbstate, uistate, track, override=False):
        Gtk.ScrolledWindow.__init__(self)
        self.set_min_content_height(60)  # Real size of the scrolled window
        self.add(HeatmapEventsMultiTreeView(dbstate, option))


# ------------------------------------------------------------------------
#
# HeatmapScrolled Class for surnames
#
# ------------------------------------------------------------------------
class HeatmapSurnamesScrolled(Gtk.ScrolledWindow):
    """Extending Gtk.ScrolledWindow."""

    def __init__(self, option, dbstate, uistate, track, override=False):
        Gtk.ScrolledWindow.__init__(self)
        self.set_min_content_height(60)  # Real size of the scrolled window
        self.add(HeatmapSurnamesMultiTreeView(dbstate, option))


# ------------------------------------------------------------------------
#
# HeatmapScrolled Class for tags
#
# ------------------------------------------------------------------------
class HeatmapTagsScrolled(Gtk.ScrolledWindow):
    """Extending Gtk.ScrolledWindow."""

    def __init__(self, option, dbstate, uistate, track, override=False):
        Gtk.ScrolledWindow.__init__(self)
        self.set_min_content_height(60)  # Real size of the scrolled window
        self.add(HeatmapTagsMultiTreeView(dbstate, option))


# ------------------------------------------------------------------------
#
# HeatmapMultiTreeView Class for events
#
# ------------------------------------------------------------------------
class HeatmapEventsMultiTreeView(MultiTreeView):
    """Extending gramps.gui.widgets.multitreeview."""

    def __init__(self, dbstate, option):
        MultiTreeView.__init__(self)
        self.db = dbstate.db
        self.option = option
        self.get_selection().set_mode(Gtk.SelectionMode.NONE)
        self.selected_rows = list()

        # Event types data
        default_types = [name[1] for name in EventType._DATAMAP]
        custom_types = [name for name in self.db.get_event_types()]
        self.data = sorted([*default_types, *custom_types])

        # Setup columns
        model = Gtk.ListStore(bool, str)
        self.set_model(model)

        toggle_renderer = Gtk.CellRendererToggle()
        toggle_renderer.set_property("activatable", True)
        toggle_renderer.connect("toggled", self.toggle, 0)
        col_check = Gtk.TreeViewColumn("", toggle_renderer)
        col_check.add_attribute(toggle_renderer, "active", 0)
        self.append_column(col_check)

        col_name = Gtk.TreeViewColumn(_("Event type"), Gtk.CellRendererText(), text=1)
        self.append_column(col_name)

        # Fill columns with data
        for item in self.data:
            model.append([False, item])

        self.load_last_values()

    def load_last_values(self):
        for row in self.option.get_value():
            self.get_model()[row][0] = True

    def toggle(self, _, row, col):
        is_activated = self.get_model()[row][col]
        values = self.option.get_value()

        if is_activated:
            values.remove(row)
        else:
            values.append(row)

        self.option.set_value(values)

        # Invert the checkbox value
        self.get_model()[row][col] = not self.get_model()[row][col]


# ------------------------------------------------------------------------
#
# HeatmapMultiTreeView Class for surnames
#
# ------------------------------------------------------------------------
class HeatmapSurnamesMultiTreeView(MultiTreeView):
    """Extending gramps.gui.widgets.multitreeview."""

    def __init__(self, dbstate, option):
        MultiTreeView.__init__(self)
        self.db = dbstate.db
        self.option = (
            option  # should contains the list of people like [self.obj_dict[Person]]
        )
        self.get_selection().set_mode(Gtk.SelectionMode.NONE)
        self.selected_rows = list()

        # Surnames list
        data = get_surnames_list(self.db)

        # Setup columns
        model = Gtk.ListStore(bool, str)
        self.set_model(model)

        toggle_renderer = Gtk.CellRendererToggle()
        toggle_renderer.set_property("activatable", True)
        toggle_renderer.connect("toggled", self.toggle, 0)
        col_check = Gtk.TreeViewColumn("", toggle_renderer)
        col_check.add_attribute(toggle_renderer, "active", 0)
        self.append_column(col_check)

        col_name = Gtk.TreeViewColumn(_("Event type"), Gtk.CellRendererText(), text=1)
        self.append_column(col_name)

        # Fill columns with data
        index = 1
        for item in sorted(data, key=lambda x: x[1], reverse=True):
            if index > 10:  # Show only the 10 largest group of people
                break
            model.append([False, item[0] + " (" + str(item[1]) + ")"])
            index += 1

        self.load_last_values()

    def load_last_values(self):
        for row in self.option.get_value():
            self.get_model()[row][0] = True

    def toggle(self, _, row, col):
        is_activated = self.get_model()[row][col]
        values = self.option.get_value()

        if is_activated:
            values.remove(row)
        else:
            values.append(row)

        self.option.set_value(values)

        # Invert the checkbox value
        self.get_model()[row][col] = not self.get_model()[row][col]


def get_surnames_list(db):
    # Assemble all the handles for each surname into a dictionary
    # We don't call sort_people because we don't care about sorting
    # individuals, only surnames
    iter_persons = (
        db.iter_person_handles()
    )  # All persons in the database. no filtering.
    surname_handle_dict = defaultdict(list)
    for person_handle in iter_persons:
        person = db.get_person_from_handle(person_handle)
        surname = get_surname_from_person(db, person)
        surname_handle_dict[surname].append(person_handle)
    # count_ppl_handle_dict = {}
    # count_ppl_handle_dict = defaultdict(list)
    count_ppl_handle = []
    for surname, data_list in surname_handle_dict.items():
        # count_ppl_handle_dict[len(data_list)].append(
        count_ppl_handle.append((surname, len(data_list), data_list))
    return count_ppl_handle


# ------------------------------------------------------------------------
#
# HeatmapMultiTreeView Class for tags
#
# ------------------------------------------------------------------------
class HeatmapTagsMultiTreeView(MultiTreeView):
    """Extending gramps.gui.widgets.multitreeview."""

    def __init__(self, dbstate, option):
        MultiTreeView.__init__(self)
        self.db = dbstate.db
        self.option = option
        self.get_selection().set_mode(Gtk.SelectionMode.NONE)
        self.selected_rows = list()

        # Tags
        data = get_tags_list(self.db)

        # Setup columns
        model = Gtk.ListStore(bool, str)
        self.set_model(model)

        toggle_renderer = Gtk.CellRendererToggle()
        toggle_renderer.set_property("activatable", True)
        toggle_renderer.connect("toggled", self.toggle, 0)
        col_check = Gtk.TreeViewColumn("", toggle_renderer)
        col_check.add_attribute(toggle_renderer, "active", 0)
        self.append_column(col_check)

        col_name = Gtk.TreeViewColumn(_("Tag"), Gtk.CellRendererText(), text=1)
        self.append_column(col_name)

        # Fill columns with data
        for item in data:
            model.append([False, item[0]])

        self.load_last_values()

    def load_last_values(self):
        for row in self.option.get_value():
            self.get_model()[row][0] = True

    def toggle(self, _, row, col):
        is_activated = self.get_model()[row][col]
        values = self.option.get_value()

        if is_activated:
            values.remove(row)
        else:
            values.append(row)

        self.option.set_value(values)

        # Invert the checkbox value
        self.get_model()[row][col] = not self.get_model()[row][col]


def get_tags_list(db):
    tag_list = []
    for handle in db.get_tag_handles(sort_handles=True):
        tag = db.get_tag_from_handle(handle)
        tag_list.append((tag.get_name(), tag.get_handle()))
    data = sorted([*tag_list])
    return data
