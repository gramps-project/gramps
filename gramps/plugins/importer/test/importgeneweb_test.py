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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Unit test of the GeneWebParser
"""
import unittest
import logging
from ..importgeneweb import GeneWebParser
from ....gen.lib.date import Date


class ParseDateTest(unittest.TestCase):
    def setUp(self):
        self.parse = GeneWebParser(dbase=None, file=None).parse_date

    def test_regular_date_parsed_dmy(self):
        d = self.parse("28/2/1876")
        self.assertEqual(d.get_ymd(), (1876, 2, 28))

    def test_invalid_date_stays_verbatim_text(self):
        text = "29/2/1875"
        logging.disable(logging.WARNING)
        d = self.parse(text)
        logging.disable(logging.NOTSET)
        self.assertEqual(d.get_modifier(), Date.MOD_TEXTONLY)
        self.assertEqual(d.get_text(), text)
