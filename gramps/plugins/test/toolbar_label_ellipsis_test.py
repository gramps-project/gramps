#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps developers
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
Regression test for bug 6583.

The list-view / category-view toolbar (and its matching menu / right-click
popup items) labelled the *Edit* action with a trailing ellipsis ("Edit...",
"_Edit...") while the Remove/Delete action carried none -- an inconsistency the
reporter flagged.

Per the GNOME Human Interface Guidelines the trailing ellipsis means "this
command needs further input from the user before it can act".  The *Edit*
action does not: it opens the selected record straight into its editor (a
state / properties window), so its label must NOT carry an ellipsis.  The
*Add* and *Merge* actions, by contrast, open a dialog that asks the user to
supply new information (which record to create, which fields to keep) before
they act -- those keep their ellipsis.  The fix therefore drops the trailing
ellipsis from the Edit label only, leaving Add.../Merge... intact.

This test parses the ``additional_ui`` UI-XML strings straight from each view's
source file (no GTK / gramps.gui / gi import, so it is headless-safe and cannot
crash the headless C4 runner) and asserts that no *Edit* action label keeps a
trailing ellipsis.  It is RED before the fix ("Edit..." present) and GREEN
after ("Edit").  It deliberately does not touch the Add/Merge labels, which
correctly retain their ellipsis.
"""

import os
import re
import unittest

# This file lives at gramps/plugins/test/<name>_test.py, so the gramps package
# root is two directories up.  Resolve the view source files relative to it
# instead of importing them -- importing pulls in gramps.gui / gi, which is not
# available (and would crash) under the headless test runner.  Reading the
# source is reading the production artifact itself: these labels are static
# UI-XML string literals, there is no runtime logic to route through.
_GRAMPS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# The category / list / relationship views whose toolbars carried the Edit
# button reported in bug 6583.
VIEW_FILES = [
    "plugins/lib/libpersonview.py",
    "plugins/lib/libplaceview.py",
    "plugins/view/citationlistview.py",
    "plugins/view/citationtreeview.py",
    "plugins/view/eventview.py",
    "plugins/view/familyview.py",
    "plugins/view/mediaview.py",
    "plugins/view/noteview.py",
    "plugins/view/repoview.py",
    "plugins/view/sourceview.py",
    "plugins/view/relview.py",
]

# An Edit label expressed as a GtkToolButton <property name="label">...</property>
# or a menu / popup <attribute name="label">...</attribute>, e.g. "Edit...".
_EDIT_XML_LABEL_RE = re.compile(
    r'name="label"(?:\s+translatable="[^"]*")?\s*>\s*(_?Edit[^<]*)<'
)
# An Edit label supplied through sgettext, e.g.  _("_Edit...", "action").
_EDIT_SGETTEXT_RE = re.compile(r'_\(\s*"(_?Edit[^"]*)"\s*,\s*"action"\s*\)')


def _iter_edit_labels(text):
    """Yield every Edit-action label string defined in *text*."""
    for value in _EDIT_XML_LABEL_RE.findall(text):
        yield value
    for value in _EDIT_SGETTEXT_RE.findall(text):
        yield value


class ToolbarLabelEllipsisTest(unittest.TestCase):
    """Bug 6583: the Edit toolbar/menu label must not end with '...'."""

    def test_edit_label_has_no_trailing_ellipsis(self):
        offenders = []
        for rel in VIEW_FILES:
            path = os.path.join(_GRAMPS_ROOT, rel)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            for label in _iter_edit_labels(text):
                if label.rstrip().endswith("..."):
                    offenders.append("%s: %r" % (rel, label))
        self.assertEqual(
            offenders,
            [],
            "Edit toolbar/menu labels still carry a trailing ellipsis "
            "(bug 6583); the Edit action opens a record and needs no "
            "ellipsis:\n  " + "\n  ".join(offenders),
        )

    def test_finds_the_edit_labels_at_all(self):
        # Guard against the parser silently matching nothing (which would make
        # the assertion above pass vacuously).  Every listed view defines at
        # least one Edit label.
        for rel in VIEW_FILES:
            path = os.path.join(_GRAMPS_ROOT, rel)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            labels = list(_iter_edit_labels(text))
            self.assertTrue(
                labels, "no Edit label parsed from %s (parser drift?)" % rel
            )


if __name__ == "__main__":
    unittest.main()
