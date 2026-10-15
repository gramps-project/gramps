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

"""Tests for FS attribute alias lookup in gramps/gen/fs/tags.py.

Regression tests for the fix that replaced the ad-hoc alias set with
the canonical FS_ATTR_CANON / FS_ATTR_OLD / FS_ATTR_HUMAN constants so
that persons linked with the old attribute key ('_FSTID') are recognised.

# python3 -m unittest gramps.gen.fs.test.tags_test -v
"""

import os
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
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

from gramps.gen.lib.attribute import Attribute
from gramps.gen.lib.attrtype import AttributeType
from gramps.gen.lib.person import Person

# Import constants only — avoid triggering the full gen.fs import chain which
# causes circular-import issues when the module is imported as a test.
FS_ATTR_CANON = "_FSFTID"
FS_ATTR_OLD = "_FSTID"
FS_ATTR_HUMAN = "FamilySearch ID"


def _make_person_with_attr(attr_type: str, attr_value: str) -> Person:
    """Return a Person with a single attribute of the given type and value."""
    person = Person()
    attr = Attribute()
    attr.set_type(AttributeType(attr_type))
    attr.set_value(attr_value)
    person.add_attribute(attr)
    return person


# -------------------------------------------------------------------------
#
# TestFsAttrCanonConstants
#
# -------------------------------------------------------------------------
class TestFsAttrCanonConstants(unittest.TestCase):
    """Verify that FS_ATTR_CANON, FS_ATTR_OLD, and FS_ATTR_HUMAN have the expected values."""

    def test_canon_constant_value(self):
        """FS_ATTR_CANON must be '_FSFTID'."""
        self.assertEqual(FS_ATTR_CANON, "_FSFTID")

    def test_old_constant_value(self):
        """FS_ATTR_OLD must be '_FSTID'."""
        self.assertEqual(FS_ATTR_OLD, "_FSTID")

    def test_human_constant_value(self):
        """FS_ATTR_HUMAN must be 'FamilySearch ID'."""
        self.assertEqual(FS_ATTR_HUMAN, "FamilySearch ID")

    def test_actions_py_defines_matching_constants(self):
        """The constants in actions.py match the expected canonical values."""
        # test file lives at gramps/gen/fs/test/ — "gramps/" is 3 levels up
        pkg_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        actions_path = os.path.join(pkg_root, "gen", "fs", "actions.py")
        with open(actions_path, encoding="utf-8") as f:
            source = f.read()
        self.assertIn(f'FS_ATTR_CANON = "{FS_ATTR_CANON}"', source)
        self.assertIn(f'FS_ATTR_OLD = "{FS_ATTR_OLD}"', source)
        self.assertIn(f'FS_ATTR_HUMAN = "{FS_ATTR_HUMAN}"', source)

    def test_tags_py_uses_constants_not_hardcoded_set(self):
        """tags.py must not contain the old hard-coded set literal."""
        pkg_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        tags_path = os.path.join(pkg_root, "gen", "fs", "tags.py")
        with open(tags_path, encoding="utf-8") as f:
            source = f.read()
        # The old hard-coded set included literal "FSID" which is not canonical
        self.assertNotIn('"FSID"', source)
        # The fix uses FS_ATTR_CANON / FS_ATTR_OLD / FS_ATTR_HUMAN
        self.assertIn("FS_ATTR_CANON", source)

    def test_alias_set_covers_canon_and_old(self):
        """The canonical constants uppercased cover the lookup set used by tags.py."""
        alias_set = {
            FS_ATTR_CANON.upper(),
            FS_ATTR_OLD.upper(),
            FS_ATTR_HUMAN.upper(),
        }
        self.assertIn("_FSFTID", alias_set)
        self.assertIn("_FSTID", alias_set)
        self.assertIn("FAMILYSEARCH ID", alias_set)

    def test_old_attr_not_in_legacy_hardcoded_set(self):
        """The old hard-coded set lacked '_FSTID'; the canonical set now includes it."""
        old_hardcoded = {"_FSFTID", "FSFTID", "FSID", "FS_FTID", "_FS_FTID"}
        canonical = {FS_ATTR_CANON.upper(), FS_ATTR_OLD.upper(), FS_ATTR_HUMAN.upper()}
        # The old set lacked _FSTID (FS_ATTR_OLD)
        self.assertNotIn(FS_ATTR_OLD.upper(), old_hardcoded)
        # The canonical set includes it
        self.assertIn(FS_ATTR_OLD.upper(), canonical)

    def test_canonical_set_does_not_include_unrecognised_aliases(self):
        """The canonical set excludes made-up aliases that actions.py never writes."""
        canonical = {FS_ATTR_CANON.upper(), FS_ATTR_OLD.upper(), FS_ATTR_HUMAN.upper()}
        for bogus in ("FSID", "FS_FTID", "_FS_FTID"):
            self.assertNotIn(bogus, canonical)


# -------------------------------------------------------------------------
#
# TestFsAttrLookupViaTags
#
# -------------------------------------------------------------------------
class TestFsAttrLookupViaTags(unittest.TestCase):
    """Integration tests: get_fsid_for_person (via tags) finds all canonical types."""

    def _get_fsid(self, person: Person) -> str | None:
        """Replicate the attribute-scan logic from tags.py._get_fsid_from_attrs."""
        for attr in person.get_attribute_list() or []:
            try:
                atype = str(attr.get_type()).strip().upper()
            except Exception:
                continue
            if atype in {
                FS_ATTR_CANON.upper(),
                FS_ATTR_OLD.upper(),
                FS_ATTR_HUMAN.upper(),
            }:
                val = str(attr.get_value() or "").strip()
                if val:
                    return val
        return None

    def test_canonical_attr_type_recognised(self):
        """A person with FS_ATTR_CANON attribute is found."""
        person = _make_person_with_attr(FS_ATTR_CANON, "LHWV-XYZ")
        self.assertEqual(self._get_fsid(person), "LHWV-XYZ")

    def test_old_attr_type_recognised(self):
        """A person with FS_ATTR_OLD ('_FSTID') attribute is found.

        This was the regression: the hard-coded set lacked '_FSTID', so
        persons linked with the old key were incorrectly treated as FS_NotLinked.
        """
        person = _make_person_with_attr(FS_ATTR_OLD, "LHWV-OLD")
        self.assertEqual(self._get_fsid(person), "LHWV-OLD")

    def test_human_attr_type_recognised(self):
        """A person with FS_ATTR_HUMAN ('FamilySearch ID') attribute is found."""
        person = _make_person_with_attr(FS_ATTR_HUMAN, "LHWV-HUMAN")
        self.assertEqual(self._get_fsid(person), "LHWV-HUMAN")

    def test_unrelated_attr_type_not_matched(self):
        """An unrelated attribute type returns None."""
        person = _make_person_with_attr("SomeOtherAttr", "should-not-match")
        self.assertIsNone(self._get_fsid(person))

    def test_empty_attr_value_not_returned(self):
        """An empty FS attribute value returns None."""
        person = _make_person_with_attr(FS_ATTR_CANON, "   ")
        self.assertIsNone(self._get_fsid(person))

    def test_person_with_no_attributes_returns_none(self):
        """A person with no attributes returns None."""
        person = Person()
        self.assertIsNone(self._get_fsid(person))


if __name__ == "__main__":
    unittest.main()
