#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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

from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

from .._regexpidbase import RegExpIdBase


# -------------------------------------------------------------------------
#
# RegExpIdOf
#
# -------------------------------------------------------------------------
class RegExpIdOf(RegExpIdBase):
    """Rule that checks for a DNA match whose Gramps ID matches a regular expression."""

    name = _("DNA matches with Id containing <text>")
    description = _(
        "Matches DNA matches whose Gramps ID contains a substring "
        "or matches a regular expression"
    )
