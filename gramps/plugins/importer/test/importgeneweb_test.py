#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013 Vassilii Khachaturov
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Unit test of the GeneWebParser
"""
from __future__ import print_function
import unittest
from ..importgeneweb import GeneWebParser
from ....gen.lib.date import Date

class ParseDateTest(unittest.TestCase):
    def setUp(self):
        self.parse = GeneWebParser(dbase=None, file=None).parse_date

    def test_regular_date_parsed_dmy(self):
        d = self.parse("28/2/1876")
        self.assertEqual(d.get_dmy(), (28, 2, 1876))

    def test_invalid_date_stays_verbatim_text(self):
        text = "29/2/1875"
        d = self.parse(text)
        self.assertEqual(d.get_modifier(), Date.MOD_TEXTONLY)
        self.assertEqual(d.get_text(), text)
