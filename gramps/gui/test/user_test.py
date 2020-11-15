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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

""" Unittest for user.py """

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
        with patch('gramps.gui.user.QuestionDialog2') as MockQD:
            self.user.prompt(TestUser.TITLE, TestUser.MSG,
                             TestUser.ACCEPT, TestUser.REJECT, parent=None)
        MockQD.assert_called_once_with(TestUser.TITLE, TestUser.MSG,
                                       TestUser.ACCEPT, TestUser.REJECT,
                                       parent=None)
        MockQD.return_value.run.assert_called_once_with()
        # TODO test that run's return is the one returned by prompt()...

class TestUser_init_accepts_uistate(unittest.TestCase):
    def test(self):
        user.User(uistate = None)

if __name__ == "__main__":
    unittest.main()
