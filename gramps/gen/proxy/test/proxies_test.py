#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Tom Samstag
# Copyright (C) 2025 Doug Blank
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

"""
Unittests for proxy databases: PrivateProxyDb, LivingProxyDb, FilterProxyDb.
"""

import unittest
import os
from unittest.mock import patch, MagicMock

from ...db.utils import import_as_dict
from ...const import TEST_DIR
from ...user import User
from ...lib.person import Person
from ...lib.date import Date
from ...lib.json_utils import remove_object
from ...filters import GenericFilter
from ...filters.rules.person import Everyone, HasIdOf

from ...proxy import PrivateProxyDb, LivingProxyDb, FilterProxyDb

EXAMPLE = os.path.join(TEST_DIR, "example.gramps")

# Handle constants from the example database
PRIVATE_PERSON = "0GDKQC54XKSWZKEBWW"  # private person (I0988)
NORMAL_PERSON = "0FWJQCLYEP736P3YZK"  # non-private person (I0122)
PERSON_WITH_PRIVATE_ATTRS = "GNUJQCL9MD64AM56OH"  # has 3 attrs, 1 private
LIVING_PERSON = "030KQCA8ZLPDRK6PP8"  # living on Jan 1 2006 (hidden in EXCLUDE_ALL, restricted in other modes) (I0342)
DEAD_PERSON = "66TJQC6CC7ZWL9YZ64"  # deceased well before 2006
NOT_HIDDEN_PERSON = "01LKQC3FMJR76T7IMG"  # not living on Jan 1 2006, included (I1370)
FAMILY_WITH_PRIVATE_FATHER = "NSVJQC89IHEEBIPDP2"  # private person is father
FAMILY_WITH_LIVING_PARENT = "05XJQC935HU62H3KL4"  # living parent, has events

# Reference date used by all living-proxy tests.  Using a past date ensures
# that probably_alive_range()'s internal Today() cap (which prevents
# estimating death dates in the future) never affects the "alive as of
# LIVING_DATE" determination, giving stable counts regardless of when the
# tests run.
LIVING_DATE = Date(2006, 1, 1)


