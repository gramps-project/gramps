#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025      Nick Hall
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

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import os

from hatchling.metadata.plugin.interface import MetadataHookInterface


# ------------------------------------------------------------------------
#
# GrampsMetaDataHook class
#
# ------------------------------------------------------------------------
class GrampsMetaDataHook(MetadataHookInterface):
    def update(self, metadata):
        version_file = os.path.join(self.root, "gramps", "version.py")
        version_info = {}
        exec(open(version_file).read(), version_info)
        metadata["version"] = version_info["VERSION"].replace("-", ".")
