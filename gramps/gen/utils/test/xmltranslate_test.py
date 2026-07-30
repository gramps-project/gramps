# -*- coding: utf-8 -*-
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

"""
Unit tests for gramps.gen.utils.xmltranslate.
"""

import unittest
import xml.etree.ElementTree as ET

from .. import xmltranslate


class FakeTranslation:
    def sgettext(self, msgid: str, context: str = "") -> str:
        if context:
            return f"[{context}:{msgid}]"
        return f"[{msgid}]"


class FakeGlocale:
    def __init__(self):
        self.translation = FakeTranslation()


class XmlTranslateTest(unittest.TestCase):
    def setUp(self):
        self._real_glocale = xmltranslate.glocale
        xmltranslate.glocale = FakeGlocale()

    def tearDown(self):
        xmltranslate.glocale = self._real_glocale

    def test_translatable_text_replaced_and_attrs_stripped(self):
        xml = (
            '<interface><property name="label" translatable="yes">'
            "Hello</property></interface>"
        )
        root = ET.fromstring(xml)
        xmltranslate.translate_xml_tree(root)
        elem = root.find("property")
        self.assertEqual(elem.text, "[Hello]")
        self.assertNotIn("translatable", elem.attrib)
        self.assertNotIn("context", elem.attrib)

    def test_context_is_passed_through(self):
        xml = (
            '<interface><attribute name="label" translatable="yes" '
            'context="Given names">_Given:</attribute></interface>'
        )
        root = ET.fromstring(xml)
        xmltranslate.translate_xml_tree(root)
        elem = root.find("attribute")
        self.assertEqual(elem.text, "[Given names:_Given:]")
        self.assertNotIn("translatable", elem.attrib)
        self.assertNotIn("context", elem.attrib)

    def test_comments_attribute_is_stripped(self):
        xml = (
            '<interface><property translatable="yes" comments="note">'
            "Hi</property></interface>"
        )
        root = ET.fromstring(xml)
        xmltranslate.translate_xml_tree(root)
        elem = root.find("property")
        self.assertNotIn("comments", elem.attrib)

    def test_non_translatable_element_untouched(self):
        xml = '<interface><property name="visible">True</property></interface>'
        root = ET.fromstring(xml)
        xmltranslate.translate_xml_tree(root)
        elem = root.find("property")
        self.assertEqual(elem.text, "True")
        self.assertEqual(elem.attrib, {"name": "visible"})

    def test_mutates_tree_in_place(self):
        xml = '<interface><property translatable="yes">Foo</property></interface>'
        root = ET.fromstring(xml)
        result = xmltranslate.translate_xml_tree(root)
        self.assertIsNone(result)
        self.assertEqual(root.find("property").text, "[Foo]")

    def test_translate_xml_string_returns_translated_xml(self):
        xml = '<interface><property translatable="yes">Foo</property></interface>'
        result = xmltranslate.translate_xml_string(xml)
        root = ET.fromstring(result)
        self.assertEqual(root.find("property").text, "[Foo]")
        self.assertNotIn("translatable", root.find("property").attrib)

    def test_non_ascii_translation_survives_ascii_serialization(self):
        # gramps/gui/uimanager.py serializes its translated tree with
        # ET.tostring(editable).decode(encoding="ascii"); confirm that
        # non-ASCII replacement text survives that specific round trip
        # (ET emits numeric character references for non-ASCII bytes-mode
        # output, which a GtkBuilder XML parser reads back correctly).
        class AccentTranslation:
            def sgettext(self, msgid: str, context: str = "") -> str:
                return "Café résumé"

        xmltranslate.glocale.translation = AccentTranslation()
        xml = '<interface><property translatable="yes">Foo</property></interface>'
        root = ET.fromstring(xml)
        xmltranslate.translate_xml_tree(root)
        xml_str = ET.tostring(root).decode(encoding="ascii")
        reparsed = ET.fromstring(xml_str)
        self.assertEqual(reparsed.find("property").text, "Café résumé")


if __name__ == "__main__":
    unittest.main()
