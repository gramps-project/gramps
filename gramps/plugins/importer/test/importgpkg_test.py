#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Gramps Development Team
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
Unittest for the tarfile path-traversal guard in the Gramps package
importer (CVE-2007-4559).
"""

import io
import os
import tarfile
import unittest

from gramps.plugins.importer.importgpkg import _is_safe_member


def _make_tarinfo(name: str, linkname: str = "", linktype: str | None = None):
    tarinfo = tarfile.TarInfo(name=name)
    if linktype == "sym":
        tarinfo.type = tarfile.SYMTYPE
        tarinfo.linkname = linkname
    elif linktype == "link":
        tarinfo.type = tarfile.LNKTYPE
        tarinfo.linkname = linkname
    return tarinfo


class SafeMemberCheck(unittest.TestCase):
    def setUp(self):
        self.target_dir = os.path.join(os.sep, "home", "user", "tree.media")

    def test_regular_relative_member_is_safe(self):
        tarinfo = _make_tarinfo("photo.jpg")
        self.assertTrue(_is_safe_member(tarinfo, self.target_dir))

    def test_relative_subdir_member_is_safe(self):
        tarinfo = _make_tarinfo(os.path.join("sub", "photo.jpg"))
        self.assertTrue(_is_safe_member(tarinfo, self.target_dir))

    def test_absolute_path_is_unsafe(self):
        tarinfo = _make_tarinfo(os.path.join(os.sep, "etc", "passwd"))
        self.assertFalse(_is_safe_member(tarinfo, self.target_dir))

    def test_parent_traversal_is_unsafe(self):
        tarinfo = _make_tarinfo(os.path.join("..", "..", "..", "etc", "passwd"))
        self.assertFalse(_is_safe_member(tarinfo, self.target_dir))

    def test_symlink_escaping_target_is_unsafe(self):
        tarinfo = _make_tarinfo(
            "innocuous",
            linkname=os.path.join("..", "..", "etc", "passwd"),
            linktype="sym",
        )
        self.assertFalse(_is_safe_member(tarinfo, self.target_dir))

    def test_symlink_within_target_is_safe(self):
        tarinfo = _make_tarinfo("link", linkname="photo.jpg", linktype="sym")
        self.assertTrue(_is_safe_member(tarinfo, self.target_dir))

    def test_hardlink_escaping_target_is_unsafe(self):
        tarinfo = _make_tarinfo(
            "innocuous",
            linkname=os.path.join(os.sep, "etc", "passwd"),
            linktype="link",
        )
        self.assertFalse(_is_safe_member(tarinfo, self.target_dir))


class MaliciousArchiveExtractionCheck(unittest.TestCase):
    """
    Build an in-memory tar archive that mimics a malicious .gpkg file and
    verify every unsafe member it contains is rejected before extraction.
    """

    def test_all_members_of_malicious_archive_are_rejected(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w") as archive:
            evil = tarfile.TarInfo(name=os.path.join("..", "..", "evil.txt"))
            data = b"payload"
            evil.size = len(data)
            archive.addfile(evil, io.BytesIO(data))
        buffer.seek(0)

        target_dir = os.path.join(os.sep, "home", "user", "tree.media")
        with tarfile.open(fileobj=buffer) as archive:
            for tarinfo in archive:
                self.assertFalse(_is_safe_member(tarinfo, target_dir))


if __name__ == "__main__":
    unittest.main()
