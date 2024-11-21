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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Unittest that tests event-specific filter rules
"""
import unittest
import os

from ....db.utils import import_as_dict
from ....filters import GenericFilterFactory
from ....const import DATA_DIR
from ....user import User
from ....utils.unittest import localize_date

from ..event import (
    AllEvents,
    HasType,
    HasIdOf,
    HasGallery,
    RegExpIdOf,
    HasCitation,
    HasNote,
    HasNoteRegexp,
    HasReferenceCountOf,
    HasSourceCount,
    EventPrivate,
    MatchesSourceConfidence,
    HasAttribute,
    HasData,
    ChangedSince,
    HasTag,
    HasDayOfWeek,
)

TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")
GenericEventFilter = GenericFilterFactory("Event")


class BaseTest(unittest.TestCase):
    """
    Event rule tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """
        cls.db = import_as_dict(EXAMPLE, User())

    def filter_with_rule(self, rule):
        """
        Apply a filter with the given rule.
        """
        filter_ = GenericEventFilter()
        filter_.add_rule(rule)
        results = filter_.apply(self.db)
        return set(results)

    def test_allevents(self):
        """
        Test AllEvents rule.
        """
        rule = AllEvents([])
        self.assertEqual(
            len(self.filter_with_rule(rule)), self.db.get_number_of_events()
        )

    def test_hastype(self):
        """
        Test HasType rule.
        """
        rule = HasType(["Burial"])
        self.assertEqual(len(self.filter_with_rule(rule)), 296)

    def test_hasidof(self):
        """
        Test HasIdOf rule.
        """
        rule = HasIdOf(["E0001"])
        self.assertEqual(self.filter_with_rule(rule), set(["a5af0eb696917232725"]))

    def test_hasgallery(self):
        """
        Test HasGallery rule.
        """
        rule = HasGallery(["0", "greater than"])
        self.assertEqual(self.filter_with_rule(rule), set(["a5af0ecb107303354a0"]))

    def test_regexpidof(self):
        """
        Test RegExpIdOf rule.
        """
        rule = RegExpIdOf(["E000."], use_regex=True)
        self.assertEqual(
            self.filter_with_rule(rule),
            set(
                [
                    "a5af0eb69cf2d3fb615",
                    "a5af0eb667015e355db",
                    "a5af0eb6a016da2d6d1",
                    "a5af0eb6a405acb126c",
                    "a5af0eb698f29568502",
                    "a5af0eb69b82a6cdc5a",
                    "a5af0eb69f41bfb5a6a",
                    "a5af0eb69c40c179441",
                    "a5af0eb6a3229544ba2",
                    "a5af0eb696917232725",
                ]
            ),
        )

    def test_hascitation(self):
        """
        Test HasCitation rule.
        """
        rule = HasCitation(["page 1", "", ""])
        self.assertEqual(self.filter_with_rule(rule), set(["a5af0ecb107303354a0"]))

    def test_hasnote(self):
        """
        Test HasNote rule.
        """
        rule = HasNote([])
        self.assertEqual(self.filter_with_rule(rule), set(["a5af0ecb11f5ac3110e"]))

    def test_hasnoteregexp(self):
        """
        Test HasNoteRegexp rule.
        """
        rule = HasNoteRegexp(["."], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set(["a5af0ecb11f5ac3110e"]))

    def test_hasreferencecountof(self):
        """
        Test HasReferenceCountOf rule.
        """
        rule = HasReferenceCountOf(["greater than", "1"])
        self.assertEqual(
            self.filter_with_rule(rule),
            set(["cc8205d86fc4e9706a5", "a5af0ed60de7a612b9e", "cc820604ef05cb67907"]),
        )

    def test_hassourcecount(self):
        """
        Test HasSourceCount rule.
        """
        rule = HasSourceCount(["1", "greater than"])
        self.assertEqual(self.filter_with_rule(rule), set(["a5af0ecb107303354a0"]))

    def test_eventprivate(self):
        """
        Test EventPrivate rule.
        """
        rule = EventPrivate([])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_matchessourceconfidence(self):
        """
        Test MatchesSourceConfidence rule.
        """
        rule = MatchesSourceConfidence(["2"])
        self.assertEqual(self.filter_with_rule(rule), set(["a5af0ecb107303354a0"]))

    def test_hasattribute(self):
        """
        Test HasAttribute rule.
        """
        rule = HasAttribute(["Cause", ""])
        self.assertEqual(self.filter_with_rule(rule), set(["a5af0ecb11f5ac3110e"]))

    def test_hasdata(self):
        """
        Test HasData rule.
        """
        date_str = localize_date("before 1800")
        rule = HasData(["Burial", date_str, "USA", ""])
        self.assertEqual(
            self.filter_with_rule(rule),
            set(["a5af0ed4211095487d2", "a5af0ed36793c1d3e05", "a5af0ecfcc16ce7a96a"]),
        )

    def test_changedsince(self):
        """
        Test ChangedSince rule.
        """
        rule = ChangedSince(["2011-01-01", "2014-01-01"])
        self.assertEqual(
            self.filter_with_rule(rule),
            set(["a5af0ecb107303354a0", "a5af0ecb11f5ac3110e", "a5af0ed5df832ee65c1"]),
        )

    def test_hastag(self):
        """
        Test HasTag rule.
        """
        rule = HasTag(["ToDo"])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_hasdayofweek(self):
        """
        Test HasDayOfWeek rule.
        """
        rule = HasDayOfWeek(["2"])
        self.assertEqual(len(self.filter_with_rule(rule)), 185)


if __name__ == "__main__":
    unittest.main()
