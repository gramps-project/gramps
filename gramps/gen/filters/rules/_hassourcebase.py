#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from . import Rule


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Any
from ...db import Database


# -------------------------------------------------------------------------
#
# HasSource
#
# -------------------------------------------------------------------------
class HasSourceBase(Rule):
    """Rule that checks for a source with a particular value"""

    labels = ["Title:", "Author:", "Abbreviation:", "Publication:"]
    name = "Sources matching parameters"
    description = "Matches sources with particular parameters"
    category = _("Citation/source filters")
    allow_regex = True

    def apply_to_one(self, db: Database, source: Any) -> bool:
        if not self.match_substring(0, source.title):
            return False

        if not self.match_substring(1, source.author):
            return False

        if not self.match_substring(2, source.abbrev):
            return False

        if not self.match_substring(3, source.pubinfo):
            return False

        return True
