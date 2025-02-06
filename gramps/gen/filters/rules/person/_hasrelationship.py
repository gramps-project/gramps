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
Rule that checks for a person who has a particular relationship.
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
from ....lib import Person
from ....db import Database


# -------------------------------------------------------------------------
#
# HasRelationship
#
# -------------------------------------------------------------------------
class HasRelationship(Rule):
    """
    Rule that checks for a person who has a particular relationship.
    """

    labels = [
        _("Number of relationships:"),
        _("Relationship type:"),
        _("Number of children:"),
    ]
    name = _("People with the <relationships>")
    description = _("Matches people with a particular relationship")
    category = _("Family filters")

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.relationship_type = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things we only want to do once.
        """
        if self.list[1]:
            self.relationship_type = FamilyRelType()
            self.relationship_type.set_from_xml_str(self.list[1])

    def apply_to_one(self, db: Database, obj: Person) -> bool:
        """
        Apply the rule. Return True on a match.
        """
        relationship_type = 0
        total_children = 0
        number_relations = len(obj.family_list)

        # count children and look for a relationship type match
        for handle in obj.family_list:
            family = db.get_family_from_handle(handle)
            if family:
                total_children += len(family.child_ref_list)
                if self.relationship_type and (self.relationship_type == family.type):
                    relationship_type = 1

        # if number of relations specified
        if self.list[0]:
            try:
                if int(self.list[0]) != number_relations:
                    return False
            except:
                return False

        # number of children
        if self.list[2]:
            try:
                if int(self.list[2]) != total_children:
                    return False
            except:
                return False

        # relation
        if self.list[1]:
            return relationship_type == 1

        return True
