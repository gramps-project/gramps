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

"""Unittest for user.py"""

import unittest
from unittest.mock import Mock, patch
from .. import user


class TestUser:
    TITLE = "Testing prompt"
    MSG = "Choices are hard. Nevertheless, please choose!"
    ACCEPT = "To be"
    REJECT = "Not to be"


class TestUser_prompt(unittest.TestCase):
    def setUp(self):
        self.user = user.User()

    def test_prompt_runs_QuestionDialog2(self):
        with patch("gramps.gui.user.QuestionDialog2") as MockQD:
            self.user.prompt(
                TestUser.TITLE,
                TestUser.MSG,
                TestUser.ACCEPT,
                TestUser.REJECT,
                parent=None,
            )
        MockQD.assert_called_once_with(
            TestUser.TITLE, TestUser.MSG, TestUser.ACCEPT, TestUser.REJECT, parent=None
        )
        MockQD.return_value.run.assert_called_once_with()
        # TODO test that run's return is the one returned by prompt()...


class TestUser_init_accepts_uistate(unittest.TestCase):
    def test(self):
        user.User(uistate=None)


class TestUser_get_cancelled(unittest.TestCase):
    def setUp(self):
        self.user = user.User()

    def test_default_is_not_cancelled(self):
        self.assertFalse(self.user.get_cancelled())

    def test_begin_progress_passes_can_cancel_and_callback_to_progressmeter(self):
        callback = Mock()
        with (
            patch("gramps.gui.user.ProgressMeter") as MockPM,
            patch("gramps.gui.user.Gtk") as MockGtk,
        ):
            MockGtk.events_pending.return_value = False
            self.user.begin_progress(
                "Title", "Message", 10, can_cancel=True, cancel_callback=callback
            )
        MockPM.assert_called_once_with(
            "Title",
            parent=self.user.parent,
            can_cancel=True,
            cancel_callback=callback,
        )

    def test_get_cancelled_delegates_to_active_progress_meter(self):
        with (
            patch("gramps.gui.user.ProgressMeter") as MockPM,
            patch("gramps.gui.user.Gtk") as MockGtk,
        ):
            MockGtk.events_pending.return_value = False
            MockPM.return_value.get_cancelled.return_value = True
            self.user.begin_progress("Title", "Message", 10, can_cancel=True)
            self.assertTrue(self.user.get_cancelled())

    def test_get_cancelled_false_once_progress_ends(self):
        with (
            patch("gramps.gui.user.ProgressMeter") as MockPM,
            patch("gramps.gui.user.Gtk") as MockGtk,
        ):
            MockGtk.events_pending.return_value = False
            MockPM.return_value.get_cancelled.return_value = True
            self.user.begin_progress("Title", "Message", 10, can_cancel=True)
            self.user.end_progress()
        self.assertFalse(self.user.get_cancelled())


if __name__ == "__main__":
    unittest.main()
