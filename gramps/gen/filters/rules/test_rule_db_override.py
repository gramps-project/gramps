# -*- coding: utf-8 -*-
"""
Tests for the DB-override dispatch on Rule.prepare and Rule.apply_to_one.

Both methods are wrapped at class-definition time via __init_subclass__ so
that calling them directly routes through the registry.  The wrapper is
injected at the concrete class level, including when the method is inherited
from an abstract base (e.g. HasTag.apply_to_one from HasTagBase), so
inheritance depth is not a concern.
"""

import unittest

from gramps.gen.filters.rules._rule import Rule, RuleOverride


def _key(cls):
    parts = cls.__module__.split(".")
    try:
        return (parts[parts.index("rules") + 1], cls.__name__)
    except (ValueError, IndexError):
        return (None, cls.__name__)


class _MockDB:
    def __init__(self):
        self._override_registry = {}

    def is_proxy(self):
        return False

    def register_override(self, namespace, key, override_class):
        self._override_registry.setdefault(namespace, {})[key] = override_class


class _FakeRule(Rule):
    """Minimal concrete rule with both methods defined."""

    labels = []

    def apply_to_one(self, db, obj):
        return False

    def prepare(self, db, user):
        db._prepare_called_by_rule = True


class TestApplyToOneDbOverride(unittest.TestCase):
    def test_override_is_used_when_present(self):
        """DB method replaces apply_to_one when register_override was called."""
        rule = _FakeRule([])
        key = _key(type(rule))

        class _Override(RuleOverride):
            def apply_to_one(self, original, db, obj):
                return True

        db = _MockDB()
        db.register_override("rule", key, _Override)

        result = rule.apply_to_one(db, None)
        self.assertTrue(result)

    def test_original_callable_from_override(self):
        """Override can call the original apply_to_one via the passed original."""
        rule = _FakeRule([])
        key = _key(type(rule))

        class _Override(RuleOverride):
            def apply_to_one(self, original, db, obj):
                return original(self.rule, db, obj)

        db = _MockDB()
        db.register_override("rule", key, _Override)

        # _FakeRule.apply_to_one returns False; the override delegates to it
        result = rule.apply_to_one(db, None)
        self.assertFalse(result)

    def test_fallback_when_no_override(self):
        """Original apply_to_one is used when DB has no override."""
        db = _MockDB()  # empty registry
        rule = _FakeRule([])
        result = rule.apply_to_one(db, None)
        self.assertFalse(result)

    def test_inherited_apply_to_one_overridden(self):
        """Override fires even when the concrete class inherits apply_to_one
        from an abstract base (the HasTag / HasTagBase pattern)."""

        class _AbstractBase(Rule):
            __module__ = "gramps.gen.filters.rules._abstractbase"
            labels = []

            def apply_to_one(self, db, obj):
                return False

        class _ConcreteRule(_AbstractBase):
            __module__ = "gramps.gen.filters.rules.person._concreterule"
            labels = []
            # no apply_to_one defined — inherited from _AbstractBase

        rule = _ConcreteRule([])
        key = _key(type(rule))

        class _Override(RuleOverride):
            def apply_to_one(self, original, db, obj):
                return True

        db = _MockDB()
        db.register_override("rule", key, _Override)

        result = rule.apply_to_one(db, None)
        self.assertTrue(result)


