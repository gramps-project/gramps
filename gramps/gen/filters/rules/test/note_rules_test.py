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
Unittest that tests note-specific filter rules
"""
import unittest

from gramps.gen.merge.diff import import_as_dict
from gramps.cli.user import User
from gramps.gen.filters import GenericFilterFactory

from gramps.gen.filters.rules.note import (
    AllNotes, HasIdOf, RegExpIdOf, HasNote, MatchesRegexpOf,
    HasReferenceCountOf, NotePrivate, ChangedSince, HasTag, HasType)

GenericNoteFilter = GenericFilterFactory('Note')

class BaseTest(unittest.TestCase):
    """
    Note rule tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """
        cls.db = import_as_dict("example/gramps/example.gramps", User())

    def filter_with_rule(self, rule):
        """
        Apply a filter with the given rule.
        """
        filter_ = GenericNoteFilter()
        filter_.add_rule(rule)
        results = filter_.apply(self.db)
        return set(results)

    def test_allnotes(self):
        """
        Test AllNotes rule.
        """
        rule = AllNotes([])
        self.assertEqual(len(self.filter_with_rule(rule)),
                         self.db.get_number_of_notes())

    def test_hasidof(self):
        """
        Test HasIdOf rule.
        """
        rule = HasIdOf(['N0001'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'ac380498bac48eedee8']))

    def test_regexpidof(self):
        """
        Test RegExpIdOf rule.
        """
        rule = RegExpIdOf(['N000.'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set([
            b'ac380498c020c7bcdc7', b'ac3804a842b21358c97',
            b'ae13613d581506d040892f88a21', b'ac3804a8405171ef666',
            b'ac3804a1d747a39822c', b'ac3804aac6b762b75a5',
            b'ac380498bac48eedee8', b'ac3804a1d66258b8e13',
            b'ac380498bc46102e1e8', b'b39fe2e143d1e599450']))

    def test_hasnote(self):
        """
        Test HasNote rule.
        """
        rule = HasNote(['note', 'Person Note'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'b39ff11d8912173cded', b'b39ff01f75c1f76859a']))

    def test_matchesregexpof(self):
        """
        Test MatchesRegexpOf rule.
        """
        rule = MatchesRegexpOf(['^This'], use_regex=True)
        self.assertEqual(self.filter_with_rule(rule), set([
            b'b39ff11d8912173cded', b'c140d4c29520c92055c',
            b'b39ff01f75c1f76859a']))

    def test_hasreferencecountof(self):
        """
        Test HasReferenceCountOf rule.
        """
        rule = HasReferenceCountOf(['greater than', '1'])
        self.assertEqual(self.filter_with_rule(rule),
                         set([b'c140d4c29520c92055c']))

    def test_noteprivate(self):
        """
        Test NotePrivate rule.
        """
        rule = NotePrivate([])
        self.assertEqual(self.filter_with_rule(rule), set([]))

    def test_changedsince(self):
        """
        Test ChangedSince rule.
        """
        rule = ChangedSince(['2010-01-01', '2016-01-01'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'c140d4c29520c92055c', b'd0436bcc69d6bba278bff5bc7db',
            b'b39fe2e143d1e599450', b'd0436bba4ec328d3b631259a4ee',
            b'd0436be64ac277b615b79b34e72']))

    def test_hastag(self):
        """
        Test HasTag rule.
        """
        rule = HasTag(['ToDo'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'b39ff01f75c1f76859a', b'b39fe2e143d1e599450']))

    def test_hastype(self):
        """
        Test HasType rule.
        """
        rule = HasType(['Person Note'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'ac380498c020c7bcdc7', b'b39ff11d8912173cded',
            b'b39ff01f75c1f76859a']))


if __name__ == "__main__":
    unittest.main()