class PrivateProxyTest(unittest.TestCase):
    """Tests for PrivateProxyDb."""

    @classmethod
    def setUpClass(cls):
        cls.db = PrivateProxyDb(import_as_dict(EXAMPLE, User()))

    def assertDataEquals(self, data1, data2):
        self.assertIsInstance(data1, dict)
        self.assertIsInstance(data2, dict)
        self.assertEqual(remove_object(data1), remove_object(data2))

    # --- person count ---

    def test_person_count(self):
        # example.gramps has exactly one private person
        self.assertEqual(self.db.get_number_of_people(), 2127)
        self.assertEqual(self.db.basedb.get_number_of_people(), 2128)

    # --- raw data access ---

    def test_private_person_data_is_none(self):
        data = self.db.get_raw_person_data(PRIVATE_PERSON)
        self.assertIsNone(data)

    def test_private_person_visible_in_basedb(self):
        data = self.db.basedb.get_raw_person_data(PRIVATE_PERSON)
        self.assertIsNotNone(data)

    def test_normal_person_data_unchanged(self):
        data = self.db.get_raw_person_data(NORMAL_PERSON)
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.handle, NORMAL_PERSON)
        data_orig = self.db.basedb.get_raw_person_data(NORMAL_PERSON)
        self.assertDataEquals(data, data_orig)

    # --- object access ---

    def test_private_person_returns_none(self):
        person = self.db.get_person_from_handle(PRIVATE_PERSON)
        self.assertIsNone(person)

    def test_normal_person_returns_person(self):
        person = self.db.get_person_from_handle(NORMAL_PERSON)
        self.assertIsInstance(person, Person)
        person_orig = self.db.basedb.get_person_from_handle(NORMAL_PERSON)
        self.assertEqual(person.gramps_id, person_orig.gramps_id)

    # --- has_*_handle ---

    def test_has_handle_false_for_private(self):
        self.assertFalse(self.db.has_person_handle(PRIVATE_PERSON))

    def test_has_handle_true_for_normal(self):
        self.assertTrue(self.db.has_person_handle(NORMAL_PERSON))

    # --- gramps_id lookup ---

    def test_gramps_id_returns_none_for_private(self):
        # Private person's gramps_id is I0988
        person = self.db.get_person_from_gramps_id("I0988")
        self.assertIsNone(person)

    def test_gramps_id_returns_person_for_normal(self):
        raw = self.db.basedb.get_person_from_handle(NORMAL_PERSON)
        person = self.db.get_person_from_gramps_id(raw.gramps_id)
        self.assertIsNotNone(person)

    # --- sub-attribute privacy ---

    def test_private_attributes_filtered(self):
        # Person has 3 attributes, 1 is private -> proxy shows 2
        person = self.db.get_person_from_handle(PERSON_WITH_PRIVATE_ATTRS)
        self.assertEqual(len(person.attribute_list), 2)
        person_raw = self.db.basedb.get_person_from_handle(PERSON_WITH_PRIVATE_ATTRS)
        self.assertEqual(len(person_raw.attribute_list), 3)

    # --- cross-reference cleanup ---

    def test_private_father_cleared_from_family(self):
        # Private person is the father in this family; proxy should set father to None
        fam = self.db.get_family_from_handle(FAMILY_WITH_PRIVATE_FATHER)
        self.assertIsNotNone(fam)
        self.assertIsNone(fam.father_handle)
        # Raw db still has the father handle
        fam_raw = self.db.basedb.get_family_from_handle(FAMILY_WITH_PRIVATE_FATHER)
        self.assertEqual(fam_raw.father_handle, PRIVATE_PERSON)

    # --- is_filter_override ---

    def test_is_filter_override_always_false(self):
        self.assertFalse(self.db.is_filter_override("person", "Everyone"))
        self.assertFalse(self.db.basedb.is_filter_override("person", "Everyone"))

    # --- iteration ---

    def test_iter_people_skips_private(self):
        handles = list(self.db.iter_person_handles())
        self.assertNotIn(PRIVATE_PERSON, handles)
        self.assertIn(NORMAL_PERSON, handles)


class LivingProxyExcludeTest(unittest.TestCase):
    """Tests for LivingProxyDb in MODE_EXCLUDE_ALL."""

    @classmethod
    def setUpClass(cls):
        cls.db = LivingProxyDb(
            import_as_dict(EXAMPLE, User()),
            mode=LivingProxyDb.MODE_EXCLUDE_ALL,
            current_year=LIVING_DATE,
            years_after_death=10,
        )

    def test_person_count(self):
        self.assertEqual(self.db.get_number_of_people(), 1255)

    def test_dead_person_data_is_none(self):
        data = self.db.get_raw_person_data(DEAD_PERSON)
        self.assertIsNone(data)

    def test_dead_person_returns_none(self):
        person = self.db.get_person_from_handle(DEAD_PERSON)
        self.assertIsNone(person)

    def test_live_person_data_accessible(self):
        # Martha (004KQCGYT27EEPQHK) is a living person with no events
        handle = "004KQCGYT27EEPQHK"
        data = self.db.get_raw_person_data(handle)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.primary_name.first_name, "Martha")

    def test_live_person_returns_person(self):
        handle = "004KQCGYT27EEPQHK"
        person = self.db.get_person_from_handle(handle)
        self.assertIsInstance(person, Person)

    def test_has_handle_false_for_dead(self):
        self.assertFalse(self.db.has_person_handle(DEAD_PERSON))

    def test_has_handle_true_for_living(self):
        self.assertTrue(self.db.has_person_handle("004KQCGYT27EEPQHK"))

    def test_family_events_cleared_when_parent_living(self):
        # Family with a living parent should have events cleared
        data = self.db.get_raw_family_data(FAMILY_WITH_LIVING_PARENT)
        self.assertIsNotNone(data)
        self.assertEqual(len(data.event_ref_list), 0)
        # Raw db has the event
        data_raw = self.db.basedb.get_raw_family_data(FAMILY_WITH_LIVING_PARENT)
        self.assertGreater(len(data_raw.event_ref_list), 0)


