# -*- coding: utf-8 -*-
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

"""Unittest for the cancellation support in user.py"""

import unittest

from .. import user


class TestUser_get_cancelled(unittest.TestCase):
    def setUp(self):
        self.user = user.User()

    def test_default_is_not_cancelled(self):
        self.assertFalse(self.user.get_cancelled())

    def test_begin_progress_accepts_can_cancel_and_callback(self):
        # The no-op User must accept the same arguments as every other
        # User implementation, even though it does nothing with them.
        called = []
        self.user.begin_progress(
            "Title", "Message", 10, can_cancel=True, cancel_callback=called.append
        )
        self.user.step_progress()
        self.user.end_progress()
        self.assertFalse(self.user.get_cancelled())
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
