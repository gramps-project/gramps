# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009       Brian G. Matherly
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

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------
from xml.sax.saxutils import escape

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
#
# Public Constants
#
# ------------------------------------------------------------------------
GRAMPS_XML_VERSION_TUPLE = (1, 7, 2)  # version for Gramps 6.0
GRAMPS_XML_VERSION = ".".join(str(i) for i in GRAMPS_XML_VERSION_TUPLE)

# table for skipping control chars from XML except 09, 0A, 0D
_STRIP_DICT = dict.fromkeys(list(range(9)) + list(range(11, 13)) + list(range(14, 32)))


def fix_media_path(path):
    """
    Serialize a media object's path for the XML ``<file src="...">`` attribute.

    Unlike the general free-text serializer (``exportxml.fix``), this MUST NOT
    strip leading or trailing whitespace: whitespace is significant in a
    filename and the package archiver stores the media file under the
    un-stripped ``str(media.get_path())`` (see ``exportpkg.py``). Stripping it
    here makes the ``<file src>`` value disagree with the archived/on-disk name,
    so the media can no longer be located on re-import (bug 6698). XML-illegal
    control characters are still removed and XML metacharacters escaped, so the
    attribute value round-trips back to the exact stored path on parse.
    """
    return escape(
        str(path).translate(_STRIP_DICT),
        {
            '"': "&quot;",
            "<": "&lt;",
            ">": "&gt;",
        },
    )
