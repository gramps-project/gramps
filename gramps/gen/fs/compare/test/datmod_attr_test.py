#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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

"""Tests that window.py writes the same attribute name that aggregate.py reads.

Regression test for the typo bug where window.py wrote `fs_person._datemod`
(with 'e') but aggregate.py read `fs_person._datmod` (without 'e'), making
the early-return optimisation in compare_fs_to_gramps permanently dead.

# python3 -m unittest gramps.gen.fs.compare.test.datmod_attr_test -v
"""

import os
import shutil
import tempfile
import types
import unittest

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..")
)


def _ensure_test_resources():
    """Ensure GRAMPS_RESOURCES points to a directory with required files."""
    resource_path = os.environ.get("GRAMPS_RESOURCES")
    if resource_path and os.path.exists(
        os.path.join(resource_path, "gramps", "authors.xml")
    ):
        return resource_path

    build_share = os.path.join(ROOT_DIR, "build", "share")
    if os.path.exists(os.path.join(build_share, "gramps", "authors.xml")):
        return build_share

    resource_path = tempfile.mkdtemp(prefix="gramps-resources-")
    os.makedirs(os.path.join(resource_path, "gramps", "images"), exist_ok=True)
    os.makedirs(os.path.join(resource_path, "doc", "gramps"), exist_ok=True)
    os.makedirs(os.path.join(resource_path, "locale"), exist_ok=True)

    shutil.copyfile(
        os.path.join(ROOT_DIR, "data", "authors.xml"),
        os.path.join(resource_path, "gramps", "authors.xml"),
    )
    shutil.copyfile(
        os.path.join(ROOT_DIR, "images", "gramps.png"),
        os.path.join(resource_path, "gramps", "images", "gramps.png"),
    )
    shutil.copyfile(
        os.path.join(ROOT_DIR, "COPYING"),
        os.path.join(resource_path, "doc", "gramps", "COPYING"),
    )
    return resource_path


os.environ["GRAMPS_RESOURCES"] = _ensure_test_resources()
os.environ["HOME"] = os.environ.get("HOME") or tempfile.mkdtemp(prefix="gramps-home-")

# test file is at gramps/gen/fs/compare/test/datmod_attr_test.py
# so "gramps/" root is 4 levels up
_GRAMPS_PKG_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
_WINDOW_PY = os.path.join(_GRAMPS_PKG_ROOT, "gui", "fs", "compare", "window.py")
_AGGREGATE_PY = os.path.join(_GRAMPS_PKG_ROOT, "gen", "fs", "compare", "aggregate.py")


def _read_source(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# -------------------------------------------------------------------------
#
# TestDatmodAttributeNameConsistency
#
# -------------------------------------------------------------------------
class TestDatmodAttributeNameConsistency(unittest.TestCase):
    """Tests that window.py writes `_datmod` (not `_datemod`) on the fs_person.

    aggregate.py reads `hasattr(fs_person, '_datmod')`, so window.py must
    write exactly that name. A typo of `_datemod` makes the early-return
    optimisation permanently dead.
    """

    def test_aggregate_reads_datmod_without_e(self):
        """aggregate.py references `_datmod` (no 'e')."""
        source = _read_source(_AGGREGATE_PY)
        self.assertIn("_datmod", source)
        # The old typo must NOT appear in aggregate.py
        self.assertNotIn("_datemod", source)

    def test_window_writes_datmod_without_e(self):
        """window.py writes `_datmod` (no 'e') to match what aggregate.py reads."""
        source = _read_source(_WINDOW_PY)
        self.assertIn("_datmod", source)
        # The old typo must NOT appear
        self.assertNotIn("_datemod", source)

    def test_attribute_names_match(self):
        """The attribute name written in window.py matches what aggregate.py reads.

        If this test fails, either window.py or aggregate.py uses the wrong
        name and the early-return optimisation is dead.
        """
        window_source = _read_source(_WINDOW_PY)
        aggregate_source = _read_source(_AGGREGATE_PY)
        self.assertIn("_datmod", window_source)
        self.assertIn("_datmod", aggregate_source)

    def test_set_then_hasattr(self):
        """Setting `_datmod` on a SimpleNamespace makes hasattr return True."""
        fs_person = types.SimpleNamespace()
        # Simulate what window.py does after the fix
        fs_person._datmod = 1767225600
        # Simulate what aggregate.py checks
        self.assertTrue(hasattr(fs_person, "_datmod"))
        self.assertEqual(fs_person._datmod, 1767225600)


if __name__ == "__main__":
    unittest.main()
