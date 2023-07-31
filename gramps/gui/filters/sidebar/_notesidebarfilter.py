#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
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
# Python modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# gtk
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ... import widgets
from gramps.gen.lib import Note, NoteType
from .. import build_filter_model
from . import SidebarFilter
from gramps.gen.filters import GenericFilterFactory, rules
from gramps.gen.filters.rules.note import RegExpIdOf, HasNote, MatchesFilter, HasTag

GenericNoteFilter = GenericFilterFactory("Note")


# -------------------------------------------------------------------------
#
# NoteSidebarFilter class
#
# -------------------------------------------------------------------------
class NoteSidebarFilter(SidebarFilter):
    def __init__(self, dbstate, uistate, clicked):
        self.clicked_func = clicked
        self.filter_id = widgets.BasicEntry()
        self.filter_text = widgets.BasicEntry()
        self.note = Note()
        self.note.set_type((NoteType.CUSTOM, ""))
        self.ntype = Gtk.ComboBox(has_entry=True)
        if dbstate.is_open():
            self.custom_types = dbstate.db.get_note_types()
        else:
            self.custom_types = []

        self.event_menu = widgets.MonitoredDataType(
            self.ntype,
            self.note.set_type,
            self.note.get_type,
            False,  # read-only?
            self.custom_types,
        )

        self.filter_regex = Gtk.CheckButton(label=_("Use regular expressions"))
        self.sensitive_regex = Gtk.CheckButton(label=_("Case sensitive"))

        self.tag = Gtk.ComboBox()
        self.generic = Gtk.ComboBox()

        SidebarFilter.__init__(self, dbstate, uistate, "Note")

    def create_widget(self):
        cell = Gtk.CellRendererText()
        cell.set_property("width", self._FILTER_WIDTH)
        cell.set_property("ellipsize", self._FILTER_ELLIPSIZE)
        self.generic.pack_start(cell, True)
        self.generic.add_attribute(cell, "text", 0)
        self.on_filters_changed("Note")

        cell = Gtk.CellRendererText()
        cell.set_property("width", self._FILTER_WIDTH)
        cell.set_property("ellipsize", self._FILTER_ELLIPSIZE)
        self.tag.pack_start(cell, True)
        self.tag.add_attribute(cell, "text", 0)

        self.ntype.get_child().set_width_chars(5)

        self.add_text_entry(_("ID"), self.filter_id)
        self.add_text_entry(_("Text"), self.filter_text)
        self.add_entry(_("Type"), self.ntype)
        self.add_entry(_("Tag"), self.tag)
        self.add_filter_entry(_("Custom filter"), self.generic)
        self.add_regex_entry(self.filter_regex)
        self.add_regex_case(self.sensitive_regex)

    def clear(self, obj):
        self.filter_id.set_text("")
        self.filter_text.set_text("")
        self.ntype.get_child().set_text("")
        self.tag.set_active(0)
        self.generic.set_active(0)

    def get_filter(self):
        gid = str(self.filter_id.get_text()).strip()
        text = str(self.filter_text.get_text()).strip()
        ntype = self.note.get_type().xml_str()
        regex = self.filter_regex.get_active()
        usecase = self.sensitive_regex.get_active()
        tag = self.tag.get_active() > 0
        gen = self.generic.get_active() > 0

        empty = not (gid or text or ntype or regex or tag or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericNoteFilter()
            if gid:
                rule = RegExpIdOf([gid], use_regex=regex, use_case=usecase)
                generic_filter.add_rule(rule)

            rule = HasNote([text, ntype], use_regex=regex, use_case=usecase)
            generic_filter.add_rule(rule)

            # check the Tag
            if tag:
                model = self.tag.get_model()
                node = self.tag.get_active_iter()
                attr = model.get_value(node, 0)
                rule = HasTag([attr])
                generic_filter.add_rule(rule)

            if self.generic.get_active() != 0:
                model = self.generic.get_model()
                node = self.generic.get_active_iter()
                obj = str(model.get_value(node, 0))
                rule = MatchesFilter([obj])
                generic_filter.add_rule(rule)

        return generic_filter

    def on_filters_changed(self, name_space):
        if name_space == "Note":
            all_filter = GenericNoteFilter()
            all_filter.set_name(_("None"))
            all_filter.add_rule(rules.note.AllNotes([]))
            self.generic.set_model(build_filter_model("Note", [all_filter]))
            self.generic.set_active(0)

    def on_tags_changed(self, tag_list):
        """
        Update the list of tags in the tag filter.
        """
        model = Gtk.ListStore(str)
        model.append(("",))
        for tag_name in tag_list:
            model.append((tag_name,))
        self.tag.set_model(model)
        self.tag.set_active(0)
