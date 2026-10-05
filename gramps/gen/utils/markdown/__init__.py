#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  Doug Blank
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
gramps.gen.utils.markdown
~~~~~~~~~~~~~~~~~~~~~~~~~~
Pure-Python parser for the Gramps markdown dialect.

Runtime GTK rendering is in gramps.gui.widgets.markdown_render.
"""

from .parse import parse_front_matter, parse_img_src, parse_markdown

__all__ = [
    "parse_front_matter",
    "parse_markdown",
    "parse_img_src",
]
