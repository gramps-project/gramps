#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2022       Nick Hall
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
A thumbnailer that uses other system thumbnailers already installed on a
Gmone desktop.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import os
import glob
import logging

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import GLib

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import THUMBSCALE, THUMBSCALE_LARGE, SIZE_LARGE
from gramps.gen.plug import Thumbnailer
from gramps.gen.constfunc import get_env_var, lin

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
LOG = logging.getLogger(".thumbnail")


class GnomeThumb(Thumbnailer):
    def __init__(self):
        self.all_mime_types = {}
        if lin():
            self.__find_thumbnailers()

    def __find_thumbnailers(self):
        path_list = GLib.get_system_data_dirs()
        path_list.append(GLib.get_user_data_dir())
        file_list = []
        for path in path_list:
            file_list.extend(
                glob.glob(os.path.join(path, "thumbnailers", "*.thumbnailer"))
            )

        for filename in file_list:
            kf = GLib.KeyFile()
            try:
                kf.load_from_file(filename, GLib.KeyFileFlags.NONE)
                cmd = kf.get_string("Thumbnailer Entry", "Exec")
                mime_types = kf.get_string_list("Thumbnailer Entry", "MimeType")
            except GLib.GError:
                continue
            if cmd and mime_types:
                for mime_type in mime_types:
                    self.all_mime_types[mime_type] = cmd

    def is_supported(self, mime_type):
        return mime_type in self.all_mime_types

    def run(self, mime_type, src_file, dest_file, size, rectangle):
        cmd = self.all_mime_types.get(mime_type)
        if cmd:
            if size == SIZE_LARGE:
                thumbscale = THUMBSCALE_LARGE
            else:
                thumbscale = THUMBSCALE
            sublist = {
                "%s": "%d" % int(thumbscale),
                "%u": "file://" + src_file,
                "%i": src_file,
                "%o": dest_file,
            }
            cmdlist = [sublist.get(x, x) for x in cmd.split()]
            return os.spawnvpe(os.P_WAIT, cmdlist[0], cmdlist, os.environ) == 0
        return False