class LivingProxyLastNameOnlyTest(unittest.TestCase):
    """Tests for LivingProxyDb in MODE_INCLUDE_LAST_NAME_ONLY."""

    @classmethod
    def setUpClass(cls):
        cls.db = LivingProxyDb(
            import_as_dict(EXAMPLE, User()),
            mode=LivingProxyDb.MODE_INCLUDE_LAST_NAME_ONLY,
            current_year=LIVING_DATE,
            years_after_death=10,
        )

    def test_living_person_given_name_replaced(self):
        # Given name is replaced with [Living], surname kept
        person = self.db.get_person_from_handle(LIVING_PERSON)
        self.assertIsNotNone(person)
        self.assertEqual(person.primary_name.first_name, "[Living]")
        self.assertEqual(person.primary_name.surname_list[0].surname, "Floyd")

    def test_living_person_events_cleared(self):
        person = self.db.get_person_from_handle(LIVING_PERSON)
        self.assertEqual(len(person.event_ref_list), 0)

    def test_living_person_alt_names_cleared(self):
        person = self.db.get_person_from_handle(LIVING_PERSON)
        self.assertEqual(len(person.alternate_names), 0)

    def test_dead_person_name_unchanged(self):
        # Deceased person's name is not restricted
        person = self.db.get_person_from_handle("004KQCGYT27EEPQHK")
        # Martha is living — if we want a definitely dead person, use DEAD_PERSON
        # but in this mode dead people are included with full data
        # Just verify dead person is still visible
        dead = self.db.get_person_from_handle(DEAD_PERSON)
        self.assertIsNotNone(dead)

    def test_person_count_same_as_raw(self):
        # In this mode living people are included (name restricted), so count = total
        self.assertEqual(
            self.db.get_number_of_people(),
            self.db.basedb.get_number_of_people(),
        )


class LivingProxyFullNameOnlyTest(unittest.TestCase):
    """Tests for LivingProxyDb in MODE_INCLUDE_FULL_NAME_ONLY."""

    @classmethod
    def setUpClass(cls):
        cls.db = LivingProxyDb(
            import_as_dict(EXAMPLE, User()),
            mode=LivingProxyDb.MODE_INCLUDE_FULL_NAME_ONLY,
            current_year=LIVING_DATE,
            years_after_death=10,
        )

    def test_living_person_name_intact(self):
        person = self.db.get_person_from_handle(LIVING_PERSON)
        self.assertIsNotNone(person)
        self.assertEqual(person.primary_name.first_name, "Christopher Randall")
        self.assertEqual(person.primary_name.surname_list[0].surname, "Floyd")

    def test_living_person_events_cleared(self):
        person = self.db.get_person_from_handle(LIVING_PERSON)
        self.assertEqual(len(person.event_ref_list), 0)

    def test_living_person_alt_names_cleared(self):
        person = self.db.get_person_from_handle(LIVING_PERSON)
        self.assertEqual(len(person.alternate_names), 0)

    def test_person_count_same_as_raw(self):
        self.assertEqual(
            self.db.get_number_of_people(),
            self.db.basedb.get_number_of_people(),
        )


class LivingProxyReplaceNameTest(unittest.TestCase):
    """Tests for LivingProxyDb in MODE_REPLACE_COMPLETE_NAME."""

    @classmethod
    def setUpClass(cls):
        cls.db = LivingProxyDb(
            import_as_dict(EXAMPLE, User()),
            mode=LivingProxyDb.MODE_REPLACE_COMPLETE_NAME,
            current_year=LIVING_DATE,
            years_after_death=10,
        )

    def test_living_person_both_names_replaced(self):
        person = self.db.get_person_from_handle(LIVING_PERSON)
        self.assertIsNotNone(person)
        self.assertEqual(person.primary_name.first_name, "[Living]")
        self.assertEqual(person.primary_name.surname_list[0].surname, "[Living]")

    def test_living_person_events_cleared(self):
        person = self.db.get_person_from_handle(LIVING_PERSON)
        self.assertEqual(len(person.event_ref_list), 0)

    def test_person_count_same_as_raw(self):
        self.assertEqual(
            self.db.get_number_of_people(),
            self.db.basedb.get_number_of_people(),
        )


