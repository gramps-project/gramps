# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020  Paul Culley
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
from gramps.gen.plug._pluginreg import register, STABLE, GENERAL
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# ------------------------------------------------------------------------
#
# Common Placetypes
#
# ------------------------------------------------------------------------
register(
    GENERAL,
    category="PLACETYPES",
    id="pt_common",
    name="Common PlaceType values",
    description=_("Provides a library of Common PlaceType values."),
    version="1.0",
    status=STABLE,
    fname="placetype_common.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
    load_on_reg=True,
    gramps_target_version="6.0",
)
