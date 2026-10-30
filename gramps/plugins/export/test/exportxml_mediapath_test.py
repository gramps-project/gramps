#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps developers
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

"""
Regression test for bug 6698: Gramps-XML export must NOT strip significant
leading/trailing whitespace from a media object's path.

The path written into ``<file src="...">`` has to stay byte-for-byte equal to
the name the package archiver stores the media file under
(``exportpkg.py``: ``archname = str(mobject.get_path())``). When the serializer
stripped the path, a filename with a leading space (e.g. ``" image.png"``)
produced a ``<file src>`` value the archive did not contain, so the media showed
as "missing" on re-import.

The unit under test is ``libgrampsxml.fix_media_path`` -- the *production* path
serializer that ``exportxml.GrampsXmlWriter.write_media`` routes the path
through. It lives in an import-light module (no ``gi`` / ``gramps.gui``), so this
test runs headless without crashing. A source-level guard asserts the export
plugin actually uses it for the ``<file src>`` attribute, so the test exercises
the real path rather than a parallel copy of it.
"""

import os
import unittest

from gramps.plugins.lib.libgrampsxml import fix_media_path


class FixMediaPathTest(unittest.TestCase):
    """The media-path serializer must preserve significant whitespace."""

    def test_leading_space_preserved(self):
        """A leading space (the reporter's case) survives serialization."""
        path = " image.png"
        self.assertEqual(fix_media_path(path), " image.png")

    def test_trailing_space_preserved(self):
        path = "image.png "
        self.assertEqual(fix_media_path(path), "image.png ")

    def test_interior_and_surrounding_whitespace_preserved(self):
        path = "  my photos/holiday 2020 .png "
        self.assertEqual(fix_media_path(path), "  my photos/holiday 2020 .png ")

    def test_plain_path_unchanged(self):
        path = "images/photo.png"
        self.assertEqual(fix_media_path(path), path)

    def test_matches_archiver_name_for_space_leading_path(self):
        """
        The serialized <file src> value (for a path with no XML-special chars)
        must equal the archiver's archname == str(media.get_path()), restoring
        the bug-6698 invariant that the XML points at the archived/on-disk name.
        """
        path = " example.png"
        archname = str(path)  # exportpkg.py: archname = str(mobject.get_path())
        self.assertEqual(fix_media_path(path), archname)

    def test_control_chars_removed_but_whitespace_kept(self):
        """XML-illegal control chars are still dropped; whitespace is not."""
        self.assertEqual(fix_media_path(" a\x01b.png"), " ab.png")

    def test_xml_metacharacters_escaped(self):
        """A path round-trips faithfully: metachars escape, value preserved."""
        self.assertEqual(fix_media_path(" a&b.png"), " a&amp;b.png")
        self.assertEqual(fix_media_path(" a<b>.png"), " a&lt;b&gt;.png")

    def test_export_plugin_routes_path_through_fix_media_path(self):
        """
        Guard: the production export plugin must serialize the <file src> path
        via fix_media_path (not the whitespace-stripping self.fix), so this unit
        test covers the real export path. Checked at source level because
        exportxml imports gramps.gui at load time and cannot be imported in the
        headless test runner.
        """
        here = os.path.dirname(os.path.abspath(__file__))
        exportxml = os.path.join(os.path.dirname(here), "exportxml.py")
        with open(exportxml, encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn(
            "fix_media_path(path)",
            source,
            "exportxml.py must serialize the media path with fix_media_path",
        )


if __name__ == "__main__":
    unittest.main()
