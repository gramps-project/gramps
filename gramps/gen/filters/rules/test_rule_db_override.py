# -*- coding: utf-8 -*-
"""
Tests for the DB-override decorator mechanism on Rule.prepare / apply_to_one.
"""

import unittest

from gramps.gen.filters.rules._rule import Rule, _rule_key


class _MockDB:
    def __init__(self):
        self._override_registry = {}

    def register_override(self, namespace, key, **handlers):
        self._override_registry.setdefault(namespace, {})[key] = handlers


class _FakeRule(Rule):
    """Minimal subclass with both methods overridden."""

    labels = []

    def apply_to_one(self, db, obj):
        return False

    def prepare(self, db, user):
        db._prepare_called_by_rule = True


class TestApplyToOneDbOverride(unittest.TestCase):
    def test_override_is_used_when_present(self):
        """DB method replaces apply_to_one when register_override was called."""
        rule = _FakeRule([])
        key = _rule_key(type(rule))

        db = _MockDB()
        db.register_override("rule", key, apply=lambda self, orig, db, obj: True)

        result = rule.apply_to_one(db, None)
        self.assertTrue(result)

    def test_original_callable_from_override(self):
        """Override can call the original apply_to_one via the passed original."""
        rule = _FakeRule([])
        key = _rule_key(type(rule))

        db = _MockDB()
        db.register_override(
            "rule",
            key,
            apply=lambda self, orig, db, obj: orig(self, db, obj),
        )

        # _FakeRule.apply_to_one returns False; the override delegates to it
        result = rule.apply_to_one(db, None)
        self.assertFalse(result)

    def test_fallback_when_no_override(self):
        """Original apply_to_one is used when DB has no override."""
        db = _MockDB()  # empty registry
        rule = _FakeRule([])
        result = rule.apply_to_one(db, None)
        self.assertFalse(result)


class TestPrepareDbOverride(unittest.TestCase):
    def test_override_is_used_when_present(self):
        """DB prepare method replaces prepare when registered."""
        rule = _FakeRule([])
        key = _rule_key(type(rule))

        called = []
        db = _MockDB()
        db.register_override(
            "rule",
            key,
            apply=lambda s, orig, d, o: None,
            prepare=lambda s, orig, d, u: called.append(True),
        )

        rule.prepare(db, None)
        self.assertEqual(called, [True])

    def test_fallback_when_no_override(self):
        """Original prepare is called when DB has no override."""
        rule = _FakeRule([])
        real_db = type("DB", (), {"_override_registry": {}})()
        rule.prepare(real_db, None)
        self.assertTrue(getattr(real_db, "_prepare_called_by_rule", False))


class TestBaseClassOverride(unittest.TestCase):
    """Base Rule methods (not overridden in subclass) are also wrapped."""

    def test_base_apply_to_one_override(self):
        """DB override works even when subclass does not define apply_to_one."""

        class _NoOverrideRule(Rule):
            labels = []

        rule = _NoOverrideRule([])
        key = _rule_key(type(rule))

        db = _MockDB()
        db.register_override(
            "rule", key, apply=lambda rule_self, orig, d, obj: "db_result"
        )

        result = rule.apply_to_one(db, None)
        self.assertEqual(result, "db_result")


if __name__ == "__main__":
    unittest.main()