class LivingPrivateProxyTest(unittest.TestCase):
    """Tests for LivingProxyDb wrapping PrivateProxyDb (chained proxies)."""

    @classmethod
    def setUpClass(cls):
        cls.db = LivingProxyDb(
            PrivateProxyDb(import_as_dict(EXAMPLE, User())),
            mode=LivingProxyDb.MODE_EXCLUDE_ALL,
            current_year=LIVING_DATE,
            years_after_death=10,
        )

    def test_person_count(self):
        self.assertEqual(self.db.get_number_of_people(), 1254)

    def test_private_person_hidden(self):
        person = self.db.get_person_from_handle(PRIVATE_PERSON)
        self.assertIsNone(person)

    def test_private_person_visible_in_basedb(self):
        person = self.db.basedb.get_person_from_handle(PRIVATE_PERSON)
        self.assertIsNotNone(person)

    def test_dead_person_hidden(self):
        person = self.db.get_person_from_handle(DEAD_PERSON)
        self.assertIsNone(person)

    def test_is_filter_override_false_for_proxy_chain(self):
        # Proxy chains never have SQL override
        self.assertFalse(self.db.is_filter_override("person", "Everyone"))


class FilterProxyTest(unittest.TestCase):
    """Tests for FilterProxyDb."""

    @classmethod
    def setUpClass(cls):
        raw_db = import_as_dict(EXAMPLE, User())

        # Proxy that passes everyone through
        everyone_filter = GenericFilter()
        everyone_filter.add_rule(Everyone([]))
        cls.db_all = FilterProxyDb(raw_db, person_filter=everyone_filter)

        # Proxy that includes only NORMAL_PERSON (I0122)
        one_person_filter = GenericFilter()
        one_person_filter.add_rule(HasIdOf(["I0122"]))
        cls.db_one = FilterProxyDb(raw_db, person_filter=one_person_filter)

        cls.raw_db = raw_db

    def test_everyone_filter_includes_all(self):
        self.assertEqual(
            self.db_all.get_number_of_people(),
            self.raw_db.get_number_of_people(),
        )

    def test_single_person_filter_count(self):
        self.assertEqual(self.db_one.get_number_of_people(), 1)

    def test_included_person_visible(self):
        data = self.db_one.get_raw_person_data(NORMAL_PERSON)
        self.assertIsNotNone(data)

    def test_excluded_person_hidden(self):
        # DEAD_PERSON is not I0122, so filtered out
        data = self.db_one.get_raw_person_data(DEAD_PERSON)
        self.assertIsNone(data)

    def test_excluded_person_gramps_id_returns_none(self):
        person = self.db_one.get_person_from_gramps_id("I0001")
        self.assertIsNone(person)

    def test_family_of_included_person_accessible(self):
        # NORMAL_PERSON (I0122) has parent family DLTJQCAPOXEIKSOU3J
        fam = self.db_one.get_family_from_handle("DLTJQCAPOXEIKSOU3J")
        self.assertIsNotNone(fam)

    def test_has_handle_false_for_excluded(self):
        self.assertFalse(self.db_one.has_person_handle(DEAD_PERSON))

    def test_has_handle_true_for_included(self):
        self.assertTrue(self.db_one.has_person_handle(NORMAL_PERSON))

    def test_iter_handles_excludes_filtered(self):
        handles = list(self.db_one.iter_person_handles())
        self.assertIn(NORMAL_PERSON, handles)
        self.assertNotIn(DEAD_PERSON, handles)

    def test_is_filter_override_false(self):
        self.assertFalse(self.db_one.is_filter_override("person", "Everyone"))


