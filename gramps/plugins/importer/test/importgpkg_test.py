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
importer (CVE-2007-4559). See also gramps.gen.utils.test.safearchive_test
for coverage of the underlying is_safe_tar_member() helper.
"""

import io
import os
import tarfile
import unittest

from gramps.gen.utils.safearchive import is_safe_tar_member


class MaliciousArchiveExtractionCheck(unittest.TestCase):
    """
    Build an in-memory tar archive that mimics a malicious .gpkg file and
    verify every unsafe member it contains is rejected before extraction,
    the same way gramps.plugins.importer.importgpkg.impData() does.
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
                self.assertFalse(is_safe_tar_member(tarinfo, target_dir))


if __name__ == "__main__":
    unittest.main()
