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

""" Unittest for constfunc.py """

import unittest
from .. import constfunc

from os import environ as env


class Test_has_display(unittest.TestCase):
    def setUp(self):
        self.has = constfunc.has_display()
        self.display_nonempty = ("DISPLAY" in env) and bool(env["DISPLAY"])

    @unittest.skipUnless(constfunc.lin(), "Written for Linux only...")
    def test_consistent_with_DISPLAY_env(self):
        assert (
            self.has == self.display_nonempty
        ), "has_display(): {}, $DISPLAY: {}".format(
            self.has, env["DISPLAY"] if ("DISPLAY" in env) else "(unset)"
        )


if __name__ == "__main__":
    unittest.main()
