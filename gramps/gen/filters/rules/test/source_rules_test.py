#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Tom Samstag
# Copyright (C) 2025 Doug Blank <doug.blank@gmail.com>
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
Unittest that tests source-specific filter rules
"""
import unittest
import os

from ....filters import reload_custom_filters

reload_custom_filters()
from ....db.utils import import_as_dict
from ....filters import GenericFilterFactory, CustomFilters
from ....const import DATA_DIR
from ....user import User

from ..repository import HasIdOf as RepositoryHasIdOf

from ..source import MatchesRepositoryFilter

TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")
GenericSourceFilter = GenericFilterFactory("Source")


class BaseTest(unittest.TestCase):
    """
    Source rule tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """
        cls.db = import_as_dict(EXAMPLE, User())

    def filter_with_rule(
        self,
        rule,
        l_op="and",
        invert=False,
        baserule=None,
        base_l_op="and",
        base_invert=False,
        base_name="Base",
        base_namespace="Source",
    ):
        """
        Apply a filter with the given rule.  'baserule' can be used to stack
        filters when using filters that are of 'offiltermatch' type.
        """
        if baserule:
            filter_constructor_ = GenericFilterFactory(base_namespace)
            filter_ = filter_constructor_()
            if isinstance(baserule, list):
                filter_.set_rules(baserule)
            else:
                filter_.add_rule(baserule)
            filter_.set_logical_op(base_l_op)
            filter_.set_invert(base_invert)
            filter_.set_name(base_name)
            filters = CustomFilters.get_filters_dict(base_namespace)
            filters[base_name] = filter_
        filter_ = GenericSourceFilter()
        if isinstance(rule, list):
            filter_.set_rules(rule)
        else:
            filter_.add_rule(rule)
        filter_.set_logical_op(l_op)
        filter_.set_invert(invert)
        results = filter_.apply(self.db)
        return set(results)

    def test_MatchesRepositoryFilter(self):
        """
        Test rule.
        """
        repository_rule = RepositoryHasIdOf(["R0002"])
        rule = MatchesRepositoryFilter(["Base"])
        res = self.filter_with_rule(
            rule, baserule=repository_rule, base_namespace="Repository"
        )
        self.assertEqual(len(res), 2)
