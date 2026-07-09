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
from .. import Rule
from ....db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# HasSubjectAccountName
#
# -------------------------------------------------------------------------
class HasSubjectAccountName(Rule):
    """Rule that matches DNA matches by the subject kit's account name."""

    labels = [_("Subject account name:")]
    name = _("DNA matches with subject account name <text>")
    description = _(
        "Matches DNA matches whose subject kit has an account name "
        "containing the given text"
    )
    category = _("DNA match filters")
    allow_regex = True

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        account_name = ""
        if dnamatch.subject_test_handle:
            subject = db.get_dnatest_from_handle(dnamatch.subject_test_handle)
            if subject:
                account_name = subject.account_name
        return self.match_substring(0, account_name)
