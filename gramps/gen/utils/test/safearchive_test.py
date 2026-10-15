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
Unittest for the archive path-traversal guards ("Zip Slip", CVE-2007-4559).
"""

import os
import tarfile
import unittest

from gramps.gen.utils.safearchive import (
    is_safe_archive_member,
    is_safe_tar_member,
    is_within_directory,
)


def _make_tarinfo(name: str, linkname: str = "", linktype: str | None = None):
    tarinfo = tarfile.TarInfo(name=name)
    if linktype == "sym":
        tarinfo.type = tarfile.SYMTYPE
        tarinfo.linkname = linkname
    elif linktype == "link":
        tarinfo.type = tarfile.LNKTYPE
        tarinfo.linkname = linkname
    return tarinfo


class IsWithinDirectoryCheck(unittest.TestCase):
    def setUp(self):
        self.target_dir = os.path.join(os.sep, "home", "user", "tree.media")

    def test_subpath_is_within(self):
        self.assertTrue(
            is_within_directory(
                self.target_dir, os.path.join(self.target_dir, "photo.jpg")
            )
        )

    def test_sibling_path_is_not_within(self):
        self.assertFalse(
            is_within_directory(
                self.target_dir,
                os.path.join(os.path.dirname(self.target_dir), "other.media"),
            )
        )


class IsSafeArchiveMemberCheck(unittest.TestCase):
    def setUp(self):
        self.target_dir = os.path.join(os.sep, "home", "user", "tree.media")

    def test_regular_relative_member_is_safe(self):
        self.assertTrue(is_safe_archive_member("photo.jpg", self.target_dir))

    def test_relative_subdir_member_is_safe(self):
        name = os.path.join("sub", "photo.jpg")
        self.assertTrue(is_safe_archive_member(name, self.target_dir))

    def test_absolute_path_is_unsafe(self):
        name = os.path.join(os.sep, "etc", "passwd")
        self.assertFalse(is_safe_archive_member(name, self.target_dir))

    def test_parent_traversal_is_unsafe(self):
        name = os.path.join("..", "..", "..", "etc", "passwd")
        self.assertFalse(is_safe_archive_member(name, self.target_dir))


class IsSafeTarMemberCheck(unittest.TestCase):
    def setUp(self):
        self.target_dir = os.path.join(os.sep, "home", "user", "tree.media")

    def test_regular_relative_member_is_safe(self):
        tarinfo = _make_tarinfo("photo.jpg")
        self.assertTrue(is_safe_tar_member(tarinfo, self.target_dir))

    def test_parent_traversal_is_unsafe(self):
        tarinfo = _make_tarinfo(os.path.join("..", "..", "..", "etc", "passwd"))
        self.assertFalse(is_safe_tar_member(tarinfo, self.target_dir))

    def test_symlink_escaping_target_is_unsafe(self):
        tarinfo = _make_tarinfo(
            "innocuous",
            linkname=os.path.join("..", "..", "etc", "passwd"),
            linktype="sym",
        )
        self.assertFalse(is_safe_tar_member(tarinfo, self.target_dir))

    def test_symlink_within_target_is_safe(self):
        tarinfo = _make_tarinfo("link", linkname="photo.jpg", linktype="sym")
        self.assertTrue(is_safe_tar_member(tarinfo, self.target_dir))

    def test_hardlink_escaping_target_is_unsafe(self):
        tarinfo = _make_tarinfo(
            "innocuous",
            linkname=os.path.join(os.sep, "etc", "passwd"),
            linktype="link",
        )
        self.assertFalse(is_safe_tar_member(tarinfo, self.target_dir))


if __name__ == "__main__":
    unittest.main()
