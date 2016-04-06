#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Tom Samstag
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
Unittest that tests family-specific filter rules
"""
import unittest

from gramps.gen.merge.diff import import_as_dict
from gramps.cli.user import User
from gramps.gen.filters import GenericFilterFactory

from gramps.gen.filters.rules.family import *

GenericFamilyFilter = GenericFilterFactory('Family')

class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = import_as_dict("example/gramps/example.gramps", User())

    def filter_with_rule(self, rule):
        filter_ = GenericFamilyFilter()
        filter_.add_rule(rule)
        results = filter_.apply(self.db)
        return set(results)

    def test_IsAncestorOf(self):
        rule = IsAncestorOf(['F0031', '0'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'4AXJQC96KTN3WGPTVE', b'1RUJQCYX9QL1V45YLD', b'5GTJQCXVYVAIQTBVKA',
            b'X3WJQCSF48F6809142', b'NSVJQC89IHEEBIPDP2', b'9OUJQCBOHW9UEK9CNV',
            b'1RUJQCCL9MVRYLMTBO', b'RRVJQC5A8DDHQFPRDL', b'0SUJQCOS78AXGWP8QR',
            b'57WJQCTBJKR5QYPS6K', b'8OUJQCUVZ0XML7BQLF', b'7PUJQC4PPS4EDIVMYE'
            ]))

    def test_IsDescendantOf(self):
        rule = IsDescendantOf(['F0031', '0'])
        self.assertEqual(self.filter_with_rule(rule), set([
            b'SFXJQCLE8PIG7PH38J', b'UCXJQCC5HS8VXDKWBM', b'IIEKQCRX89WYBHKB7R',
            b'XDXJQCMWU5EIV8XCRF', b'7BXJQCU22OCA4HN38A', b'3FXJQCR749H2H7G321',
            b'IEXJQCFUN95VENI6BO', b'4FXJQC7656WDQ3HJGW', b'FLEKQCRVG3O1UA9YUB',
            b'BCXJQC9AQ0DBXCVLEQ', b'9SEKQCAAWRUCIO7A0M', b'DDXJQCVT5X72TOXP0C',
            b'CGXJQC515QL9RLPQTU', b'XGXJQCNVZH2PWRMVAH', b'RBXJQCUYMQR2KRMDFY'
            ]))


if __name__ == "__main__":
    unittest.main()
