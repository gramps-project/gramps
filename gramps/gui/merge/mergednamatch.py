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
Provide merge capabilities for DNA matches.
"""

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.merge import MergeDNAMatchQuery
from gramps.gen.utils.db import dnatest_short_label
from ..display import display_help
from ..managedwindow import ManagedWindow

WIKI_HELP_PAGE = URL_MANUAL_PAGE
WIKI_HELP_SEC = _("Merge_DNA_Matches", "manual")
_GLADE_FILE = "mergednamatch.glade"


# -------------------------------------------------------------------------
#
# MergeDNAMatch
#
# -------------------------------------------------------------------------
class MergeDNAMatch(ManagedWindow):
    """
    Displays a dialog box that allows two DNA match records to be merged.
    """

    def __init__(self, dbstate, uistate, track, handle1, handle2):
        ManagedWindow.__init__(self, uistate, track, self.__class__)
        self.dbstate = dbstate
        database = dbstate.db
        self.dm1 = database.get_dnamatch_from_handle(handle1)
        self.dm2 = database.get_dnamatch_from_handle(handle2)

        self.define_glade("mergednamatch", _GLADE_FILE)
        self.set_window(
            self._gladeobj.toplevel,
            self.get_widget("dnamatch_title"),
            _("Merge DNA Matches"),
        )
        self.setup_configs("interface.merge-dnamatch", 700, 300)

        gramps1 = self.dm1.get_gramps_id()
        gramps2 = self.dm2.get_gramps_id()

        subject1 = dnatest_short_label(database, self.dm1.get_subject_test_handle())
        subject2 = dnatest_short_label(database, self.dm2.get_subject_test_handle())
        match1 = dnatest_short_label(database, self.dm1.get_match_test_handle())
        match2 = dnatest_short_label(database, self.dm2.get_match_test_handle())

        def _fmt_float(v):
            return str(v) if v else ""

        def _fmt_int(v):
            return str(v) if v else ""

        shared_cm1 = _fmt_float(self.dm1.get_shared_cm())
        shared_cm2 = _fmt_float(self.dm2.get_shared_cm())
        pct1 = _fmt_float(self.dm1.get_percent_shared())
        pct2 = _fmt_float(self.dm2.get_percent_shared())
        seg_count1 = _fmt_int(self.dm1.get_segment_count())
        seg_count2 = _fmt_int(self.dm2.get_segment_count())
        largest1 = _fmt_float(self.dm1.get_largest_segment_cm())
        largest2 = _fmt_float(self.dm2.get_largest_segment_cm())
        rel1 = self.dm1.get_predicted_relationship()
        rel2 = self.dm2.get_predicted_relationship()
        gen1 = _fmt_float(self.dm1.get_predicted_generations())
        gen2 = _fmt_float(self.dm2.get_predicted_generations())

        label1 = "%s / %s [%s]" % (
            subject1 or _("unknown"),
            match1 or _("unknown"),
            gramps1,
        )
        label2 = "%s / %s [%s]" % (
            subject2 or _("unknown"),
            match2 or _("unknown"),
            gramps2,
        )
        self.get_widget("label_handle_btn1").set_label(label1)
        self.get_widget("label_handle_btn2").set_label(label2)
        self.get_widget("handle_btn1").connect("toggled", self.on_handle1_toggled)

        self._init_field(
            "subject1", "subject2", "subject_btn1", "subject_btn2", subject1, subject2
        )
        self._init_field("match1", "match2", "match_btn1", "match_btn2", match1, match2)
        self._init_field(
            "shared_cm1",
            "shared_cm2",
            "shared_cm_btn1",
            "shared_cm_btn2",
            shared_cm1,
            shared_cm2,
        )
        self._init_field(
            "percent_shared1",
            "percent_shared2",
            "percent_shared_btn1",
            "percent_shared_btn2",
            pct1,
            pct2,
        )
        self._init_field(
            "segment_count1",
            "segment_count2",
            "segment_count_btn1",
            "segment_count_btn2",
            seg_count1,
            seg_count2,
        )
        self._init_field(
            "largest_segment1",
            "largest_segment2",
            "largest_segment_btn1",
            "largest_segment_btn2",
            largest1,
            largest2,
        )
        self._init_field(
            "relationship1",
            "relationship2",
            "relationship_btn1",
            "relationship_btn2",
            rel1,
            rel2,
        )
        self._init_field(
            "generations1",
            "generations2",
            "generations_btn1",
            "generations_btn2",
            gen1,
            gen2,
        )
        self._init_field(
            "gramps1", "gramps2", "gramps_btn1", "gramps_btn2", gramps1, gramps2
        )

        self.connect_button("dnamatch_help", self.cb_help)
        self.connect_button("dnamatch_ok", self.cb_merge)
        self.connect_button("dnamatch_cancel", self.close)
        self.show()

    def _init_field(self, entry1_id, entry2_id, btn1_id, btn2_id, val1, val2):
        self.get_widget(entry1_id).set_text(val1 or "")
        self.get_widget(entry2_id).set_text(val2 or "")
        if (val1 or "") == (val2 or ""):
            for w in (entry1_id, entry2_id, btn1_id, btn2_id):
                self.get_widget(w).set_sensitive(False)

    def on_handle1_toggled(self, obj):
        if obj.get_active():
            for btn in (
                "subject_btn1",
                "match_btn1",
                "shared_cm_btn1",
                "percent_shared_btn1",
                "segment_count_btn1",
                "largest_segment_btn1",
                "relationship_btn1",
                "generations_btn1",
                "gramps_btn1",
            ):
                self.get_widget(btn).set_active(True)
        else:
            for btn in (
                "subject_btn2",
                "match_btn2",
                "shared_cm_btn2",
                "percent_shared_btn2",
                "segment_count_btn2",
                "largest_segment_btn2",
                "relationship_btn2",
                "generations_btn2",
                "gramps_btn2",
            ):
                self.get_widget(btn).set_active(True)

    def cb_help(self, obj):
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def cb_merge(self, obj):
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.dm1
            titanic = self.dm2
        else:
            phoenix = self.dm2
            titanic = self.dm1

        if self.get_widget("subject_btn1").get_active() ^ use_handle1:
            phoenix.set_subject_test_handle(titanic.get_subject_test_handle())
        if self.get_widget("match_btn1").get_active() ^ use_handle1:
            phoenix.set_match_test_handle(titanic.get_match_test_handle())
        if self.get_widget("shared_cm_btn1").get_active() ^ use_handle1:
            phoenix.set_shared_cm(titanic.get_shared_cm())
        if self.get_widget("percent_shared_btn1").get_active() ^ use_handle1:
            phoenix.set_percent_shared(titanic.get_percent_shared())
        if self.get_widget("segment_count_btn1").get_active() ^ use_handle1:
            phoenix.set_segment_count(titanic.get_segment_count())
        if self.get_widget("largest_segment_btn1").get_active() ^ use_handle1:
            phoenix.set_largest_segment_cm(titanic.get_largest_segment_cm())
        if self.get_widget("relationship_btn1").get_active() ^ use_handle1:
            phoenix.set_predicted_relationship(titanic.get_predicted_relationship())
        if self.get_widget("generations_btn1").get_active() ^ use_handle1:
            phoenix.set_predicted_generations(titanic.get_predicted_generations())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())

        query = MergeDNAMatchQuery(self.dbstate, phoenix, titanic)
        query.execute()
        self.uistate.set_active(phoenix.get_handle(), "DNAMatch")
        self.close()
