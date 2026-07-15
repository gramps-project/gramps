#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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

"""Tests for scanning and overriding <accelerator> tags in .glade files."""

# python3 -m unittest gramps.gui.test.glade_test -v

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

os.environ.setdefault("GDK_BACKEND", "-")
os.environ.setdefault("LANG", "en_US.utf-8")

import gi

gi.require_version("Gtk", "3.0")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gramps.gen.const import GLADE_DIR
from gramps.gui.glade import (
    apply_glade_accel_overrides,
    iter_glade_accelerators,
    _accel_to_glade_key_modifiers,
    _glade_modifiers_to_prefix,
)

SAMPLE_XML = """<object id="mybutton" class="GtkButton">
  <property name="visible">True</property>
  <child internal-child="accessible">
    <object class="AtkObject">
      <property name="AtkObject::accessible-name" translatable="yes">Add</property>
    </object>
  </child>
  <accelerator key="a" signal="activate" modifiers="GDK_CONTROL_MASK"/>
</object>
"""

SAMPLE_XML_TOOLTIP = """<object id="datebtn" class="GtkButton">
  <property name="tooltip-text" translatable="yes">Invoke date editor</property>
  <child internal-child="accessible">
    <object class="AtkObject">
      <property name="AtkObject::accessible-name" translatable="yes">Date</property>
    </object>
  </child>
  <accelerator key="d" signal="activate" modifiers="GDK_CONTROL_MASK"/>
</object>
"""

SAMPLE_XML_MULTILINE_TOOLTIP = """<object id="multsurnamebtn" class="GtkButton">
  <property name="tooltip-text" translatable="yes">Use Multiple Surnames
Indicate that the surname consists of different parts.</property>
  <accelerator key="a" signal="activate" modifiers="GDK_CONTROL_MASK"/>
</object>
"""

SAMPLE_XML_NO_LABEL = """<object id="mystery" class="GtkButton">
  <accelerator key="w" signal="grab_focus" modifiers="GDK_MOD1_MASK"/>
</object>
"""

SAMPLE_XML_MULTI = """<interface>
  <object id="outer" class="GtkBox">
    <child>
      <object id="inner" class="GtkButton">
        <accelerator key="s" signal="activate" modifiers="GDK_CONTROL_MASK"/>
      </object>
    </child>
  </object>
</interface>
"""


class ModifierConversionTest(unittest.TestCase):
    """Pure string conversions between glade attributes and accel strings
    must not require Gtk/Gdk or a real display."""

    def test_glade_modifiers_to_prefix(self):
        self.assertEqual(_glade_modifiers_to_prefix("GDK_CONTROL_MASK"), "<Primary>")
        self.assertEqual(
            _glade_modifiers_to_prefix("GDK_CONTROL_MASK|GDK_SHIFT_MASK"),
            "<Primary><Shift>",
        )
        self.assertEqual(_glade_modifiers_to_prefix("GDK_MOD1_MASK"), "<Alt>")
        self.assertEqual(_glade_modifiers_to_prefix(""), "")

    def test_accel_to_glade_key_modifiers(self):
        self.assertEqual(
            _accel_to_glade_key_modifiers("<Primary><Shift>a"),
            ("a", "GDK_CONTROL_MASK|GDK_SHIFT_MASK"),
        )
        self.assertEqual(
            _accel_to_glade_key_modifiers("<Alt>w"), ("w", "GDK_MOD1_MASK")
        )
        self.assertEqual(_accel_to_glade_key_modifiers("a"), ("a", ""))
        self.assertEqual(_accel_to_glade_key_modifiers(""), (None, None))

    def test_round_trip_modifiers(self):
        prefix = _glade_modifiers_to_prefix("GDK_CONTROL_MASK|GDK_SHIFT_MASK")
        key, modifiers = _accel_to_glade_key_modifiers(prefix + "a")
        self.assertEqual(key, "a")
        self.assertEqual(
            set(modifiers.split("|")), {"GDK_CONTROL_MASK", "GDK_SHIFT_MASK"}
        )


