#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2019  Matthias Kemmer
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
Rule that checks for an object with a particular attribute.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale
from ...lib.attrtype import AttributeType
from . import Rule

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ...lib.attrbase import AttributeBase
from ...db import Database


# -------------------------------------------------------------------------
#
# HasAttributeBase
#
# -------------------------------------------------------------------------
class HasAttributeBase(Rule):
    """
    Rule that checks for an object with a particular attribute.
    """

    labels = ["Attribute:", "Value:"]
    name = "Objects with the <attribute>"
    description = "Matches objects with the given attribute of a particular value"
    category = _("General filters")
    allow_regex = True

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.attribute_type = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things that should only be done once.
        """
        if self.list[0]:
            self.attribute_type = AttributeType()
            self.attribute_type.set_from_xml_str(self.list[0])

    def apply_to_one(self, db: Database, obj: AttributeBase) -> bool:
        """
        Apply the rule. Return True if a match.
        """
        if self.attribute_type:
            for attribute in obj.attribute_list:
                name_match = attribute.type == self.attribute_type
                if name_match:
                    if self.match_substring(1, attribute.value):
                        return True
        return False
