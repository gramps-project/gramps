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
Helpers guarding archive extraction against path-traversal ("Zip Slip",
CVE-2007-4559): a crafted zip or tar file can use an absolute path, a
``../`` member name, or a symlink/hardlink to make a naive extractor
create or overwrite files outside the intended target directory.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import tarfile


# -------------------------------------------------------------------------
#
# Functions
#
# -------------------------------------------------------------------------
def is_within_directory(directory: str, target: str) -> bool:
    """
    Return True if ``target`` resolves to a path inside ``directory``.
    """
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    return os.path.commonpath([abs_directory, abs_target]) == abs_directory


def is_safe_archive_member(name: str, target_dir: str) -> bool:
    """
    Check that extracting an archive member named ``name`` into
    ``target_dir`` cannot write outside of it.
    """
    if os.path.isabs(name) or name.startswith(("/", "\\")):
        return False
    target_path = os.path.join(target_dir, name)
    return is_within_directory(target_dir, target_path)


def is_safe_tar_member(tarinfo: tarfile.TarInfo, target_dir: str) -> bool:
    """
    Check that extracting ``tarinfo`` into ``target_dir`` cannot write or
    link outside of it.
    """
    if not is_safe_archive_member(tarinfo.name, target_dir):
        return False
    if tarinfo.issym() or tarinfo.islnk():
        target_path = os.path.join(target_dir, tarinfo.name)
        link_target = os.path.join(os.path.dirname(target_path), tarinfo.linkname)
        if not is_within_directory(target_dir, link_target):
            return False
    return True
