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
from gramps.gen.lib.dnatest import DNATest
from gramps.gen.lib.dnaprovidertype import DNAProviderType
from gramps.gen.lib.dnatesttype import DNATestType
from . import SidebarFilter
from gramps.gen.filters import GenericFilterFactory
from gramps.gen.filters.rules.dnatest import (
    RegExpIdOf,
    HasTag,
    HasDNATest,
    HasProvider,
    HasTestType,
    IsUnidentified,
)

GenericDNATestFilter = GenericFilterFactory("DNATest")

_CHROMOSOMES = [str(i) for i in range(1, 23)] + ["X", "Y", "MT"]


# -------------------------------------------------------------------------
#
# DNATestSidebarFilter class
#
# -------------------------------------------------------------------------
class DNATestSidebarFilter(SidebarFilter):
    def __init__(self, dbstate, uistate, clicked):
        self.clicked_func = clicked
        self.filter_id = widgets.BasicEntry()
        self.filter_person = widgets.BasicEntry()
        self.filter_account = widgets.BasicEntry()
        self.filter_kit = widgets.BasicEntry()
        self.filter_haplogroup = widgets.BasicEntry()

        self._dnatest = DNATest()
        self._dnatest.set_provider((DNAProviderType.CUSTOM, ""))
        self._dnatest.set_test_type((DNATestType.CUSTOM, ""))

        self.provider_combo = Gtk.ComboBox(has_entry=True)
        self.provider_menu = widgets.MonitoredDataType(
            self.provider_combo,
            self._dnatest.set_provider,
            self._dnatest.get_provider,
            False,
            [],
        )

        self.testtype_combo = Gtk.ComboBox(has_entry=True)
        self.testtype_menu = widgets.MonitoredDataType(
            self.testtype_combo,
            self._dnatest.set_test_type,
            self._dnatest.get_test_type,
            False,
            [],
        )

        self.filter_unidentified = Gtk.CheckButton(label=_("Unidentified only"))
        self.filter_regex = Gtk.CheckButton(label=_("Use regular expressions"))
        self.sensitive_regex = Gtk.CheckButton(label=_("Case sensitive"))

        self.tag = Gtk.ComboBox()

        SidebarFilter.__init__(self, dbstate, uistate, "DNATest")
        self.vbox.remove(self.define_filter_btn.get_parent())

    def create_widget(self):
        cell = Gtk.CellRendererText()
        cell.set_property("width", self._FILTER_WIDTH)
        cell.set_property("ellipsize", self._FILTER_ELLIPSIZE)
        self.tag.pack_start(cell, True)
        self.tag.add_attribute(cell, "text", 0)

        self.provider_combo.get_child().set_width_chars(5)
        self.testtype_combo.get_child().set_width_chars(5)

        self.add_text_entry(_("ID"), self.filter_id)
        self.add_text_entry(_("Person"), self.filter_person)
        self.add_text_entry(_("Account name"), self.filter_account)
        self.add_text_entry(_("Kit ID"), self.filter_kit)
        self.add_entry(_("Provider"), self.provider_combo)
        self.add_entry(_("Test type"), self.testtype_combo)
        self.add_text_entry(_("Haplogroup"), self.filter_haplogroup)

        hbox = Gtk.Box()
        hbox.pack_start(self.filter_unidentified, False, False, 12)
        self.vbox.pack_start(hbox, False, False, 0)

        self.add_entry(_("Tag"), self.tag)
        self.add_regex_entry(self.filter_regex)
        self.add_regex_case(self.sensitive_regex)

    def clear(self, obj):
        self.filter_id.set_text("")
        self.filter_person.set_text("")
        self.filter_account.set_text("")
        self.filter_kit.set_text("")
        self.filter_haplogroup.set_text("")
        self.provider_combo.get_child().set_text("")
        self.testtype_combo.get_child().set_text("")
        self.filter_unidentified.set_active(False)
        self.tag.set_active(0)

    def get_filter(self):
        gid = str(self.filter_id.get_text()).strip()
        person = str(self.filter_person.get_text()).strip()
        account = str(self.filter_account.get_text()).strip()
        kit = str(self.filter_kit.get_text()).strip()
        haplogroup = str(self.filter_haplogroup.get_text()).strip()
        provider = self._dnatest.get_provider().xml_str()
        testtype = self._dnatest.get_test_type().xml_str()
        unidentified = self.filter_unidentified.get_active()
        regex = self.filter_regex.get_active()
        usecase = self.sensitive_regex.get_active()
        tag = self.tag.get_active() > 0

        empty = not (
            gid
            or person
            or account
            or kit
            or haplogroup
            or provider
            or testtype
            or unidentified
            or regex
            or tag
        )
        if empty:
            return None

        generic_filter = GenericDNATestFilter()

        if gid:
            rule = RegExpIdOf([gid], use_regex=regex, use_case=usecase)
            generic_filter.add_rule(rule)

        if person or account or kit or haplogroup:
            rule = HasDNATest(
                [person, account, kit, haplogroup],
                use_regex=regex,
                use_case=usecase,
            )
            generic_filter.add_rule(rule)

        if provider:
            rule = HasProvider([provider])
            generic_filter.add_rule(rule)

        if testtype:
            rule = HasTestType([testtype])
            generic_filter.add_rule(rule)

        if unidentified:
            rule = IsUnidentified([])
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
