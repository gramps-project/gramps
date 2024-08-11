#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# gen/mime/__init__.py

try:
    from ._winmime import get_description, get_type, mime_type_is_defined
except:
    from ._pythonmime import get_description, get_type, mime_type_is_defined


def base_type(val):
    return val.split("/")[0]


def is_image_type(val):
    return base_type(val) == "image"


def is_directory(val):
    return base_type(val) == "x-directory"


_invalid_mime_types = ("x-directory", "x-special")


def is_valid_type(val):
    return base_type(val) not in _invalid_mime_types
