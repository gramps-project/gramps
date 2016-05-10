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
from .. import user

class TestUser:
    TITLE = "Testing prompt"
    MSG = "Choices are hard. Nevertheless, please choose!"
    ACCEPT = "To be"
    REJECT = "Not to be"

class TestUser_prompt(unittest.TestCase):
    def setUp(self):
        self.user = user.User()

    def test_not_implemented(self):
        self.assertRaises(NotImplementedError, self.user.prompt,
                          TestUser.TITLE,
                          TestUser.MSG,
                          TestUser.ACCEPT,
                          TestUser.REJECT)

if __name__ == "__main__":
    unittest.main()
