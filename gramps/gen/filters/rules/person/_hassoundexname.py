#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017  Paul Culley <paulr2787_at_gmail.com>
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
Rule that checks for full or partial name matches based on soundex.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
from ....lib.nameorigintype import NameOriginType
from ....soundex import soundex
from .. import Rule

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Person
from ....db import Database


# -------------------------------------------------------------------------
#
# HasSoundexName
#
# -------------------------------------------------------------------------
class HasSoundexName(Rule):
    """
    Rule that checks for full or partial name matches based on soundex.
    """

    labels = [_("Name:")]
    name = _("Soundex match of People with the <name>")
    description = _(
        "Soundex Match of people with a specified name. First name, Surname, "
        "Call name, and Nickname are searched in primary and alternate names."
    )
    category = _("General filters")
    allow_regex = False

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.soundex = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things we only want to do once.
        """
        if self.list[0]:
            self.soundex = soundex(self.list[0])

    def apply_to_one(self, _db: Database, obj: Person) -> bool:
        """
        Apply the rule. Return True on a match.
        """
        for name in [obj.primary_name] + obj.alternate_names:
            if self._match_name(name):
                return True
        return False

    def _match_name(self, name):
        """
        Match a name against the soundex.
        """
        if self.soundex:
            if soundex(str(name.first_name)) == self.soundex:
                return True
            if soundex(str(name.get_surname())) == self.soundex:
                return True
            if soundex(str(name.call)) == self.soundex:
                return True
            if soundex(str(name.nick)) == self.soundex:
                return True
            if soundex(str(name.famnick)) == self.soundex:
                return True
            for surname in name.surname_list:
                if self._match_surname(surname):
                    return True
        return False

    def _match_surname(self, surname):
        """
        Match a surname against the soundex.
        """
        if soundex(str(surname.get_surname())) == self.soundex:
            return True
        if int(surname.origintype.value) == NameOriginType.PATRONYMIC:
            if soundex(str(surname.surname)) == self.soundex:
                return True
        return False
