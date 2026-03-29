# -*- coding: utf-8 -*-
"""
Tests for the DB-override dispatch on Rule.apply_to_one and
Rule._checked_prepare / requestprepare.

apply_to_one is wrapped at class-definition time via __init_subclass__ so that
rule.apply_to_one(db, obj) — called directly by the filter — routes through
the registry.  The wrapper is injected at the concrete class level, including
when apply_to_one is inherited from an abstract base (e.g. HasTag from
HasTagBase), so inheritance depth is not a concern.

prepare is dispatched through _checked_prepare called from requestprepare;
_checked_prepare is never overridden by subclasses so it works for all depths.
"""

import unittest

from gramps.gen.filters.rules._rule import Rule


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

    def register_override(self, namespace, key, **handlers):
        self._override_registry.setdefault(namespace, {})[key] = handlers


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

        db = _MockDB()
        db.register_override("rule", key, apply_to_one=lambda self, orig, db, obj: True)

        result = rule.apply_to_one(db, None)
        self.assertTrue(result)

    def test_original_callable_from_override(self):
        """Override can call the original apply_to_one via the passed original."""
        rule = _FakeRule([])
        key = _key(type(rule))

        db = _MockDB()
        db.register_override(
            "rule",
            key,
            apply_to_one=lambda self, orig, db, obj: orig(self, db, obj),
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

        db = _MockDB()
        db.register_override("rule", key, apply_to_one=lambda s, orig, d, obj: True)

        result = rule.apply_to_one(db, None)
        self.assertTrue(result)


class TestPrepareDbOverride(unittest.TestCase):
    def test_override_is_used_when_present(self):
        """DB prepare method replaces prepare when registered."""
        rule = _FakeRule([])
        key = _key(type(rule))

        called = []
        db = _MockDB()
        db.register_override(
            "rule",
            key,
            prepare=lambda s, orig, d, u: called.append(True),
        )

        rule._checked_prepare(db, None)
        self.assertEqual(called, [True])

    def test_fallback_when_no_override(self):
        """Original prepare is called when DB has no override."""
        rule = _FakeRule([])
        real_db = type(
            "DB", (), {"_override_registry": {}, "is_proxy": lambda self: False}
        )()
        rule._checked_prepare(real_db, None)
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
        db = _MockDB()
        db.register_override(
            "rule", key, prepare=lambda s, orig, d, u: called.append(True)
        )

        rule._checked_prepare(db, None)
        self.assertEqual(called, [True])
        self.assertFalse(getattr(db, "_base_prepare_called", False))


class TestProxyBypassesOverride(unittest.TestCase):
    """Overrides must be skipped when the database is a proxy."""

    def test_proxy_db_uses_original_apply_to_one(self):
        """apply_to_one override is not called when db.is_proxy() is True."""
        rule = _FakeRule([])
        key = _key(type(rule))

        class _ProxyDB(_MockDB):
            def is_proxy(self):
                return True

        db = _ProxyDB()
        db.register_override(
            "rule", key, apply_to_one=lambda s, orig, d, obj: "override_result"
        )

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

        db = _ProxyDB()
        db.register_override(
            "rule", key, prepare=lambda s, orig, d, u: called.append("override")
        )

        rule._checked_prepare(db, None)
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

        db = _MockDB()
        db.register_override(
            "rule",
            key,
            apply_to_one=lambda s, orig, d, obj: (
                call_log.append("override") or orig(s, d, obj)
            ),
        )

        result = rule.apply_to_one(db, None)

        # override fires once → calls concrete (orig) → concrete calls abstract via super
        self.assertEqual(call_log, ["override", "concrete", "abstract"])
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
