#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2022 Nick Hall
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
Utilities used in unit tests.
"""

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from ..utils.grampslocale import GrampsLocale

# -------------------------------------------------------------------------
#
# Unit test utilities
#
# -------------------------------------------------------------------------

parser = GrampsLocale(lang="en").date_parser
displayer = GrampsLocale().date_displayer


def localize_date(date_str):
    """
    Translate a date into the current locale.
    """
    date = parser.parse(date_str)
    return displayer.display(date)
