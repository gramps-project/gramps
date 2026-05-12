#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

from ....const import GRAMPS_LOCALE as glocale
from ....display.name import displayer as name_displayer
from .. import Rule
from ....db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# HasDNAMatch
#
# -------------------------------------------------------------------------
class HasDNAMatch(Rule):
    """
    Rule that matches DNA matches by subject person name, subject account
    name, or match person/account name.  All supplied fields must match
    (AND logic).  Empty fields are ignored.
    """

    labels = [
        _("Subject person name:"),
        _("Subject account name:"),
        _("Match person name:"),
        _("Match account name:"),
    ]
    name = _("DNA matches matching <text>")
    description = _(
        "Matches DNA matches by subject person name, subject account name, "
        "match person name, or match account name"
    )
    category = _("DNA match filters")
    allow_regex = True

    def _get_dnatest(self, db, handle):
        if handle:
            return db.get_dnatest_from_handle(handle)
        return None

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        if self.list[0] or self.list[1]:
            subject = self._get_dnatest(db, dnamatch.subject_test_handle)
            if self.list[0]:
                subject_person_name = ""
                if subject and subject.person_handle:
                    person = db.get_person_from_handle(subject.person_handle)
                    if person:
                        subject_person_name = name_displayer.display(person)
                if not self.match_substring(0, subject_person_name):
                    return False
            if self.list[1]:
                subject_account = subject.account_name if subject else ""
                if not self.match_substring(1, subject_account):
                    return False

        if self.list[2] or self.list[3]:
            match_test = self._get_dnatest(db, dnamatch.match_test_handle)
            if self.list[2]:
                match_person_name = ""
                if match_test and match_test.person_handle:
                    person = db.get_person_from_handle(match_test.person_handle)
                    if person:
                        match_person_name = name_displayer.display(person)
                if not self.match_substring(2, match_person_name):
                    return False
            if self.list[3]:
                match_account = match_test.account_name if match_test else ""
                if not self.match_substring(3, match_account):
                    return False

        return True
