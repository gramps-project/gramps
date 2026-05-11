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
Provide merge capabilities for DNA tests.
"""

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.datehandler import get_date
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.merge import MergeDNATestQuery
from ..display import display_help
from ..managedwindow import ManagedWindow

WIKI_HELP_PAGE = URL_MANUAL_PAGE
WIKI_HELP_SEC = _("Merge_DNA_Tests", "manual")
_GLADE_FILE = "mergednatest.glade"


# -------------------------------------------------------------------------
#
# MergeDNATest
#
# -------------------------------------------------------------------------
class MergeDNATest(ManagedWindow):
    """
    Displays a dialog box that allows two DNA test records to be merged.
    """

    def __init__(self, dbstate, uistate, track, handle1, handle2):
        ManagedWindow.__init__(self, uistate, track, self.__class__)
        self.dbstate = dbstate
        database = dbstate.db
        self.dt1 = database.get_dnatest_from_handle(handle1)
        self.dt2 = database.get_dnatest_from_handle(handle2)

        self.define_glade("mergednatest", _GLADE_FILE)
        self.set_window(
            self._gladeobj.toplevel,
            self.get_widget("dnatest_title"),
            _("Merge DNA Tests"),
        )
        self.setup_configs("interface.merge-dnatest", 700, 300)

        gramps1 = self.dt1.get_gramps_id()
        gramps2 = self.dt2.get_gramps_id()

        person1 = self._person_name(database, self.dt1.get_person_handle())
        person2 = self._person_name(database, self.dt2.get_person_handle())

        label1 = "%s [%s]" % (person1 or self.dt1.get_account_name(), gramps1)
        label2 = "%s [%s]" % (person2 or self.dt2.get_account_name(), gramps2)
        self.get_widget("label_handle_btn1").set_label(label1)
        self.get_widget("label_handle_btn2").set_label(label2)
        self.get_widget("handle_btn1").connect("toggled", self.on_handle1_toggled)

        self._init_field(
            "person1", "person2", "person_btn1", "person_btn2", person1, person2
        )
        self._init_field(
            "account1",
            "account2",
            "account_btn1",
            "account_btn2",
            self.dt1.get_account_name(),
            self.dt2.get_account_name(),
        )
        self._init_field(
            "provider1",
            "provider2",
            "provider_btn1",
            "provider_btn2",
            str(self.dt1.get_provider()),
            str(self.dt2.get_provider()),
        )
        self._init_field(
            "kit_id1",
            "kit_id2",
            "kit_id_btn1",
            "kit_id_btn2",
            self.dt1.get_kit_id(),
            self.dt2.get_kit_id(),
        )
        self._init_field(
            "test_type1",
            "test_type2",
            "test_type_btn1",
            "test_type_btn2",
            str(self.dt1.get_test_type()),
            str(self.dt2.get_test_type()),
        )
        self._init_field(
            "genome_build1",
            "genome_build2",
            "genome_build_btn1",
            "genome_build_btn2",
            str(self.dt1.get_genome_build()),
            str(self.dt2.get_genome_build()),
        )
        self._init_field(
            "haplogroup1",
            "haplogroup2",
            "haplogroup_btn1",
            "haplogroup_btn2",
            self.dt1.get_haplogroup(),
            self.dt2.get_haplogroup(),
        )
        self._init_field(
            "date1",
            "date2",
            "date_btn1",
            "date_btn2",
            get_date(self.dt1),
            get_date(self.dt2),
        )
        self._init_field(
            "gramps1", "gramps2", "gramps_btn1", "gramps_btn2", gramps1, gramps2
        )

        self.connect_button("dnatest_help", self.cb_help)
        self.connect_button("dnatest_ok", self.cb_merge)
        self.connect_button("dnatest_cancel", self.close)
        self.show()

    def _person_name(self, database, handle):
        if not handle:
            return ""
        person = database.get_person_from_handle(handle)
        return name_displayer.display(person) if person else ""

    def _init_field(self, entry1_id, entry2_id, btn1_id, btn2_id, val1, val2):
        self.get_widget(entry1_id).set_text(val1 or "")
        self.get_widget(entry2_id).set_text(val2 or "")
        if (val1 or "") == (val2 or ""):
            for w in (entry1_id, entry2_id, btn1_id, btn2_id):
                self.get_widget(w).set_sensitive(False)

    def on_handle1_toggled(self, obj):
        if obj.get_active():
            for btn in (
                "person_btn1",
                "account_btn1",
                "provider_btn1",
                "kit_id_btn1",
                "test_type_btn1",
                "genome_build_btn1",
                "haplogroup_btn1",
                "date_btn1",
                "gramps_btn1",
            ):
                self.get_widget(btn).set_active(True)
        else:
            for btn in (
                "person_btn2",
                "account_btn2",
                "provider_btn2",
                "kit_id_btn2",
                "test_type_btn2",
                "genome_build_btn2",
                "haplogroup_btn2",
                "date_btn2",
                "gramps_btn2",
            ):
                self.get_widget(btn).set_active(True)

    def cb_help(self, obj):
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def cb_merge(self, obj):
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.dt1
            titanic = self.dt2
        else:
            phoenix = self.dt2
            titanic = self.dt1

        if self.get_widget("person_btn1").get_active() ^ use_handle1:
            phoenix.set_person_handle(titanic.get_person_handle())
        if self.get_widget("account_btn1").get_active() ^ use_handle1:
            phoenix.set_account_name(titanic.get_account_name())
        if self.get_widget("provider_btn1").get_active() ^ use_handle1:
            phoenix.set_provider(titanic.get_provider())
        if self.get_widget("kit_id_btn1").get_active() ^ use_handle1:
            phoenix.set_kit_id(titanic.get_kit_id())
        if self.get_widget("test_type_btn1").get_active() ^ use_handle1:
            phoenix.set_test_type(titanic.get_test_type())
        if self.get_widget("genome_build_btn1").get_active() ^ use_handle1:
            phoenix.set_genome_build(titanic.get_genome_build())
        if self.get_widget("haplogroup_btn1").get_active() ^ use_handle1:
            phoenix.set_haplogroup(titanic.get_haplogroup())
        if self.get_widget("date_btn1").get_active() ^ use_handle1:
            phoenix.set_date_object(titanic.get_date_object())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())

        query = MergeDNATestQuery(self.dbstate, phoenix, titanic)
        query.execute()
        self.uistate.set_active(phoenix.get_handle(), "DNATest")
        self.close()
