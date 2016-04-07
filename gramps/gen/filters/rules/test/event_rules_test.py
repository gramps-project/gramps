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

from gramps.gen.merge.diff import import_as_dict
from gramps.cli.user import User
from gramps.gen.filters import GenericFilterFactory

from gramps.gen.filters.rules.event import *

GenericEventFilter = GenericFilterFactory('Event')

class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = import_as_dict("example/gramps/example.gramps", User())

    def filter_with_rule(self, rule):
        filter_ = GenericEventFilter()
        filter_.add_rule(rule)
        results = filter_.apply(self.db)
        return set(results)

    def test_AllEvents(self):
        rule = AllEvents([])
        self.assertEqual(len(self.filter_with_rule(rule)),
                         self.db.get_number_of_events())

    def test_HasType(self):
        rule = HasType(['Burial'])
        self.assertEqual(len(self.filter_with_rule(rule)), 296)

    def test_HasIdOf(self):
        rule = HasIdOf(['E0001'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'a5af0eb696917232725']))

    def test_HasGallery(self):
        rule = HasGallery(['0', 'greater than'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'a5af0ecb107303354a0']))

    def test_RegExpIdOf(self):
        rule = RegExpIdOf(['E000.'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set([
            b'a5af0eb69cf2d3fb615', b'a5af0eb667015e355db',
            b'a5af0eb6a016da2d6d1', b'a5af0eb6a405acb126c',
            b'a5af0eb698f29568502', b'a5af0eb69b82a6cdc5a',
            b'a5af0eb69f41bfb5a6a', b'a5af0eb69c40c179441',
            b'a5af0eb6a3229544ba2', b'a5af0eb696917232725']))

    def test_HasCitation(self):
        rule = HasCitation(['page 1', '', ''])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'a5af0ecb107303354a0']))

    def test_HasNote(self):
        rule = HasNote([])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'a5af0ecb11f5ac3110e']))

    def test_HasNoteRegexp(self):
        rule = HasNoteRegexp(['.'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'a5af0ecb11f5ac3110e']))

    def test_HasReferenceCountOf(self):
        rule = HasReferenceCountOf(['greater than', '1'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'cc8205d86fc4e9706a5', b'a5af0ed60de7a612b9e',
            b'cc820604ef05cb67907']))

    def test_HasSourceCount(self):
        rule = HasSourceCount(['1', 'greater than'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'a5af0ecb107303354a0']))

    def test_EventPrivate(self):
        rule = EventPrivate([])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_MatchesSourceConfidence(self):
        rule = MatchesSourceConfidence(['2'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'a5af0ecb107303354a0']))

    def test_HasAttribute(self):
        rule = HasAttribute(['Cause', ''])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'a5af0ecb11f5ac3110e']))

    def test_HasData(self):
        rule = HasData(['Burial', 'before 1800', 'USA', ''])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'a5af0ed4211095487d2', b'a5af0ed36793c1d3e05',
            b'a5af0ecfcc16ce7a96a']))

    def test_ChangedSince(self):
        rule = ChangedSince(['2011-01-01', '2014-01-01'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'a5af0ecb107303354a0', b'a5af0ecb11f5ac3110e',
            b'a5af0ed5df832ee65c1']))

    def test_HasTag(self):
        rule = HasTag(['ToDo'])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_HasDayOfWeek(self):
        rule = HasDayOfWeek(['2'])
        self.assertEqual(len(self.filter_with_rule(rule)), 177)


if __name__ == "__main__":
    unittest.main()
