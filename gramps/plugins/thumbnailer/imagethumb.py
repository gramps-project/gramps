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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
A thumbnailer for images and sub-sections of images.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import THUMBSCALE, THUMBSCALE_LARGE, SIZE_LARGE
from gramps.gen.plug import Thumbnailer

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
LOG = logging.getLogger(".thumbnail")


# -------------------------------------------------------------------------
#
# ImageThumb
#
# -------------------------------------------------------------------------
class ImageThumb(Thumbnailer):
    def is_supported(self, mime_type):
        if mime_type:
            return mime_type.startswith("image")
        else:
            return False

    def run(self, mime_type, src_file, dest_file, size, rectangle):
        # build a thumbnail by scaling the image using GTK's built in
        # routines, falling back to PIL where GTK is unavailable
        # (headless/CLI environments without PyGObject).
        try:
            from gi.repository import GdkPixbuf
        except ImportError:
            return self._run_pil(src_file, dest_file, size, rectangle)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(src_file)
            width = pixbuf.get_width()
            height = pixbuf.get_height()

            if rectangle is not None:
                upper_x = min(rectangle[0], rectangle[2]) / 100.0
                lower_x = max(rectangle[0], rectangle[2]) / 100.0
                upper_y = min(rectangle[1], rectangle[3]) / 100.0
                lower_y = max(rectangle[1], rectangle[3]) / 100.0
                sub_x = int(upper_x * width)
                sub_y = int(upper_y * height)
                sub_width = int((lower_x - upper_x) * width)
                sub_height = int((lower_y - upper_y) * height)
                if sub_width > 0 and sub_height > 0:
                    pixbuf = pixbuf.new_subpixbuf(sub_x, sub_y, sub_width, sub_height)
                    width = sub_width
                    height = sub_height

            if size == SIZE_LARGE:
                thumbscale = THUMBSCALE_LARGE
            else:
                thumbscale = THUMBSCALE
            scale = thumbscale / (float(max(width, height)))

            scaled_width = int(width * scale)
            scaled_height = int(height * scale)

            pixbuf = pixbuf.scale_simple(
                scaled_width, scaled_height, GdkPixbuf.InterpType.BILINEAR
            )
            pixbuf.savev(dest_file, "png", [], [])
            return True
        except Exception as err:
            LOG.warning("Error scaling image down: %s", str(err))
            return False

    def _run_pil(self, src_file, dest_file, size, rectangle):
        """Scale the image with PIL when GTK is unavailable."""
        try:
            from PIL import Image
        except ImportError as err:
            LOG.warning("Error scaling image down: %s", str(err))
            return False
        try:
            with Image.open(src_file) as img:
                img.load()
                width, height = img.size
                if rectangle is not None:
                    upper_x = min(rectangle[0], rectangle[2]) / 100.0
                    lower_x = max(rectangle[0], rectangle[2]) / 100.0
                    upper_y = min(rectangle[1], rectangle[3]) / 100.0
                    lower_y = max(rectangle[1], rectangle[3]) / 100.0
                    sub = (
                        int(upper_x * width),
                        int(upper_y * height),
                        int(lower_x * width),
                        int(lower_y * height),
                    )
                    if sub[2] > sub[0] and sub[3] > sub[1]:
                        img = img.crop(sub)
                        width = sub[2] - sub[0]
                        height = sub[3] - sub[1]
                thumbscale = THUMBSCALE_LARGE if size == SIZE_LARGE else THUMBSCALE
                scale = thumbscale / float(max(width, height))
                scaled = img.resize(
                    (max(1, int(width * scale)), max(1, int(height * scale))),
                    Image.BILINEAR,
                )
                scaled.save(dest_file, "PNG")
                return True
        except Exception as err:
            LOG.warning("Error scaling image down: %s", str(err))
            return False
