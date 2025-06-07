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

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import re
from ...const import GRAMPS_LOCALE as glocale

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
from ...lib.notebase import NoteBase
from ...types import Database


# -------------------------------------------------------------------------
# Objects having notes that contain a substring or match a regular expression
# -------------------------------------------------------------------------
class HasNoteRegexBase(Rule):
    """Objects having notes containing <text>."""

    labels = [_("Text:")]
    name = "Objects having notes containing <text>"
    description = (
        "Matches objects whose notes contain a substring "
        "or match a regular expression"
    )
    category = _("General filters")
    allow_regex = True

    def apply_to_one(self, db: Database, obj: NoteBase) -> bool:
        for handle in obj.note_list:
            note = db.get_note_from_handle(handle)
            if self.match_substring(0, str(note.text)):
                return True
        return False
