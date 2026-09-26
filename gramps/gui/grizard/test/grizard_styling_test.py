#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Grizard Compare Styling Tests
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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Unit tests for the Grizard compare styling functions.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import sys
import unittest
from unittest.mock import Mock


def _has_gtk_display() -> bool:
    """
    Return True only if a real Gtk display is available.

    Building a widget without one crashes, so those tests must be skipped.
    An X11 backend needs DISPLAY set and cannot run with the CI value of
    GDK_BACKEND; the Windows and macOS backends need neither.
    """
    if sys.platform not in ("win32", "darwin"):
        if not os.environ.get("DISPLAY") or os.environ.get("GDK_BACKEND") == "-":
            return False
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        return bool(Gtk.init_check([])[0])
    except Exception:
        return False


_HAS_GTK_DISPLAY = _has_gtk_display()


class TestGrizardStyling(unittest.TestCase):
    """Test cases for Pango markup rendering in grizard compare/merge dialogs."""

    def test_compare_bold_only_content_not_punct(self):
        """Test that in compare window, only word content is bold, not punct."""
        from gramps.gui.grizard.grizardcompare import (
            GrizardCompareWindow,
        )

        # "b. 1234," vs "b. 5678," - only numbers differ, comma should NOT be bold
        result = GrizardCompareWindow._italicize_with_bold_diffs(
            "b. 1234,", "b. 1234,", "b. 5678,"
        )
        # "b." should be italic but not bold
        self.assertIn("<i>b.</i>", result)
        # "1234" should be bold
        self.assertIn("<b>1234</b>", result)
        # Verify comma is NOT inside bold tags
        import re

        bold_content = re.findall(r"<b>(.*?)</b>", result)
        self.assertNotIn(",", bold_content)

    def test_compare_matching_words_not_bold(self):
        """Test that matching words are not bold."""
        from gramps.gui.grizard.grizardcompare import (
            GrizardCompareWindow,
        )

        # "John Smith" vs "John Doe" - only "Smith" differs
        result = GrizardCompareWindow._italicize_with_bold_diffs(
            "John Smith", "John Smith", "John Doe"
        )
        # "John" should be italic but NOT bold
        self.assertIn("<i>John</i>", result)
        self.assertNotIn("<b>John</b>", result)
        # "Smith" should be bold
        self.assertIn("<b>Smith</b>", result)

    def test_compare_punctuation_not_bold(self):
        """Test various punctuation types are handled correctly."""
        from gramps.gui.grizard.grizardcompare import (
            GrizardCompareWindow,
        )

        # Test with comma
        result = GrizardCompareWindow._italicize_with_bold_diffs(
            "hello,", "hello,", "world,"
        )
        import re

        bold_content = re.findall(r"<b>(.*?)</b>", result)
        self.assertIn("hello", bold_content)
        self.assertNotIn(",", bold_content)  # comma should NOT be in bold

        # Test with period
        result = GrizardCompareWindow._italicize_with_bold_diffs(
            "test.", "test.", "demo."
        )
        bold_content = re.findall(r"<b>(.*?)</b>", result)
        self.assertIn("test", bold_content)
        self.assertNotIn(".", bold_content)  # period should NOT be in bold

    def test_merge_bold_only_content_not_punct(self):
        """Test that in merge dialog, only word content is bold, not punct."""
        from gramps.gui.grizard.grizardmergedialog import (
            GrizardMergeDialog,
        )

        # Test without label - this tests the core logic
        result = GrizardMergeDialog._format_diff_line(
            "ignored", "Boston,", "New York,", show_label=False, is_left=True
        )
        # "Boston" should be bold
        self.assertIn("<b>Boston</b>", result)
        # Comma should NOT be bold
        import re

        bold_content = re.findall(r"<b>(.*?)</b>", result)
        self.assertNotIn(",", bold_content)

    def test_merge_location_comma_not_bold(self):
        """Test that comma in location is not bold."""
        from gramps.gui.grizard.grizardmergedialog import (
            GrizardMergeDialog,
        )

        # "Boston, MA" vs "New York, NY" - compare word by word
        result = GrizardMergeDialog._format_diff_line(
            "ignored", "Boston, MA", "New York, NY", show_label=False, is_left=True
        )
        # "Boston" should be bold
        self.assertIn("<b>Boston</b>", result)
        # "MA" should be bold
        self.assertIn("<b>MA</b>", result)
        # Commas should NOT be bold
        import re

        bold_content = re.findall(r"<b>(.*?)</b>", result)
        self.assertNotIn(",", bold_content)