class TestPrepareDbOverride(unittest.TestCase):
    def test_override_is_used_when_present(self):
        """DB prepare method replaces prepare when registered."""
        rule = _FakeRule([])
        key = _key(type(rule))

        called = []

        class _Override(RuleOverride):
            def prepare(self, original, db, user):
                called.append(True)

        db = _MockDB()
        db.register_override("rule", key, _Override)

        rule.prepare(db, None)
        self.assertEqual(called, [True])

    def test_fallback_when_no_override(self):
        """Original prepare is called when DB has no override."""
        rule = _FakeRule([])
        real_db = type(
            "DB", (), {"_override_registry": {}, "is_proxy": lambda self: False}
        )()
        rule.prepare(real_db, None)
        self.assertTrue(getattr(real_db, "_prepare_called_by_rule", False))

    def test_inherited_prepare_overridden(self):
        """Override fires even when the concrete class inherits prepare."""

        class _AbstractBase(Rule):
            __module__ = "gramps.gen.filters.rules._abstractbase"
            labels = []

            def prepare(self, db, user):
                db._base_prepare_called = True

        class _ConcreteRule(_AbstractBase):
            __module__ = "gramps.gen.filters.rules.person._concreterule"
            labels = []
            # no prepare defined — inherited from _AbstractBase

        rule = _ConcreteRule([])
        key = _key(type(rule))

        called = []

        class _Override(RuleOverride):
            def prepare(self, original, db, user):
                called.append(True)

        db = _MockDB()
        db.register_override("rule", key, _Override)

        rule.prepare(db, None)
        self.assertEqual(called, [True])
        self.assertFalse(getattr(db, "_base_prepare_called", False))

    def test_override_instance_shared_between_prepare_and_apply(self):
        """State set in prepare is available during apply_to_one."""
        rule = _FakeRule([])
        key = _key(type(rule))

        class _Override(RuleOverride):
            def prepare(self, original, db, user):
                self.selected = {42}

            def apply_to_one(self, original, db, obj):
                return obj in self.selected

        db = _MockDB()
        db.register_override("rule", key, _Override)

        rule.prepare(db, None)
        self.assertTrue(rule.apply_to_one(db, 42))
        self.assertFalse(rule.apply_to_one(db, 99))


class TestProxyBypassesOverride(unittest.TestCase):
    """Overrides must be skipped when the database is a proxy."""

    def test_proxy_db_uses_original_apply_to_one(self):
        """apply_to_one override is not called when db.is_proxy() is True."""
        rule = _FakeRule([])
        key = _key(type(rule))

        class _ProxyDB(_MockDB):
            def is_proxy(self):
                return True

        class _Override(RuleOverride):
            def apply_to_one(self, original, db, obj):
                return "override_result"

        db = _ProxyDB()
        db.register_override("rule", key, _Override)

        # _FakeRule.apply_to_one returns False; override must not be called
        result = rule.apply_to_one(db, None)
        self.assertFalse(result)

    def test_proxy_db_uses_original_prepare(self):
        """prepare override is not called when db.is_proxy() is True."""
        rule = _FakeRule([])
        key = _key(type(rule))

        called = []

        class _ProxyDB(_MockDB):
            def is_proxy(self):
                return True

        class _Override(RuleOverride):
            def prepare(self, original, db, user):
                called.append("override")

        db = _ProxyDB()
        db.register_override("rule", key, _Override)

        rule.prepare(db, None)
        self.assertEqual(called, [])
        self.assertTrue(getattr(db, "_prepare_called_by_rule", False))


class TestNoDoubleDispatch(unittest.TestCase):
    """Override fires exactly once even when super().apply_to_one() is called."""

    def test_override_fires_once_with_super_chain(self):
        call_log = []

        class _AbstractBase(Rule):
            __module__ = "gramps.gen.filters.rules._abstractbase"
            labels = []

            def apply_to_one(self, db, obj):
                call_log.append("abstract")
                return False

        class _ConcreteRule(_AbstractBase):
            __module__ = "gramps.gen.filters.rules.person._concreterule"
            labels = []

            def apply_to_one(self, db, obj):
                call_log.append("concrete")
                return super().apply_to_one(db, obj)

        rule = _ConcreteRule([])
        key = _key(type(rule))

        class _Override(RuleOverride):
            def apply_to_one(self, original, db, obj):
                call_log.append("override")
                return original(self.rule, db, obj)

        db = _MockDB()
        db.register_override("rule", key, _Override)

        result = rule.apply_to_one(db, None)

        # override fires once → calls concrete (orig) → concrete calls abstract via super
        self.assertEqual(call_log, ["override", "concrete", "abstract"])
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
