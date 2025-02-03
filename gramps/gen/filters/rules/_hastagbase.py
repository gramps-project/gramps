#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010    Nick Hall
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
Rule that checks for an object with a particular tag.
"""

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
from ...lib.primaryobj import PrimaryObject
from ...db import Database


# -------------------------------------------------------------------------
#
# HasTag
#
# -------------------------------------------------------------------------
class HasTagBase(Rule):
    """
    Rule that checks for an object with a particular tag.
    """

    labels = ["Tag:"]
    name = "Objects with the <tag>"
    description = "Matches objects with the given tag"
    category = _("General filters")

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things we want to do just once.
        """
        self.tag_handle = None
        tag = db.get_tag_from_name(self.list[0])
        if tag is not None:
            self.tag_handle = tag.handle

    def apply_to_one(self, db: Database, obj: PrimaryObject) -> bool:
        """
        Apply the rule.  Return True for a match.
        """
        if self.tag_handle is None:
            return False
        return self.tag_handle in obj.tag_list
