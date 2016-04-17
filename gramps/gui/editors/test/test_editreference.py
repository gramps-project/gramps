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
import sys
try:
    if sys.version_info < (3,3):
        from mock import Mock, patch
    else:
        from unittest.mock import Mock, patch
    MOCKING = True
except:
    MOCKING = False

from  gramps.gen.lib import (Person, Family, Event, Source, Place, Citation,
                             Repository, Media, Note, Tag)
from gramps.cli.user import User
from gramps.gen.dbstate import DbState
from gramps.gen.merge.diff import *
from gramps.gui.editors.editreference import EditReference

class MockWindow():
    def set_transient_for(self, *args, **kwargs):
        pass
    def show_all(self):
        pass

class MockEditReference(EditReference):
    def __init__(self, dbstate, uistate, track, source, source_ref, update):
        self.window = MockWindow()
        super().__init__(dbstate, uistate, track, source, source_ref, update)

example = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "../../../..",
                 "example/gramps/example.gramps"))

class TestEditReference(unittest.TestCase):

    @unittest.skipUnless(MOCKING, "Requires unittest.mock to run")
    def test_editreference(self):
        dbstate = DbState()
        db = dbstate.make_database("bsddb")
        path = "/tmp/edit_ref_test"
        try:
            os.mkdir(path)
        except:
            pass
        db.write_version(path)
        db.load(path)
        dbstate.change_database(db)
        source = Place()
        source.gramps_id = "P0001"
        dbstate.db.place_map[source.handle] = source.serialize()
        editor = MockEditReference(dbstate, uistate=None, track=[],
                                   source=source, source_ref=None, update=None)
        with patch('gramps.gui.editors.editreference.ErrorDialog') as MockED:
            editor.check_for_duplicate_id("Place")
            self.assertTrue(MockED.called)

if __name__ == "__main__":
    unittest.main()
