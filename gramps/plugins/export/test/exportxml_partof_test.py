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

"""Round-trip test for Event.super_event_list through Gramps XML.

# python3 -m unittest gramps.plugins.export.test.exportxml_partof_test -v
"""

import os
import shutil
import tempfile
import unittest

import gi

gi.require_version("Gtk", "3.0")

from gramps.cli.user import User
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import Event, EventType
from gramps.plugins.export.exportxml import export_data
from gramps.plugins.importer.importxml import importData


class ExportImportPartOfTest(unittest.TestCase):
    """Tests that super_event_list survives an XML export/import round trip."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)

    def _make_source_db(self):
        db = make_database("sqlite")
        source_dir = os.path.join(self.tmpdir, "source_db")
        os.mkdir(source_dir)
        db.load(source_dir)

        top = Event()
        top.set_type(EventType.CUSTOM)
        top.set_description("Emigration 1882")
        mid = Event()
        mid.set_type(EventType.CUSTOM)
        mid.set_description("Montebello Journey")
        sub = Event()
        sub.set_type(EventType.CUSTOM)
        sub.set_description("Departure from Bremen")

        with DbTxn("add events", db) as trans:
            db.add_event(top, trans)
            db.add_event(mid, trans)
            db.add_event(sub, trans)
            mid.add_super_event(top.handle)
            sub.add_super_event(mid.handle)
            db.commit_event(mid, trans)
            db.commit_event(sub, trans)

        return db, top.gramps_id, mid.gramps_id, sub.gramps_id

    def test_super_event_list_round_trip(self):
        db, top_gid, mid_gid, sub_gid = self._make_source_db()

        xml_path = os.path.join(self.tmpdir, "export.gramps")
        export_data(db, xml_path, User())
        db.close()

        target = make_database("sqlite")
        target_dir = os.path.join(self.tmpdir, "target_db")
        os.mkdir(target_dir)
        target.load(target_dir)
        importData(target, xml_path, User())

        top2 = target.get_event_from_gramps_id(top_gid)
        mid2 = target.get_event_from_gramps_id(mid_gid)
        sub2 = target.get_event_from_gramps_id(sub_gid)

        self.assertEqual(mid2.get_super_event_list(), [top2.handle])
        self.assertEqual(sub2.get_super_event_list(), [mid2.handle])
        self.assertEqual(top2.get_super_event_list(), [])

        target.close()


if __name__ == "__main__":
    unittest.main()
