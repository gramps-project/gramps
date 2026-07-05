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

"""Tests for MergeEventQuery and Event super_event_list backlinks.

# python3 -m unittest gramps.gen.merge.test.mergeeventquery_test -v
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.utils.id import set_det_id
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.dbstate import DbState
from gramps.cli.clidbman import CLIDbManager
from gramps.gen.lib import Event, EventType
from gramps.gen.merge import MergeEventQuery


class MergeEventQueryTest(unittest.TestCase):
    param = "sqlite"

    def setUp(self):
        set_det_id(True)
        self.dbstate = DbState()
        self.dbman = CLIDbManager(self.dbstate)
        dirpath, _name = self.dbman.create_new_db_cli(
            "Test: MergeEventQuery", dbid=self.param
        )
        self.db = make_database(self.param)
        self.db.load(dirpath, None)
        self.dbstate.change_database_noclose(self.db)

    def tearDown(self):
        self.db.close()
        self.dbman.remove_database("Test: MergeEventQuery")

    def _add_event(self, description, super_event_list=None):
        event = Event()
        event.set_type(EventType.CUSTOM)
        event.set_description(description)
        event.set_super_event_list(super_event_list or [])
        with DbTxn("add event", self.db) as trans:
            self.db.add_event(event, trans)
        return event

    def test_merge_super_event_updates_sub_event_backlink(self):
        """Merging a super-event updates the sub-event's super_event_list."""
        super_a = self._add_event("Super A")
        super_b = self._add_event("Super B")
        sub = self._add_event("Sub", super_event_list=[super_b.handle])

        query = MergeEventQuery(self.dbstate, super_a, super_b)
        query.execute()

        updated_sub = self.db.get_event_from_handle(sub.handle)
        self.assertEqual(updated_sub.get_super_event_list(), [super_a.handle])
        with self.assertRaises(Exception):
            self.db.get_event_from_handle(super_b.handle)

    def test_merge_does_not_create_self_reference(self):
        """Merging a super-event into its own sub-event drops the stale link
        instead of making the result its own super-event."""
        super_event = self._add_event("Super")
        sub = self._add_event("Sub", super_event_list=[super_event.handle])

        # sub (phoenix) absorbs super_event (titanic): sub was a sub-event
        # of super_event, so after the merge sub must not reference itself.
        query = MergeEventQuery(self.dbstate, sub, super_event)
        query.execute()

        updated_sub = self.db.get_event_from_handle(sub.handle)
        self.assertEqual(updated_sub.get_super_event_list(), [])
        self.assertNotIn(sub.handle, updated_sub.get_super_event_list())

    def test_merge_unrelated_events_leaves_super_event_lists_untouched(self):
        """Merging events unrelated to any sub-event hierarchy is a no-op
        for other events' super_event_list."""
        top = self._add_event("Top")
        sub = self._add_event("Sub", super_event_list=[top.handle])
        other_a = self._add_event("Other A")
        other_b = self._add_event("Other B")

        query = MergeEventQuery(self.dbstate, other_a, other_b)
        query.execute()

        updated_sub = self.db.get_event_from_handle(sub.handle)
        self.assertEqual(updated_sub.get_super_event_list(), [top.handle])


if __name__ == "__main__":
    unittest.main()
