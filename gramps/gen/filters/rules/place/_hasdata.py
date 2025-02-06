#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2015       Nick Hall
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
Rule that checks for a place with a particular value
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
from ....lib import PlaceType
from .. import Rule

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Place
from ....db import Database


_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# HasData
#
# -------------------------------------------------------------------------
class HasData(Rule):
    """
    Rule that checks for a place with a particular value
    """

    labels = [
        _("Name:", "place"),
        _("Place type:"),
        _("Code:"),
    ]
    name = _("Places matching parameters")
    description = _("Matches places with particular parameters")
    category = _("General filters")
    allow_regex = True

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.place_type = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things we only want to do once.
        """
        if self.list[1]:
            self.place_type = PlaceType()
            self.place_type.set_from_xml_str(self.list[1])

    def apply_to_one(self, _db: Database, obj: Place) -> bool:
        """
        Apply the rule. Return True on a match.
        """
        if not self.match_name(obj):
            return False

        if self.place_type and obj.place_type != self.place_type:
            return False

        if not self.match_substring(2, obj.code):
            return False

        return True

    def match_name(self, place):
        """
        Match any name in a list of names.
        """
        for name in place.get_all_names():
            if self.match_substring(0, name.value):
                return True
        return False