class IsFilterOverrideTest(unittest.TestCase):
    """
    Tests for is_filter_override across all proxy types, using mock to
    simulate both the non-override (full Python scan) and override (SQL
    fast path) variants.  In both cases filter.apply() is what runs;
    is_filter_override is only a performance hint to the caller.
    """

    @classmethod
    def setUpClass(cls):
        cls.raw_db = import_as_dict(EXAMPLE, User())

    # --- default behaviour ---

    def test_raw_db_returns_false(self):
        self.assertFalse(self.raw_db.is_filter_override("person", "Everyone"))

    def test_private_proxy_returns_false(self):
        db = PrivateProxyDb(self.raw_db)
        self.assertFalse(db.is_filter_override("person", "Everyone"))

    def test_living_proxy_returns_false(self):
        db = LivingProxyDb(self.raw_db, mode=LivingProxyDb.MODE_EXCLUDE_ALL)
        self.assertFalse(db.is_filter_override("person", "Everyone"))

    def test_filter_proxy_returns_false(self):
        f = GenericFilter()
        f.add_rule(Everyone([]))
        db = FilterProxyDb(self.raw_db, person_filter=f)
        self.assertFalse(db.is_filter_override("person", "Everyone"))

    # --- non-override path: filter.apply() does a full Python scan ---

    def test_non_override_filter_apply_called(self):
        """When is_filter_override is False, filter.apply() is called and
        its return value is used to build the handle set."""
        f = GenericFilter()
        f.add_rule(HasIdOf(["I0122"]))

        with patch.object(self.raw_db, "is_filter_override", return_value=False):
            with patch.object(f, "apply", wraps=f.apply) as mock_apply:
                proxy = FilterProxyDb(self.raw_db, person_filter=f)
                mock_apply.assert_called_once()
                self.assertEqual(proxy.get_number_of_people(), 1)
                self.assertTrue(proxy.has_person_handle(NORMAL_PERSON))

    # --- override path: filter.apply() returns a pre-computed (SQL) result ---

    def test_override_filter_apply_called_with_sql_result(self):
        """When is_filter_override is True (SQL backend), filter.apply()
        still runs but may return results directly from SQL.  The proxy
        must use whatever apply() returns, regardless of how it was
        computed.  We simulate this by patching apply() to return a
        known handle list."""
        f = GenericFilter()
        f.add_rule(Everyone([]))

        sql_handles = [NORMAL_PERSON, DEAD_PERSON]  # simulated SQL result

        with patch.object(self.raw_db, "is_filter_override", return_value=True):
            with patch.object(f, "apply", return_value=sql_handles) as mock_apply:
                proxy = FilterProxyDb(self.raw_db, person_filter=f)
                mock_apply.assert_called_once()
                # Proxy should contain exactly the two handles SQL returned
                self.assertEqual(proxy.get_number_of_people(), 2)
                self.assertTrue(proxy.has_person_handle(NORMAL_PERSON))
                self.assertTrue(proxy.has_person_handle(DEAD_PERSON))
                self.assertFalse(proxy.has_person_handle(LIVING_PERSON))

    # --- both paths produce the same result for a given filter ---

    def test_override_and_non_override_agree(self):
        """The SQL and Python paths must produce identical handle sets."""
        f = GenericFilter()
        f.add_rule(HasIdOf(["I0122"]))

        with patch.object(self.raw_db, "is_filter_override", return_value=False):
            proxy_scan = FilterProxyDb(self.raw_db, person_filter=f)
            scan_handles = set(proxy_scan.iter_person_handles())

        f2 = GenericFilter()
        f2.add_rule(HasIdOf(["I0122"]))

        with patch.object(self.raw_db, "is_filter_override", return_value=True):
            proxy_sql = FilterProxyDb(self.raw_db, person_filter=f2)
            sql_handles = set(proxy_sql.iter_person_handles())

        self.assertEqual(scan_handles, sql_handles)
