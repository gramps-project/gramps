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
Translation of GtkBuilder XML.

Gtk.Builder translates ``translatable="yes"`` XML attributes itself, via
GLib's C-level gettext binding, straight from the compiled .mo catalog. It
never calls into Gramps' own translation object, so user-defined translation
overrides (see :mod:`gramps.gen.utils.translationoverride`) are never
consulted for menu, toolbar, or .glade dialog text defined this way.

The functions here pre-resolve that text in Python, through the same
override-aware path an ordinary ``_()`` call already uses, before the XML is
ever handed to Gtk.Builder.
"""

from __future__ import annotations

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import xml.etree.ElementTree as ET

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale


def translate_xml_tree(root: ET.Element) -> None:
    """
    Resolve ``translatable="yes"`` GtkBuilder XML text in place.

    Each such element's text is replaced with its translation (consulting
    user overrides first, then the normal catalog), and its
    ``translatable``, ``context``, and ``comments`` attributes are removed
    so Gtk.Builder does not attempt to translate it again.

    :param root: the root of the XML tree to translate, mutated in place.
    :type root: :py:class:`xml.etree.ElementTree.Element`
    """
    for elem in root.iter():
        if elem.get("translatable") == "yes":
            if elem.text:
                context = elem.get("context", "")
                elem.text = glocale.translation.sgettext(elem.text, context)
            del elem.attrib["translatable"]
            elem.attrib.pop("context", None)
            elem.attrib.pop("comments", None)


def translate_xml_string(xml_str: str) -> str:
    """
    Resolve ``translatable="yes"`` GtkBuilder XML text in a serialized
    XML string.

    :param xml_str: GtkBuilder XML source.
    :type xml_str: str
    :returns: the same XML with translatable text resolved and the
              ``translatable``/``context``/``comments`` attributes removed.
    :rtype: str
    """
    root = ET.fromstring(xml_str)
    translate_xml_tree(root)
    return ET.tostring(root, encoding="unicode")
