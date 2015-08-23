#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Donald N. Allingham
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

""" Unittest for testing ... """

import unittest

from ..keyword import (KEYWORDS, get_translation_from_keyword,
                       get_keyword_from_translation)

class TestCase(unittest.TestCase):

    def keyword_case(self, item1, item2):
        result = get_translation_from_keyword(item1)
        self.assertEqual(result, item2)

    def translation_case(self, item1, item2):
        result = get_keyword_from_translation(item1)
        self.assertEqual(result, item2)

    def test_from_keyword(self):
        for keyword, code, standard, upper in KEYWORDS:
            self.keyword_case(keyword, standard)

    def test_from_translation(self):
        for keyword, code, standard, upper in KEYWORDS:
            self.translation_case(standard, keyword)

    def test_from_lower(self):
        for keyword, code, standard, upper in KEYWORDS:
            self.translation_case(standard.lower(), keyword)

    def test_from_upper(self):
        for keyword, code, standard, upper in KEYWORDS:
            self.translation_case(upper, keyword.upper())


if __name__ == "__main__":
    unittest.main()
