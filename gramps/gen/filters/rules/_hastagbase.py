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

    def prepare(self, db, user):
        """
        Prepare the rule. Things we want to do just once.
        """
        self.tag_handle = None
        tag = db.get_tag_from_name(self.list[0])
        if tag is not None:
            self.tag_handle = tag.get_handle()

    def apply(self, db, obj):
        """
        Apply the rule.  Return True for a match.
        """
        if self.tag_handle is None:
            return False
        return self.tag_handle in obj.get_tag_list()
