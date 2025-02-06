#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Gramps
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
Rule that checks the type of Surname origin.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
from ....lib.nameorigintype import NameOriginType
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
# HasNameOriginType
#
# -------------------------------------------------------------------------
class HasNameOriginType(Rule):
    """
    Rule that checks the type of Surname origin.
    """

    labels = [_("Surname origin type:")]
    name = _("People with the <Surname origin type>")
    description = _("Matches people with a surname origin")
    category = _("General filters")

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.name_origin_type = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things we only want to do once.
        """
        if self.list[0]:
            self.name_origin_type = NameOriginType()
            self.name_origin_type.set_from_xml_str(self.list[0])

    def apply_to_one(self, _db: Database, obj: Person) -> bool:
        """
        Apply the rule. Return True on a match.
        """
        if self.name_origin_type:
            for name in [obj.primary_name] + obj.alternate_names:
                for surname in name.surname_list:
                    if surname.origintype == self.name_origin_type:
                        return True
        return False
