# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013 Vassilii Khachaturov <vassilii@tarunz.org>
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

"""Unittest for argparser.py"""

import unittest
import os
import json
import tempfile
from unittest.mock import Mock
from ..argparser import ArgParser


class TestArgParser(unittest.TestCase):
    def setUp(self):
        pass

    def create_parser(*self_and_args):
        return ArgParser(list(self_and_args))

    def triggers_option_error(self, option):
        ap = self.create_parser(option)
        return (str(ap.errors).find("option " + option) >= 0, ap)

    def test_wrong_argument_triggers_option_error(self):
        bad, ap = self.triggers_option_error("--I-am-a-wrong-argument")
        self.assertTrue(bad, ap.__dict__)

    def test_y_shortopt_sets_auto_accept(self):
        bad, ap = self.triggers_option_error("-y")

        self.assertFalse(bad)

        expected_errors = [
            (
                "Error parsing the arguments",
                "Error parsing the arguments: [ -y ] \n"
                + "To use in the command-line mode, supply at least one input file to process.",
            )
        ]
        self.assertEqual(expected_errors, ap.errors)

        self.assertTrue(ap.auto_accept)

    def test_yes_longopt_sets_auto_accept(self):
        bad, ap = self.triggers_option_error("--yes")
        self.assertFalse(bad, ap.errors)
        self.assertTrue(ap.auto_accept)

    def test_q_shortopt_sets_quiet(self):
        bad, ap = self.triggers_option_error("-q")
        self.assertFalse(bad, ap.errors)
        self.assertTrue(ap.quiet)

    def test_quiet_longopt_sets_quiet(self):
        bad, ap = self.triggers_option_error("--quiet")
        self.assertFalse(bad, ap.errors)
        self.assertTrue(ap.quiet)

    def test_quiet_exists_by_default(self):
        ap = self.create_parser()
        self.assertTrue(hasattr(ap, "quiet"))

    def test_auto_accept_unset_by_default(self):
        ap = self.create_parser()
        self.assertFalse(ap.auto_accept)

    def test_exception(self):
        argument_parser = self.create_parser("-O")

        expected_errors = [
            (
                "Error parsing the arguments",
                "option -O requires argument\n"
                "Error parsing the arguments: [ -O ] \n"
                "Type gramps --help for an overview of commands, or read the manual pages.",
            )
        ]
        self.assertEqual(expected_errors, argument_parser.errors)

    def test_option_with_multiple_arguments(self):
        argument_parser = self.create_parser("-l", "family_tree_name")
        self.assertEqual(argument_parser.database_names, ["family_tree_name"])

    def write_state_file(self, contents):
        state_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        self.addCleanup(os.remove, state_file.name)
        json.dump(contents, state_file)
        state_file.close()
        return state_file.name

    def test_restore_state_longopt_sets_open_from_tree(self):
        path = self.write_state_file({"tree": "My Family Tree"})
        ap = self.create_parser("--restore-state", path)
        self.assertEqual(ap.open, "My Family Tree")
        self.assertEqual(ap.restore_state_path, path)

    def test_restore_state_without_tree_key_leaves_open_none(self):
        path = self.write_state_file({"language": "fr_FR.UTF-8"})
        ap = self.create_parser("--restore-state", path)
        self.assertIsNone(ap.open)
        self.assertEqual(ap.restore_state_path, path)

    def test_restore_state_missing_file_does_not_crash(self):
        ap = self.create_parser("--restore-state", "/no/such/file.json")
        self.assertIsNone(ap.open)
        self.assertEqual(ap.restore_state_path, "/no/such/file.json")

    def test_restore_state_path_defaults_to_none(self):
        ap = self.create_parser()
        self.assertIsNone(ap.restore_state_path)


if __name__ == "__main__":
    unittest.main()
