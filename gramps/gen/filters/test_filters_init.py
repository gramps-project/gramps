# -*- coding: utf-8 -*-
"""
Tests for gramps.gen.filters top-level helpers:
  get_filter_by_name, get_rule_names, _get_rule_names_recursively
"""

import unittest

import gramps.gen.filters as filters_module
from gramps.gen.filters import (
    get_filter_by_name,
    get_rule_names,
    _get_rule_names_recursively,
    set_custom_filters,
)
from gramps.gen.filters.rules._matchesfilterbase import MatchesFilterBase
from gramps.gen.filters.rules import Rule

# ---------------------------------------------------------------------------
# Minimal mock objects
# ---------------------------------------------------------------------------


class _MockRule:
    """Pretends to be a Rule with a known class name."""

    def __init__(self, class_name):
        self.__class__ = type(class_name, (Rule,), {"labels": [], "name": class_name})
        self.name = class_name

    @property
    def _class_name(self):
        return type(self).__name__


class _SimpleRule:
    """Simple mock rule — not a MatchesFilterBase."""

    def __init__(self, class_name):
        self._class_name = class_name
        self.__class__ = type(class_name, (), {})

    @property
    def name(self):
        return self._class_name


class _MatchesRule(MatchesFilterBase):
    """MatchesFilterBase subclass that returns a fixed nested filter."""

    labels = []
    namespace = "person"

    def __init__(self, nested_filter):
        self._nested = nested_filter
        self.list = ["nested"]

    def find_filter(self):
        return self._nested


class _MockFilter:
    """Minimal filter object with a name and a list of rules."""

    def __init__(self, name, rules=None):
        self.name = name
        self._rules = rules or []

    def get_rules(self):
        return self._rules


class _MockCustomFilters:
    """Replaces gramps.gen.filters.CustomFilters in tests."""

    def __init__(self, namespace_map):
        # namespace_map: {namespace: {filter_name: filter_obj}}
        self._map = namespace_map

    def get_filters_dict(self, namespace="generic"):
        return self._map.get(namespace, {})


# ---------------------------------------------------------------------------
# Tests for get_filter_by_name
# ---------------------------------------------------------------------------


class TestGetFilterByName(unittest.TestCase):
    def setUp(self):
        self._orig = filters_module.CustomFilters
        filt = _MockFilter("MyFilter")
        set_custom_filters(_MockCustomFilters({"person": {"MyFilter": filt}}))
        self._filt = filt

    def tearDown(self):
        set_custom_filters(self._orig)

    def test_returns_existing_filter(self):
        result = get_filter_by_name("person", "MyFilter")
        self.assertIs(result, self._filt)

    def test_returns_none_for_missing_filter(self):
        result = get_filter_by_name("person", "NoSuchFilter")
        self.assertIsNone(result)

    def test_returns_none_for_missing_namespace(self):
        result = get_filter_by_name("event", "MyFilter")
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# Tests for _get_rule_names_recursively
# ---------------------------------------------------------------------------


class TestGetRuleNamesRecursively(unittest.TestCase):
    def _simple_rule(self, class_name):
        """Return a plain non-MatchesFilterBase rule whose class name is class_name."""
        cls = type(class_name, (), {})
        obj = object.__new__(cls)
        return obj

    def test_empty_filter_returns_empty_list(self):
        filt = _MockFilter("F", rules=[])
        self.assertEqual(_get_rule_names_recursively(filt), [])

    def test_single_rule_returns_class_name(self):
        rule = self._simple_rule("HasTag")
        filt = _MockFilter("F", rules=[rule])
        self.assertEqual(_get_rule_names_recursively(filt), ["HasTag"])

    def test_multiple_rules_returns_all_class_names(self):
        rules = [self._simple_rule("HasTag"), self._simple_rule("IsMale")]
        filt = _MockFilter("F", rules=rules)
        self.assertEqual(_get_rule_names_recursively(filt), ["HasTag", "IsMale"])

    def test_nested_filter_rules_included(self):
        inner_rule = self._simple_rule("IsFemale")
        inner_filt = _MockFilter("Inner", rules=[inner_rule])

        outer_rule = _MatchesRule(inner_filt)
        outer_filt = _MockFilter("Outer", rules=[outer_rule])

        names = _get_rule_names_recursively(outer_filt)
        self.assertIn("_MatchesRule", names)
        self.assertIn("IsFemale", names)

    def test_cycle_is_handled(self):
        """A filter that references itself (directly or indirectly) does not loop."""
        # Build a cyclic reference: outer → MatchesRule → outer
        outer_filt = _MockFilter("Cyclic", rules=[])
        cycle_rule = _MatchesRule(outer_filt)
        outer_filt._rules = [cycle_rule]

        # Should terminate without RecursionError
        names = _get_rule_names_recursively(outer_filt)
        self.assertIn("_MatchesRule", names)

    def test_seen_set_prevents_duplicate_rules(self):
        """Second visit to the same filter name is skipped."""
        shared_rule = self._simple_rule("IsBookmarked")
        shared_filt = _MockFilter("Shared", rules=[shared_rule])

        rule1 = _MatchesRule(shared_filt)
        rule2 = _MatchesRule(shared_filt)
        outer_filt = _MockFilter("Outer", rules=[rule1, rule2])

        names = _get_rule_names_recursively(outer_filt)
        self.assertEqual(names.count("IsBookmarked"), 1)


# ---------------------------------------------------------------------------
# Tests for get_rule_names
# ---------------------------------------------------------------------------


class TestGetRuleNames(unittest.TestCase):
    def setUp(self):
        self._orig = filters_module.CustomFilters

    def tearDown(self):
        set_custom_filters(self._orig)

    def _plain_rule(self, class_name):
        cls = type(class_name, (), {})
        return object.__new__(cls)

    def test_returns_class_names_from_filter(self):
        rule = self._plain_rule("HasTag")
        filt = _MockFilter("MyFilter", rules=[rule])
        set_custom_filters(_MockCustomFilters({"person": {"MyFilter": filt}}))
        self.assertEqual(get_rule_names("person", "MyFilter"), ["HasTag"])

    def test_missing_filter_raises_or_returns_empty(self):
        set_custom_filters(_MockCustomFilters({"person": {}}))
        # get_filter_by_name returns None; _get_rule_names_recursively will
        # raise AttributeError on None.filt.name — this documents current behaviour.
        with self.assertRaises(AttributeError):
            get_rule_names("person", "NoSuchFilter")


if __name__ == "__main__":
    unittest.main()
