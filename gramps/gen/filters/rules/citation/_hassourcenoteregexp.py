#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2014       Nick Hall
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
Filter rule to match citations whose source notes contain a substring or
match a regular expression.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .._hasnoteregexbase import HasNoteRegexBase


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Citation
from ....db import Database


# -------------------------------------------------------------------------
#
# HasSourceNoteRegexp
#
# -------------------------------------------------------------------------
class HasSourceNoteRegexp(HasNoteRegexBase):
    """
    Rule that checks if a citation has a source note that contains a
    substring or matches a regular expression.
    """

    name = _("Citations having source notes containing <text>")
    description = _(
        "Matches citations whose source notes contain a substring "
        "or match a regular expression"
    )
    category = _("Source filters")

    def apply_to_one(self, db: Database, citation: Citation) -> bool:  # type: ignore[override]
        source = db.get_source_from_handle(citation.source_handle)
        return HasNoteRegexBase.apply_to_one(self, db, source)
