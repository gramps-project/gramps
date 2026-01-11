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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Any
from ....db import Database


# -------------------------------------------------------------------------
#
# HasNameOf
#
# -------------------------------------------------------------------------
class SearchName(Rule):
    """Rule that checks for full or partial name matches"""

    labels = [_("Substring:")]
    name = _("People matching the <name>")
    description = _("Matches people with a specified (partial) name")
    category = _("General filters")

    def prepare(self, db, user):
        src = self.list[0].upper()

        if db.can_use_fast_selects():
            if not src:
                # Nothing:
                self.select_handles = set()
                return

            # First, get any matches on names:
            self.selected_handles = set(
                list(
                    db.select_from_person(
                        what="person.handle",
                        where=(
                            "any([surname for surname in [name.surname_list for name in [person.primary_name] + person.alternate_names] "
                            + "    if src in (surname.prefix + ' ' + surname.surname + ' ' + surname.connector)])"
                        ),
                        env={"src": src},
                    )
                )
            )
            # Then match any of the others:
            self.selected_handles.update(
                list(
                    db.select_from_person(
                        what="person.handle",
                        where=(
                            "any([name for name in [person.primary_name] + person.alternate_names if "
                            + "src in name.first_name or "
                            + "src in name.suffix or "
                            + "src in name.title or "
                            + "src in name.nick or "
                            + "src in name.famnick or "
                            + "src in name.call"
                            + "])"
                        ),
                        env={"src": src},
                    )
                )
            )

    @Rule.apply_fast_selects
    def apply_to_one(self, db: Database, person: Any) -> bool:
        src = self.list[0].upper()
        if not src:
            return False

        for name in [person.primary_name] + person.alternate_names:
            for field in [
                name.first_name,
                name.get_surname(),
                name.suffix,
                name.title,
                name.nick,
                name.famnick,
                name.call,
            ]:
                if src in field.upper():
                    return True
        return False
