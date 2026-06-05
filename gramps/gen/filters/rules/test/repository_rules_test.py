#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Tom Samstag
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
Unittest that tests repository-specific filter rules
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest
import os

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....db.utils import import_as_dict
from ....filters import GenericFilterFactory
from ....const import TEST_DIR
from ....user import User

from ..repository import (
    AllRepos,
    HasIdOf,
    RegExpIdOf,
    HasNoteRegexp,
    HasReferenceCountOf,
    RepoPrivate,
    ChangedSince,
    MatchesNameSubstringOf,
    HasTag,
)

EXAMPLE = os.path.join(TEST_DIR, "example.gramps")
GenericRepositoryFilter = GenericFilterFactory("Repository")


class BaseTest(unittest.TestCase):
    """
    Repository rule tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """
        # the test results depend on specific grampsIds, so we need to use the same prefixes as the example database
        cls.db = import_as_dict(
            EXAMPLE,
            User(),
            person_prefix="I%04d",
            media_prefix="O%04d",
            family_prefix="F%04d",
            source_prefix="S%04d",
            citation_prefix="C%04d",
            place_prefix="P%04d",
            event_prefix="E%04d",
            repository_prefix="R%04d",
            note_prefix="N%04d",
        )

    def filter_with_rule(self, rule):
        """
        Apply a filter with the given rule.
        """
        filter_ = GenericRepositoryFilter()
        filter_.add_rule(rule)
        results = filter_.apply(self.db)
        return set(results)

    def test_allrepos(self):
        """
        Test AllRepos rule.
        """
        rule = AllRepos([])
        self.assertEqual(
            len(self.filter_with_rule(rule)), self.db.get_number_of_repositories()
        )

    def test_hasidof(self):
        """
        Test HasIdOf rule.
        """
        rule = HasIdOf(["R0000"])
        self.assertEqual(self.filter_with_rule(rule), set(["b39fe38593f3f8c4f12"]))

    def test_regexpidof(self):
        """
        Test RegExpIdOf rule.
        """
        rule = RegExpIdOf(["R000."], use_regex=True)
        self.assertEqual(
            self.filter_with_rule(rule),
            set(["a701ead12841521cd4d", "a701e99f93e5434f6f3", "b39fe38593f3f8c4f12"]),
        )

    def test_hasnoteregexp(self):
        """
        Test HasNoteRegexp rule.
        """
        rule = HasNoteRegexp(["."], use_regex=True)
        self.assertEqual(
            self.filter_with_rule(rule),
            set(["a701ead12841521cd4d", "b39fe38593f3f8c4f12"]),
        )

    def test_hasreferencecountof(self):
        """
        Test HasReferenceCountOf rule.
        """
        rule = HasReferenceCountOf(["greater than", "1"])
        self.assertEqual(self.filter_with_rule(rule), set(["a701e99f93e5434f6f3"]))

    def test_repoprivate(self):
        """
        Test RepoPrivate rule.
        """
        rule = RepoPrivate([])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_changedsince(self):
        """
        Test ChangedSince rule.
        """
        rule = ChangedSince(["2010-01-01", "2016-01-01"])
        self.assertEqual(self.filter_with_rule(rule), set(["a701e99f93e5434f6f3"]))

    def test_matchesnamesubstringof(self):
        """
        Test MatchesNameSubstringOf rule.
        """
        rule = MatchesNameSubstringOf(["Martha"])
        self.assertEqual(self.filter_with_rule(rule), set(["a701ead12841521cd4d"]))

    def test_hastag(self):
        """
        Test HasTag rule.
        """
        rule = HasTag(["ToDo"])
        self.assertEqual(self.filter_with_rule(rule), set())


if __name__ == "__main__":
    unittest.main()
