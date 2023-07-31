#
# Gramps - a GTK+/GNOME based genealogy program
#
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
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

MODULE_VERSION = "5.2"

# ------------------------------------------------------------------------
#
# Default thumbnailers for Gramps
#
# ------------------------------------------------------------------------

register(
    THUMBNAILER,
    id="gnomethumb",
    name=_("Gnome Thumbnailer"),
    description=_("Gnome Thumbnailer"),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="gnomethumb.py",
    thumbnailer="GnomeThumb",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
)

register(
    THUMBNAILER,
    id="imagethumb",
    name=_("Image Thumbnailer"),
    description=_("Image Thumbnailer"),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    order=START,
    fname="imagethumb.py",
    thumbnailer="ImageThumb",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
)
