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
# HasMatchPersonName
#
# -------------------------------------------------------------------------
class HasMatchPersonName(Rule):
    """
    Rule that matches DNA matches by the display name of the person linked
    to the match kit.

    Resolving the display name is comparatively expensive, so this rule is
    kept separate from the cheaper account-name rules; that lets the filter
    optimizer narrow the candidate set with the cheaper rules first.
    """

    labels = [_("Match person name:")]
    name = _("DNA matches with match person name <text>")
    description = _(
        "Matches DNA matches whose match kit is linked to a person whose "
        "name contains the given text"
    )
    category = _("DNA match filters")
    allow_regex = True

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        person_name = ""
        if dnamatch.match_test_handle:
            match_test = db.get_dnatest_from_handle(dnamatch.match_test_handle)
            if match_test and match_test.person_handle:
                person = db.get_person_from_handle(match_test.person_handle)
                if person:
                    person_name = name_displayer.display(person)
        return self.match_substring(0, person_name)
