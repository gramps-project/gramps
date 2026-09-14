#
# Gramps - a GTK+/GNOME based genealogy program
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

"""Mantis 10768 — fan-chart Print dialogs must not override the paper size.

The reported failure (Mac OS X, Gramps 5.0+): opening File → Print on a
Fan Chart View showed the paper-size combo grayed out at "Custom",
forced a custom paper size matching the chart's natural rendered
millimetre dimensions (e.g. 1330×1330mm for 16 generations), and made
the printer literally try to reproduce that custom page — printing one
quarter of the chart on real Letter paper.

Root cause was identical across the three fan-chart view modules: each
built a ``Gtk.PaperSize.new_custom("custom", "Custom Size", widthpx *
0.2646, heightpx * 0.2646, Gtk.Unit.MM)`` and called
``operation.set_default_page_setup(page_setup)`` on it (twice — once
for the first ``operation.run`` and once when reconstructing the
operation for the preview-rerun branch).

The actual print flow is GUI-bound (live ``Gtk.PrintOperation``, real
``PRINT_DIALOG``, a printer to receive the job) so a runtime unit test
of the dialog is impractical in headless CI.  These tests are the
cheaper guard: they assert the buggy fragments are absent from each
file so the pattern doesn't accidentally reappear via copy-paste from
a sibling view or a stale revert.  Same shape as the source-grep
guards in ``gramps/gen/plug/docgen/test/graphdoc_test.py`` (bug 6556 /
PR 2318)."""

import os
import unittest


def _read(*parts: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "..", *parts)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


VIEW_FILES = (
    "fanchartview.py",
    "fanchart2wayview.py",
    "fanchartdescview.py",
)

BUGGY_FRAGMENTS = (
    # The custom paper size constructor and its mm-conversion magic.
    'PaperSize.new_custom("custom"',
    "widthpx * 0.2646",
    # Locking the dialog into the custom size.
    "set_default_page_setup(page_setup)",
    # The chained construction the previous two depended on.
    "page_setup = Gtk.PageSetup()",
)


class FanChartPrintNoCustomPaperSizeTest(unittest.TestCase):
    """Each of the three fan-chart views must not reintroduce the
    custom-paper override that bug 10768 was fixed by removing."""

    def test_fanchartview_does_not_override_paper_size(self):
        self._assert_no_buggy_fragments("fanchartview.py")

    def test_fanchart2wayview_does_not_override_paper_size(self):
        self._assert_no_buggy_fragments("fanchart2wayview.py")

    def test_fanchartdescview_does_not_override_paper_size(self):
        self._assert_no_buggy_fragments("fanchartdescview.py")

    def test_all_view_files_exist(self):
        # Tripwire: if any of the three files is renamed or moved, this
        # test surfaces it so the per-file tests above aren't silently
        # vacuous.
        for name in VIEW_FILES:
            path = os.path.join(os.path.dirname(__file__), "..", name)
            self.assertTrue(
                os.path.exists(path),
                f"expected view file missing: {path} — "
                "rename/move the per-file tests too",
            )

    def _assert_no_buggy_fragments(self, name: str) -> None:
        source = _read(name)
        for fragment in BUGGY_FRAGMENTS:
            self.assertNotIn(
                fragment,
                source,
                f"{name}: re-introduction of bug 10768 custom-paper override "
                f"(forbidden fragment {fragment!r})",
            )


if __name__ == "__main__":
    unittest.main()
