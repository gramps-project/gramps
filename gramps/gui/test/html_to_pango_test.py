#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  The Gramps Project
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Tests for HTMLToPangoParser in htmlview.py.
"""

# python3 -m unittest gramps.gui.test.html_to_pango_test -v

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.plugins.view.htmlview import HTMLToPangoParser


# -------------------------------------------------------------------------
#
# HtmlToPangoTest
#
# -------------------------------------------------------------------------
class HtmlToPangoTest(unittest.TestCase):
    """
    Tests for the HTMLToPangoParser class to ensure safe and simple Pango markup generation.
    """

    def test_basic_formatting(self):
        """
        Test basic tags like bold, italics, underline, and links.
        """
        parser = HTMLToPangoParser()
        parser.feed(
            "Hello <b>World</b>, this is <i>italic</i> and <a href='http://test'>a link</a>."
        )
        self.assertEqual(
            parser.get_pango_markup(),
            'Hello <b>World</b>, this is <i>italic</i> and <a href="http://test">a link</a>.',
        )

    def test_escaping_raw_characters(self):
        """
        Test that special XML characters like '<' and '&' in plain text are correctly escaped.
        """
        parser = HTMLToPangoParser()
        parser.feed("Raw text with & and < characters.")
        self.assertEqual(
            parser.get_pango_markup(),
            "Raw text with &amp; and &lt; characters.",
        )

    def test_stripping_stylesheets_and_scripts(self):
        """
        Test that <style> and <script> blocks (and their content) are stripped.
        """
        parser = HTMLToPangoParser()
        parser.feed(
            "<html><head><style>body { color: red; }</style>"
            "<script>alert(1);</script></head>"
            "<body>Content <b>here</b></body></html>"
        )
        self.assertEqual(
            parser.get_pango_markup(),
            "Content <b>here</b>",
        )

    def test_headers_and_linebreaks(self):
        """
        Test that h1-h3 are converted to big/bold headers and paragraphs cause line breaks.
        """
        parser = HTMLToPangoParser()
        parser.feed("<h1>My Title</h1><p>Paragraph text.<br>Line 2.</p>")
        self.assertEqual(
            parser.get_pango_markup(),
            "<big><b>My Title</b></big>\n\nParagraph text.\nLine 2.",
        )
