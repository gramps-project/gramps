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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

# Standard Python modules
#
# -------------------------------------------------------------------------
import logging

from ...const import GRAMPS_LOCALE as glocale

LOG = logging.getLogger(".")
_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from . import Rule


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ...lib.primaryobj import PrimaryObject
from ...db import Database


# -------------------------------------------------------------------------
# "SelectWhereBase"
# -------------------------------------------------------------------------
class SelectWhereBase(Rule):
    """
    Base rule that uses a user-supplied filter expression.

    The expression should use the table name as the variable
    (e.g., "person.gender == Person.MALE" for person table,
    "family.type == FamilyRelType.MARRIED" for family table).
    """

    labels = [_("Expression:")]
    name = "Objects matching expression"
    description = "Matches objects using a filter expression. Use the table name in the expression (e.g., 'person.gender == Person.MALE')."
    category = _("General filters")
    table: str  # Set by subclasses

    def prepare(self, db: Database, user):
        """
        Prepare the rule by executing the filter expression and collecting
        matching handles.

        The expression should use the table name as the variable
        (e.g., "person.gender == Person.MALE" for person table).
        """
        where_expr = self.list[0] if self.list and len(self.list) > 0 else None
        if where_expr:
            try:
                # Use obj.handle for what (generic name that works for all tables)
                # User's expression should use table name (e.g., "person.gender == Person.MALE")
                self.selected_handles = set(
                    list(
                        db._select_from_table(
                            self.table,
                            what="obj.handle",
                            where=where_expr,
                            override=False,
                        )
                    )
                )
            except Exception as e:
                # If the where expression fails, log error and match nothing
                LOG.warning(
                    f"Error in filter expression for {self.table}: {where_expr}. Error: {e}"
                )
                self.selected_handles = set()
        else:
            self.selected_handles = set()

    def apply_to_one(self, db: Database, obj: PrimaryObject) -> bool:
        """
        Check if the object's handle is in the selected handles.
        """
        return obj.handle in self.selected_handles
