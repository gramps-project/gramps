#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Doug Blank <doug.blank@gmail.com>
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

"""Unittest for filter cancellation support."""

import io
import os
import unittest

from ...const import TEST_DIR
from ...db.utils import import_as_dict
from ...user import User
from ....cli.user import User as CliUser
from .. import GenericFilter, reload_custom_filters
from ....gen import filters as filters_module
from ..rules.person import HasIdOf, IsAncestorOfFilterMatch

EXAMPLE = os.path.join(TEST_DIR, "example.gramps")


class CancelAfterSteps(CliUser):
    """
    Test double, built on the real CLI User (not a bare stub), that
    reports itself as cancelled once a fixed number of
    ``step_progress()`` calls have been made, regardless of how many
    separate ``begin_progress``/``end_progress`` cycles they span.
    """

    def __init__(self, cancel_after):
        CliUser.__init__(self)
        self._fileout = io.StringIO()  # suppress progress output during tests
        self.cancel_after = cancel_after
        self.steps_taken = 0

    def step_progress(self):
        self.steps_taken += 1
        CliUser.step_progress(self)

    def get_cancelled(self):
        return self.steps_taken >= self.cancel_after


class FilterCancelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # the test results depend on specific grampsIds, so we need to use
        # the same prefixes as the example database
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

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.db = None

    def test_uncancelled_user_is_never_cancelled(self):
        user = User()
        filt = GenericFilter()
        results = filt.apply(self.db, user=user)
        self.assertFalse(user.get_cancelled())
        self.assertEqual(len(results), self.db.get_number_of_people())

    def test_cancel_before_any_step_returns_empty(self):
        user = CancelAfterSteps(cancel_after=0)
        filt = GenericFilter()
        results = filt.apply(self.db, user=user)
        self.assertEqual(results, [])

    def test_cancel_stops_apply_after_exact_step_count(self):
        # An empty rule list matches everyone, so the number of matches
        # found before cancellation is exactly the number of steps taken,
        # regardless of handle iteration order.
        for cancel_after in (1, 5, 50):
            with self.subTest(cancel_after=cancel_after):
                user = CancelAfterSteps(cancel_after=cancel_after)
                filt = GenericFilter()
                results = filt.apply(self.db, user=user)
                self.assertEqual(len(results), cancel_after)
                self.assertTrue(user.get_cancelled())

    def test_cancel_returns_subset_of_uncancelled_results(self):
        full_filter = GenericFilter()
        full_results = set(full_filter.apply(self.db))

        user = CancelAfterSteps(cancel_after=50)
        partial_filter = GenericFilter()
        partial_results = partial_filter.apply(self.db, user=user)

        self.assertEqual(len(partial_results), 50)
        self.assertTrue(set(partial_results).issubset(full_results))

    def test_cancel_during_filtermatch_prepare_does_not_raise(self):
        """
        Rules such as IsAncestorOfFilterMatch gather their sub-filter
        matches, then walk each match's ancestor tree during prepare().
        Cancelling partway through that recursive walk must not raise
        and must still return a usable (possibly partial) list.
        """
        reload_custom_filters()
        base = GenericFilter()
        base.set_logical_op("or")
        base.add_rule(HasIdOf(["I0006"]))
        base.add_rule(HasIdOf(["I0005"]))
        base.set_name("Base")
        filters_module.CustomFilters.get_filters_dict("Person")["Base"] = base
        try:
            full_filter = GenericFilter()
            full_filter.add_rule(IsAncestorOfFilterMatch(["Base"]))
            full_results = full_filter.apply(self.db)
            # sanity check: this rule matches a substantial part of the tree
            self.assertGreater(len(full_results), 10)

            user = CancelAfterSteps(cancel_after=2)
            cancelled_filter = GenericFilter()
            cancelled_filter.add_rule(IsAncestorOfFilterMatch(["Base"]))
            partial_results = cancelled_filter.apply(self.db, user=user)

            self.assertIsInstance(partial_results, list)
            self.assertLessEqual(len(partial_results), len(full_results))
            self.assertTrue(user.get_cancelled())
        finally:
            reload_custom_filters()


if __name__ == "__main__":
    unittest.main()
