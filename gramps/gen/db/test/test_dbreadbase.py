# -*- coding: utf-8 -*-
"""
Tests for DbReadBase.is_proxy, register_rule_override, and is_filter_override.
"""

import unittest
from unittest.mock import MagicMock

import gramps.gen.filters as filters_module
from gramps.gen.filters import set_custom_filters
from gramps.gen.db.base import DbReadBase


class _MinimalDb(DbReadBase):
    """Minimal concrete subclass — only implements __init__."""

    def __init__(self):
        super().__init__()


class _MockCustomFilters:
    def __init__(self, namespace_map):
        self._map = namespace_map

    def get_filters_dict(self, namespace="generic"):
        return self._map.get(namespace, {})


class _MockFilter:
    def __init__(self, name, rules=None):
        self.name = name
        self._rules = rules or []

    def get_rules(self):
        return self._rules


class TestIsProxy(unittest.TestCase):
    def test_plain_db_is_not_proxy(self):
        """A freshly created database is not a proxy of itself."""
        db = _MinimalDb()
        self.assertFalse(db.is_proxy())

    def test_proxy_db_is_proxy(self):
        """When basedb points to a different object, is_proxy returns True."""
        base = _MinimalDb()
        proxy = _MinimalDb()
        proxy.basedb = base
        self.assertTrue(proxy.is_proxy())

    def test_basedb_none_is_not_proxy(self):
        """If basedb is explicitly None, is_proxy returns False."""
        db = _MinimalDb()
        db.basedb = None
        self.assertFalse(db.is_proxy())


class _SimpleOverride:
    def __init__(self, rule):
        self.rule = rule

    def apply_to_one(self, original, db, obj):
        return True


class TestRegisterRuleOverride(unittest.TestCase):
    def test_class_stored_in_registry(self):
        """register_rule_override stores the class under the 'rule' namespace."""
        db = _MinimalDb()
        db.register_rule_override(("person", "MyRule"), _SimpleOverride)
        self.assertIs(
            db._override_registry["rule"][("person", "MyRule")], _SimpleOverride
        )

    def test_different_keys_stored_independently(self):
        """Two keys in the 'rule' namespace do not interfere."""

        class _OverrideA:
            def __init__(self, rule):
                pass

            def apply_to_one(self, original, db, obj):
                return True

        class _OverrideB:
            def __init__(self, rule):
                pass

            def apply_to_one(self, original, db, obj):
                return False

        db = _MinimalDb()
        db.register_rule_override(("person", "RuleA"), _OverrideA)
        db.register_rule_override(("person", "RuleB"), _OverrideB)
        self.assertIs(db._override_registry["rule"][("person", "RuleA")], _OverrideA)
        self.assertIs(db._override_registry["rule"][("person", "RuleB")], _OverrideB)

    def test_registration_overwrites_existing_entry(self):
        """Re-registering the same key replaces the previous class."""

        class _OldOverride:
            def __init__(self, rule):
                pass

            def apply_to_one(self, original, db, obj):
                return False

        class _NewOverride:
            def __init__(self, rule):
                pass

            def apply_to_one(self, original, db, obj):
                return True

        db = _MinimalDb()
        db.register_rule_override(("person", "MyRule"), _OldOverride)
        db.register_rule_override(("person", "MyRule"), _NewOverride)
        self.assertIs(
            db._override_registry["rule"][("person", "MyRule")], _NewOverride
        )

    def test_empty_registry_on_new_db(self):
        """A fresh database has an empty override registry."""
        db = _MinimalDb()
        self.assertEqual(db._override_registry, {})


class TestIsFilterOverride(unittest.TestCase):
    def setUp(self):
        self._orig = filters_module.CustomFilters

    def tearDown(self):
        set_custom_filters(self._orig)

    def _rule_obj(self, class_name):
        cls = type(class_name, (), {})
        return object.__new__(cls)

    def test_returns_true_when_override_registered(self):
        rule = self._rule_obj("HasTag")
        filt = _MockFilter("MyFilter", rules=[rule])
        set_custom_filters(_MockCustomFilters({"person": {"MyFilter": filt}}))

        db = _MinimalDb()
        db.register_rule_override(("person", "HasTag"), _SimpleOverride)

        self.assertTrue(db.is_filter_override("person", "MyFilter"))

    def test_returns_none_when_no_override_registered(self):
        rule = self._rule_obj("HasTag")
        filt = _MockFilter("MyFilter", rules=[rule])
        set_custom_filters(_MockCustomFilters({"person": {"MyFilter": filt}}))

        db = _MinimalDb()
        # no override registered
        result = db.is_filter_override("person", "MyFilter")
        self.assertIsNone(result)

    def test_only_matching_table_triggers_true(self):
        rule = self._rule_obj("HasTag")
        filt = _MockFilter("MyFilter", rules=[rule])
        set_custom_filters(_MockCustomFilters({"person": {"MyFilter": filt}}))

        db = _MinimalDb()
        # override registered under "event", not "person"
        db.register_rule_override(("event", "HasTag"), _SimpleOverride)

        result = db.is_filter_override("person", "MyFilter")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
