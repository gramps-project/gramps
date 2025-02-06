#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
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
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....lib.nameorigintype import NameOriginType


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Person
from ....db import Database


# -------------------------------------------------------------------------
#
# HasNameOf
#
# -------------------------------------------------------------------------
class HasNameOf(Rule):
    """Rule that checks for full or partial name matches"""

    labels = [
        _("Given name:"),
        _("Full Family name:"),
        _("Title:", "person"),
        _("Suffix:"),
        _("Call Name:"),
        _("Nick Name:"),
        _("Prefix:"),
        _("Single Surname:"),
        _("Connector"),
        _("Patronymic:"),
        _("Family Nick Name:"),
    ]
    name = _("People with the <name>")
    description = _("Matches people with a specified (partial) name")
    category = _("General filters")
    allow_regex = True

    def apply_to_one(self, db: Database, person: Person) -> bool:
        for name in [person.primary_name] + person.alternate_names:
            if self.match_name(name):
                return True
        return False

    def match_name(self, name):
        if self.list[0] and not self.match_substring(0, name.first_name):
            return False
        elif self.list[1] and not self.match_substring(1, name.get_surname()):
            return False
        elif self.list[2] and not self.match_substring(2, name.title):
            return False
        elif self.list[3] and not self.match_substring(3, name.suffix):
            return False
        elif self.list[4] and not self.match_substring(4, name.call):
            return False
        elif self.list[5] and not self.match_substring(5, name.nick):
            return False
        elif self.list[10] and not self.match_substring(10, name.famnick):
            return False
        else:
            for surn in name.surname_list:
                if self.match_surname(surn):
                    return True
        return False

    def match_surname(self, surn):
        if self.list[6] and not self.match_substring(6, surn.prefix):
            return False
        if self.list[7] and not self.match_substring(7, surn.surname):
            return False
        if self.list[8] and not self.match_substring(8, surn.connector):
            return False
        if int(surn.origintype.value) == NameOriginType.PATRONYMIC:
            if self.list[9] and not self.match_substring(9, surn.surname):
                return False
        return True
