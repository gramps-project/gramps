#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Kevin White
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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Check and Repair keeps a media checksum when the file cannot be read."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import hashlib
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import Media
from gramps.gen.types import MediaHandle
from gramps.plugins.tool.check import CheckIntegrity


class _DbState:
    """Minimal stand-in for Gramps' DbState."""

    def __init__(self, db: object) -> None:
        self.db = db


class CheckChecksumTest(unittest.TestCase):
    """CheckIntegrity.check_checksum updates checksums but never clears them."""

    def setUp(self) -> None:
        self.db = make_database("sqlite")
        self.db.load(":memory:")
        self.tmp = tempfile.mkdtemp()
        self.db.set_mediapath(self.tmp)

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def add_media(self, path: str, checksum: str) -> MediaHandle:
        """Add a media record with a stored checksum and return its handle."""
        with DbTxn("add media", self.db) as trans:
            media = Media()
            media.set_path(path)
            media.set_checksum(checksum)
            return self.db.add_media(media, trans)

    def write(self, name: str, content: bytes) -> str:
        """Write a file in the media folder and return its MD5."""
        with open(os.path.join(self.tmp, name), "wb") as handle:
            handle.write(content)
        return hashlib.md5(content).hexdigest()

    def run_check(self) -> None:
        """Run only the checksum pass, without a progress window."""
        with patch("gramps.plugins.tool.check.ProgressMeter", MagicMock()):
            with DbTxn("check", self.db, batch=True) as trans:
                CheckIntegrity(_DbState(self.db), None, trans).check_checksum()

    def checksum(self, handle: MediaHandle) -> str:
        """Return the stored checksum of a media record."""
        return self.db.get_media_from_handle(handle).get_checksum()

    def test_missing_file_keeps_checksum(self) -> None:
        """A record whose file is missing keeps its checksum."""
        handle = self.add_media("renamed_or_moved.jpg", "a" * 32)
        self.run_check()
        self.assertEqual(self.checksum(handle), "a" * 32)

    def test_changed_file_gets_new_checksum(self) -> None:
        """A readable file whose content changed gets its new checksum."""
        digest = self.write("photo.jpg", b"edited photo")
        handle = self.add_media("photo.jpg", "b" * 32)
        self.run_check()
        self.assertEqual(self.checksum(handle), digest)

    def test_empty_checksum_filled_in(self) -> None:
        """A readable file without a checksum gets one."""
        digest = self.write("scan.jpg", b"scan")
        handle = self.add_media("scan.jpg", "")
        self.run_check()
        self.assertEqual(self.checksum(handle), digest)

    def test_missing_file_without_checksum_unchanged(self) -> None:
        """A missing file with no checksum stays without one."""
        handle = self.add_media("gone.jpg", "")
        self.run_check()
        self.assertEqual(self.checksum(handle), "")


if __name__ == "__main__":
    unittest.main()