class TestGrizardCompareDiffStatus(unittest.TestCase):
    """Test matched-pair and Add as New button behavior."""

    def test_dict_diff_entry_does_not_break_matched_pair_buttons(self) -> None:
        from types import SimpleNamespace

        from gramps.gui.grizard.grizardcompare import GrizardCompareWindow

        window = SimpleNamespace(
            current_category="person",
            diff_list=[{"source_handle": "source", "target_handle": "target"}],
            diff_index=0,
            _get_selected_pair=lambda: ("source", "target"),
            btn_prev=Mock(),
            btn_next=Mock(),
            btn_merge_dialog=Mock(),
            btn_add_new=Mock(),
            diff_label=Mock(),
        )

        GrizardCompareWindow._update_diff_status(window)

        window.btn_merge_dialog.set_sensitive.assert_called_once_with(True)
        window.btn_add_new.set_label.assert_called_once_with("Not a Match")
        window.btn_add_new.set_sensitive.assert_called_once_with(True)

    def test_unmatched_pair_shows_add_as_new(self) -> None:
        from types import SimpleNamespace

        from gramps.gui.grizard.grizardcompare import GrizardCompareWindow

        window = SimpleNamespace(
            current_category="person",
            diff_list=[{"source_handle": "source", "target_handle": None}],
            diff_index=0,
            _get_selected_pair=lambda: ("source", None),
            btn_prev=Mock(),
            btn_next=Mock(),
            btn_merge_dialog=Mock(),
            btn_add_new=Mock(),
            diff_label=Mock(),
        )

        GrizardCompareWindow._update_diff_status(window)

        window.btn_merge_dialog.set_sensitive.assert_called_once_with(False)
        window.btn_add_new.set_label.assert_called_once_with("Add as New...")
        window.btn_add_new.set_sensitive.assert_called_once_with(True)

    def test_reject_pair_updates_maps_and_keeps_diff_dict(self) -> None:
        from types import SimpleNamespace

        from gramps.gui.grizard.grizardcompare import GrizardCompareWindow

        window = SimpleNamespace(
            _rejected={},
            _pair_map={"source": "target"},
            _pair_map_rev={"target": "source"},
            diff_list=[{"source_handle": "source", "target_handle": "target"}],
            diff_index=0,
            source_db=SimpleNamespace(get_person_from_handle=Mock(return_value=None)),
            left_panel={"store": Mock()},
            right_panel={"store": Mock(), "tree": Mock()},
            _syncing=False,
            _mark_row=Mock(),
            _update_diff_status=Mock(),
        )

        GrizardCompareWindow._reject_pair(window, "source", "target")

        self.assertEqual(window._rejected, {"source": {"target"}})
        self.assertIsNone(window._pair_map["source"])
        self.assertNotIn("target", window._pair_map_rev)
        self.assertIsNone(window.diff_list[0]["target_handle"])
        window._update_diff_status.assert_called_once_with()

        window._match_key = lambda _person: ("surname", "i")
        window._target_index = {("surname", "i"): ["target"]}
        self.assertIsNone(
            GrizardCompareWindow._best_match(
                window, Mock(), SimpleNamespace(handle="source")
            )
        )


class TestGrizardDiffHighlight(unittest.TestCase):
    """Test cases for the diff-line row highlight used by the merge dialog."""

    def test_diff_line_rule_defines_background(self) -> None:
        """The dialog stylesheet must style .diff-line with a background."""
        from gramps.gui.grizard.grizardmergedialog import (
            DIFF_CSS_DATA,
            DIFF_STYLE_CLASS,
        )

        css_text = DIFF_CSS_DATA.decode("utf-8")
        self.assertIn(".%s" % DIFF_STYLE_CLASS, css_text)
        rule_start = css_text.index(".%s" % DIFF_STYLE_CLASS)
        rule = css_text[rule_start:]
        self.assertIn("background-color", rule[: rule.find("}")])

    def test_diff_css_parses(self) -> None:
        """The dialog stylesheet data must parse without GLib error."""
        from gi.repository import Gtk

        from gramps.gui.grizard.grizardmergedialog import DIFF_CSS_DATA

        provider = Gtk.CssProvider()
        provider.load_from_data(DIFF_CSS_DATA)

    def test_ensure_diff_styles_installed_without_screen(self) -> None:
        """Installing the stylesheet must be safe in a headless run."""
        from gi.repository import Gdk

        from gramps.gui.grizard import grizardmergedialog

        saved = grizardmergedialog._DIFF_CSS_INSTALLED
        try:
            grizardmergedialog._DIFF_CSS_INSTALLED = False
            result = grizardmergedialog.ensure_diff_styles_installed()
        finally:
            grizardmergedialog._DIFF_CSS_INSTALLED = saved

        self.assertIsInstance(result, bool)
        if Gdk.Screen.get_default() is None:
            self.assertFalse(result)

    @unittest.skipUnless(
        _HAS_GTK_DISPLAY,
        "needs a real Gtk display; building a widget without one crashes",
    )
    def test_diff_highlight_class_applied_to_differing_cells(self) -> None:
        """Only the cells of a differing row may carry the diff-line class."""
        from gramps.gui.grizard.grizardmergedialog import (
            DIFF_STYLE_CLASS,
            create_diff_cell,
            field_values_differ,
        )

        differs = field_values_differ("Hansdotter", "Hansdotter Smith")
        marked = create_diff_cell("<i>Surname: </i>Hansdotter", differs, 0.0)
        self.assertTrue(marked.get_style_context().has_class(DIFF_STYLE_CLASS))
        self.assertEqual(marked.get_text(), "Surname: Hansdotter")
        self.assertEqual(marked.get_xalign(), 0.0)

        matches = field_values_differ("Anna", "Anna")
        plain = create_diff_cell("<i>Given Name: </i>Anna", matches, 1.0)
        self.assertFalse(plain.get_style_context().has_class(DIFF_STYLE_CLASS))
        self.assertEqual(plain.get_xalign(), 1.0)


if __name__ == "__main__":
    unittest.main()
