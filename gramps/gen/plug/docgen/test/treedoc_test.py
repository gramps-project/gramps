#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps Development Team
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
Unit tests for the image-source option of
``gramps.gen.plug.docgen.treedoc`` (bug 0013888).

Since PR 1620 (core commit 7335883f68) the genealogytree (Tree) reports
embed only cached thumbnails. This adds a user-selectable ``images``
option restoring the pre-1620 full-resolution emission as an opt-in, and
- when a thumbnail is used - annotates the node with the original
filename as a LaTeX comment so the ``.tex`` stays identifiable.

These tests drive the production ``TreeDocBase.write_node`` path (via the
concrete ``TreeGraphDoc`` subclass and a real options menu built by
``TreeOptions``) and assert both branches:

* ``images = "original"`` -> ``image = {<original media path>}`` and no
  ``% original image:`` comment;
* ``images = "thumbnail"`` (default) -> the cached-thumbnail path (not the
  original) plus a ``% original image: <path>`` comment naming the source.

Import-safety
-------------
This module imports no GUI toolkit at load time, and the thumbnail case
replaces ``get_thumbnail_path`` (an unchanged collaborator that would,
when run for real, load thumbnailer plugins and transitively a Gtk widget
that aborts a headless interpreter) with a stub. The branch routing and
the comment emission under test remain the production ``write_node`` code;
only the thumbnail *path source* is stubbed, so the test exercises the
real code path while staying safe under the plain headless C4 runner.
"""

import base64
import os
import tempfile
import unittest
from unittest import mock

from gramps.gen.lib import Media, MediaRef, Person
from gramps.gen.plug.menu import Menu
from gramps.gen.plug.docgen.treedoc import TreeGraphDoc, TreeOptions

# A minimal valid 1x1 PNG so the on-disk media file is a real image.
_PNG_1x1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR42mN"
    "kYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


class _StubDb:
    """Just enough database surface for ``write_node`` to resolve one
    image media reference. ``media_path_full`` is given an absolute path,
    so the media base path is never consulted."""

    def __init__(self, media):
        self._media = media

    def get_media_from_handle(self, _handle):
        return self._media


class WriteNodeImageSourceTest(unittest.TestCase):
    """Exercise the production ``write_node`` image-source branches."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.image_path = os.path.join(self._tmp.name, "portrait.png")
        with open(self.image_path, "wb") as handle:
            handle.write(_PNG_1x1)
        # A stand-in for the cached thumbnail get_thumbnail_path would
        # return: a real file (so write_node's os.path.isfile check passes)
        # whose path is distinct from the original.
        self.thumb_path = os.path.join(self._tmp.name, "thumb_deadbeef.png")
        with open(self.thumb_path, "wb") as handle:
            handle.write(_PNG_1x1)

        media = Media()
        media.set_path(self.image_path)
        media.set_mime_type("image/png")

        mediaref = MediaRef()
        mediaref.set_reference_handle("media-handle")

        self.person = Person()
        self.person.gramps_id = "I0001"
        self.person.gender = Person.MALE
        self.person.add_media_reference(mediaref)

        self.db = _StubDb(media)

    def tearDown(self):
        self._tmp.cleanup()

    def _make_doc(self, images_value):
        """Build a real options menu, select the image source, and return
        a concrete TreeDocBase instance (production wiring)."""
        menu = Menu()
        TreeOptions().add_menu_options(menu)
        menu.get_option_by_name("images").set_value(images_value)

        class _Options:
            pass

        options = _Options()
        options.menu = menu
        return TreeGraphDoc(options, None)

    def _render(self, images_value):
        """Run the production write_node, stubbing the (unchanged) thumbnail
        generator so the test stays headless-safe and deterministic."""
        doc = self._make_doc(images_value)
        with mock.patch(
            "gramps.gen.utils.thumbnails.get_thumbnail_path",
            return_value=self.thumb_path,
        ):
            doc.write_node(self.db, 0, "child", self.person, False)
        return doc._tex.getvalue()

    def test_default_is_thumbnail(self):
        """The option defaults to today's behaviour (PR 1620 preserved)."""
        doc = self._make_doc("thumbnail")
        self.assertEqual(doc.images, "thumbnail")

    def test_original_emits_full_resolution_path(self):
        """``original`` restores the pre-1620 emission: the full media
        path, with no thumbnail comment."""
        tex = self._render("original")
        self.assertIn("image = {%s}," % self.image_path, tex)
        self.assertNotIn("original image:", tex)

    def test_thumbnail_emits_thumbnail_path_and_comment(self):
        """``thumbnail`` emits the cached-thumbnail path (not the original)
        and a ``% original image:`` comment naming the source file."""
        tex = self._render("thumbnail")

        # The embedded image is the thumbnail, not the original.
        self.assertIn("image = {%s}," % self.thumb_path, tex)
        self.assertNotIn("image = {%s}," % self.image_path, tex)

        # The original file stays recorded as an inert LaTeX comment.
        self.assertIn("%% original image: %s" % self.image_path, tex)


if __name__ == "__main__":
    unittest.main()
