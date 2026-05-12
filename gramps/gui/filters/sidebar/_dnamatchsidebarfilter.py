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

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

from gi.repository import Gtk

from ... import widgets
from . import SidebarFilter
from gramps.gen.filters import GenericFilterFactory
from gramps.gen.filters.rules.dnamatch import (
    RegExpIdOf,
    HasTag,
    HasDNAMatch,
    HasSharedCm,
)

GenericDNAMatchFilter = GenericFilterFactory("DNAMatch")


# -------------------------------------------------------------------------
#
# DNAMatchSidebarFilter class
#
# -------------------------------------------------------------------------
class DNAMatchSidebarFilter(SidebarFilter):
    def __init__(self, dbstate, uistate, clicked):
        self.clicked_func = clicked
        self.filter_id = widgets.BasicEntry()
        self.filter_subject_person = widgets.BasicEntry()
        self.filter_subject_account = widgets.BasicEntry()
        self.filter_match_person = widgets.BasicEntry()
        self.filter_match_account = widgets.BasicEntry()
        self.filter_min_cm = widgets.BasicEntry()
        self.filter_max_cm = widgets.BasicEntry()

        self.filter_regex = Gtk.CheckButton(label=_("Use regular expressions"))
        self.sensitive_regex = Gtk.CheckButton(label=_("Case sensitive"))

        self.tag = Gtk.ComboBox()

        SidebarFilter.__init__(self, dbstate, uistate, "DNAMatch")
        self.vbox.remove(self.define_filter_btn.get_parent())

    def create_widget(self):
        cell = Gtk.CellRendererText()
        cell.set_property("width", self._FILTER_WIDTH)
        cell.set_property("ellipsize", self._FILTER_ELLIPSIZE)
        self.tag.pack_start(cell, True)
        self.tag.add_attribute(cell, "text", 0)

        self.add_text_entry(_("ID"), self.filter_id)
        self.add_text_entry(_("Subject person"), self.filter_subject_person)
        self.add_text_entry(_("Subject account name"), self.filter_subject_account)
        self.add_text_entry(_("Match person"), self.filter_match_person)
        self.add_text_entry(_("Match account name"), self.filter_match_account)
        self.add_text_entry(_("Shared cM min"), self.filter_min_cm)
        self.add_text_entry(_("Shared cM max"), self.filter_max_cm)
        self.add_entry(_("Tag"), self.tag)
        self.add_regex_entry(self.filter_regex)
        self.add_regex_case(self.sensitive_regex)

    def clear(self, obj):
        self.filter_id.set_text("")
        self.filter_subject_person.set_text("")
        self.filter_subject_account.set_text("")
        self.filter_match_person.set_text("")
        self.filter_match_account.set_text("")
        self.filter_min_cm.set_text("")
        self.filter_max_cm.set_text("")
        self.tag.set_active(0)

    def get_filter(self):
        gid = str(self.filter_id.get_text()).strip()
        subject_person = str(self.filter_subject_person.get_text()).strip()
        subject_account = str(self.filter_subject_account.get_text()).strip()
        match_person = str(self.filter_match_person.get_text()).strip()
        match_account = str(self.filter_match_account.get_text()).strip()
        min_cm = str(self.filter_min_cm.get_text()).strip()
        max_cm = str(self.filter_max_cm.get_text()).strip()
        regex = self.filter_regex.get_active()
        usecase = self.sensitive_regex.get_active()
        tag = self.tag.get_active() > 0

        empty = not (
            gid
            or subject_person
            or subject_account
            or match_person
            or match_account
            or min_cm
            or max_cm
            or regex
            or tag
        )
        if empty:
            return None

        generic_filter = GenericDNAMatchFilter()

        if gid:
            rule = RegExpIdOf([gid], use_regex=regex, use_case=usecase)
            generic_filter.add_rule(rule)

        if subject_person or subject_account or match_person or match_account:
            rule = HasDNAMatch(
                [subject_person, subject_account, match_person, match_account],
                use_regex=regex,
                use_case=usecase,
            )
            generic_filter.add_rule(rule)

        if min_cm or max_cm:
            rule = HasSharedCm([min_cm, max_cm])
            generic_filter.add_rule(rule)

        if tag:
            model = self.tag.get_model()
            node = self.tag.get_active_iter()
            attr = model.get_value(node, 0)
            rule = HasTag([attr])
            generic_filter.add_rule(rule)

        return generic_filter

    def on_tags_changed(self, tag_list):
        model = Gtk.ListStore(str)
        model.append(("",))
        for tag_name in tag_list:
            model.append((tag_name,))
        self.tag.set_model(model)
        self.tag.set_active(0)
