#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Doug Blank
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

import unittest

from ..requirements import Requirements, _mod_entry


class TestModEntry(unittest.TestCase):
    def test_string_returns_same_for_both(self):
        self.assertEqual(_mod_entry("os"), ("os", "os"))

    def test_string_hyphenated_package(self):
        self.assertEqual(
            _mod_entry(("gramps_gedcom7", "gramps-gedcom7")),
            ("gramps_gedcom7", "gramps-gedcom7"),
        )

    def test_tuple_with_version_constraint(self):
        self.assertEqual(
            _mod_entry(("gramps_gedcom7", "gramps-gedcom7>=1.0")),
            ("gramps_gedcom7", "gramps-gedcom7>=1.0"),
        )


class TestCheckMod(unittest.TestCase):
    def setUp(self):
        self.req = Requirements()

    def test_string_present_module(self):
        self.assertTrue(self.req.check_mod("os"))

    def test_string_absent_module(self):
        self.assertFalse(self.req.check_mod("_nonexistent_module_xyz"))

    def test_tuple_present_module(self):
        self.assertTrue(self.req.check_mod(("os", "os-package")))

    def test_tuple_absent_module(self):
        self.assertFalse(
            self.req.check_mod(("_nonexistent_module_xyz", "nonexistent-pkg>=1.0"))
        )

    def test_string_result_cached(self):
        self.req.check_mod("os")
        self.assertIn("os", self.req.mod_list)

    def test_tuple_caches_import_name_not_pip_spec(self):
        self.req.check_mod(("os", "os-package>=1.0"))
        self.assertIn("os", self.req.mod_list)
        self.assertNotIn("os-package>=1.0", self.req.mod_list)


class TestInstall(unittest.TestCase):
    def setUp(self):
        self.req = Requirements()

    def test_string_missing_module_returns_import_name(self):
        result = self.req.install({"rm": ["_nonexistent_module_xyz"]})
        self.assertEqual(result, ["_nonexistent_module_xyz"])

    def test_tuple_missing_module_returns_pip_spec(self):
        result = self.req.install(
            {"rm": [("_nonexistent_module_xyz", "nonexistent-pkg>=1.0")]}
        )
        self.assertEqual(result, ["nonexistent-pkg>=1.0"])

    def test_present_module_not_in_install_list(self):
        result = self.req.install({"rm": ["os"]})
        self.assertEqual(result, [])

    def test_mixed_list(self):
        result = self.req.install(
            {"rm": ["os", ("_nonexistent_module_xyz", "nonexistent-pkg>=2.0")]}
        )
        self.assertEqual(result, ["nonexistent-pkg>=2.0"])

    def test_no_rm_key(self):
        self.assertEqual(self.req.install({}), [])


class TestInfo(unittest.TestCase):
    def setUp(self):
        self.req = Requirements()

    def test_string_label_is_plain_name(self):
        info = self.req.info({"rm": ["os"]})
        table = info[1]
        self.assertEqual(table[0][0], "os")

    def test_tuple_label_shows_pip_spec_when_different(self):
        info = self.req.info({"rm": [("gramps_gedcom7", "gramps-gedcom7>=1.0")]})
        table = info[1]
        self.assertIn("gramps_gedcom7", table[0][0])
        self.assertIn("gramps-gedcom7>=1.0", table[0][0])

    def test_tuple_label_plain_when_same(self):
        info = self.req.info({"rm": [("os", "os")]})
        table = info[1]
        self.assertEqual(table[0][0], "os")


if __name__ == "__main__":
    unittest.main()
