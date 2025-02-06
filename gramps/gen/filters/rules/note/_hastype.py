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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Rule that checks for a note of a particular type.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
from ....lib.notetype import NoteType
from .. import Rule

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Note
from ....db import Database


# -------------------------------------------------------------------------
#
# HasType
#
# -------------------------------------------------------------------------
class HasType(Rule):
    """
    Rule that checks for a note of a particular type.
    """

    labels = [_("Note type:")]
    name = _("Notes with the particular type")
    description = _("Matches notes with the particular type ")
    category = _("General filters")

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.note_type = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things we only want to do once.
        """
        if self.list[0]:
            self.note_type = NoteType()
            self.note_type.set_from_xml_str(self.list[0])

    def apply_to_one(self, _db: Database, obj: Note) -> bool:
        """
        Apply the rule. Return True on a match.
        """
        if self.note_type:
            return obj.type == self.note_type
        return False