class IterGladeAcceleratorsTest(unittest.TestCase):
    def test_finds_accelerator_and_accessible_name_label(self):
        results = list(iter_glade_accelerators(SAMPLE_XML))
        self.assertEqual(results, [("mybutton", "<Primary>a", "Add")])

    def test_prefers_tooltip_over_accessible_name(self):
        results = list(iter_glade_accelerators(SAMPLE_XML_TOOLTIP))
        self.assertEqual(results, [("datebtn", "<Primary>d", "Invoke date editor")])

    def test_multiline_tooltip_uses_first_line_only(self):
        results = list(iter_glade_accelerators(SAMPLE_XML_MULTILINE_TOOLTIP))
        self.assertEqual(
            results, [("multsurnamebtn", "<Primary>a", "Use Multiple Surnames")]
        )

    def test_falls_back_to_object_id_when_no_label(self):
        results = list(iter_glade_accelerators(SAMPLE_XML_NO_LABEL))
        self.assertEqual(results, [("mystery", "<Alt>w", "mystery")])

    def test_nested_object_attributed_to_its_own_id(self):
        results = list(iter_glade_accelerators(SAMPLE_XML_MULTI))
        self.assertEqual(results, [("inner", "<Primary>s", "inner")])

    def test_no_accelerators_yields_nothing(self):
        results = list(iter_glade_accelerators('<object id="x"></object>'))
        self.assertEqual(results, [])

    def test_every_real_glade_file_parses_without_error(self):
        """Regression smoke test: every .glade file under GLADE_DIR must
        be scannable, not just the ones known to carry accelerators."""
        filenames = [f for f in os.listdir(GLADE_DIR) if f.endswith(".glade")]
        self.assertGreater(len(filenames), 0)
        for filename in filenames:
            path = os.path.join(GLADE_DIR, filename)
            with open(path, "r", encoding="utf-8") as handle:
                data = handle.read()
            try:
                list(iter_glade_accelerators(data))
            except ET.ParseError as err:
                self.fail(f"{filename} failed to parse: {err}")


class ApplyGladeAccelOverridesTest(unittest.TestCase):
    def setUp(self):
        self._orig_get_default = Gtk.Application.get_default
        self.addCleanup(setattr, Gtk.Application, "get_default", self._orig_get_default)

    def _set_fake_app(self, accel_dict):
        app = MagicMock()
        app.uimanager.accel_dict = accel_dict
        Gtk.Application.get_default = staticmethod(lambda: app)

    def test_no_accelerator_tag_returns_input_unchanged(self):
        xml = '<object id="x"><property name="visible">True</property></object>'
        self._set_fake_app({})
        self.assertIs(apply_glade_accel_overrides(xml, "somefile"), xml)

    def test_no_running_application_returns_input_unchanged(self):
        Gtk.Application.get_default = staticmethod(lambda: None)
        self.assertEqual(
            apply_glade_accel_overrides(SAMPLE_XML, "somefile"), SAMPLE_XML
        )

    def test_no_matching_override_leaves_xml_unchanged(self):
        self._set_fake_app({"glade.somefile.unrelated": "<Primary>z"})
        result = apply_glade_accel_overrides(SAMPLE_XML, "somefile")
        self.assertEqual(
            list(iter_glade_accelerators(result)), [("mybutton", "<Primary>a", "Add")]
        )

    def test_matching_override_rewrites_only_that_element(self):
        self._set_fake_app({"glade.somefile.mybutton": "<Primary><Shift>a"})
        result = apply_glade_accel_overrides(SAMPLE_XML, "somefile")
        self.assertEqual(
            list(iter_glade_accelerators(result)),
            [("mybutton", "<Primary><Shift>a", "Add")],
        )

    def test_override_does_not_touch_unrelated_elements(self):
        two_buttons = f"<interface>{SAMPLE_XML}{SAMPLE_XML_TOOLTIP}</interface>"
        self._set_fake_app({"glade.somefile.mybutton": "<Primary><Shift>a"})
        result = apply_glade_accel_overrides(two_buttons, "somefile")
        results = dict((r[0], r[1]) for r in iter_glade_accelerators(result))
        self.assertEqual(results["mybutton"], "<Primary><Shift>a")
        self.assertEqual(results["datebtn"], "<Primary>d")


if __name__ == "__main__":
    unittest.main()
