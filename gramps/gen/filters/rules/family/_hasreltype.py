#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
Rule that checks for families with a particular relationship type.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
from ....lib.familyreltype import FamilyRelType
from .. import Rule

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Family
from ....db import Database


# -------------------------------------------------------------------------
#
# HasRelType
#
# -------------------------------------------------------------------------
class HasRelType(Rule):
    """
    Rule that checks for families with a particular relationship type.
    """

    labels = [_("Relationship type:")]
    name = _("Families with the relationship type")
    description = _("Matches families with the relationship type of a particular value")
    category = _("General filters")

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.relation_type = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things we only want to do once.
        """
        if self.list[0]:
            self.relation_type = FamilyRelType()
            self.relation_type.set_from_xml_str(self.list[0])

    def apply_to_one(self, _db: Database, obj: Family) -> bool:
        """
        Apply the rule. Return True on a match.
        """
        if self.relation_type:
            if self.relation_type.is_custom() and self.use_regex:
                if self.regex[0].search(str(obj.type)) is None:
                    return False
            elif self.relation_type != obj.type:
                return False
        return True
