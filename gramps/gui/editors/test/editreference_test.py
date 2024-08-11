#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013 Doug Blank <doug.blank@gmail.com>
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

""" Unittest for editreference.py """

import unittest
from unittest.mock import Mock, patch
import os

from gramps.gen.lib import (
    Person,
    Family,
    Event,
    Source,
    Place,
    Citation,
    Repository,
    Media,
    Note,
    Tag,
)
from gramps.cli.user import User
from gramps.gen.dbstate import DbState
from gramps.gen.db.utils import make_database
from gramps.gen.db import DbTxn
from gramps.gui.editors.editreference import EditReference


class MockWindow:
    def set_transient_for(self, *args, **kwargs):
        pass

    def show_all(self):
        pass


class MockEditReference(EditReference):
    def __init__(self, dbstate, uistate, track, source, source_ref, update):
        self.window = MockWindow()
        super().__init__(dbstate, uistate, track, source, source_ref, update)


class TestEditReference(unittest.TestCase):
    def test_editreference(self):
        dbstate = DbState()
        db = make_database("sqlite")
        path = "/tmp/edit_ref_test"
        try:
            os.mkdir(path)
        except:
            pass
        db.load(path)
        dbstate.change_database(db)
        source = Place()
        source.gramps_id = "P0001"
        with DbTxn("test place", dbstate.db) as trans:
            dbstate.db.add_place(source, trans)
        editor = MockEditReference(
            dbstate, uistate=None, track=[], source=source, source_ref=None, update=None
        )
        with patch("gramps.gui.editors.editreference.ErrorDialog") as MockED:
            editor.check_for_duplicate_id("Place")
            self.assertTrue(MockED.called)


if __name__ == "__main__":
    unittest.main()
