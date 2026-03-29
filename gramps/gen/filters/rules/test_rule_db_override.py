# -*- coding: utf-8 -*-
"""
Tests for the DB-override decorator mechanism on Rule.prepare / apply_to_one.
"""

import unittest

from gramps.gen.filters.rules._rule import Rule, _rule_key


class _MockDB:
    def __init__(self):
        self._override_registry = {}

    def is_proxy(self):
        return False

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
        db.register_override("rule", key, apply_to_one=lambda self, orig, db, obj: True)

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
            apply_to_one=lambda s, orig, d, o: None,
            prepare=lambda s, orig, d, u: called.append(True),
        )

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
            "rule", key, apply_to_one=lambda rule_self, orig, d, obj: "db_result"
        )

        result = rule.apply_to_one(db, None)
        self.assertEqual(result, "db_result")


class TestProxyBypassesOverride(unittest.TestCase):
    """Overrides must be skipped when the database is a proxy."""

    def test_proxy_db_uses_original_apply_to_one(self):
        """apply_to_one override is not called when db.is_proxy() is True."""
        rule = _FakeRule([])
        key = _rule_key(type(rule))

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
        key = _rule_key(type(rule))

        called = []

        class _ProxyDB(_MockDB):
            def is_proxy(self):
                return True

        db = _ProxyDB()
        db.register_override(
            "rule", key, prepare=lambda s, orig, d, u: called.append("override")
        )

        rule.prepare(db, None)
        self.assertEqual(called, [])
        self.assertTrue(getattr(db, "_prepare_called_by_rule", False))


class TestSuperCallNoDoubleDispatch(unittest.TestCase):
    """
    Override must fire exactly once regardless of super() calls in the chain.

    Two scenarios are covered:

    1. Concrete → abstract base (starts with "_"): __init_subclass__ leaves the
       abstract base unwrapped, so the override fires once and super() falls
       through to the raw abstract implementation.

    2. Concrete-B → concrete-A (both in category subdirectories and both
       wrapped): without a re-entry guard the override for B would fire a
       second time inside A's wrapper.  The guard on the rule instance prevents
       this.
    """

    def test_abstract_base_not_wrapped_no_double_dispatch(self):
        """Override fires once; super() into an unwrapped abstract base is safe."""
        call_log = []

        # Set __module__ *in the class body* so __init_subclass__ sees the
        # correct path and skips wrapping the abstract base.
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
        key = _rule_key(type(rule))

        db = _MockDB()
        db.register_override(
            "rule",
            key,
            apply_to_one=lambda s, orig, d, obj: (
                call_log.append("override") or orig(s, d, obj)
            ),
        )

        result = rule.apply_to_one(db, None)

        # override → concrete (orig) → abstract (super, unwrapped)
        self.assertEqual(call_log, ["override", "concrete", "abstract"])
        self.assertFalse(result)

    def test_concrete_intermediate_base_no_double_dispatch(self):
        """Override fires once even when super() goes into a wrapped concrete base.

        This mirrors the real-world pattern where a family rule (e.g.
        MotherHasNameOf) inherits from a person rule (e.g. HasNameOf) and
        delegates via super().apply_to_one().  Both live in category
        subdirectories so both are wrapped.  Without a re-entry guard the
        override would fire a second time inside the parent's wrapper.
        """
        call_log = []

        class _PersonRule(Rule):
            __module__ = "gramps.gen.filters.rules.person._personrule"
            labels = []

            def apply_to_one(self, db, obj):
                call_log.append("person_rule")
                return False

        class _FamilyRule(_PersonRule):
            __module__ = "gramps.gen.filters.rules.family._familyrule"
            labels = []

            def apply_to_one(self, db, obj):
                call_log.append("family_rule")
                return super().apply_to_one(db, obj)

        rule = _FamilyRule([])
        key = _rule_key(type(rule))  # ('family', '_FamilyRule')

        db = _MockDB()
        db.register_override(
            "rule",
            key,
            apply_to_one=lambda s, orig, d, obj: (
                call_log.append("override") or orig(s, d, obj)
            ),
        )

        result = rule.apply_to_one(db, None)

        # override → family_rule (orig) → person_rule (super, wrapped but
        # re-entry guard prevents a second override dispatch)
        self.assertEqual(call_log, ["override", "family_rule", "person_rule"])
        self.assertEqual(call_log.count("override"), 1)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
